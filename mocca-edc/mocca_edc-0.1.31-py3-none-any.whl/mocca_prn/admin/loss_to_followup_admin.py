from django.contrib import admin
from edc_ltfu.modeladmin_mixin import LtfuModelAdminMixin
from edc_model_admin import SimpleHistoryAdmin
from edc_model_admin.dashboard import ModelAdminSubjectDashboardMixin

from ..admin_site import mocca_prn_admin
from ..forms import LossToFollowupForm
from ..models import LossToFollowup


@admin.register(LossToFollowup, site=mocca_prn_admin)
class LossToFollowupAdmin(
    LtfuModelAdminMixin, ModelAdminSubjectDashboardMixin, SimpleHistoryAdmin
):

    form = LossToFollowupForm
