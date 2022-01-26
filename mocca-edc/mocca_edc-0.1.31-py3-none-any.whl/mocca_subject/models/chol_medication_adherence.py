from edc_adherence.model_mixins import MedicationAdherenceModelMixin
from edc_model import models as edc_models

from ..model_mixins import CrfModelMixin


class CholMedicationAdherence(
    MedicationAdherenceModelMixin,
    CrfModelMixin,
    edc_models.BaseUuidModel,
):
    class Meta(CrfModelMixin.Meta, edc_models.BaseUuidModel.Meta):
        verbose_name = "Cholesterol Medication Adherence"
        verbose_name_plural = "Cholesterol Medication Adherence"
