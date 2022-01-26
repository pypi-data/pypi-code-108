from canvas_workflow_kit.constants import CHANGE_TYPE
from canvas_workflow_kit.utils import parse_class_from_python_source
from .base import SDKBaseTest
from canvas_workflow_kit import settings
from canvas_workflow_kit import events
from pathlib import Path
from canvas_workflow_kit.protocol import (
    ProtocolResult,
    STATUS_DUE,
    STATUS_SATISFIED,
    STATUS_NOT_APPLICABLE
)


class TemplateTest(SDKBaseTest):

    def setUp(self):
        super().setUp()
        self.mocks_path = f'{settings.BASE_DIR}/builtin_cqms/tests/mock_data'

        patient = self.load_patient('patient')
        self.base_class = self.createProtocolClass({})(patient=patient)
        self.satisfied_class = self.createProtocolClass(
            {'denominator': 'return True', 'numerator': 'return True'})(
            patient=patient)
        self.due_class = self.createProtocolClass({'denominator': 'return True',
                                                   'numerator': 'return False'})(patient=patient)

    def createProtocolClass(self, fields={}):
        template_fields = {
            'value_sets': '*',
            'year': '2022',
            'class_name': "MyClinicalQualityMeasure",
            'title': "My Clinical Quality Measure",
            'description': 'Description',
            'information_link': 'https://link_to_protocol_information',
            'types': ['CQM'],
            'authors': '"Canvas Example Medical Association (CEMA)"',
            'references': '"Gunderson, Beau;  Excellence in Software Templates. 2012 Oct 20;161(7):422-34."',
            'funding_source': '',
            'denominator': 'pass',
            'numerator': 'pass',
            **fields
        }
        template_path = Path(__file__).parent.parent / 'builtin_cqms/stub_template_user.py.txt'
        template = template_path.open('r').read()

        content = template.format(**template_fields)
        return parse_class_from_python_source(content)

    def test_base_fields(self):
        Protocol = self.base_class
        self.assertEqual('Description', Protocol._meta.description)
        self.assertEqual('My Clinical Quality Measure', Protocol._meta.title)
        self.assertEqual('2022-v1', Protocol._meta.version)
        self.assertEqual('https://link_to_protocol_information', Protocol._meta.information)
        self.assertEqual(['CMSMyClinicalQualityMeasure'], Protocol._meta.identifiers)
        self.assertEqual(['CQM'], Protocol._meta.types)
        self.assertEqual([events.HEALTH_MAINTENANCE], Protocol._meta.responds_to_event_types)
        self.assertEqual([CHANGE_TYPE.CONDITION], Protocol._meta.compute_on_change_types)
        self.assertEqual(['Canvas Example Medical Association (CEMA)'], Protocol._meta.authors)
        self.assertEqual(
            ['Gunderson, Beau;  Excellence in Software Templates. 2012 Oct 20;161(7):422-34.'],
            Protocol._meta.references)
        self.assertEqual('', Protocol._meta.funding_source)

    def test_base_numerator(self):
        tested = self.base_class

        numerator = tested.in_numerator()
        self.assertIsNone(numerator)

    def test_base_denominator(self):
        tested = self.base_class

        denominator = tested.in_denominator()
        self.assertIsNone(denominator)

    def test_base_result(self):
        tested = self.base_class
        result = tested.compute_results()

        self.assertIsInstance(result, ProtocolResult)
        self.assertEqual(STATUS_NOT_APPLICABLE, result.status)
        self.assertEqual([], result.recommendations)
        self.assertEqual('', result.narrative)
        self.assertIsNone(result.due_in)
        self.assertEqual(30, result.days_of_notice)
        self.assertIsNone(result.next_review)

    def test_satisfied_numerator(self):
        tested = self.satisfied_class

        numerator = tested.in_numerator()
        self.assertTrue(numerator)

    def test_satisfied_denominator(self):
        tested = self.satisfied_class

        denominator = tested.in_denominator()
        self.assertTrue(denominator)

    def test_satisfied_result(self):
        tested = self.satisfied_class

        result = tested.compute_results()
        self.assertIsInstance(result, ProtocolResult)
        self.assertEqual(STATUS_SATISFIED, result.status)
        self.assertEqual([], result.recommendations)
        self.assertEqual('', result.narrative)
        self.assertIsNone(result.due_in)
        self.assertEqual(30, result.days_of_notice)
        self.assertIsNone(result.next_review)

    def test_due_numerator(self):
        tested = self.due_class

        numerator = tested.in_numerator()
        self.assertFalse(numerator)

    def test_due_denominator(self):
        tested = self.due_class

        denominator = tested.in_denominator()
        self.assertTrue(denominator)

    def test_due_result(self):
        tested = self.due_class

        result = tested.compute_results()
        self.assertIsInstance(result, ProtocolResult)
        self.assertEqual(STATUS_DUE, result.status)
        self.assertEqual(
            'Nicolas has at least two eGFR measurements < 60 ml/min over the last two years suggesting renal disease. There is no associated condition on the Conditions List.',
            result.narrative)
        self.assertEqual(-1, result.due_in)
        self.assertEqual(30, result.days_of_notice)
        self.assertIsNone(result.next_review)
        self.assertEqual(len(result.recommendations), 1)

    def test_due_result_recommendation(self):
        tested = self.due_class

        result = tested.compute_results()
        recommendation = result.recommendations[0]
        self.assertEqual(recommendation.key, 'HCC002v2_RECOMMEND_DIAGNOSE')
        self.assertEqual(recommendation.rank, 1)
        self.assertEqual(recommendation.button, 'Diagnose')
        self.assertEqual(
            recommendation.title,
            'Consider updating the Conditions List to include kidney related problems as clinically appropriate')
        self.assertEqual(
            recommendation.narrative,
            'Nicolas has at least two eGFR measurements < 60 ml/min over the last two years suggesting renal disease. There is no associated condition on the Conditions List.')
        self.assertEqual(recommendation.command, {'type': 'diagnose'})
