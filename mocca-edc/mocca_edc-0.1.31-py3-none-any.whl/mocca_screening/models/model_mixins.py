from django.db import models
from edc_constants.choices import YES_NO_NA, YES_NO_UNKNOWN
from edc_constants.constants import NOT_APPLICABLE
from edc_model_fields.fields import OtherCharField

from ..choices import CARE_SINCE_MOCCA, NOT_ICC_REASONS


class CareModelMixin(models.Model):
    care = models.CharField(
        verbose_name="Is the patient in care?",
        choices=YES_NO_UNKNOWN,
        max_length=25,
    )

    care_not_in_reason = models.CharField(
        verbose_name="If not in care, why?", max_length=25, null=True, blank=True
    )

    care_facility_location = models.CharField(
        verbose_name="Does the patient receive care in this facility",
        max_length=25,
        choices=YES_NO_NA,
        default=NOT_APPLICABLE,
        help_text="Either integrated care or vertical care",
    )

    icc_since_mocca = models.CharField(
        verbose_name=(
            "Has the patient received integrated care "
            "since the leaving the MOCCA (orig) trial until now?"
        ),
        max_length=25,
        choices=CARE_SINCE_MOCCA,
    )

    icc_since_mocca_comment = OtherCharField(
        verbose_name="If some interruption in integrated care, please explain"
    )

    icc = models.CharField(
        verbose_name="Does the patient currently receive integrated care",
        max_length=25,
        choices=YES_NO_NA,
        default=NOT_APPLICABLE,
        help_text="Either at this facility or elsewhere",
    )

    icc_not_in_reason = models.CharField(
        verbose_name="If not receiving integrated care, why not?",
        max_length=25,
        choices=NOT_ICC_REASONS,
        default=NOT_APPLICABLE,
    )

    care_comment = models.TextField(
        verbose_name="Additional comments relevant to this patient's care",
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True
