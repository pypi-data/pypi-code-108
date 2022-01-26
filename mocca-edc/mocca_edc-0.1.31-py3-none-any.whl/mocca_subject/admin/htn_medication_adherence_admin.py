from django.contrib import admin
from django_audit_fields import audit_fieldset_tuple
from edc_adherence.model_admin_mixin import (
    MedicationAdherenceAdminMixin,
    get_visual_score_fieldset_tuple,
    missed_medications_fieldset_tuple,
)
from edc_form_label.form_label_modeladmin_mixin import FormLabelModelAdminMixin
from edc_model_admin import SimpleHistoryAdmin

from ..admin_site import mocca_subject_admin
from ..forms import HtnMedicationAdherenceForm
from ..models import HtnMedicationAdherence
from .modeladmin_mixins import CrfModelAdminMixin


@admin.register(HtnMedicationAdherence, site=mocca_subject_admin)
class HtnMedicationAdherenceAdmin(
    MedicationAdherenceAdminMixin,
    CrfModelAdminMixin,
    FormLabelModelAdminMixin,
    SimpleHistoryAdmin,
):

    form = HtnMedicationAdherenceForm

    fieldsets = (
        (None, {"fields": ("subject_visit", "report_datetime")}),
        get_visual_score_fieldset_tuple(),
        missed_medications_fieldset_tuple,
        audit_fieldset_tuple,
    )
