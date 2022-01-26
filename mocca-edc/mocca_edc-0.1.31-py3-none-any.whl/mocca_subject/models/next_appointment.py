from django.db import models
from edc_model import models as edc_models

from ..model_mixins import CrfModelMixin


class NextAppointment(CrfModelMixin, edc_models.BaseUuidModel):

    appt_date = models.DateField(
        verbose_name="Next scheduled routine appointment",
        null=True,
        blank=True,
        help_text="if applicable.",
    )

    class Meta(CrfModelMixin.Meta, edc_models.BaseUuidModel.Meta):
        verbose_name = "Routine Appointment"
        verbose_name_plural = "Routine Appointments"
