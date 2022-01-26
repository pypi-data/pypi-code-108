from django.conf import settings
from django.db import models
from edc_model import models as edc_models


class DiagnosisLocationModelMixin(models.Model):

    dx_location = models.ForeignKey(
        f"{settings.LIST_MODEL_APP_LABEL}.diagnosislocations",
        verbose_name="Where was the diagnosis made?",
        on_delete=models.PROTECT,
    )

    dx_location_other = edc_models.OtherCharField()

    class Meta:
        abstract = True
