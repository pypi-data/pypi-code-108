import arrow

from canvas_workflow_kit import settings

from canvas_workflow_kit.builtin_cqms.hcc004v1_dysrhythmia_suspect import Hcc004v1
from canvas_workflow_kit.patient_recordset import ConditionRecordSet, MedicationRecordSet
from canvas_workflow_kit.tests.base import SDKBaseTest
from canvas_workflow_kit.timeframe import Timeframe


class TestHcc004v1(SDKBaseTest):

    def setUp(self):
        self.mocks_path = f'{settings.BASE_DIR}/builtin_cqms/tests/mock_data'

    def test_enabled(self):
        self.assertTrue(Hcc004v1.enabled())

    def test_description(self):
        expected = ('All patients with potential dysrhythmia based on '
                    'an active medication without associated active problem.')
        self.assertEqual(expected, Hcc004v1._meta.description)

    def test_information(self):
        expected = ('https://canvas-medical.zendesk.com/hc/en-us/articles/360059083773-Dysrhythmia-Suspects-HCC004v1')
        self.assertEqual(expected, Hcc004v1._meta.information)

    def test_change_types(self):
        result = Hcc004v1._meta.compute_on_change_types
        expected = [
            'protocol_override',
            'condition',
            'medication',
        ]
        self.assertEqual(len(expected), len(result))
        for change in expected:
            self.assertIn(change, result)

    def test_in_initial_population(self):
        start = arrow.get('2017-08-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)
        patient = self.load_patient('hcc004v1')
        tested = Hcc004v1(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.in_initial_population())

    def test_in_denominator_patient_with_active_antiarrhythmics_medication(self):
        start = arrow.get('2017-08-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)

        patient = self.load_patient('hcc004v1')
        patient.medications = MedicationRecordSet([{
            'periods': [{
                'from': '2018-08-18',
                'to': None
            }],
            'clinicalStatus': 'active',
            'coding': [{
                'id': 35,
                'system': 'http://www.fdbhealth.com/',
                'version': '',
                'code': '564460'
            }]
        }])
        tested = Hcc004v1(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.in_denominator())

        patient = self.load_patient('hcc004v1')
        patient.active_only = True
        patient.medications = MedicationRecordSet([{
            'periods': [{
                'from': '2018-03-08',
                'to': '2018-08-18'
            }],
            'clinicalStatus': 'active',
            'coding': [{
                'id': 35,
                'system': 'http://www.fdbhealth.com/',
                'version': '',
                'code': '564460'
            }]
        }])
        tested = Hcc004v1(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.in_denominator())

        patient = self.load_patient('hcc004v1')
        patient.active_only = True
        patient.medications = MedicationRecordSet([{
            'periods': [{
                'from': '2018-03-08',
                'to': '2018-08-24'
            }],
            'clinicalStatus': 'active',
            'coding': [{
                'id': 35,
                'system': 'http://www.fdbhealth.com/',
                'version': '',
                'code': '564460'
            }]
        }])
        tested = Hcc004v1(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.in_denominator())

    def test_in_denominator_patient_with_active_medication_not_antiarrhythmics(self):
        start = arrow.get('2017-08-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)

        patient = self.load_patient('hcc004v1')
        patient.medications = MedicationRecordSet([{
            'periods': [{
                'from': '2018-08-18',
                'to': None
            }],
            'clinicalStatus': 'active',
            'coding': [{
                'id': 35,
                'system': 'http://www.fdbhealth.com/',
                'version': '',
                'code': '564017'
            }]
        }])
        tested = Hcc004v1(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.in_denominator())

    def test_in_denominator_patient_without_active_medication(self):
        start = arrow.get('2017-08-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)
        patient = self.load_patient('hcc004v1')
        tested = Hcc004v1(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.in_denominator())

    def test_in_numerator_patient_without_active_condition(self):
        now = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=now, end=now)
        patient = self.load_patient('hcc004v1')
        tested = Hcc004v1(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.in_numerator())

    def test_in_numerator_patient_with_active_condition_in_dysrhythmia_class(self):
        start = arrow.get('2017-08-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)

        patient = self.load_patient('hcc004v1')
        patient.conditions = ConditionRecordSet([{
            'clinicalStatus': 'active',
            'coding': [{
                'system': 'ICD-10',
                'code': 'I420'
            }],
            'periods': [{
                'from': '2018-08-23',
                'to': None
            }],
        }])
        tested = Hcc004v1(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.in_numerator())

        patient = self.load_patient('hcc004v1')
        patient.active_only = True
        patient.conditions = ConditionRecordSet([{
            'clinicalStatus': 'active',
            'coding': [{
                'system': 'ICD-10',
                'code': 'I420'
            }],
            'periods': [{
                'from': '2018-05-23',
                'to': '2018-08-20'
            }],
        }])
        tested = Hcc004v1(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.in_numerator())

        patient = self.load_patient('hcc004v1')
        patient.active_only = True
        patient.conditions = ConditionRecordSet([{
            'clinicalStatus': 'active',
            'coding': [{
                'system': 'ICD-10',
                'code': 'I420'
            }],
            'periods': [{
                'from': '2018-08-01',
                'to': '2018-08-27'
            }],
        }])
        tested = Hcc004v1(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.in_numerator())

    def test_in_numerator_patient_with_not_active_condition_in_dysrhythmia_class(self):
        start = arrow.get('2017-08-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)
        patient = self.load_patient('hcc004v1')
        patient.conditions = ConditionRecordSet([{
            'clinicalStatus': 'active',
            'coding': [{
                'system': 'ICD-10',
                'code': 'I420'
            }],
            'periods': [{
                'from': '2016-08-23',
                'to': '2017-08-22'
            }],
        }])
        tested = Hcc004v1(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.in_numerator())

    def test_in_numerator_patient_with_active_condition_not_in_dysrhythmia_class(self):
        start = arrow.get('2017-08-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)
        patient = self.load_patient('hcc004v1')
        patient.conditions = ConditionRecordSet([{
            'clinicalStatus': 'active',
            'coding': [{
                'system': 'ICD-10',
                'code': 'I240'
            }],
            'periods': [{
                'from': '2018-08-23',
                'to': None
            }],
        }])
        tested = Hcc004v1(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.in_numerator())

    def test_compute_results_patient_without_active_medication(self):
        start = arrow.get('2017-08-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)
        patient = self.load_patient('hcc004v1')
        tested = Hcc004v1(patient=patient, timeframe=timeframe)
        result = tested.compute_results()
        self.assertIsNotApplicable(result)

    def test_compute_results_patient_with_active_antiarrhythmics_med_with_dysrhythmia_dx(self):
        start = arrow.get('2017-08-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)
        patient = self.load_patient('hcc004v1')
        patient.medications = MedicationRecordSet([{
            'periods': [{
                'from': '2018-08-18',
                'to': None
            }],
            'clinicalStatus': 'active',
            'coding': [{
                'id': 35,
                'system': 'http://www.fdbhealth.com/',
                'version': '',
                'code': '564460'
            }]
        }])
        patient.conditions = ConditionRecordSet([{
            'clinicalStatus': 'active',
            'coding': [{
                'system': 'ICD-10',
                'code': 'I420'
            }],
            'periods': [{
                'from': '2018-08-23',
                'to': None
            }],
        }])
        tested = Hcc004v1(patient=patient, timeframe=timeframe)
        result = tested.compute_results()
        self.assertEqual('satisfied', result.status)
        text = ''
        self.assertEqual(text, result.narrative)
        self.assertEqual([], result.recommendations)
        self.assertIsNone(result.due_in)

    def test_compute_results_patient_with_active_antiarrhythmics_med_without_dysrhythmia_dx(self):
        start = arrow.get('2017-08-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)
        patient = self.load_patient('hcc004v1')
        patient.medications = MedicationRecordSet([{
            'periods': [{
                'from': '2018-08-18',
                'to': None
            }],
            'clinicalStatus': 'active',
            'coding': [{
                'id': 35,
                'system': 'http://www.fdbhealth.com/',
                'version': '',
                'code': '564460'
            }]
        }])
        tested = Hcc004v1(patient=patient, timeframe=timeframe)
        result = tested.compute_results()
        self.assertEqual('due', result.status)
        text = (
            'Jim has an active medication on the Medication List commonly used for Dysrhythmia. '
            'There is no associated condition on the Conditions List.')
        self.assertEqual(text, result.narrative)
        expected = [
            {
                'title': ('Consider updating the Conditions List to include Dysrhythmia '
                          'related problem as clinically appropriate.'),
                'command': {
                    'key': 'diagnose'
                },
                'key': 'HCC004v1_RECOMMEND_DIAGNOSE_DYSRHYTHMIA',
                'rank': 1,
                'button': 'Diagnose',
            },
        ]  # yapf: disable
        self.helper_exam_recommended(expected, result.recommendations)
        self.assertEqual(-1, result.due_in)

    def helper_exam_recommended(self, expected, result):
        for exp, recommendation in zip(expected, result):
            self.assertEqual(exp['key'], recommendation.key)
            self.assertEqual(exp['rank'], recommendation.rank)
            self.assertEqual(exp['button'], recommendation.button)
            self.assertEqual(exp['title'], recommendation.title)
            self.assertEqual(exp['command']['key'], recommendation.command['key'])
