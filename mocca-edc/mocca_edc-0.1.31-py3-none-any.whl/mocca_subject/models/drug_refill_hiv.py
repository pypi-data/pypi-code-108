from django.db import models
from edc_model import models as edc_models

from mocca_lists.models import ArvRegimens

from ..model_mixins import CrfModelMixin
from .model_mixins import DrugRefillModelMixin


class DrugRefillHiv(DrugRefillModelMixin, CrfModelMixin, edc_models.BaseUuidModel):

    rx = models.ForeignKey(
        ArvRegimens,
        verbose_name="Which medicine did the patient receive today?",
        on_delete=models.PROTECT,
    )

    class Meta(CrfModelMixin.Meta, edc_models.BaseUuidModel.Meta):
        verbose_name = "Drug Refill: HIV"
        verbose_name_plural = "Drug Refills: HIV"
