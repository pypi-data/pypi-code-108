from django.core.validators import (
    MaxLengthValidator,
    MaxValueValidator,
    MinLengthValidator,
    MinValueValidator,
    RegexValidator,
)
from django.db import models
from django_crypto_fields.fields import EncryptedCharField
from edc_constants.choices import YES_NO, YES_NO_NA
from edc_constants.constants import NO, NOT_APPLICABLE, YES
from edc_model.models import BaseUuidModel
from edc_screening.model_mixins import EligibilityModelMixin, ScreeningModelMixin
from edc_screening.screening_identifier import (
    ScreeningIdentifier as BaseScreeningIdentifier,
)
from edc_utils import get_utcnow

from mocca_lists.models import MoccaOriginalSites

from ..eligibility import MoccaScreeningEligibility
from ..mocca_original_sites import get_mocca_site_limited_to
from .mocca_register import MoccaRegister
from .model_mixins import CareModelMixin

PREG_YES_NO_NA = (
    (YES, "Yes"),
    (NO, "No"),
    (NOT_APPLICABLE, "Not Applicable"),
)


class ScreeningIdentifier(BaseScreeningIdentifier):
    template = "S{random_string}"


class SubjectScreening(
    CareModelMixin,
    ScreeningModelMixin,
    EligibilityModelMixin,
    BaseUuidModel,
):
    identifier_cls = ScreeningIdentifier

    eligibility_cls = MoccaScreeningEligibility

    subject_identifier = models.CharField(max_length=50, null=True, blank=True)

    screening_consent = models.CharField(
        verbose_name=(
            "Has the subject given his/her verbal consent "
            "to be screened for the MOCCA Extension study?"
        ),
        max_length=15,
        choices=YES_NO,
    )

    mocca_site = models.ForeignKey(
        MoccaOriginalSites,
        verbose_name="Original MOCCA site",
        on_delete=models.PROTECT,
        limit_choices_to=get_mocca_site_limited_to,
    )

    mocca_participant = models.CharField(
        verbose_name="Was the patient enrolled to the original MOCCA study?",
        max_length=25,
        choices=YES_NO,
        default=YES,
    )

    mocca_study_identifier = models.CharField(
        verbose_name="MOCCA (original) study identifier",
        unique=True,
        max_length=25,
        # validators=[
        #     RegexValidator(
        #         r"0[0-9]{1}\-0[0-9]{3}|[0-9]{6}",
        #         "Invalid format. Expected 12-3456 for UG, 123456 for TZ",
        #     )
        # ],
        help_text="Format must match original identifier. e.g. 12-3456 for UG, 123456 for TZ",
    )

    initials = EncryptedCharField(
        validators=[
            RegexValidator("[A-Z]{1,3}", "Invalid format"),
            MinLengthValidator(2),
            MaxLengthValidator(3),
        ],
        help_text=(
            "Use UPPERCASE letters only. May be 2 or 3 letters. "
            "Use `F`irst`L`ast or `L`ast`F`irst depending on the country custom. "
        ),
        blank=False,
    )

    birth_year = models.IntegerField(
        validators=[MinValueValidator(1900), MaxValueValidator(2002)],
    )

    mocca_register = models.OneToOneField(
        MoccaRegister,
        on_delete=models.PROTECT,
        null=True,
        verbose_name="MOCCA (original) register details",
    )

    willing_to_consent = models.CharField(
        verbose_name=(
            "Has the patient expressed willingness to participate "
            "in the `MOCCA extension` study"
        ),
        max_length=25,
        choices=YES_NO_NA,
        default=NOT_APPLICABLE,
        help_text="If No, complete refusal form.",
    )

    pregnant = models.CharField(
        verbose_name="Is the patient pregnant?",
        max_length=15,
        choices=PREG_YES_NO_NA,
        default=NOT_APPLICABLE,
    )

    requires_acute_care = models.CharField(
        verbose_name="Does the patient require acute care including in-patient admission",
        max_length=25,
        choices=YES_NO_NA,
        default=NOT_APPLICABLE,
    )

    def save(self, *args, **kwargs):
        self.age_in_years = self.mocca_register.age_in_years
        self.birth_year = self.mocca_register.birth_year
        self.gender = self.mocca_register.gender
        self.initials = self.mocca_register.initials
        self.mocca_screening_identifier = self.mocca_register.mocca_screening_identifier
        self.mocca_site = self.mocca_register.mocca_site
        self.mocca_study_identifier = self.mocca_register.mocca_study_identifier
        self.eligibility_datetime = self.report_datetime
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Subject Screening"
        verbose_name_plural = "Subject Screening"
