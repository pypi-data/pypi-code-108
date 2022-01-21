import arrow

from canvas_workflow_kit import settings

from canvas_workflow_kit.builtin_cqms.hcc001v1_problem_list_hygiene import Hcc001v1
from canvas_workflow_kit.patient_recordset import ConditionRecordSet, ProtocolOverrideRecordSet
from canvas_workflow_kit.tests.base import SDKBaseTest
from canvas_workflow_kit.timeframe import Timeframe


class TestCanvasHcc001v1(SDKBaseTest):

    def setUp(self):
        self.mocks_path = f'{settings.BASE_DIR}/builtin_cqms/tests/mock_data'

    def test_enabled(self):
        self.assertTrue(Hcc001v1.enabled())

    def test_description(self):
        expected = ('All patients with active condition not assessed within the last year.')
        self.assertEqual(expected, Hcc001v1._meta.description)

    def test_information(self):
        expected = ('https://canvas-medical.zendesk.com/hc/en-us/articles/360059083693-Problem-List-Hygiene-HCC001v1')
        self.assertEqual(expected, Hcc001v1._meta.information)

    def test_change_types(self):
        result = Hcc001v1._meta.compute_on_change_types
        expected = [
            'protocol_override',
            'condition',
        ]
        self.assertEqual(len(expected), len(result))
        for change in expected:
            self.assertIn(change, result)

    def test_active_hcc(self):
        start = arrow.get('2017-08-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)

        # patient has a active condition in HCC
        patient = self.load_patient('hcc001v1')
        tested = Hcc001v1(patient=patient, timeframe=timeframe)
        result = tested.active_hcc

        self.assertEqual(1, len(result))
        self.assertEqual('I429', result[0]['ICD10'])
        self.assertEqual('2018-08-22 23:08:00', result[0]['date'].format('YYYY-MM-DD HH:MM:SS'))

        patient.conditions = patient.conditions + patient.conditions + patient.conditions
        tested = Hcc001v1(patient=patient, timeframe=timeframe)
        result = tested.active_hcc

        self.assertEqual(3, len(result))

        # patient has NO active condition in HCC
        patient = self.load_patient('hcc001v1')
        patient.conditions[0]['clinicalStatus'] = 'XXXXXXXX'
        tested = Hcc001v1(patient=patient, timeframe=timeframe)
        result = tested.active_hcc

        self.assertEqual(0, len(result))

        # patient has a condition NOT in HCC
        patient = self.load_patient('hcc001v1')
        patient.conditions[0]['coding'][0]['code'] = 'XXXXXXXX'
        patient.conditions[0]['coding'][1]['code'] = 'XXXXXXXX'
        tested = Hcc001v1(patient=patient, timeframe=timeframe)
        result = tested.active_hcc

        self.assertEqual(0, len(result))

        # patient has NO condition
        patient = self.load_patient('hcc001v1')
        patient.conditions = ConditionRecordSet([])
        tested = Hcc001v1(patient=patient, timeframe=timeframe)
        result = tested.active_hcc

        self.assertEqual(0, len(result))

    def test_too_old_hccs(self):
        patient = self.load_patient('hcc001v1')
        patient.conditions = ConditionRecordSet([
            {
                'coding': [{'system': 'ICD-10', 'code': 'I427', }],
                'clinicalStatus': 'active',
                'periods': [{'from': '2018-05-22', 'to': None}],
                'lastTimestamps': {'assessed': '2017-08-22 13:24:56', },
            },
            {
                'coding': [{'system': 'ICD-10', 'code': 'I428', }],
                'clinicalStatus': 'active',
                'periods': [{'from': '2018-05-22', 'to': None}],
                'lastTimestamps': {'assessed': '2017-07-21 13:24:56', },
            },
            {
                'coding': [{'system': 'ICD-10', 'code': 'I429', }],
                'clinicalStatus': 'active',
                'periods': [{'from': '2018-05-22', 'to': None}],
                'lastTimestamps': {'assessed': '2017-09-22 13:24:56', },
            },
        ])  # yapf: disable

        # no adjustment
        start = arrow.get('2017-08-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)

        tested = Hcc001v1(patient=patient, timeframe=timeframe)
        result = tested.too_old_hccs
        expected = [
            'I427',
            'I428',
        ]
        self.assertEqual(len(expected), len(result))
        for item in result:
            self.assertIn(item['ICD10'], expected)

        # with adjustment
        patient.protocol_overrides = ProtocolOverrideRecordSet([{
            'protocolKey': 'Hcc001v1',
            'adjustment': {
                'reference': '2018-02-01T00:00:00Z',
                'cycleDays': 180
            },
            'snooze': None,
            'modified': '2018-03-15T12:32:54Z',
        }])  # yapf: disable
        tested = Hcc001v1(patient=patient, now=arrow.get('2018-02-01').shift(days=20))
        result = tested.too_old_hccs
        expected = [
            'I427',
            'I428',
        ]
        self.assertEqual(len(expected), len(result))
        for item in result:
            self.assertIn(item['ICD10'], expected)
        tested = Hcc001v1(patient=patient, now=arrow.get('2018-02-01').shift(days=80))
        result = tested.too_old_hccs
        expected = [
            'I427',
            'I428',
            'I429',
        ]
        self.assertEqual(len(expected), len(result))
        for item in result:
            self.assertIn(item['ICD10'], expected)

    def test_in_initial_population(self):
        start = arrow.get('2017-08-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)

        # any patient --> true
        patient = self.load_patient('hcc001v1')
        tested = Hcc001v1(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.in_initial_population())

        patient.conditions = []
        tested = Hcc001v1(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.in_initial_population())

    def test_in_denominator(self):
        start = arrow.get('2017-08-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)

        # patient has a active condition in HCC --> true
        patient = self.load_patient('hcc001v1')
        tested = Hcc001v1(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.in_denominator())

        # patient has NO active condition in HCC --> true
        patient = self.load_patient('hcc001v1')
        patient.conditions[0]['clinicalStatus'] = 'XXXXXXXX'
        tested = Hcc001v1(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.in_denominator())

        # patient has a condition NOT in HCC --> false
        patient = self.load_patient('hcc001v1')
        patient.conditions[0]['coding'][0]['code'] = 'XXXXXXXX'
        patient.conditions[0]['coding'][1]['code'] = 'XXXXXXXX'
        tested = Hcc001v1(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.in_denominator())

        # patient has NO condition --> false
        patient = self.load_patient('hcc001v1')
        patient.conditions = ConditionRecordSet([])
        tested = Hcc001v1(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.in_denominator())

    def test_in_numerator(self):
        start = arrow.get('2017-08-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)

        # patient has a condition in HCC that is assessed within the year --> false
        patient = self.load_patient('hcc001v1')
        tested = Hcc001v1(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.in_numerator())

        # patient has a condition in HCC that is NOT assessed within the year --> true
        patient = self.load_patient('hcc001v1')
        patient.conditions[0]['noteTimestamp'] = '2018-08-22 13:24:56'
        patient.conditions[0]['lastTimestamps']['assessed'] = '2017-08-22 13:24:56'
        tested = Hcc001v1(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.in_numerator())

        # patient has a condition in HCC that is assessed within the year --> false
        patient = self.load_patient('hcc001v1')
        patient.conditions[0]['noteTimestamp'] = '2018-08-22 13:24:56'
        patient.conditions[0]['lastTimestamps']['assessed'] = None
        tested = Hcc001v1(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.in_numerator())

        # patient has a condition in HCC that is NOT assessed within the year --> true
        patient = self.load_patient('hcc001v1')
        patient.conditions[0]['noteTimestamp'] = '2017-08-22 13:24:56'
        patient.conditions[0]['lastTimestamps']['assessed'] = None
        tested = Hcc001v1(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.in_numerator())

        # patient has a condition NOT in HCC that is NOT assessed within the year --> false
        patient = self.load_patient('hcc001v1')
        patient.conditions[0]['lastTimestamps']['assessed'] = '2017-08-22 13:24:56'
        patient.conditions[0]['coding'][0]['code'] = 'XXXXXXXX'
        patient.conditions[0]['coding'][1]['code'] = 'XXXXXXXX'
        tested = Hcc001v1(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.in_numerator())

    def test_in_numerator_with_override(self):
        patient = self.load_patient('hcc001v1')
        patient.protocol_overrides = ProtocolOverrideRecordSet([{
            'protocolKey': 'Hcc001v1',
            'adjustment': {
                'reference': '2018-02-01T00:00:00Z',
                'cycleDays': 180
            },
            'snooze': None,
            'modified': '2018-03-15T12:32:54Z',
        }])  # yapf: disable
        patient.conditions[0]['noteTimestamp'] = '2002-08-22 13:24:56'
        patient.conditions[0]['lastTimestamps']['assessed'] = '2018-08-05 13:24:56'

        tested = Hcc001v1(patient=patient, now=arrow.get('2018-08-05').shift(days=1))
        self.assertFalse(tested.in_numerator())

        tested = Hcc001v1(patient=patient, now=arrow.get('2018-08-05').shift(days=80))
        self.assertFalse(tested.in_numerator())

        tested = Hcc001v1(patient=patient, now=arrow.get('2018-08-05').shift(days=180))
        self.assertFalse(tested.in_numerator())

        tested = Hcc001v1(patient=patient, now=arrow.get('2018-08-05').shift(days=181))
        self.assertTrue(tested.in_numerator())

    def test_compute_results(self):
        start = arrow.get('2017-09-23 13:24:56')
        end = arrow.get('2018-09-23 13:24:56')
        now = arrow.get('2018-09-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)

        # patient has a active condition in HCC assessed within the year --> satisfied
        patient = self.load_patient('hcc001v1')
        tested = Hcc001v1(patient=patient, timeframe=timeframe, now=now)
        result = tested.compute_results()
        self.assertEqual('satisfied', result.status)
        text = 'All Significant Condition have been assessed within the last 12 months.'
        self.assertEqual(text, result.narrative)
        self.assertEqual([], result.recommendations)
        self.assertEqual(333, result.due_in)

        patient.conditions = ConditionRecordSet([
            {
                'coding': [{'system': 'ICD-10', 'code': 'I429', }],
                'clinicalStatus': 'active',
                'periods': [{'from': '2018-05-22', 'to': None}],
                'lastTimestamps': {'assessed': '2018-07-22 13:24:56', },
            },
            {
                'coding': [{'system': 'ICD-10', 'code': 'I429', }],
                'clinicalStatus': 'active',
                'periods': [{'from': '2018-05-22', 'to': None}],
                'lastTimestamps': {'assessed': '2018-06-21 13:24:56', },
            },
            {
                'coding': [{'system': 'ICD-10', 'code': 'I429', }],
                'clinicalStatus': 'active',
                'periods': [{'from': '2018-05-22', 'to': None}],
                'lastTimestamps': {'assessed': '2018-08-22 13:24:56', },
            },
        ])  # yapf: disable
        tested = Hcc001v1(patient=patient, timeframe=timeframe, now=now)
        result = tested.compute_results()
        self.assertEqual(271, result.due_in)

        # patient has a active condition in HCC NOT assessed within the year --> due
        patient = self.load_patient('hcc001v1')
        tested = Hcc001v1(patient=patient, timeframe=timeframe, now=now)
        patient.conditions[0]['lastTimestamps']['assessed'] = '2017-09-22 13:24:56'
        result = tested.compute_results()
        self.assertEqual('due', result.status)
        text = ('Cardiomyopathy, unspecified (I429) is a significant condition '
                'which should be assessed annually.'
                ' The condition was last assessed on 9/22/17 and carries a RAF value of 0.368')
        self.assertEqual(text, result.narrative)
        expected = [
            {
                'title': 'Assess, update or resolve conditions as clinically appropriate',
                'command': {
                    'key': 'assess'
                },
                'key': 'HCC001v1_RECOMMEND_ASSESS_CONDITION',
                'rank': 1,
                'button': 'Assess',
            }, {
                'title': 'Resolve conditions as clinically appropriate',
                'command': {
                    'key': 'resolveCondition'
                },
                'key': 'HCC001v1_RECOMMEND_RESOLVE_CONDITION',
                'rank': 2,
                'button': 'Assess',
            },
        ]  # yapf: disable
        self.helper_exam_recommended(expected, result.recommendations)
        self.assertEqual(-1, result.due_in)

        # patient has NO condition --> false
        patient = self.load_patient('hcc001v1')
        patient.conditions = ConditionRecordSet([])
        tested = Hcc001v1(patient=patient, timeframe=timeframe, now=now)
        result = tested.compute_results()
        self.assertIsNotApplicable(result)

    def test_compute_results_with_override(self):
        patient = self.load_patient('hcc001v1')
        patient.protocol_overrides = ProtocolOverrideRecordSet([{
            'protocolKey': 'Hcc001v1',
            'adjustment': {
                'reference': '2018-02-01T00:00:00Z',
                'cycleDays': 180
            },
            'snooze': None,
            'modified': '2018-03-15T12:32:54Z',
        }])  # yapf: disable
        patient.conditions[0]['noteTimestamp'] = '2002-08-22 13:24:56'
        patient.conditions[0]['lastTimestamps']['assessed'] = '2018-08-05 13:24:56'

        # assessment done within the last 180 days
        tested = Hcc001v1(patient=patient, now=arrow.get('2018-08-05').shift(days=80))
        result = tested.compute_results()
        self.assertEqual('satisfied', result.status)
        text = 'All Significant Condition have been assessed within the last 6 months.'
        self.assertEqual(text, result.narrative)
        self.assertEqual(0, len(result.recommendations))
        self.assertEqual(100, result.due_in)

        # assessment done 181 days ago
        tested = Hcc001v1(patient=patient, now=arrow.get('2018-08-05').shift(days=181))
        result = tested.compute_results()
        self.assertEqual('due', result.status)
        text = ('Cardiomyopathy, unspecified (I429) is a significant condition '
                'which should be assessed annually. The condition was last assessed '
                'on 8/5/18 and carries a RAF value of 0.368')
        self.assertEqual(text, result.narrative)
        self.assertEqual(2, len(result.recommendations))
        self.assertEqual(-1, result.due_in)

    def helper_exam_recommended(self, expected, result):
        for exp, recommendation in zip(expected, result):
            self.assertEqual(exp['key'], recommendation.key)
            self.assertEqual(exp['rank'], recommendation.rank)
            self.assertEqual(exp['button'], recommendation.button)
            self.assertEqual(exp['title'], recommendation.title)
            self.assertEqual(exp['command']['key'], recommendation.command['key'])
