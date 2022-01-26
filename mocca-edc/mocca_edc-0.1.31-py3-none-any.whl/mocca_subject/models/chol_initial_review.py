from django.conf import settings
from django.db import models
from edc_constants.choices import YES_NO
from edc_constants.constants import NOT_APPLICABLE
from edc_dx_review.model_mixins import (
    InitialReviewModelMixin,
    NcdInitialReviewModelMixin,
)
from edc_model import models as edc_models

from ..choices import CHOL_MANAGEMENT
from ..model_mixins import CrfModelMixin, DiagnosisLocationModelMixin


class CholInitialReview(
    InitialReviewModelMixin,
    DiagnosisLocationModelMixin,
    NcdInitialReviewModelMixin,
    CrfModelMixin,
    edc_models.BaseUuidModel,
):

    ncd_condition_label = "cholesterol"

    subject_visit = models.OneToOneField(
        settings.SUBJECT_VISIT_MODEL,
        on_delete=models.PROTECT,
        related_name="+",
    )

    managed_by = models.CharField(
        verbose_name="How is the patient's cholesterol managed?",
        max_length=25,
        choices=CHOL_MANAGEMENT,
        default=NOT_APPLICABLE,
    )

    chol_performed = models.CharField(
        verbose_name=(
            "Has the patient had their cholesterol measured in the last few months?"
        ),
        max_length=15,
        choices=YES_NO,
    )

    class Meta(CrfModelMixin.Meta, edc_models.BaseUuidModel.Meta):
        verbose_name = "High Cholesterol Initial Review"
        verbose_name_plural = "High Cholesterol Initial Reviews"
