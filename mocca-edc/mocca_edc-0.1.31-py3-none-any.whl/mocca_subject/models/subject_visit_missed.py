from django.db import models
from edc_crf.crf_with_action_model_mixin import CrfWithActionModelMixin
from edc_model import models as edc_models
from edc_sites.models import SiteModelMixin
from edc_visit_tracking.model_mixins import SubjectVisitMissedModelMixin

from mocca_lists.models import SubjectVisitMissedReasons

from ..model_mixins import CrfModelMixin


class SubjectVisitMissed(
    SubjectVisitMissedModelMixin,
    CrfWithActionModelMixin,
    SiteModelMixin,
    edc_models.BaseUuidModel,
):

    action_identifier = models.CharField(max_length=50, null=True)

    tracking_identifier = models.CharField(max_length=30, null=True)

    missed_reasons = models.ManyToManyField(
        SubjectVisitMissedReasons, blank=True, related_name="+"
    )

    class Meta(
        CrfModelMixin.Meta,
        SubjectVisitMissedModelMixin.Meta,
        edc_models.BaseUuidModel.Meta,
    ):
        verbose_name = "Missed Visit Report"
        verbose_name_plural = "Missed Visit Report"
