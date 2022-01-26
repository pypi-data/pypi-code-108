import arrow

from canvas_workflow_kit.timeframe import Timeframe
from canvas_workflow_kit.value_set.v2018 import TobaccoUseScreening, AdultDepressionScreening

from .base import SDKBaseTest


class SDKInterviewTest(SDKBaseTest):

    def test_interviews(self):
        patient = self.load_patient('example')
        self.assertTrue(patient)

        # look for interview he doesn't have
        t = Timeframe(arrow.get('2017-01-01'), arrow.get('2018-02-01'))
        self.assertFalse(patient.interviews.find(AdultDepressionScreening).within(t).last())

        # look for an interview he does have
        self.assertTrue(patient.interviews.find(TobaccoUseScreening).within(t).last())
