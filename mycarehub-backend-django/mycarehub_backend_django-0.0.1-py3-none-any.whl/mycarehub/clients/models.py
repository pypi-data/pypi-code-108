from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models.enums import TextChoices
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from wagtail.snippets.models import register_snippet

from mycarehub.common.models import AbstractBase
from mycarehub.common.models.base_models import Attachment
from mycarehub.common.models.common_models import Address, Contact, Facility
from mycarehub.users.models import GenderChoices


class FlavourChoices(TextChoices):
    PRO = "PRO", _("PRO")
    CONSUMER = "CONSUMER", _("CONSUMER")


class ClientType(models.TextChoices):
    """
    The client types shown below can be expanded over time:

        - PMTCT: Prevention of mother-to-child transmission;
        all pregnant and breastfeeding women living with HIV.
        Exit when baby turns 2 years.

        - OTZ:  Operation Tripple Zero – for Zero Missed Appointments, zero
        missed Drugs and Zero Viral Load – all HIV positive persons aged
        between 0-19 years

        - OTZ Plus: All women aged between 10-24 years who are pregnant or
        breastfeeding. Exit when baby turns 2 years

        - HVL: High Viral Load – All HIV positive clients with a viral load
        >1,000 copies per ml. Exit when VL is <1,000 copies/ml

        - OVC: Orphans and Vulnerable Children – all children and
        adolescents aged 0-17 years who are enrolled with an OVC partner.
        Exit when they 18 years

        - DREAMS: Determined, Resilient, Empowered, AIDS-free, mentored and
        Safe – all HIV positive 9-24 year old women enroll with a DREAMS
        partner. Exit when they turn 25 years

        - High Risk Clients: all paediatric patients 0-4 yrs, all 0-4 year
        olds with a HIV negative guardian, all clients with low viremia
        (50-999 copies/ml). TI and new in the last 1 year, RTC in the last
        6 months.

        - Spouses of PMTCT mothers who have disclosed – exit when the
        baby turns 2 years

        - Youth: 20–24-year-olds both male and female. Exit when they turn
        25 years
    """

    PMTCT = "PMTCT", _("PMTCT")
    OTZ = "OTZ", _("OTZ")
    OTZ_PLUS = "OTZ_PLUS", _("OTZ Plus")
    HVL = "HVL", _("HVL")
    OVC = "OVC", _("OVC")
    DREAMS = "DREAMS", _("DREAMS")
    HIGH_RISK = "HIGH_RISK", _("High Risk Clients")
    SPOUSES = "SPOUSES", _("SPOUSES")
    YOUTH = "YOUTH", _("Youth")


class Languages(TextChoices):
    en = "en", "English"
    sw = "sw", "Swahili"


@register_snippet
class Identifier(AbstractBase):
    class IdentifierType(models.TextChoices):
        CCC = "CCC", _("Comprehensive Care Clinic Number")
        NATIONAL_ID = "NATIONAL_ID", _("National ID Document")
        BIRTH_CERTIFICATE = "BIRTH_CERTIFICATE", _("Birth Certificate")
        PASSPORT = "PASSPORT", _("Passport")
        UNIQUE = "UNIQUE", _("Unique Identifier")

    class IdentifierUse(models.TextChoices):
        OFFICIAL = "OFFICIAL", _("Official Identifier")
        TEMPORARY = "TEMPORARY", _("Temporary Identifier")
        OLD = "OLD", _("Old (retired) Identifier")

    identifier_type = models.CharField(
        choices=IdentifierType.choices, max_length=64, null=False, blank=False
    )
    identifier_value = models.TextField()
    identifier_use = models.CharField(
        choices=IdentifierUse.choices, max_length=64, null=False, blank=False
    )
    description = models.TextField()
    valid_from = models.DateTimeField(default=timezone.now)
    valid_to = models.DateTimeField(null=True, blank=True)
    is_primary_identifier = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.identifier_value} ({self.identifier_type}, {self.identifier_use})"

    class Meta(AbstractBase.Meta):
        unique_together = (
            "identifier_type",
            "identifier_value",
        )


