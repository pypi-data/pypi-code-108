from django.conf import settings
from django.db import models
from edc_constants.constants import NOT_APPLICABLE
from edc_model import models as edc_models

from mocca_subject.choices import DM_MANAGEMENT

from ..model_mixins import CrfModelMixin
from .model_mixins import ReviewModelMixin


class DmReview(ReviewModelMixin, CrfModelMixin, edc_models.BaseUuidModel):

    subject_visit = models.OneToOneField(
        settings.SUBJECT_VISIT_MODEL,
        on_delete=models.PROTECT,
        related_name="+",
    )

    managed_by = models.CharField(
        verbose_name="How will the patient's diabetes be managed going forward?",
        max_length=25,
        choices=DM_MANAGEMENT,
        default=NOT_APPLICABLE,
    )

    class Meta(CrfModelMixin.Meta, edc_models.BaseUuidModel.Meta):
        verbose_name = "Diabetes Review"
        verbose_name_plural = "Diabetes Review"
