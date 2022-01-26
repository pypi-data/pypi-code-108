import arrow

from canvas_workflow_kit.timeframe import Timeframe
from canvas_workflow_kit.value_set.v2018 import AntibioticMedicationsForPharyngitis, ContraceptiveMedications

from .base import SDKBaseTest


class SDKMedicationTest(SDKBaseTest):

    def test_medications(self):
        patient = self.load_patient('example')
        self.assertTrue(patient)

        # look for meds he doesn't have
        t = Timeframe(arrow.get('2017-01-01'), arrow.get('2018-02-01'))
        self.assertFalse(
            patient.medications.find(ContraceptiveMedications).intersects(t, still_active=False))

        # look for a med he does have
        self.assertTrue(
            patient.medications.find(AntibioticMedicationsForPharyngitis).intersects(
                t, still_active=False))
