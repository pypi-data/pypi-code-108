from typing import Dict, List
from unittest.mock import PropertyMock, patch

import arrow

from canvas_workflow_kit import settings

from canvas_workflow_kit.builtin_cqms.ccp001v1_symptomatic_surveillance import Ccp001v1
from canvas_workflow_kit.patient_recordset import InterviewRecordSet
from canvas_workflow_kit.tests.base import SDKBaseTest
from canvas_workflow_kit.timeframe import Timeframe


class TestCcp001v1(SDKBaseTest):

    def setUp(self):
        self.mocks_path = f'{settings.BASE_DIR}/builtin_cqms/tests/mock_data'

    def test_enabled(self):
        self.assertTrue(Ccp001v1.enabled())

    def test_description(self):
        # flake8: noqa
        expected = 'All patients with COVID Questionnaire completed Date < 7 days ago and >  5 days ago.'
        self.assertEqual(expected, Ccp001v1._meta.description)

    def test_information(self):
        # flake8: noqa
        expected = 'https://canvas-medical.zendesk.com/hc/en-us/articles/360059084173-COVID-19-Risk-Assessment-Follow-Up-Protocol'
        self.assertEqual(expected, Ccp001v1._meta.information)

    def test_change_types(self):
        result = Ccp001v1._meta.compute_on_change_types
        expected = ['interview']
        self.assertEqual(expected, result)

    def test___init__(self):
        start = arrow.get('2019-03-20 13:24:56')
        end = arrow.get('2020-03-20 13:24:56')
        timeframe = Timeframe(start=start, end=end)
        patient = self.load_patient('patient')
        tested = Ccp001v1(patient=patient, timeframe=timeframe)

        self.assertEqual([], tested.rationales_for_inclusion_in_numerator)

    def test_anchor_time(self):
        patient = self.load_patient('patient')

        tests = [
            ('00', '2020-03-20T09:00:00+00:00'),
            ('01', '2020-03-20T09:00:00+00:00'),
            ('02', '2020-03-20T09:00:00+00:00'),
            ('03', '2020-03-20T09:00:00+00:00'),
            ('04', '2020-03-20T09:00:00+00:00'),
            ('05', '2020-03-20T09:00:00+00:00'),
            ('06', '2020-03-20T09:00:00+00:00'),
            ('07', '2020-03-20T09:00:00+00:00'),
            ('08', '2020-03-20T09:00:00+00:00'),
            ('09', '2020-03-20T09:00:00+00:00'),
            ('10', '2020-03-20T09:00:00+00:00'),
            ('11', '2020-03-20T09:00:00+00:00'),
            ('12', '2020-03-20T09:00:00+00:00'),
            ('13', '2020-03-20T09:00:00+00:00'),
            ('14', '2020-03-20T09:00:00+00:00'),
            ('15', '2020-03-20T09:00:00+00:00'),
            ('16', '2020-03-20T09:00:00+00:00'),
            ('17', '2020-03-20T09:00:00+00:00'),
            ('18', '2020-03-20T09:00:00+00:00'),
            ('19', '2020-03-20T09:00:00+00:00'),
            ('20', '2020-03-20T09:00:00+00:00'),
            ('21', '2020-03-21T09:00:00+00:00'),
            ('22', '2020-03-21T09:00:00+00:00'),
            ('23', '2020-03-21T09:00:00+00:00'),
        ]
        start = arrow.get('2019-03-20 13:24:56')
        for hour, expected in tests:
            end = arrow.get(f'2020-03-20 {hour}:24:56')
            timeframe = Timeframe(start=start, end=end)
            tested = Ccp001v1(patient=patient, timeframe=timeframe)
            result = tested.anchor_time
            assert expected == str(result), f'{hour} -> {result}'

    @patch(
        'canvas_workflow_kit.builtin_cqms.ccp001v1_symptomatic_surveillance.Ccp001v1.anchor_time',
        new_callable=PropertyMock)
    def test_interview(self, anchor_time):
        anchor_time.return_value = arrow.get('2020-03-20T09:00:00+00:00')
        start = arrow.get('2019-03-20 13:24:56')
        end = arrow.get('2010-03-20 13:24:56')
        timeframe = Timeframe(start=start, end=end)
        patient = self.load_patient('patient')

        # no interview -> empty
        tested = Ccp001v1(patient=patient, timeframe=timeframe)
        result = tested.interview
        self.assertEqual(0, len(result.keys()))

        # interview just after the end of the 6th day -> empty
        patient.interviews = InterviewRecordSet(
            [self.helper_questionnaire(123, '2020-03-14T08:59:59+00:00', {})])
        tested = Ccp001v1(patient=patient, timeframe=timeframe)
        result = tested.interview
        self.assertEqual(0, len(result.keys()))

        # interview just before the end of the 6th day -> the interview
        patient.interviews = InterviewRecordSet(
            [self.helper_questionnaire(124, '2020-03-14T09:00:00+00:00', {})])
        tested = Ccp001v1(patient=patient, timeframe=timeframe)
        result = tested.interview
        self.assertEqual(7, len(result.keys()))
        self.assertEqual(124, result['id'])

        # interview within the 6th day -> the interview
        for day in range(14, 20):
            patient.interviews = InterviewRecordSet(
                [self.helper_questionnaire(124, f'2020-03-{day}T17:45:41+00:00', {})])
            tested = Ccp001v1(patient=patient, timeframe=timeframe)
            result = tested.interview
            self.assertEqual(7, len(result.keys()))
            self.assertEqual(124, result['id'])

        # several interviews -> the interview that is the oldest within the 6 days
        patient.interviews = InterviewRecordSet([
            self.helper_questionnaire(124, '2020-03-14T08:59:59+00:00', {}),
            self.helper_questionnaire(144, '2020-03-14T09:00:10+00:00', {}),
            self.helper_questionnaire(134, '2020-03-14T09:00:09+00:00', {}),
            self.helper_questionnaire(154, '2020-03-14T09:00:11+00:00', {}),
        ])
        tested = Ccp001v1(patient=patient, timeframe=timeframe)
        result = tested.interview
        self.assertEqual(7, len(result.keys()))
        self.assertEqual(134, result['id'])

    @patch(
        'canvas_workflow_kit.builtin_cqms.ccp001v1_symptomatic_surveillance.Ccp001v1.anchor_time',
        new_callable=PropertyMock)
    def test_in_initial_population(self, anchor_time):
        anchor_time.return_value = arrow.get('2020-03-20T09:00:00+00:00')
        start = arrow.get('2019-03-20 13:24:56')
        end = arrow.get('2010-03-20 13:24:56')
        timeframe = Timeframe(start=start, end=end)
        patient = self.load_patient('patient')

        # no interview -> no
        tested = Ccp001v1(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.in_initial_population())

        # interview older than 6 days -> no
        patient.interviews = InterviewRecordSet(
            [self.helper_questionnaire(123, '2020-03-14T08:59:59+00:00', {})])
        tested = Ccp001v1(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.in_initial_population())

        # interview newer than 6 days -> yes
        for day in range(14, 20):
            patient.interviews = InterviewRecordSet(
                [self.helper_questionnaire(124, f'2020-03-{day}T17:45:41+00:00', {})])
            tested = Ccp001v1(patient=patient, timeframe=timeframe)
            self.assertTrue(tested.in_initial_population())

        # several interviews with some within 6 days -> yes
        patient.interviews = InterviewRecordSet([
            self.helper_questionnaire(124, '2020-03-14T08:59:59+00:00', {}),
            self.helper_questionnaire(144, '2020-03-14T09:00:10+00:00', {}),
            self.helper_questionnaire(134, '2020-03-14T09:00:09+00:00', {}),
            self.helper_questionnaire(154, '2020-03-14T09:00:11+00:00', {}),
        ])
        tested = Ccp001v1(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.in_initial_population())

    @patch(
        'canvas_workflow_kit.builtin_cqms.ccp001v1_symptomatic_surveillance.Ccp001v1.anchor_time',
        new_callable=PropertyMock)
    def test_in_denominator(self, anchor_time):
        anchor_time.return_value = arrow.get('2020-03-20T09:00:00+00:00')
        start = arrow.get('2019-03-20 13:24:56')
        end = arrow.get('2010-03-20 13:24:56')
        timeframe = Timeframe(start=start, end=end)
        patient = self.load_patient('patient')

        # no interview -> no
        tested = Ccp001v1(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.in_denominator())

        # interviews
        tests = [
            ('2020-03-14T08:59:59+00:00', False),  # interview older than 6 days -> no
            ('2020-03-14T09:00:00+00:00', True),  # interview within 6 days -> yes
            ('2020-03-14T22:33:44+00:00', True),  # interview within 6 days -> yes
            ('2020-03-15T08:59:59+00:00', True),  # interview within 6 days -> yes
            ('2020-03-15T09:00:00+00:00', False),  # interview newer than 6 days -> no
        ]
        for date, expected in tests:
            patient.interviews = InterviewRecordSet([self.helper_questionnaire(123, date, {})])
            tested = Ccp001v1(patient=patient, timeframe=timeframe)
            if expected:
                self.assertTrue(tested.in_denominator())
            else:
                self.assertFalse(tested.in_denominator())

    def test_group_question_responses(self):
        tested = Ccp001v1.group_question_responses

        # empty --> empty
        interview = {
            'questions': [],
            'responses': [],
        }
        result = tested(interview)
        self.assertEqual({}, result)

        #
        interview = {
            'questions': [
                {
                    'questionResponseId': 10,
                    'code': 'question-10'
                },
                {
                    'questionResponseId': 11,
                    'code': 'question-11'
                },
                {
                    'questionResponseId': 12,
                    'code': 'question-12'
                },
            ],
            'responses': [
                {
                    'questionResponseId': 10,
                    'code': 'response-10'
                },
                {
                    'questionResponseId': 11,
                    'code': 'response-11a'
                },
                {
                    'questionResponseId': 11,
                    'code': 'response-11b'
                },
                {
                    'questionResponseId': 11,
                    'code': 'response-11c'
                },
                {
                    'questionResponseId': 12,
                    'code': 'response-12'
                },
            ],
        }
        result = tested(interview)
        expected = {
            'question-10': ['response-10'],
            'question-11': ['response-11a', 'response-11b', 'response-11c'],
            'question-12': ['response-12'],
        }
        self.assertEqual(expected, result)

    @patch(
        'canvas_workflow_kit.builtin_cqms.ccp001v1_symptomatic_surveillance.Ccp001v1.interview',
        new_callable=PropertyMock)
    @patch(
        'canvas_workflow_kit.builtin_cqms.ccp001v1_symptomatic_surveillance.Ccp001v1.anchor_time',
        new_callable=PropertyMock)
    def test_in_numerator(self, anchor_time, interview):
        anchor_time.return_value = arrow.get('2020-03-20T09:00:00+00:00')
        start = arrow.get('2019-03-20 13:24:56')
        end = arrow.get('2010-03-20 13:24:56')
        timeframe = Timeframe(start=start, end=end)
        patient = self.load_patient('patient')

        # all responses are negative --> false
        tested = Ccp001v1(patient=patient, timeframe=timeframe)
        interview.return_value = self.helper_questionnaire(123, '2020-03-16 20:24:56+00:00', {})
        self.assertFalse(tested.in_numerator())
        self.assertEqual([], tested.rationales_for_inclusion_in_numerator)

        # Q1 has one answer -> true + value in narrative
        tested = Ccp001v1(patient=patient, timeframe=timeframe)
        interview.return_value = self.helper_questionnaire(123, '2020-03-16 20:24:56+00:00',
                                                           {35: '386661006'})
        self.assertTrue(tested.in_numerator())
        expected = ['Symptoms exhibited: fever']
        self.assertEqual(expected, tested.rationales_for_inclusion_in_numerator)

        # Q1 has two answer -> true + all values in narrative
        tested = Ccp001v1(patient=patient, timeframe=timeframe)
        interview.return_value = self.helper_questionnaire(123, '2020-03-16 20:24:56+00:00', {
            35: '386661006',
            39: '49727002'
        })
        self.assertTrue(tested.in_numerator())
        expected = ['Symptoms exhibited: fever, cough']
        self.assertEqual(expected, tested.rationales_for_inclusion_in_numerator)

        # Q4 yes -> true + value in narrative
        tested = Ccp001v1(patient=patient, timeframe=timeframe)
        interview.return_value = self.helper_questionnaire(123, '2020-03-16 20:24:56+00:00',
                                                           {38: '183616001'})
        self.assertTrue(tested.in_numerator())
        expected = ['Follow-up requested by care team']
        self.assertEqual(expected, tested.rationales_for_inclusion_in_numerator)

        # Q2 yes + patient 65+ -> yes
        tested = Ccp001v1(patient=patient, timeframe=timeframe)
        interview.return_value = self.helper_questionnaire(123, '2020-03-16 20:24:56+00:00',
                                                           {36: '276030007'})
        self.assertTrue(tested.in_numerator())
        expected = ['Age 65+ with recent travel']
        self.assertEqual(expected, tested.rationales_for_inclusion_in_numerator)

        # Q2 yes + patient < 65> -> no
        patient.patient['birthDate'] = '1955-03-22'
        tested = Ccp001v1(patient=patient, timeframe=timeframe)
        interview.return_value = self.helper_questionnaire(123, '2020-03-16 20:24:56+00:00',
                                                           {36: '276030007'})
        self.assertFalse(tested.in_numerator())
        self.assertEqual([], tested.rationales_for_inclusion_in_numerator)
        patient.patient['birthDate'] = '1954-03-22'

        # Q3 yes + patient 65+ -> yes
        tested = Ccp001v1(patient=patient, timeframe=timeframe)
        interview.return_value = self.helper_questionnaire(123, '2020-03-16 20:24:56+00:00',
                                                           {37: '150781000119103'})
        self.assertTrue(tested.in_numerator())
        expected = ['Age 65+ with recent exposure']
        self.assertEqual(expected, tested.rationales_for_inclusion_in_numerator)

        # Q3 yes + patient < 65> -> no
        patient.patient['birthDate'] = '1955-03-22'
        tested = Ccp001v1(patient=patient, timeframe=timeframe)
        interview.return_value = self.helper_questionnaire(123, '2020-03-16 20:24:56+00:00',
                                                           {37: '150781000119103'})
        self.assertFalse(tested.in_numerator())
        self.assertEqual([], tested.rationales_for_inclusion_in_numerator)
        patient.patient['birthDate'] = '1954-03-22'

        # Q1, Q2, Q3, Q4
        tested = Ccp001v1(patient=patient, timeframe=timeframe)
        responses = {
            35: '386661006',
            36: '276030007',
            37: '150781000119103',
            38: '183616001',
            39: '49727002',
        }
        interview.return_value = self.helper_questionnaire(123, '2020-03-16 20:24:56+00:00',
                                                           responses)
        self.assertTrue(tested.in_numerator())
        expected = [
            'Symptoms exhibited: fever, cough',
            'Follow-up requested by care team',
            'Recent travel',
            'Recent exposure',
        ]
        self.assertEqual(expected, tested.rationales_for_inclusion_in_numerator)

    @patch('canvas_workflow_kit.builtin_cqms.ccp001v1_symptomatic_surveillance.arrow.utcnow')
    @patch(
        'canvas_workflow_kit.builtin_cqms.ccp001v1_symptomatic_surveillance.Ccp001v1.anchor_time',
        new_callable=PropertyMock)
    def test_compute_results(self, anchor_time, utcnow):
        utcnow.return_value = arrow.get('2020-03-20 13:24:56')
        anchor_time.return_value = arrow.get('2020-03-20T09:00:00+00:00')

        start = arrow.get('2019-03-20 13:24:56')
        end = arrow.get('2010-03-20 13:24:56')
        timeframe = Timeframe(start=start, end=end)
        patient = self.load_patient('patient')

        # no interview -> n/a with no due_in
        tested = Ccp001v1(patient=patient, timeframe=timeframe)
        result = tested.compute_results()
        self.assertEqual('not_applicable', result.status)
        self.assertEqual([], result.narratives)
        self.assertEqual([], result.recommendations)
        self.assertIsNone(result.due_in)
        self.assertIsNone(result.next_review)

        # too old interview -> n/a with no due_in
        patient.interviews = InterviewRecordSet(
            [self.helper_questionnaire(123, '2020-03-14T08:59:59+00:00', {})])
        tested = Ccp001v1(patient=patient, timeframe=timeframe)
        result = tested.compute_results()
        self.assertEqual('not_applicable', result.status)
        self.assertEqual([], result.narratives)
        self.assertEqual([], result.recommendations)
        self.assertIsNone(result.due_in)
        self.assertIsNone(result.next_review)

        # too new interview -> n/a with due_in=1
        patient.interviews = InterviewRecordSet(
            [self.helper_questionnaire(123, '2020-03-16T09:01:02+00:00', {})])
        tested = Ccp001v1(patient=patient, timeframe=timeframe)
        result = tested.compute_results()
        self.assertEqual('not_applicable', result.status)
        self.assertEqual([], result.narratives)
        self.assertEqual([], result.recommendations)
        self.assertEqual(1, result.due_in)
        next_review = arrow.get('2020-03-21T10:00:00+00:00')
        self.assertEqual(next_review, result.next_review)

        # too new interview -> n/a with due_in=3
        patient.interviews = InterviewRecordSet(
            [self.helper_questionnaire(123, '2020-03-19T09:01:02+00:00', {})])
        tested = Ccp001v1(patient=patient, timeframe=timeframe)
        result = tested.compute_results()
        self.assertEqual('not_applicable', result.status)
        self.assertEqual([], result.narratives)
        self.assertEqual([], result.recommendations)
        self.assertEqual(4, result.due_in)
        next_review = arrow.get('2020-03-21T10:00:00+00:00')
        self.assertEqual(next_review, result.next_review)

        # the review time is constant regardless of the current time
        # as long as it is in the window
        tests = [
            ('2020-03-19 20:24:56', '2020-03-20T10:00:00+00:00', 5),
            ('2020-03-19 22:24:57', '2020-03-21T10:00:00+00:00', 5),
            ('2020-03-22 22:24:57', '2020-03-24T10:00:00+00:00', 2),
        ]
        for utcnow_time, expected_review, expected_due in tests:
            utcnow.return_value = arrow.get(utcnow_time)
            patient.interviews = InterviewRecordSet(
                [self.helper_questionnaire(123, '2020-03-19T09:01:02+00:00', {})])
            tested = Ccp001v1(patient=patient, timeframe=timeframe)
            result = tested.compute_results()
            self.assertEqual('not_applicable', result.status)
            self.assertEqual([], result.narratives)
            self.assertEqual([], result.recommendations)
            self.assertEqual(expected_due, result.due_in)
            next_review = arrow.get(expected_review)
            self.assertEqual(next_review, result.next_review)

        # interview done 6 days ago without follow up -> satisfied
        utcnow.return_value = arrow.get('2020-03-20 13:24:56')
        patient.interviews = InterviewRecordSet(
            [self.helper_questionnaire(123, '2020-03-14T13:24:58+00:00', {})])
        tested = Ccp001v1(patient=patient, timeframe=timeframe)
        result = tested.compute_results()
        self.assertEqual('satisfied', result.status)
        self.assertEqual(['Nicolas does not need a follow-up arranged'], result.narratives)
        self.assertEqual([], result.recommendations)
        self.assertEqual(-1, result.due_in)
        next_review = arrow.get('2020-03-21T13:24:56+00:00')
        self.assertEqual(next_review, result.next_review)

        # interview done 6 days ago requiring a follow up -> due
        responses = {
            35: '386661006',
            36: '276030007',
            37: '150781000119103',
            38: '183616001',
            39: '49727002',
        }
        patient.interviews = InterviewRecordSet(
            [self.helper_questionnaire(123, '2020-03-14T20:24:56+00:00', responses)])
        tested = Ccp001v1(patient=patient, timeframe=timeframe)
        result = tested.compute_results()
        self.assertEqual('due', result.status)
        narratives = [
            'Nicolas should have a follow-up arranged',
            'Symptoms exhibited: fever, cough',
            'Follow-up requested by care team',
            'Recent travel',
            'Recent exposure',
        ]
        self.assertEqual(narratives, result.narratives)
        self.assertEqual(1, len(result.recommendations))
        recommendation = result.recommendations[0]
        self.assertEqual('CCP001v1_RECOMMEND_FOLLOW_UP', recommendation.key)
        self.assertEqual('Arrange a follow-up', recommendation.title)
        self.assertEqual(-1, result.due_in)
        next_review = arrow.get('2020-03-21 13:24:56+00:00')
        self.assertEqual(next_review, result.next_review)

        # interview done 7 days ago -> not applicable
        patient.interviews = InterviewRecordSet(
            [self.helper_questionnaire(123, '2020-03-13T13:24:58+00:00', {})])
        tested = Ccp001v1(patient=patient, timeframe=timeframe)
        result = tested.compute_results()
        self.assertEqual('not_applicable', result.status)
        self.assertEqual([], result.narratives)
        self.assertEqual([], result.recommendations)
        self.assertIsNone(result.due_in)
        self.assertIsNone(result.next_review)

    def helper_questionnaire(self, interview_id: int, date: str, answers: Dict):
        question_codes = {
            35: 'CANVAS0002',
            36: 'CANVAS0003',
            37: 'CANVAS0004',
            38: 'CANVAS0005',
            39: 'CANVAS0002',
        }
        response_values = {
            '386661006': 'fever',
            '267036007': 'sob',
            '49727002': 'cough',
            '276030007': 'travel abroad',
            '150781000119103': 'exposure to viral disease',
            '183616001': 'Follow up arranged',
            '260385009': 'negative',
        }
        default = {
            35: '',
            36: '260385009',
            37: '260385009',
            38: '260385009',
            39: '',
        }
        default.update(answers)

        questions: Dict = {}
        responses: List = []
        for questionResponseId, codes in default.items():
            for code in [c for c in codes.split(',') if c != '']:
                questions[questionResponseId] = {
                    'questionResponseId': questionResponseId,
                    'code': question_codes[questionResponseId],
                    'codeSystem': 'CANVAS',
                }
                responses.append({
                    'questionResponseId': questionResponseId,
                    'value': response_values[code],
                    'code': code,
                    'codeSystem': 'http://snomed.info/sct'
                })

        return {
            'id': interview_id,
            'noteTimestamp': date,
            'name': 'COVID Questionnaire',
            'results': [],
            'questionnaires': [{
                'code': 'CANVAS0001',
                'codeSystem': 'CANVAS'
            }],
            'questions': list(questions.values()),
            'responses': responses,
        }
