import arrow

from canvas_workflow_kit import settings

from canvas_workflow_kit.builtin_cqms.cms131v6_diabetes_eye_exam import ClinicalQualityMeasure131v6
from canvas_workflow_kit.patient_recordset import BillingLineItemRecordSet, ProtocolOverrideRecordSet
from canvas_workflow_kit.tests.base import SDKBaseTest
from canvas_workflow_kit.timeframe import Timeframe


class ClinicalQualityMeasure131v6Test(SDKBaseTest):

    def setUp(self):
        self.mocks_path = f'{settings.BASE_DIR}/builtin_cqms/tests/mock_data'

    def test_enabled(self):
        self.assertTrue(ClinicalQualityMeasure131v6.enabled())

    def test_description(self):
        expected = ('Patients 18-75 years of age with diabetes who have not had a retinal or '
                    'dilated eye exam by an eye care professional.')
        self.assertEqual(expected, ClinicalQualityMeasure131v6._meta.description)

    def test_information(self):
        expected = 'https://ecqi.healthit.gov/sites/default/files/ecqm/measures/CMS131v6.html'
        self.assertEqual(expected, ClinicalQualityMeasure131v6._meta.information)

    def test_version(self):
        self.assertTrue(hasattr(ClinicalQualityMeasure131v6._meta, 'version'))

    def test_change_types(self):
        result = ClinicalQualityMeasure131v6._meta.compute_on_change_types
        expected = [
            'protocol_override',
            'condition',
            'patient',
            'referral_report',
        ]
        self.assertEqual(len(expected), len(result))
        for change in expected:
            self.assertIn(change, result)

    def test_in_denominator(self):
        start = arrow.get('2017-08-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)

        # patient has no diabetes --> false
        patient = self.load_patient('cms131v6_diabetes_no')
        tested = ClinicalQualityMeasure131v6(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.in_denominator())

        # patient has diabetes --> true
        patient = self.load_patient('cms131v6_diabetes_yesnoreferralreport')
        tested = ClinicalQualityMeasure131v6(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.in_denominator())

        # -- patient to young < 18 --> false
        patient = self.load_patient('cms131v6_diabetes_yesnoreferralreport')
        patient.patient['birthDate'] = '2000-08-24'
        self.assertTrue(17 < patient.age_at(timeframe.end) < 18)
        tested = ClinicalQualityMeasure131v6(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.in_denominator())
        patient.patient['birthDate'] = '2000-08-23'
        self.assertTrue(patient.age_at(timeframe.end) == 18)
        tested = ClinicalQualityMeasure131v6(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.in_denominator())

        # -- patient to old > 75 --> false
        patient = self.load_patient('cms131v6_diabetes_yesnoreferralreport')
        patient.patient['birthDate'] = '1943-08-22'
        self.assertTrue(75 < patient.age_at(timeframe.end) < 76)
        tested = ClinicalQualityMeasure131v6(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.in_denominator())
        patient.patient['birthDate'] = '1943-08-23'
        self.assertTrue(patient.age_at(timeframe.end) == 75)
        tested = ClinicalQualityMeasure131v6(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.in_denominator())
        patient.patient['birthDate'] = '1943-08-24'
        self.assertTrue(patient.age_at(timeframe.end) < 75)
        tested = ClinicalQualityMeasure131v6(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.in_denominator())

        # -- patient has an other code --> false
        patient = self.load_patient('cms131v6_diabetes_yesnoreferralreport')
        for condition in patient.conditions:
            for code in condition['coding']:
                code['code'] = 'code'
        tested = ClinicalQualityMeasure131v6(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.in_denominator())

        # patient has diabetes + already perform the exam --> true
        patient = self.load_patient('cms131v6_diabetes_yeswithreferralreport')
        tested = ClinicalQualityMeasure131v6(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.in_denominator())

    def test_in_numerator(self):
        start = arrow.get('2017-08-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)

        # not test when patient has no diabetes because it makes no sense
        # patient = self.load_patient('cms131v6_diabetes_no')

        # patient has diabetes + no exam performed --> false
        patient = self.load_patient('cms131v6_diabetes_yesnoreferralreport')
        tested = ClinicalQualityMeasure131v6(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.in_numerator())

        # patient has diabetes + already perform the exam, regardless the result --> true
        tests = [
            '37231002',
            '43959009',
            '4855003',
            '721103006',
        ]
        for on_date in ['2018-08-22', '2018-02-22', '2017-08-24']:
            for code in tests:
                patient = self.load_patient('cms131v6_diabetes_yeswithreferralreport')
                for reports in patient.referral_reports:
                    reports['originalDate'] = on_date
                    for coding in reports['codings']:
                        if coding['id'] == 59:
                            coding['code'] = code
                            break
                tested = ClinicalQualityMeasure131v6(patient=patient, timeframe=timeframe)
                self.assertTrue(tested.in_numerator())

        # -- exams performed within the previous year of the measurement period
        # --> true for 721103006
        tests = [
            '37231002',
            '43959009',
            '4855003',
            '721103006',
        ]
        for on_date in ['2017-08-22', '2017-02-22', '2016-08-24']:
            for code in tests:
                patient = self.load_patient('cms131v6_diabetes_yeswithreferralreport')
                for reports in patient.referral_reports:
                    reports['originalDate'] = on_date
                    for coding in reports['codings']:
                        if coding['id'] == 59:
                            coding['code'] = code
                            break
                tested = ClinicalQualityMeasure131v6(patient=patient, timeframe=timeframe)
                tested.in_numerator()

                if code == '721103006':
                    self.assertTrue(tested.in_numerator(), f'code {code} ({on_date})')
                else:
                    self.assertFalse(tested.in_numerator(), f'code {code} ({on_date})')

        # -- exams performed before the previous year of the measurement period --> false
        tests = [
            '37231002',
            '43959009',
            '4855003',
            '721103006',
        ]
        for on_date in ['2016-08-22', '2016-02-22']:
            for code in tests:
                patient = self.load_patient('cms131v6_diabetes_yeswithreferralreport')
                for reports in patient.referral_reports:
                    reports['originalDate'] = on_date
                    for coding in reports['codings']:
                        if coding['id'] == 59:
                            coding['code'] = code
                            break
                tested = ClinicalQualityMeasure131v6(patient=patient, timeframe=timeframe)
                self.assertFalse(tested.in_numerator())

    def test_in_numerator_with_override(self):
        patient = self.load_patient('cms131v6_diabetes_yeswithreferralreport')
        patient.protocol_overrides = ProtocolOverrideRecordSet([{
            'protocolKey': 'ClinicalQualityMeasure131v6',
            'adjustment': {
                'reference': '2018-02-01T00:00:00Z',
                'cycleDays': 180
            },
            'snooze': None,
            'modified': '2018-03-15T12:32:54Z',
        }])  # yapf: disable
        patient.referral_reports[0]['originalDate'] = '2018-08-05'

        tested = ClinicalQualityMeasure131v6(
            patient=patient, now=arrow.get('2018-08-05').shift(days=0))
        self.assertTrue(tested.in_numerator())

        tested = ClinicalQualityMeasure131v6(
            patient=patient, now=arrow.get('2018-08-05').shift(days=80))
        self.assertTrue(tested.in_numerator())

        tested = ClinicalQualityMeasure131v6(
            patient=patient, now=arrow.get('2018-08-05').shift(days=180))
        self.assertTrue(tested.in_numerator())

        tested = ClinicalQualityMeasure131v6(
            patient=patient, now=arrow.get('2018-08-05').shift(days=181))
        self.assertFalse(tested.in_numerator())

        # -- exams performed before the previous year of the measurement period --> false
        tests = [
            '37231002',
            '43959009',
            '4855003',
            '721103006',
        ]
        for code in tests:
            for reports in patient.referral_reports:
                reports['originalDate'] = '2018-08-05'
                for coding in reports['codings']:
                    if coding['id'] == 59:
                        coding['code'] = code
                        break
            tested = ClinicalQualityMeasure131v6(
                patient=patient, now=arrow.get('2018-08-05').shift(days=350))
            if code == '721103006':
                self.assertTrue(tested.in_numerator(), f'code {code}')
            else:
                self.assertFalse(tested.in_numerator(), f'code {code}')

            tested = ClinicalQualityMeasure131v6(
                patient=patient, now=arrow.get('2018-08-05').shift(days=361))
            self.assertFalse(tested.in_numerator(), f'code {code}')

    def test_compute_results(self):
        start = arrow.get('2017-09-03 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        now = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)

        # patient has no diabetes --> false
        patient = self.load_patient('cms131v6_diabetes_no')
        tested = ClinicalQualityMeasure131v6(patient=patient, timeframe=timeframe, now=now)
        result = tested.compute_results()
        self.assertIsNotApplicable(result)

        # patient has diabetes --> true
        patient = self.load_patient('cms131v6_diabetes_yesnoreferralreport')
        tested = ClinicalQualityMeasure131v6(patient=patient, timeframe=timeframe, now=now)
        result = tested.compute_results()
        self.assertEqual('due', result.status)
        text = ('Dohav has diabetes and no documentation of retinal '
                'examination in the past 12 months.')
        self.assertEqual(text, result.narrative)
        self.helper_exam_recommended(result.recommendations)
        self.assertEqual(-1, result.due_in)

        # patient has diabetes + already perform the exam --> true
        patient = self.load_patient('cms131v6_diabetes_yeswithreferralreport')
        tested = ClinicalQualityMeasure131v6(patient=patient, timeframe=timeframe, now=now)
        result = tested.compute_results()
        self.assertEqual('satisfied', result.status)
        text = (r'^Dohav has diabetes and a retinal examination was done [\w\s]+ on 8/22/18,'
                ' demonstrating Retinopathy co-occurrent and due to diabetes mellitus.$')
        self.assertRegex(result.narrative, text)
        self.assertEqual([], result.recommendations)
        self.assertEqual(352, result.due_in)

        # -- exams performed within the previous year of the measurement period
        # --> true for 721103006
        tests = [
            '37231002',
            '43959009',
            '4855003',
            '721103006',
        ]
        for code in tests:
            patient = self.load_patient('cms131v6_diabetes_yeswithreferralreport')
            for reports in patient.referral_reports:
                reports['originalDate'] = '2017-02-22'
                for coding in reports['codings']:
                    if coding['id'] == 59:
                        coding['code'] = code
                        break
            tested = ClinicalQualityMeasure131v6(patient=patient, timeframe=timeframe, now=now)
            result = tested.compute_results()

            if code == '721103006':
                text = (
                    r'^Dohav has diabetes and a retinal examination was done [\w\s]+ on 2/22/17 '
                    'demonstrating no diabetic eye disease. '
                    'Next examination is due 2/11/18.$')
                self.assertRegex(result.narrative, text)
                self.assertEqual([], result.recommendations)
                self.assertEqual('satisfied', result.status)
                self.assertEqual(-194, result.due_in)
            else:
                text = (
                    r'^Dohav has diabetes and a prior abnormal retinal examination [\w\s]+ '
                    'on 2/22/17 showing Retinopathy co-occurrent and due to diabetes mellitus. '
                    'Dohav is due for retinal examination.$')
                self.assertRegex(result.narrative, text)
                self.helper_exam_recommended(result.recommendations)
                self.assertEqual('due', result.status)
                self.assertEqual(-1, result.due_in)

        # -- exams performed before the previous year of the measurement period --> false
        tests = [
            '37231002',
            '43959009',
            '4855003',
            '721103006',
        ]
        for on_date in ['2016-08-22', '2016-02-22']:
            for code in tests:
                patient = self.load_patient('cms131v6_diabetes_yeswithreferralreport')
                for reports in patient.referral_reports:
                    reports['originalDate'] = on_date
                    for coding in reports['codings']:
                        if coding['id'] == 59:
                            coding['code'] = code
                            break
                tested = ClinicalQualityMeasure131v6(patient=patient, timeframe=timeframe, now=now)
                result = tested.compute_results()
                text = ('Dohav has diabetes and no documentation of retinal '
                        'examination in the past 12 months.')
                self.assertEqual(text, result.narrative)
                self.helper_exam_recommended(result.recommendations)
                self.assertEqual('due', result.status)
                self.assertEqual(-1, result.due_in)

        # patient has diabetes + younger than 18 --> n/a + due in
        patient = self.load_patient('cms131v6_diabetes_no')
        patient.patient['birthDate'] = '2000-08-30'
        tested = ClinicalQualityMeasure131v6(patient=patient, timeframe=timeframe, now=now)
        result = tested.compute_results()
        self.assertEqual('not_applicable', result.status)
        self.assertIsNone(result.due_in)
        patient = self.load_patient('cms131v6_diabetes_yesnoreferralreport')
        patient.patient['birthDate'] = '2000-08-30'
        tested = ClinicalQualityMeasure131v6(patient=patient, timeframe=timeframe, now=now)
        result = tested.compute_results()
        self.assertEqual('not_applicable', result.status)
        self.assertEqual(6, result.due_in)

    def test_compute_results_with_override(self):
        patient = self.load_patient('cms131v6_diabetes_yeswithreferralreport')
        patient.protocol_overrides = ProtocolOverrideRecordSet([{
            'protocolKey': 'ClinicalQualityMeasure131v6',
            'adjustment': {
                'reference': '2018-02-01T00:00:00Z',
                'cycleDays': 180
            },
            'snooze': None,
            'modified': '2018-03-15T12:32:54Z',
        }])  # yapf: disable
        patient.referral_reports[0]['originalDate'] = '2018-08-05'

        # exam done within the last 180 days
        tested = ClinicalQualityMeasure131v6(
            patient=patient, now=arrow.get('2018-08-05').shift(days=80))
        result = tested.compute_results()
        self.assertEqual('satisfied', result.status)
        text = ('Dohav has diabetes and a retinal examination was done 2 months ago on 8/5/18, '
                'demonstrating Retinopathy co-occurrent and due to diabetes mellitus.')
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
        tested = ClinicalQualityMeasure131v6(
            patient=patient, now=arrow.get('2018-08-05').shift(days=181))
        result = tested.compute_results()
        self.assertEqual('due', result.status)
        text = (
            'Dohav has diabetes and a prior abnormal retinal examination 6 months ago on 8/5/18 '
            'showing Retinopathy co-occurrent and due to diabetes mellitus. '
            'Dohav is due for retinal examination.')
        self.assertEqual(text, result.narrative)
        self.assertEqual(2, len(result.recommendations))
        self.assertEqual(-1, result.due_in)

        # exam done 240 days ago
        tests = [
            '37231002',
            '43959009',
            '4855003',
            '721103006',
        ]
        for code in tests:
            for reports in patient.referral_reports:
                reports['originalDate'] = '2018-08-05'
                for coding in reports['codings']:
                    if coding['id'] == 59:
                        coding['code'] = code
                        break
            tested = ClinicalQualityMeasure131v6(
                patient=patient, now=arrow.get('2018-08-05').shift(days=240))
            result = tested.compute_results()

            if code == '721103006':
                text = ('Dohav has diabetes and a retinal examination was done 8 months ago '
                        'on 8/5/18 demonstrating no diabetic eye disease. '
                        'Next examination is due 2/1/19.')
                self.assertEqual(text, result.narrative)
                self.assertEqual([], result.recommendations)
                self.assertEqual('satisfied', result.status)
                self.assertEqual(-60, result.due_in)
            else:
                text = ('Dohav has diabetes and a prior abnormal retinal examination 8 months ago '
                        'on 8/5/18 showing Retinopathy co-occurrent and due to diabetes mellitus. '
                        'Dohav is due for retinal examination.')
                self.assertEqual(text, result.narrative)
                self.helper_exam_recommended(result.recommendations)
                self.assertEqual('due', result.status)
                self.assertEqual(-1, result.due_in)

    def helper_exam_recommended(self, result):
        expected = [
            {
                'title': 'Perform retinal examination',
                'narrative': None,
                'command': {
                    'type': 'perform',
                    'filter': {
                        'coding': [{
                            'system': 'cpt',
                            'code': ['92250']
                        }]
                    }
                },
                'key': 'CMS131v6_RECOMMEND_PERFORM_EYE_EXAM',
                'rank': 1,
                'button': 'Perform',
            },
            {
                'title': 'Refer for retinal examination',
                'narrative': None,
                'command': {
                    'type': 'refer',
                    'filter': {
                        'coding': [{
                            'system': 'snomedct',
                            'code': [
                                '427478009', '308110009', '410453006', '314972008', '410451008',
                                '252789008', '410452001', '252784003', '274798009', '314971001',
                                '410455004', '420213007', '252780007', '6615001', '425816006',
                                '252790004', '252782004', '274795007', '252788000', '252779009',
                                '252781006', '252783009'
                            ]
                        }]
                    }
                },
                'key': 'CMS131v6_RECOMMEND_REFER_EYE_EXAM',
                'rank': 2,
                'button': 'Refer',
            },
        ]

        for exp, recommendation in zip(expected, result):
            self.assertEqual(exp['key'], recommendation.key)
            self.assertEqual(exp['rank'], recommendation.rank)
            self.assertEqual(exp['button'], recommendation.button)
            self.assertEqual(exp['title'], recommendation.title)
            self.assertEqual(exp['narrative'], recommendation.narrative)
            self.assertEqual(exp['command']['type'], recommendation.command['type'])
            exp_item = exp['command']['filter']['coding']
            rec_item = recommendation.command['filter']['coding']
            self.assertEqual(len(exp_item), len(rec_item))
            for exp_coding, rec_coding in zip(exp_item, rec_item):
                self.assertEqual(exp_coding['system'], rec_coding['system'])
                self.assertEqual(sorted(exp_coding['code']), sorted(rec_coding['code']))
