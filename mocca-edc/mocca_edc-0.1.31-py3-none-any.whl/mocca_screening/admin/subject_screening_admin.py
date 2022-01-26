from django.contrib import admin
from django.template.loader import render_to_string
from django.urls.base import reverse
from django.urls.exceptions import NoReverseMatch
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from django_audit_fields.admin import audit_fieldset_tuple
from edc_dashboard.url_names import url_names
from edc_model_admin import SimpleHistoryAdmin
from edc_model_admin.dashboard import ModelAdminSubjectDashboardMixin
from edc_screening import format_reasons_ineligible

from ..admin_site import mocca_screening_admin
from ..forms import SubjectScreeningForm
from ..models import SubjectScreening
from .fieldsets import care_status_fieldset


@admin.register(SubjectScreening, site=mocca_screening_admin)
class SubjectScreeningAdmin(ModelAdminSubjectDashboardMixin, SimpleHistoryAdmin):
    form = SubjectScreeningForm

    post_url_on_delete_name = "screening_listboard_url"
    subject_listboard_url_name = "screening_listboard_url"

    additional_instructions = (
        "Patients must meet ALL of the inclusion criteria and NONE of the "
        "exclusion criteria in order to proceed"
    )

    fieldsets = (
        [None, {"fields": ("report_datetime",)}],
        [
            "Original MOCCA information",
            {
                "fields": (
                    "mocca_participant",
                    "mocca_register",
                    "screening_consent",
                )
            },
        ],
        care_status_fieldset,
        [
            "Consent",
            {
                "fields": (
                    "willing_to_consent",
                    "pregnant",
                    "requires_acute_care",
                )
            },
        ],
        audit_fieldset_tuple,
    )

    list_display = (
        "screening_identifier",
        "eligiblity_status",
        "demographics",
        "integrated_care",
        "will_consent",
        "reasons",
        "report_datetime",
        "user_created",
        "created",
    )

    list_filter = (
        "report_datetime",
        "gender",
        "eligible",
        "consented",
        "refused",
        "eligible",
        "icc",
        "willing_to_consent",
    )

    search_fields = (
        "screening_identifier",
        "subject_identifier",
        "mocca_register__mocca_study_identifier",
        "initials",
        "reasons_ineligible",
    )

    radio_fields = {
        "mocca_participant": admin.VERTICAL,
        "mocca_site": admin.VERTICAL,
        "gender": admin.VERTICAL,
        "screening_consent": admin.VERTICAL,
        "unsuitable_agreed": admin.VERTICAL,
        "care": admin.VERTICAL,
        "care_facility_location": admin.VERTICAL,
        "icc": admin.VERTICAL,
        "icc_not_in_reason": admin.VERTICAL,
        "icc_since_mocca": admin.VERTICAL,
        "willing_to_consent": admin.VERTICAL,
        "pregnant": admin.VERTICAL,
        "requires_acute_care": admin.VERTICAL,
    }

    def get_readonly_fields(self, request, obj=None):
        fields = super().get_readonly_fields(request, obj=obj)
        if obj and "mocca_register" not in fields:
            fields = list(fields)
            fields.append("mocca_register")
            fields = tuple(fields)
        return fields

    def post_url_on_delete_kwargs(self, request, obj):
        return {}

    def demographics(self, obj=None):
        return mark_safe(
            f"{obj.get_gender_display()} {obj.age_in_years}yrs {obj.initials.upper()}"
        )

    def integrated_care(self, obj=None):
        return obj.get_icc_display()

    def will_consent(self, obj=None):
        return obj.get_willing_to_consent_display()

    def reasons(self, obj=None):
        return format_reasons_ineligible(obj.reasons_ineligible)

    def eligiblity_status(self, obj=None):
        return "Eligible" if obj.eligible else "Ineligible"

    def dashboard(self, obj=None, label=None):
        try:
            url = reverse(
                self.get_subject_dashboard_url_name(),
                kwargs=self.get_subject_dashboard_url_kwargs(obj),
            )
        except NoReverseMatch:
            url = reverse(url_names.get("screening_listboard_url"), kwargs={})
            context = dict(
                title=_("Go to screening listboard"),
                url=f"{url}?q={obj.screening_identifier}",
                label=label,
            )
        else:
            context = dict(title=_("Go to subject dashboard"), url=url, label=label)
        return render_to_string("dashboard_button.html", context=context)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "mocca_register" and request.GET.get("mocca_register"):
            kwargs["queryset"] = db_field.related_model.objects.filter(
                pk=request.GET.get("mocca_register", 0)
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
