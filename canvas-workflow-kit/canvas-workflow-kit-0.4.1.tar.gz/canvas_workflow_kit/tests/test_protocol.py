from datetime import datetime, timedelta

import arrow

from canvas_workflow_kit.patient_recordset import ProtocolOverrideRecordSet
from canvas_workflow_kit.protocol import (
    ClinicalQualityMeasure,
    Protocol,
    ProtocolResult,
    ProtocolSource,
    get_protocols,
    get_subclasses,
    protocols_for_patient
)
from canvas_workflow_kit.recommendation import Recommendation, PlanRecommendation
from canvas_workflow_kit.tests import get_protocols_unittest
from canvas_workflow_kit.timeframe import Timeframe

from .base import SDKBaseTest


LOADED_PROTOCOLS = get_protocols(get_protocols_unittest)

class TestProtocolResult(SDKBaseTest):

    def test___init__(self):
        tested = ProtocolResult()
        self.assertEqual([], tested.recommendations)
        self.assertEqual('not_applicable', tested.status)
        self.assertEqual([], tested.narratives)
        self.assertIsNone(tested.due_in)
        self.assertEqual(30, tested.days_of_notice)
        self.assertIsNone(tested.next_review)

    def test_add_recommendation(self):
        tested = ProtocolResult()
        self.assertEqual([], tested.recommendations)
        tested.add_recommendation(
            Recommendation('KEY-A', 7, 'ACT', 'reco A', 'this is the reco A'))
        tested.add_recommendation(
            Recommendation('KEY-B', 3, 'BAC', 'reco B', 'this is the reco B'))
        tested.add_recommendation(
            PlanRecommendation('KEY-C', 4, 'BAC', 'button', 'reco C', 'this is the reco C'))
        self.assertEqual(3, len(tested.recommendations))
        for recommendation in tested.recommendations:
            self.assertIn(recommendation.title, ['reco A', 'reco B', 'reco C'])

    def test_add_recommendation_shorthand(self):
        tested = ProtocolResult()
        self.assertEqual([], tested.recommendations)
        tested.add_recommendation(
            'KEY-A', 7, 'ACT', 'reco A', 'this is the reco A')
        tested.add_recommendation(
            key='KEY-B', rank=3, button='BAC', title='reco B', narrative='this is the reco B')
        self.assertEqual(2, len(tested.recommendations))
        for recommendation in tested.recommendations:
            self.assertIn(recommendation.title, ['reco A', 'reco B'])

    def test_add_recommendation_shorthand_custom(self):
        tested = ProtocolResult()
        self.assertEqual([], tested.recommendations)
        tested.add_plan_recommendation('KEY-A', 7, 'ACT', 'reco A', 'this is the reco A')
        tested.add_vital_sign_recommendation('KEY-B', 3, 'BAC', 'reco B', 'this is the reco B')
        self.assertEqual(2, len(tested.recommendations))

        self.assertEqual(tested.recommendations[0].__class__.__name__, 'PlanRecommendation')
        self.assertEqual(tested.recommendations[1].__class__.__name__, 'VitalSignRecommendation')

    def test_add_narrative(self):
        tested = ProtocolResult()
        self.assertEqual([], tested.narratives)
        tested.add_narrative('narrative A')
        tested.add_narrative('narrative B')
        self.assertEqual(2, len(tested.narratives))
        for narrative in tested.narratives:
            self.assertIn(narrative, ['narrative A', 'narrative B'])

    def test_narrative(self):
        tested = ProtocolResult()
        self.assertEqual('', tested.narrative)
        tested.add_narrative('narrative A')
        tested.add_narrative('narrative B')
        expected = 'narrative A\nnarrative B'
        self.assertEqual(expected, tested.narrative)


class TestProtocolSource(SDKBaseTest):

    def test___init__(self):
        tested = ProtocolSource('Some text', 'https://not.known.com/utests')
        self.assertIsInstance(tested, ProtocolSource)
        self.assertEqual('Some text', tested.text)
        self.assertEqual('https://not.known.com/utests', tested.url)


