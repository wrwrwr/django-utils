from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.utils.translation import ugettext_lazy as _

from mezzanine.core.admin import DisplayableAdmin
from mezzanine.pages.admin import PageAdminForm

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


def separate_page_admin(page_models, page_admins):
    """
    Mezzanine. Makes an admin view / menu entry for a subset of pages' types.

    Examples:

        # Cartridge category administration split from other content types.
        separate_page_admin(Category, CategoryAdmin)

        # View with just subpages and galleries (add RichTextPage to the menu).
        separate_page_admin((RichTextPage, Gallery), (PageAdmin, GalleryAdmin))
    """
    if not isinstance(page_models, (tuple, list)):
        page_models = [page_models]
    if not isinstance(page_admins, (tuple, list)):
        page_admins = [page_admins]

    for page_admin, page_model in zip(page_admins, page_models):

        class SeparatePageAdmin(page_admin):
            @classmethod
            def get_content_models(cls):
                # PageAdmin.get_content_models side effects.
                page_admin.get_content_models()
                return page_models

            def in_menu(self):
                return self.model == page_models[0]

            def changelist_view(self, request, **kwargs):
                kwargs.setdefault('extra_context', {})
                kwargs['extra_context']['page_models'] = \
                    self.get_content_models()
                return DisplayableAdmin.changelist_view(self, request,
                                                        **kwargs)

        admin.site.unregister(page_model)
        admin.site.register(page_model, SeparatePageAdmin)


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


def initial_in_menus(page_admin, in_menus):
    """
    Chooses some initial menus for a page subtype.
    """
    class InitialInMenusForm(PageAdminForm):
        def __init__(self, *args, **kwargs):
            super(InitialInMenusForm, self).__init__(*args, **kwargs)
            if not 'in_menus' in self.initial:
                self.initial['in_menus'] = in_menus

    page_admin.form = InitialInMenusForm
