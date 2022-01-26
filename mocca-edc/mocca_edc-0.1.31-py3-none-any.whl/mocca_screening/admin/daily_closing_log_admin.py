from django.contrib import admin
from django.utils.safestring import mark_safe
from django_audit_fields.admin import audit_fieldset_tuple
from edc_model_admin import ModelAdminFormInstructionsMixin, TemplatesModelAdminMixin
from edc_model_admin.model_admin_simple_history import SimpleHistoryAdmin

from ..admin_site import mocca_screening_admin
from ..forms import DailyClosingLogForm
from ..models import DailyClosingLog


@admin.register(DailyClosingLog, site=mocca_screening_admin)
class DailyClosingLogAdmin(
    TemplatesModelAdminMixin, ModelAdminFormInstructionsMixin, SimpleHistoryAdmin
):
    form = DailyClosingLogForm
    date_hierarchy = "log_date"
    show_object_tools = True
    additional_instructions = mark_safe(
        "<font color='orange'><B>This form should be completed "
        "at the end of each clinic day.</B></font>"
    )

    fieldsets = (
        [None, {"fields": ("log_date", "site")}],
        [
            "Daily Closing Log",
            {
                "fields": (
                    "clinic_services",
                    "attended",
                    "selection_method",
                    "approached",
                    "agreed_to_screen",
                    "comment",
                )
            },
        ],
        audit_fieldset_tuple,
    )

    list_display = (
        "log_date",
        "clinic_services",
        "number_attended",
        "number_approached",
        "number_agreed_to_screen",
    )

    list_filter = ("log_date", "clinic_services", "created", "modified")

    radio_fields = {
        "clinic_services": admin.VERTICAL,
        "selection_method": admin.VERTICAL,
    }

    def number_attended(self, obj):
        return obj.attended

    number_attended.short_description = "Attended"

    def number_approached(self, obj):
        return obj.approached

    number_approached.short_description = "Approached"

    def number_agreed_to_screen(self, obj):
        return obj.agreed_to_screen

    number_agreed_to_screen.short_description = "Agreed to Screen"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "site":
            try:
                site_id = request.site.id
            except AttributeError:
                site_id = None
            kwargs["queryset"] = db_field.related_model.objects.filter(pk=site_id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
