from django.contrib.auth import get_user_model
from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.db.models.fields.json import JSONField
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from ..constants import COUNTRY_CODES, WHITELIST_COUNTIES
from ..utils import get_constituencies, get_counties, get_sub_counties, get_wards
from .base_models import AbstractBase, AbstractBaseManager, AbstractBaseQuerySet, Attachment

User = get_user_model()


# =============================================================================
# QUERYSETS
# =============================================================================


class FacilityQuerySet(AbstractBaseQuerySet):
    """Queryset for the Facility model."""

    def mycarehub_facilities(self):
        """Return all the facilities that are part of the FYJ program."""
        return self.active().filter(
            county__in=WHITELIST_COUNTIES,
        )


# =============================================================================
# MANAGERS
# =============================================================================


class FacilityManager(AbstractBaseManager):
    """Manager for the UserFacilityAllotment model."""

    def mycarehub_facilities(self):
        """Return all the facilities that are part of the FYJ program."""
        return self.get_queryset().mycarehub_facilities()

    def get_queryset(self):
        return FacilityQuerySet(self.model, using=self.db)


# =============================================================================
# MODELS
# =============================================================================


class Facility(AbstractBase):
    """A facility with M&E reporting.

    The data is fetched - and updated - from the Kenya Master Health Facilities List.
    """

    name = models.TextField(unique=True)
    description = models.TextField(blank=True, default="")
    mfl_code = models.IntegerField(unique=True, help_text="MFL Code")
    county = models.CharField(max_length=64, choices=get_counties())
    phone = models.CharField(max_length=15, null=True, blank=True)

    objects = FacilityManager()

    model_validators = [
        "check_facility_name_longer_than_three_characters",
    ]

    def get_absolute_url(self):
        update_url = reverse("common:facility_update", kwargs={"pk": self.pk})
        return update_url

    def check_facility_name_longer_than_three_characters(self):
        if len(self.name) < 3:
            raise ValidationError("the facility name should exceed 3 characters")

    def __str__(self):
        return f"{self.name} - {self.mfl_code} ({self.county})"

    class Meta(AbstractBase.Meta):
        verbose_name_plural = "facilities"


class FacilityAttachment(Attachment):
    """Any document attached to a facility."""

    facility = models.ForeignKey(Facility, on_delete=models.PROTECT)
    notes = models.TextField()

    organisation_verify = ["facility"]

    class Meta(AbstractBase.Meta):
        """Define ordering and other attributes for attachments."""

        ordering = ("-updated", "-created")


