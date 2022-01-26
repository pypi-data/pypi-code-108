from django.contrib import admin
from django.utils.html import format_html
from django_audit_fields.admin import audit_fieldset_tuple
from edc_crf.admin import crf_status_fieldset_tuple
from edc_form_label.form_label_modeladmin_mixin import FormLabelModelAdminMixin
from edc_model_admin import SimpleHistoryAdmin
from edc_phq9.fieldsets import get_phq9_fieldsets
from edc_phq9.model_admin_mixins import get_phq9_radio_fields

from ..admin_site import mocca_subject_admin
from ..forms import PatientHealthForm
from ..models import PatientHealth
from .modeladmin_mixins import CrfModelAdminMixin

radio_fields = get_phq9_radio_fields()
radio_fields.update({"crf_status": admin.VERTICAL, "ph9_performed": admin.VERTICAL})


@admin.register(PatientHealth, site=mocca_subject_admin)
class PatientHealthAdmin(CrfModelAdminMixin, FormLabelModelAdminMixin, SimpleHistoryAdmin):
    form = PatientHealthForm

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "subject_visit",
                    "report_datetime",
                    "ph9_performed",
                    "ph9_not_performed_reason",
                )
            },
        ),
        get_phq9_fieldsets(),
        crf_status_fieldset_tuple,
        audit_fieldset_tuple,
    )

    radio_fields = radio_fields
