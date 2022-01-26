from django.db import models
from edc_model.models import BaseUuidModel, OtherCharField
from edc_model.models.historical_records import HistoricalRecords
from edc_search.model_mixins import SearchSlugManager
from edc_sites.models import CurrentSiteManager, SiteModelMixin
from edc_utils import get_utcnow

from ..choices import REFUSAL_REASONS


class SubjectRefusalManager(SearchSlugManager, models.Manager):
    def get_by_natural_key(self, screening_identifier):
        return self.get(screening_identifier=screening_identifier)


class SubjectRefusal(SiteModelMixin, BaseUuidModel):
    screening_identifier = models.CharField(max_length=50, unique=True)

    report_datetime = models.DateTimeField(
        verbose_name="Report Date and Time", default=get_utcnow
    )

    reason = models.CharField(
        verbose_name="Reason for refusal to join",
        max_length=25,
        choices=REFUSAL_REASONS,
    )

    other_reason = OtherCharField()

    comment = models.TextField(
        verbose_name="Additional Comments",
        null=True,
        blank=True,
    )

    on_site = CurrentSiteManager()

    objects = SubjectRefusalManager()

    history = HistoricalRecords()

    def __str__(self):
        return self.screening_identifier

    def natural_key(self):
        return (self.screening_identifier,)

    @staticmethod
    def get_search_slug_fields():
        return ["screening_identifier"]

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Refusal to Consent"
        verbose_name_plural = "Refusal to Consent"
