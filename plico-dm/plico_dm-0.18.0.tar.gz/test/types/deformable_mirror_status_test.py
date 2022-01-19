#!/usr/bin/env python
import unittest
import numpy as np
from plico_dm.types.deformable_mirror_status import DeformableMirrorStatus



class DeformableMirrorStatusTest(unittest.TestCase):


    def testHappyPath(self):
        numberOfActs= 10
        numberOfModes= 8
        actuatorCommands= np.arange(numberOfActs)
        commandCounter= 42
        status= DeformableMirrorStatus(
            numberOfActs,
            numberOfModes,
            actuatorCommands,
            commandCounter)

        self.assertEqual(numberOfActs, status.numberOfActuators())
        self.assertEqual(numberOfModes, status.numberOfModes())
        self.assertTrue(np.allclose(
            actuatorCommands, status.actuatorCommands()))
        self.assertEqual(commandCounter, status.commandCounter())


if __name__ == "__main__":
    unittest.main()
