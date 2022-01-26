from unittest.mock import PropertyMock, patch

import arrow

from canvas_workflow_kit import settings

from canvas_workflow_kit.builtin_cqms.ccp003v1_hypertension import Ccp003v1
from canvas_workflow_kit.patient_recordset import ConditionRecordSet
from canvas_workflow_kit.tests.base import SDKBaseTest
from canvas_workflow_kit.timeframe import Timeframe


class TestCcp003v1(SDKBaseTest):

    def setUp(self):
        self.mocks_path = f'{settings.BASE_DIR}/builtin_cqms/tests/mock_data'

    def test_enabled(self):
        self.assertTrue(Ccp003v1.enabled())

    def test_description(self):
        expected = 'All patients with Diagnosis Of Hypertension.'
        self.assertEqual(expected, Ccp003v1._meta.description)

    def test_information(self):
        expected = 'https://canvas-medical.zendesk.com/hc/en-us'
        self.assertEqual(expected, Ccp003v1._meta.information)

    def test_change_types(self):
        result = Ccp003v1._meta.compute_on_change_types
        expected = ['condition']
        self.assertEqual(expected, result)

    def test_version(self):
        self.assertTrue(hasattr(Ccp003v1._meta, 'version'))

    def test_date_of_diagnosis(self):
        start = arrow.get('2019-03-30 13:24:56')
        end = arrow.get('2020-03-30 13:24:56')
        timeframe = Timeframe(start=start, end=end)
        patient = self.load_patient('patient')

        # no condition -> False
        tested = Ccp003v1(patient=patient, timeframe=timeframe)
        result = tested.date_of_diagnosis
        self.assertEqual('', result)

        # not hypertension condition -> False
        patient.conditions = ConditionRecordSet([self.helper_condition('active', '0QPD0JZ')])
        tested = Ccp003v1(patient=patient, timeframe=timeframe)
        result = tested.date_of_diagnosis
        self.assertEqual('', result)

        # hypertension condition --> active -> date
        patient.conditions = ConditionRecordSet([self.helper_condition('2018-08-20', 'H35039')])
        tested = Ccp003v1(patient=patient, timeframe=timeframe)
        result = tested.date_of_diagnosis
        self.assertEqual('2018-08-20', result)

        # hypertension condition --> resolved -> ''
        patient.conditions = ConditionRecordSet([self.helper_condition('', 'H35039')])
        tested = Ccp003v1(patient=patient, timeframe=timeframe)
        result = tested.date_of_diagnosis
        self.assertEqual('', result)

        # several hypertension conditions --> the oldest
        patient.conditions = ConditionRecordSet([
            self.helper_condition('2018-08-19', 'I10'),
            self.helper_condition('2018-08-17', 'I169'),
            self.helper_condition('2018-08-18', 'I130'),
        ])
        tested = Ccp003v1(patient=patient, timeframe=timeframe)
        result = tested.date_of_diagnosis
        self.assertEqual('2018-08-17', result)

    def test_in_initial_population(self):
        start = arrow.get('2019-03-22 13:24:56')
        end = arrow.get('2020-03-22 13:24:56')
        timeframe = Timeframe(start=start, end=end)
        patient = self.load_patient('patient')

        # all patients are in the population
        tested = Ccp003v1(patient=patient, timeframe=timeframe)
        result = tested.in_initial_population()
        self.assertTrue(result)

    def test_in_denominator(self):
        start = arrow.get('2019-03-22 13:24:56')
        end = arrow.get('2020-03-22 13:24:56')
        timeframe = Timeframe(start=start, end=end)
        patient = self.load_patient('patient')

        # all patients are in the denominator
        tested = Ccp003v1(patient=patient, timeframe=timeframe)
        result = tested.in_initial_population()
        self.assertTrue(result)

    def test_in_numerator(self):
        start = arrow.get('2019-03-30 13:24:56')
        end = arrow.get('2020-03-30 13:24:56')
        timeframe = Timeframe(start=start, end=end)
        patient = self.load_patient('patient')

        # no condition -> False
        tested = Ccp003v1(patient=patient, timeframe=timeframe)
        result = tested.in_numerator()
        self.assertFalse(result)

        # not hypertension condition -> False
        patient.conditions = ConditionRecordSet([self.helper_condition('2018-08-20', '0QPD0JZ')])
        tested = Ccp003v1(patient=patient, timeframe=timeframe)
        result = tested.in_numerator()
        self.assertFalse(result)

        # hypertension condition --> True
        patient.conditions = ConditionRecordSet([self.helper_condition('2018-08-20', 'H35039')])
        tested = Ccp003v1(patient=patient, timeframe=timeframe)
        result = tested.in_numerator()
        self.assertTrue(result)

        # hypertension condition --> False
        patient.conditions = ConditionRecordSet([self.helper_condition('', 'H35039')])
        tested = Ccp003v1(patient=patient, timeframe=timeframe)
        result = tested.in_numerator()
        self.assertFalse(result)

        # several hypertension conditions --> True
        patient.conditions = ConditionRecordSet([
            self.helper_condition('2018-08-19', 'I10'),
            self.helper_condition('2018-08-17', 'I169'),
            self.helper_condition('2018-08-18', 'I130'),
        ])
        tested = Ccp003v1(patient=patient, timeframe=timeframe)
        result = tested.in_numerator()
        self.assertTrue(result)

    @patch(
        'canvas_workflow_kit.builtin_cqms.ccp003v1_hypertension.Ccp003v1.date_of_diagnosis',
        new_callable=PropertyMock)
    @patch('canvas_workflow_kit.builtin_cqms.ccp003v1_hypertension.Ccp003v1.in_numerator')
    @patch('canvas_workflow_kit.builtin_cqms.ccp003v1_hypertension.Ccp003v1.in_denominator')
    def test_compute_results(self, in_denominator, in_numerator, date_of_diagnosis):
        start = arrow.get('2019-03-30 13:24:56')
        end = arrow.get('2020-03-30 13:24:56')
        timeframe = Timeframe(start=start, end=end)
        patient = self.load_patient('patient')

        # not in_denominator (impossible in theory) -> not_applicable
        in_denominator.return_value = False
        in_numerator.return_value = True
        date_of_diagnosis.return_value = '2017-03-14 13:24:55+00:00'

        tested = Ccp003v1(patient=patient, timeframe=timeframe)
        result = tested.compute_results()
        self.assertEqual('not_applicable', result.status)
        self.assertIsNone(result.due_in)

        # in_denominator + not in_numerator -> satisfied
        in_denominator.return_value = True
        in_numerator.return_value = False
        date_of_diagnosis.return_value = '2017-03-14 13:24:55+00:00'

        tested = Ccp003v1(patient=patient, timeframe=timeframe)
        result = tested.compute_results()
        self.assertEqual('satisfied', result.status)
        self.assertEqual(-1, result.due_in)
        narratives = ['Nicolas has not been diagnosed of hypertension.']
        self.assertEqual(narratives, result.narratives)
        self.assertEqual(0, len(result.recommendations))

        # in_denominator + in_numerator -> due + date of diagnosis
        in_denominator.return_value = True
        in_numerator.return_value = True
        date_of_diagnosis.return_value = '2017-03-14 13:24:55+00:00'

        tested = Ccp003v1(patient=patient, timeframe=timeframe)
        result = tested.compute_results()
        self.assertEqual('due', result.status)
        self.assertEqual(0, result.due_in)
        narratives = ['Nicolas has been diagnosed of hypertension on Tue, Mar 14th 2017.']
        self.assertEqual(narratives, result.narratives)
        self.assertEqual(1, len(result.recommendations))
        recommendation = result.recommendations[0]
        self.assertEqual('CCP003v1_RECOMMEND_CONTACT', recommendation.key)
        self.assertEqual('Contact the patient', recommendation.title)

    def helper_condition(self, active_date: str, icd10: str):
        periods = [{'from': '2016-04-18', 'to': '2017-11-21'}]
        status = 'resolved'
        if active_date:
            status = 'active'
            periods.append({'from': active_date, 'to': None})
        return {
            'clinicalStatus': status,
            'coding': [{
                'code': icd10,
                'system': 'ICD-10'
            }],
            'periods': periods,
        }