class TestProtocol(SDKBaseTest):

    def test___init__(self):
        patient = self.load_patient('full')
        tested = Protocol(patient)
        self.assertIsInstance(tested, Protocol)
        self.assertIs(patient, tested.patient)
        self.assertEqual([], tested._meta.compute_on_change_types)
        self.assertEqual([], tested._meta.responds_to_event_types)
        self.assertEqual([], tested._meta.identifiers)
        self.assertEqual('', tested._meta.title)
        self.assertEqual('', tested._meta.description)
        self.assertEqual('', tested._meta.information)

    def test_protocol_key(self):
        patient = self.load_patient('full')
        tested = Protocol(patient)
        expected = 'Protocol'
        result = tested.protocol_key()
        self.assertEqual(expected, result)

        tested = TestProto(patient)
        expected = 'TestProto'
        result = tested.protocol_key()
        self.assertEqual(expected, result)

    def test_protocol_title(self):
        patient = self.load_patient('full')
        tested = Protocol(patient)
        expected = ''
        result = tested._meta.title
        self.assertEqual(expected, result)

        tested = TestProto(patient)
        expected = 'Title TestProtocol'
        result = tested._meta.title
        self.assertEqual(expected, result)

    def test_references(self):
        patient = self.load_patient('full')
        tested = Protocol(patient)

        tested = TestProto(patient)
        expected = [
            'Small title #1. www.unittests.med/canvas?id=1',
            'Small title #2. http://www.unittests.med/canvas?id=2',
            'Small title #3. https://www.unittests.med/canvas?id=3',
            'Small title #4. WWW.unittests.med/canvas?id=4',
            'Not valid #5  www.unittests.med/canvas?id=5 because of this',
        ]
        self.assertEqual(expected, tested._meta.references)

    def test_relative_float(self):
        tests = [
            ['123.45', 123.45],
            ['≤123.45', 123.45],
            ['≥123.45', 123.45],
            ['>=123.45', 123.45],
            ['<=123.45', 123.45],
            ['>123.45', 123.450001],
            ['<123.45', 123.449999],
            ['-123.45', -123.45],
            ['=123.45', 123.45],
            ['=', 0],
            ['', 0],
            ['abcd', 0],
        ]
        for value, expected in tests:
            result = Protocol.relative_float(value)
            self.assertEqual(expected, result, value)

    def test_sources(self):
        patient = self.load_patient('full')
        tested = TestProto(patient)

        expected = [
            'www.unittests.med/canvas?id=1',
            'http://www.unittests.med/canvas?id=2',
            'https://www.unittests.med/canvas?id=3',
            'WWW.unittests.med/canvas?id=4',
            None,
        ]
        result = tested.sources()
        self.assertEqual(len(expected), len(result))
        for src in result:
            self.assertIsInstance(src, ProtocolSource)
            self.assertEqual(1, expected.count(src.url))

    def test_status(self):
        patient = self.load_patient('full')
        tested = Protocol(patient)
        with self.assertRaises(NotImplementedError):
            tested.status()

        tested = TestProto(patient)
        expected = 'current status'
        self.assertEqual(expected, tested.status())

    def test_snoozed(self):
        patient = self.load_patient('full')
        patient.protocol_overrides = ProtocolOverrideRecordSet([
            {
                'protocolKey': 'TEST001v2',
                'adjustment': {
                    'reference': '2018-10-01T00:00:00Z',
                    'cycleDays': 19
                },
                'snooze': {
                    'reference': arrow.now(),
                    'snoozedDays': 22
                },
                'modified': '2018-10-02T21:50:09.661490Z'
            },
            {
                'protocolKey': 'TEST003v2',
                'adjustment': None,
                'snooze': {
                    'reference': '2018-09-15T00:00:00Z',
                    'snoozedDays': 12
                },
                'modified': '2018-09-15T21:50:09.661490Z'
            },
            {
                'protocolKey': 'TEST004v1',
                'adjustment': {
                    'reference': '2018-08-15T00:00:00Z',
                    'cycleDays': 60
                },
                'snooze': None,
                'modified': '2018-08-23T21:50:09.661490Z'
            }])  # yapf: disable

        # no protocol override --> false
        tested = Protocol(patient=patient)
        tested.identifiers = ['TEST005v1']
        self.assertFalse(tested.snoozed())

        # protocol override without snooze --> false
        tested = Protocol(patient=patient)
        tested.identifiers = ['TEST004v1']
        self.assertFalse(tested.snoozed())

        # protocol override with past snooze --> false
        tested = Protocol(patient=patient)
        tested.identifiers = ['TEST003v2']
        self.assertFalse(tested.snoozed())

        # protocol override with snooze --> true
        tested = Protocol(patient=patient)
        tested.protocol_key = lambda: 'TEST001v2'
        tested.identifiers = ['TEST001v2']
        self.assertTrue(tested.snoozed())

        # protocol override switch off --> true
        patient.protocol_overrides = ProtocolOverrideRecordSet([{
            'protocolKey': '*',
            'adjustment': None,
            'snooze': None,
            'modified': '2018-08-23T21:50:09.661490Z'
        }])
        tested = Protocol(patient=patient)
        tested.identifiers = ['TEST005v2']
        self.assertTrue(tested.snoozed())

    def test_enabled(self):
        patient = self.load_patient('full')
        tested = TestProto(patient)
        self.assertTrue(tested.enabled())

        tested = TestPFalse(patient)
        self.assertFalse(tested.enabled())


