# type: ignore
from typing import Dict, List, Optional, cast

import arrow

from cached_property import cached_property

from canvas_workflow_kit import events, settings
from canvas_workflow_kit.protocol import (
    STATUS_DUE,
    STATUS_SATISFIED,
    ClinicalQualityMeasure,
    CodingStruct,
    ExternallyAwareClinicalQualityMeasure,
    ProtocolResult
)
from canvas_workflow_kit.recommendation import StructuredAssessmentRecommendation
from canvas_workflow_kit.timeframe import Timeframe
from canvas_workflow_kit.value_set.customer_value_sets.scan import (
    QuestionnairePVQ,
    StructuredAssessmentQuestionnaireUrinarySymptoms
)


class CustomerScanUrinarySymptomsAssessment(ExternallyAwareClinicalQualityMeasure,
                                            ClinicalQualityMeasure):
    """
    If a patient has urinary leakage, administer a Urinary Symptoms Structured Assessment.
    """

    class Meta:
        title = 'SCAN: Urinary Symptoms Assessment'
        version = '2020-10-13v1'
        description = ''
        information = 'https://docs.google.com/document/d/1NW4b3OT_yPeZy_oIKt_DCCeQ0egDaWFE/edit'

        identifiers = ['CustomerScanUrinarySymptomsAssessmentV1']

        types = ['CQM']

        responds_to_event_types = [
            events.HEALTH_MAINTENANCE,
        ]

        authors = [
            'SCAN',
        ]
        compute_on_change_types = [
            ClinicalQualityMeasure.CHANGE_PROTOCOL_OVERRIDE,
            ClinicalQualityMeasure.CHANGE_INTERVIEW,
        ]

        funding_source = 'SCAN'

        references = ['Written by SCAN']

    @classmethod
    def enabled(cls) -> bool:
        return cast(bool, settings.IS_HEALTHCHEC)

    def in_initial_population(self) -> bool:
        return True

    def interview_lookback_timeframe(self) -> Timeframe:
        return Timeframe(start=self.timeframe.end.shift(days=-30), end=self.timeframe.end)

    @cached_property
    def recent_pvqs(self) -> List[Dict]:
        interviews = self.patient.interviews.find(QuestionnairePVQ).within(
            self.interview_lookback_timeframe())

        for interview in interviews:
            interview['groupedResponses'] = self.group_question_responses(interview)

        return interviews

    @cached_property
    def latest_urine_leakage_response(self) -> Optional[Dict]:
        urine_leakage_question_coding = CodingStruct(code='123978lijsdf386', system='INTERNAL')

        return self.latest_response_to_question(question_coding=urine_leakage_question_coding)

    def latest_urine_leakage_response_date(self) -> Optional[arrow.Arrow]:
        if self.latest_urine_leakage_response:
            return arrow.get(self.latest_urine_leakage_response.get('note_timestamp'))

    def latest_response_to_question(self, question_coding: CodingStruct) -> Optional[Dict]:
        for interview in sorted(
                self.recent_pvqs, key=lambda i: arrow.get(i['noteTimestamp']), reverse=True):
            question_responses = interview.get('groupedResponses', {}).get(
                question_coding.code, [])
            if question_responses:
                return {
                    'note_timestamp': interview['noteTimestamp'],
                    'question_coding': question_coding,
                    'responses': question_responses,
                }

    def last_interview(self, questionnaire_valueset, timeframe=None) -> Optional[Dict]:
        interview = self.patient.interviews.find(questionnaire_valueset).within(
            timeframe or self.timeframe).last()

        if not interview:
            return None

        return interview

    @cached_property
    def last_urinary_symptoms_assessment(self) -> Optional[Dict]:
        return self.last_interview(
            questionnaire_valueset=StructuredAssessmentQuestionnaireUrinarySymptoms,
            timeframe=self.interview_lookback_timeframe())

    def last_urinary_symptoms_assessment_date(self) -> Optional[arrow.Arrow]:
        if self.last_urinary_symptoms_assessment:
            return arrow.get(self.last_urinary_symptoms_assessment['noteTimestamp'])
        return None

    def urinary_symptoms_assessed_on_or_after(self, reference_date: arrow.Arrow) -> bool:
        # It can't have been assessed after a date that doesn't exist!
        if not reference_date:
            return False

        # If it hasn't been assessed, it certainly wasn't assessed after the
        # reference date.
        if not self.last_urinary_symptoms_assessment_date():
            return False

        return self.last_urinary_symptoms_assessment_date() >= reference_date

    def in_denominator(self) -> bool:
        """
        Denominator: Equals Initial Population

        Exclusions: Exclude patients who were in hospice care during the measurement year

        Exceptions: None
        """
        if not self.in_initial_population():
            return False

        if self.patient.hospice_within(self.timeframe):
            return False

        return True

    def in_numerator(self) -> bool:
        """
        Patient is in the numerator if they have not indicated (via the PVQ) that they have
        experienced urine leakage OR if they have indicated experiencing urine leakage, but
        have since had their urinary symptoms assessed.
        """

        urine_leakage_affirmative_answer_coding = CodingStruct(
            code='123978lijsdf387', system='INTERNAL')

        urine_leakage_reported = False

        if self.latest_urine_leakage_response:
            urine_leakage_reported = urine_leakage_affirmative_answer_coding.code in self.latest_urine_leakage_response[  # noqa: E501
                'responses']

        no_urine_leakage_reported = not urine_leakage_reported

        urinary_symptoms_assessed = self.urinary_symptoms_assessed_on_or_after(
            self.latest_urine_leakage_response_date())

        return no_urine_leakage_reported or (urine_leakage_reported and urinary_symptoms_assessed)

    def craft_satisfied_result(self):
        """
        Satisfied if in numerator. (See in_numerator for inclusion details)
        """
        result = ProtocolResult()

        result.due_in = -1
        result.status = STATUS_SATISFIED

        urinary_symptoms_assessed = self.urinary_symptoms_assessed_on_or_after(
            self.latest_urine_leakage_response_date())
        if urinary_symptoms_assessed:
            result.add_narrative(
                f'{self.patient.first_name} reported urinary leakage, but their symptoms were '
                f'assessed {self.display_date(self.last_urinary_symptoms_assessment_date())}.')
        else:
            result.add_narrative(f'{self.patient.first_name} has not reported urinary leakage '
                                 'within the past 30 days.')

        return result

    def craft_unsatisfied_result(self):
        """
        Unsatisfied if not in numerator. Recommend the Urinary Symptoms Structured Assessment.
        """
        result = ProtocolResult()

        result.due_in = -1
        result.status = STATUS_DUE

        result.add_narrative(f'{self.patient.first_name} reported urinary leakage '
                             f'{self.display_date(self.latest_urine_leakage_response_date())}.')

        result.add_recommendation(
            StructuredAssessmentRecommendation(
                key='CUSTOMER_SCAN_RECOMMEND_URINARY_SYMPTOMS_STRUCTURED_ASSESSMENT',
                rank=1,
                button='Assess',
                patient=self.patient,
                questionnaires=[StructuredAssessmentQuestionnaireUrinarySymptoms],
                title='Assess Urinary Symptoms'))

        return result
