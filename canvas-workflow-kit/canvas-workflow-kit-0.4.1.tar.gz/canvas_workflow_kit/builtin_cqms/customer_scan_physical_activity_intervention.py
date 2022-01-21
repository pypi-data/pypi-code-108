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
from canvas_workflow_kit.recommendation import InterviewRecommendation
from canvas_workflow_kit.timeframe import Timeframe
from canvas_workflow_kit.value_set.customer_value_sets.scan import (
    QuestionnaireHealthCHECReferrals,
    QuestionnairePVQ
)


class CustomerScanPhysicalActivityIntervention(ExternallyAwareClinicalQualityMeasure,
                                               ClinicalQualityMeasure):
    """
    Look out for patients reporting rare or light physical activity and recommend the
    physical activity intervention if needed.
    """

    class Meta:
        title = 'SCAN: Physical Activity Intervention'
        version = '2020-10-13v1'
        description = ''
        information = 'https://docs.google.com/document/d/1NW4b3OT_yPeZy_oIKt_DCCeQ0egDaWFE/edit'

        identifiers = ['CustomerScanPhysicalActivityInterventionV1']

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
    def latest_how_physically_active_response(self) -> Optional[Dict]:
        how_physically_active_question_coding = CodingStruct(
            code='123978lijsdf169', system='INTERNAL')

        return self.latest_response_to_question(
            question_coding=how_physically_active_question_coding)

    def latest_how_physically_active_response_date(self) -> Optional[arrow.Arrow]:
        if self.latest_how_physically_active_response:
            return arrow.get(self.latest_how_physically_active_response.get('note_timestamp'))

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

    @cached_property
    def last_referral_for_physical_activity_intervention(self) -> Optional[Dict]:
        interviews = self.patient.interviews.find(QuestionnaireHealthCHECReferrals).within(
            self.interview_lookback_timeframe())

        if not interviews:
            return None

        # Go through them in order with the most recent one first and working
        # backwards
        # return the first one with a response representing a physical
        # activity intervention
        for interview in sorted(
                interviews, key=lambda i: arrow.get(i['noteTimestamp']), reverse=True):
            for response in interview.get('responses', []):
                if response.get(
                        'code'
                ) == '390893007' and 'Physical Activity Intervention' in response.get('value', ''):
                    return interview

        # nothing found
        return None

    def last_referral_for_physical_activity_intervention_date(self) -> Optional[arrow.Arrow]:
        if self.last_referral_for_physical_activity_intervention:
            return arrow.get(
                self.last_referral_for_physical_activity_intervention['noteTimestamp'])
        return None

    def referred_for_physical_activity_intervention_on_or_after(
            self, reference_date: arrow.Arrow) -> bool:
        # It can't have been referred after a date that doesn't exist!
        if not reference_date:
            return False

        # If it hasn't been referred, it certainly wasn't referred after the
        # reference date.
        if not self.last_referral_for_physical_activity_intervention_date():
            return False

        return self.last_referral_for_physical_activity_intervention_date() >= reference_date

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
        Patient is in the numerator if they have not indicated inadequate physical activity OR if
        they have indicated inadequate physical activity, but they have been referred for a
        physical activity intervention since then.
        """

        inadequate_physical_activity_reported = False

        rarely_physically_active_answer_coding = CodingStruct(
            code='123978lijsdf170', system='INTERNAL')
        light_not_every_week_physically_active_answer_coding = CodingStruct(
            code='123978lijsdf171', system='INTERNAL')
        light_every_week_physically_active_answer_coding = CodingStruct(
            code='123978lijsdf172', system='INTERNAL')

        if self.latest_how_physically_active_response:
            set_of_answers_indicating_additional_monitoring_required = set([
                rarely_physically_active_answer_coding.code,
                light_not_every_week_physically_active_answer_coding.code,
                light_every_week_physically_active_answer_coding.code
            ])
            set_of_actual_responses = set(
                self.latest_how_physically_active_response.get('responses', []))
            inadequate_physical_activity_reported = len(
                set_of_actual_responses.intersection(
                    set_of_answers_indicating_additional_monitoring_required)) > 0

        no_inadequate_physical_activity_reported = not inadequate_physical_activity_reported

        referred_for_physical_activity_intervention = self.referred_for_physical_activity_intervention_on_or_after(  # noqa: E501
            self.latest_how_physically_active_response_date())

        return no_inadequate_physical_activity_reported or (
            inadequate_physical_activity_reported and referred_for_physical_activity_intervention)

    def craft_satisfied_result(self):
        """
        Satisfied if in the numerator. (See in_numerator description for inclusion criteria)
        """
        result = ProtocolResult()

        result.due_in = -1
        result.status = STATUS_SATISFIED

        referred_for_physical_activity_intervention = self.referred_for_physical_activity_intervention_on_or_after(  # noqa: E501
            self.latest_how_physically_active_response_date())

        if referred_for_physical_activity_intervention:
            result.add_narrative(
                f'{self.patient.first_name} reported suboptimal physical '
                'activity, but was referred for physical activity intervention '
                f'{self.display_date(self.last_referral_for_physical_activity_intervention_date())}.'  # noqa: E501
            )
        else:
            result.add_narrative(f'{self.patient.first_name} has not reported suboptimal physical '
                                 'activity in the past 30 days.')

        return result

    def craft_unsatisfied_result(self):
        """
        Unsatisfied if not in the numerator. Recommend a Physical Activity Intervention.
        """
        result = ProtocolResult()

        result.due_in = -1
        result.status = STATUS_DUE

        result.add_narrative(
            f'{self.patient.first_name} reported suboptimal physical activity '
            f'{self.display_date(self.latest_how_physically_active_response_date())}.')

        result.add_recommendation(
            InterviewRecommendation(
                key='CUSTOMER_SCAN_RECOMMEND_PHYSICAL_ACTIVITY_INTERVENTION_REFERRAL',
                rank=1,
                button='Refer',
                patient=self.patient,
                questionnaires=[QuestionnaireHealthCHECReferrals],
                title='Refer for Physical Activity Intervention'))

        return result
