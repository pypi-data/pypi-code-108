import arrow

from canvas_workflow_kit import settings

from canvas_workflow_kit.builtin_cqms.cms130v6_colorectal_cancer_screening import ClinicalQualityMeasure130v6
from canvas_workflow_kit.patient_recordset import (
    BillingLineItemRecordSet,
    ConditionRecordSet,
    ImagingReportRecordSet,
    LabReportRecordSet,
    ProtocolOverrideRecordSet,
    ReferralReportRecordSet
)
from canvas_workflow_kit.tests.base import SDKBaseTest
from canvas_workflow_kit.timeframe import Timeframe


class ClinicalQualityMeasure130v6Test(SDKBaseTest):

    def setUp(self):
        self.mocks_path = f'{settings.BASE_DIR}/builtin_cqms/tests/mock_data'

    def test_description(self):
        expected = ('Adults 50-75 years of age who have not had appropriate '
                    'screening for colorectal cancer.')
        self.assertEqual(expected, ClinicalQualityMeasure130v6._meta.description)

    def test_information(self):
        expected = 'https://ecqi.healthit.gov/sites/default/files/ecqm/measures/CMS130v6.html'
        self.assertEqual(expected, ClinicalQualityMeasure130v6._meta.information)

    def test_enabled(self):
        self.assertTrue(ClinicalQualityMeasure130v6.enabled())

    def test_change_types(self):
        result = ClinicalQualityMeasure130v6._meta.compute_on_change_types
        expected = [
            'protocol_override',
            'condition',
            'imaging_report',
            'lab_report',
            'patient',
            'referral_report',
        ]
        self.assertEqual(len(expected), len(result))
        for change in expected:
            self.assertIn(change, result)

    def test_first_due_in(self):
        start = arrow.get('2017-08-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)

        # patient older than 50 --> none
        patient = self.load_patient('cms130v6_patient_due')
        patient.patient['birthDate'] = '1968-08-22'
        protocol = ClinicalQualityMeasure130v6(patient=patient, timeframe=timeframe)
        self.assertIsNone(protocol.first_due_in())

        # patient younger than 50 --> 6
        patient = self.load_patient('cms130v6_patient_due')
        patient.patient['birthDate'] = '1968-08-30'
        protocol = ClinicalQualityMeasure130v6(patient=patient, timeframe=timeframe)
        self.assertEqual(6, protocol.first_due_in())

        # patient younger than 50 + colon exclusion --> none
        patient = self.load_patient('cms130v6_patient_due')
        patient.patient['birthDate'] = '1968-08-30'
        patient.conditions = ConditionRecordSet([{
            'coding': [{
                'system': 'http://snomed.info/sct',
                'code': '26390003'
            }],
            'clinicalStatus': 'active',
            'periods': [{
                'from': '2008-08-22',
                'to': None
            }]
        }])
        protocol = ClinicalQualityMeasure130v6(patient=patient, timeframe=timeframe)
        self.assertIsNone(protocol.first_due_in())

    def test_had_colon_exclusion(self):
        patient = self.load_patient('cms130v6_patient_due')
        patient.conditions = ConditionRecordSet([{
            'coding': [{
                'system': 'http://snomed.info/sct',
                'code': '26390003'
            }],
            'clinicalStatus': 'active',
            'periods': [{
                'from': '2008-08-22',
                'to': None
            }]
        }])

        start = arrow.get('2017-08-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)
        protocol = ClinicalQualityMeasure130v6(patient=patient, timeframe=timeframe)
        self.assertTrue(protocol.had_colon_exclusion())

        start = arrow.get('2007-08-23 13:24:56')
        end = arrow.get('2008-08-20 13:24:56')
        timeframe = Timeframe(start=start, end=end)
        protocol = ClinicalQualityMeasure130v6(patient=patient, timeframe=timeframe)
        self.assertFalse(protocol.had_colon_exclusion())

    def test_in_initial_population(self):
        start = arrow.get('2017-08-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)

        # patient is 49 --> false
        patient = self.load_patient('cms130v6_patient_due')
        patient.patient['birthDate'] = '1968-08-24'
        protocol = ClinicalQualityMeasure130v6(patient=patient, timeframe=timeframe)
        self.assertFalse(protocol.in_initial_population())

        # patient is 50 --> true
        patient = self.load_patient('cms130v6_patient_due')
        patient.patient['birthDate'] = '1968-08-22'
        protocol = ClinicalQualityMeasure130v6(patient=patient, timeframe=timeframe)
        self.assertTrue(protocol.in_initial_population())

        # patient is 75 --> true
        patient = self.load_patient('cms130v6_patient_due')
        patient.patient['birthDate'] = '1943-08-24'
        protocol = ClinicalQualityMeasure130v6(patient=patient, timeframe=timeframe)
        self.assertTrue(protocol.in_initial_population())

        # patient is 76 --> false
        patient = self.load_patient('cms130v6_patient_due')
        patient.patient['birthDate'] = '1943-08-22'
        protocol = ClinicalQualityMeasure130v6(patient=patient, timeframe=timeframe)
        self.assertFalse(protocol.in_initial_population())

        # context
        patient = self.load_patient('cms130v6_patient_due')
        patient.patient['birthDate'] = '1968-08-22'
        patient.billing_line_items = BillingLineItemRecordSet([])
        tested = ClinicalQualityMeasure130v6(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.in_initial_population())
        tested = ClinicalQualityMeasure130v6(
            patient=patient, timeframe=timeframe, context='report')
        self.assertFalse(tested.in_initial_population())
        tested = ClinicalQualityMeasure130v6(
            patient=patient, timeframe=timeframe, context='guidance')
        self.assertTrue(tested.in_initial_population())

    def test_in_denominator(self):
        start = arrow.get('2017-08-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)

        patient = self.load_patient('cms130v6_patient_due')
        # patient between 50 and 75 --> true
        protocol = ClinicalQualityMeasure130v6(patient=patient, timeframe=timeframe)
        self.assertTrue(protocol.in_denominator())

        # patient with colon exclusion --> false
        patient.conditions = ConditionRecordSet([{
            'coding': [{
                'system': 'http://snomed.info/sct',
                'code': '26390003'
            }],
            'clinicalStatus': 'active',
            'periods': [{
                'from': '2008-08-22',
                'to': None
            }]
        }])
        protocol = ClinicalQualityMeasure130v6(patient=patient, timeframe=timeframe)
        self.assertFalse(protocol.in_denominator())

    def test_in_numerator_with_override(self):
        patient = self.load_patient('cms130v6_patient_satisfied')
        patient.protocol_overrides = ProtocolOverrideRecordSet([{
            'protocolKey': 'ClinicalQualityMeasure130v6',
            'adjustment': {
                'reference': '2018-02-01T00:00:00Z',
                'cycleDays': 180
            },
            'snooze': None,
            'modified': '2018-03-15T12:32:54Z',
        }])  # yapf: disable

        #
        patient.lab_reports[0]['originalDate'] = '2018-08-10'
        patient.imaging_reports[0]['originalDate'] = '2018-08-10'
        patient.referral_reports[0]['originalDate'] = '2018-08-10'
        tested = ClinicalQualityMeasure130v6(
            patient=patient, now=arrow.get('2018-08-15').shift(days=0))
        self.assertTrue(tested.in_numerator())
        expected = {
            'date': '2018-08-10',
            'what': 'FOBT',
            'days': 180,
        }
        self.assertEqual(expected, tested._last_exam)
        #
        patient.lab_reports[0]['originalDate'] = '2018-02-10'
        tested = ClinicalQualityMeasure130v6(
            patient=patient, now=arrow.get('2018-08-15').shift(days=0))
        self.assertTrue(tested.in_numerator())
        expected = {
            'date': '2018-08-10',
            'what': 'CT Colonography',
            'days': 180,
        }
        self.assertEqual(expected, tested._last_exam)
        #
        patient.imaging_reports[0]['originalDate'] = '2018-02-10'
        tested = ClinicalQualityMeasure130v6(
            patient=patient, now=arrow.get('2018-08-15').shift(days=0))
        self.assertTrue(tested.in_numerator())
        expected = {
            'date': '2018-08-10',
            'what': 'Colonoscopy',
            'days': 180,
        }
        self.assertEqual(expected, tested._last_exam)
        #
        patient.referral_reports[0]['originalDate'] = '2018-02-10'
        tested = ClinicalQualityMeasure130v6(
            patient=patient, now=arrow.get('2018-08-15').shift(days=0))
        self.assertFalse(tested.in_numerator())

        #
        patient.lab_reports[0]['originalDate'] = '2018-08-10'
        patient.imaging_reports[0]['originalDate'] = '2018-08-10'
        patient.referral_reports[0]['originalDate'] = '2018-08-10'
        tested = ClinicalQualityMeasure130v6(
            patient=patient, now=arrow.get('2018-08-15').shift(days=174))
        self.assertTrue(tested.in_numerator())
        expected = {
            'date': '2018-08-10',
            'what': 'FOBT',
            'days': 180,
        }
        self.assertEqual(expected, tested._last_exam)
        tested = ClinicalQualityMeasure130v6(
            patient=patient, now=arrow.get('2018-08-15').shift(days=176))
        self.assertFalse(tested.in_numerator())

    def test_in_numerator_fitdna(self):
        start = arrow.get('2017-08-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)

        # referral report
        patient = self.load_patient('cms130v6_patient_due')
        tested = ClinicalQualityMeasure130v6(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.in_numerator())
        self.assertIsNone(tested._last_exam)

        # lab report less than 1 year ago -- > true
        patient = self.load_patient('cms130v6_patient_satisfied')
        patient.lab_reports = LabReportRecordSet([{
            'originalDate': '2018-08-05',
            'loincCodes': [{
                'code': '27925-7'
            }]
        }])
        tested = ClinicalQualityMeasure130v6(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.in_numerator())
        expected = {
            'date': '2018-08-05',
            'what': 'FOBT',
            'days': 365,
        }
        self.assertEqual(expected, tested._last_exam)

        # lab report more than 1 year ago --> false
        patient = self.load_patient('cms130v6_patient_due')
        patient.lab_reports = LabReportRecordSet([{
            'originalDate': '2017-08-05',
            'loincCodes': [{
                'code': '27925-7'
            }]
        }])
        tested = ClinicalQualityMeasure130v6(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.in_numerator())
        self.assertIsNone(tested._last_exam)

        # lab report less than 3 years ago --> true
        patient = self.load_patient('cms130v6_patient_due')
        patient.lab_reports = LabReportRecordSet([{
            'originalDate': '2015-08-26',
            'loincCodes': [{
                'code': '77353-1',
            }]
        }])
        tested = ClinicalQualityMeasure130v6(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.in_numerator())
        expected = {
            'date': '2015-08-26',
            'what': 'FIT-DNA',
            'days': 1096,
        }
        self.assertEqual(expected, tested._last_exam)

        # lab report more than 3 years ago --> false
        patient = self.load_patient('cms130v6_patient_due')
        patient.lab_reports = LabReportRecordSet([{
            'originalDate': '2015-08-17',
            'loincCodes': [{
                'code': '77353-1',
            }]
        }])
        tested = ClinicalQualityMeasure130v6(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.in_numerator())
        self.assertIsNone(tested._last_exam)

    def test_in_numerator_flexible_sigmoidoscopy(self):
        start = arrow.get('2017-08-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)

        # referral report less than 5 years ago --> true
        patient = self.load_patient('cms130v6_patient_due')
        patient.referral_reports = ReferralReportRecordSet([{
            'originalDate': '2013-08-26',
            'codings': [{
                'system': 'http://www.ama-assn.org/go/cpt',
                'code': '45332',
            }]
        }])
        tested = ClinicalQualityMeasure130v6(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.in_numerator())
        expected = {
            'date': '2013-08-26',
            'what': 'Flexible sigmoidoscopy',
            'days': 1826,
        }
        self.assertEqual(expected, tested._last_exam)

        # referral report more than 5 years ago --> false
        patient = self.load_patient('cms130v6_patient_due')
        patient.referral_reports = ReferralReportRecordSet([{
            'originalDate': '2013-08-17',
            'codings': [{
                'system': 'http://www.ama-assn.org/go/cpt',
                'code': '45332',
            }]
        }])
        tested = ClinicalQualityMeasure130v6(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.in_numerator())
        self.assertIsNone(tested._last_exam)

        # imaging report less than 5 years ago --> true
        patient = self.load_patient('cms130v6_patient_due')
        patient.imaging_reports = ImagingReportRecordSet([{
            'originalDate': '2013-08-26',
            'codings': [{
                'system': 'http://www.ama-assn.org/go/cpt',
                'code': '45332',
            }]
        }])
        tested = ClinicalQualityMeasure130v6(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.in_numerator())
        expected = {
            'date': '2013-08-26',
            'what': 'Flexible sigmoidoscopy',
            'days': 1826,
        }
        self.assertEqual(expected, tested._last_exam)

        # imaging report more than 5 years ago --> false
        patient = self.load_patient('cms130v6_patient_due')
        patient.imaging_reports = ImagingReportRecordSet([{
            'originalDate': '2013-08-17',
            'codings': [{
                'system': 'http://www.ama-assn.org/go/cpt',
                'code': '45332',
            }]
        }])
        tested = ClinicalQualityMeasure130v6(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.in_numerator())
        self.assertIsNone(tested._last_exam)

    def test_in_numerator_ct_colonography(self):
        start = arrow.get('2017-08-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)

        tests = [
            ('http://www.ama-assn.org/go/cpt', '74263'),
            ('http://loinc.org', '79101-2'),
        ]
        for system, code in tests:
            # imaging report less than 5 years ago --> true
            patient = self.load_patient('cms130v6_patient_due')
            patient.imaging_reports = ImagingReportRecordSet([{
                'originalDate': '2013-08-26',
                'codings': [{
                    'system': system,
                    'code': code,
                }]
            }])
            tested = ClinicalQualityMeasure130v6(patient=patient, timeframe=timeframe)
            self.assertTrue(tested.in_numerator())
            expected = {
                'date': '2013-08-26',
                'what': 'CT Colonography',
                'days': 1826,
            }
            self.assertEqual(expected, tested._last_exam)

            # imaging report more than 5 years ago --> false
            patient = self.load_patient('cms130v6_patient_due')
            patient.imaging_reports = ImagingReportRecordSet([{
                'originalDate': '2013-08-20',
                'codings': [{
                    'system': system,
                    'code': code,
                }]
            }])
            tested = ClinicalQualityMeasure130v6(patient=patient, timeframe=timeframe)
            self.assertFalse(tested.in_numerator())
            self.assertIsNone(tested._last_exam)

            # referral report less than 5 years ago --> true
            patient = self.load_patient('cms130v6_patient_due')
            patient.referral_reports = ReferralReportRecordSet([{
                'originalDate': '2013-08-26',
                'codings': [{
                    'system': system,
                    'code': code,
                }]
            }])
            tested = ClinicalQualityMeasure130v6(patient=patient, timeframe=timeframe)
            self.assertTrue(tested.in_numerator())
            expected = {
                'date': '2013-08-26',
                'what': 'CT Colonography',
                'days': 1826,
            }
            self.assertEqual(expected, tested._last_exam)

            # referral report more than 5 years ago --> false
            patient = self.load_patient('cms130v6_patient_due')
            patient.referral_reports = ReferralReportRecordSet([{
                'originalDate': '2013-08-20',
                'codings': [{
                    'system': system,
                    'code': code,
                }]
            }])
            tested = ClinicalQualityMeasure130v6(patient=patient, timeframe=timeframe)
            self.assertFalse(tested.in_numerator())
            self.assertIsNone(tested._last_exam)

    def test_in_numerator_colonoscopy(self):
        start = arrow.get('2017-08-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)

        # referral report less than 10 years ago --> true
        patient = self.load_patient('cms130v6_patient_due')
        patient.referral_reports = ReferralReportRecordSet([{
            'originalDate': '2008-08-26',
            'codings': [{
                'system': 'http://snomed.info/sct',
                'code': '34264006',
            }]
        }])
        tested = ClinicalQualityMeasure130v6(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.in_numerator())
        expected = {
            'date': '2008-08-26',
            'what': 'Colonoscopy',
            'days': 3652,
        }
        self.assertEqual(expected, tested._last_exam)

        # referral report more than 10 years ago --> false
        patient = self.load_patient('cms130v6_patient_due')
        patient.referral_reports = ReferralReportRecordSet([{
            'originalDate': '2008-08-17',
            'codings': [{
                'system': 'http://snomed.info/sct',
                'code': '34264006',
            }]
        }])
        tested = ClinicalQualityMeasure130v6(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.in_numerator())
        self.assertIsNone(tested._last_exam)

        # imaging report less than 10 years ago --> true
        patient = self.load_patient('cms130v6_patient_due')
        patient.imaging_reports = ImagingReportRecordSet([{
            'originalDate': '2008-08-26',
            'codings': [{
                'system': 'http://snomed.info/sct',
                'code': '34264006',
            }]
        }])
        tested = ClinicalQualityMeasure130v6(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.in_numerator())
        expected = {
            'date': '2008-08-26',
            'what': 'Colonoscopy',
            'days': 3652,
        }
        self.assertEqual(expected, tested._last_exam)

        # imaging report more than 10 years ago --> false
        patient = self.load_patient('cms130v6_patient_due')
        patient.imaging_reports = ImagingReportRecordSet([{
            'originalDate': '2008-08-17',
            'codings': [{
                'system': 'http://snomed.info/sct',
                'code': '34264006',
            }]
        }])
        tested = ClinicalQualityMeasure130v6(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.in_numerator())
        self.assertIsNone(tested._last_exam)

    def test_compute_results(self):
        start = arrow.get('2017-10-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        now = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)

        # patient satisfied
        patient = self.load_patient('cms130v6_patient_satisfied')
        tested = ClinicalQualityMeasure130v6(patient=patient, timeframe=timeframe, now=now)
        result = tested.compute_results()
        self.assertEqual('satisfied', result.status)
        text = 'Nat had a FOBT 2 weeks ago on 8/5/18.'
        self.assertEqual(text, result.narrative)
        self.assertEqual([], result.recommendations)
        self.assertEqual(285, result.due_in)  # not one year since the time frame define the period

        # patient due
        patient = self.load_patient('cms130v6_patient_due')
        tested = ClinicalQualityMeasure130v6(patient=patient, timeframe=timeframe, now=now)
        result = tested.compute_results()
        self.assertEqual('due', result.status)
        text = ('Nat is due for a Colorectal Cancer Screening.\n'
                'No relevant exams found.\n'
                'Current screening interval 10 years.')
        self.assertEqual(text, result.narrative)

        expected = [
            {
                'title': 'Order a FOBT',
                'command': {
                    'type': 'labOrder',
                    'filter': {
                        'coding': [
                            {
                                'system': 'loinc',
                                'code': ['29771-3', '12504-7', '57905-2', '80372-6',
                                         '27396-1', '56491-4', '58453-2', '12503-9',
                                         '2335-8', '14564-9', '27926-5', '27925-7',
                                         '27401-9', '14563-1', '14565-6',
                                         '56490-6']}]}
                },
                'key': 'CMS130v6_RECOMMEND_FOBT',
                'rank': 1,
                'button': 'Order',
            },
            {
                'title': 'Order a FIT-DNA',
                'command': {
                    'type': 'labOrder',
                    'filter': {
                        'coding': [
                            {
                                'system': 'loinc',
                                'code': ['77353-1', '77354-9']}]}
                },
                'key': 'CMS130v6_RECOMMEND_FITDNA',
                'rank': 2,
                'button': 'Order',
            },
            {
                'title': 'Order a Flexible sigmoidoscopy',
                'command': {
                    'type': 'refer',
                    'filter': {
                        'coding': [
                            {
                                'system': 'cpt',
                                'code': ['45350', '45338', '45334', '45337', '45339',
                                         '45333', '45341', '45345', '45346', '45340',
                                         '45349', '45335', '45347', '45330', '45342',
                                         '45332', '45331',
                                         ]},
                            {
                                'system': 'hcpcs', 'code': ['G0104', ]},
                            {
                                'system': 'snomedct',
                                'code': ['396226005', '425634007', '44441009',
                                         '112870002',
                                         ]}]}
                },
                'key': 'CMS130v6_RECOMMEND_SIGMOIDOSCOPY',
                'rank': 3,
                'button': 'Order',
            },
            {
                'title': 'Order a CT Colonography',
                'command': {
                    'type': 'imagingOrder',
                    'filter': {
                        'coding': [
                            {
                                'system': 'cpt',
                                'code': ['74263']},
                            {
                                'system': 'snomedct',
                                'code': ['418714002']}]}
                },
                'key': 'CMS130v6_RECOMMEND_COLONOGRAPHY',
                'rank': 4,
                'button': 'Order',
            },
            {
                'title': 'Order a Colonoscopy',
                'command': {
                    'type': 'refer',
                    'filter': {
                        'coding': [
                            {
                                'system': 'cpt',
                                'code': ['44401', '44402', '45391', '45392', '45388',
                                         '45393', '44394', '44407', '44405', '45387',
                                         '45355', '45398', '45378', '44404', '44392',
                                         '44390', '44403', '44391', '45383', '45384',
                                         '45390', '45379', '45380', '44388', '44393',
                                         '45385', '44397', '45381', '45382', '44406',
                                         '45389', '44389', '44408', '45386',
                                         ]},
                            {
                                'system': 'hcpcs',
                                'code': ['G0105', 'G0121', ]},
                            {
                                'system': 'snomedct',
                                'code': ['8180007', '427459009', '310634005',
                                         '174184006', '443998000', '446521004',
                                         '303587008', '12350003', '367535003',
                                         '444783004', '34264006', '447021001',
                                         '73761001', '25732003', '446745002',
                                         '235150006', '235151005', '174158000',
                                         ]}]}
                },
                'key': 'CMS130v6_RECOMMEND_COLONOSCOPY',
                'rank': 5,
                'button': 'Order',
            }
        ]  # yapf: disable
        # self.assertEqual(recommendations, result.recommendations)
        self.helper_compare_recommendations(expected, result.recommendations)
        self.assertEqual(-1, result.due_in)

        # patient younger than 50 --> n/a + due in
        patient = self.load_patient('cms130v6_patient_due')
        patient.patient['birthDate'] = '1968-08-30'
        tested = ClinicalQualityMeasure130v6(patient=patient, timeframe=timeframe, now=now)
        result = tested.compute_results()
        self.assertEqual('not_applicable', result.status)
        self.assertEqual(6, result.due_in)

    def test_compute_results_with_override(self):
        patient = self.load_patient('cms130v6_patient_satisfied')
        patient.protocol_overrides = ProtocolOverrideRecordSet([{
            'protocolKey': 'ClinicalQualityMeasure130v6',
            'adjustment': {
                'cycleDays': 180
            },
            'snooze': None,
            'modified': '2018-03-15T12:32:54Z',
        }])  # yapf: disable
        patient.referral_reports[0]['originalDate'] = '2019-07-26'
        patient.billing_line_items[0]['created'] = '2019-07-26'

        # exam done within the last 180 days
        tested = ClinicalQualityMeasure130v6(
            patient=patient, now=arrow.get('2019-07-26').shift(days=80))
        result = tested.compute_results()
        self.assertEqual('satisfied', result.status)
        text = 'Nat had a Colonoscopy 3 months ago on 7/26/19.'
        self.assertEqual(text, result.narrative)
        self.assertEqual(0, len(result.recommendations))
        self.assertEqual(100, result.due_in)

        # exam done 181 days
        patient.billing_line_items[0]['created'] = '2028-07-29'  # visit within the 180-day period
        tested = ClinicalQualityMeasure130v6(
            patient=patient, now=arrow.get('2028-07-26').shift(days=181))
        result = tested.compute_results()
        self.assertEqual('due', result.status)
        text = ('Nat is due for a Colorectal Cancer Screening.\n'
                'Last Colonoscopy done 9 years ago on 7/26/19.\n'
                'Current screening interval 6 months.')
        self.assertEqual(text, result.narrative)
        self.assertEqual(5, len(result.recommendations))
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
