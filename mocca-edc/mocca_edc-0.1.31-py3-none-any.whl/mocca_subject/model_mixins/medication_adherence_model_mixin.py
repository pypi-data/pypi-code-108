from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.html import format_html
from edc_model import models as edc_models

from mocca_lists.models import NonAdherenceReasons

from ..choices import MISSED_PILLS


class MedicationAdherenceModelMixin(models.Model):

    condition_label = "condition_label"

    visual_score_slider = models.CharField(
        verbose_name=format_html(
            f"Visual adherence score for <U>{condition_label}</U> medication"
        ),
        max_length=3,
        help_text="%",
    )

    visual_score_confirmed = models.IntegerField(
        verbose_name=format_html(
            "<B><font color='orange'>Interviewer</font></B>: "
            "please confirm the score indicated from above."
        ),
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="%",
    )

    last_missed_pill = models.CharField(
        verbose_name=format_html(
            "When was the last time you missed taking your "
            f"<U>{condition_label}</U> medication?"
        ),
        max_length=25,
        choices=MISSED_PILLS,
    )

    missed_pill_reason = models.ManyToManyField(
        NonAdherenceReasons,
        verbose_name="Reasons for miss taking medication",
        blank=True,
    )

    other_missed_pill_reason = edc_models.OtherCharField()

    class Meta:
        abstract = True
