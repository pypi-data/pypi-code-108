from django.contrib import admin
from edc_model_admin import SimpleHistoryAdmin

from ..admin_site import mocca_prn_admin
from ..models import OffSchedule
from .modeladmin_mixins import EndOfStudyModelAdminMixin


@admin.register(OffSchedule, site=mocca_prn_admin)
class OffScheduleAdmin(EndOfStudyModelAdminMixin, SimpleHistoryAdmin):

    pass
