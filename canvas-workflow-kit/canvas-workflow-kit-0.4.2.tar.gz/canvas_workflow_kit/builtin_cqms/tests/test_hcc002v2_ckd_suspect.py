import arrow

from canvas_workflow_kit import settings

from canvas_workflow_kit.builtin_cqms.hcc002v2_ckd_suspect import Hcc002v2
from canvas_workflow_kit.patient_recordset import ConditionRecordSet, ProtocolOverrideRecordSet
from canvas_workflow_kit.tests.base import SDKBaseTest
from canvas_workflow_kit.timeframe import Timeframe


class TestHcc002v2(SDKBaseTest):

    def setUp(self):
        self.mocks_path = f'{settings.BASE_DIR}/builtin_cqms/tests/mock_data'

    def test_enabled(self):
        self.assertTrue(Hcc002v2.enabled())

    def test_description(self):
        expected = ('All patients with evidence of two or more elevated eGFR values '
                    'and no active CKD problem on the Conditions List.')
        self.assertEqual(expected, Hcc002v2._meta.description)

    def test_information(self):
        expected = 'https://canvas-medical.zendesk.com/hc/en-us/articles/360059083713-CKD-Suspect-HCC002v2'
        self.assertEqual(expected, Hcc002v2._meta.information)

    def test_change_types(self):
        result = Hcc002v2._meta.compute_on_change_types
        expected = [
            'protocol_override',
            'condition',
            'lab_report',
            'patient',
        ]
        self.assertEqual(len(expected), len(result))
        for change in expected:
            self.assertIn(change, result)

    def test_high_creatine_levels(self):
        start = arrow.get('2017-08-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)

        # patient has two lab reports with creatinine eGFR under 60 within the last 2 years
        patient = self.load_patient('hcc002v2_diagnosed')
        tested = Hcc002v2(patient=patient, timeframe=timeframe)
        self.assertEqual(2, len(tested.high_creatine_levels))

        # patient has two lab report within the last 2 years,
        # only one with creatinine eGFR under 60
        patient = self.load_patient('hcc002v2_diagnosed')
        patient.lab_reports[0]['value'] = '1.1'
        tested = Hcc002v2(patient=patient, timeframe=timeframe)
        self.assertEqual(1, len(tested.high_creatine_levels))

        # patient has two lab reports with creatinine eGFR under 60,
        # only one within the last 2 years
        patient = self.load_patient('hcc002v2_diagnosed')
        patient.lab_reports[0]['originalDate'] = '2016-08-22'
        tested = Hcc002v2(patient=patient, timeframe=timeframe)
        self.assertEqual(1, len(tested.high_creatine_levels))

    def test_high_creatine_levels_with_override(self):
        patient = self.load_patient('hcc002v2_diagnosed')
        patient.protocol_overrides = ProtocolOverrideRecordSet([{
            'protocolKey': 'Hcc002v2',
            'adjustment': {
                'reference': '2018-02-01T00:00:00Z',
                'cycleDays': 180
            },
            'snooze': None,
            'modified': '2018-03-15T12:32:54Z',
        }])  # yapf: disable
        patient.lab_reports[0]['originalDate'] = '2018-08-01'
        patient.lab_reports[1]['originalDate'] = '2018-09-01'

        tested = Hcc002v2(patient=patient, now=arrow.get('2018-08-01').shift(days=120))
        self.assertEqual(2, len(tested.high_creatine_levels))
        tested = Hcc002v2(patient=patient, now=arrow.get('2018-08-01').shift(days=180))
        self.assertEqual(2, len(tested.high_creatine_levels))
        tested = Hcc002v2(patient=patient, now=arrow.get('2018-08-01').shift(days=181))
        self.assertEqual(1, len(tested.high_creatine_levels))

    def test_has_active_condition(self):
        start = arrow.get('2017-08-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)

        # patient has an active condition in HCC
        patient = self.load_patient('hcc002v2_diagnosed')
        tested = Hcc002v2(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.has_active_condition)

        # patient has NO active condition in HCC
        patient = self.load_patient('hcc002v2_diagnosed')
        patient.conditions[0]['clinicalStatus'] = 'XXXXXXXX'
        tested = Hcc002v2(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.has_active_condition)

        # patient has a condition NOT in HCC
        patient = self.load_patient('hcc002v2_diagnosed')
        patient.conditions[0]['coding'][0]['code'] = 'XXXXXXXX'
        patient.conditions[0]['coding'][1]['code'] = 'XXXXXXXX'
        tested = Hcc002v2(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.has_active_condition)

        # patient has NO condition
        patient = self.load_patient('hcc002v2_diagnosed')
        patient.conditions = ConditionRecordSet([])
        tested = Hcc002v2(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.has_active_condition)

    def test_eGFR(self):
        start = arrow.get('2017-08-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        now = arrow.get('2018-12-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)

        patient = self.load_patient('hcc002v2_diagnosed')
        tested = Hcc002v2(patient=patient, timeframe=timeframe, now=now)

        # change of units
        result = tested.eGFR(1.37, 'mg/dL')
        expected = 66.45
        self.assertAlmostEqual(expected, result, 2)

        result = tested.eGFR(1.37 * 88.4, 'µmol/L')
        expected = 66.45
        self.assertAlmostEqual(expected, result, 2)

        # sex influence
        tested.patient.patient['sexAtBirth'] = 'F'
        result = tested.eGFR(1.37, 'mg/dL')
        expected = 49.31
        self.assertAlmostEqual(expected, result, 2)
        tested.patient.patient['sexAtBirth'] = 'M'

        # race influence
        tested.patient.patient['biologicalRaceCode'] = '2106-3'
        result = tested.eGFR(1.37, 'mg/dL')
        expected = 54.92
        self.assertAlmostEqual(expected, result, 2)
        tested.patient.patient['biologicalRaceCode'] = '2054-5'

        # age influence
        tested.patient.patient['birthDate'] = '1941-01-01'
        result = tested.eGFR(1.37, 'mg/dL')
        expected = 64.80
        self.assertAlmostEqual(expected, result, 2)
        tested.patient.patient['birthDate'] = '1951-01-01'

    def test_in_initial_population(self):
        start = arrow.get('2017-08-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)

        # any patient --> true
        patient = self.load_patient('hcc002v2_diagnosed')
        tested = Hcc002v2(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.in_initial_population())

    def test_in_denominator(self):
        start = arrow.get('2017-08-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)

        # patient has two lab reports with creatinine above 1.1 within the last 2 years
        patient = self.load_patient('hcc002v2_diagnosed')
        tested = Hcc002v2(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.in_denominator())

        # patient has two lab report within the last 2 years, only one with creatinine above 1.1
        patient = self.load_patient('hcc002v2_diagnosed')
        patient.lab_reports[0]['value'] = '1.1'
        tested = Hcc002v2(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.in_denominator())

        # patient has two lab reports with creatinine above 1.1, only one within the last 2 years
        patient = self.load_patient('hcc002v2_diagnosed')
        patient.lab_reports[0]['originalDate'] = '2016-08-22'
        tested = Hcc002v2(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.in_denominator())

    def test_in_numerator(self):
        start = arrow.get('2017-08-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)

        # patient has a active condition in HCC
        patient = self.load_patient('hcc002v2_diagnosed')
        tested = Hcc002v2(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.in_numerator())

        # patient has NO active condition in HCC
        patient = self.load_patient('hcc002v2_diagnosed')
        patient.conditions[0]['clinicalStatus'] = 'XXXXXXXX'
        tested = Hcc002v2(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.in_numerator())

        # patient has a condition NOT in HCC
        patient = self.load_patient('hcc002v2_diagnosed')
        patient.conditions[0]['coding'][0]['code'] = 'XXXXXXXX'
        patient.conditions[0]['coding'][1]['code'] = 'XXXXXXXX'
        tested = Hcc002v2(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.in_numerator())

        # patient has NO condition
        patient = self.load_patient('hcc002v2_diagnosed')
        patient.conditions = ConditionRecordSet([])
        tested = Hcc002v2(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.in_numerator())

    def test_compute_results(self):
        start = arrow.get('2017-08-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)

        # patient has a active condition in HCC and two lab reports
        # with creatinine above 1.1 within the last 2 years
        # --> satisfied
        patient = self.load_patient('hcc002v2_diagnosed')
        tested = Hcc002v2(patient=patient, timeframe=timeframe)
        result = tested.compute_results()
        self.assertEqual('satisfied', result.status)
        text = ''
        self.assertEqual(text, result.narrative)
        self.assertEqual([], result.recommendations)
        self.assertIsNone(result.due_in)

        # patient has NO active condition in HCC and two lab reports
        # with creatinine above 1.1 within the last 2 years
        # --> due
        patient = self.load_patient('hcc002v2_diagnosed')
        tested = Hcc002v2(patient=patient, timeframe=timeframe)
        patient.conditions[0]['coding'][0]['code'] = 'XXXXXXXX'
        patient.conditions[0]['coding'][1]['code'] = 'XXXXXXXX'
        result = tested.compute_results()
        self.assertEqual('due', result.status)
        text = (f'Jim has at least two eGFR measurements < 60 ml/min '
                f'over the last two years suggesting renal disease. '
                f'There is no associated condition on the Conditions List.')
        self.assertEqual(text, result.narrative)
        expected = [
            {
                'title': (f'Consider updating the Conditions List to include kidney '
                          f'related problems as clinically appropriate'),
                'command': {
                    'key': 'diagnose'
                },
                'key': 'HCC002v2_RECOMMEND_DIAGNOSE',
                'rank': 1,
                'button': 'Diagnose',
            },
        ]  # yapf: disable
        self.helper_exam_recommended(expected, result.recommendations)
        self.assertEqual(-1, result.due_in)

        # patient has one lab report with creatinine above 1.1 within the last 2 years
        # --> n/a
        patient = self.load_patient('hcc002v2_diagnosed')
        patient.conditions = ConditionRecordSet([])
        patient.lab_reports[0]['value'] = '1.1'
        tested = Hcc002v2(patient=patient, timeframe=timeframe)
        result = tested.compute_results()
        self.assertIsNotApplicable(result)

    def test_compute_results_with_override(self):
        patient = self.load_patient('hcc002v2_diagnosed')
        patient.protocol_overrides = ProtocolOverrideRecordSet([{
            'protocolKey': 'Hcc002v2',
            'adjustment': {
                'reference': '2018-02-01T00:00:00Z',
                'cycleDays': 180
            },
            'snooze': None,
            'modified': '2018-03-15T12:32:54Z',
        }])  # yapf: disable
        patient.lab_reports[0]['originalDate'] = '2018-08-01'
        patient.lab_reports[1]['originalDate'] = '2018-09-01'
        patient.conditions[0]['coding'][0]['code'] = 'XXXXXXXX'
        patient.conditions[0]['coding'][1]['code'] = 'XXXXXXXX'

        tested = Hcc002v2(patient=patient, now=arrow.get('2018-08-01').shift(days=120))
        result = tested.compute_results()
        self.assertEqual('due', result.status)
        self.assertEqual(-1, result.due_in)

        tested = Hcc002v2(patient=patient, now=arrow.get('2018-08-01').shift(days=180))
        result = tested.compute_results()
        self.assertEqual('due', result.status)
        self.assertEqual(-1, result.due_in)

        tested = Hcc002v2(patient=patient, now=arrow.get('2018-08-01').shift(days=181))
        result = tested.compute_results()
        self.assertIsNotApplicable(result)

    def helper_exam_recommended(self, expected, result):
        for exp, recommendation in zip(expected, result):
            self.assertEqual(exp['key'], recommendation.key)
            self.assertEqual(exp['rank'], recommendation.rank)
            self.assertEqual(exp['button'], recommendation.button)
            self.assertEqual(exp['title'], recommendation.title)
            self.assertEqual(exp['command']['key'], recommendation.command['key'])
