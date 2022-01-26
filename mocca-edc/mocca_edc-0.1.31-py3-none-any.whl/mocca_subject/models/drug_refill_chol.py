from django.db import models
from edc_model import models as edc_models

from mocca_lists.models import CholTreatments

from ..model_mixins import CrfModelMixin
from .model_mixins import DrugRefillModelMixin


class DrugRefillChol(DrugRefillModelMixin, CrfModelMixin, edc_models.BaseUuidModel):

    rx = models.ManyToManyField(
        CholTreatments,
        verbose_name="Which medicine did the patient receive today?",
    )

    class Meta(CrfModelMixin.Meta, edc_models.BaseUuidModel.Meta):
        verbose_name = "Drug Refill: Cholesterol"
        verbose_name_plural = "Drug Refills: Cholesterol"
