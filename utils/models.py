"""
In-memory models -- models that are not stored in any database.

Suppose you have a fixed collection of objects that fit the Django's ORM
architecture well and could make use of the rest of the framework, but
(for now?) shouldn't be stored in the database.

One solution would be to make use of an in-memory database or table, but for
single cases this isn't that convenient or even supported with some engines.
Another, is to use plain Python objects, but then you're likely to replicate
more than necessary of the functionality that Django and its add-ons provide.

The VolatileModel class is built on top of a fake queryset that ignores your
database backends, instead using a Python dict (primary key --> model instance)
as storage. Obviously -- such storage is volatile -- the objects need to be
recreated anew after each application restart.

Ihe implementation is partial. Filtering, ordering and aggregation are normally
delegated to the database, so will mostly not work with this minimal approach.
However, it is sufficient to display a basic change list in admin.


How to use it:

    from utils.models import VolatileModel


    class YesNo(VolatileModel):
        word = models.CharField(max_length=5, primary_key=True)
        value = models.BooleanField()

        def __str__(self):
            return "{} == {}".format(self.word, self.value)


    manager = YesNo.objects
    manager.create(word="Yes", value=True)
    manager.create(word="No", value=False)
    manager.create(word="Maybe", value=True)
    print(manager.all())
    model = manager.get(pk="Maybe")
    model.value = False
    model.save()
    print(manager.filter(pk="Maybe"))


Coded for Django 1.5, may need some adaptation for newer versions.
"""
import copy

from django.db import connections
from django.db.models import Manager, Model
from django.db.models.base import ModelBase
from django.db.models.query import QuerySet
from django.utils import six


def ignore(*args, **kwargs):
    pass


class VolatileDatabaseWrapper(object):
    """
    Database dummy, so we can use some methods that call transaction methods.
    """
    # enter_transaction_management = ignore
    # leave_transaction_management = ignore
    commit_unless_managed = ignore
    # rollback_unless_managed = ignore
    savepoint = ignore
    savepoint_commit = ignore
    # savepoint_rollback = ignore


# Name of the fake connection added to the connection handler.
DB_ALIAS = 'volatile-model-storage'

# This will be added to the connections under ``DB_ALIAS``.
DB_WRAPPER = VolatileDatabaseWrapper()


class VolatileQuerySet(object):
    """
    A partial implementation of the ``QuerySet`` API using key-sorted dict
    as the storage.

    Note that it does not postpone processing, creating or deleting models
    won't be reflected in existing query sets. Also note that unlike with
    vanilla you don't get multiple copies of model instances -- all queries
    return the same (last stored) instance.
    """
    def __init__(self, model):
        self.model = model
        self.storage = model.storage  # The underlying class-wide storage.
        self.items = copy.copy(self.storage)  # Filtered collection.
        # We'd like to reuse a few of QuerySet methods.
        self.db = None
        # Some parts of admin use QuerySet.query directly.
        self.query = type('', (), {})
        self.query.select_related = True
        self.query.order_by = []
        self.query.where = None
        # Ensure the fake database entry exists.
        setattr(connections._connections, DB_ALIAS, DB_WRAPPER)

    def __getitem__(self, k):
        # This may support a bit more slices than QuerySet.
        return self.items.values()[k]

    def __repr__(self):
        # Use the QuerySet implementation.
        return QuerySet.__repr__.__func__(self)

    def __len__(self):
        # The size of the filtered collection.
        return len(self.items)

    def iterator(self):
        # The items are kept sorted properly, so we can just iterate values.
        return six.itervalues(self.items)

    def count(self):
        # The size of the filtered collection.
        return len(self.items)

    def get(self, *args, **kwargs):
        # Delegated to filter(), almost the same as QuerySet.get().
        filtered = self.filter(*args, **kwargs)
        count = filtered.count()
        if count == 1:
            return filtered[0]
        elif count == 0:
            raise self.model.DoesNotExist()
        else:
            raise self.model.MultipleObjectsReturned()

    def create(self, **kwargs):
        # This calls Model.save().
        QuerySet.create.__func__(self, **kwargs)

    def bulk_create(self, objs, batch_size=None):
        # Django does not call Model.save() or send signals in bulk methods.
        # We also handle auto-incrementing ids here.
        storage = self.storage
        max_pk = storage.keys()[-1] if storage else -1
        for obj in objs:
            pk = obj.pk
            if pk is None:
                max_pk += 1
                pk = max_pk
            elif isinstance(pk, six.integer_types) and pk > max_pk:
                max_pk = pk
            storage[pk] = obj
        self.storage = sorted(storage)
        self.items = copy.copy(self.storage)

    def get_or_create(self, **kwargs):
        # This handles arguments and calls Model.save().
        return QuerySet.get_or_create.__func__(self, **kwargs)

    def _update(self, values):
        # This is called from save_base(), which already modified the stored
        # instance, thus we don't need to do anything.
        pass

    def exists(self):
        return bool(self.storage)

    def filter(self, *args, **kwargs):
        # Could support some more comparisons. Filtering by non-primary-key
        # fields could also be implemented (with linear cost).
        if kwargs != {} and kwargs.keys() != ['pk']:
            raise ValueError("Only filtering by primary key is "
                             "supported ({}).".format(kwargs))
        if kwargs == {}:
            return self._clone()
        items = self.items
        value = kwargs['pk']
        filtered_items = {pk: items[pk] for pk in items if pk == value}
        return self._clone(filtered_items)

    def select_related(self, *fields, **kwargs):
        # We're storing models, these may only be created with references to
        # other loaded models.
        return self

    def order_by(self, *field_names):
        # TODO: We just ignore the ordering for now.
        return self

    def using(self, alias):
        if alias != DB_ALIAS:
            raise ValueError("Only operates on the in-memory storage.")
        return self

    def _clone(self, new_items=None):
        # Same, but independent, filters.
        clone = copy.copy(self)
        clone.items = copy.copy(self.items) if new_items is None else new_items
        return clone


class VolatileManager(Manager):
    """
    Manager that uses ``VolatileQuerySet`` for all operations.
    """
    use_for_related_fields = True  # Also use for Django-created managers.

    def get_empty_query_set(self):
        # Used mostly for Manager.none().
        raise NotImplementedError()

    def get_query_set(self):
        # Most manager methods are delegated to query set.
        return VolatileQuerySet(self.model)

    def _insert(self, objs, fields, **kwargs):
        # Called from Model.save().
        VolatileQuerySet(self.model).bulk_create(objs)


class VolatileModelBase(ModelBase):
    """
    Creates a class-wide database (dict) for each volatile model subclass.
    The storage dict is kept sorted at all times.
    """
    def __new__(cls, name, bases, attrs):
        abstract = getattr(attrs.get('Meta', None), 'abstract', False)
        new_class = super(VolatileModelBase, cls).__new__(cls, name, bases, attrs)
        if name != 'NewBase' and not abstract:
            new_class.storage = {}
        return new_class


class VolatileModel(six.with_metaclass(VolatileModelBase, Model)):
    """
    Base for in-memory models, deriving from this class will make sure that
    class-storage is available for the model and the volatile manager and
    storage are used on default (overriding routing).
    """
    objects = VolatileManager()

    class Meta:
        abstract = True
        managed = False

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        # Model.save() defaults to using the router-selected database.
        if using is None:
            using = DB_ALIAS
        return super(VolatileModel, self).save(force_insert, force_update, using, update_fields)

    def delete(self, using=None):
        # Model.delete() defaults to using the router-selected database.
        if using is None:
            using = DB_ALIAS
        return super(VolatileModel, self).delete(using)
