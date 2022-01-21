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
    QuestionnaireComprehensiveGeriatricAssessment,
    StructuredAssessmentQuestionnaireCognitiveDisorders
)


class CustomerScanDementiaAssessment(ExternallyAwareClinicalQualityMeasure,
                                     ClinicalQualityMeasure):
    """
    A clinical quality measure (which is a type of protocol) for the customer SCAN.
    More information at https://docs.google.com/document/d/1NW4b3OT_yPeZy_oIKt_DCCeQ0egDaWFE/edit
    """

    class Meta:
        title = 'SCAN: Dementia Assessment'
        version = '2020-10-13v1'
        description = 'A clinical quality measure (which is a type of protocol) for the customer SCAN.'  # noqa: E501
        information = 'https://docs.google.com/document/d/1NW4b3OT_yPeZy_oIKt_DCCeQ0egDaWFE/edit'

        identifiers = ['CustomerScanDementiaAssessmentV1']

        types = ['CQM']

        responds_to_event_types = [
            events.HEALTH_MAINTENANCE,
        ]

        authors = [
            'SCAN',
        ]
        references = ['Written by SCAN']

        compute_on_change_types = [
            ClinicalQualityMeasure.CHANGE_PROTOCOL_OVERRIDE,
            ClinicalQualityMeasure.CHANGE_INTERVIEW,
        ]

        funding_source = 'SCAN'

    @classmethod
    def enabled(cls) -> bool:
        return cast(bool, settings.IS_HEALTHCHEC)

    def in_initial_population(self) -> bool:
        return True

    def interview_lookback_timeframe(self) -> Timeframe:
        return Timeframe(start=self.timeframe.end.shift(days=-30), end=self.timeframe.end)

    @cached_property
    def recent_comprehensive_geriatric_assessments(self) -> List[Dict]:
        interviews = self.patient.interviews.find(
            QuestionnaireComprehensiveGeriatricAssessment).within(
                self.interview_lookback_timeframe())

        for interview in interviews:
            interview['groupedResponses'] = self.group_question_responses(interview)

        return interviews

    @cached_property
    def latest_minicog_response(self) -> Optional[Dict]:
        minicog_question_coding = CodingStruct(
            code='SCAN_MINICOG_QUESTION_CODE', system='INTERNAL')

        return self.latest_response_to_question(question_coding=minicog_question_coding)

    def latest_minicog_response_date(self) -> Optional[arrow.Arrow]:
        if self.latest_minicog_response:
            return arrow.get(self.latest_minicog_response.get('note_timestamp'))
        return None

    def latest_response_to_question(self, question_coding: CodingStruct) -> Optional[Dict]:
        for interview in sorted(
                self.recent_comprehensive_geriatric_assessments,
                key=lambda i: arrow.get(i['noteTimestamp']),
                reverse=True):
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
    def last_cognitive_disorders_assessment(self) -> Optional[Dict]:
        return self.last_interview(
            questionnaire_valueset=StructuredAssessmentQuestionnaireCognitiveDisorders,
            timeframe=self.interview_lookback_timeframe())

    def last_cognitive_disorders_assessment_date(self) -> Optional[arrow.Arrow]:
        if self.last_cognitive_disorders_assessment:
            return arrow.get(self.last_cognitive_disorders_assessment['noteTimestamp'])
        return None

    def cognitive_disorders_assessed_on_or_after(self, reference_date: arrow.Arrow) -> bool:
        # It can't have been assessed after a date that doesn't exist!
        if not reference_date:
            return False

        # If it hasn't been assessed, it certainly wasn't assessed after the
        # reference date.
        if not self.last_cognitive_disorders_assessment_date():
            return False

        return self.last_cognitive_disorders_assessment_date() >= reference_date

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
        Represents whether this patient should be counted in the numerator of a fraction
        representing how many patients have been properly appraised regarding the
        CustomerScanDementiaAssessment clinical quality measure.
        A patient have been properly appraised if they either indicated via the assessment that they
        did not need further assessment or, if they indicated that they did, they received that
        assessment.
        """

        low_minicog_score_reported = False

        if self.latest_minicog_response:
            if set(self.latest_minicog_response['responses']).intersection(
                    set(['minicog_score_0', 'minicog_score_1', 'minicog_score_2'])):
                low_minicog_score_reported = True

        no_low_minicog_score_reported = not low_minicog_score_reported

        cognitive_disorders_assessed = self.cognitive_disorders_assessed_on_or_after(
            self.latest_minicog_response_date())

        return no_low_minicog_score_reported or (low_minicog_score_reported and
                                                 cognitive_disorders_assessed)

    def craft_satisfied_result(self):
        """
        Creates and returns a STATUS_SATISFIED-status protocol result with a narrative explaining
        the status of a recent CustomerScanDementiaAssessment if there was one.
        """
        result = ProtocolResult()

        result.due_in = -1
        result.status = STATUS_SATISFIED

        cognitive_disorders_assessed = self.cognitive_disorders_assessed_on_or_after(
            self.latest_minicog_response_date())

        if cognitive_disorders_assessed:
            # Assessment was administered
            result.add_narrative(
                f'{self.patient.first_name} had a cognitive disorders assessment '
                f'{self.display_date(self.last_cognitive_disorders_assessment_date())}.')
        else:
            if self.latest_minicog_response_date():
                result.add_narrative(
                    f"{self.patient.first_name}'s most recent minicog score was not less than 3.")
            else:
                result.add_narrative(f'{self.patient.first_name} has not had a '
                                     'low minicog score in the past 30 days.')

        return result

    def craft_unsatisfied_result(self):
        """
        Creates and returns a STATUS_DUE-status protocol result with a recommendation for a
        CUSTOMER_SCAN_RECOMMEND_COGNITIVE_DISORDERS_ASSESSMENT.
        """
        result = ProtocolResult()

        result.due_in = -1
        result.status = STATUS_DUE

        result.add_narrative(f'{self.patient.first_name} had a minicog score < 3 '
                             f'{self.display_date(self.latest_minicog_response_date())}.')

        result.add_recommendation(
            StructuredAssessmentRecommendation(
                key='CUSTOMER_SCAN_RECOMMEND_COGNITIVE_DISORDERS_ASSESSMENT',
                rank=1,
                button='Assess',
                patient=self.patient,
                questionnaires=[StructuredAssessmentQuestionnaireCognitiveDisorders],
                title='Assess Cognitive Disorder'))

        return result
