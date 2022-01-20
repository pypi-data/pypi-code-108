# coding: utf-8
from __future__ import unicode_literals

from django.contrib import admin
from django.utils.translation import gettext as _

from .custom_admin import CustomAdmin
from .views import ListModelView, EditTranslationView, ImportTranslationView


class TranslationAdmin(CustomAdmin):
    app_label = "modeltranslation_rosetta"
    module_name = "trans"
    verbose_name = _("Modeltranslate")
    verbose_name_plural = _("Modeltranslates")

    changelist_view = ListModelView
    change_view = EditTranslationView

    view_classes = {"import_trans": (r"^import_trans/$", ImportTranslationView)}

    def has_add_permission(self, request):
        return False


TranslationAdmin.register_at(admin.site)
