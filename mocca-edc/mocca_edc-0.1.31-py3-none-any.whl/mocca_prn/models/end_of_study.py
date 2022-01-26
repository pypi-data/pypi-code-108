from django.db import models
from edc_action_item.models import ActionModelMixin
from edc_constants.choices import YES_NO_NA
from edc_constants.constants import NOT_APPLICABLE
from edc_identifier.model_mixins import TrackingModelMixin
from edc_model import models as edc_models
from edc_offstudy.constants import END_OF_STUDY_ACTION
from edc_sites.models import CurrentSiteManager
from edc_visit_schedule.model_mixins import (
    OffScheduleModelMixin,
    VisitScheduleFieldsModelMixin,
)

from mocca_lists.models import OffstudyReasons


class EndOfStudy(
    OffScheduleModelMixin,
    VisitScheduleFieldsModelMixin,
    ActionModelMixin,
    TrackingModelMixin,
    edc_models.BaseUuidModel,
):

    action_name = END_OF_STUDY_ACTION

    tracking_identifier_prefix = "ST"

    offschedule_datetime = models.DateTimeField(
        verbose_name="Date patient was terminated from the study",
        validators=[edc_models.datetime_not_future],
        blank=False,
        null=True,
    )

    last_study_fu_date = models.DateField(
        verbose_name="Date of last research follow up (if different):",
        validators=[edc_models.date_not_future],
        blank=True,
        null=True,
    )

    offschedule_reason = models.ForeignKey(
        OffstudyReasons,
        verbose_name="Reason patient was terminated from the study",
        on_delete=models.PROTECT,
        null=True,
    )

    other_offschedule_reason = models.TextField(
        verbose_name="If OTHER, please specify", max_length=500, blank=True, null=True
    )

    ltfu_last_alive_date = models.DateField(
        verbose_name="If lost to followup, date last known to be alive",
        validators=[edc_models.date_not_future],
        blank=True,
        null=True,
    )

    death_date = models.DateField(
        verbose_name="If deceased, date of death",
        validators=[edc_models.date_not_future],
        blank=True,
        null=True,
    )

    ltfu_date = models.DateField(
        verbose_name="Date lost to followup, if applicable",
        validators=[edc_models.date_not_future],
        blank=True,
        null=True,
    )

    transferred_consent = models.CharField(
        verbose_name=("If transferred, has the patient provided consent to be followed-up?"),
        choices=YES_NO_NA,
        max_length=15,
        default=NOT_APPLICABLE,
    )

    comment = models.TextField(verbose_name="Comments", null=True, blank=True)

    on_site = CurrentSiteManager()

    class Meta(OffScheduleModelMixin.Meta):
        verbose_name = "End of Study"
        verbose_name_plural = "End of Study"