@register_snippet
class SecurityQuestion(AbstractBase):
    class ResponseType(models.TextChoices):
        TEXT = "TEXT", _("Text Response")
        DATE = "DATE", _("Date Response")
        NUMBER = "NUMBER", _("Number Response")
        BOOLEAN = "BOOLEAN", _("Boolean Response")

    stem = models.TextField()
    description = models.TextField()
    sequence = models.IntegerField(default=0)
    response_type = models.CharField(max_length=32, choices=ResponseType.choices)
    flavour = models.CharField(
        choices=FlavourChoices.choices, max_length=32, null=True, blank=True
    )

    def __str__(self) -> str:
        return self.stem


@register_snippet
class SecurityQuestionResponse(AbstractBase):

    user = models.ForeignKey(get_user_model(), on_delete=models.PROTECT)
    question = models.ForeignKey(SecurityQuestion, on_delete=models.PROTECT)
    timestamp = models.DateTimeField(default=timezone.now)
    response = models.TextField()  # should be hashed
    is_correct = models.BooleanField(default=True)

    class Meta:
        unique_together = (
            "user",
            "question",
        )

    def __str__(self) -> str:
        return f"Response to '{self.question}' by '{self.user.name}'"


@register_snippet
class RelatedPerson(AbstractBase):
    class RelationshipType(TextChoices):
        SPOUSE = "SPOUSE", _("Spouse")
        NEXT_OF_KIN = "NEXT_OF_KIN", _("Next of kin")
        CHILD = "CHILD", _("Child")
        PARENT = "PARENT", _("Parent")
        SIBLING = "SIBLING", _("Sibling")
        NEIGHBOUR = "NEIGHBOUR", _("Neighbour")
        OTHER = "OTHER", _("Other")

    first_name = models.TextField()
    last_name = models.TextField()
    other_name = models.TextField()
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=16, choices=GenderChoices.choices)
    relationship_type = models.CharField(max_length=64, choices=RelationshipType.choices)
    addresses = models.ManyToManyField(
        Address,
        related_name="related_person_addresses",
    )
    contacts = models.ManyToManyField(
        Contact,
        related_name="related_person_contacts",
    )

    def __str__(self):
        return f"{self.first_name} {self.other_name} {self.last_name} ({self.relationship_type})"


class Caregiver(AbstractBase):
    """
    A caregiver is a person who is assigned to a client.
    """

    class CaregiverType(models.TextChoices):
        FATHER = "FATHER", _("Father")
        MOTHER = "MOTHER", _("Mother")
        SIBLING = "SIBLING", _("Sibling")
        HEALTHCARE_PROFESSIONAL = "HEALTHCARE_PROFESSIONAL", _("Healthcare Professional")

    first_name = models.TextField()
    last_name = models.TextField()
    caregiver_type = models.CharField(max_length=64, choices=CaregiverType.choices)
    phone_number = models.TextField(null=True, blank=True, max_length=14)


@register_snippet
class Client(AbstractBase):
    """
    A client is a patient or non-professional end user.
    """

    client_type = models.CharField(
        max_length=64,
        choices=ClientType.choices,
        null=False,
        blank=False,
    )

    # a client is a user, hence the one-to-one mapping
    # however, the client can be created (e.g via an integration) before
    # the user is invited. This is the reason why this field is nullable.
    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    # a client must have an enrollment date.
    # if it is not known, integration code should set a sensible default.
    enrollment_date = models.DateTimeField(null=False, blank=False, default=timezone.now)

    # the client's FHIR health record ID
    # optional because the client's FHIR health record is created after the client is enrolled
    fhir_patient_id = models.TextField(null=True, blank=True, unique=True)

    # the client's EMR ID
    # optional because it can be updated after the client is added e.g via an integration
    emr_health_record_id = models.TextField(null=True, blank=True, unique=True)

    # each client is assigned to a facility
    current_facility = models.ForeignKey(
        Facility,
        on_delete=models.PROTECT,
        null=False,
        blank=False,
    )

    # a client can be assigned a community health volunteer
    chv = models.ForeignKey(
        get_user_model(),
        on_delete=models.PROTECT,
        related_name="client_chvs",
        null=True,
        blank=True,
    )

    # a client can be assigned a treatment buddy
    treatment_buddy = models.TextField(null=True, blank=True)

    # a client should only be invited to the platform after they have been
    # counselled
    counselled = models.BooleanField(default=False)

    # a client can have multiple unique identifiers
    identifiers = models.ManyToManyField(Identifier, related_name="client_identifiers")

    addresses = models.ManyToManyField(
        Address,
        related_name="client_addresses",
        blank=True,
    )
    contacts = models.ManyToManyField(
        Contact,
        related_name="client_contacts",
        blank=True,
    )
    related_persons = models.ManyToManyField(
        RelatedPerson,
        related_name="client_related_persons",
        blank=True,
    )
    languages = ArrayField(
        models.CharField(
            max_length=150,
            choices=Languages.choices,
        ),
        null=True,
        blank=True,
    )
    caregiver = models.OneToOneField(
        Caregiver, related_name="client_caregiver", on_delete=models.PROTECT, null=True, blank=True
    )

    def __str__(self):
        return (
            f"{self.user.name} ({self.client_type})" if self.user else f"{self.client_type} client"
        )


