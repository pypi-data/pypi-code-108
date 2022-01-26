from typing import Dict, List, Optional, cast

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
from canvas_workflow_kit.recommendation import InterviewRecommendation
from canvas_workflow_kit.timeframe import Timeframe
from canvas_workflow_kit.value_set.customer_value_sets.scan import (
    QuestionnaireHealthCHECReferrals,
    QuestionnairePVQ
)


class CustomerScanComplexCaseManagementReferral(ExternallyAwareClinicalQualityMeasure,
                                                ClinicalQualityMeasure):
    """
    A clinical quality measure (which is a type of protocol) used only by one customer (SCAN).
    More information at https://docs.google.com/document/d/1NW4b3OT_yPeZy_oIKt_DCCeQ0egDaWFE/edit.
    """

    class Meta:
        title = 'SCAN: Complex Case Management Referral'
        version = '2020-10-13v1'
        description = 'A clinical quality measure (which is a type of protocol) used only by SCAN.'
        information = 'https://docs.google.com/document/d/1NW4b3OT_yPeZy_oIKt_DCCeQ0egDaWFE/edit'

        identifiers = ['CustomerScanComplexCaseManagementReferralV1']

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
    def recent_pvqs(self) -> List[Dict]:
        interviews = cast(
            List[Dict],
            self.patient.interviews.find(QuestionnairePVQ).within(
                self.interview_lookback_timeframe()))

        for interview in interviews:
            interview['groupedResponses'] = self.group_question_responses(interview)

        return interviews

    @cached_property
    def last_referral_for_complex_case_management(self) -> Optional[Dict]:
        interviews = cast(
            List[Dict],
            self.patient.interviews.find(QuestionnaireHealthCHECReferrals).within(
                self.interview_lookback_timeframe()))

        if not interviews:
            return None

        # Go through them in order with the most recent one first and working
        # backwards
        # return the first one with a response representing a physical
        # activity intervention
        for interview in sorted(
                interviews, key=lambda i: arrow.get(i['noteTimestamp']), reverse=True):
            for response in interview.get('responses', []):
                if response.get('code') == '698943000':
                    return interview

        # nothing found
        return None

    def last_referral_for_complex_case_management_date(self) -> Optional[arrow.Arrow]:
        if self.last_referral_for_complex_case_management:
            return arrow.get(self.last_referral_for_complex_case_management['noteTimestamp'])
        return None

    def referred_for_complex_case_management_on_or_after(
            self, reference_date: Optional[arrow.Arrow]) -> bool:
        # It can't have been referred after a date that doesn't exist!
        if not reference_date:
            return False

        # If it hasn't been referred, it certainly wasn't referred after the
        # reference date.
        if not self.last_referral_for_complex_case_management_date():
            return False

        return self.last_referral_for_complex_case_management_date() >= reference_date

    def latest_case_complexity_indication_date(self) -> Optional[arrow.Arrow]:
        dates = cast(List[arrow.Arrow],
                     [date for date in self.latest_case_complexity_indicators().values() if date])
        if dates:
            return max(dates)
        return None

    def latest_case_complexity_indicators(self) -> Dict:
        questions_and_responses_that_indicate_case_complexity: Dict[str, str] = {
            '123978lijsdf293': '123978lijsdf295',
            '123978lijsdf344': '123978lijsdf345',
            '123978lijsdf324': '123978lijsdf326',
            '123978lijsdf350': '123978lijsdf351',
        }

        dates_of_indication: Dict[str, Optional[arrow.Arrow]] = {
            '123978lijsdf293': None,
            '123978lijsdf344': None,
            '123978lijsdf324': None,
            '123978lijsdf350': None,
        }

        # Go through all pvq interviews within the past 30 days in order from
        # the earliest.
        for interview in sorted(self.recent_pvqs, key=lambda i: arrow.get(i['noteTimestamp'])):
            # Check the currently observed interview for each of the trigger
            # questions.
            for question_coding, response_coding in questions_and_responses_that_indicate_case_complexity.items(  # noqa: E501
            ):  # noqa: E501
                question_responses = interview.get('groupedResponses', {}).get(question_coding, [])
                # Check if the question was responded to.
                if question_responses:
                    # Since it was responded to, we consider this a more
                    # updated answer to the question.
                    # If the question's response is one that indicates case
                    # complexity, we'll put this interview's date as the most
                    # recent indication of case complexity. If there are
                    # responses after this, it will get overwritten with the
                    # more recent date.
                    if response_coding in question_responses:
                        dates_of_indication[question_coding] = arrow.get(
                            interview['noteTimestamp'])
                    # If the question's response is not one that indicates
                    # case complexity, we set this question's slot to None,
                    # even if it was previously filled. We are only
                    # considering the most recent response for each question.
                    # If a question is not responded to, the previous response
                    # will remain considered.
                    else:
                        dates_of_indication[question_coding] = None
        return dates_of_indication

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
        A patient should be in the numerator if they either:
        1) Have been determined to not need anything addressed (regarding the
           CustomerScanComplexCaseManagementReferral quality measure)
        OR
        2) Have been addressed (regarding the CustomerScanComplexCaseManagementReferral
           quality measure)
        """

        case_complexity_indicated = False
        referred_for_complex_case_management = False

        if self.latest_case_complexity_indication_date():
            case_complexity_indicated = True

        no_case_complexity_indicated = not case_complexity_indicated

        referred_for_complex_case_management = self.referred_for_complex_case_management_on_or_after(  # noqa: E501
            self.latest_case_complexity_indication_date())

        return no_case_complexity_indicated or (case_complexity_indicated and
                                                referred_for_complex_case_management)

    def craft_satisfied_result(self) -> ProtocolResult:
        """
        Creates and returns a ProtocolResult instance that indicates a satisfied result.
        The narrative added either indicates that the patient was referred to complex case
        management or that the patient did not indicate case complexity within a timeframe.
        """
        result = ProtocolResult()

        result.due_in = -1
        result.status = STATUS_SATISFIED

        referred_for_complex_case_management = self.referred_for_complex_case_management_on_or_after(  # noqa: E501
            self.latest_case_complexity_indication_date())

        if referred_for_complex_case_management:
            result.add_narrative(
                f'{self.patient.first_name} was referred for complex case '
                f'management {self.display_date(self.last_referral_for_complex_case_management_date())}.'  # noqa: E501
            )
        else:
            result.add_narrative(
                f'{self.patient.first_name} has not indicated case complexity in the past 30 days.'
            )

        return result

    def craft_unsatisfied_result(self) -> ProtocolResult:
        """
        Creates and returns a ProtocolResult instance that indicates an unsatisfied result.
        Adds an interview recommendation to the protocol result as well as a narrative based on
        the patient's answers.
        """
        result = ProtocolResult()

        result.due_in = -1
        result.status = STATUS_DUE

        narrative_description_from_question_coding = {
            '123978lijsdf293': 'reported feeling unsafe',
            '123978lijsdf344': 'reported medication issues',
            '123978lijsdf324': 'reported not having emergency help',
            '123978lijsdf350': 'reported food insecurity',
        }

        for question_coding, response_date in self.latest_case_complexity_indicators().items():
            if response_date:
                narrative_description = narrative_description_from_question_coding.get(
                    question_coding, 'indicated a case complexity')
                result.add_narrative(f'{self.patient.first_name} {narrative_description} '
                                     f'{self.display_date(response_date)}.')

        result.add_recommendation(
            InterviewRecommendation(
                key='CUSTOMER_SCAN_RECOMMEND_COMPLEX_CASE_MANAGEMENT_REFERRAL',
                rank=1,
                button='Refer',
                patient=self.patient,
                questionnaires=[QuestionnaireHealthCHECReferrals],
                title='Refer for Complex Case Management'))

        return result
