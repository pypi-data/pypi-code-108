#!/usr/bin/env python

import unittest
import numpy as np
from plico_dm.calibration.in_memory_calibration_manager import \
    InMemoryCalibrationManager
from plico_dm.types.modal_basis import ModalBasis



class InMemoryCalibrationManagerTest(unittest.TestCase):

    def setUp(self):
        self.calibMgr= InMemoryCalibrationManager()


    def testModalBasisStorage(self):
        tag= "20140909_110800"
        originalObject= ModalBasis(np.arange(8).reshape((4, 2)))
        self.calibMgr.saveModalBasis(tag, originalObject)
        storedObject= self.calibMgr.loadModalBasis(tag)
        self.assertEqual(storedObject, originalObject)


    def testZonalCommandStorage(self):
        tag= "20181222_110000"
        originalObject= np.arange(8)
        self.calibMgr.saveZonalCommand(tag, originalObject)
        storedObject= self.calibMgr.loadZonalCommand(tag)
        self.assertTrue(np.array_equal(
            storedObject, originalObject))


if __name__ == "__main__":
    unittest.main()
