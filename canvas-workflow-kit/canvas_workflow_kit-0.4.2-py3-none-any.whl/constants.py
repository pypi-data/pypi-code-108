from enum import Enum

COMMAND_TYPE_IMAGING = 'imagingOrder'
COMMAND_TYPE_IMMUNIZATION = 'immunization'
COMMAND_TYPE_INSTRUCTION = 'instruct'
COMMAND_TYPE_INTERVIEW = 'interview'
COMMAND_TYPE_LAB_ORDER = 'labOrder'
COMMAND_TYPE_PERFORM = 'perform'
COMMAND_TYPE_PLAN = 'plan'
COMMAND_TYPE_PRESCRIBE = 'prescribe'
COMMAND_TYPE_REFERRAL = 'refer'
COMMAND_TYPE_STRUCTURED_ASSESSMENT = 'structuredAssessment'
COMMAND_TYPE_TASK = 'task'
COMMAND_TYPE_VITALSIGN = 'vitalSign'


class CHANGE_TYPE:

    """
    Change types tell the system when to recompute this protocol.
    Include only the types that are used to compute whether the protocol is used to
    ensure the system processes data in an optimized manner.

    ```python
    class ClinicalQualityMeasure122v6(ClinicalQualityMeasure):

        ...

        compute_on_change_types = [
            CHANGE_TYPE.PROTOCOL_OVERRIDE,
            CHANGE_TYPE.CONDITION,
            CHANGE_TYPE.LAB_REPORT,
            CHANGE_TYPE.PATIENT,
        ]
    ```
    """

    ALLERGY_INTOLERANCE = 'allergy_intolerance'
    "Recompute protocol on an update to allergy information."

    APPOINTMENT = 'appointment'
    "Recompute protocol when a patient's appointment is updated."

    BILLING_LINE_ITEM = 'billing_line_item'
    "Recompute protocol when billing line items are updated."

    CONDITION = 'condition'
    "Recompute protocol when a patient's condition is updated."

    COVERAGE = 'coverage'
    "Recompute protocol when a patient's insurance coverage is updated."

    ENCOUNTER = 'encounter'
    "Recompute protocol when a patient's insurance coverage is updated."

    IMAGING_REPORT = 'imaging_report'
    "Recompute protocol when a patient's imaging report is updated."

    IMMUNIZATION = 'immunization'
    "Recompute protocol when a patient's immunization records have been updated."

    INSTRUCTION = 'instruction'
    "Recompute protocol when a patient's instruction has been updated."

    INTERVIEW = 'interview'
    "Recompute protocol when a patient's interview record has been updated."

    LAB_REPORT = 'lab_report'
    "Recompute protocol when a lab order has been updated."

    MEDICATION = 'medication'
    "Recompute protocol when a medication has been updated."

    MESSAGE = 'message'
    "Recompute protocol when a patient message transmission has been created."

    PATIENT = 'patient'
    "Recompute protocol when a patient's demographic information has been updated."

    PROTOCOL_OVERRIDE = 'protocol_override'
    "Recompute protocol when a protocol is overridden."

    REFERRAL_REPORT = 'referral_report'
    "Recompute protocol when a referral or referral report is updated."

    SUSPECT_HCC = 'suspect_hcc'
    "Recompute protocol when hierarchical condition categories are updated."

    VITAL_SIGN = 'vital_sign'
    "Recompute protocol when a patient's vital signs are updated."


class AlertPlacement(Enum):
    ALERT_PLACEMENT_CHART = 'chart'
    ALERT_PLACEMENT_TIMELINE = 'timeline'
    ALERT_PLACEMENT_APPOINTMENT_CARD = 'appointment_card'
    ALERT_PLACEMENT_SCHEDULING_CARD = 'scheduling_card'
    ALERT_PLACEMENT_PROFILE = 'profile'


class AlertIntent(Enum):
    ALERT_INTENT_INFO = 'info'
    ALERT_INTENT_WARNING = 'warning'
    ALERT_INTENT_ALERT = 'alert'
