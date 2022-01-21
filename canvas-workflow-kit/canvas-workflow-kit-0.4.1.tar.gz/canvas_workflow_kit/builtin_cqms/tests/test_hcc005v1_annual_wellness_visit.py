import arrow

from canvas_workflow_kit import settings

from canvas_workflow_kit.builtin_cqms.hcc005v1_annual_wellness_visit import Hcc005v1
from canvas_workflow_kit.patient_recordset import BillingLineItemRecordSet, ProtocolOverrideRecordSet
from canvas_workflow_kit.tests.base import SDKBaseTest
from canvas_workflow_kit.timeframe import Timeframe


class TestHcc005v1(SDKBaseTest):

    def setUp(self):
        self.mocks_path = f'{settings.BASE_DIR}/builtin_cqms/tests/mock_data'

    def test_enabled(self):
        self.assertTrue(Hcc005v1.enabled())

    def test_description(self):
        expected = 'Patient 65 or older due  for Annual Wellness Visit.'
        self.assertEqual(expected, Hcc005v1._meta.description)

    def test_information(self):
        expected = ('https://canvas-medical.zendesk.com/hc/en-us/articles/360059083973-Annual-Wellness-Visit-HCC005v1')
        self.assertEqual(expected, Hcc005v1._meta.information)

    def test_change_types(self):
        result = Hcc005v1._meta.compute_on_change_types
        expected = [
            'protocol_override',
            'billing_line_item',
            'patient',
        ]
        self.assertEqual(len(expected), len(result))
        for change in expected:
            self.assertIn(change, result)

    def test_in_initial_population(self):
        start = arrow.get('2017-08-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)
        patient = self.load_patient('hcc005v1')
        tested = Hcc005v1(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.in_initial_population())

        start = arrow.get('2011-08-23 13:24:56')
        end = arrow.get('2012-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)
        patient = self.load_patient('hcc005v1')
        tested = Hcc005v1(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.in_initial_population())

    def test_in_denominator(self):
        start = arrow.get('2017-08-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)
        patient = self.load_patient('hcc005v1')
        tested = Hcc005v1(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.in_denominator())

        start = arrow.get('2011-08-23 13:24:56')
        end = arrow.get('2012-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)
        patient = self.load_patient('hcc005v1')
        tested = Hcc005v1(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.in_denominator())

    def test_in_numerator_patient_with_wellness_cpt(self):
        start = arrow.get('2017-08-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)

        tests = [
            ('G0437', True),
            ('G0438', False),
            ('G0439', False),
            ('G0402', False),
            ('99387', False),
            ('99397', False),
            ('99999', True),
        ]
        for code, expected in tests:
            patient = self.load_patient('hcc005v1')
            patient.billing_line_items = BillingLineItemRecordSet([{
                'id': 92,
                'created': '2018-07-13T21:41:21.407046Z',
                'cpt': code,
                'units': 1
            }])
            tested = Hcc005v1(patient=patient, timeframe=timeframe)
            if expected:
                self.assertTrue(tested.in_numerator())
            else:
                self.assertFalse(tested.in_numerator())

            patient = self.load_patient('hcc005v1')
            patient.billing_line_items = BillingLineItemRecordSet([{
                'id': 92,
                'created': '2017-07-13T21:41:21.407046Z',
                'cpt': code,
                'units': 1
            }])
            tested = Hcc005v1(patient=patient, timeframe=timeframe)
            self.assertTrue(tested.in_numerator())

    def test_in_numerator_patient_without_wellness_cpt(self):
        start = arrow.get('2017-08-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')

        timeframe = Timeframe(start=start, end=end)
        patient = self.load_patient('hcc005v1')
        tested = Hcc005v1(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.in_numerator())

    def test_compute_results_patient_with_wellness_cpt(self):
        start = arrow.get('2017-08-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        now = arrow.get('2018-12-15 13:24:56')
        timeframe = Timeframe(start=start, end=end)
        patient = self.load_patient('hcc005v1')
        patient.billing_line_items = BillingLineItemRecordSet([{
            'id': 92,
            'created': '2018-07-13T21:41:21.407046Z',
            'cpt': 'G0438',
            'units': 1
        }])
        tested = Hcc005v1(patient=patient, timeframe=timeframe, now=now)
        result = tested.compute_results()
        self.assertEqual('satisfied', result.status)
        text = r'^Jim had a visit [\w\s]+ on 7/13/18.$'
        self.assertRegex(result.narrative, text)
        self.assertEqual([], result.recommendations)
        self.assertEqual(210, result.due_in)

    def test_compute_results_patient_without_wellness_cpt(self):
        start = arrow.get('2017-08-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)
        patient = self.load_patient('hcc005v1')
        tested = Hcc005v1(patient=patient, timeframe=timeframe)
        result = tested.compute_results()
        self.assertEqual('due', result.status)
        text = ('Jim is due for a Annual Wellness Visit.\n'
                'There are no Annual Wellness Visits on record.')
        self.assertEqual(text, result.narrative)
        expected = [
            {
                'title': 'Schedule for Annual Wellness Visit',
                'command': {
                    'type': 'instruct',
                    'filter': {
                        'coding': [{'system': 'hcpcs', 'code': [
                            '99387',
                            '99397',
                            'G0402',
                            'G0438',
                            'G0439',
                        ], }]}},
                'key': 'HCC005v1_RECOMMEND_WELLNESS_VISIT',
                'rank': 1,
                'button': 'Plan',
            },
        ]  # yapf: disable
        self.helper_exam_recommended(expected, result.recommendations)
        self.assertEqual(-1, result.due_in)

    def test_compute_results_with_override(self):
        patient = self.load_patient('hcc005v1')
        patient.protocol_overrides = ProtocolOverrideRecordSet([{
            'protocolKey': 'Hcc005v1',
            'adjustment': {
                'reference': '2018-02-01T00:00:00Z',
                'cycleDays': 180
            },
            'snooze': None,
            'modified': '2018-03-15T12:32:54Z',
        }])  # yapf: disable
        patient.billing_line_items = BillingLineItemRecordSet([{
            'id': 92,
            'created': '2018-08-05T21:41:21.407046Z',
            'cpt': 'G0438',
            'units': 1
        }])
        # exam done within the last 180 days
        tested = Hcc005v1(patient=patient, now=arrow.get('2018-08-05').shift(days=80))
        result = tested.compute_results()
        self.assertEqual('satisfied', result.status)
        text = r'^Jim had a visit [\w\s]+ on 8/5/18.$'
        self.assertRegex(result.narrative, text)
        self.assertEqual(0, len(result.recommendations))
        self.assertEqual(100, result.due_in)

        # exam done 181 days
        tested = Hcc005v1(patient=patient, now=arrow.get('2018-08-05').shift(days=181))
        result = tested.compute_results()
        self.assertEqual('due', result.status)
        text = ('Jim is due for a Annual Wellness Visit.\n'
                'Last Annual Wellness Visit was 6 months ago on 8/5/18.')
        self.assertEqual(text, result.narrative)
        self.assertEqual(1, len(result.recommendations))
        self.assertEqual(-1, result.due_in)

    def helper_exam_recommended(self, expected, result):
        for exp, recommendation in zip(expected, result):
            self.assertEqual(exp['key'], recommendation.key)
            self.assertEqual(exp['rank'], recommendation.rank)
            self.assertEqual(exp['button'], recommendation.button)
            self.assertEqual(exp['title'], recommendation.title)
            self.assertEqual(exp['command']['type'], recommendation.command['type'])
            exp_item = exp['command']['filter']['coding']
            rec_item = recommendation.command['filter']['coding']
            self.assertEqual(len(exp_item), len(rec_item))
            for exp_coding, rec_coding in zip(exp_item, rec_item):
                self.assertEqual(exp_coding['system'], rec_coding['system'])
                self.assertEqual(sorted(exp_coding['code']), sorted(rec_coding['code']))
