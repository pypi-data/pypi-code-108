from django.db import models
from edc_model.models import BaseUuidModel, OtherCharField
from edc_model.models.historical_records import HistoricalRecords
from edc_search.model_mixins import SearchSlugManager
from edc_sites.models import CurrentSiteManager, SiteModelMixin
from edc_utils import get_utcnow

from ..choices import REFUSAL_REASONS_SCREENING


class Manager(SearchSlugManager, models.Manager):
    use_in_migrations = True

    def get_by_natural_key(self, mocca_register):
        return self.get(mocca_register=mocca_register)


class SubjectRefusalScreening(SiteModelMixin, BaseUuidModel):
    mocca_register = models.OneToOneField(
        "mocca_screening.moccaregister",
        on_delete=models.PROTECT,
        null=True,
        verbose_name="MOCCA (original) register details",
    )

    report_datetime = models.DateTimeField(
        verbose_name="Report Date and Time", default=get_utcnow
    )

    reason = models.CharField(
        verbose_name="Reason for refusal to screen",
        max_length=25,
        choices=REFUSAL_REASONS_SCREENING,
    )

    other_reason = OtherCharField()

    comment = models.TextField(
        verbose_name="Additional Comments",
        null=True,
        blank=True,
    )

    on_site = CurrentSiteManager()

    objects = Manager()

    history = HistoricalRecords()

    def __str__(self):
        return self.mocca_register.mocca_study_identifier

    def natural_key(self):
        return tuple(self.mocca_register)

    @staticmethod
    def get_search_slug_fields():
        return ["screening_identifier"]

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Refusal to Screen"
        verbose_name_plural = "Refusal to Screen"
