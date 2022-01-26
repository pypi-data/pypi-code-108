from django.core.exceptions import ImproperlyConfigured
from edc_action_item import Action, site_action_items
from edc_adverse_event.constants import AE_INITIAL_ACTION
from edc_blood_results import BLOOD_RESULTS_LIPID_ACTION
from edc_constants.constants import HIGH_PRIORITY, YES
from edc_ltfu.constants import LTFU_ACTION
from edc_visit_schedule.utils import is_baseline
from edc_visit_tracking.action_items import VisitMissedAction

from mocca_visit_schedule.constants import SCHEDULE


class SubjectVisitMissedAction(VisitMissedAction):
    reference_model = "mocca_subject.subjectvisitmissed"
    admin_site_name = "mocca_subject_admin"
    loss_to_followup_action_name = None

    def get_loss_to_followup_action_name(self):
        schedule = self.reference_obj.visit.appointment.schedule
        if schedule.name == SCHEDULE:
            return LTFU_ACTION
        raise ImproperlyConfigured(
            "Unable to determine action name. Schedule name not known. "
            f"Got {schedule.name}."
        )


class BaseBloodResultsAction(Action):
    name = None
    display_name = None
    reference_model = None

    priority = HIGH_PRIORITY
    show_on_dashboard = True
    create_by_user = False

    def reopen_action_item_on_change(self):
        return False

    def get_next_actions(self):
        next_actions = []
        if (
            self.reference_obj.results_abnormal == YES
            and self.reference_obj.results_reportable == YES
            and not is_baseline(self.reference_obj_has_changed)
        ):
            # AE for reportable result, though not on DAY1.0
            next_actions = [AE_INITIAL_ACTION]
        return next_actions


class BloodResultsLipidAction(BaseBloodResultsAction):
    name = BLOOD_RESULTS_LIPID_ACTION
    display_name = "Reportable result: LIPIDS"
    reference_model = "mocca_subject.bloodresultslipid"


site_action_items.register(BloodResultsLipidAction)
site_action_items.register(SubjectVisitMissedAction)
