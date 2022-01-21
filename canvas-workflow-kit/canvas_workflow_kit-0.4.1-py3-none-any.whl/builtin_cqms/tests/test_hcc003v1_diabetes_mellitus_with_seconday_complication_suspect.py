import arrow

from canvas_workflow_kit import settings

from canvas_workflow_kit.builtin_cqms.hcc003v1_diabetes_mellitus_with_seconday_complication_suspect import (
    DiabetesOtherClassConditionSuspect,
    DiabetesWithoutComplication,
    Hcc003v1
)
from canvas_workflow_kit.patient_recordset import ConditionRecordSet
from canvas_workflow_kit.tests.base import SDKBaseTest
from canvas_workflow_kit.timeframe import Timeframe


class TestHcc003v1(SDKBaseTest):

    def setUp(self):
        self.mocks_path = f'{settings.BASE_DIR}/builtin_cqms/tests/mock_data'

    def test_enabled(self):
        self.assertTrue(Hcc003v1.enabled())

    def test_description(self):
        expected = ('All patients with diabetes, uncomplicated AND a '
                    '2ndary condition often associated with diabetes.')
        self.assertEqual(expected, Hcc003v1._meta.description)

    def test_information(self):
        expected = ('https://canvas-medical.zendesk.com/hc/en-us/articles/360057221174-Diabetes-Mellitus-With-Secondary-Complication-Suspect-HCC003v1')
        self.assertEqual(expected, Hcc003v1._meta.information)

    def test_change_types(self):
        result = Hcc003v1._meta.compute_on_change_types
        expected = [
            'protocol_override',
            'condition',
        ]
        self.assertEqual(len(expected), len(result))
        for change in expected:
            self.assertIn(change, result)

    def test__has_active_condition(self):
        start = arrow.get('2017-08-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)

        patient = self.load_patient('hcc003v1_diagnosed')

        # patient has a active condition after the date --> false
        patient.conditions = ConditionRecordSet([{
            'clinicalStatus': 'active',
            'coding': [{
                'system': 'ICD-10',
                'code': 'E119'
            }],
            'periods': [{
                'from': '2018-08-24',
                'to': None
            }]
        }])
        tested = Hcc003v1(patient=patient, timeframe=timeframe)
        self.assertFalse(tested._has_active_condition(DiabetesWithoutComplication))

        # patient has a active condition before the date --> true
        patient.conditions = ConditionRecordSet([{
            'clinicalStatus': 'active',
            'coding': [{
                'system': 'ICD-10',
                'code': 'E119'
            }],
            'periods': [{
                'from': '2018-08-23',
                'to': None
            }]
        }])
        tested = Hcc003v1(patient=patient, timeframe=timeframe)
        self.assertTrue(tested._has_active_condition(DiabetesWithoutComplication))

        # patient has a not active condition before the date --> false
        patient.conditions = ConditionRecordSet([{
            'clinicalStatus': 'active',
            'coding': [{
                'system': 'ICD-10',
                'code': 'E119'
            }],
            'periods': [{
                'from': '2016-08-23',
                'to': '2017-08-22'
            }]
        }])
        tested = Hcc003v1(patient=patient, timeframe=timeframe)
        self.assertFalse(tested._has_active_condition(DiabetesWithoutComplication))

        # patient has a resolved condition before the end date --> false
        patient.active_only = True
        patient.conditions = ConditionRecordSet([{
            'clinicalStatus': 'active',
            'coding': [{
                'system': 'ICD-10',
                'code': 'E119'
            }],
            'periods': [{
                'from': '2016-08-23',
                'to': '2018-08-20'
            }]
        }])
        tested = Hcc003v1(patient=patient, timeframe=timeframe)
        self.assertFalse(tested._has_active_condition(DiabetesWithoutComplication))

        # patient has a resolved condition after the end date --> true
        patient.conditions = ConditionRecordSet([{
            'clinicalStatus': 'active',
            'coding': [{
                'system': 'ICD-10',
                'code': 'E119'
            }],
            'periods': [{
                'from': '2016-08-23',
                'to': '2018-08-25'
            }]
        }])
        tested = Hcc003v1(patient=patient, timeframe=timeframe)
        self.assertTrue(tested._has_active_condition(DiabetesWithoutComplication))

        # patient has an other active condition before the date --> false
        patient.conditions = ConditionRecordSet([{
            'clinicalStatus': 'active',
            'coding': [{
                'system': 'ICD-10',
                'code': 'E119X'
            }],
            'periods': [{
                'from': '2018-08-23',
                'to': None
            }]
        }])
        tested = Hcc003v1(patient=patient, timeframe=timeframe)
        self.assertFalse(tested._has_active_condition(DiabetesWithoutComplication))

    def test__has_active_class_condition(self):
        start = arrow.get('2017-08-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)

        patient = self.load_patient('hcc003v1_diagnosed')

        # patient has a active condition after the date --> false
        patient.conditions = ConditionRecordSet([{
            'clinicalStatus': 'active',
            'coding': [{
                'system': 'ICD-10',
                'code': 'L97123'
            }],
            'periods': [{
                'from': '2018-08-24',
                'to': None
            }]
        }])
        tested = Hcc003v1(patient=patient, timeframe=timeframe)
        self.assertFalse(tested._has_active_class_condition(DiabetesOtherClassConditionSuspect))

        # patient has a active condition before the date --> true
        patient.conditions = ConditionRecordSet([{
            'clinicalStatus': 'active',
            'coding': [{
                'system': 'ICD-10',
                'code': 'L97123'
            }],
            'periods': [{
                'from': '2018-08-23',
                'to': None
            }]
        }])
        tested = Hcc003v1(patient=patient, timeframe=timeframe)
        self.assertTrue(tested._has_active_class_condition(DiabetesOtherClassConditionSuspect))

        # patient has a not active condition before the date --> false
        patient.conditions = ConditionRecordSet([{
            'clinicalStatus': 'active',
            'coding': [{
                'system': 'ICD-10',
                'code': 'L97123'
            }],
            'periods': [{
                'from': '2016-08-23',
                'to': '2017-08-23'
            }]
        }])
        tested = Hcc003v1(patient=patient, timeframe=timeframe)
        self.assertFalse(tested._has_active_class_condition(DiabetesOtherClassConditionSuspect))

        # patient has a resolved condition within the period --> false
        patient.active_only = True
        patient.conditions = ConditionRecordSet([{
            'clinicalStatus': 'active',
            'coding': [{
                'system': 'ICD-10',
                'code': 'L97123'
            }],
            'periods': [{
                'from': '2016-08-23',
                'to': '2018-08-20'
            }]
        }])
        tested = Hcc003v1(patient=patient, timeframe=timeframe)
        self.assertFalse(tested._has_active_class_condition(DiabetesOtherClassConditionSuspect))

        # patient has a resolved condition after the period --> false
        patient.active_only = True
        patient.conditions = ConditionRecordSet([{
            'clinicalStatus': 'active',
            'coding': [{
                'system': 'ICD-10',
                'code': 'L97123'
            }],
            'periods': [{
                'from': '2016-08-23',
                'to': '2018-08-25'
            }]
        }])
        tested = Hcc003v1(patient=patient, timeframe=timeframe)
        self.assertTrue(tested._has_active_class_condition(DiabetesOtherClassConditionSuspect))

        # patient has an other active condition before the date --> false
        patient.conditions = ConditionRecordSet([{
            'clinicalStatus': 'active',
            'coding': [{
                'system': 'ICD-10',
                'code': 'M97123'
            }],
            'periods': [{
                'from': '2018-08-23',
                'to': None
            }]
        }])
        tested = Hcc003v1(patient=patient, timeframe=timeframe)
        self.assertFalse(tested._has_active_class_condition(DiabetesOtherClassConditionSuspect))

    def test_has_diabetes_with_unspecified_condition(self):
        start = arrow.get('2017-08-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)

        patient = self.load_patient('hcc003v1_diagnosed')
        # patient has a active condition in HCC --> true
        patient.conditions = ConditionRecordSet([{
            'clinicalStatus': 'active',
            'coding': [{
                'system': 'ICD-10',
                'code': 'E119'
            }],
            'periods': [{
                'from': '2018-08-23',
                'to': None
            }]
        }])
        tested = Hcc003v1(patient=patient, timeframe=timeframe)

        self.assertTrue(tested.has_diabetes_with_unspecified_condition)
        # it is NOT memoize
        tested.patient.conditions = ConditionRecordSet([])
        self.assertFalse(tested.has_diabetes_with_unspecified_condition)

        # patient has NO active condition in HCC
        patient.conditions = ConditionRecordSet([{
            'clinicalStatus': 'active',
            'coding': [{
                'system': 'ICD-10',
                'code': 'E119X'
            }],
            'periods': [{
                'from': '2018-08-23',
                'to': None
            }]
        }])
        tested = Hcc003v1(patient=patient, timeframe=timeframe)

        self.assertFalse(tested.has_diabetes_with_unspecified_condition)

    def test_has_suspect_eye_condition(self):
        start = arrow.get('2017-08-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)

        patient = self.load_patient('hcc003v1_diagnosed')
        # patient has a active condition in HCC --> true
        patient.conditions = ConditionRecordSet([{
            'clinicalStatus': 'active',
            'coding': [{
                'system': 'ICD-10',
                'code': 'H28'
            }],
            'periods': [{
                'from': '2018-08-23',
                'to': None
            }]
        }])
        tested = Hcc003v1(patient=patient, timeframe=timeframe)

        self.assertTrue(tested.has_suspect_eye_condition)
        # it is memoize
        tested.patient.conditions = ConditionRecordSet([])
        self.assertTrue(tested.has_suspect_eye_condition)

        # patient has NO active condition in HCC
        patient.conditions = ConditionRecordSet([{
            'clinicalStatus': 'active',
            'coding': [{
                'system': 'ICD-10',
                'code': 'H28X'
            }],
            'periods': [{
                'from': '2018-08-23',
                'to': None
            }]
        }])
        tested = Hcc003v1(patient=patient, timeframe=timeframe)

        self.assertFalse(tested.has_suspect_eye_condition)

        # patient has a active class condition in HCC --> true
        patient.conditions = ConditionRecordSet([{
            'clinicalStatus': 'active',
            'coding': [{
                'system': 'ICD-10',
                'code': 'H35123'
            }],
            'periods': [{
                'from': '2018-08-23',
                'to': None
            }]
        }])
        tested = Hcc003v1(patient=patient, timeframe=timeframe)

        self.assertTrue(tested.has_suspect_eye_condition)

    def test_has_suspect_neurologic_condition(self):
        start = arrow.get('2017-08-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)

        patient = self.load_patient('hcc003v1_diagnosed')
        # patient has a active condition in HCC --> true
        patient.conditions = ConditionRecordSet([{
            'clinicalStatus': 'active',
            'coding': [{
                'system': 'ICD-10',
                'code': 'G63'
            }],
            'periods': [{
                'from': '2018-08-23',
                'to': None
            }]
        }])
        tested = Hcc003v1(patient=patient, timeframe=timeframe)

        self.assertTrue(tested.has_suspect_neurologic_condition)
        # it is memoize
        tested.patient.conditions = ConditionRecordSet([])
        self.assertTrue(tested.has_suspect_neurologic_condition)

        # patient has NO active condition in HCC
        patient.conditions = ConditionRecordSet([{
            'clinicalStatus': 'active',
            'coding': [{
                'system': 'ICD-10',
                'code': 'G63X'
            }],
            'periods': [{
                'from': '2018-08-23',
                'to': None
            }]
        }])
        tested = Hcc003v1(patient=patient, timeframe=timeframe)

        self.assertFalse(tested.has_suspect_neurologic_condition)

    def test_has_suspect_renal_condition(self):
        start = arrow.get('2017-08-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)

        patient = self.load_patient('hcc003v1_diagnosed')
        # patient has a active condition in HCC --> true
        patient.conditions = ConditionRecordSet([{
            'clinicalStatus': 'active',
            'coding': [{
                'system': 'ICD-10',
                'code': 'N184'
            }],
            'periods': [{
                'from': '2018-08-23',
                'to': None
            }]
        }])
        tested = Hcc003v1(patient=patient, timeframe=timeframe)

        self.assertTrue(tested.has_suspect_renal_condition)
        # it is memoize
        tested.patient.conditions = ConditionRecordSet([])
        self.assertTrue(tested.has_suspect_renal_condition)

        # patient has NO active condition in HCC
        patient.conditions = ConditionRecordSet([{
            'clinicalStatus': 'active',
            'coding': [{
                'system': 'ICD-10',
                'code': 'N184X'
            }],
            'periods': [{
                'from': '2018-08-23',
                'to': None
            }]
        }])
        tested = Hcc003v1(patient=patient, timeframe=timeframe)

        self.assertFalse(tested.has_suspect_renal_condition)

    def test_has_suspect_circulatory_condition(self):
        start = arrow.get('2017-08-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)

        patient = self.load_patient('hcc003v1_diagnosed')
        # patient has a active condition in HCC --> true
        patient.conditions = ConditionRecordSet([{
            'clinicalStatus': 'active',
            'coding': [{
                'system': 'ICD-10',
                'code': 'I70123'
            }],
            'periods': [{
                'from': '2018-08-23',
                'to': None
            }]
        }])
        tested = Hcc003v1(patient=patient, timeframe=timeframe)

        self.assertTrue(tested.has_suspect_circulatory_condition)
        # it is memoize
        tested.patient.conditions = ConditionRecordSet([])
        self.assertTrue(tested.has_suspect_circulatory_condition)

        # patient has NO active condition in HCC
        patient.conditions = ConditionRecordSet([{
            'clinicalStatus': 'active',
            'coding': [{
                'system': 'ICD-10',
                'code': 'I72123'
            }],
            'periods': [{
                'from': '2018-08-23',
                'to': None
            }]
        }])
        tested = Hcc003v1(patient=patient, timeframe=timeframe)

        self.assertFalse(tested.has_suspect_circulatory_condition)

    def test_has_suspect_other_condition(self):
        start = arrow.get('2017-08-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)

        patient = self.load_patient('hcc003v1_diagnosed')
        # patient has a active condition in HCC --> true
        patient.conditions = ConditionRecordSet([{
            'clinicalStatus': 'active',
            'coding': [{
                'system': 'ICD-10',
                'code': 'L970123'
            }],
            'periods': [{
                'from': '2018-08-23',
                'to': None
            }]
        }])
        tested = Hcc003v1(patient=patient, timeframe=timeframe)

        self.assertTrue(tested.has_suspect_other_condition)
        # it is memoize
        tested.patient.conditions = ConditionRecordSet([])
        self.assertTrue(tested.has_suspect_other_condition)

        # patient has NO active condition in HCC
        patient.conditions = ConditionRecordSet([{
            'clinicalStatus': 'active',
            'coding': [{
                'system': 'ICD-10',
                'code': 'L880123'
            }],
            'periods': [{
                'from': '2018-08-23',
                'to': None
            }]
        }])
        tested = Hcc003v1(patient=patient, timeframe=timeframe)

        self.assertFalse(tested.has_suspect_other_condition)

    def test_in_initial_population(self):
        start = arrow.get('2017-08-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)

        # any patient --> true
        patient = self.load_patient('hcc003v1_diagnosed')
        tested = Hcc003v1(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.in_initial_population())

    def test_in_denominator(self):
        start = arrow.get('2017-08-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)

        # patient has diabetes with unspecified conditions
        patient = self.load_patient('hcc003v1_diagnosed')
        patient.conditions = ConditionRecordSet([{
            'clinicalStatus': 'active',
            'coding': [{
                'system': 'ICD-10',
                'code': 'E119'
            }],
            'periods': [{
                'from': '2018-08-23',
                'to': None
            }]
        }])
        tested = Hcc003v1(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.in_denominator())

        # patient has no diabetes with unspecified conditions
        patient = self.load_patient('hcc003v1_diagnosed')
        patient.conditions = ConditionRecordSet([{
            'clinicalStatus': 'active',
            'coding': [{
                'system': 'ICD-10',
                'code': 'E119X'
            }],
            'periods': [{
                'from': '2018-08-23',
                'to': None
            }]
        }])
        tested = Hcc003v1(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.in_denominator())

    def test_in_numerator(self):
        start = arrow.get('2017-08-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)
        patient = self.load_patient('hcc003v1_diagnosed')

        # patient has a active eye condition
        patient.conditions = ConditionRecordSet([{
            'clinicalStatus': 'active',
            'coding': [{
                'system': 'ICD-10',
                'code': 'H28'
            }],
            'periods': [{
                'from': '2018-08-23',
                'to': None
            }]
        }])
        tested = Hcc003v1(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.in_numerator())

        # patient has a active neurologic condition
        patient.conditions = ConditionRecordSet([{
            'clinicalStatus': 'active',
            'coding': [{
                'system': 'ICD-10',
                'code': 'G63'
            }],
            'periods': [{
                'from': '2018-08-23',
                'to': None
            }]
        }])
        tested = Hcc003v1(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.in_numerator())

        # patient has a active renal condition
        patient.conditions = ConditionRecordSet([{
            'clinicalStatus': 'active',
            'coding': [{
                'system': 'ICD-10',
                'code': 'N184'
            }],
            'periods': [{
                'from': '2018-08-23',
                'to': None
            }]
        }])
        tested = Hcc003v1(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.in_numerator())

        # patient has a active circulatory condition
        patient.conditions = ConditionRecordSet([{
            'clinicalStatus': 'active',
            'coding': [{
                'system': 'ICD-10',
                'code': 'I70123'
            }],
            'periods': [{
                'from': '2018-08-23',
                'to': None
            }]
        }])
        tested = Hcc003v1(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.in_numerator())

        # patient has a active other complication condition
        patient.conditions = ConditionRecordSet([{
            'clinicalStatus': 'active',
            'coding': [{
                'system': 'ICD-10',
                'code': 'M14123'
            }],
            'periods': [{
                'from': '2018-08-23',
                'to': None
            }]
        }])
        tested = Hcc003v1(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.in_numerator())

        # patient has a active other condition
        patient.conditions = ConditionRecordSet([{
            'clinicalStatus': 'active',
            'coding': [{
                'system': 'ICD-10',
                'code': 'XXXX'
            }],
            'periods': [{
                'from': '2018-08-23',
                'to': None
            }]
        }])
        tested = Hcc003v1(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.in_numerator())

    def test_compute_results(self):
        start = arrow.get('2017-08-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)

        # patient has a No active condition diabetes with unspecified complications only
        # --> n/a
        patient = self.load_patient('hcc003v1_diagnosed')
        patient.conditions = ConditionRecordSet([{
            'clinicalStatus': 'active',
            'coding': [{
                'system': 'ICD-10',
                'code': 'H28'
            }],
            'periods': [{
                'from': '2018-08-23',
                'to': None
            }]
        }])
        tested = Hcc003v1(patient=patient, timeframe=timeframe)
        result = tested.compute_results()
        self.assertIsNotApplicable(result)

        # patient has a active condition diabetes with unspecified complications only
        # --> satisfied
        patient = self.load_patient('hcc003v1_diagnosed')
        tested = Hcc003v1(patient=patient, timeframe=timeframe)
        result = tested.compute_results()
        self.assertEqual('satisfied', result.status)
        self.assertEqual('', result.narrative)
        self.assertEqual([], result.recommendations)
        self.assertIsNone(result.due_in)

        # patient has a active condition diabetes with unspecified complications + eye suspect
        # --> due
        patient = self.load_patient('hcc003v1_diagnosed')
        patient.conditions = patient.conditions + ConditionRecordSet([{
            'clinicalStatus': 'active',
            'coding': [{
                'system': 'ICD-10',
                'code': 'H28'
            }],
            'periods': [{
                'from': '2018-08-23',
                'to': None
            }]
        }])
        tested = Hcc003v1(patient=patient, timeframe=timeframe)
        result = tested.compute_results()
        self.assertEqual('due', result.status)
        text = (f'Jim has Diabetes without complications AND '
                f'an eye condition commonly caused by diabetes on the Conditions list.')
        self.assertEqual(text, result.narrative)
        expected = [
            {
                'title': (f'Consider updating the Diabetes without complications (E11.9) '
                          f'to Diabetes with secondary eye disease as clinically appropriate.'),
                'command': {
                    'key': 'diagnose'
                },
                'key': 'HCC003v1_RECOMMEND_DIAGNOSE_EYE',
                'rank': 1,
                'button': 'Diagnose',
            },
        ]  # yapf: disable
        self.helper_exam_recommended(expected, result.recommendations)
        self.assertEqual(-1, result.due_in)

        # patient has a active condition diabetes with
        # unspecified complications + neurologic suspect --> due
        patient = self.load_patient('hcc003v1_diagnosed')
        patient.conditions = patient.conditions + ConditionRecordSet([{
            'clinicalStatus': 'active',
            'coding': [{
                'system': 'ICD-10',
                'code': 'G63'
            }],
            'periods': [{
                'from': '2018-08-23',
                'to': None
            }]
        }])
        tested = Hcc003v1(patient=patient, timeframe=timeframe)
        result = tested.compute_results()
        self.assertEqual('due', result.status)
        text = (f'Jim has Diabetes without complications AND '
                f'a neurological condition commonly caused by diabetes on the Conditions list.')
        self.assertEqual(text, result.narrative)
        expected = [
            {
                'title': ('Consider updating the Diabetes without '
                          'complications (E11.9) to Diabetes with '
                          'secondary neurological sequela as '
                          'clinically appropriate.'),
                'command': {
                    'key': 'diagnose'
                },
                'key': 'HCC003v1_RECOMMEND_DIAGNOSE_NEUROLOGICAL_SEQUELA',
                'rank': 2,
                'button': 'Diagnose',
            },
        ]  # yapf: disable
        self.helper_exam_recommended(expected, result.recommendations)
        self.assertEqual(-1, result.due_in)

        # patient has a active condition diabetes with unspecified complications + renal suspect
        # --> due
        patient = self.load_patient('hcc003v1_diagnosed')
        patient.conditions = patient.conditions + ConditionRecordSet([{
            'clinicalStatus': 'active',
            'coding': [{
                'system': 'ICD-10',
                'code': 'N184'
            }],
            'periods': [{
                'from': '2018-08-23',
                'to': None
            }]
        }])
        tested = Hcc003v1(patient=patient, timeframe=timeframe)
        result = tested.compute_results()
        self.assertEqual('due', result.status)
        text = (f'Jim has Diabetes without complications AND '
                f'a chronic renal condition commonly caused by diabetes on the Conditions list.')
        self.assertEqual(text, result.narrative)
        expected = [
            {
                'title': (f'Consider updating the Diabetes without complications (E11.9) '
                          f'to Diabetes with secondary renal disease as clinically appropriate.'),
                'command': {
                    'key': 'diagnose'
                },
                'key': 'HCC003v1_RECOMMEND_DIAGNOSE_RENAL_DISEASE',
                'rank': 3,
                'button': 'Diagnose',
            },
        ]  # yapf: disable
        self.helper_exam_recommended(expected, result.recommendations)
        self.assertEqual(-1, result.due_in)

        # patient has a active condition diabetes with
        # unspecified complications + circulatory suspect --> due
        patient = self.load_patient('hcc003v1_diagnosed')
        patient.conditions = patient.conditions + ConditionRecordSet([{
            'clinicalStatus': 'active',
            'coding': [{
                'system': 'ICD-10',
                'code': 'I79123'
            }],
            'periods': [{
                'from': '2018-08-23',
                'to': None
            }]
        }])
        tested = Hcc003v1(patient=patient, timeframe=timeframe)
        result = tested.compute_results()
        self.assertEqual('due', result.status)
        text = (f'Jim has Diabetes without complications AND '
                f'a circulatory condition commonly caused by diabetes on the Conditions list.')
        self.assertEqual(text, result.narrative)
        expected = [
            {
                'title': ('Consider updating the Diabetes without '
                          'complications (E11.9) to Diabetes with '
                          'secondary circulatory disorder as '
                          'clinically appropriate.'),
                'command': {
                    'key': 'diagnose'
                },
                'key': 'HCC003v1_RECOMMEND_DIAGNOSE_CIRCULATORY_DISORDER',
                'rank': 4,
                'button': 'Diagnose',
            },
        ]  # yapf: disable
        self.helper_exam_recommended(expected, result.recommendations)
        self.assertEqual(-1, result.due_in)

        # patient has a active condition diabetes with
        # unspecified complications + other suspect --> due
        patient = self.load_patient('hcc003v1_diagnosed')
        patient.conditions = patient.conditions + ConditionRecordSet([{
            'clinicalStatus': 'active',
            'coding': [{
                'system': 'ICD-10',
                'code': 'L98456'
            }],
            'periods': [{
                'from': '2018-08-23',
                'to': None
            }]
        }])
        tested = Hcc003v1(patient=patient, timeframe=timeframe)
        result = tested.compute_results()
        self.assertEqual('due', result.status)
        text = (f'Jim has Diabetes without complications AND '
                f'an another condition commonly caused by diabetes on the Conditions list.')
        self.assertEqual(text, result.narrative)
        expected = [
            {
                'title': ('Consider updating the Diabetes without '
                          'complications (E11.9) to Diabetes with '
                          'other secondary complication as '
                          'clinically appropriate.'),
                'command': {
                    'key': 'diagnose'
                },
                'key': 'HCC003v1_RECOMMEND_DIAGNOSE_COMPLICATION',
                'rank': 5,
                'button': 'Diagnose',
            },
        ]  # yapf: disable
        self.helper_exam_recommended(expected, result.recommendations)
        self.assertEqual(-1, result.due_in)

        # patient has a active condition diabetes with
        # unspecified complications + eye suspect + renal suspect --> due
        patient = self.load_patient('hcc003v1_diagnosed')
        patient.conditions = patient.conditions + ConditionRecordSet([
            {
                'clinicalStatus': 'active',
                'coding': [{
                    'system': 'ICD-10',
                    'code': 'N184'
                }],
                'periods': [{'from': '2018-08-23', 'to': None}]
            },
            {
                'clinicalStatus': 'active',
                'coding': [{
                    'system': 'ICD-10',
                    'code': 'H28'
                }],
                'periods': [{'from': '2018-08-23', 'to': None}]
            }
        ])  # yapf: disable
        tested = Hcc003v1(patient=patient, timeframe=timeframe)
        result = tested.compute_results()
        self.assertEqual('due', result.status)
        text = (f'Jim has Diabetes without complications AND '
                f'an eye condition commonly caused by diabetes on the Conditions list.\n'
                f'Jim has Diabetes without complications AND '
                f'a chronic renal condition commonly caused by diabetes on the Conditions list.')
        self.assertEqual(text, result.narrative)
        expected = [
            {
                'title': (f'Consider updating the Diabetes without complications (E11.9) '
                          f'to Diabetes with secondary eye disease as clinically appropriate.'),
                'command': {
                    'key': 'diagnose'
                },
                'key': 'HCC003v1_RECOMMEND_DIAGNOSE_EYE',
                'rank': 1,
                'button': 'Diagnose',
            },
            {
                'title': (f'Consider updating the Diabetes without complications (E11.9) '
                          f'to Diabetes with secondary renal disease as clinically appropriate.'),
                'command': {
                    'key': 'diagnose'
                },
                'key': 'HCC003v1_RECOMMEND_DIAGNOSE_RENAL_DISEASE',
                'rank': 3,
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
