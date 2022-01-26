from django.contrib import admin
from django_audit_fields import audit_fieldset_tuple
from edc_adherence.model_admin_mixin import (
    MedicationAdherenceAdminMixin,
    get_visual_score_fieldset_tuple,
    missed_medications_fieldset_tuple,
)
from edc_model_admin import SimpleHistoryAdmin

from ..admin_site import mocca_subject_admin
from ..forms import CholMedicationAdherenceForm
from ..models import CholMedicationAdherence
from .modeladmin_mixins import CrfModelAdminMixin


@admin.register(CholMedicationAdherence, site=mocca_subject_admin)
class CholMedicationAdherenceAdmin(
    MedicationAdherenceAdminMixin,
    CrfModelAdminMixin,
    SimpleHistoryAdmin,
):

    form = CholMedicationAdherenceForm

    fieldsets = (
        (None, {"fields": ("subject_visit", "report_datetime")}),
        get_visual_score_fieldset_tuple(),
        missed_medications_fieldset_tuple,
        audit_fieldset_tuple,
    )
