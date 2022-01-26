import json

from builtins import bool
from typing import Any, Dict, List, Optional, Type

import arrow

from canvas_workflow_kit.patient_recordset import (
    AllergyIntoleranceRecordSet,
    PatientRecordSet,
    BillingLineItemRecordSet,
    ConditionRecordSet,
    ImagingReportRecordSet,
    ImmunizationRecordSet,
    InpatientStayRecordSet,
    InstructionRecordSet,
    InterviewRecordSet,
    LabReportRecordSet,
    MedicationRecordSet,
    MessageRecordSet,
    ProtocolOverrideRecordSet,
    ReasonForVisitRecordSet,
    ReferralRecordSet,
    ReferralReportRecordSet,
    UpcomingAppointmentNoteRecordSet,
    UpcomingAppointmentRecordSet,
    VitalSignRecordSet
)
from canvas_workflow_kit.internal.attrdict import to_attr_dict
from canvas_workflow_kit.timeframe import Timeframe
from canvas_workflow_kit.value_set.value_set import ValueSet

# from protocols.value_set.v2018 import (DischargedToHealthCareFacilityForHospiceCare,
#                                  DischargedToHomeForHospiceCare, HomeHealthcareServices,
#                                  HospiceCareAmbulatory)


class Patient:
    """
    Wrapper around a Canvas patient to add convenience methods specific to science functionality.
    """
    SEX_FEMALE = 'F'
    SEX_MALE = 'M'

    RECORDSET_CLASSES = (
        AllergyIntoleranceRecordSet,
        BillingLineItemRecordSet,
        ConditionRecordSet,
        ImagingReportRecordSet,
        ImmunizationRecordSet,
        InpatientStayRecordSet,
        InstructionRecordSet,
        InterviewRecordSet,
        LabReportRecordSet,
        MedicationRecordSet,
        ProtocolOverrideRecordSet,
        ReasonForVisitRecordSet,
        ReferralRecordSet,
        ReferralReportRecordSet,
        UpcomingAppointmentNoteRecordSet,
        UpcomingAppointmentRecordSet,
        VitalSignRecordSet,
    )

    def __init__(self, data: Dict):
        self.patient = data.get('patient', None)
        self.active_only = False

        self.allergy_intolerances = AllergyIntoleranceRecordSet.new_from(
            data.get(AllergyIntoleranceRecordSet.API_UPDATE_FIELD, []))

        self.billing_line_items = BillingLineItemRecordSet.new_from(
            data.get(BillingLineItemRecordSet.API_UPDATE_FIELD, []))

        self.conditions = ConditionRecordSet.new_from(
            data.get(ConditionRecordSet.API_UPDATE_FIELD, []))

        self.imaging_reports = ImagingReportRecordSet.new_from(
            data.get(ImagingReportRecordSet.API_UPDATE_FIELD, []))

        self.immunizations = ImmunizationRecordSet.new_from(
            data.get(ImmunizationRecordSet.API_UPDATE_FIELD, []))

        self.instructions = InstructionRecordSet.new_from(
            data.get(InstructionRecordSet.API_UPDATE_FIELD, []))

        self.interviews = InterviewRecordSet.new_from(
            data.get(InterviewRecordSet.API_UPDATE_FIELD, []))

        self.lab_reports = LabReportRecordSet.new_from(
            data.get(LabReportRecordSet.API_UPDATE_FIELD, []))

        self.medications = MedicationRecordSet.new_from(
            data.get(MedicationRecordSet.API_UPDATE_FIELD, []))

        self.messages = MessageRecordSet.new_from(
            data.get(MessageRecordSet.API_UPDATE_FIELD, []))

        self.protocol_overrides = ProtocolOverrideRecordSet.new_from(
            data.get(ProtocolOverrideRecordSet.API_UPDATE_FIELD, []))

        self.reason_for_visits = ReasonForVisitRecordSet.new_from(
            data.get(ReasonForVisitRecordSet.API_UPDATE_FIELD, []))

        self.referral_reports = ReferralReportRecordSet.new_from(
            data.get(ReferralReportRecordSet.API_UPDATE_FIELD, []))

        self.referrals = ReferralRecordSet.new_from(
            data.get(ReferralRecordSet.API_UPDATE_FIELD, []))

        self.inpatient_stays = InpatientStayRecordSet.new_from(
            data.get(InpatientStayRecordSet.API_UPDATE_FIELD, []))

        self.suspect_hccs = data.get('suspectHccs', [])

        self.upcoming_appointments = UpcomingAppointmentRecordSet.new_from(
            data.get(UpcomingAppointmentRecordSet.API_UPDATE_FIELD))

        self.upcoming_appointment_notes = UpcomingAppointmentNoteRecordSet.new_from(
            data.get(UpcomingAppointmentNoteRecordSet.API_UPDATE_FIELD))

        self.vital_signs = VitalSignRecordSet.new_from(
            data.get(VitalSignRecordSet.API_UPDATE_FIELD, []))

        if self.patient and self.patient.get('addresses'):
            self.addresses = PatientRecordSet.new_from(to_attr_dict(self.patient.get('addresses')))

    @classmethod
    def recordset_fields(cls) -> List[str]:
        """
        Returns available patient record set fields ('conditions', 'medications', etc.)
        """
        return [r_cls.PATIENT_FIELD for r_cls in cls.RECORDSET_CLASSES]

    @property
    def patient_key(self) -> str:
        return self.patient['key']

    @property
    def first_name(self) -> str:
        return self.patient['firstName']

    @property
    def last_name(self) -> str:
        return self.patient.get('lastName', '')

    @property
    def is_female(self) -> bool:
        return self.patient['sexAtBirth'] == self.SEX_FEMALE

    @property
    def is_male(self) -> bool:
        return self.patient['sexAtBirth'] == self.SEX_MALE

    @property
    def is_african_american(self) -> bool:
        return self.patient['biologicalRaceCode'] == '2054-5'

    @property
    def date_of_birth(self) -> str:
        return self.patient['birthDate']

    @property
    def birthday(self) -> arrow.Arrow:
        return arrow.get(self.patient['birthDate'], 'YYYY-MM-DD')

    @property
    def coverages(self) -> List[Dict]:
        return self.patient.get('coverages', [])

    @property
    def age(self):
        return self.age_at(arrow.now())

    # TODO timezones
    def age_at(self, time: arrow.Arrow) -> float:
        """
        Returns the number of years already passed at the time provided
        plus the number of days between the passed birthday and the provided date
        divided by the number of days between the passed and the next birthday
        """
        age = 0
        if not self.patient:
            return age

        birth_day = self.birthday
        if birth_day.date() < time.date():
            age = time.datetime.year - birth_day.datetime.year
            if time.datetime.month < birth_day.datetime.month or (
                    time.datetime.month == birth_day.datetime.month and
                    time.datetime.day < birth_day.datetime.day):
                age -= 1

            current_year = birth_day.shift(years=age)
            next_year = birth_day.shift(years=age + 1)
            age += (time.date() - current_year.date()) / (next_year.date() - current_year.date())
        return age

    def age_at_between(self, time: arrow.Arrow, age_start_inclusive: int,
                       age_end_exclusive: int) -> bool:
        return age_start_inclusive <= self.age_at(time) < age_end_exclusive

    # TODO_REPORTING
    def hospice_within(self, timeframe: Timeframe) -> bool:
        # FIX: is this correct, are these hospice value-sets conditions?
        # return (self.conditions
        #         .before(timeframe.end)
        #         .find(HospiceCareAmbulatory |
        #               DischargedToHomeForHospiceCare |
        #               DischargedToHealthCareFacilityForHospiceCare))  # yapf: disable
        return False

    def has_visit_within(self, timeframe: Timeframe,
                         encounters: Optional[Type[ValueSet]] = None) -> bool:
        if not encounters:
            return True
        return bool(self.count_visit_within(timeframe, encounters) > 0)

    def count_visit_within(self, timeframe: Timeframe,
                           encounters: Optional[Type[ValueSet]] = None) -> int:
        if not encounters:
            return 0

        recordset = (self
                     .billing_line_items
                     .after(timeframe.start)
                     .before(timeframe.end)
                     .find(encounters))  # yapf: disable

        return len(recordset.records) if recordset else 0

    def as_dict(self) -> Dict[str, Any]:
        return {
            'patient_key': self.patient_key,
            'patient': self.patient,
            **{
                cls.PATIENT_FIELD: getattr(self, cls.PATIENT_FIELD).records
                for cls in self.RECORDSET_CLASSES
            },
        }

    def print(self) -> None:
        print(json.dumps(self.as_dict(), indent=2))
