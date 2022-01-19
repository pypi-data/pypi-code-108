#!/usr/bin/env python
import os
import unittest
import shutil

import numpy as np
from palpao.calibration.calibration_manager import CalibrationManager,\
    CalibrationManagerException
from palpao.types.modal_basis import ModalBasis


class CalibrationManagerTest(unittest.TestCase):

    CALIB_DIR = os.path.join(os.getcwd(), 'calib_tmp')

    def _removeCalibrationDir(self):
        if os.path.exists(self.CALIB_DIR):
            shutil.rmtree(self.CALIB_DIR)

    def setUp(self):
        self._removeCalibrationDir()
        self.calibMgr = CalibrationManager(self.CALIB_DIR)

    def tearDown(self):
        try:
            self._removeCalibrationDir()
        except Exception:
            pass

    def _createModalBasis(self):
        return ModalBasis(np.arange(6).reshape((3, 2)))

    def test_all(self):
        self._testStorageOfModalBasis()
        self._testStorageOfZonalCommand()
        self._testInvalidTag()

    def _testStorageOfModalBasis(self):
        result = self._createModalBasis()

        self.calibMgr.saveModalBasis("foo", result)
        self.assertTrue(os.path.exists(
            os.path.join(self.CALIB_DIR, "modal_basis", "foo.fits")))

        loaded = self.calibMgr.loadModalBasis("foo")
        self.assertTrue(np.array_equal(
            result.modalToZonalMatrix, loaded.modalToZonalMatrix))

    def _testInvalidTag(self):
        res = self._createModalBasis()
        self.assertRaises(
            CalibrationManagerException,
            self.calibMgr.saveModalBasis,
            None, res)
        self.assertRaises(
            CalibrationManagerException,
            self.calibMgr.saveModalBasis,
            "", res)

        self.assertRaises(
            CalibrationManagerException,
            self.calibMgr.loadModalBasis, None)
        self.assertRaises(
            CalibrationManagerException,
            self.calibMgr.loadModalBasis, "")

    def _testStorageOfZonalCommand(self):
        result = np.random.rand(100)

        self.calibMgr.saveZonalCommand("abc", result)
        self.assertTrue(os.path.exists(
            os.path.join(self.CALIB_DIR, "zonal_command", "abc.fits")))

        loaded = self.calibMgr.loadZonalCommand("abc")
        self.assertTrue(np.array_equal(
            result, loaded))


if __name__ == "__main__":
    unittest.main()
