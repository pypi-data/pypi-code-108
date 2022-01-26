from django.contrib import admin
from django_audit_fields.admin import ModelAdminAuditFieldsMixin, audit_fieldset_tuple
from edc_model_admin import (
    ModelAdminFormAutoNumberMixin,
    ModelAdminFormInstructionsMixin,
    TemplatesModelAdminMixin,
)
from edc_model_admin.model_admin_simple_history import SimpleHistoryAdmin
from edc_sites import get_current_country

from ..admin_site import mocca_screening_admin
from ..forms import MoccaRegisterContactForm, MoccaRegisterForm
from ..mocca_original_sites import get_mocca_sites_by_country
from ..models import MoccaRegister, MoccaRegisterContact
from .changelist_buttons import (
    CareStatusButton,
    ScreeningButton,
    SubjectRefusalScreeningButton,
)
from .list_filters import CallListFilter, ContactAttemptsListFilter, ScreenedListFilter


class MoccaRegisterContactInlineMixin:
    model = MoccaRegisterContact
    form = MoccaRegisterContactForm
    extra = 0
    readonly_fields = ["report_datetime"]
    radio_fields = {
        "answered": admin.VERTICAL,
        "respondent": admin.VERTICAL,
        "survival_status": admin.VERTICAL,
        "willing_to_attend": admin.VERTICAL,
        "icc": admin.VERTICAL,
        "call_again": admin.VERTICAL,
    }


class AddMoccaRegisterContactInline(
    ModelAdminAuditFieldsMixin, MoccaRegisterContactInlineMixin, admin.StackedInline
):
    fieldsets = (
        [None, {"fields": ("report_datetime",)}],
        (
            "Details of the call",
            {
                "fields": (
                    "answered",
                    "respondent",
                    "survival_status",
                    "death_date",
                    "willing_to_attend",
                    "icc",
                    "next_appt_date",
                    "call_again",
                    "comment",
                ),
            },
        ),
    )
    verbose_name = "New Contact Attempt"
    verbose_name_plural = "New Contact Attempt"

    def has_change_permission(self, request, obj=None):
        return True

    def get_queryset(self, request):
        return MoccaRegisterContact.objects.none()


class ViewMoccaRegisterContactInline(
    ModelAdminAuditFieldsMixin, MoccaRegisterContactInlineMixin, admin.StackedInline
):

    fieldsets = (
        [None, {"fields": (("report_datetime", "answered"),)}],
        (
            "Details of the call",
            {
                "classes": ("collapse",),
                "fields": (
                    "respondent",
                    "survival_status",
                    "death_date",
                    "willing_to_attend",
                    "icc",
                    "next_appt_date",
                    "call_again",
                    "comment",
                ),
            },
        ),
    )
    verbose_name = "Past Contact Attempt"
    verbose_name_plural = "Past Contact Attempts"

    def has_add_permission(self, request, obj):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(MoccaRegister, site=mocca_screening_admin)
class MoccaRegisterAdmin(
    TemplatesModelAdminMixin,
    ModelAdminFormAutoNumberMixin,
    ModelAdminFormInstructionsMixin,
    SimpleHistoryAdmin,
):
    form = MoccaRegisterForm
    inlines = [AddMoccaRegisterContactInline, ViewMoccaRegisterContactInline]
    ordering = ["mocca_study_identifier"]
    show_object_tools = True
    list_per_page = 15

    changelist_url_name = "mocca_screening_admin:mocca_screening_moccaregister_changelist"

    fieldsets = (
        [None, {"fields": ("screening_identifier",)}],
        [
            "Original Enrollment Data",
            {
                "fields": (
                    "mocca_study_identifier",
                    "mocca_screening_identifier",
                    "mocca_site",
                    "first_name",
                    "last_name",
                    "initials",
                    "gender",
                    "dob",
                    "birth_year",
                    "age_in_years",
                )
            },
        ],
        [
            "Contact",
            {
                "fields": (
                    "notes",
                    "tel_one",
                    "tel_two",
                    "tel_three",
                    "best_tel",
                    "subject_present",
                )
            },
        ],
        audit_fieldset_tuple,
    )

    list_display = (
        "mocca_patient",
        "call_now",
        "care_status",
        "refusal",
        "screen",
        "date_last_called",
        "next_appt_date",
        "user_modified",
    )

    list_display_links = ("mocca_patient", "call_now")

    list_filter = (
        ScreenedListFilter,
        ContactAttemptsListFilter,
        CallListFilter,
        "date_last_called",
        "next_appt_date",
        "gender",
        "created",
        "modified",
    )

    radio_fields = {
        "best_tel": admin.VERTICAL,
        "call": admin.VERTICAL,
        "gender": admin.VERTICAL,
        "mocca_site": admin.VERTICAL,
        "subject_present": admin.VERTICAL,
    }

    search_fields = (
        "mocca_study_identifier",
        "initials",
        "mocca_screening_identifier",
        "screening_identifier",
        "user_modified",
        "user_created",
    )

    def call_now(self, obj):
        return f"{obj.call} ({obj.contact_attempts})"

    call_now.admin_order_field = "call"

    def mocca_patient(self, obj):
        return str(obj)

    mocca_patient.admin_order_field = "mocca_study_identifier"

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj=None)
        fields = [
            "contact_attempts",
            "screening_identifier",
            "mocca_study_identifier",
            "mocca_screening_identifier",
            "mocca_site",
        ]
        readonly_fields = list(readonly_fields)
        for f in fields:
            if f not in readonly_fields:
                readonly_fields.append(f)
        readonly_fields = tuple(readonly_fields)
        return readonly_fields

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "mocca_site":
            sites = get_mocca_sites_by_country(country=get_current_country())
            kwargs["queryset"] = db_field.related_model.objects.filter(
                name__in=[v.name for v in sites.values()]
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def screen(self, obj=None):
        """Returns a rendered screening button or `empty` display
        value.
        """
        button = ScreeningButton(
            mocca_register=obj,
            changelist_url_name=self.changelist_url_name,
        )
        return button.rendered or self.get_empty_value_display()

    def care_status(self, obj=None):
        """Returns a rendered care_status button or `empty` display
        value.
        """
        button = CareStatusButton(
            mocca_register=obj,
            changelist_url_name=self.changelist_url_name,
        )
        return button.rendered or self.get_empty_value_display()

    care_status.short_description = "Care Status"

    def refusal(self, obj=None):
        """Returns a rendered care_status button or `empty` display
        value.
        """
        button = SubjectRefusalScreeningButton(
            mocca_register=obj,
            changelist_url_name=self.changelist_url_name,
        )
        return button.rendered or self.get_empty_value_display()
