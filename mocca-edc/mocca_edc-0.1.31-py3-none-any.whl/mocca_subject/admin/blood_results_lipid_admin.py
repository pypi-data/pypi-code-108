from django.contrib import admin
from edc_blood_results.admin import BloodResultsModelAdminMixin
from edc_blood_results.fieldsets import BloodResultFieldset

from ..admin_site import mocca_subject_admin
from ..forms import BloodResultsLipidForm
from ..models import BloodResultsLipid
from .modeladmin_mixins import CrfModelAdmin


@admin.register(BloodResultsLipid, site=mocca_subject_admin)
class BloodResultsLipidAdmin(BloodResultsModelAdminMixin, CrfModelAdmin):
    form = BloodResultsLipidForm
    fieldsets = BloodResultFieldset(
        BloodResultsLipid.lab_panel, model_cls=BloodResultsLipid
    ).fieldsets
