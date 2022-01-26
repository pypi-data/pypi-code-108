# flake8: noqa
from canvas_workflow_kit import events
from canvas_workflow_kit.protocol import ClinicalQualityMeasure
from canvas_workflow_kit.value_set.v2018 import (OfficeVisit, PsychVisit, FaceToFaceInteractionNoEd, Dysthymia,
                                 MajorDepression, CareServicesInLongTermResidentialFacility,
                                 PalliativeCareEncounter, PalliativeCare, BipolarDisorder,
                                 PersonalityDisorder)


class DepressionUtilizationPhq9(ClinicalQualityMeasure):
    """
    Guidance: If a patient has a qualifying diagnosis and encounter in more than one of the 4 month
    periods within the measurement year, the patient must be counted (denominator and numerator) in
    each qualifying 4 month period. For example, a patient could be counted in the first and third
    4 month periods.
    """

    # this protocol was created before an overhaul and needs finishing
    # to work
    @classmethod
    def enabled(cls):
        return False

    responds_to_event_types = [
        events.HEALTH_MAINTENANCE,
    ]

    def in_initial_population(self):

        def age_range():
            # TODO is this correct or can the patient turn 18 during the measurement period?
            return self.patient.age_at(self.timeframe.start) >= 18

        def has_office_visit():
            return self.patient.conditions_within(self.timeframe, OfficeVisit)

        def has_psych_visit():
            return self.patient.conditions_within(self.timeframe, PsychVisit)

        def has_face_to_face_no_ed():
            return self.patient.conditions_within(self.timeframe, FaceToFaceInteractionNoEd)

        def has_qualifying_diagnosis():
            # TODO is this correct or does the diagnosis have to be within the timeframe, not just
            # before it ends?
            return any([
                self.patient.conditions_within(self.timeframe, Dysthymia),
                self.patient.conditions_within(self.timeframe, MajorDepression),
            ])

        return all([
            age_range(),
            has_qualifying_diagnosis(),
            any([
                has_office_visit(),
                has_psych_visit(),
                has_face_to_face_no_ed(),
            ]),
        ])

    def in_denominator(self):
        if not self.in_initial_population():
            return False

        def long_term_care_resident():
            return self.patient.conditions_after_one_year_before_timeframe_end(
                self.timeframe, CareServicesInLongTermResidentialFacility)

        def received_palliative_care():
            return any([
                self.patient.conditions_after_one_year_before_timeframe_end(
                    self.timeframe, PalliativeCare),
                self.patient.conditions_after_one_year_before_timeframe_end(
                    self.timeframe, PalliativeCareEncounter),
            ])

        def has_disqualifying_disorder():
            return any([
                self.patient.conditions_before(self.timeframe.end, BipolarDisorder),
                self.patient.conditions_before(self.timeframe.end, PersonalityDisorder),
            ])

        # TODO 'patient characteristic: expired' not in value set
        def deceased():
            return False

        return all([
            not deceased(),
            not received_palliative_care(),
            not long_term_care_resident(),
            not has_disqualifying_disorder(),
        ])

    def in_numerator(self):
        pass
        # return self.patient.has_any_within(timeframe=self.timeframe,
        # **value_sets.phq_tool.values)
