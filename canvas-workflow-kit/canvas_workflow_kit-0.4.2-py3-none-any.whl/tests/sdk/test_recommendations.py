from canvas_workflow_kit.recommendation import Recommendation, LabRecommendation
from canvas_workflow_kit.value_set.v2018 import Diabetes, Hba1CLaboratoryTest

from .base import SDKBaseTest


class SDKLabTest(SDKBaseTest):

    def test_lab_recommendation(self):
        patient = self.load_patient('example')
        self.assertTrue(patient)

        rec = LabRecommendation(
            key='KEY-ID',
            rank=123,
            button='ACT',
            patient=patient,
            lab=Hba1CLaboratoryTest,
            condition=Diabetes)
        self.assertTrue(rec)
        self.assertIn('Diabetes', rec.narrative)
        self.assertIn('HbA1c', rec.narrative)
        self.assertIn('lab', rec.command['type'])

    def test_basic_recommendation(self):
        rec = Recommendation(
            key='KEY-ID',
            rank=123,
            button='ACT',
            title='Do Something',
            narrative="'I'm not sure what, but do something!'")
        self.assertTrue(rec)
        self.assertEqual(rec.command, {})
