from edc_model import models as edc_models

from ..model_mixins import CrfModelMixin
from .model_mixins import ComplicationsBaselineModelMixin


class ComplicationsBaseline(
    ComplicationsBaselineModelMixin, CrfModelMixin, edc_models.BaseUuidModel
):
    class Meta(CrfModelMixin.Meta, edc_models.BaseUuidModel.Meta):
        verbose_name = "Complications: Baseline"
        verbose_name_plural = "Complications: Baseline"
