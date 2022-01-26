from django.contrib import admin
from edc_form_label.form_label_modeladmin_mixin import FormLabelModelAdminMixin
from edc_model_admin import SimpleHistoryAdmin

from ..admin_site import mocca_subject_admin
from ..forms import GlucoseBaselineForm
from ..models import GlucoseBaseline
from .modeladmin_mixins import CrfModelAdminMixin, GlucoseModelAdminMixin


@admin.register(GlucoseBaseline, site=mocca_subject_admin)
class GlucoseBaselineAdmin(
    GlucoseModelAdminMixin, CrfModelAdminMixin, FormLabelModelAdminMixin, SimpleHistoryAdmin
):

    form = GlucoseBaselineForm

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj=obj, **kwargs)
        form = self.replace_label_text(
            form, "since the last visit", "sometime in the past few months"
        )
        return form
