import arrow

from canvas_workflow_kit import settings

from canvas_workflow_kit.builtin_cqms.diabetes_quality_measure import DiabetesQualityMeasure
from canvas_workflow_kit.patient_recordset import (
    BillingLineItemRecordSet,
    ConditionRecordSet,
    ProtocolOverrideRecordSet
)
from canvas_workflow_kit.tests.base import SDKBaseTest
from canvas_workflow_kit.timeframe import Timeframe


class DiabetesQualityMeasureTest(SDKBaseTest):

    def setUp(self):
        self.mocks_path = f'{settings.BASE_DIR}/builtin_cqms/tests/mock_data'

    def test_abstract(self):
        self.assertTrue(DiabetesQualityMeasure._meta.abstract)

    def test_in_initial_population(self):
        start = arrow.get('2017-08-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)

        # patient has no diabetes --> false
        patient = self.load_patient('diabetes_mixin')
        patient.conditions = ConditionRecordSet([])
        protocol = DiabetesQualityMeasure(patient=patient, timeframe=timeframe)
        self.assertFalse(protocol.in_initial_population())

        # patient has diabetes --> true
        patient = self.load_patient('diabetes_mixin')
        protocol = DiabetesQualityMeasure(patient=patient, timeframe=timeframe)
        self.assertTrue(protocol.in_initial_population())

        patient.billing_line_items = BillingLineItemRecordSet([])
        protocol = DiabetesQualityMeasure(patient=patient, timeframe=timeframe)
        protocol.in_initial_population()
        self.assertFalse(protocol.in_initial_population())
        protocol = DiabetesQualityMeasure(patient=patient, timeframe=timeframe, context='report')
        self.assertFalse(protocol.in_initial_population())
        protocol = DiabetesQualityMeasure(patient=patient, timeframe=timeframe, context='guidance')
        self.assertTrue(protocol.in_initial_population())

        # -- patient to young < 18 --> false
        patient = self.load_patient('diabetes_mixin')
        patient.patient['birthDate'] = '2000-08-24'
        self.assertTrue(17 < patient.age_at(timeframe.end) < 18)
        protocol = DiabetesQualityMeasure(patient=patient, timeframe=timeframe)
        self.assertFalse(protocol.in_initial_population())
        patient.patient['birthDate'] = '2000-08-23'
        self.assertTrue(patient.age_at(timeframe.end) == 18)
        protocol = DiabetesQualityMeasure(patient=patient, timeframe=timeframe)
        self.assertTrue(protocol.in_initial_population())

        # -- patient to old > 75 --> false
        patient = self.load_patient('diabetes_mixin')
        patient.patient['birthDate'] = '1943-08-22'
        self.assertTrue(75 < patient.age_at(timeframe.end) < 76)
        protocol = DiabetesQualityMeasure(patient=patient, timeframe=timeframe)
        self.assertFalse(protocol.in_initial_population())
        patient.patient['birthDate'] = '1943-08-23'
        self.assertTrue(patient.age_at(timeframe.end) == 75)
        protocol = DiabetesQualityMeasure(patient=patient, timeframe=timeframe)
        self.assertFalse(protocol.in_initial_population())
        patient.patient['birthDate'] = '1943-08-24'
        self.assertTrue(patient.age_at(timeframe.end) < 75)
        protocol = DiabetesQualityMeasure(patient=patient, timeframe=timeframe)
        self.assertTrue(protocol.in_initial_population())

        # -- patient has an other code --> false
        patient = self.load_patient('diabetes_mixin')
        for condition in patient.conditions:
            for code in condition['coding']:
                code['code'] = 'code'
        protocol = DiabetesQualityMeasure(patient=patient, timeframe=timeframe)
        self.assertFalse(protocol.in_initial_population())

        # -- patient has diabetes resolved before the period --> false
        patient = self.load_patient('diabetes_mixin')
        patient.conditions[0]['periods'][0]['to'] = '2017-08-22'
        protocol = DiabetesQualityMeasure(patient=patient, timeframe=timeframe)
        self.assertFalse(protocol.in_initial_population())

        # -- patient has diabetes resolved within the period --> true
        patient = self.load_patient('diabetes_mixin')
        patient.conditions[0]['periods'][0]['to'] = '2017-08-24'
        protocol = DiabetesQualityMeasure(patient=patient, timeframe=timeframe)
        self.assertTrue(protocol.in_initial_population())

        # -- patient has diabetes resolved within the period + active only  --> false
        patient = self.load_patient('diabetes_mixin')
        patient.conditions[0]['periods'][0]['to'] = '2017-08-24'
        patient.active_only = True
        protocol = DiabetesQualityMeasure(patient=patient, timeframe=timeframe)
        self.assertFalse(protocol.in_initial_population())

    def test_in_initial_population_with_override(self):
        patient = self.load_patient('diabetes_mixin')
        patient.protocol_overrides = ProtocolOverrideRecordSet([{
            'protocolKey': 'DiabetesQualityMeasure',
            'adjustment': {
                'reference': '2018-02-01T00:00:00Z',
                'cycleDays': 180
            },
            'snooze': None,
            'modified': '2018-03-15T12:32:54Z',
        }])  # yapf: disable
        patient.patient['birthDate'] = '2000-08-24'

        tested = DiabetesQualityMeasure(patient=patient, now=arrow.get('2018-08-23'))
        self.assertFalse(tested.in_initial_population())

        tested = DiabetesQualityMeasure(patient=patient, now=arrow.get('2018-08-25'))
        self.assertTrue(tested.in_initial_population())

        patient.billing_line_items = BillingLineItemRecordSet([{
            'id': 92,
            'created': '2075-08-05T21:41:21.407046Z',
            'cpt': '99202',
            'units': 1
        }])
        tested = DiabetesQualityMeasure(patient=patient, now=arrow.get('2075-08-23'))
        self.assertTrue(tested.in_initial_population())

        tested = DiabetesQualityMeasure(patient=patient, now=arrow.get('2075-08-25'))
        self.assertFalse(tested.in_initial_population())

    def test_has_diabetes_in_period(self):
        start = arrow.get('2017-08-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)

        # patient has no diabetes --> false
        patient = self.load_patient('diabetes_mixin')
        patient.conditions = ConditionRecordSet([])
        protocol = DiabetesQualityMeasure(patient=patient, timeframe=timeframe)
        self.assertFalse(protocol.has_diabetes_in_period())

        # patient has diabetes --> true
        patient = self.load_patient('diabetes_mixin')
        protocol = DiabetesQualityMeasure(patient=patient, timeframe=timeframe)
        self.assertTrue(protocol.has_diabetes_in_period())

        # -- patient has diabetes resolved before the period --> false
        patient = self.load_patient('diabetes_mixin')
        patient.conditions[0]['periods'][0]['to'] = '2017-08-22'
        protocol = DiabetesQualityMeasure(patient=patient, timeframe=timeframe)
        self.assertFalse(protocol.has_diabetes_in_period())

        # -- patient has diabetes resolved within the period --> true
        patient = self.load_patient('diabetes_mixin')
        patient.conditions[0]['periods'][0]['to'] = '2017-08-24'
        protocol = DiabetesQualityMeasure(patient=patient, timeframe=timeframe)
        self.assertTrue(protocol.has_diabetes_in_period())

        # -- patient has diabetes resolved within the period + active only--> false
        patient = self.load_patient('diabetes_mixin')
        patient.conditions[0]['periods'][0]['to'] = '2017-08-24'
        patient.active_only = True
        protocol = DiabetesQualityMeasure(patient=patient, timeframe=timeframe)
        self.assertFalse(protocol.has_diabetes_in_period())

        # -- patient has diabetes after the period --> false
        now = arrow.get('1998-08-22 13:24:56')
        timeframe = Timeframe(start=now, end=now)
        patient = self.load_patient('diabetes_mixin')
        protocol = DiabetesQualityMeasure(patient=patient, timeframe=timeframe)
        self.assertTrue(protocol.has_diabetes_in_period())
        now = arrow.get('1998-08-21 13:24:56')
        timeframe = Timeframe(start=now, end=now)
        patient = self.load_patient('diabetes_mixin')
        protocol = DiabetesQualityMeasure(patient=patient, timeframe=timeframe)
        self.assertFalse(protocol.has_diabetes_in_period())

    def test_first_due_in(self):
        start = arrow.get('2017-08-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)

        # patient has diabetes + older than 18 --> none
        patient = self.load_patient('diabetes_mixin')
        patient.patient['birthDate'] = '2000-08-22'
        protocol = DiabetesQualityMeasure(patient=patient, timeframe=timeframe)
        self.assertIsNone(protocol.first_due_in())

        # patient has diabetes + younger than 18 --> none
        patient = self.load_patient('diabetes_mixin')
        patient.patient['birthDate'] = '2000-08-30'
        protocol = DiabetesQualityMeasure(patient=patient, timeframe=timeframe)
        self.assertEqual(6, protocol.first_due_in())

        # patient has NO diabetes + younger than 18 --> none
        patient = self.load_patient('diabetes_mixin')
        patient.conditions = ConditionRecordSet([])
        patient.patient['birthDate'] = '2000-08-30'
        protocol = DiabetesQualityMeasure(patient=patient, timeframe=timeframe)
        self.assertIsNone(protocol.first_due_in())

    def test_first_due_in_with_override(self):
        patient = self.load_patient('diabetes_mixin')
        # patient.conditions = ConditionRecordSet([{
        #     'coding': [{
        #         'system': 'ICD-10',
        #         'code': 'E119'
        #     }],
        #     'periods': [{
        #         'from': '2018-05-24',
        #         'to': None
        #     }]
        # }])
        patient.protocol_overrides = ProtocolOverrideRecordSet([{
            'protocolKey': 'DiabetesQualityMeasure',
            'adjustment': {
                'reference': '2018-02-01T00:00:00Z',
                'cycleDays': 180
            },
            'snooze': None,
            'modified': '2018-03-15T12:32:54Z',
        }])  # yapf: disable
        patient.patient['birthDate'] = '2000-08-24'
        tested = DiabetesQualityMeasure(patient=patient, now=arrow.get('2018-08-05'))
        result = tested.first_due_in()
        self.assertEqual(19, result)

    def test_specific_visits(self):
        patient = self.load_patient('diabetes_mixin')
        tested = DiabetesQualityMeasure(patient=patient, now=arrow.get('2018-08-05'))
        result = tested.specific_visits
        self.assertIn('cpt', result.values)
        self.assertEqual(24, len(result.values['cpt']))
