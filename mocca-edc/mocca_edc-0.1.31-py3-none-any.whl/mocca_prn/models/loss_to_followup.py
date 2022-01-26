from django.db import models
from edc_action_item.models.action_model_mixin import ActionModelMixin
from edc_identifier.model_mixins import (
    NonUniqueSubjectIdentifierFieldMixin,
    TrackingModelMixin,
)
from edc_ltfu.choices import LTFU_CHOICES
from edc_ltfu.constants import LTFU_ACTION
from edc_ltfu.model_mixins import LtfuModelMixin
from edc_model.models.base_uuid_model import BaseUuidModel
from edc_sites.models import CurrentSiteManager, SiteModelMixin
from edc_visit_schedule.model_mixins import VisitScheduleFieldsModelMixin


class LossToFollowup(
    NonUniqueSubjectIdentifierFieldMixin,
    LtfuModelMixin,
    VisitScheduleFieldsModelMixin,
    SiteModelMixin,
    ActionModelMixin,
    TrackingModelMixin,
    BaseUuidModel,
):

    action_name = LTFU_ACTION

    tracking_identifier_prefix = "LF"

    # loss_category = models.CharField(
    #     verbose_name="Category of loss to follow up",
    #     max_length=25,
    #     choices=LTFU_CHOICES,
    # )

    on_site = CurrentSiteManager()

    class Meta(LtfuModelMixin.Meta, BaseUuidModel.Meta):
        indexes = [
            models.Index(fields=["subject_identifier", "action_identifier", "site", "id"])
        ]
