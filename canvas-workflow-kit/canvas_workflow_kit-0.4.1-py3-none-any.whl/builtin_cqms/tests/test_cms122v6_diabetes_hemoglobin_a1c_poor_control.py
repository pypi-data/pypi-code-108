import arrow

from canvas_workflow_kit import settings

from canvas_workflow_kit.builtin_cqms.cms122v6_diabetes_hemoglobin_a1c_poor_control import (
    ClinicalQualityMeasure122v6
)
from canvas_workflow_kit.patient_recordset import (
    BillingLineItemRecordSet,
    LabReportRecordSet,
    ProtocolOverrideRecordSet
)
from canvas_workflow_kit.tests.base import SDKBaseTest
from canvas_workflow_kit.timeframe import Timeframe


class ClinicalQualityMeasure122v6Test(SDKBaseTest):

    def setUp(self):
        self.mocks_path = f'{settings.BASE_DIR}/builtin_cqms/tests/mock_data'

    def test_description(self):
        expected = (
            'Patients 18-75 years of age with diabetes who have either a hemoglobin A1c > 9.0% '
            'or no hemoglobin A1c within the last year.')
        self.assertEqual(expected, ClinicalQualityMeasure122v6._meta.description)

    def test_information(self):
        expected = 'https://ecqi.healthit.gov/sites/default/files/ecqm/measures/CMS122v6.html'
        self.assertEqual(expected, ClinicalQualityMeasure122v6._meta.information)

    def test_enabled(self):
        self.assertTrue(ClinicalQualityMeasure122v6.enabled())

        def test_version(self):
            self.assertTrue(hasattr(ClinicalQualityMeasure122v6._meta, 'version'))

    def test_change_types(self):
        result = ClinicalQualityMeasure122v6._meta.compute_on_change_types
        expected = [
            'protocol_override',
            'condition',
            'lab_report',
            'patient',
        ]
        self.assertEqual(len(expected), len(result))
        for change in expected:
            self.assertIn(change, result)

    def test_last_hba1c_record(self):
        start = arrow.get('2017-08-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)

        # patient has diabetes --> true
        patient = self.load_patient('cms122v6_diabetes_yeswithtest')
        tested = ClinicalQualityMeasure122v6(patient=patient, timeframe=timeframe)
        self.assertTrue('id' in tested.last_hba1c_record)
        self.assertEqual(644, tested.last_hba1c_record['id'])

        # patient has diabetes + already perform the exam --> true
        patient = self.load_patient('cms122v6_diabetes_yesnotest')
        tested = ClinicalQualityMeasure122v6(patient=patient, timeframe=timeframe)
        self.assertIsNone(tested.last_hba1c_record)

    def test_in_numerator_with_override(self):
        patient = self.load_patient('cms122v6_diabetes_yeswithtest')
        patient.protocol_overrides = ProtocolOverrideRecordSet([{
            'protocolKey': 'ClinicalQualityMeasure122v6',
            'adjustment': {
                'reference': '2018-02-01T00:00:00Z',
                'cycleDays': 180
            },
            'snooze': None,
            'modified': '2018-03-15T12:32:54Z',
        }])  # yapf: disable
        patient.lab_reports[0]['originalDate'] = '2018-08-05'

        tested = ClinicalQualityMeasure122v6(
            patient=patient, now=arrow.get('2018-08-05').shift(days=0))
        self.assertTrue('id' in tested.last_hba1c_record)
        self.assertEqual(644, tested.last_hba1c_record['id'])

        tested = ClinicalQualityMeasure122v6(
            patient=patient, now=arrow.get('2018-08-05').shift(days=80))
        self.assertTrue('id' in tested.last_hba1c_record)
        self.assertEqual(644, tested.last_hba1c_record['id'])

        tested = ClinicalQualityMeasure122v6(
            patient=patient, now=arrow.get('2018-08-05').shift(days=180))
        self.assertTrue('id' in tested.last_hba1c_record)
        self.assertEqual(644, tested.last_hba1c_record['id'])

        tested = ClinicalQualityMeasure122v6(
            patient=patient, now=arrow.get('2018-08-05').shift(days=181))
        self.assertIsNone(tested.last_hba1c_record)

    def test_last_hba1c_value(self):
        start = arrow.get('2017-08-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)

        # patient has diabetes --> true
        patient = self.load_patient('cms122v6_diabetes_yeswithtest')
        tested = ClinicalQualityMeasure122v6(patient=patient, timeframe=timeframe)
        self.assertEqual(7, tested.last_hba1c_value)

        # patient has diabetes + already perform the exam --> true
        patient = self.load_patient('cms122v6_diabetes_yesnotest')
        tested = ClinicalQualityMeasure122v6(patient=patient, timeframe=timeframe)
        self.assertIsNone(tested.last_hba1c_value)

        # patient with invalid value --> 0
        patient = self.load_patient('cms122v6_diabetes_yesnotest')
        patient.lab_reports = LabReportRecordSet([
            {
                'originalDate': '2018-08-02',
                'loincCodes': [{
                    'code': '17856-6',
                    'value': 644
                }],
                'value': 'asdf',
            },
        ])
        tested = ClinicalQualityMeasure122v6(patient=patient, timeframe=timeframe)
        self.assertEqual(0, tested.last_hba1c_value)

    def test_last_hba1c_date(self):
        start = arrow.get('2017-08-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)

        # patient has diabetes --> true
        patient = self.load_patient('cms122v6_diabetes_yeswithtest')
        tested = ClinicalQualityMeasure122v6(patient=patient, timeframe=timeframe)
        text = r'^[\w\s]+ on 8/2/18$'
        self.assertRegex(tested.last_hba1c_date, text)

        # patient has diabetes + already perform the exam --> true
        patient = self.load_patient('cms122v6_diabetes_yesnotest')
        tested = ClinicalQualityMeasure122v6(patient=patient, timeframe=timeframe)
        self.assertIsNone(tested.last_hba1c_date)

    def test_in_denominator(self):
        start = arrow.get('2017-08-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)

        # patient has no diabetes --> false
        patient = self.load_patient('cms122v6_diabetes_no')
        tested = ClinicalQualityMeasure122v6(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.in_denominator())

        # patient has diabetes --> true
        patient = self.load_patient('cms122v6_diabetes_yeswithtest')
        tested = ClinicalQualityMeasure122v6(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.in_denominator())

        # -- patient to young < 18 --> false
        patient = self.load_patient('cms122v6_diabetes_yeswithtest')
        patient.patient['birthDate'] = '2000-08-24'
        self.assertTrue(17 < patient.age_at(timeframe.end) < 18)
        tested = ClinicalQualityMeasure122v6(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.in_denominator())
        patient.patient['birthDate'] = '2000-08-23'
        self.assertTrue(patient.age_at(timeframe.end) == 18)
        tested = ClinicalQualityMeasure122v6(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.in_denominator())

        # -- patient to old > 75 --> false
        patient = self.load_patient('cms122v6_diabetes_yeswithtest')
        patient.patient['birthDate'] = '1943-08-22'
        self.assertTrue(75 < patient.age_at(timeframe.end) < 76)
        tested = ClinicalQualityMeasure122v6(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.in_denominator())
        patient.patient['birthDate'] = '1943-08-23'
        self.assertTrue(patient.age_at(timeframe.end) == 75)
        tested = ClinicalQualityMeasure122v6(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.in_denominator())
        patient.patient['birthDate'] = '1943-08-24'
        self.assertTrue(patient.age_at(timeframe.end) < 75)
        tested = ClinicalQualityMeasure122v6(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.in_denominator())

        # -- patient has an other code --> false
        patient = self.load_patient('cms122v6_diabetes_yeswithtest')
        for condition in patient.conditions:
            for code in condition['coding']:
                code['code'] = 'code'
        tested = ClinicalQualityMeasure122v6(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.in_denominator())

        # patient has diabetes + already perform the exam --> true
        patient = self.load_patient('cms122v6_diabetes_yeswithtest')
        tested = ClinicalQualityMeasure122v6(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.in_denominator())

    def test_in_numerator(self):
        start = arrow.get('2017-08-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)

        # not test when patient has no diabetes because it makes no sense
        # patient = self.load_patient('cms122v6_diabetes_no')

        # patient has diabetes + exam performed with value under 9 --> false
        patient = self.load_patient('cms122v6_diabetes_yeswithtest')
        tested = ClinicalQualityMeasure122v6(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.in_numerator())

        # patient has diabetes + exam performed with value equals to 9 --> false
        patient = self.load_patient('cms122v6_diabetes_yeswithtest')
        patient.lab_reports.records[0]['value'] = 9
        tested = ClinicalQualityMeasure122v6(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.in_numerator())

        # patient has diabetes + exam performed with value above 9 --> true
        patient = self.load_patient('cms122v6_diabetes_yeswithtest')
        patient.lab_reports.records[0]['value'] = 10
        tested = ClinicalQualityMeasure122v6(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.in_numerator())

        # patient has diabetes + no exam --> true
        patient = self.load_patient('cms122v6_diabetes_yesnotest')
        tested = ClinicalQualityMeasure122v6(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.in_numerator())

    def test_compute_results(self):
        start = arrow.get('2017-10-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        now = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)

        # patient has no diabetes --> n/a
        patient = self.load_patient('cms122v6_diabetes_no')
        tested = ClinicalQualityMeasure122v6(patient=patient, timeframe=timeframe, now=now)
        result = tested.compute_results()
        self.assertIsNotApplicable(result)

        # patient has diabetes + exam performed with value under 9 --> satisfied
        patient = self.load_patient('cms122v6_diabetes_yeswithtest')
        tested = ClinicalQualityMeasure122v6(patient=patient, timeframe=timeframe, now=now)
        result = tested.compute_results()
        self.assertEqual('satisfied', result.status)
        text = r"^Dohav's last HbA1c done [\w\s]+ on 8/2/18 was 7.0%.$"
        self.assertRegex(result.narrative, text)
        self.assertEqual([], result.recommendations)
        self.assertEqual(282, result.due_in)  # not one year since the time frame define the period

        # patient has diabetes + exam performed with value above 9 --> due
        patient = self.load_patient('cms122v6_diabetes_yeswithtest')
        patient.lab_reports.records[0]['value'] = 11.23
        tested = ClinicalQualityMeasure122v6(patient=patient, timeframe=timeframe, now=now)
        result = tested.compute_results()
        self.assertEqual('due', result.status)
        text = r"^Dohav's last HbA1c done [\w\s]+ on 8/2/18 was 11.2%.$"
        self.assertRegex(result.narrative, text)
        expected = [{
            'title': (
                'Discuss lifestyle modification and medication adherence.'
                ' Consider diabetes education and medication intensification as appropriate.'),
            'command': {
                'type': 'instruct',
                'filter': {
                    'coding': [
                        {
                            'system': 'hcpcs',
                            'code': ['S9452', 'S9470']
                        }, {
                            'system': 'icd10cm',
                            'code': ['Z713']
                        }, {
                            'system': 'icd9cm',
                            'code': ['V653']
                        },
                        {
                            'system': 'snomedct',
                            'code': [
                                '304491008', '410177006', '418995006', '410270001', '182922004',
                                '183065007', '370847001', '386464006', '182955009', '182960008',
                                '182954008', '410171007', '306163007', '284352003', '424753004',
                                '103699006', '182956005', '281085002', '183071001', '183061003',
                                '11816003', '61310001', '410114009', '183070000', '443288003',
                                '361231003', '413315001', '284071006'
                            ]
                        }
                    ]
                }
            },
            'key': 'CMS122v6_RECOMMEND_DISCUSS_LIFESTYLE',
            'rank': 1,
            'button': 'Instruct',
        }]
        # self.assertEqual(recommendations, result.recommendations)
        self.helper_compare_recommendations(expected, result.recommendations)
        self.assertEqual(-1, result.due_in)

        # patient has diabetes + no exam --> due
        patient = self.load_patient('cms122v6_diabetes_yesnotest')
        tested = ClinicalQualityMeasure122v6(patient=patient, timeframe=timeframe, now=now)
        result = tested.compute_results()
        self.assertEqual('due', result.status)
        text = "Dohav's last HbA1c test was over 10 months."
        self.assertEqual(text, result.narrative)
        expected = [
            {
                'title': 'Order HbA1c',
                'command': {
                    'type': 'labOrder',
                    'filter': {
                        'coding': [{
                            'system': 'loinc',
                            'code': ['4548-4', '17856-6', '4549-2']
                        }]
                    }
                },
                'key': 'CMS122v6_RECOMMEND_HBA1C',
                'rank': 1,
                'button': 'Order',
            },
        ]
        self.helper_compare_recommendations(expected, result.recommendations)
        self.assertEqual(-1, result.due_in)

        # patient has diabetes + younger than 18 --> n/a + due in
        patient = self.load_patient('cms122v6_diabetes_no')
        patient.patient['birthDate'] = '2000-08-30'
        tested = ClinicalQualityMeasure122v6(patient=patient, timeframe=timeframe, now=now)
        result = tested.compute_results()
        self.assertEqual('not_applicable', result.status)
        self.assertIsNone(result.due_in)
        patient = self.load_patient('cms122v6_diabetes_yesnotest')
        patient.patient['birthDate'] = '2000-08-30'
        tested = ClinicalQualityMeasure122v6(patient=patient, timeframe=timeframe, now=now)
        result = tested.compute_results()
        self.assertEqual('not_applicable', result.status)
        self.assertEqual(6, result.due_in)

    def test_compute_results_with_override(self):
        patient = self.load_patient('cms122v6_diabetes_yeswithtest')
        patient.protocol_overrides = ProtocolOverrideRecordSet([{
            'protocolKey': 'ClinicalQualityMeasure122v6',
            'adjustment': {
                'reference': '2018-02-01T00:00:00Z',
                'cycleDays': 180
            },
            'snooze': None,
            'modified': '2018-03-15T12:32:54Z',
        }])  # yapf: disable
        patient.lab_reports[0]['originalDate'] = '2018-08-05'

        # exam done within the last 180 days
        tested = ClinicalQualityMeasure122v6(
            patient=patient, now=arrow.get('2018-08-05').shift(days=80))
        result = tested.compute_results()
        self.assertEqual('satisfied', result.status)
        text = "Dohav's last HbA1c done 2 months ago on 8/5/18 was 7.0%."
        self.assertEqual(text, result.narrative)
        self.assertEqual(0, len(result.recommendations))
        self.assertEqual(100, result.due_in)

        # exam done 181 days
        patient.billing_line_items = BillingLineItemRecordSet([{
            'id': 92,
            'created': arrow.get('2018-08-01').shift(days=181),
            'cpt': '99202',
            'units': 1
        }])
        tested = ClinicalQualityMeasure122v6(
            patient=patient, now=arrow.get('2018-08-05').shift(days=181))
        result = tested.compute_results()
        self.assertEqual('due', result.status)
        text = "Dohav's last HbA1c test was over 6 months."
        self.assertEqual(text, result.narrative)
        self.assertEqual(1, len(result.recommendations))
        self.assertEqual(-1, result.due_in)

    def helper_compare_recommendations(self, expected, result):
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
