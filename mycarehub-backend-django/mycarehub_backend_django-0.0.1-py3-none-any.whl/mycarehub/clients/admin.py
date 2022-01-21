from django.contrib import admin
from django.contrib.admin.decorators import display

from mycarehub.common.admin import BaseAdmin

from .models import (
    Caregiver,
    Client,
    ClientFacility,
    HealthDiaryAttachment,
    HealthDiaryEntry,
    HealthDiaryQuote,
    Identifier,
    RelatedPerson,
    SecurityQuestion,
    SecurityQuestionResponse,
    ServiceRequest,
)


@admin.register(Identifier)
class IdentifierAdmin(BaseAdmin):
    pass


@admin.register(SecurityQuestion)
class SecurityQuestionAdmin(BaseAdmin):
    pass


@admin.register(SecurityQuestionResponse)
class SecurityQuestionResponseAdmin(BaseAdmin):
    pass


@admin.register(RelatedPerson)
class RelatedPersonAdmin(BaseAdmin):
    pass


@admin.register(Caregiver)
class CaregiverAdmin(BaseAdmin):
    pass


@admin.register(Client)
class ClientAdmin(BaseAdmin):
    list_display = (
        "get_user_name",
        "client_type",
        "enrollment_date",
    )
    date_hierarchy = "enrollment_date"
    exclude = (
        "fhir_patient_id",
        "emr_health_record_id",
    )  # type: ignore

    @display(ordering="user__name", description="User")
    def get_user_name(self, obj):
        return obj.user.name if obj.user else "-"


@admin.register(ClientFacility)
class ClientFacilityAdmin(BaseAdmin):
    pass


@admin.register(HealthDiaryEntry)
class HealthDiaryEntryAdmin(BaseAdmin):
    list_display = (
        "client",
        "entry_type",
        "mood",
        "note",
        "share_with_health_worker",
        "shared_at",
    )
    date_hierarchy = "created"


@admin.register(HealthDiaryAttachment)
class HealthDiaryAttachmentAdmin(BaseAdmin):
    list_display = (
        "title",
        "content_type",
        "description",
        "health_diary_entry",
        "size",
        "aspect_ratio",
    )
    date_hierarchy = "creation_date"


@admin.register(HealthDiaryQuote)
class HealthDiaryQuoteAdmin(BaseAdmin):
    list_display = ("quote",)


@admin.register(ServiceRequest)
class ServiceRequestAdmin(BaseAdmin):
    list_display = ("client", "request_type", "status")