class TestClinicalQualityMeasure(SDKBaseTest):

    def test___init__(self):
        patient = self.load_patient('full')

        # no change types, time frame provided
        tested = CQMImplementation(patient=patient)

        self.assertEqual(['HEALTH_MAINTENANCE'], tested._meta.responds_to_event_types)
        self.assertIsNone(tested.results())

        result = tested.timeframe
        self.assertIsInstance(result, Timeframe)
        fmt = '%Y-%m-%d %H:%M'

        last_year = {
            'year': datetime.utcnow().year - 1,
            'month': datetime.utcnow().month,
            'day': datetime.utcnow().day,
            'hour': datetime.utcnow().hour,
            'minute': datetime.utcnow().minute,
        }

        self.assertEqual(datetime(**last_year).strftime(fmt), tested.timeframe.start.strftime(fmt))
        self.assertEqual(datetime.utcnow().strftime(fmt), tested.timeframe.end.strftime(fmt))

        self.assertEqual(datetime.utcnow().strftime(fmt), tested.now.strftime(fmt))
        self.assertEqual('report', tested.context)

        # context provided
        tests = {
            'report': 'report',
            'guidance': 'guidance',
            'nope': 'report',
        }
        for context, expected in tests.items():
            tested = CQMImplementation(patient=patient, context=context)
            self.assertEqual(expected, tested.context)

        # time frame provided
        start = arrow.get('2018-08-17 01:23:45')
        end = arrow.get('2018-08-17 12:34:56')
        timeframe = Timeframe(start, end)
        tested = ClinicalQualityMeasure(patient=patient, timeframe=timeframe)
        result = tested.timeframe
        self.assertIsInstance(result, Timeframe)
        self.assertIs(start, result.start)
        self.assertIs(end, result.end)

        self.assertEqual(datetime.utcnow().strftime(fmt), tested.now.strftime(fmt))

        # now provided
        tested = ClinicalQualityMeasure(patient=patient, now=arrow.get('2018-10-30 12:34'))
        self.assertEqual('2018-10-30 12:34', tested.now.strftime(fmt))

        # adjustment
        patient.protocol_overrides = ProtocolOverrideRecordSet([{
            'protocolKey': 'TestCQM',
            'adjustment': {
                'reference': '2018-02-01T00:00:00Z',
                'cycleDays': 180
            },
            'snooze': None,
            'modified': '2018-03-15T12:32:54Z',
        }])  # yapf: disable
        tested = TestCQM(patient=patient, now=arrow.get('2018-10-30 12:34'))
        result = tested.timeframe
        self.assertEqual('2018-05-03 12:34', result.start.strftime(fmt))
        self.assertEqual('2018-10-30 12:34', result.end.strftime(fmt))

        # change types provided
        # + empty -> instance is computable
        tested = CQMImplementation(patient=patient, change_types=[])

        self.assertEqual(['HEALTH_MAINTENANCE'], tested._meta.responds_to_event_types)
        self.assertIsNone(tested.results())

        # + with changes + instance with empty impacting list -> instance is computable
        tested = CQMImplementation(
            patient=patient, change_types=[
                'change_A',
                'change_B',
            ])

        self.assertEqual(['HEALTH_MAINTENANCE'], tested._meta.responds_to_event_types)
        self.assertIsNone(tested.results())

        # + with changes + instance impacted by one change -> instance is computable
        class UnitTestCQMImpactedByA(CQMImplementation):
            class Meta:
                compute_on_change_types = [
                    'change_A',
                    'change_C',
                ]

        tested = UnitTestCQMImpactedByA(
            patient=patient, change_types=[
                'change_A',
                'change_B',
            ])

        self.assertEqual(['HEALTH_MAINTENANCE'], tested._meta.responds_to_event_types)
        self.assertIsNone(tested.results())

        # + with changes + instance impacted by other changes -> instance is not computable
        tested = UnitTestCQMImpactedByA(
            patient=patient, change_types=[
                'change_D',
                'change_B',
            ])

        self.assertEqual(['HEALTH_MAINTENANCE'], tested._meta.responds_to_event_types)
        self.assertIsNotNone(tested.results())
        self.assertEqual('not_relevant', tested.status())

    def test_impacted_by_changes(self):
        patient = self.load_patient('full')
        tested = CQMImplementation(patient=patient, change_types=[])

        # no change types -> True
        result = tested.impacted_by_changes([])
        self.assertTrue(result)
        # change types + no impacting changes -> True
        result = tested.impacted_by_changes([
            'change_A',
            'change_B',
            'change_C',
        ])
        self.assertTrue(result)
        # change types + impacting changes in the changes -> True
        tested._meta.compute_on_change_types = [
            'change_X',
            'change_B',
            'change_C',
        ]
        result = tested.impacted_by_changes([
            'change_A',
            'change_B',
            'change_C',
        ])
        self.assertTrue(result)
        result = tested.impacted_by_changes([
            'change_A',
            'change_B',
        ])
        self.assertTrue(result)
        result = tested.impacted_by_changes([
            'change_C',
        ])
        self.assertTrue(result)
        # change types + impacting changes Not in the changes -> False
        result = tested.impacted_by_changes([
            'change_U',
            'change_V',
            'change_W',
        ])
        self.assertFalse(result)

    def test_period_adjustment(self):
        patient = self.load_patient('full')

        tested = TestCQM(patient=patient, now=arrow.get('2018-10-30 12:34'))
        result = tested.period_adjustment
        self.assertIsNone(result)

        patient.protocol_overrides = ProtocolOverrideRecordSet([{
            'protocolKey': 'TestCQM',
            'adjustment': {
                'reference': '2018-02-01T00:00:00Z',
                'cycleDays': 180
            },
            'snooze': None,
            'modified': '2018-03-15T12:32:54Z',
        }])  # yapf: disable
        tested = TestCQM(patient=patient, now=arrow.get('2018-10-30 12:34'))
        result = tested.period_adjustment
        self.assertEqual('2018-02-01T00:00:00Z', result['reference'])
        self.assertEqual(180, result['cycleDays'])

    def test_in_initial_population(self):
        patient = self.load_patient('full')
        # base class
        tested = CQMImplementation(patient=patient)
        result = tested.in_initial_population()
        self.assertIsNone(result)
        # implementation
        tested = TestCQM(patient=patient)
        result = tested.in_initial_population()
        self.assertTrue(result)

    def test_in_denominator(self):
        patient = self.load_patient('full')
        # base class
        tested = CQMImplementation(patient=patient)
        result = tested.in_denominator()
        self.assertIsNone(result)
        # implementation
        tested = TestCQM(patient=patient)
        result = tested.in_denominator()
        self.assertTrue(result)

    def test_in_numerator(self):
        patient = self.load_patient('full')
        # base class
        tested = CQMImplementation(patient=patient)
        result = tested.in_numerator()
        self.assertIsNone(result)
        # implementation
        tested = TestCQM(patient=patient)
        result = tested.in_numerator()
        self.assertTrue(result)

    def test_compute_results(self):
        patient = self.load_patient('full')
        # base class
        tested = CQMImplementation(patient=patient)
        result = tested.compute_results()
        self.assertIsNone(result)
        # implementation
        tested = TestCQM(patient=patient)
        result = tested.compute_results()
        self.assertIsInstance(result, ProtocolResult)
        self.assertEqual('Current', result.status)
        self.assertEqual('This is an example only', result.narrative)
        self.assertEqual(2, len(result.recommendations))
        self.assertIsInstance(result.recommendations[0], TestAResult)
        self.assertIsInstance(result.recommendations[1], TestBResult)
        # change the status --> the computation is independent of the cache
        tested.the_status = 'Pending'
        result = tested.compute_results()
        self.assertIsInstance(result, ProtocolResult)
        self.assertEqual('Pending', result.status)

    def test_results(self):
        patient = self.load_patient('full')
        # base class
        tested = CQMImplementation(patient=patient)
        result = tested.results()
        self.assertIsNone(result)
        # implementation
        tested = TestCQM(patient=patient)
        result = tested.results()
        self.assertIsInstance(result, ProtocolResult)
        self.assertEqual('Current', result.status)
        self.assertEqual('This is an example only', result.narrative)
        self.assertEqual(2, len(result.recommendations))
        self.assertIsInstance(result.recommendations[0], TestAResult)
        self.assertIsInstance(result.recommendations[1], TestBResult)
        # change the status --> the cache is not changed
        tested.the_status = 'Pending'
        result = tested.results()
        self.assertIsInstance(result, ProtocolResult)
        self.assertEqual('Current', result.status)

    def test_recommendations(self):
        patient = self.load_patient('full')
        # base class
        tested = CQMImplementation(patient=patient)
        with self.assertRaises(AttributeError):
            tested.recommendations()
        # implementation
        tested = TestCQM(patient=patient)
        result = tested.recommendations()
        self.assertEqual(2, len(result))
        self.assertIsInstance(result[0], TestAResult)
        self.assertIsInstance(result[1], TestBResult)

    def test_narrative(self):
        patient = self.load_patient('full')
        # base class
        tested = CQMImplementation(patient=patient)
        with self.assertRaises(AttributeError):
            tested.narrative()
        # implementation
        tested = TestCQM(patient=patient)
        result = tested.narrative()
        self.assertEqual('This is an example only', result)

    def test_status(self):
        patient = self.load_patient('full')
        # base class
        tested = CQMImplementation(patient=patient)
        with self.assertRaises(AttributeError):
            tested.status()
        # implementation
        tested = TestCQM(patient=patient)
        result = tested.status()
        self.assertEqual('Current', result)

    def test_due_in(self):
        patient = self.load_patient('full')
        # base class
        tested = CQMImplementation(patient=patient)
        with self.assertRaises(AttributeError):
            tested.due_in()
        # implementation
        tested = TestCQM(patient=patient)
        result = tested.due_in()
        self.assertEqual(-17, result)

    def test_days_of_notice(self):
        patient = self.load_patient('full')
        # base class
        tested = CQMImplementation(patient=patient)
        with self.assertRaises(AttributeError):
            tested.days_of_notice()
        # implementation
        tested = TestCQM(patient=patient)
        result = tested.days_of_notice()
        self.assertEqual(30, result)

    def test_next_review(self):
        patient = self.load_patient('full')
        # base class
        tested = CQMImplementation(patient=patient)
        with self.assertRaises(AttributeError):
            tested.next_review()
        # implementation
        tested = TestCQM(patient=patient)
        result = tested.next_review()
        self.assertEqual('2018-11-17T12:34:56.421', result)

        # - no due_in defined
        tested = TestCQM(patient=patient)
        tested._results = ProtocolResult()
        self.assertIsNone(tested.next_review())

        # - due_in with a negative value
        tested._results.due_in = -1
        self.assertIsNone(tested.next_review())

        # - due_in with a positive value
        tested._results.due_in = 10
        template = '%Y-%m-%d %H:%M:%S'
        expected = (datetime.utcnow() + timedelta(days=10)).strftime(template)
        template = 'YYYY-MM-DD HH:mm:ss'
        result = tested.next_review().format(template)
        self.assertEqual(expected, result)

    def test_display_date(self):
        patient = self.load_patient('full')
        # base class
        tested = CQMImplementation(patient=patient, now=arrow.get('2018-10-01'))

        tests = [
            ('2018-09-09', '3 weeks ago on 9/9/18'),
            ('2018-09-19', 'a week ago on 9/19/18'),
            ('2018-07-13', '3 months ago on 7/13/18'),
            ('2018-03-13', '7 months ago on 3/13/18'),
            ('2017-03-13', 'a year ago on 3/13/17'),
        ]
        for day, expected in tests:
            result = tested.display_date(arrow.get(day))
            self.assertEqual(expected, result)

    def test_display_period(self):
        tests = [
            ('2018-09-09', '2018-12-19', 'between 9/9/18 and 12/19/18$'),
            ('2018-07-17', '2018-08-03', 'between 7/17/18 and 8/3/18$'),
            ('2002-05-21', '2007-02-03', 'between 5/21/02 and 2/3/07$'),
        ]
        for day_from, day_to, expected in tests:
            result = ClinicalQualityMeasure.display_period(arrow.get(day_from), arrow.get(day_to))
            self.assertRegex(result, expected)

    def test_screening_interval_context(self):
        patient = self.load_patient('full')
        # no default_display_interval_in_days set
        result = ClinicalQualityMeasure(patient=patient).screening_interval_context()
        self.assertEqual(result, '')

        class CQMWithDefaultDisplayInterval(ClinicalQualityMeasure):
            class Meta:
                default_display_interval_in_days = 30

        # no period adjustment
        cqm = CQMWithDefaultDisplayInterval(patient=patient)
        result = cqm.screening_interval_context()
        self.assertEqual(result, 'Current screening interval 1 month.')
        # there is a period adjustment
        cqm = CQMWithDefaultDisplayInterval(patient=patient)
        cqm._meta.default_display_interval_in_days = 30
        cqm.period_adjustment = {'cycleDays': 60}
        result = cqm.screening_interval_context()
        self.assertEqual(result, 'Current screening interval 2 months.')

    def test_friendly_time_duration(self):
        tests = [
            (2, '2 days'),
            (30, '1 month'),
            (31, '1 month, 1 day'),
            ((30 * 2), '2 months'),
            (((30 * 2) + 2), '2 months, 2 days'),
            (365, '1 year'),
            (365 + 1, '1 year'),
            (365 + 30, '1 year, 1 month'),
            (365 + 60, '1 year, 2 months'),
            ((365 * 2) + (30 * 2), '2 years, 2 months'),
        ]
        for actual_input, expected_output in tests:
            result = ClinicalQualityMeasure.friendly_time_duration(actual_input)
            self.assertRegex(result, expected_output)


