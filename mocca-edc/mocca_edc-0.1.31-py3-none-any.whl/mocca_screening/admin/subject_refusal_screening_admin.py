from django.contrib import admin
from django_audit_fields.admin import audit_fieldset_tuple
from edc_model_admin import (
    ModelAdminFormAutoNumberMixin,
    ModelAdminFormInstructionsMixin,
    ModelAdminNextUrlRedirectMixin,
    TemplatesModelAdminMixin,
)
from edc_model_admin.model_admin_simple_history import SimpleHistoryAdmin

from ..admin_site import mocca_screening_admin
from ..forms import SubjectRefusalScreeningForm
from ..models import SubjectRefusalScreening


@admin.register(SubjectRefusalScreening, site=mocca_screening_admin)
class SubjectRefusalScreeningAdmin(
    TemplatesModelAdminMixin,
    ModelAdminFormAutoNumberMixin,
    ModelAdminFormInstructionsMixin,
    ModelAdminNextUrlRedirectMixin,
    SimpleHistoryAdmin,
):
    form = SubjectRefusalScreeningForm

    fieldsets = (
        [
            None,
            {
                "fields": (
                    "mocca_register",
                    "report_datetime",
                    "reason",
                    "other_reason",
                    "comment",
                )
            },
        ],
        audit_fieldset_tuple,
    )

    list_display = (
        "mocca_register",
        "report_datetime",
        "reason",
        "user_created",
        "created",
    )

    list_filter = ("report_datetime", "reason")

    search_fields = (
        "mocca_register__mocca_study_identifier",
        "mocca_register__initials",
        "mocca_register__mocca_screening_identifier",
    )

    radio_fields = {"reason": admin.VERTICAL}

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "mocca_register" and request.GET.get("mocca_register"):
            kwargs["queryset"] = db_field.related_model.objects.filter(
                pk=request.GET.get("mocca_register", 0)
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
