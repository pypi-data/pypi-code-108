from django.conf import settings
from django.db import models
from edc_constants.constants import NOT_APPLICABLE
from edc_dx_review.model_mixins import (
    InitialReviewModelMixin,
    NcdInitialReviewModelMixin,
)
from edc_model import models as edc_models

from mocca_subject.model_mixins import CrfModelMixin

from ..choices import HTN_MANAGEMENT
from ..model_mixins import DiagnosisLocationModelMixin


class HtnInitialReview(
    InitialReviewModelMixin,
    DiagnosisLocationModelMixin,
    NcdInitialReviewModelMixin,
    CrfModelMixin,
    edc_models.BaseUuidModel,
):
    ncd_condition_label = "hypertension"

    subject_visit = models.OneToOneField(
        settings.SUBJECT_VISIT_MODEL,
        on_delete=models.PROTECT,
        related_name="+",
    )

    managed_by = models.CharField(
        verbose_name="How is the patient's hypertension managed?",
        max_length=15,
        choices=HTN_MANAGEMENT,
        default=NOT_APPLICABLE,
    )

    class Meta(CrfModelMixin.Meta, edc_models.BaseUuidModel.Meta):
        verbose_name = "Hypertension Initial Review"
        verbose_name_plural = "Hypertension Initial Reviews"
