from django.db import models
from django_crypto_fields.fields import EncryptedTextField
from edc_constants.choices import ALIVE_DEAD_UNKNOWN_NA, YES_NO, YES_NO_UNSURE_NA
from edc_constants.constants import NOT_APPLICABLE
from edc_model.models import BaseUuidModel, HistoricalRecords
from edc_sites.models import CurrentSiteManager, SiteModelMixin
from edc_utils import get_utcnow

from ..choices import RESPONDENT_CHOICES
from .mocca_register import MoccaRegister


class Manager(models.Manager):
    """A manager class for Crf models, models that have an FK to
    the visit model.
    """

    use_in_migrations = True

    def get_by_natural_key(self, mocca_register):
        return self.get(mocca_register=mocca_register)


class MoccaRegisterContact(SiteModelMixin, BaseUuidModel):

    mocca_register = models.ForeignKey(MoccaRegister, on_delete=models.PROTECT)

    report_datetime = models.DateTimeField(default=get_utcnow)

    answered = models.CharField(max_length=15, choices=YES_NO, null=True, blank=False)

    respondent = models.CharField(
        max_length=15, choices=RESPONDENT_CHOICES, default=NOT_APPLICABLE
    )

    survival_status = models.CharField(
        max_length=15,
        choices=ALIVE_DEAD_UNKNOWN_NA,
        default=NOT_APPLICABLE,
    )

    death_date = models.DateField(verbose_name="Date of death", null=True, blank=True)

    willing_to_attend = models.CharField(
        max_length=15, choices=YES_NO_UNSURE_NA, default=NOT_APPLICABLE
    )

    icc = models.CharField(
        verbose_name="Does the patient currently receive regular integrated care",
        max_length=25,
        choices=YES_NO_UNSURE_NA,
        null=True,
        blank=False,
        help_text="Either at this facility or elsewhere",
    )

    next_appt_date = models.DateField(verbose_name="Next Appt.", null=True, blank=True)

    call_again = models.CharField(verbose_name="Call again?", max_length=15, choices=YES_NO)

    comment = EncryptedTextField(verbose_name="Note", null=True, blank=True)

    on_site = CurrentSiteManager()
    objects = Manager()
    history = HistoricalRecords()

    def __str__(self):
        return str(self.mocca_register)

    def natural_key(self):
        return (self.mocca_register,)

    natural_key.dependencies = [
        "sites.Site",
        "mocca_screening.MoccaRegister",
    ]

    class Meta:
        verbose_name = "MOCCA Patient Register Contact"
        verbose_name_plural = "MOCCA Patient Register Contacts"
        ordering = ["report_datetime"]