@register_snippet
class ClientFacility(AbstractBase):
    """
    ClientFacility tracks a client's assigned facilities and changes over time.
    """

    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    facility = models.ForeignKey(Facility, on_delete=models.PROTECT)
    notes = models.TextField(default="-")
    assigned = models.DateTimeField(default=timezone.now)
    transferred_out = models.DateTimeField(null=True, blank=True)

    class Meta(AbstractBase.Meta):
        unique_together = (
            "client",
            "facility",
        )


@register_snippet
class HealthDiaryEntry(AbstractBase):
    class HealthDiaryEntryType(models.TextChoices):
        HOME_PAGE_HEALTH_DIARY_ENTRY = (
            "HOME_PAGE_HEALTH_DIARY_ENTRY",
            "Home page health diary entry",
        )
        OTHER_NOTE = "OTHER_NOTE", "Other note e.g a note taken after a conversation"

    class MoodScale(models.TextChoices):
        VERY_HAPPY = "VERY_HAPPY", _("Very happy")
        HAPPY = "HAPPY", _("Happy")
        NEUTRAL = "NEUTRAL", _("Neutral")
        SAD = "SAD", _("Sad")
        VERY_SAD = "VERY_SAD", _("Very sad")

    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    mood = models.CharField(choices=MoodScale.choices, max_length=16)
    note = models.TextField(null=True, blank=True)
    entry_type = models.CharField(
        choices=HealthDiaryEntryType.choices,
        max_length=36,
        default=HealthDiaryEntryType.HOME_PAGE_HEALTH_DIARY_ENTRY,
    )
    share_with_health_worker = models.BooleanField(default=False)
    shared_at = models.DateTimeField(null=True, blank=True)

    organisation_verify = ["client"]

    def __str__(self) -> str:
        return f"{self.client}'s {self.entry_type} ({self.mood})"

    class Meta(AbstractBase.Meta):
        verbose_name_plural = "health diary entries"


class HealthDiaryAttachment(Attachment):
    """
    A client can attach videos and pictures to their health diary.
    """

    health_diary_entry = models.ForeignKey(HealthDiaryEntry, on_delete=models.PROTECT)

    organisation_verify = ["health_diary_entry"]


@register_snippet
class HealthDiaryQuote(AbstractBase):
    """
    Clients will only be allowed to make health diary entries once every
    e.g 24 hours.

    In between, a random quote should be displayed each time the health diary
    is rendered.
    """

    quote = models.TextField(unique=True)
    by = models.TextField()  # quote author


class ServiceRequest(AbstractBase):
    """
    ServiceRequest is used to consolidate service requests sent by clients.
    """

    class ServiceRequestType(models.TextChoices):
        HEALTH_DIARY_ENTRY = "HEALTH_DIARY_ENTRY", _("HEALTH DIARY ENTRY")
        RED_FLAG = "RED_FLAG", _("RED FLAG")

    class ServiceRequestStatus(models.TextChoices):
        PENDING = "PENDING", _("PENDING")
        IN_PROGRESS = "IN PROGRESS", _("IN PROGRESS")
        RESOLVED = "RESOLVED", _("RESOLVED")

    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    request_type = models.CharField(
        choices=ServiceRequestType.choices,
        max_length=36,
    )
    request = models.TextField()
    status = models.CharField(
        choices=ServiceRequestStatus.choices,
        max_length=36,
        default=ServiceRequestStatus.PENDING,
    )

    in_progress_by = models.ForeignKey(
        get_user_model(),
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="service_request_in_progress_by_users",
    )
    in_progress_at = models.DateTimeField(null=True, blank=True)

    resolved_by = models.ForeignKey(
        get_user_model(),
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="service_request_resolved_by_users",
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
