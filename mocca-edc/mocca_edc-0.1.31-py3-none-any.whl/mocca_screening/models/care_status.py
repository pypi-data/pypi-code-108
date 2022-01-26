from django.db import models
from edc_constants.choices import YES_NO
from edc_constants.constants import YES
from edc_model.models import BaseUuidModel, HistoricalRecords
from edc_sites.models import CurrentSiteManager, SiteModelMixin
from edc_utils import get_utcnow

from mocca_screening.models.model_mixins import CareModelMixin


class Manager(models.Manager):
    """A manager class for Crf models, models that have an FK to
    the visit model.
    """

    use_in_migrations = True

    def get_by_natural_key(self, mocca_register):
        return self.get(mocca_register=mocca_register)


class CareStatus(SiteModelMixin, CareModelMixin, BaseUuidModel):

    willing_to_answer = models.CharField(
        verbose_name="Is the patient willing to provide information about their care status?",
        max_length=15,
        choices=YES_NO,
        default=YES,
    )

    report_datetime = models.DateTimeField(
        verbose_name="Report Date and Time",
        default=get_utcnow,
        help_text="Date and time of report.",
    )

    mocca_register = models.OneToOneField(
        "mocca_screening.moccaregister",
        on_delete=models.PROTECT,
        null=True,
        verbose_name="MOCCA (original) register details",
    )

    on_site = CurrentSiteManager()
    objects = Manager()
    history = HistoricalRecords()

    def natural_key(self):
        return tuple(self.mocca_register)

    natural_key.dependencies = [
        "sites.Site",
        "mocca_screen ing.MoccaRegister",
    ]

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Care Status"
        verbose_name_plural = "Care Status"