class UserFacilityAllotment(AbstractBase):
    """Define the allocation of a facility/facilities to a user."""

    class AllotmentType(models.TextChoices):
        """The type of facility allocation to a user."""

        BY_FACILITY = "facility", "By Facility"
        BY_REGION = "region", "By Region"
        BY_FACILITY_AND_REGION = "both", "By Both Facility and Region"

    class RegionType(models.TextChoices):
        """The type of region whose facilities are to be assigned user."""

        COUNTY = "county"
        CONSTITUENCY = "constituency"
        SUB_COUNTY = "sub_county"
        WARD = "ward"

    user = models.OneToOneField(User, on_delete=models.PROTECT)
    allotment_type = models.CharField(max_length=10, choices=AllotmentType.choices)
    region_type = models.CharField(
        max_length=20, choices=RegionType.choices, null=True, blank=True
    )
    facilities = models.ManyToManyField(Facility, blank=True)
    counties = ArrayField(
        models.CharField(max_length=150, choices=get_counties(), null=True, blank=True),
        help_text=(
            "All the facilities in the selected counties will be allocated to the selected user."
        ),
        null=True,
        blank=True,
    )
    constituencies = ArrayField(
        models.CharField(max_length=150, choices=get_constituencies(), null=True, blank=True),
        help_text=(
            "All the facilities in the selected constituencies will be allocated to the selected "
            "user."
        ),
        null=True,
        blank=True,
    )
    sub_counties = ArrayField(
        models.CharField(max_length=150, choices=get_sub_counties(), null=True, blank=True),
        help_text=(
            "All the facilities in the selected sub counties will be allocated to the selected "
            "user."
        ),
        null=True,
        blank=True,
    )
    wards = ArrayField(
        models.CharField(max_length=150, choices=get_wards(), null=True, blank=True),
        help_text=(
            "All the facilities in the selected wards will be allocated to the selected user."
        ),
        null=True,
        blank=True,
    )

    model_validators = [
        "check_region_type_is_provided_if_allot_by_region_or_both",
        "check_county_is_provided_if_region_type_is_county",
        "check_constituency_is_provided_if_region_type_is_constituency",
        "check_sub_county_is_provided_if_region_type_is_sub_county",
        "check_ward_is_provided_if_region_type_is_ward",
    ]

    def check_region_type_is_provided_if_allot_by_region_or_both(self):
        by_both = self.AllotmentType.BY_FACILITY_AND_REGION.value
        by_region = self.AllotmentType.BY_REGION.value
        if self.allotment_type in (by_both, by_region) and not self.region_type:
            raise ValidationError(
                {
                    "region_type": 'A region type must be provided if allotment type is "%s"'
                    % self.get_allotment_type_display()  # noqa
                },
                code="required",
            )

    def check_county_is_provided_if_region_type_is_county(self):
        by_both = self.AllotmentType.BY_FACILITY_AND_REGION.value
        by_region = self.AllotmentType.BY_REGION.value
        county = self.RegionType.COUNTY
        if (
            self.allotment_type in (by_both, by_region)
            and self.region_type == county.value
            and not self.counties
        ):
            raise ValidationError(
                {
                    "counties": 'At least 1 county must be selected if region type is "%s"'
                    % county.label
                },
                code="required",
            )

    def check_constituency_is_provided_if_region_type_is_constituency(self):
        by_both = self.AllotmentType.BY_FACILITY_AND_REGION.value
        by_region = self.AllotmentType.BY_REGION.value
        constituency = self.RegionType.CONSTITUENCY
        if (
            self.allotment_type in (by_both, by_region)
            and self.region_type == constituency.value
            and not self.constituencies
        ):
            raise ValidationError(
                {
                    "constituencies": "At least 1 constituency must be selected if region type "
                    'is "%s"' % constituency.label
                },
                code="required",
            )

    def check_sub_county_is_provided_if_region_type_is_sub_county(self):
        by_both = self.AllotmentType.BY_FACILITY_AND_REGION.value
        by_region = self.AllotmentType.BY_REGION.value
        sub_county = self.RegionType.SUB_COUNTY
        if (
            self.allotment_type in (by_both, by_region)
            and self.region_type == sub_county.value
            and not self.sub_counties
        ):
            raise ValidationError(
                {
                    "sub_counties": 'At least 1 sub_county must be selected if region type is "%s"'
                    % sub_county.label
                },
                code="required",
            )

    def check_ward_is_provided_if_region_type_is_ward(self):
        by_both = self.AllotmentType.BY_FACILITY_AND_REGION.value
        by_region = self.AllotmentType.BY_REGION.value
        ward = self.RegionType.WARD
        if (
            self.allotment_type in (by_both, by_region)
            and self.region_type == ward.value
            and not self.wards
        ):
            raise ValidationError(
                {"wards": 'At least 1 ward must be selected if region type is "%s"' % ward.label},
                code="required",
            )

    def get_absolute_url(self):
        update_url = reverse("common:user_facility_allotment_update", kwargs={"pk": self.pk})
        return update_url

    def __str__(self):
        return (
            f"User: {self.user.name}; Allotment Type: {self.get_allotment_type_display()}"  # noqa
        )

    @staticmethod
    def get_facilities_for_user(user):
        """Return a queryset containing all the facilities allotted to the given user."""

        allotment = UserFacilityAllotment.objects.filter(user=user).first()
        if not allotment:
            return Facility.objects.none()
        return UserFacilityAllotment.get_facilities_for_allotment(allotment)

    @staticmethod
    def get_facilities_for_allotment(allotment: "UserFacilityAllotment"):
        """Return a queryset containing all the facilities specified in the given allotment."""

        by_facility = UserFacilityAllotment.AllotmentType.BY_FACILITY.value
        by_region = UserFacilityAllotment.AllotmentType.BY_REGION.value

        by_facility_filter = UserFacilityAllotment._get_allot_by_facility_filter(allotment)
        by_region_filter = UserFacilityAllotment._get_allot_by_region_filter(allotment)
        facilities = Facility.objects.filter(organisation=allotment.organisation)

        if allotment.allotment_type == by_facility:
            return facilities.filter(**by_facility_filter)
        if allotment.allotment_type == by_region:
            return facilities.filter(**by_region_filter)
        # for both facility and region
        return facilities.filter(Q(**by_facility_filter) | Q(**by_region_filter))

    @staticmethod
    def _get_allot_by_facility_filter(allotment: "UserFacilityAllotment"):
        """Helper for generating a queryset filter."""

        return {"pk__in": allotment.facilities.values_list("pk", flat=True)}

    @staticmethod
    def _get_allot_by_region_filter(allotment: "UserFacilityAllotment"):
        """Helper for generating a queryset filter."""

        by_region_filter = {}
        if allotment.region_type == UserFacilityAllotment.RegionType.COUNTY.value:
            by_region_filter["county__in"] = allotment.counties

        return by_region_filter

    class Meta(AbstractBase.Meta):
        """Define ordering and other attributes for attachments."""

        ordering = ("-updated", "-created")


