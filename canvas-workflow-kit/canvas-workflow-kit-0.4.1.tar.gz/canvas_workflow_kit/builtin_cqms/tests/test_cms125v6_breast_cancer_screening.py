import arrow

from canvas_workflow_kit import settings

from canvas_workflow_kit.builtin_cqms.cms125v6_breast_cancer_screening import ClinicalQualityMeasure125v6
from canvas_workflow_kit.patient_recordset import BillingLineItemRecordSet, ProtocolOverrideRecordSet
from canvas_workflow_kit.tests.base import SDKBaseTest
from canvas_workflow_kit.timeframe import Timeframe


class TestClinicalQualityMeasure125v6(SDKBaseTest):

    def setUp(self):
        self.mocks_path = f'{settings.BASE_DIR}/builtin_cqms/tests/mock_data'

    def test_description(self):
        expected = ('Women 50-74 years of age who have not had a mammogram to screen for '
                    'breast cancer within the last 27 months.')
        self.assertEqual(expected, ClinicalQualityMeasure125v6._meta.description)

    def test_information(self):
        expected = 'https://ecqi.healthit.gov/sites/default/files/ecqm/measures/CMS125v6.html'
        self.assertEqual(expected, ClinicalQualityMeasure125v6._meta.information)

    def test_enabled(self):
        self.assertTrue(ClinicalQualityMeasure125v6.enabled())

    def test_version(self):
        self.assertTrue(hasattr(ClinicalQualityMeasure125v6._meta, 'version'))

    def test_change_types(self):
        result = ClinicalQualityMeasure125v6._meta.compute_on_change_types
        expected = [
            'protocol_override',
            'condition',
            'imaging_report',
            'patient',
        ]
        self.assertEqual(len(expected), len(result))
        for change in expected:
            self.assertIn(change, result)

    def test_had_mastectomy(self):
        start = arrow.get('2017-08-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)

        # patient is woman between 50-74 --> true
        patient = self.load_patient('cms125v6_woman_due')
        tested = ClinicalQualityMeasure125v6(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.had_mastectomy())

        # patient is woman had a bilateral mastectomy --> false
        patient = self.load_patient('cms125v6_woman_mastectomy')
        tested = ClinicalQualityMeasure125v6(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.had_mastectomy())

        # patient is woman had a two unilateral mastectomies --> false
        patient = self.load_patient('cms125v6_woman_mastectomy')
        patient.conditions[0]['coding'][0]['code'] = '172043006'
        tested = ClinicalQualityMeasure125v6(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.had_mastectomy())

        patient.conditions = patient.conditions + patient.conditions
        tested = ClinicalQualityMeasure125v6(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.had_mastectomy())

        # patient is woman had a unilateral mastectomy
        # + evidence of a right unilateral mastectomy --> false
        patient = self.load_patient('cms125v6_woman_mastectomy')
        patient.conditions[0]['coding'][0]['code'] = '172043006'
        tested = ClinicalQualityMeasure125v6(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.had_mastectomy())

        patient.conditions = patient.conditions + patient.conditions
        patient.conditions[0]['coding'][0]['code'] = '429242008'
        patient.conditions[1]['coding'][0]['code'] = '172043006'
        tested = ClinicalQualityMeasure125v6(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.had_mastectomy())

        # patient is woman had a unilateral mastectomy
        # + evidence of a left unilateral mastectomy --> false
        patient = self.load_patient('cms125v6_woman_mastectomy')
        patient.conditions[0]['coding'][0]['code'] = '172043006'
        tested = ClinicalQualityMeasure125v6(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.had_mastectomy())

        patient.conditions = patient.conditions + patient.conditions
        patient.conditions[0]['coding'][0]['code'] = '429242008'
        patient.conditions[1]['coding'][0]['code'] = '172043006'
        tested = ClinicalQualityMeasure125v6(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.had_mastectomy())

    def test_first_due_in(self):
        start = arrow.get('2017-08-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)

        # patient is woman + older than 50 --> none
        patient = self.load_patient('cms125v6_woman_due')
        patient.patient['birthDate'] = '1967-08-22'
        protocol = ClinicalQualityMeasure125v6(patient=patient, timeframe=timeframe)
        self.assertIsNone(protocol.first_due_in())

        # patient is woman + younger than 50 --> due in
        patient = self.load_patient('cms125v6_woman_due')
        patient.patient['birthDate'] = '1967-08-30'
        protocol = ClinicalQualityMeasure125v6(patient=patient, timeframe=timeframe)
        self.assertEqual(6, protocol.first_due_in())

        # patient is woman + younger than 50 + mastectomy--> none
        patient = self.load_patient('cms125v6_woman_mastectomy')
        patient.patient['birthDate'] = '1967-08-30'
        protocol = ClinicalQualityMeasure125v6(patient=patient, timeframe=timeframe)
        self.assertIsNone(protocol.first_due_in())

    def test_first_due_in_with_override(self):
        override = ProtocolOverrideRecordSet([{
            'protocolKey': 'CMS125v6',
            'adjustment': {
                'reference': '2018-02-01T00:00:00Z',
                'cycleDays': 180
            },
            'snooze': None,
            'modified': '2018-03-15T12:32:54Z',
        }])  # yapf: disable

        # patient is woman + older than 50 --> none
        patient = self.load_patient('cms125v6_woman_mammography')
        patient.protocol_overrides = override
        patient.patient['birthDate'] = '1967-07-22'
        tested = ClinicalQualityMeasure125v6(patient=patient, now=arrow.get('2018-08-05'))
        self.assertIsNone(tested.first_due_in())

        # patient is woman + younger than 50 --> due in
        patient = self.load_patient('cms125v6_woman_mammography')
        patient.protocol_overrides = override
        patient.patient['birthDate'] = '1967-08-11'
        tested = ClinicalQualityMeasure125v6(patient=patient, now=arrow.get('2018-08-05'))
        self.assertEqual(6, tested.first_due_in())

        # patient is woman + younger than 50 + mastectomy--> none
        patient = self.load_patient('cms125v6_woman_mastectomy')
        patient.protocol_overrides = override
        patient.patient['birthDate'] = '1967-08-30'
        tested = ClinicalQualityMeasure125v6(patient=patient, now=arrow.get('2018-08-05'))
        self.assertIsNone(tested.first_due_in())

    def test_in_initial_population(self):
        start = arrow.get('2017-08-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)

        # patient is woman between 50-74 --> true
        patient = self.load_patient('cms125v6_woman_due')
        tested = ClinicalQualityMeasure125v6(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.in_initial_population())

        patient.billing_line_items = BillingLineItemRecordSet([])
        tested = ClinicalQualityMeasure125v6(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.in_initial_population())
        tested = ClinicalQualityMeasure125v6(
            patient=patient, timeframe=timeframe, context='report')
        self.assertFalse(tested.in_initial_population())
        tested = ClinicalQualityMeasure125v6(
            patient=patient, timeframe=timeframe, context='guidance')
        self.assertTrue(tested.in_initial_population())

        # patient is not a woman
        patient = self.load_patient('cms125v6_woman_due')
        for sex in ['M', 'O', 'UNK']:
            patient.patient['sexAtBirth'] = sex
            tested = ClinicalQualityMeasure125v6(patient=patient, timeframe=timeframe)
            self.assertFalse(tested.in_initial_population())
        patient.patient['sexAtBirth'] = 'F'
        self.assertTrue(tested.in_initial_population())

        # patient is younger than 51
        patient.patient['birthDate'] = end.shift(years=-51, days=+1).format('YYYY-MM-DD')
        tested = ClinicalQualityMeasure125v6(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.in_initial_population())
        patient.patient['birthDate'] = end.shift(years=-51, days=-1).format('YYYY-MM-DD')
        self.assertTrue(tested.in_initial_population())

        # patient is older than 74
        patient.patient['birthDate'] = end.shift(years=-74, days=-1).format('YYYY-MM-DD')
        tested = ClinicalQualityMeasure125v6(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.in_initial_population())
        patient.patient['birthDate'] = end.shift(years=-74, days=+1).format('YYYY-MM-DD')
        self.assertTrue(tested.in_initial_population())

    def test_in_initial_population_with_override(self):
        override = ProtocolOverrideRecordSet([{
            'protocolKey': 'CMS125v6',
            'adjustment': {
                'reference': '2018-02-01T00:00:00Z',
                'cycleDays': 180
            },
            'snooze': None,
            'modified': '2018-03-15T12:32:54Z',
        }])  # yapf: disable

        # patient is woman between 50-74 --> true
        patient = self.load_patient('cms125v6_woman_due')
        patient.protocol_overrides = override
        tested = ClinicalQualityMeasure125v6(patient=patient, now=arrow.get('2018-08-05'))
        self.assertTrue(tested.in_initial_population())

        # patient is not a woman
        for sex in ['M', 'O', 'UNK']:
            patient.patient['sexAtBirth'] = sex
            tested = ClinicalQualityMeasure125v6(patient=patient, now=arrow.get('2018-08-05'))
            self.assertFalse(tested.in_initial_population())
        patient.patient['sexAtBirth'] = 'F'
        self.assertTrue(tested.in_initial_population())

        # patient is younger than 51
        patient.patient['birthDate'] = '1967-08-06'
        tested = ClinicalQualityMeasure125v6(patient=patient, now=arrow.get('2018-08-05'))
        self.assertFalse(tested.in_initial_population())
        patient.patient['birthDate'] = '1967-08-04'
        self.assertTrue(tested.in_initial_population())

        # patient is older than 74
        patient.patient['birthDate'] = '1944-08-04'
        tested = ClinicalQualityMeasure125v6(patient=patient, now=arrow.get('2018-08-05'))
        self.assertFalse(tested.in_initial_population())
        patient.patient['birthDate'] = '1944-08-06'
        self.assertTrue(tested.in_initial_population())

    def test_in_denominator(self):
        start = arrow.get('2017-08-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)

        # patient is woman between 50-74 --> true
        patient = self.load_patient('cms125v6_woman_due')
        tested = ClinicalQualityMeasure125v6(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.in_denominator())

        # patient is woman had a bilateral mastectomy --> false
        patient = self.load_patient('cms125v6_woman_mastectomy')
        tested = ClinicalQualityMeasure125v6(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.in_denominator())

        # patient is woman had a two unilateral mastectomies --> false
        patient = self.load_patient('cms125v6_woman_mastectomy')
        patient.conditions[0]['coding'][0]['code'] = '172043006'
        tested = ClinicalQualityMeasure125v6(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.in_denominator())

        patient.conditions = patient.conditions + patient.conditions
        tested = ClinicalQualityMeasure125v6(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.in_denominator())

        # patient is woman had a unilateral mastectomy
        # + evidence of a right unilateral mastectomy --> false
        patient = self.load_patient('cms125v6_woman_mastectomy')
        patient.conditions[0]['coding'][0]['code'] = '172043006'
        tested = ClinicalQualityMeasure125v6(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.in_denominator())

        patient.conditions = patient.conditions + patient.conditions
        patient.conditions[0]['coding'][0]['code'] = '429242008'
        patient.conditions[1]['coding'][0]['code'] = '172043006'
        tested = ClinicalQualityMeasure125v6(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.in_denominator())

        # patient is woman had a unilateral mastectomy
        # + evidence of a left unilateral mastectomy --> false
        patient = self.load_patient('cms125v6_woman_mastectomy')
        patient.conditions[0]['coding'][0]['code'] = '172043006'
        tested = ClinicalQualityMeasure125v6(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.in_denominator())

        patient.conditions = patient.conditions + patient.conditions
        patient.conditions[0]['coding'][0]['code'] = '429242008'
        patient.conditions[1]['coding'][0]['code'] = '172043006'
        tested = ClinicalQualityMeasure125v6(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.in_denominator())

    def test_in_numerator(self):
        start = arrow.get('2017-08-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)

        # patient is woman between 50-74 --> false
        patient = self.load_patient('cms125v6_woman_due')
        tested = ClinicalQualityMeasure125v6(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.in_numerator())

        # patient is woman between 50-74 + mammography --> true
        patient = self.load_patient('cms125v6_woman_mammography')
        tested = ClinicalQualityMeasure125v6(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.in_numerator())

        # patient is woman between 50-74 + mammography too old --> true
        patient = self.load_patient('cms125v6_woman_mammography')
        patient.imaging_reports[0]['originalDate'] = start.shift(months=-15).format('YYYY-MM-DD')
        tested = ClinicalQualityMeasure125v6(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.in_numerator())
        patient.imaging_reports[0]['originalDate'] = start.shift(
            months=-15, days=+1).format('YYYY-MM-DD')
        tested = ClinicalQualityMeasure125v6(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.in_numerator())

    def test_in_numerator_with_override(self):
        patient = self.load_patient('cms125v6_woman_mammography')
        patient.protocol_overrides = ProtocolOverrideRecordSet([{
            'protocolKey': 'ClinicalQualityMeasure125v6',
            'adjustment': {
                'reference': '2018-02-01T00:00:00Z',
                'cycleDays': 180
            },
            'snooze': None,
            'modified': '2018-03-15T12:32:54Z',
        }])  # yapf: disable
        patient.imaging_reports[0]['originalDate'] = '2018-08-05'

        tested = ClinicalQualityMeasure125v6(
            patient=patient, now=arrow.get('2018-08-05').shift(days=0))
        self.assertTrue(tested.in_numerator())

        tested = ClinicalQualityMeasure125v6(
            patient=patient, now=arrow.get('2018-08-05').shift(days=80))
        self.assertTrue(tested.in_numerator())

        tested = ClinicalQualityMeasure125v6(
            patient=patient, now=arrow.get('2018-08-05').shift(days=180))
        self.assertTrue(tested.in_numerator())

        tested = ClinicalQualityMeasure125v6(
            patient=patient, now=arrow.get('2018-08-05').shift(days=181))
        self.assertFalse(tested.in_numerator())

    def test_compute_results(self):
        start = arrow.get('2017-08-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        now = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)

        # patient is woman between 50-74 --> due
        patient = self.load_patient('cms125v6_woman_due')
        tested = ClinicalQualityMeasure125v6(patient=patient, timeframe=timeframe, now=now)
        result = tested.compute_results()
        self.assertEqual('due', result.status)
        self.assertEqual(
            result.narrative,
            'No relevant exams found.\nCurrent screening interval 2 years, 3 months.')
        expected = [
            {
                'title': 'Discuss breast cancer screening and order imaging as appropriate',
                'command': {
                    'type': 'instruct',
                    'filter': {
                        'coding': [
                            {
                                'system': 'hcpcs',
                                'code': ['G0206', 'G0202', 'G0204', ]
                            },
                            {
                                'system': 'loinc',
                                'code': [
                                    '37539-4', '37774-7', '24610-8', '37029-6', '37006-4',
                                    '26351-7', '36642-7',
                                    '26175-0', '37553-5', '39153-2', '46337-2', '26346-7',
                                    '46380-2', '48475-8',
                                    '24605-8', '42416-8', '24606-6', '46335-6', '42415-0',
                                    '26176-8', '48492-3',
                                    '38820-7', '38854-6', '26347-5', '69251-7', '46356-2',
                                    '26348-3', '36962-9',
                                    '46350-5', '37770-5', '37038-7', '39150-8', '46354-7',
                                    '38090-7', '69259-0',
                                    '26291-5', '38072-5', '26177-6', '38070-9', '26287-3',
                                    '24604-1', '46355-4',
                                    '42169-3', '37543-6', '36319-2', '26349-1', '46351-3',
                                    '46338-0', '36626-0',
                                    '37037-9', '37052-8', '39154-0', '37551-9', '37005-6',
                                    '38071-7', '26350-9',
                                    '37775-4', '26289-9', '37769-7', '42168-5', '42174-3',
                                    '46339-8', '69150-1',
                                    '38067-5', '38855-3', '38807-4', '37053-6', '37028-8',
                                    '37016-3', '37030-4',
                                    '37017-1', '37542-8', '37771-3', '37552-7', '37768-9',
                                    '39152-4', '46342-2',
                                    '38091-5', '36627-8', '37773-9', '37772-1', '46336-4',
                                    '37554-3', '36625-2',
                                ],
                            },
                        ],
                    },
                },
                'key': 'CMS125v6_RECOMMEND_MAMMOGRAPHY',
                'rank': 1,
                'button': 'Plan',
            },
        ]  # yapf: disable
        self.helper_exam_recommended(expected, result.recommendations)
        self.assertEqual(-1, result.due_in)

        # patient is woman between 50-74 + mammography --> satisfied
        patient = self.load_patient('cms125v6_woman_mammography')
        tested = ClinicalQualityMeasure125v6(patient=patient, timeframe=timeframe, now=now)
        result = tested.compute_results()
        self.assertEqual('satisfied', result.status)
        text = r'^Jane had a mammography [\w\s]+ on 7/30/18.$'
        self.assertRegex(result.narrative, text)
        self.assertEqual([], result.recommendations)
        self.assertEqual(797, result.due_in)

        # patient is woman had a two unilateral mastectomies --> N/A
        patient = self.load_patient('cms125v6_woman_mastectomy')
        tested = ClinicalQualityMeasure125v6(patient=patient, timeframe=timeframe, now=now)
        result = tested.compute_results()
        self.assertIsNotApplicable(result)

        # patient is woman under 50 without mastectomies -> N/A + due in
        patient = self.load_patient('cms125v6_woman_due')
        patient.patient['birthDate'] = '1967-12-23'
        tested = ClinicalQualityMeasure125v6(patient=patient, timeframe=timeframe, now=now)
        result = tested.compute_results()
        self.assertEqual('not_applicable', result.status)
        self.assertEqual(121, result.due_in)

        # patient is woman under 50 with mastectomies -> N/A
        patient = self.load_patient('cms125v6_woman_mastectomy')
        patient.patient['birthDate'] = '1967-12-23'
        tested = ClinicalQualityMeasure125v6(patient=patient, timeframe=timeframe, now=now)
        result = tested.compute_results()
        self.assertEqual('not_applicable', result.status)
        self.assertIsNone(result.due_in)

    def test_compute_results_with_override(self):
        patient = self.load_patient('cms125v6_woman_mammography')
        patient.protocol_overrides = ProtocolOverrideRecordSet([{
            'protocolKey': 'ClinicalQualityMeasure125v6',
            'adjustment': {
                'reference': '2018-02-01T00:00:00Z',
                'cycleDays': 180
            },
            'snooze': None,
            'modified': '2018-03-15T12:32:54Z',
        }])  # yapf: disable
        patient.imaging_reports[0]['originalDate'] = '2018-08-05'

        # mammography done within the last 180 days
        tested = ClinicalQualityMeasure125v6(
            patient=patient, now=arrow.get('2018-08-05').shift(days=176))
        result = tested.compute_results()
        self.assertEqual('satisfied', result.status)
        self.assertEqual('Jane had a mammography 5 months ago on 8/5/18.', result.narrative)
        self.assertEqual(0, len(result.recommendations))
        self.assertEqual(4, result.due_in)

        # mammography done 181 days after the 2018-02-01
        patient.billing_line_items[0]['created'] = '2018-08-10'  # visit within the 180-day period
        tested = ClinicalQualityMeasure125v6(
            patient=patient, now=arrow.get('2018-08-05').shift(days=181))
        result = tested.compute_results()
        self.assertEqual('due', result.status)
        self.assertEqual(result.narrative,
                         'No relevant exams found.\nCurrent screening interval 6 months.')
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
