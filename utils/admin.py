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
