import arrow

from canvas_workflow_kit import builtin_cqms
from canvas_workflow_kit.builtin_cqms.cms122v6_diabetes_hemoglobin_a1c_poor_control import (
    ClinicalQualityMeasure122v6
)
from canvas_workflow_kit.builtin_cqms.cms123v6_diabetes_foot_exam import ClinicalQualityMeasure123v6
from canvas_workflow_kit.builtin_cqms.cms131v6_diabetes_eye_exam import ClinicalQualityMeasure131v6
from canvas_workflow_kit.builtin_cqms.cms134v6_diabetes_medical_attention_for_nephropathy import (
    ClinicalQualityMeasure134v6
)
from canvas_workflow_kit.protocol import get_protocols  # , STATUS_NOT_APPLICABLE
from canvas_workflow_kit.recommendation import (
    InterviewRecommendation,
    LabRecommendation,
    PerformRecommendation,
    ReferRecommendation
)
from canvas_workflow_kit.timeframe import Timeframe

from .base import SDKBaseTest

# from protocols.value_set import v2018


class SDKProtocolTest(SDKBaseTest):

    def setUp(self):
        super().setUp()
        self.protocols = get_protocols(builtin_cqms)

    def test_cms122v6(self):
        now = arrow.get('2018-08-23 13:24:56')
        # diabetic1 hasn't had a hab1c test, should tell him to get one
        patient = self.load_patient('diabetic1')
        protocol = ClinicalQualityMeasure122v6(now=now, patient=patient)
        self.assertTrue(protocol.in_denominator())

        recs = protocol.recommendations()
        self.assertEqual(len(recs), 1)
        self.assertTrue(isinstance(recs[0], LabRecommendation))
        self.assertEqual(protocol.status(), 'due')
        self.assertIn('last hba1c test', protocol.narrative().lower())

        # diabetic2 has had a test but it was too long ago, same result
        patient = self.load_patient('diabetic2')
        protocol = ClinicalQualityMeasure122v6(now=now, patient=patient)
        self.assertTrue(protocol.in_denominator())

        recs = protocol.recommendations()
        self.assertEqual(len(recs), 1)
        self.assertTrue(isinstance(recs[0], LabRecommendation))
        self.assertEqual(protocol.status(), 'due')
        self.assertIn('last hba1c test', protocol.narrative().lower())

        # diabetic3 is doing great, good job diabetic3!
        patient = self.load_patient('diabetic3')
        protocol = ClinicalQualityMeasure122v6(now=now, patient=patient)
        self.assertTrue(protocol.in_denominator())

        recs = protocol.recommendations()
        self.assertEqual(len(recs), 0)
        self.assertEqual(protocol.status(), 'satisfied')
        self.assertIn('last hba1c', protocol.narrative().lower())

        # diabetic4 had a recent test but it was bad.
        patient = self.load_patient('diabetic4')
        protocol = ClinicalQualityMeasure122v6(now=now, patient=patient)
        self.assertTrue(protocol.in_denominator())

        recs = protocol.recommendations()
        self.assertEqual(len(recs), 1)
        self.assertEqual(protocol.status(), 'due')
        self.assertIn('last hba1c', protocol.narrative().lower())

    def test_cms123v6(self):
        # not yet screened, should get a screening
        patient = self.load_patient('diabetic1')
        now = arrow.get('2017-11-01 12:00:00')
        timeframe = Timeframe(
            start=now.replace(hour=0, minute=0), end=now.replace(hour=23, minute=59))
        protocol = ClinicalQualityMeasure123v6(patient=patient, timeframe=timeframe)
        self.assertTrue(protocol.in_denominator())

        recs = protocol.recommendations()
        self.assertEqual(len(recs), 1)
        self.assertTrue(isinstance(recs[0], InterviewRecommendation))
        # self.assertTrue(isinstance(recs[1], InterviewRecommendation))
        # self.assertTrue(isinstance(recs[2], InterviewRecommendation))
        self.assertEqual(protocol.status(), 'due')
        self.assertIn('foot', protocol.narrative().lower())

        # got screened, satisfied
        patient = self.load_patient('feet1')
        protocol = ClinicalQualityMeasure123v6(patient=patient, timeframe=timeframe)
        self.assertTrue(protocol.in_denominator())

        recs = protocol.recommendations()
        self.assertEqual(len(recs), 0)
        self.assertEqual(protocol.status(), 'satisfied')

    def test_cms134v6(self):
        # not yet tested, should get a test
        patient = self.load_patient('diabetic1')
        now = arrow.get('2017-11-01 12:00:00')
        timeframe = Timeframe(
            start=now.replace(hour=0, minute=0), end=now.replace(hour=23, minute=59))
        protocol = ClinicalQualityMeasure134v6(patient=patient, timeframe=timeframe)
        self.assertTrue(protocol.in_denominator())

        recs = protocol.recommendations()
        self.assertEqual(len(recs), 1)
        self.assertTrue(isinstance(recs[0], LabRecommendation))
        self.assertEqual(protocol.status(), 'due')
        self.assertIn('urine', protocol.narrative().lower())

    def test_cms131v6(self):
        # not yet tested, should get a test
        patient = self.load_patient('diabetic1')
        now = arrow.get('2017-11-01 12:00:00')
        timeframe = Timeframe(
            start=now.replace(hour=0, minute=0), end=now.replace(hour=23, minute=59))
        protocol = ClinicalQualityMeasure131v6(patient=patient, timeframe=timeframe)
        self.assertTrue(protocol.in_denominator())

        recs = protocol.recommendations()
        self.assertEqual(len(recs), 2)
        self.assertTrue(isinstance(recs[0], PerformRecommendation))
        self.assertTrue(isinstance(recs[1], ReferRecommendation))
        self.assertEqual(protocol.status(), 'due')
        self.assertIn('retinal', protocol.narrative().lower())
