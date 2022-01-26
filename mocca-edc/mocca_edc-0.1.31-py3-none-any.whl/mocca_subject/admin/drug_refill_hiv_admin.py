from django.contrib import admin
from django.utils.safestring import mark_safe
from django_audit_fields.admin import audit_fieldset_tuple
from edc_crf.admin import crf_status_fieldset_tuple
from edc_form_label.form_label_modeladmin_mixin import FormLabelModelAdminMixin
from edc_model_admin import SimpleHistoryAdmin

from ..admin_site import mocca_subject_admin
from ..forms import DrugRefillHivForm
from ..models import DrugRefillHiv
from .modeladmin_mixins import CrfModelAdminMixin


@admin.register(DrugRefillHiv, site=mocca_subject_admin)
class DrugRefillHivAdmin(CrfModelAdminMixin, FormLabelModelAdminMixin, SimpleHistoryAdmin):
    form = DrugRefillHivForm

    additional_instructions = mark_safe(
        '<span style="color:orange">Note: Medications CRF must be completed first.</span>'
    )

    autocomplete_fields = ["rx"]

    fieldsets = (
        (None, {"fields": ("subject_visit", "report_datetime")}),
        (
            "ART Drug Refill Today",
            {
                "fields": (
                    "rx",
                    "rx_other",
                    "rx_modified",
                    "modifications",
                    "modifications_other",
                    "modifications_reason",
                    "modifications_reason_other",
                    "return_in_days",
                )
            },
        ),
        crf_status_fieldset_tuple,
        audit_fieldset_tuple,
    )

    filter_horizontal = ["modifications", "modifications_reason"]

    radio_fields = {
        "crf_status": admin.VERTICAL,
        "rx_modified": admin.VERTICAL,
    }
