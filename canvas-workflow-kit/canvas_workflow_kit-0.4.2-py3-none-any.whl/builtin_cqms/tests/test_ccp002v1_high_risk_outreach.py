from unittest.mock import PropertyMock, patch

import arrow

from canvas_workflow_kit import settings

from canvas_workflow_kit.builtin_cqms.ccp002v1_high_risk_outreach import MINIMUM_AGE, Ccp002v1
from canvas_workflow_kit.patient_recordset import ConditionRecordSet, InterviewRecordSet
from canvas_workflow_kit.tests.base import SDKBaseTest
from canvas_workflow_kit.timeframe import Timeframe


class TestCcp002v1(SDKBaseTest):

    def setUp(self):
        self.mocks_path = f'{settings.BASE_DIR}/builtin_cqms/tests/mock_data'

    def test_minimal_age(self):
        assert 65 == MINIMUM_AGE

    def test_enabled(self):
        self.assertTrue(Ccp002v1.enabled())

    def test_description(self):
        expected = 'All patients with 65+ with chronic conditions to be reached.'
        self.assertEqual(expected, Ccp002v1._meta.description)

    def test_information(self):
        expected = (
            'https://canvas-medical.zendesk.com/hc/en-us/articles/360059084173-COVID-19-Risk-Assessment-Follow-Up-Protocol')
        self.assertEqual(expected, Ccp002v1._meta.information)

    def test_change_types(self):
        result = Ccp002v1._meta.compute_on_change_types
        expected = ['condition', 'interview', 'patient']
        self.assertEqual(expected, result)

    def test_version(self):
        self.assertTrue(hasattr(Ccp002v1._meta, 'version'))

    def test_date_of_first_questionnaire(self):
        start = arrow.get('2019-03-24 13:24:56')
        end = arrow.get('2020-03-24 13:24:56')
        timeframe = Timeframe(start=start, end=end)
        patient = self.load_patient('patient')

        # no interview
        tested = Ccp002v1(patient=patient, timeframe=timeframe)
        result = tested.date_of_first_questionnaire
        self.assertEqual('', result)

        # interview symptomatic surveillance
        patient.interviews = InterviewRecordSet(
            [self.helper_questionnaire('2020-03-14 13:24:55+00:00', 'CANVAS0001')])
        tested = Ccp002v1(patient=patient, timeframe=timeframe)
        result = tested.date_of_first_questionnaire
        self.assertEqual('2020-03-14 13:24:55+00:00', result)

        # interview high risk outreach
        patient.interviews = InterviewRecordSet(
            [self.helper_questionnaire('2020-03-14 13:24:55+00:00', 'CANVAS0006')])
        tested = Ccp002v1(patient=patient, timeframe=timeframe)
        result = tested.date_of_first_questionnaire
        self.assertEqual('2020-03-14 13:24:55+00:00', result)

        # interviews -> the oldest
        patient.interviews = InterviewRecordSet([
            self.helper_questionnaire('2020-03-14 13:24:55+00:00', 'CANVAS0001'),
            self.helper_questionnaire('2020-03-14 13:24:54+00:00', 'CANVAS0006'),
            self.helper_questionnaire('2020-03-14 13:24:56+00:00', 'CANVAS0001'),
        ])
        tested = Ccp002v1(patient=patient, timeframe=timeframe)
        result = tested.date_of_first_questionnaire
        self.assertEqual('2020-03-14 13:24:54+00:00', result)

    def test_high_risk_conditions(self):
        start = arrow.get('2019-03-24 13:24:56')
        end = arrow.get('2020-03-24 13:24:56')
        timeframe = Timeframe(start=start, end=end)
        patient = self.load_patient('patient')

        # no condition -> False
        tested = Ccp002v1(patient=patient, timeframe=timeframe)
        result = tested.high_risk_conditions
        self.assertEqual([], result)

        # not high risk condition -> False
        patient.conditions = ConditionRecordSet([self.helper_condition('active', '0QPD0JZ')])
        tested = Ccp002v1(patient=patient, timeframe=timeframe)
        result = tested.high_risk_conditions
        self.assertEqual([], result)

        # high risk condition --> active > True, resolved > False
        tests = [
            'K7150',
            'J441',
            'E119',
            'C8122',
            'I63531',
            'N172',
            'Z6841',
            'J4532',
        ]
        for code in tests:
            patient.conditions = ConditionRecordSet([self.helper_condition('active', code)])
            tested = Ccp002v1(patient=patient, timeframe=timeframe)
            result = tested.high_risk_conditions
            self.assertEqual([{
                'clinicalStatus': 'active',
                'coding': [{
                    'code': code,
                    'system': 'ICD-10'
                }],
                'periods': [{
                    'from': '2018-08-20',
                    'to': None
                }],
            }], result)

            patient.conditions = ConditionRecordSet([self.helper_condition('resolved', code)])
            tested = Ccp002v1(patient=patient, timeframe=timeframe)
            result = tested.high_risk_conditions
            self.assertEqual([], result)

        # several high risk conditions --> list all
        patient.conditions = ConditionRecordSet([
            self.helper_condition('active', 'E119'),
            self.helper_condition('active', 'Z6841'),
        ])
        tested = Ccp002v1(patient=patient, timeframe=timeframe)
        result = tested.high_risk_conditions
        self.assertEqual([
            {
                'clinicalStatus': 'active',
                'coding': [{
                    'code': 'E119',
                    'system': 'ICD-10'
                }],
                'periods': [{
                    'from': '2018-08-20',
                    'to': None
                }],
            },
            {
                'clinicalStatus': 'active',
                'coding': [{
                    'code': 'Z6841',
                    'system': 'ICD-10'
                }],
                'periods': [{
                    'from': '2018-08-20',
                    'to': None
                }],
            },
        ], result)

    def test_in_initial_population(self):
        with patch('canvas_workflow_kit.builtin_cqms.ccp002v1_high_risk_outreach.arrow.now') as now:
            now.return_value = arrow.get('2020-03-22 13:24:56')

            start = arrow.get('2019-03-22 13:24:56')
            end = arrow.get('2020-03-22 13:24:56')
            timeframe = Timeframe(start=start, end=end)
            patient = self.load_patient('patient')

            # 65+ + no high risk condition --> True
            patient.patient['birthDate'] = '1955-03-20'
            patient.conditions = ConditionRecordSet([self.helper_condition('active', 'H3533')])
            tested = Ccp002v1(patient=patient, timeframe=timeframe)
            result = tested.in_initial_population()
            self.assertTrue(result)

            # <65 + high risk condition --> True
            patient.patient['birthDate'] = '1955-03-20'
            patient.conditions = ConditionRecordSet([self.helper_condition('active', 'C8122')])
            tested = Ccp002v1(patient=patient, timeframe=timeframe)
            result = tested.in_initial_population()
            self.assertTrue(result)

            # <65 +  no high risk condition -> False
            patient.patient['birthDate'] = '1955-03-24'
            patient.conditions = ConditionRecordSet([self.helper_condition('active', 'H3533')])
            tested = Ccp002v1(patient=patient, timeframe=timeframe)
            result = tested.in_initial_population()
            self.assertFalse(result)

    def test_in_denominator(self):
        with patch('canvas_workflow_kit.builtin_cqms.ccp002v1_high_risk_outreach.arrow.now') as now:
            now.return_value = arrow.get('2020-03-22 13:24:56')

            start = arrow.get('2019-03-22 13:24:56')
            end = arrow.get('2020-03-22 13:24:56')
            timeframe = Timeframe(start=start, end=end)
            patient = self.load_patient('patient')

            # 65+ + no high risk condition --> True
            patient.patient['birthDate'] = '1955-03-21'
            patient.conditions = ConditionRecordSet([self.helper_condition('active', 'H3533')])
            tested = Ccp002v1(patient=patient, timeframe=timeframe)
            result = tested.in_denominator()
            self.assertTrue(result)

            # <65 + high risk condition --> True
            patient.patient['birthDate'] = '1955-03-24'
            patient.conditions = ConditionRecordSet([self.helper_condition('active', 'C8122')])
            tested = Ccp002v1(patient=patient, timeframe=timeframe)
            result = tested.in_denominator()
            self.assertTrue(result)

            # <65 + no high risk condition -> False
            patient.conditions = ConditionRecordSet([self.helper_condition('active', 'H3533')])
            tested = Ccp002v1(patient=patient, timeframe=timeframe)
            result = tested.in_denominator()
            self.assertFalse(result)

    def test_in_numerator(self):
        start = arrow.get('2019-03-24 13:24:56')
        end = arrow.get('2020-03-24 13:24:56')
        timeframe = Timeframe(start=start, end=end)
        patient = self.load_patient('patient')

        # no interview
        tested = Ccp002v1(patient=patient, timeframe=timeframe)
        result = tested.in_numerator()
        self.assertFalse(result)

        # interview not Covid-19 -> False
        patient.interviews = InterviewRecordSet(
            [self.helper_questionnaire('2020-03-14 13:24:55+00:00', 'CANVAS0002')])
        tested = Ccp002v1(patient=patient, timeframe=timeframe)
        result = tested.in_numerator()
        self.assertFalse(result)

        # interview symptomatic surveillance -> True
        patient.interviews = InterviewRecordSet(
            [self.helper_questionnaire('2020-03-14 13:24:55+00:00', 'CANVAS0001')])
        tested = Ccp002v1(patient=patient, timeframe=timeframe)
        result = tested.in_numerator()
        self.assertTrue(result)

        # interview high risk outreach -> True
        patient.interviews = InterviewRecordSet(
            [self.helper_questionnaire('2020-03-14 13:24:55+00:00', 'CANVAS0006')])
        tested = Ccp002v1(patient=patient, timeframe=timeframe)
        result = tested.in_numerator()
        self.assertTrue(result)

        # multiple including covid-19 -> True
        patient.interviews = InterviewRecordSet([
            self.helper_questionnaire('2020-03-14 13:24:55+00:00', 'CANVAS0001'),
            self.helper_questionnaire('2020-03-14 13:24:54+00:00', 'CANVAS0006'),
            self.helper_questionnaire('2020-03-14 13:24:56+00:00', 'CANVAS0002'),
        ])
        tested = Ccp002v1(patient=patient, timeframe=timeframe)
        result = tested.in_numerator()
        self.assertTrue(result)

    @patch(
        'canvas_workflow_kit.builtin_cqms.ccp002v1_high_risk_outreach.Ccp002v1.high_risk_conditions',
        new_callable=PropertyMock)
    @patch(
        'canvas_workflow_kit.builtin_cqms.ccp002v1_high_risk_outreach.Ccp002v1.date_of_first_questionnaire',
        new_callable=PropertyMock)
    @patch('canvas_workflow_kit.builtin_cqms.ccp002v1_high_risk_outreach.Ccp002v1.in_numerator')
    @patch('canvas_workflow_kit.builtin_cqms.ccp002v1_high_risk_outreach.Ccp002v1.in_denominator')
    @patch('canvas_workflow_kit.builtin_cqms.ccp002v1_high_risk_outreach.arrow.now')
    def test_compute_results(self, now, in_denominator, in_numerator, date_of_first_questionnaire,
                             high_risk_conditions):
        now.return_value = arrow.get('2020-03-22 13:24:56')

        start = arrow.get('2019-03-24 13:24:56')
        end = arrow.get('2020-03-24 13:24:56')
        timeframe = Timeframe(start=start, end=end)
        patient = self.load_patient('patient')

        # not in_denominator -> not_applicable
        high_risk_conditions.return_value = []
        in_denominator.return_value = False
        in_numerator.return_value = True
        date_of_first_questionnaire.return_value = '2020-03-14 13:24:55+00:00'

        tested = Ccp002v1(patient=patient, timeframe=timeframe)
        result = tested.compute_results()
        self.assertEqual('not_applicable', result.status)
        self.assertIsNone(result.due_in)

        # in_denominator + in_numerator -> satisfied
        high_risk_conditions.return_value = []
        in_denominator.return_value = True
        in_numerator.return_value = True
        date_of_first_questionnaire.return_value = '2020-03-14 13:24:55+00:00'

        tested = Ccp002v1(patient=patient, timeframe=timeframe)
        result = tested.compute_results()
        self.assertEqual('satisfied', result.status)
        self.assertEqual(-1, result.due_in)
        narratives = ['Nicolas took a COVID-19 outreach questionnaire on Sat, Mar 14th 2020.']
        self.assertEqual(narratives, result.narratives)
        self.assertEqual(0, len(result.recommendations))

        # patient is less than 65
        patient.patient['birthDate'] = '1956-03-20'
        # in_denominator + not in_numerator + no display -> due + count of high risk conditions
        high_risk_conditions.return_value = [
            {
                'clinicalStatus': 'active',
                'coding': [{
                    'code': 'E119',
                    'system': 'ICD-10'
                }],
                'periods': [{
                    'from': '2018-08-20',
                    'to': None
                }],
            },
            {
                'clinicalStatus': 'active',
                'coding': [{
                    'code': 'Z6841',
                    'system': 'ICD-10'
                }],
                'periods': [{
                    'from': '2018-08-20',
                    'to': None
                }],
            },
        ]
        in_denominator.return_value = True
        in_numerator.return_value = False
        date_of_first_questionnaire.return_value = '2020-03-14 13:24:55+00:00'

        tested = Ccp002v1(patient=patient, timeframe=timeframe)
        result = tested.compute_results()
        self.assertEqual('due', result.status)
        self.assertEqual(0, result.due_in)
        narratives = [
            'Nicolas should take a COVID-19 outreach questionnaire.',
            'Nicolas has 2 high risk conditions',
        ]
        self.assertEqual(narratives, result.narratives)
        self.assertEqual(1, len(result.recommendations))
        recommendation = result.recommendations[0]
        self.assertEqual('CCP002v1_RECOMMEND_QUESTIONNAIRE', recommendation.key)
        self.assertEqual('Complete COVID-19 outreach questionnaire', recommendation.title)

        # in_denominator + not in_numerator + display -> due + list of high risk conditions
        high_risk_conditions.return_value = [
            {
                'clinicalStatus': 'active',
                'coding': [{
                    'code': 'E119',
                    'system': 'ICD-10',
                    'display': 'diabetes'
                }],
                'periods': [{
                    'from': '2018-08-20',
                    'to': None
                }],
            },
            {
                'clinicalStatus': 'active',
                'coding': [{
                    'code': 'Z6841',
                    'system': 'ICD-10',
                    'display': 'body mass'
                }],
                'periods': [{
                    'from': '2018-08-20',
                    'to': None
                }],
            },
        ]
        in_denominator.return_value = True
        in_numerator.return_value = False
        date_of_first_questionnaire.return_value = '2020-03-14 13:24:55+00:00'

        tested = Ccp002v1(patient=patient, timeframe=timeframe)
        result = tested.compute_results()
        self.assertEqual('due', result.status)
        self.assertEqual(0, result.due_in)
        narratives = [
            'Nicolas should take a COVID-19 outreach questionnaire.',
            'Nicolas has high risk conditions:',
            'diabetes',
            'body mass',
        ]
        self.assertEqual(narratives, result.narratives)
        self.assertEqual(1, len(result.recommendations))
        recommendation = result.recommendations[0]
        self.assertEqual('CCP002v1_RECOMMEND_QUESTIONNAIRE', recommendation.key)
        self.assertEqual('Complete COVID-19 outreach questionnaire', recommendation.title)

        # patient is more than 65
        patient.patient['birthDate'] = '1954-03-20'
        # in_denominator + not in_numerator + display -> due + list of high risk conditions
        high_risk_conditions.return_value = [
            {
                'clinicalStatus': 'active',
                'coding': [{
                    'code': 'E119',
                    'system': 'ICD-10',
                    'display': 'diabetes'
                }],
                'periods': [{
                    'from': '2018-08-20',
                    'to': None
                }],
            },
            {
                'clinicalStatus': 'active',
                'coding': [{
                    'code': 'Z6841',
                    'system': 'ICD-10',
                    'display': 'body mass'
                }],
                'periods': [{
                    'from': '2018-08-20',
                    'to': None
                }],
            },
        ]
        in_denominator.return_value = True
        in_numerator.return_value = False
        date_of_first_questionnaire.return_value = '2020-03-14 13:24:55+00:00'

        tested = Ccp002v1(patient=patient, timeframe=timeframe)
        result = tested.compute_results()
        self.assertEqual('due', result.status)
        self.assertEqual(0, result.due_in)
        narratives = [
            'Nicolas should take a COVID-19 outreach questionnaire.',
            'Nicolas is 65+',
            'Nicolas has high risk conditions:',
            'diabetes',
            'body mass',
        ]
        self.assertEqual(narratives, result.narratives)
        self.assertEqual(1, len(result.recommendations))
        recommendation = result.recommendations[0]
        self.assertEqual('CCP002v1_RECOMMEND_QUESTIONNAIRE', recommendation.key)
        self.assertEqual('Complete COVID-19 outreach questionnaire', recommendation.title)

        # in_denominator + not in_numerator + no high risk condition -> due + age
        high_risk_conditions.return_value = []
        in_denominator.return_value = True
        in_numerator.return_value = False
        date_of_first_questionnaire.return_value = '2020-03-14 13:24:55+00:00'

        tested = Ccp002v1(patient=patient, timeframe=timeframe)
        result = tested.compute_results()
        self.assertEqual('due', result.status)
        self.assertEqual(0, result.due_in)
        narratives = [
            'Nicolas should take a COVID-19 outreach questionnaire.',
            'Nicolas is 65+',
        ]
        self.assertEqual(narratives, result.narratives)
        self.assertEqual(1, len(result.recommendations))
        recommendation = result.recommendations[0]
        self.assertEqual('CCP002v1_RECOMMEND_QUESTIONNAIRE', recommendation.key)
        self.assertEqual('Complete COVID-19 outreach questionnaire', recommendation.title)

    def helper_condition(self, status: str, icd10: str):
        return {
            'clinicalStatus': status,
            'coding': [{
                'code': icd10,
                'system': 'ICD-10'
            }],
            'periods': [{
                'from': '2018-08-20',
                'to': None if status == 'active' else '2020-03-21'
            }],
        }

    def helper_questionnaire(self, date: str, canvas: str):
        return {
            'noteTimestamp': date,
            'name': 'COVID Questionnaire',
            'results': [],
            'questionnaires': [{
                'code': canvas,
                'codeSystem': 'CANVAS'
            }],
        }
