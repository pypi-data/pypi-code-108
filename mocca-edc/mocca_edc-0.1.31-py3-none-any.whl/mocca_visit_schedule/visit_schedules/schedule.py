from dateutil.relativedelta import relativedelta
from edc_ltfu.utils import get_ltfu_model_name
from edc_visit_schedule import Schedule
from edc_visit_schedule import Visit as BaseVisit
from edc_visit_schedule.constants import DAY1

from ..constants import SCHEDULE
from .crfs import crfs, crfs_d1, crfs_missed
from .crfs import crfs_prn as default_crfs_prn
from .crfs import crfs_unscheduled as default_crfs_unscheduled
from .requisitions import requisitions_all, requisitions_d1, requisitions_prn

default_requisitions = None


class Visit(BaseVisit):
    def __init__(
        self,
        crfs_unscheduled=None,
        requisitions_unscheduled=None,
        crfs_prn=None,
        requisitions_prn=None,
        allow_unscheduled=None,
        **kwargs
    ):
        super().__init__(
            allow_unscheduled=True if allow_unscheduled is None else allow_unscheduled,
            crfs_unscheduled=crfs_unscheduled or default_crfs_unscheduled,
            requisitions_unscheduled=requisitions_unscheduled or default_requisitions,
            crfs_prn=crfs_prn or default_crfs_prn,
            requisitions_prn=requisitions_prn,  # or default_requisitions_prn,
            crfs_missed=crfs_missed,
            **kwargs,
        )


# schedule for new participants
schedule = Schedule(
    name=SCHEDULE,
    verbose_name="Day 1 to Month 12",
    onschedule_model="mocca_prn.onschedule",
    offschedule_model="mocca_prn.offschedule",
    consent_model="mocca_consent.subjectconsent",
    appointment_model="edc_appointment.appointment",
    loss_to_followup_model=get_ltfu_model_name(),
)

visit00 = Visit(
    code=DAY1,
    title="Day 1",
    timepoint=0,
    rbase=relativedelta(days=0),
    rlower=relativedelta(days=0),
    rupper=relativedelta(days=0),
    requisitions=requisitions_d1,
    requisitions_prn=requisitions_prn,
    crfs=crfs_d1,
    facility_name="5-day-clinic",
)

schedule.add_visit(visit=visit00)

for n in range(1, 13):
    visit = Visit(
        code=str(1000 + (10 * n)),
        title=f"Month {n}",
        timepoint=n,
        rbase=relativedelta(months=n),
        rlower=relativedelta(months=0),
        rupper=relativedelta(months=n + 1),
        requisitions=requisitions_all,
        requisitions_prn=requisitions_prn,
        crfs=crfs,
        facility_name="5-day-clinic",
    )
    schedule.add_visit(visit=visit)
