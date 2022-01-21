import arrow

from canvas_workflow_kit.timeframe import Timeframe
from canvas_workflow_kit.value_set.v2017 import LdlC, ProthrombinTime

from .base import SDKBaseTest


class SDKLabTest(SDKBaseTest):

    def test_lab_reports(self):
        patient = self.load_patient('example')
        self.assertTrue(patient)
        self.assertEqual(patient.first_name, 'Darey')

        # look for labs he doesn't have
        t = Timeframe(arrow.get('2017-01-17'), arrow.get('2018-01-17'))
        self.assertFalse(patient.lab_reports.find(ProthrombinTime).within(t).last())

        # look for a lab he does have
        self.assertTrue(patient.lab_reports.find(LdlC).within(t).last())

        # and the value should come back
        self.assertEqual(patient.lab_reports.find(LdlC).within(t).last()['value'], '120')

        # but if we move the timeframe it shouldn't come back
        t2 = Timeframe(arrow.get('2016-01-17'), arrow.get('2017-01-17'))
        self.assertFalse(patient.lab_reports.find(LdlC).within(t2).last())
        self.assertEqual(patient.lab_reports.find(LdlC).within(t2).last(), None)
