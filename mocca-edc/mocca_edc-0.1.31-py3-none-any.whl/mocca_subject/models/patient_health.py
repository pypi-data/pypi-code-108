from edc_model import models as edc_models
from edc_phq9.model_mixins import Phq9ModelMixin

from ..model_mixins import CrfModelMixin


class PatientHealth(Phq9ModelMixin, CrfModelMixin, edc_models.BaseUuidModel):
    class Meta(Phq9ModelMixin.Meta, CrfModelMixin.Meta, edc_models.BaseUuidModel.Meta):
        pass
