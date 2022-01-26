from django.contrib import admin
from django_audit_fields.admin import audit_fieldset_tuple
from edc_crf.admin import crf_status_fieldset_tuple
from edc_model_admin import SimpleHistoryAdmin

from ..admin_site import mocca_subject_admin
from ..forms import HivInitialReviewForm
from ..models import HivInitialReview
from .modeladmin_mixins import CrfModelAdminMixin


@admin.register(HivInitialReview, site=mocca_subject_admin)
class HivInitialReviewAdmin(CrfModelAdminMixin, SimpleHistoryAdmin):
    form = HivInitialReviewForm

    fieldsets = (
        (None, {"fields": ("subject_visit", "report_datetime")}),
        (
            "Diagnosis and Care",
            {
                "fields": (
                    "dx_ago",
                    "dx_date",
                    "dx_location",
                    "dx_location_other",
                    "receives_care",
                    "clinic",
                    "clinic_other",
                )
            },
        ),
        (
            "Monitoring and Treatment",
            {
                "fields": (
                    "arv_initiated",
                    "arv_initiation_ago",
                    "arv_initiation_actual_date",
                    "has_vl",
                    "vl",
                    "vl_quantifier",
                    "vl_date",
                    "has_cd4",
                    "cd4",
                    "cd4_date",
                ),
            },
        ),
        crf_status_fieldset_tuple,
        audit_fieldset_tuple,
    )

    radio_fields = {
        "arv_initiated": admin.VERTICAL,
        "clinic": admin.VERTICAL,
        "crf_status": admin.VERTICAL,
        "has_cd4": admin.VERTICAL,
        "has_vl": admin.VERTICAL,
        "receives_care": admin.VERTICAL,
        "vl_quantifier": admin.VERTICAL,
        "dx_location": admin.VERTICAL,
    }
