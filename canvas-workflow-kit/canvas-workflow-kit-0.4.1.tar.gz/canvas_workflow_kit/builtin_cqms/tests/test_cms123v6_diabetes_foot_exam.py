import arrow

from canvas_workflow_kit import settings

from canvas_workflow_kit.builtin_cqms.cms123v6_diabetes_foot_exam import ClinicalQualityMeasure123v6
from canvas_workflow_kit.patient_recordset import (
    BillingLineItemRecordSet,
    ConditionRecordSet,
    ProtocolOverrideRecordSet
)
from canvas_workflow_kit.tests.base import SDKBaseTest
from canvas_workflow_kit.timeframe import Timeframe


class ClinicalQualityMeasure123v6Test(SDKBaseTest):

    def setUp(self):
        self.mocks_path = f'{settings.BASE_DIR}/builtin_cqms/tests/mock_data'

    def test_description(self):
        expected = ('Patients 18-75 years of age with diabetes who '
                    'have not received a foot exam in the last year.')
        self.assertEqual(expected, ClinicalQualityMeasure123v6._meta.description)

    def test_information(self):
        expected = 'https://ecqi.healthit.gov/sites/default/files/ecqm/measures/CMS123v6.html'
        self.assertEqual(expected, ClinicalQualityMeasure123v6._meta.information)

    def test_enabled(self):
        self.assertTrue(ClinicalQualityMeasure123v6.enabled())

    def test_version(self):
        self.assertTrue(hasattr(ClinicalQualityMeasure123v6._meta, 'version'))

    def test_change_types(self):
        result = ClinicalQualityMeasure123v6._meta.compute_on_change_types
        expected = [
            'protocol_override',
            'condition',
            'interview',
            'patient',
        ]
        self.assertEqual(len(expected), len(result))
        for change in expected:
            self.assertIn(change, result)

    def test_period(self):
        start = arrow.get('2017-01-23 13:24:56')
        end = arrow.get('2018-01-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)

        patient = self.load_patient('cms123v6_diabetes_no')
        tested = ClinicalQualityMeasure123v6(patient=patient, timeframe=timeframe)

        # no dates --> N/A
        self.assertEqual('N/A', tested.period)

        # identical dates
        tested._on_dates = []
        tested._on_dates.append(arrow.get('2018-08-23'))
        tested._on_dates.append(arrow.get('2018-08-23'))
        tested._on_dates.append(arrow.get('2018-08-23'))
        self.assertRegex(tested.period, r'^[\w\s]+ on 8/23/18$')

        # different dates
        tested._on_dates.append(arrow.get('2018-08-21'))
        self.assertEqual('between 8/21/18 and 8/23/18', tested.period)
        tested._on_dates.append(arrow.get('2018-08-22'))
        self.assertEqual('between 8/21/18 and 8/23/18', tested.period)
        tested._on_dates.append(arrow.get('2018-08-24'))
        self.assertEqual('between 8/21/18 and 8/24/18', tested.period)

    def test_in_denominator(self):
        start = arrow.get('2017-08-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)

        # patient has no diabetes --> false
        patient = self.load_patient('cms123v6_diabetes_no')
        tested = ClinicalQualityMeasure123v6(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.in_denominator())

        # patient has diabetes --> true
        patient = self.load_patient('cms123v6_diabetes_yes')
        tested = ClinicalQualityMeasure123v6(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.in_denominator())

        # -- patient to young < 18 --> false
        patient = self.load_patient('cms123v6_diabetes_yes')
        patient.patient['birthDate'] = '2000-08-24'
        self.assertTrue(17 < patient.age_at(timeframe.end) < 18)
        tested = ClinicalQualityMeasure123v6(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.in_denominator())
        patient.patient['birthDate'] = '2000-08-23'
        self.assertTrue(patient.age_at(timeframe.end) == 18)
        tested = ClinicalQualityMeasure123v6(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.in_denominator())

        # -- patient to old > 75 --> false
        patient = self.load_patient('cms123v6_diabetes_yes')
        patient.patient['birthDate'] = '1943-08-22'
        self.assertTrue(75 < patient.age_at(timeframe.end) < 76)
        tested = ClinicalQualityMeasure123v6(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.in_denominator())
        patient.patient['birthDate'] = '1943-08-23'
        self.assertTrue(patient.age_at(timeframe.end) == 75)
        tested = ClinicalQualityMeasure123v6(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.in_denominator())
        patient.patient['birthDate'] = '1943-08-24'
        self.assertTrue(patient.age_at(timeframe.end) < 75)
        tested = ClinicalQualityMeasure123v6(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.in_denominator())

        # -- patient has an other code --> false
        patient = self.load_patient('cms123v6_diabetes_yes')
        for condition in patient.conditions:
            for code in condition['coding']:
                code['code'] = 'code'
        tested = ClinicalQualityMeasure123v6(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.in_denominator())

        # -- patient had amputations --> false
        tests = [
            ['Q7223'],  # bilateral amputation
            ['Q7222', 'Q7220'],  # left amputation
            ['Q7221', 'Q7222'],  # right amputation
            ['Q7220', 'Q7221'],  # unspecified amputation
        ]
        for codes in tests:
            patient = self.load_patient('cms123v6_diabetes_yes')
            amputations = []
            for code in codes:
                amputations.append({
                    'clinicalStatus': 'active',
                    'coding': [{
                        'system': 'ICD-10',
                        'code': code
                    }],
                    'periods': [{
                        'from': '1998-08-22',
                        'to': None
                    }]
                })
            patient.conditions += ConditionRecordSet(amputations)
            tested = ClinicalQualityMeasure123v6(patient=patient, timeframe=timeframe)
            self.assertFalse(tested.in_denominator(), 'for the code %s' % code)

        # patient has diabetes + already perform the exam --> true
        patient = self.load_patient('cms123v6_diabetes_yesdone')
        tested = ClinicalQualityMeasure123v6(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.in_denominator())

    def test_in_numerator(self):
        start = arrow.get('2017-08-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)

        # not test when patient has no diabetes because it makes no sense
        # patient = self.load_patient('cms123v6_diabetes_no')

        # patient has diabetes + no exam performed --> false
        patient = self.load_patient('cms123v6_diabetes_yes')
        tested = ClinicalQualityMeasure123v6(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.in_numerator())

        # patient has diabetes + already perform the exam --> true
        patient = self.load_patient('cms123v6_diabetes_yesdone')
        tested = ClinicalQualityMeasure123v6(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.in_numerator())

        # -- all exams are required
        tests = ['134388005', '91161007', '401191002']
        for test in tests:
            patient = self.load_patient('cms123v6_diabetes_yesdone')
            for interview in patient.interviews:
                records = interview['questions']
                interview['questions'] = []
                for record in records:
                    if record['code'] != test:
                        interview['questions'].append(record)
            tested = ClinicalQualityMeasure123v6(patient=patient, timeframe=timeframe)
            self.assertFalse(tested.in_numerator())

        # -- exams have to have been performed within the year
        patient = self.load_patient('cms123v6_diabetes_yesdone')
        for interview in patient.interviews:
            interview['noteTimestamp'] = '2017-08-23 13:24:55'
        tested = ClinicalQualityMeasure123v6(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.in_numerator())
        for interview in patient.interviews:
            interview['noteTimestamp'] = '2017-08-23 13:24:57'
        tested = ClinicalQualityMeasure123v6(patient=patient, timeframe=timeframe)
        self.assertTrue(tested.in_numerator())

        # -- exams have to be committed
        patient = self.load_patient('cms123v6_diabetes_yesdone')
        for interview in patient.interviews:
            interview['committer'] = None  # id of the person
        tested = ClinicalQualityMeasure123v6(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.in_numerator())

        # -- exams have to be not entered in error
        patient = self.load_patient('cms123v6_diabetes_yesdone')
        for interview in patient.interviews:
            interview['entered_in_error'] = 3  # id of the person
        tested = ClinicalQualityMeasure123v6(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.in_numerator())

        # -- exams have to be not deleted
        patient = self.load_patient('cms123v6_diabetes_yesdone')
        for interview in patient.interviews:
            interview['deleted'] = True
        tested = ClinicalQualityMeasure123v6(patient=patient, timeframe=timeframe)
        self.assertFalse(tested.in_numerator())

    def test_in_numerator_with_override(self):
        patient = self.load_patient('cms123v6_diabetes_yesdone')
        patient.protocol_overrides = ProtocolOverrideRecordSet([{
            'protocolKey': 'ClinicalQualityMeasure123v6',
            'adjustment': {
                'reference': '2018-02-01T00:00:00Z',
                'cycleDays': 180
            },
            'snooze': None,
            'modified': '2018-03-15T12:32:54Z',
        }])  # yapf: disable
        patient.interviews[0]['noteTimestamp'] = '2018-08-05'

        tested = ClinicalQualityMeasure123v6(
            patient=patient, now=arrow.get('2018-08-05').shift(days=0))
        self.assertTrue(tested.in_numerator())

        tested = ClinicalQualityMeasure123v6(
            patient=patient, now=arrow.get('2018-08-05').shift(days=80))
        self.assertTrue(tested.in_numerator())

        tested = ClinicalQualityMeasure123v6(
            patient=patient, now=arrow.get('2018-08-05').shift(days=180))
        self.assertTrue(tested.in_numerator())

        tested = ClinicalQualityMeasure123v6(
            patient=patient, now=arrow.get('2018-08-05').shift(days=181))
        self.assertFalse(tested.in_numerator())

    def test_compute_results(self):
        start = arrow.get('2017-10-23 13:24:56')
        end = arrow.get('2018-08-23 13:24:56')
        now = arrow.get('2018-08-23 13:24:56')
        timeframe = Timeframe(start=start, end=end)

        # patient has no diabetes --> not in denominator and numerator
        patient = self.load_patient('cms123v6_diabetes_no')
        tested = ClinicalQualityMeasure123v6(patient=patient, timeframe=timeframe, now=now)
        result = tested.compute_results()
        self.assertIsNotApplicable(result)

        # patient has diabetes --> in denominator, not numerator
        patient = self.load_patient('cms123v6_diabetes_yes')
        tested = ClinicalQualityMeasure123v6(patient=patient, timeframe=timeframe, now=now)
        result = tested.compute_results()
        self.assertEqual('due', result.status)
        text = 'Dohav has diabetes and is due for foot exam.'
        self.assertEqual(text, result.narrative)
        expected = [
            {
                'title': (
                    'Conduct comprehensive foot examination '
                    'including assessment of protective sensation, pulses and visual inspection.'),
                'narrative': None,
                'command': {
                    'type': 'interview',
                    'filter': {
                        'coding': [{
                            'system': 'snomedct',
                            'code': ['401191002', '91161007', '134388005']
                        }]
                    }
                },
                'key': 'CMS123v6_RECOMMEND_FOOT_EXAM',
                'rank': 1,
                'button': 'Plan',
            },
        ]
        for exp, recommendation in zip(expected, result.recommendations):
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
                self.assertEqual(exp_coding['code'], rec_coding['code'])
        self.assertEqual(-1, result.due_in)

        # patient has diabetes + already perform the exam --> in denominator and numerator
        patient = self.load_patient('cms123v6_diabetes_yesdone')
        tested = ClinicalQualityMeasure123v6(patient=patient, timeframe=timeframe, now=now)
        result = tested.compute_results()
        self.assertEqual('satisfied', result.status)
        text = r'^Dohav has diabetes and his comprehensive foot exam was done [\w\s]+ on 8/22/18.$'
        self.assertRegex(result.narrative, text)
        self.assertEqual([], result.recommendations)
        self.assertEqual(303, result.due_in)  # not one year since the time frame define the period

        # patient has diabetes + younger than 18 --> n/a + due in
        patient = self.load_patient('cms123v6_diabetes_no')
        patient.patient['birthDate'] = '2000-08-30'
        tested = ClinicalQualityMeasure123v6(patient=patient, timeframe=timeframe, now=now)
        result = tested.compute_results()
        self.assertEqual('not_applicable', result.status)
        self.assertIsNone(result.due_in)
        patient = self.load_patient('cms123v6_diabetes_yes')
        patient.patient['birthDate'] = '2000-08-30'
        tested = ClinicalQualityMeasure123v6(patient=patient, timeframe=timeframe, now=now)
        result = tested.compute_results()
        self.assertEqual('not_applicable', result.status)
        self.assertEqual(6, result.due_in)

    def test_compute_results_with_override(self):
        patient = self.load_patient('cms123v6_diabetes_yesdone')
        patient.protocol_overrides = ProtocolOverrideRecordSet([{
            'protocolKey': 'ClinicalQualityMeasure123v6',
            'adjustment': {
                'reference': '2018-02-01T00:00:00Z',
                'cycleDays': 180
            },
            'snooze': None,
            'modified': '2018-03-15T12:32:54Z',
        }])  # yapf: disable
        patient.interviews[0]['noteTimestamp'] = '2018-08-05'

        # exam done within the last 180 days
        tested = ClinicalQualityMeasure123v6(
            patient=patient, now=arrow.get('2018-08-05').shift(days=80))
        result = tested.compute_results()
        self.assertEqual('satisfied', result.status)
        text = ('Dohav has diabetes and his comprehensive foot '
                'exam was done 2 months ago on 8/5/18.')
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
        tested = ClinicalQualityMeasure123v6(
            patient=patient, now=arrow.get('2018-08-05').shift(days=181))
        result = tested.compute_results()
        self.assertEqual('due', result.status)
        text = 'Dohav has diabetes and is due for foot exam.'
        self.assertEqual(text, result.narrative)
        self.assertEqual(1, len(result.recommendations))
        self.assertEqual(-1, result.due_in)
