from django.contrib import admin
from edc_form_label import FormLabelModelAdminMixin
from edc_model_admin import SimpleHistoryAdmin

from ..admin_site import mocca_subject_admin
from ..forms import GlucoseFollowupForm
from ..models import GlucoseFollowup
from .modeladmin_mixins import CrfModelAdminMixin, GlucoseModelAdminMixin


@admin.register(GlucoseFollowup, site=mocca_subject_admin)
class GlucoseFollowupAdmin(
    GlucoseModelAdminMixin,
    CrfModelAdminMixin,
    FormLabelModelAdminMixin,
    SimpleHistoryAdmin,
):
    form = GlucoseFollowupForm
