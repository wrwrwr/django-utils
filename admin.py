from django.contrib import admin

import modeltranslation.admin


class TabbedTranslationAdmin(modeltranslation.admin.TranslationAdmin):
	class Media:
		js = (
            'http://code.jquery.com/jquery-1.9.0.min.js',
            'http://code.jquery.com/ui/1.10.0/jquery-ui.min.js',
            'modeltranslation/js/tabbed_translation_fields.js',
		)
		css = {
			'screen': ('http://code.jquery.com/ui/1.10.0/themes/base/jquery-ui.css',),
		}


class SortableAdmin(admin.ModelAdmin):
	class Media:
		js = (
			'scripts/jquery.min.js',
			'scripts/jquery-ui.min.js',
			'scripts/admin-sortable.js',
		)

