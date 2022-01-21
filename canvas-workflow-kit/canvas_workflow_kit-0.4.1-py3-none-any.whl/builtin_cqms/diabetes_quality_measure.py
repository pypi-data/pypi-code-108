# type: ignore
from typing import Optional

from canvas_workflow_kit.protocol import CONTEXT_REPORT, ClinicalQualityMeasure, ProtocolResult
from canvas_workflow_kit.value_set.v2018 import (
    AnnualWellnessVisit,
    Diabetes,
    HomeHealthcareServices,
    OfficeVisit,
    PreventiveCareServicesEstablishedOfficeVisit18AndUp,
    PreventiveCareServicesInitialOfficeVisit18AndUp
)
from canvas_workflow_kit.value_set.value_set import ValueSet


class DiabetesQualityMeasure(ClinicalQualityMeasure):

    class Meta:
        title = 'Diabetes Quality Measure'
        version = '1.0'
        changelog = 'Initial release'

        description = ''
        information = ''

        identifiers = []

        types = ['CCP']

        authors = [
            'Canvas Medical Team',
        ]

        abstract = True

    AGE_RANGE_START = 18
    AGE_RANGE_END = 75

    @classmethod
    def enabled(cls) -> bool:
        # necessary to prevent error based on not implementing the methods
        return True

    def in_initial_population(self) -> bool:
        """
        Initial population: Patients 18-75 years of age with diabetes with a visit during the
        measurement period
        """
        return (self.patient.age_at_between(self.timeframe.end, self.AGE_RANGE_START,
                                            self.AGE_RANGE_END) and
                self.has_diabetes_in_period() and
                (self.patient.has_visit_within(self.timeframe, self.specific_visits)
                 if self.context == CONTEXT_REPORT else True))

    def has_diabetes_in_period(self):
        if self.patient.conditions.find(Diabetes).intersects(
                self.timeframe, still_active=self.patient.active_only):
            return True
        return False

    def first_due_in(self) -> Optional[int]:
        if (self.patient.age_at(self.timeframe.end) < self.AGE_RANGE_START and
                self.has_diabetes_in_period()):
            return (
                self.patient.birthday.shift(years=self.AGE_RANGE_START) - self.timeframe.end).days
        return None

    def in_denominator(self) -> bool:
        raise NotImplementedError('in_denominator must be overridden')

    def in_numerator(self) -> bool:
        raise NotImplementedError('in_numerator must be overridden')

    def compute_results(self) -> ProtocolResult:
        raise NotImplementedError('compute_results must be overridden')

    @property
    def specific_visits(self) -> ValueSet:
        return (
            OfficeVisit |
            # notes will be enriched with encounter logic to manage
            # FaceToFaceInteraction codings (Andrew, 2019-03-11)
            # FaceToFaceInteraction (SNOMED)
            PreventiveCareServicesEstablishedOfficeVisit18AndUp |
            PreventiveCareServicesInitialOfficeVisit18AndUp | HomeHealthcareServices |
            AnnualWellnessVisit)
