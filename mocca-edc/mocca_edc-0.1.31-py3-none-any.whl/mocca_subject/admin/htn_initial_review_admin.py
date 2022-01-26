from django.contrib import admin
from django_audit_fields.admin import audit_fieldset_tuple
from edc_crf.admin import crf_status_fieldset_tuple
from edc_form_label.form_label_modeladmin_mixin import FormLabelModelAdminMixin
from edc_model_admin import SimpleHistoryAdmin

from ..admin_site import mocca_subject_admin
from ..forms import HtnInitialReviewForm
from ..models import HtnInitialReview
from .modeladmin_mixins import CrfModelAdminMixin


@admin.register(HtnInitialReview, site=mocca_subject_admin)
class HtnInitialReviewAdmin(CrfModelAdminMixin, FormLabelModelAdminMixin, SimpleHistoryAdmin):

    form = HtnInitialReviewForm

    fieldsets = (
        (None, {"fields": ("subject_visit", "report_datetime")}),
        (
            "Diagnosis and Treatment",
            {
                "fields": (
                    "dx_ago",
                    "dx_date",
                    "dx_location",
                    "dx_location_other",
                    "managed_by",
                    "med_start_ago",
                )
            },
        ),
        crf_status_fieldset_tuple,
        audit_fieldset_tuple,
    )

    radio_fields = {
        "crf_status": admin.VERTICAL,
        "managed_by": admin.VERTICAL,
        "dx_location": admin.VERTICAL,
    }

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj=obj, **kwargs)
        form = self.replace_label_text(
            form, "ncd_condition_label", self.model.ncd_condition_label
        )
        return form
