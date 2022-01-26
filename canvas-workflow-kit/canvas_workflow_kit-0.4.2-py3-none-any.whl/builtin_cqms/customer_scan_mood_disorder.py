# type: ignore
from typing import Dict, Optional, cast

import arrow

from cached_property import cached_property

from canvas_workflow_kit import events, settings
from canvas_workflow_kit.protocol import (
    STATUS_DUE,
    STATUS_SATISFIED,
    ClinicalQualityMeasure,
    ExternallyAwareClinicalQualityMeasure,
    ProtocolResult
)
from canvas_workflow_kit.recommendation import StructuredAssessmentRecommendation
from canvas_workflow_kit.timeframe import Timeframe
from canvas_workflow_kit.value_set.customer_value_sets.scan import (
    StructuredAssessmentQuestionnaireMoodDisorder
)
from canvas_workflow_kit.value_set.value_set import ValueSet


class QuestionnairePhq9(ValueSet):

    VALUE_SET_NAME = 'PHQ-9 Questionnaire'

    LOINC = {'44249-1'}


class QuestionnaireGad7(ValueSet):

    VALUE_SET_NAME = 'GAD-7 Questionnaire'

    LOINC = {'69737-5'}


class CustomerScanMoodDisorder(ExternallyAwareClinicalQualityMeasure, ClinicalQualityMeasure):
    """
    Major Depression
    phq9 score of 5 or greater
    Mood Disorder SA
    Please consider the need to include major depression as a diagnosis within the care plan.
    Please use the Mood Disorder Structured Assessment.

    Generalized Anxiety Disorder
    GAD7 score of 5 or greater
    Mood Disorder SA
    Please consider the need to include generalized anxiety disorder as a diagnosis within the care
    plan.  Please use the Mood Disorder Structured Assessment.
    """

    class Meta:
        title = 'SCAN: Mood Disorder Structured Assessment'
        version = '2020-09-04v1'
        description = ''
        information = 'https://docs.google.com/document/d/1NW4b3OT_yPeZy_oIKt_DCCeQ0egDaWFE/edit'

        identifiers = ['CustomerScanMoodDisorderV1']

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

    def last_interview(self, questionnaire_valueset, timeframe=None) -> Optional[Dict]:
        interview = self.patient.interviews.find(questionnaire_valueset).within(
            timeframe or self.timeframe).last()

        if not interview:
            return None

        return interview

    @cached_property
    def last_gad7(self) -> Optional[Dict]:
        return self.last_interview(
            questionnaire_valueset=QuestionnaireGad7,
            timeframe=self.interview_lookback_timeframe())

    def last_gad7_score(self) -> Optional[int]:
        if self.last_gad7:
            return self.last_gad7['results'][0]['score']
        return None

    def last_gad7_date(self) -> Optional[arrow.Arrow]:
        if self.last_gad7:
            return arrow.get(self.last_gad7['noteTimestamp'])
        return None

    @cached_property
    def last_phq9(self) -> Optional[Dict]:
        return self.last_interview(
            questionnaire_valueset=QuestionnairePhq9,
            timeframe=self.interview_lookback_timeframe())

    def last_phq9_score(self) -> Optional[int]:
        if self.last_phq9:
            return self.last_phq9['results'][0]['score']
        return None

    def last_phq9_date(self) -> Optional[arrow.Arrow]:
        if self.last_phq9:
            return arrow.get(self.last_phq9['noteTimestamp'])
        return None

    def last_elevated_gad7_or_phq9_date(self) -> Optional[arrow.Arrow]:
        date_of_most_recent_elevated_screening = None

        if self.last_gad7_score() and self.last_gad7_score() >= 5:
            date_of_most_recent_elevated_screening = self.last_gad7_date()

        if self.last_phq9_score() and self.last_phq9_score() >= 5:
            if date_of_most_recent_elevated_screening and self.last_phq9_date():
                date_of_most_recent_elevated_screening = max(
                    date_of_most_recent_elevated_screening, self.last_phq9_date())
            else:
                date_of_most_recent_elevated_screening = self.last_phq9_date()

        return date_of_most_recent_elevated_screening

    @cached_property
    def last_mood_disorder_assessment(self) -> Optional[Dict]:
        return self.last_interview(
            questionnaire_valueset=StructuredAssessmentQuestionnaireMoodDisorder,
            timeframe=self.interview_lookback_timeframe())

    def last_mood_disorder_assessment_date(self) -> Optional[arrow.Arrow]:
        if self.last_mood_disorder_assessment:
            return arrow.get(self.last_mood_disorder_assessment['noteTimestamp'])
        return None

    def mood_disorder_assessed_on_or_after(self, reference_date: arrow.Arrow) -> bool:
        # It can't have been assessed after a date that doesn't exist!
        if not reference_date:
            return False

        # If it hasn't been assessed, it certainly wasn't assessed after the
        # reference date.
        if not self.last_mood_disorder_assessment_date():
            return False

        return self.last_mood_disorder_assessment_date() >= reference_date

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
        Patient is in the numerator if their last gad7 or phq9 test was not elevated, or if it was,
        but they have had a mood disorder assessment since then. They are also in the numerator if
        they have not had any gad7 or phq9 result. (Can't be elevated if never assessed!)
        """
        mood_disorder_indicated = False

        date_of_most_recent_elevated_screening = self.last_elevated_gad7_or_phq9_date()

        if date_of_most_recent_elevated_screening:
            mood_disorder_indicated = True

        # Patient is in the numerator if the scores do not indicate a mood
        # disorder. Being in the numerator means the protocol is satisfied.
        # The goal is to ensure patients are monitored appropriately. Getting
        # the numerator as close to the denominator as possible indicates good
        # monitoring.
        mood_disorder_not_indicated = not mood_disorder_indicated

        mood_disorder_assessed = self.mood_disorder_assessed_on_or_after(
            date_of_most_recent_elevated_screening)

        return (mood_disorder_not_indicated or
                (mood_disorder_indicated and mood_disorder_assessed))

    def craft_satisfied_result(self):
        """
        Satisfied if in numerator. (See numerator description)
        """
        result = ProtocolResult()

        result.due_in = -1
        result.status = STATUS_SATISFIED

        mood_disorder_assessed = self.mood_disorder_assessed_on_or_after(
            self.last_elevated_gad7_or_phq9_date())
        if mood_disorder_assessed:
            result.add_narrative(f'{self.patient.first_name} had elevated PHQ9 or GAD7 scores, '
                                 'but a mood disorder assessment was performed '
                                 f'{self.display_date(self.last_elevated_gad7_or_phq9_date())}')
        else:
            result.add_narrative(f'{self.patient.first_name} has not had elevated PHQ9 or GAD7 '
                                 'scores in the past 30 days.')

        return result

    def craft_unsatisfied_result(self):
        """
        Unsatisfied if not in the numerator. Recommend a Mood Disorder Structured Assessment.
        """
        result = ProtocolResult()

        result.due_in = -1
        result.status = STATUS_DUE

        if self.last_phq9_score() and self.last_phq9_score() >= 5:
            result.add_narrative(f'{self.patient.first_name} had a PHQ9 score >= 5 '
                                 f'{self.display_date(self.last_phq9_date())}.')

        if self.last_gad7_score() and self.last_gad7_score() >= 5:
            result.add_narrative(f'{self.patient.first_name} had a GAD7 score >= 5 '
                                 f'{self.display_date(self.last_gad7_date())}.')

        result.add_recommendation(
            StructuredAssessmentRecommendation(
                key='CUSTOMER_SCAN_RECOMMEND_MOOD_DISORDER_STRUCTURED_ASSESSMENT',
                rank=1,
                button='Assess',
                patient=self.patient,
                questionnaires=[StructuredAssessmentQuestionnaireMoodDisorder],
                title='Assess Mood Disorder'))

        return result
