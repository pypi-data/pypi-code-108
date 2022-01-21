import arrow

from canvas_workflow_kit.timeframe import Timeframe
from canvas_workflow_kit.value_set.v2018 import Height, DeltaSystolicBloodPressure

from .base import SDKBaseTest


class SDKVitalsignTest(SDKBaseTest):

    def test_vitalsigns(self):
        patient = self.load_patient('bmi1')
        self.assertTrue(patient)
        self.assertEqual(patient.first_name, 'Bee')

        # look for vitals he doesn't have
        t = Timeframe(arrow.get('2017-02-04'), arrow.get('2018-02-04'))
        self.assertFalse(patient.vital_signs.within(t).find(DeltaSystolicBloodPressure))

        # look for a lab he does have
        self.assertTrue(patient.vital_signs.within(t).find(Height))

        # but if we move the timeframe it shouldn't come back
        t2 = Timeframe(arrow.get('2016-01-17'), arrow.get('2017-01-17'))
        self.assertFalse(patient.vital_signs.within(t2).find(Height))