# class to be able to test the top level procedures
class TestProcedures(SDKBaseTest):

    def test_get_subclasses(self):
        result = get_subclasses(TestClassBase)
        self.assertEqual(3, len(result))
        expected = ['TestClassSubA', 'TestClassSubB', 'TestClassSubC']
        for a_class in result:
            self.assertIn(a_class.__name__, expected)

    def test_get_protocols(self):
        # result includes also the actual classes
        result = LOADED_PROTOCOLS
        self.assertEqual(2, len(result))
        self.assertIn('HEALTH_MAINTENANCE', result)
        health = list(map(lambda x: x.__name__, result['HEALTH_MAINTENANCE']))
        self.assertIn('ProtoUnitTestAllTrue', health)
        self.assertNotIn('ProtoUnitTestX', health)
        self.assertIn('ProtoUnitTestY', health)

        expected = [
            'ProtoUnitTestAllTrue',
            'ProtoUnitTestX',
            'ProtoUnitTestY',
            'ProtoUnitTestZ',
        ]
        self.assertIn('UNIT_TESTS', result)
        self.assertEqual(len(expected), len(result['UNIT_TESTS']))
        for a_class in result['UNIT_TESTS']:
            self.assertIn(a_class.__name__, expected)

    def test_protocols_for_patient(self):
        patient = self.load_patient('full')
        protocols = LOADED_PROTOCOLS
        result = protocols_for_patient(protocols['UNIT_TESTS'], patient)
        expected = [
            'ProtoUnitTestAllTrue',
            'ProtoUnitTestX',
            'ProtoUnitTestZ',
        ]
        # ProtoUnitTestY has not_applicable as status
        # ProtoUnitTestZ has not_applicable as status but has due_in not null
        self.assertEqual(len(expected), len(result))

        for instance in result:
            self.assertIn(instance.__class__.__name__, expected)
            self.assertEqual('report', instance.context)

        result = protocols_for_patient(protocols['UNIT_TESTS'], patient, context='guidance')
        expected = [
            'ProtoUnitTestAllTrue',
            'ProtoUnitTestX',
            'ProtoUnitTestZ',
        ]
        # ProtoUnitTestY has not_applicable as status
        # ProtoUnitTestZ has not_applicable as status but has due_in not null
        self.assertEqual(len(expected), len(result))

        for instance in result:
            self.assertIn(instance.__class__.__name__, expected)
            self.assertEqual('guidance', instance.context)

        # no empty change types
        result = protocols_for_patient(protocols['UNIT_TESTS'], patient, [
            'change_A',
            'change_B',
        ])
        expected = [
            'ProtoUnitTestAllTrue',
            'ProtoUnitTestX',
            'ProtoUnitTestZ',
        ]
        # ProtoUnitTestX is impacted by change_C
        # ProtoUnitTestY has not_applicable as status
        # ProtoUnitTestZ has not_applicable as status but has due_in not null
        self.assertEqual(len(expected), len(result))

        for instance in result:
            self.assertIn(instance.__class__.__name__, expected)
            if instance.__class__.__name__ == 'ProtoUnitTestX':
                self.assertEqual('not_relevant', instance.status())
            else:
                self.assertNotEqual('not_relevant', instance.status())

        # ProtoUnitTestAllTrue snoozed
        patient = self.load_patient('full')
        patient.protocol_overrides = ProtocolOverrideRecordSet([{
            'protocolKey': 'ProtoUnitTestAllTrue',
            'adjustment': None,
            'snooze': {
                'reference': arrow.now(),
                'snoozedDays': 22
            },
            'modified': '2018-10-02T21:50:09.661490Z'
        }])

        protocols = LOADED_PROTOCOLS
        result = protocols_for_patient(protocols['UNIT_TESTS'], patient)
        expected = [
            'ProtoUnitTestAllTrue',
            'ProtoUnitTestX',
            'ProtoUnitTestZ',
        ]
        # ProtoUnitTestY has not_applicable as status
        # ProtoUnitTestZ has not_applicable as status but has due_in not null
        self.assertEqual(len(expected), len(result))

        for instance in result:
            class_name = instance.__class__.__name__
            self.assertIn(class_name, expected)
            if class_name == 'ProtoUnitTestAllTrue':
                self.assertTrue(instance.snoozed(), class_name)
            else:
                self.assertFalse(instance.snoozed(), class_name)