class Address(AbstractBase):
    class AddressType(models.TextChoices):
        POSTAL = "POSTAL", _("Postal Address")
        PHYSICAL = "PHYSICAL", _("Physical Address")
        BOTH = "BOTH", _("Both physical and postal")

    address_type = models.CharField(choices=AddressType.choices, max_length=16)
    text = models.TextField()
    postal_code = models.TextField()
    country = models.CharField(max_length=255, choices=COUNTRY_CODES, default="KEN")

    def __str__(self):
        return f"{self.text} ({self.address_type})"


class Contact(AbstractBase):
    class ContactType(models.TextChoices):
        PHONE = "PHONE", _("PHONE")
        EMAIL = "EMAIL", _("EMAIL")

    class FlavourChoices(models.TextChoices):
        PRO = "PRO", _("PRO")
        CONSUMER = "CONSUMER", _("CONSUMER")

    contact_type = models.CharField(choices=ContactType.choices, max_length=16)
    contact_value = models.TextField(unique=True)
    opted_in = models.BooleanField(default=False)
    flavour = models.CharField(
        choices=FlavourChoices.choices, max_length=32, null=True, blank=True
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.contact_value} ({self.contact_type})"


class AuditLog(AbstractBase):
    """
    AuditLog is used to record all senstive changes

    e.g
        - changing a client's treatment buddy
        - changing a client's facility
        - deactivating a client
        - changing a client's assigned community health volunteer

    Rules of thumb: is there a need to find out what/when/why something
    occured? Is a mistake potentially serious? Is there potential for
    fraud?
    """

    timestamp = models.DateTimeField(default=timezone.now)
    record_type = models.TextField()
    notes = models.TextField()
    payload = JSONField()


class FAQ(AbstractBase):
    class FlavourChoices(models.TextChoices):
        PRO = "PRO", _("PRO")
        CONSUMER = "CONSUMER", _("CONSUMER")

    title = models.TextField(unique=True)
    description = models.TextField(unique=True, null=True, blank=True)
    body = models.TextField(unique=True)
    flavour = models.CharField(
        choices=FlavourChoices.choices, max_length=32, null=True, blank=True
    )
