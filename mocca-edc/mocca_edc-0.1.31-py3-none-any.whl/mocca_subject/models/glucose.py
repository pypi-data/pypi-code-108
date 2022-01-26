from django.db import models
from edc_blood_results.model_mixins import GlucoseModelMixin
from edc_constants.choices import YES_NO, YES_NO_NA
from edc_constants.constants import NOT_APPLICABLE
from edc_lab.choices import RESULT_QUANTIFIER
from edc_lab.constants import EQ
from edc_model import models as edc_models
from edc_model.models import date_not_future

from ..model_mixins import CrfModelMixin


class Glucose(GlucoseModelMixin, CrfModelMixin, edc_models.BaseUuidModel):

    """See also proxy models"""

    glucose_performed = models.CharField(
        verbose_name=(
            "Has the patient had their glucose measured today or since the last visit?"
        ),
        max_length=15,
        choices=YES_NO,
    )

    glucose_date = models.DateField(
        validators=[date_not_future],
        null=True,
        blank=True,
    )

    glucose_fasted = models.CharField(
        verbose_name="Has the participant fasted?",
        max_length=15,
        choices=YES_NO_NA,
        default=NOT_APPLICABLE,
    )

    glucose_value = models.DecimalField(
        verbose_name="Glucose result",
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
    )

    glucose_quantifier = models.CharField(
        max_length=10,
        choices=RESULT_QUANTIFIER,
        default=EQ,
        null=True,
        blank=True,
    )

    class Meta(CrfModelMixin.Meta, edc_models.BaseUuidModel.Meta):
        verbose_name = "Glucose"
        verbose_name_plural = "Glucose"
