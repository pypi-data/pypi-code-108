from django.conf import settings
from django.db import models
from edc_constants.constants import NOT_APPLICABLE
from edc_dx_review.model_mixins import (
    InitialReviewModelMixin,
    NcdInitialReviewModelMixin,
)
from edc_model import models as edc_models

from mocca_subject.model_mixins import CrfModelMixin, DiagnosisLocationModelMixin

from ..choices import DM_MANAGEMENT


class DmInitialReview(
    InitialReviewModelMixin,
    DiagnosisLocationModelMixin,
    NcdInitialReviewModelMixin,
    CrfModelMixin,
    edc_models.BaseUuidModel,
):

    ncd_condition_label = "diabetes"

    subject_visit = models.OneToOneField(
        settings.SUBJECT_VISIT_MODEL,
        on_delete=models.PROTECT,
        related_name="+",
    )

    managed_by = models.CharField(
        verbose_name="How is the patient's diabetes managed?",
        max_length=25,
        choices=DM_MANAGEMENT,
        default=NOT_APPLICABLE,
        help_text="If insulin or oral drugs, diet and lifestyle is assumed.",
    )

    class Meta(CrfModelMixin.Meta, edc_models.BaseUuidModel.Meta):
        verbose_name = "Diabetes Initial Review"
        verbose_name_plural = "Diabetes Initial Reviews"
