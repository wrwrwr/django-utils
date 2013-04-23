from django.contrib.admin import ModelAdmin

from modeltranslation.admin import TranslationAdmin


class TabbedTranslationAdmin(TranslationAdmin):
    class Media:
        js = (
            '//ajax.googleapis.com/ajax/libs/jquery/1/jquery.min.js',
            '//ajax.googleapis.com/ajax/libs/jqueryui/1/jquery-ui.min.js',
            'modeltranslation/js/tabbed_translation_fields.js',
        )


class SortableAdmin(ModelAdmin):
    class Media:
        js = (
            '//ajax.googleapis.com/ajax/libs/jquery/1/jquery.min.js',
            '//ajax.googleapis.com/ajax/libs/jqueryui/1/jquery-ui.min.js',
            'scripts/admin-sortable.js',
        )


def make_changelist_mutable(model_admin):
    """
    Casts list display attributes to lists.
    """
    for setting in ('list_display', 'list_display_links', 'list_editable'):
        if hasattr(model_admin, setting):
            setattr(model_admin, setting, list(getattr(model_admin, setting)))


def remove_changelist_field(model_admin, field):
    """
    Removes a field from all list display lists.
    """
    for setting in ('list_display', 'list_display_links', 'list_editable'):
        try:
            field_list = list(getattr(model_admin, setting))
            field_list.remove(field)
        except (AttributeError, ValueError):
            pass
        else:
            setattr(model_admin, setting, field_list)


def make_fields_mutable(model_admin):
    """
    Casts ``fields`` to a list in all fieldsets.
    """
    for fieldset in model_admin.fieldsets:
        fieldset[1]['fields'] = list(fieldset[1]['fields'])


def collapsible_status(model_admin):
    """
    Mezzanine specific. Puts ``status``, ``available`` and publication dates
    under a single collapsed fieldset.
    """
    fields = model_admin.fieldsets[0][1]['fields']
    status_fields = []
    for f in (
            'status',
            ('status', 'available'),
            ('publish_date', 'expiry_date')):
        if f in fields:
            fields.remove(f)
            status_fields.append(f)
    model_admin.fieldsets = list(model_admin.fieldsets)
    model_admin.fieldsets.insert(1,
        (_("Status"), {
            'fields': status_fields,
            'classes': ('collapse-closed',)
        }))


def collapsible_menus(model_admin):
    """
    Mezzanine specific. Puts menu selection and ``login_required`` under a
    collapsed fieldset.
    """
    fields = model_admin.fieldsets[0][1]['fields']
    menus_fields = []
    for f in ('in_menus', 'login_required'):
        if f in fields:
            fields.remove(f)
            menus_fields.append(f)
    model_admin.fieldsets = list(model_admin.fieldsets)
    model_admin.fieldsets.insert(1,
        (_("Menus"), {
            'fields': menus_fields,
            'classes': ('collapse-closed',)
        }))
