import arrow

from canvas_workflow_kit import settings

from canvas_workflow_kit.builtin_cqms.cms134v6_diabetes_medical_attention_for_nephropathy import (
    ClinicalQualityMeasure134v6
)
from canvas_workflow_kit.patient_recordset import (
    BillingLineItemRecordSet,
    InstructionRecordSet,
    MedicationRecordSet,
    ProtocolOverrideRecordSet,
    ReferralReportRecordSet
)
from canvas_workflow_kit.tests.base import SDKBaseTest
from canvas_workflow_kit.timeframe import Timeframe


class ClinicalQualityMeasure134v6Test(SDKBaseTest):

    def setUp(self):
        self.mocks_path = f'{settings.BASE_DIR}/builtin_cqms/tests/mock_data'

    def test_enabled(self):
        self.assertTrue(ClinicalQualityMeasure134v6.enabled())

    def test_description(self):
        expected = (
            'Patients 18-75 years of age with diabetes who have not had a nephropathy screening '
            'test in the last year or evidence of nephropathy.')
        self.assertEqual(expected, ClinicalQualityMeasure134v6._meta.description)

    def test_information(self):
        expected = 'https://ecqi.healthit.gov/sites/default/files/ecqm/measures/CMS134v6.html'
        self.assertEqual(expected, ClinicalQualityMeasure134v6._meta.information)

    def test_version(self):
        self.assertTrue(hasattr(ClinicalQualityMeasure134v6._meta, 'version'))

    def test_change_types(self):
        result = ClinicalQualityMeasure134v6._meta.compute_on_change_types
        expected = [
            'protocol_override',
            'condition',
            'instruction',
            'lab_report',
            'medication',
            'referral_report',
            'patient',
        ]
        self.assertEqual(len(expected), len(result))
        for change in expected:
            self.assertIn(change, result)

    def test_in_numerator_with_override(self):
        patient = self.load_patient('cms134v6_diabetes_yes')
        patient.protocol_overrides = ProtocolOverrideRecordSet([{
            'protocolKey': 'ClinicalQualityMeasure134v6',
            'adjustment': {
                'reference': '2018-02-01T00:00:00Z',
                'cycleDays': 180
            },
            'snooze': None,
            'modified': '2018-03-15T12:32:54Z',
        }])  # yapf: disable
        patient.lab_reports[0]['originalDate'] = '2018-08-10'

        tested = ClinicalQualityMeasure134v6(
            patient=patient, now=arrow.get('2018-08-15').shift(days=0))
        self.assertTrue(tested.in_numerator())
        expected = r'^Dohav has diabetes and had a Dialysis Related Service [\w\s]+ on 7/26/18'
        self.assertRegex(tested.message, expected)
        self.assertEqual(-1, tested._due_in)

        tested = ClinicalQualityMeasure134v6(
            patient=patient, now=arrow.get('2018-08-15').shift(days=80))
        self.assertTrue(tested.in_numerator())
        expected = r'^Dohav has diabetes and had a Dialysis Related Service [\w\s]+ on 7/26/18'
        self.assertRegex(tested.message, expected)
        self.assertEqual(-1, tested._due_in)

        del (patient.conditions.records[1])
        patient.referral_reports = ReferralReportRecordSet([])
        patient.medications = MedicationRecordSet([])
        patient.instructions = InstructionRecordSet([])

        tested = ClinicalQualityMeasure134v6(
            patient=patient, now=arrow.get('2018-08-15').shift(days=0))
        self.assertTrue(tested.in_numerator())
        expected = r'^Dohav has diabetes and a urine protein test was done [\w\s]+ on 8/10/18'
        self.assertRegex(tested.message, expected)
        self.assertEqual(175, tested._due_in)

        tested = ClinicalQualityMeasure134v6(
            patient=patient, now=arrow.get('2018-08-15').shift(days=80))
        self.assertTrue(tested.in_numerator())
        self.assertEqual(95, tested._due_in)

        tested = ClinicalQualityMeasure134v6(
            patient=patient, now=arrow.get('2018-08-15').shift(days=175))
        self.assertTrue(tested.in_numerator())
        self.assertEqual(0, tested._due_in)

        tested = ClinicalQualityMeasure134v6(
            patient=patient, now=arrow.get('2018-08-15').shift(days=176))
        self.assertFalse(tested.in_numerator())
        self.assertEqual(-1, tested._due_in)

    def test_in_denominator(self):
        start = arrow.get('2017-08-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)

        # patient has no diabetes --> false
        patient = self.load_patient('cms134v6_diabetes_no')
        tested = ClinicalQualityMeasure134v6(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.in_denominator())

        # patient has diabetes --> true
        patient = self.load_patient('cms134v6_diabetes_yes')
        tested = ClinicalQualityMeasure134v6(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.in_denominator())

        # -- patient to young < 18 --> false
        patient = self.load_patient('cms134v6_diabetes_yes')
        patient.patient['birthDate'] = '2000-08-24'
        self.assertTrue(17 < patient.age_at(timeframe.end) < 18)
        tested = ClinicalQualityMeasure134v6(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.in_denominator())
        patient.patient['birthDate'] = '2000-08-23'
        self.assertTrue(patient.age_at(timeframe.end) == 18)
        tested = ClinicalQualityMeasure134v6(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.in_denominator())

        # -- patient to old > 75 --> false
        patient = self.load_patient('cms134v6_diabetes_yes')
        patient.patient['birthDate'] = '1943-08-22'
        self.assertTrue(75 < patient.age_at(timeframe.end) < 76)
        tested = ClinicalQualityMeasure134v6(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.in_denominator())
        patient.patient['birthDate'] = '1943-08-23'
        self.assertTrue(patient.age_at(timeframe.end) == 75)
        tested = ClinicalQualityMeasure134v6(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.in_denominator())
        patient.patient['birthDate'] = '1943-08-24'
        self.assertTrue(patient.age_at(timeframe.end) < 75)
        tested = ClinicalQualityMeasure134v6(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.in_denominator())

        # -- patient has an other code --> false
        patient = self.load_patient('cms134v6_diabetes_yes')
        for condition in patient.conditions:
            for code in condition['coding']:
                code['code'] = 'code'
        tested = ClinicalQualityMeasure134v6(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.in_denominator())

    def test_in_numerator(self):
        now = arrow.get('2018-12-06 13:24:56')
        start = arrow.get('2017-08-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)

        # not test when patient has no diabetes because it makes no sense

        # referral report
        patient = self.load_patient('cms134v6_diabetes_yes')
        tested = ClinicalQualityMeasure134v6(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.in_numerator())
        expected = r'^Dohav has diabetes and had a Dialysis Related Service [\w\s]+ on 7/26/18'
        self.assertRegex(tested.message, expected)
        self.assertEqual(-1, tested._due_in)

        # medication
        patient.referral_reports = ReferralReportRecordSet([])
        tested = ClinicalQualityMeasure134v6(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.in_numerator())
        expected = 'Dohav has diabetes and is under Ace Inhibitors medication'
        self.assertEqual(expected, tested.message)
        self.assertEqual(-1, tested._due_in)

        # conditions - HypertensiveChronicKidneyDisease
        patient.medications = MedicationRecordSet([])

        patient.conditions.records[1]['coding'][0]['code'] = 'I129'
        tested = ClinicalQualityMeasure134v6(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.in_numerator())
        expected = 'Dohav has diabetes and has been diagnosed Hypertensive Chronic Kidney Disease'
        self.assertEqual(expected, tested.message)
        self.assertEqual(-1, tested._due_in)

        patient.conditions.records[1]['coding'][0]['code'] = 'N170'
        tested = ClinicalQualityMeasure134v6(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.in_numerator())
        expected = 'Dohav has diabetes and has been diagnosed Kidney Failure'
        self.assertEqual(expected, tested.message)
        self.assertEqual(-1, tested._due_in)

        patient.conditions.records[1]['coding'][0]['code'] = 'N000'
        tested = ClinicalQualityMeasure134v6(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.in_numerator())
        expected = ('Dohav has diabetes and has been diagnosed Glomerulonephritis '
                    'and Nephrotic Syndrome')
        self.assertEqual(expected, tested.message)
        self.assertEqual(-1, tested._due_in)

        patient.conditions.records[1]['coding'][0]['code'] = 'E0829'
        tested = ClinicalQualityMeasure134v6(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.in_numerator())
        expected = 'Dohav has diabetes and has been diagnosed Diabetic Nephropathy'
        self.assertEqual(expected, tested.message)
        self.assertEqual(-1, tested._due_in)

        patient.conditions.records[1]['coding'][0]['code'] = 'R808'
        tested = ClinicalQualityMeasure134v6(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.in_numerator())
        expected = 'Dohav has diabetes and has been diagnosed Proteinuria'
        self.assertEqual(expected, tested.message)
        self.assertEqual(-1, tested._due_in)

        patient.conditions.records[1]['coding'][0]['system'] = 'http://snomed.info/sct'
        patient.conditions.records[1]['coding'][0]['code'] = '175901007'
        tested = ClinicalQualityMeasure134v6(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.in_numerator())
        expected = 'Dohav has diabetes and had a Kidney Transplant'
        self.assertEqual(expected, tested.message)
        self.assertEqual(-1, tested._due_in)

        # instructions
        del (patient.conditions.records[1])
        tested = ClinicalQualityMeasure134v6(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.in_numerator())
        expected = (r'^Dohav has diabetes and had an ESRD Monthly Outpatient Services [\w\s]+ '
                    'on 7/6/18')
        self.assertRegex(tested.message, expected)
        self.assertEqual(-1, tested._due_in)

        # lab report
        patient.instructions = InstructionRecordSet([])
        tested = ClinicalQualityMeasure134v6(patient=patient, timeframe=timeframe, now=now)
        self.assertTrue(tested.in_numerator())
        expected = r'^Dohav has diabetes and a urine protein test was done [\w\s]+ on 8/5/18'
        self.assertRegex(tested.message, expected)
        self.assertEqual(241, tested._due_in)

    def test_compute_results(self):
        start = arrow.get('2017-10-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        now = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)

        # patient has no diabetes --> n/a
        patient = self.load_patient('cms134v6_diabetes_no')
        tested = ClinicalQualityMeasure134v6(patient=patient, timeframe=timeframe, now=now)
        result = tested.compute_results()
        self.assertIsNotApplicable(result)

        # patient has diabetes --> satisfied
        patient = self.load_patient('cms134v6_diabetes_yes')
        tested = ClinicalQualityMeasure134v6(patient=patient, timeframe=timeframe, now=now)
        result = tested.compute_results()
        self.assertEqual('satisfied', result.status)
        text = r'^Dohav has diabetes and had a Dialysis Related Service [\w\s]+ on 7/26/18$'
        self.assertRegex(result.narrative, text)
        self.assertEqual([], result.recommendations)
        self.assertEqual(-1, result.due_in)

        # patient has diabetes --> satisfied
        patient = self.load_patient('cms134v6_diabetes_yes')

        del (patient.conditions.records[1])
        patient.referral_reports = ReferralReportRecordSet([])
        patient.medications = MedicationRecordSet([])
        patient.instructions = InstructionRecordSet([])

        tested = ClinicalQualityMeasure134v6(patient=patient, timeframe=timeframe, now=now)
        result = tested.compute_results()
        self.assertEqual('satisfied', result.status)
        text = r'^Dohav has diabetes and a urine protein test was done [\w\s]+ on 8/5/18$'
        self.assertRegex(result.narrative, text)
        self.assertEqual([], result.recommendations)
        self.assertEqual(285, result.due_in)  # not one year since the time frame define the period

        # patient has diabetes --> due
        patient = self.load_patient('cms134v6_diabetes_yes_only')
        tested = ClinicalQualityMeasure134v6(patient=patient, timeframe=timeframe, now=now)
        result = tested.compute_results()
        self.assertEqual('due', result.status)
        text = (r'^Dohav has diabetes and a urine microalbumin test is due to screen '
                r'for nephropathy$')
        self.assertRegex(result.narrative, text)
        expected = [{
            'title': 'Order a urine microalbumin test',
            'command': {
                'type': 'labOrder',
                'filter': {
                    'coding': [
                        {
                            'system': 'loinc',
                            'code': [
                                '50561-0', '14956-7', '11218-5', '5804-0',
                                '57735-3', '44292-1', '53525-2', '53531-0',
                                '58992-9', '21482-5', '13801-6', '63474-1',
                                '9318-7', '12842-1', '43607-1', '20454-5',
                                '32209-9', '1755-8', '77158-4', '13705-9',
                                '20621-9', '2887-8', '56553-1', '53532-8',
                                '32551-4', '30003-8', '43606-3', '50949-7',
                                '14959-1', '53530-2', '1754-1', '40663-7',
                                '14585-4', '14957-5', '32294-1', '2889-4',
                                '49023-5', '57369-1', '2888-6', '43605-5',
                                '35663-4', '26801-1', '53121-0', '27298-9',
                                '30000-4', '40486-3', '40662-9', '2890-2',
                                '30001-2', '1757-4', '18373-1', '59159-4',
                                '1753-3', '77254-1', '58448-2', '60678-0',
                                '76401-9', '14958-3', '47558-2', '21059-1',
                                '34366-5', '77253-3',
                            ]
                        }
                    ]
                }
            },
            'key': 'CMS134v6_RECOMMEND_URINE_TEST',
            'rank': 1,
            'button': 'Order',

        }]  # yapf: disable
        # self.assertEqual(recommendations, result.recommendations)
        self.helper_compare_recommendations(expected, result.recommendations)
        self.assertEqual(-1, result.due_in)

        # patient has diabetes + younger than 18 --> n/a + due in
        patient = self.load_patient('cms134v6_diabetes_no')
        patient.patient['birthDate'] = '2000-08-30'
        tested = ClinicalQualityMeasure134v6(patient=patient, timeframe=timeframe, now=now)
        result = tested.compute_results()
        self.assertEqual('not_applicable', result.status)
        self.assertIsNone(result.due_in)
        patient = self.load_patient('cms134v6_diabetes_yes_only')
        patient.patient['birthDate'] = '2000-08-30'
        tested = ClinicalQualityMeasure134v6(patient=patient, timeframe=timeframe, now=now)
        result = tested.compute_results()
        self.assertEqual('not_applicable', result.status)
        self.assertEqual(6, result.due_in)

    def test_compute_results_with_override(self):
        patient = self.load_patient('cms134v6_diabetes_yes')
        patient.protocol_overrides = ProtocolOverrideRecordSet([{
            'protocolKey': 'ClinicalQualityMeasure134v6',
            'adjustment': {
                'reference': '2018-02-01T00:00:00Z',
                'cycleDays': 180
            },
            'snooze': None,
            'modified': '2018-03-15T12:32:54Z',
        }])  # yapf: disable
        patient.lab_reports[0]['originalDate'] = '2018-08-10'

        # exam done within the last 180 days
        del (patient.conditions.records[1])
        patient.referral_reports = ReferralReportRecordSet([])
        patient.medications = MedicationRecordSet([])
        patient.instructions = InstructionRecordSet([])

        tested = ClinicalQualityMeasure134v6(
            patient=patient, now=arrow.get('2018-08-05').shift(days=80))
        result = tested.compute_results()
        self.assertEqual('satisfied', result.status)
        text = 'Dohav has diabetes and a urine protein test was done 2 months ago on 8/10/18'
        self.assertEqual(text, result.narrative)
        self.assertEqual(0, len(result.recommendations))
        self.assertEqual(105, result.due_in)

        # exam done 181 days
        patient.billing_line_items = BillingLineItemRecordSet([{
            'id': 92,
            'created': arrow.get('2018-08-01').shift(days=186),
            'cpt': '99202',
            'units': 1
        }])
        tested = ClinicalQualityMeasure134v6(
            patient=patient, now=arrow.get('2018-08-05').shift(days=186))
        result = tested.compute_results()
        self.assertEqual('due', result.status)
        text = 'Dohav has diabetes and a urine microalbumin test is due to screen for nephropathy'
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
