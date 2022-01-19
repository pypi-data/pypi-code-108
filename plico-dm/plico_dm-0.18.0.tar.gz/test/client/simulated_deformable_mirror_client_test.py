#!/usr/bin/env python
import unittest
import numpy as np
from plico_dm.client.simulated_deformable_mirror_client import \
    SimulatedDeformableMirrorClient
from test.fake_time_mod import FakeTimeMod


class SimulatedDeformableMirrorClientTest(unittest.TestCase):


    def setUp(self):
        self.timeMod= FakeTimeMod()
        self.dm= SimulatedDeformableMirrorClient(timeModule=self.timeMod)
        self.nModes= SimulatedDeformableMirrorClient.N_MODES


    def testGetNumberOfModes(self):
        nModes= self.dm.getNumberOfModes()
        self.assertEqual(
            SimulatedDeformableMirrorClient.N_MODES, nModes)


    def testSetAndGetShape(self):
        wantShape=np.arange(self.nModes)
        self.dm.setShape(wantShape)
        getShape= self.dm.getShape()
        self.assertTrue(np.array_equal(wantShape, getShape))


    def testLoopSequence(self):
        timeStepInSeconds=0.1
        seqNumberOfTimeSteps= 100

        initialShape= np.arange(self.nModes) * 42
        self.dm.setShape(initialShape)
        seq= np.arange(self.nModes * seqNumberOfTimeSteps).reshape(
            self.nModes, seqNumberOfTimeSteps)
        self.dm.loadShapeSequence(seq, timeStepInSeconds)

        self.dm.startShapeSequence()
        shapeBefore= self.dm.getShape()
        self.timeMod.sleep(timeStepInSeconds * 2)
        shapeAfter= self.dm.getShape()
        self.assertFalse(np.array_equal(shapeAfter, shapeBefore))

        self.dm.stopShapeSequence()
        shapeBefore= self.dm.getShape()
        self.timeMod.sleep(timeStepInSeconds * 2)
        shapeAfter= self.dm.getShape()
        self.assertTrue(np.array_equal(shapeAfter, shapeBefore))


if __name__ == "__main__":
    unittest.main()
