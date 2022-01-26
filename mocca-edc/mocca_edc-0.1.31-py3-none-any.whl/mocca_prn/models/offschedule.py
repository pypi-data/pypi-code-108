from edc_offstudy.constants import END_OF_STUDY_ACTION
from edc_visit_schedule import site_visit_schedules

from mocca_visit_schedule.constants import SCHEDULE

from .end_of_study import EndOfStudy


class OffSchedule(EndOfStudy):
    action_name = END_OF_STUDY_ACTION

    tracking_identifier_prefix = "OH"

    def save(self, *args, **kwargs):
        self.visit_schedule_name = "visit_schedule"
        self.schedule_name = SCHEDULE
        super().save(*args, **kwargs)

    @property
    def visit_schedule(self):
        """Returns a visit schedule object."""
        return site_visit_schedules.get_by_onschedule_model(
            onschedule_model=self._meta.label_lower
        )[0]

    @property
    def schedule(self):
        """Returns a schedule object."""
        return site_visit_schedules.get_by_onschedule_model(
            onschedule_model=self._meta.label_lower
        )[1]

    class Meta:
        proxy = True
        verbose_name = "End of Study"
        verbose_name_plural = "End of Study"
