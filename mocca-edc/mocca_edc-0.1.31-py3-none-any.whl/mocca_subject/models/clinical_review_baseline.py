from django.conf import settings
from django.db import models
from edc_dx_review.model_mixins import (
    ClinicalReviewBaselineCholModelMixin,
    ClinicalReviewBaselineDmModelMixin,
    ClinicalReviewBaselineHivModelMixin,
    ClinicalReviewBaselineHtnModelMixin,
    ClinicalReviewBaselineModelMixin,
)
from edc_model import models as edc_models

from ..model_mixins import CrfModelMixin


class ClinicalReviewBaseline(
    ClinicalReviewBaselineHivModelMixin,
    ClinicalReviewBaselineHtnModelMixin,
    ClinicalReviewBaselineDmModelMixin,
    ClinicalReviewBaselineCholModelMixin,
    ClinicalReviewBaselineModelMixin,
    CrfModelMixin,
    edc_models.BaseUuidModel,
):
    subject_visit = models.OneToOneField(
        settings.SUBJECT_VISIT_MODEL,
        on_delete=models.PROTECT,
        related_name="+",
    )

    class Meta(CrfModelMixin.Meta, edc_models.BaseUuidModel.Meta):
        verbose_name = "Clinical Review: Baseline"
        verbose_name_plural = "Clinical Review: Baseline"