# ---helper ---
class TestProto(Protocol):

    __test__ = False

    the_status = 'current status'

    class Meta:

        title = 'Title TestProtocol'

        references = [
            'Small title #1. www.unittests.med/canvas?id=1',
            'Small title #2. http://www.unittests.med/canvas?id=2',
            'Small title #3. https://www.unittests.med/canvas?id=3',
            'Small title #4. WWW.unittests.med/canvas?id=4',
            'Not valid #5  www.unittests.med/canvas?id=5 because of this',
        ]

    def status(self) -> str:
        return self.the_status


class TestPFalse(Protocol):

    __test__ = False

    references = []

    def status(self) -> str:
        return 'Current'

    @classmethod
    def enabled(cls) -> bool:
        return False


class CQMImplementation(ClinicalQualityMeasure):

    class Meta:
        compute_on_change_types = [
            'change_A',
            'change_B',
            'change_C',
        ]

    def in_initial_population(self) -> bool:
        pass

    def in_denominator(self) -> bool:
        pass

    def in_numerator(self) -> bool:
        pass

    def compute_results(self) -> ProtocolResult:
        pass


class TestCQM(ClinicalQualityMeasure):

    __test__ = False

    is_in_ini = True
    is_in_den = True
    is_in_num = True
    the_status = 'Current'

    identifiers = ['TestCQM']

    references = [
        'Small title #1. www.unittests.med/canvas?id=1',
    ]

    @classmethod
    def revision(cls) -> str:
        return '2019-02-12 09:54:31+00:00'

    def in_initial_population(self) -> bool:
        return self.is_in_ini

    def in_denominator(self) -> bool:
        return self.is_in_den

    def in_numerator(self) -> bool:
        return self.is_in_num

    def compute_results(self) -> ProtocolResult:
        result = ProtocolResult()
        result.status = self.the_status
        result.add_narrative('This is an example only')
        result.add_recommendation(TestAResult())
        result.add_recommendation(TestBResult())
        result.due_in = -17
        result.next_review = '2018-11-17T12:34:56.421'
        return result


class TestAResult(Recommendation):

    __test__ = False

    def __init__(self):
        command = {'type': 'TestAResult'}

        super().__init__(
            key='KEY-ID',
            rank=123,
            button='ACT',
            title='Title TestAResult',
            narrative='Narrative TestAResult',
            command=command)


class TestBResult(Recommendation):

    __test__ = False

    def __init__(self):
        command = {'type': 'TestBResult'}

        super().__init__(
            key='KEY-ID',
            rank=123,
            button='ACT',
            title='Title TestBResult',
            narrative='Narrative TestBResult',
            command=command)


class TestClassBase():

    __test__ = False


class TestClassSubA(TestClassBase):

    __test__ = False


class TestClassSubB(TestClassBase):

    __test__ = False


class TestClassSubC(TestClassSubB):

    __test__ = False
