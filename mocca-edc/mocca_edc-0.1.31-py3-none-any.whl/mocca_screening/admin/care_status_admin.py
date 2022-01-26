from django.contrib import admin
from django_audit_fields import audit_fieldset_tuple
from edc_model_admin import (
    ModelAdminFormInstructionsMixin,
    ModelAdminNextUrlRedirectMixin,
    SimpleHistoryAdmin,
    TemplatesModelAdminMixin,
)

from ..admin_site import mocca_screening_admin
from ..forms import CareStatusForm
from ..models import CareStatus
from .fieldsets import care_status_fieldset


@admin.register(CareStatus, site=mocca_screening_admin)
class CareStatusAdmin(
    TemplatesModelAdminMixin,
    ModelAdminFormInstructionsMixin,
    ModelAdminNextUrlRedirectMixin,
    SimpleHistoryAdmin,
):
    form = CareStatusForm

    fieldsets = (
        [None, {"fields": ("mocca_register", "report_datetime", "willing_to_answer")}],
        care_status_fieldset,
        audit_fieldset_tuple,
    )

    list_display = (
        "mocca_register",
        "report_datetime",
        "care",
        "care_facility_location",
        "icc",
        "user_created",
        "created",
    )

    radio_fields = {
        "care": admin.VERTICAL,
        "care_facility_location": admin.VERTICAL,
        "icc": admin.VERTICAL,
        "icc_not_in_reason": admin.VERTICAL,
        "icc_since_mocca": admin.VERTICAL,
    }

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "mocca_register" and request.GET.get("mocca_register"):
            kwargs["queryset"] = db_field.related_model.objects.filter(
                pk=request.GET.get("mocca_register", 0)
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
