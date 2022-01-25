# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2016-2017 European Synchrotron Radiation Facility
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# ###########################################################################*/

__authors__ = ["PJ. Gouttenoire", "H. Payno"]
__license__ = "MIT"
__date__ = "23/04/2018"

import logging
import os
import shutil
import tempfile
import unittest
import socket
from glob import glob
from tomwer.core.process.reconstruction.pyhst.pyhstcaller import PyHSTCaller
from tomwer.core.utils.pyhstutils import _findPyHSTVersions, _getPyHSTDir
from tomwer.test.utils import UtilsTest, rebaseParFile
from tomwer.core.utils import getParametersFromParOrInfo
from tomwer.core.process.reconstruction.ftseries.params import ReconsParams
from tomwer.core.process.reconstruction.ftseries.params.paganin import PaganinMode
from tomwer.core.scan.edfscan import EDFTomoScan
from tomwer.core.utils.device import CudaDevice
from tomwer.core.utils.scanutils import MockEDF
from tomwer.core.process.reconstruction.ftseries.params.ft import FixedSliceMode
from tomwer.core import settings
import pytest


logging.disable(logging.INFO)

pyhstVersion = _findPyHSTVersions(_getPyHSTDir())


@pytest.mark.skipif(len(pyhstVersion) == 0, reason="PyHST2 missing")
class TestRecHSTCreation(unittest.TestCase):
    """
    Test that rec HST file are correctly processing
    """

    def setUp(self):
        self.topDir = tempfile.mkdtemp()
        self.dataset = "scan_3_"
        dataTestDir = UtilsTest.getEDFDataset(self.dataset)
        self.targetFolder = os.path.join(self.topDir, self.dataset)
        shutil.copytree(dataTestDir, self.targetFolder)

        self.parFile = os.path.join(self.targetFolder, self.dataset + ".par")
        self.parSliceFile = os.path.join(self.targetFolder, self.dataset + "slice.par")

        for pFile in (self.parFile, self.parSliceFile):
            rebaseParFile(
                filePath=pFile,
                scanOldPath="/lbsram/data/visitor/mi1226/id19/nemoz/henri/",
                scanNewPath=os.path.join(self.topDir),
            )
            rebaseParFile(
                filePath=pFile,
                scanOldPath="/data/visitor/mi1226/id19/nemoz/henri/",
                scanNewPath=os.path.join(self.topDir),
            )

    def tearDown(self):
        for folder in (self.targetFolder, self.topDir):
            shutil.rmtree(folder)

    def testRecFileCreation(self):
        """Check if the PyHST caller is able to create the .rec file"""
        rec_file = os.path.join(self.targetFolder, self.dataset + ".rec")
        par_file = os.path.join(self.targetFolder, self.dataset + ".par")
        PyHSTCaller.make_rec_file(
            rec_file=rec_file, par_file=par_file, recons_params=ReconsParams()
        )
        self.assertTrue(os.path.isfile(rec_file))


class TestParFile(unittest.TestCase):
    """Test the behavior of the `makeParFile` function"""

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def setUp(self):
        # prepare dataset
        self.datasetID = "test10"
        self.tmpdir = tempfile.mkdtemp()
        self.test10_folder = os.path.join(self.tmpdir, self.datasetID)
        test10_path = UtilsTest().getEDFDataset(self.datasetID)
        shutil.copytree(src=test10_path, dst=self.test10_folder)

        # create scan
        self.scan = EDFTomoScan(scan=self.test10_folder)
        self.scan.ftseries_recons_params = ReconsParams(empty=False)
        self.reconsparams = self.scan.ftseries_recons_params
        self.reconsparams.ft.do_test_slice = False
        self.file_prefix = os.path.join(
            self.scan.path, os.path.basename(self.scan.path)
        )
        self.par_file = self.file_prefix + ".par"
        if os.path.exists(self.par_file):
            os.remove(self.par_file)
        self.assertFalse(os.path.exists(self.par_file))

    def testGenericReconsParameters(self):
        pyhst_caller = PyHSTCaller(
            inputs={
                "data": self.scan,
                "dry_run": True,
                "pyhst2_params": self.reconsparams,
            }
        )
        pyhst_caller.run()
        self.assertTrue(os.path.exists(self.par_file))
        par_file_parameters = getParametersFromParOrInfo(self.par_file)
        assert len(par_file_parameters) > 0
        waited_values = {
            "MULTIFRAME": "0",
            "FILE_PREFIX": self.file_prefix,
            "NUM_FIRST_IMAGE": "0",
            "NUM_LAST_IMAGE": "19",
            "NUMBER_LENGTH_VARIES": "NO",
            "LENGTH_OF_NUMERICAL_PART": "4",
            "FILE_POSTFIX": ".edf",
            "FILE_INTERVAL": "1",
            "NUM_IMAGE_1": "2048",
            "NUM_IMAGE_2": "2048",
            "IMAGE_PIXEL_SIZE_1": "3.020000",
            "IMAGE_PIXEL_SIZE_2": "3.020000",
            "SUBTRACT_BACKGROUND": "YES",
            "BACKGROUND_FILE": os.path.join(self.scan.path, "dark.edf"),
            "CORRECT_FLATFIELD": "YES",
            "FLATFIELD_CHANGING": "YES",
            "FLATFIELD_FILE": "refHST0000.edf",
            "FF_PREFIX": os.path.join(self.scan.path, "refHST"),
            "FF_NUM_FIRST_IMAGE": "0",
            "FF_NUM_LAST_IMAGE": "20",
            "FF_NUMBER_LENGTH_VARIES": "NO",
            "FF_LENGTH_OF_NUMERICAL_PART": "4",
            "FF_POSTFIX": ".edf",
            "FF_FILE_INTERVAL": "20",
            "TAKE_LOGARITHM": "YES",
            "ANGLE_BETWEEN_PROJECTIONS": "9.000000",
            "ROTATION_VERTICAL": "YES",
            "ROTATION_AXIS_POSITION": "1024.000000",
            "OUTPUT_SINOGRAMS": "NO",
            "OUTPUT_RECONSTRUCTION": "YES",
            "START_VOXEL_1": "1",
            "START_VOXEL_2": "1",
            "START_VOXEL_3": "1",
            "END_VOXEL_1": "2048",
            "END_VOXEL_2": "2048",
            "END_VOXEL_3": "2048",
            "OVERSAMPLING_FACTOR": "4",
            "ANGLE_OFFSET": "0.000000",
        }
        for key, value in waited_values.items():
            with self.subTest(key=key, value=value):
                self.assertTrue(key.lower() in par_file_parameters)
                self.assertEqual(value, par_file_parameters[key.lower()])

    def testOutputMode(self):
        """Test that the putput mode is correctly write"""
        for file_ext, is_vol in zip((".vol", ".edf"), (True, False)):
            with self.subTest(file_ext=file_ext):
                self.reconsparams.ft.vol_out_file = is_vol
                pyhst_caller = PyHSTCaller(
                    inputs={
                        "data": self.scan,
                        "dry_run": True,
                        "pyhst2_params": self.reconsparams,
                    }
                )
                pyhst_caller.run()
                self.assertTrue(os.path.exists(self.par_file))
                par_file_parameters = getParametersFromParOrInfo(self.par_file)
                self.assertTrue("OUTPUT_FILE".lower() in par_file_parameters)
                output_file = par_file_parameters["OUTPUT_FILE".lower()]
                self.assertEqual(
                    output_file,
                    os.path.join(
                        self.scan.path, os.path.basename(self.scan.path) + file_ext
                    ),
                )

    def testPaganinOff(self):
        """Test par generation if paganin mode is off"""
        self.reconsparams.paganin.mode = PaganinMode.off
        pyhst_caller = PyHSTCaller(
            inputs={
                "data": self.scan,
                "dry_run": True,
                "pyhst2_params": self.reconsparams,
            }
        )
        pyhst_caller.run()
        self.assertTrue(os.path.exists(self.par_file))
        par_file_parameters = getParametersFromParOrInfo(self.par_file)
        self.assertFalse("DO_PAGANIN" in par_file_parameters)
        self.assertFalse("MULTI_PAGANIN_PARS".lower() in par_file_parameters)

    def testPaganinOn(self):
        """Test par generation if paganin mode is on"""
        self.reconsparams.paganin.mode = PaganinMode.on
        self.par_file = os.path.join(self.scan.path, "test10pag_0500.par")
        pyhst_caller = PyHSTCaller(
            inputs={
                "data": self.scan,
                "dry_run": True,
                "pyhst2_params": self.reconsparams,
            }
        )
        pyhst_caller.run()
        self.assertTrue(os.path.exists(self.par_file))

        waited_values = {
            "PAGANIN_Lmicron": "500.000000",
            "PAGANIN_MARGE": "200",
            "DO_OUTPUT_PAGANIN": "0",
            "OUTPUT_PAGANIN_FILE": "paga_cufft",
            "PAGANIN_TRY_CUFFT": "1",
            "PAGANIN_TRY_FFTW": "1",
            "UNSHARP_LOG": "1",
            "PUS": "0.800000",
            "PUC": "3.000000",
            "TRYEDFCONSTANTHEADER": "1",
            "OUTPUT_FILE": self.file_prefix + "pag_0500.edf",
        }
        par_file_parameters = getParametersFromParOrInfo(self.par_file)
        self.assertTrue("DO_PAGANIN".lower() in par_file_parameters)
        self.assertEqual(par_file_parameters["DO_PAGANIN".lower()], "1")

        for key, value in waited_values.items():
            with self.subTest(key=key, value=value):
                self.assertTrue(key.lower() in par_file_parameters)
                self.assertEqual(value, par_file_parameters[key.lower()])

        # test with other values
        self.reconsparams.paganin.mode = PaganinMode.multi
        self.reconsparams.paganin.db = 10
        self.reconsparams.paganin.db2 = 1000
        self.reconsparams.paganin.unsharp_sigma = 0.36
        self.reconsparams.paganin.unsharp_coeff = 0.87
        self.reconsparams.paganin.median_r = 1.25
        self.reconsparams.paganin.dilate = 1.69
        self.reconsparams.paganin.mkeep_soft = True

        pyhst_caller = PyHSTCaller(
            inputs={
                "data": self.scan,
                "dry_run": True,
                "pyhst2_params": self.reconsparams,
            }
        )
        pyhst_caller.run()
        waited_values = {
            "PAGANIN_Lmicron": "%.6f" % self.reconsparams.paganin.db,
            "PAGANIN_MARGE": "200",
            "PUS": "%f" % self.reconsparams.paganin.unsharp_sigma,
            "PUC": "%f" % self.reconsparams.paganin.unsharp_coeff,
        }
        self.par_file = os.path.join(
            self.scan.path,
            os.path.basename(self.scan.path) + "multipag_db0010-db1000.par",
        )
        self.assertTrue(os.path.exists(self.par_file))
        par_file_parameters = getParametersFromParOrInfo(self.par_file)
        for key, value in waited_values.items():
            with self.subTest(key=key, value=value):
                self.assertTrue(key.lower() in par_file_parameters)
                self.assertEqual(value, par_file_parameters[key.lower()])
        self.assertTrue("MULTI_PAGANIN_PARS".lower() in par_file_parameters)

    def testPaganinBoth(self):
        """Test par generation if paganin mode is both"""
        db = self.scan.ftseries_recons_params.paganin.db
        self.par_file = os.path.join(
            self.scan.path, os.path.basename(self.scan.path) + "pag_%04d.par" % db
        )
        self.reconsparams.paganin.mode = PaganinMode.both
        pyhst_caller = PyHSTCaller(
            inputs={
                "data": self.scan,
                "dry_run": True,
                "pyhst2_params": self.reconsparams,
            }
        )
        pyhst_caller.run()
        self.assertTrue(os.path.exists(self.par_file))
        par_file_parameters = getParametersFromParOrInfo(self.par_file)
        self.assertTrue("DO_PAGANIN".lower() in par_file_parameters)
        self.assertEqual(par_file_parameters["DO_PAGANIN".lower()], "1")
        self.assertFalse("MULTI_PAGANIN_PARS".lower() in par_file_parameters)

    def testPaganinMulti(self):
        """Test par generation if paganin mode is multi"""
        db = self.scan.ftseries_recons_params.paganin.db
        db2 = self.scan.ftseries_recons_params.paganin.db2
        self.par_file = os.path.join(
            self.scan.path,
            os.path.basename(self.scan.path) + "multipag_db%04d-db%04d.par" % (db, db2),
        )
        self.reconsparams.paganin.mode = PaganinMode.multi
        pyhst_caller = PyHSTCaller(
            inputs={
                "data": self.scan,
                "dry_run": True,
                "pyhst2_params": self.reconsparams,
            }
        )
        pyhst_caller.run()
        self.assertTrue(os.path.exists(self.par_file))
        par_file_parameters = getParametersFromParOrInfo(self.par_file)
        self.assertTrue("DO_PAGANIN".lower() in par_file_parameters)
        self.assertEqual(par_file_parameters["DO_PAGANIN".lower()], "1")
        self.assertTrue("MULTI_PAGANIN_PARS".lower() in par_file_parameters)
        waited_values = {
            'MULTI_PAGANIN_PARS["DILATE"]': str(self.reconsparams.paganin.dilate),
            'MULTI_PAGANIN_PARS["MEDIANR"]': str(self.reconsparams.paganin.median_r),
            'MULTI_PAGANIN_PARS["THRESHOLD"]': "%1.3f"
            % self.reconsparams.paganin.threshold,
            'MULTI_PAGANIN_PARS["BONE_Lmicron"]': "%.6f"
            % self.reconsparams.paganin.db2,
        }
        for key, value in waited_values.items():
            with self.subTest(key=key, value=value):
                self.assertTrue(key.lower() in par_file_parameters)
                self.assertEqual(value, par_file_parameters[key.lower()])

        # test with some other random values
        self.reconsparams.paganin.dilate = 1
        self.reconsparams.paganin.median_r = 3
        self.reconsparams.paganin.threshold = 400.0
        pyhst_caller = PyHSTCaller(
            inputs={
                "data": self.scan,
                "dry_run": True,
                "pyhst2_params": self.reconsparams,
            }
        )
        pyhst_caller.run()
        par_file_parameters = getParametersFromParOrInfo(self.par_file)
        waited_values = {
            'MULTI_PAGANIN_PARS["DILATE"]': str(self.reconsparams.paganin.dilate),
            'MULTI_PAGANIN_PARS["MEDIANR"]': str(self.reconsparams.paganin.median_r),
            'MULTI_PAGANIN_PARS["THRESHOLD"]': "%1.3f"
            % self.reconsparams.paganin.threshold,
        }
        for key, value in waited_values.items():
            with self.subTest(key=key, value=value):
                self.assertTrue(key.lower() in par_file_parameters)
                self.assertEqual(value, par_file_parameters[key.lower()])


class TestMultipleReconsParams(unittest.TestCase):
    """Test the reconstruction parameters that can have several values."""

    def setUp(self) -> None:
        super(TestMultipleReconsParams, self).setUp()
        self.inputdir = tempfile.mkdtemp()
        mock = MockEDF(scan_path=self.inputdir, n_radio=10, n_ini_radio=10)
        mock.end_acquisition()
        info_file = mock.get_info_file()
        assert os.path.exists(info_file)
        self.scan = EDFTomoScan(scan=mock.scan_path)
        self.scan.ftseries_recons_params = ReconsParams()
        self.scan.ftseries_recons_params.ft.do_test_slice = False
        self.pyhst_caller = PyHSTCaller(
            inputs={
                "pyhst2_params": self.scan.ftseries_recons_params,
                "data": self.scan,
                "dry_run": True,
            }
        )
        par_files = glob(self.scan.path + os.sep + "*.par")
        self.assertEqual(len(par_files), 0)

    def tearDown(self) -> None:
        super(TestMultipleReconsParams, self).tearDown()
        shutil.rmtree(self.inputdir)

    def test_off(self):
        """Test that .par file will be generated with the 'default' name
        if no paganin requested"""
        self.scan.ftseries_recons_params.paganin.mode = PaganinMode.off
        self.scan.ftseries_recons_params.paganin.db = [100.0, 200.0]
        # remove all .par file
        self.assertEqual(len(glob(self.scan.path + os.sep + "*.par")), 0)
        self.pyhst_caller.run()
        par_files = glob(self.scan.path + os.sep + "*.par")
        self.assertEqual(len(par_files), 1)
        basename = os.path.basename(self.scan.path)
        self.assertTrue(par_files[0] == os.path.join(self.scan.path, basename + ".par"))

    def test_multi(self):
        """
        Make sure pyhscaller will create several .par file if several
        values of delta/beta are requested and paganin mode is `multi`
        """
        self.scan.ftseries_recons_params.paganin.mode = PaganinMode.multi
        self.scan.ftseries_recons_params.paganin.db = [100.0, 200.0]
        self.scan.ftseries_recons_params.paganin.db2 = [100.0]
        # remove all .par file
        self.assertEqual(len(glob(self.scan.path + os.sep + "*.par")), 0)
        self.pyhst_caller.run()
        par_files = glob(self.scan.path + os.sep + "*.par")
        self.assertEqual(len(par_files), 2)
        basename = os.path.basename(self.scan.path)
        for file_name in (
            basename + "multipag_db0200-db0100.par",
            basename + "multipag_db0100-db0100.par",
        ):
            full_file_path = os.path.join(self.scan.path, file_name)
            self.assertTrue(full_file_path in par_files)

    def test_on_several_value(self):
        """Test .par files generated if paga is `on`"""
        self.scan.ftseries_recons_params.paganin.mode = PaganinMode.on
        self.scan.ftseries_recons_params.paganin.db = [100.0, 200.0]
        # remove all .par file
        self.assertEqual(len(glob(self.scan.path + os.sep + "*.par")), 0)
        self.pyhst_caller.run()
        par_files = glob(self.scan.path + os.sep + "*.par")
        self.assertEqual(len(par_files), 2)
        basename = os.path.basename(self.scan.path)
        for file_name in (basename + "pag_0200.par", basename + "pag_0100.par"):
            full_file_path = os.path.join(self.scan.path, file_name)
            self.assertTrue(full_file_path in par_files)

    def test_both(self):
        """Test .par file generated if paga is `both`"""
        self.scan.ftseries_recons_params.paganin.mode = PaganinMode.both
        self.scan.ftseries_recons_params.paganin.db = [100.0, 200.0]
        # remove all .par file
        self.assertEqual(len(glob(self.scan.path + os.sep + "*.par")), 0)
        self.pyhst_caller.run()
        par_files = glob(self.scan.path + os.sep + "*.par")
        self.assertEqual(len(par_files), 2)
        basename = os.path.basename(self.scan.path)
        for file_name in (basename + "pag_0200.par", basename + "pag_0100.par"):
            full_file_path = os.path.join(self.scan.path, file_name)
            self.assertTrue(full_file_path in par_files)


class TestUtils(unittest.TestCase):
    """Test utils functions"""

    def test_get_gpu_command(self):
        device_0 = CudaDevice(name="device1", id_=0)
        device_1 = CudaDevice(name="device2", id_=1)
        expected_res = socket.gethostname() + ",0"
        self.assertEqual(PyHSTCaller._get_gpu_command((device_0,)), expected_res)

        expected_res = socket.gethostname() + ",1,0"
        self.assertEqual(
            PyHSTCaller._get_gpu_command((device_1, device_0)), expected_res
        )


class TestSlices(unittest.TestCase):
    """Test that the slices parameter is well managed"""

    def setUp(self) -> None:
        super(TestSlices, self).setUp()
        self.inputdir = tempfile.mkdtemp()
        mock = MockEDF(scan_path=self.inputdir, n_radio=10, n_ini_radio=10)
        mock.end_acquisition()
        info_file = mock.get_info_file()
        assert os.path.exists(info_file)
        self.scan = EDFTomoScan(scan=mock.scan_path)
        self.scan.ftseries_recons_params = ReconsParams()
        self.pyhst_caller = PyHSTCaller(
            inputs={
                "data": self.scan,
                "dry_run": True,
                "pyhst2_params": self.scan.ftseries_recons_params,
            }
        )
        self.assertEqual(len(glob(self.scan.path + os.sep + "*.par")), 0)

    def tearDown(self) -> None:
        super(TestSlices, self).tearDown()
        shutil.rmtree(self.inputdir)

    def testNoSlices(self):
        """Test that .par file will be generated with the 'default' name
        if no Paganin requested"""
        self.scan.ftseries_recons_params.ft.do_test_slice = False
        self.pyhst_caller.run()
        par_files = glob(self.scan.path + os.sep + "*.par")
        self.assertEqual(len(par_files), 1)
        basename = os.path.basename(self.scan.path)
        self.assertTrue(par_files[0] == os.path.join(self.scan.path, basename + ".par"))

    def testSingleMiddleSliceNoPag(self):
        """Make sure par file name are correct regarding the do_test and
        the fixed_slice parameter"""
        self.scan.ftseries_recons_params.ft.do_test_slice = True
        self.scan.ftseries_recons_params.ft.fixed_slice = FixedSliceMode.middle
        self.pyhst_caller.run()
        par_files = glob(self.scan.path + os.sep + "*.par")
        self.assertEqual(len(par_files), 2)
        basename = os.path.basename(self.scan.path)
        full_rec_par_file = os.path.join(self.scan.path, basename + ".par")
        self.assertTrue(full_rec_par_file in par_files)

        # check the one with slices
        middle_slice_rec_par_file = (
            basename + "slice_" + str(self.scan.dim_2 // 2).zfill(4)
        )
        middle_slice_rec_par_file = os.path.join(
            self.scan.path, middle_slice_rec_par_file + ".par"
        )
        self.assertTrue(middle_slice_rec_par_file in par_files)

    def testSingleRowNSliceNoPag(self):
        """Make sure par file name are correct regarding the do_test and
        the row_n parameter"""
        self.scan.ftseries_recons_params.ft.do_test_slice = True
        self.scan.ftseries_recons_params.ft.fixed_slice = 2
        self.pyhst_caller.run()
        par_files = glob(self.scan.path + os.sep + "*.par")
        self.assertEqual(len(par_files), 2)
        basename = os.path.basename(self.scan.path)
        full_rec_par_file = os.path.join(self.scan.path, basename + ".par")
        self.assertTrue(full_rec_par_file in par_files)

        # check the one with slices
        middle_slice_rec_par_file = basename + "slice_" + str(2).zfill(4)
        middle_slice_rec_par_file = os.path.join(
            self.scan.path, middle_slice_rec_par_file + ".par"
        )
        self.assertTrue(middle_slice_rec_par_file in par_files)

    def testSingleSliceSeveralPag(self):
        """Test that all .par files for paganin and n rows are created
        if requested"""
        self.scan.ftseries_recons_params.ft.do_test_slice = True
        self.scan.ftseries_recons_params.ft.fixed_slice = 4
        self.scan.ftseries_recons_params.paganin.mode = PaganinMode.both
        self.scan.ftseries_recons_params.paganin.db = [100.0, 200.0]
        self.pyhst_caller.run()
        par_files = glob(self.scan.path + os.sep + "*.par")
        self.assertEqual(len(par_files), 4)
        basename = os.path.basename(self.scan.path)
        # check the .par for full reconstruction
        for file_name in (basename + "pag_0200.par", basename + "pag_0100.par"):
            full_file_path = os.path.join(self.scan.path, file_name)
            self.assertTrue(full_file_path in par_files)

        # check the .par for the middle slice
        # check the .par for full reconstruction
        file_slice_pag_1 = (
            basename
            + "slice_pag_0200_"
            + str(self.scan.ftseries_recons_params.ft.fixed_slice).zfill(4)
            + ".par"
        )
        file_slice_pag_2 = (
            basename
            + "slice_pag_0100_"
            + str(self.scan.ftseries_recons_params.ft.fixed_slice).zfill(4)
            + ".par"
        )
        for file_name in (file_slice_pag_1, file_slice_pag_2):
            full_file_path = os.path.join(self.scan.path, file_name)
            self.assertTrue(full_file_path in par_files)

    def testSeveralSliceNoPag(self):
        """Make sure .par file generated for several slice (using n row)
        are correct if no paganin is activated"""
        slices = (2, 56, 89)
        self.scan.ftseries_recons_params.ft.do_test_slice = True
        self.scan.ftseries_recons_params.ft.fixed_slice = slices
        self.scan.ftseries_recons_params.paganin.mode = PaganinMode.off
        self.pyhst_caller.run()
        par_files = glob(self.scan.path + os.sep + "*.par")
        self.assertEqual(len(par_files), 4)
        basename = os.path.basename(self.scan.path)
        full_rec_par_file = os.path.join(self.scan.path, basename + ".par")
        self.assertTrue(full_rec_par_file in par_files)

        # check the one with slices
        for slice in slices:
            slice_rec_par_file = basename + "slice_" + str(slice).zfill(4)
            slice_rec_par_file = os.path.join(
                self.scan.path, slice_rec_par_file + ".par"
            )
            self.assertTrue(slice_rec_par_file in par_files)

    def testSeveralSliceAndSinglePag(self):
        """Make sure .par file generated for several slice (using n row)
        are correct if only a single paganin is requested"""
        slices = (2, 56, 89)
        self.scan.ftseries_recons_params.ft.do_test_slice = True
        self.scan.ftseries_recons_params.ft.fixed_slice = slices
        self.scan.ftseries_recons_params.paganin.mode = PaganinMode.on
        self.scan.ftseries_recons_params.paganin.db = 100.0
        self.pyhst_caller.run()
        par_files = glob(self.scan.path + os.sep + "*.par")
        self.assertEqual(len(par_files), 4)
        basename = os.path.basename(self.scan.path)
        full_rec_par_file = os.path.join(self.scan.path, basename + "pag_0100.par")
        self.assertTrue(full_rec_par_file in par_files)

        # check the one with slices
        for slice in slices:
            slice_rec_par_file = (
                basename
                + "slice_pag_"
                + "%04d_" % self.scan.ftseries_recons_params.paganin.db
                + str(slice).zfill(4)
            )
            slice_rec_par_file = os.path.join(
                self.scan.path, slice_rec_par_file + ".par"
            )
            self.assertTrue(slice_rec_par_file in par_files)

    def testSeveralSliceAndSeveralPag(self):
        """Make sure .par file generated for several slice (using n row)
        are correct if several paganin are requested"""
        slices = (2, 56, 89)
        db_values = [100.0, 200.0]
        self.scan.ftseries_recons_params.ft.do_test_slice = True
        self.scan.ftseries_recons_params.ft.fixed_slice = slices
        self.scan.ftseries_recons_params.paganin.mode = PaganinMode.on
        self.scan.ftseries_recons_params.paganin.db = db_values
        self.pyhst_caller.run()
        par_files = glob(self.scan.path + os.sep + "*.par")
        self.assertEqual(len(par_files), 8)
        basename = os.path.basename(self.scan.path)
        for db_value in db_values:
            full_rec_par_file = (
                basename + ("pag_%04d" % db_value).replace(".", "_") + ".par"
            )
            full_rec_par_file = os.path.join(self.scan.path, full_rec_par_file)
            self.assertTrue(full_rec_par_file in par_files)

        # check the one with slices
        for db_value in db_values:
            for slice in slices:
                file_name = basename + ("slice_pag_%04d" % db_value)
                slice_rec_par_file = "_".join((file_name, str(slice).zfill(4)))
                slice_rec_par_file = os.path.join(slice_rec_par_file + ".par")
                slice_rec_par_file = os.path.join(self.scan.path, slice_rec_par_file)
                self.assertTrue(slice_rec_par_file in par_files)


class TestLbsramBehavior(unittest.TestCase):
    """Make sure the .par file will be valid in case we are running under
    with lbsram system"""

    def setUp(self) -> None:
        super(TestLbsramBehavior, self).setUp()
        self.__original_lbsram = settings.get_lbsram_path()
        self.__original_dest = settings.get_dest_path()

        self._lbsram_dir = tempfile.mkdtemp()
        self._dest_dir = tempfile.mkdtemp()
        settings._set_lbsram_path(self._lbsram_dir)
        settings._set_dest_path(self._dest_dir)
        mock = MockEDF(scan_path=self._lbsram_dir, n_radio=10, n_ini_radio=10)
        mock.end_acquisition()
        self.scan = EDFTomoScan(scan=mock.scan_path)
        self.scan.ftseries_recons_params = ReconsParams()
        self.assertEqual(len(glob(self.scan.path + os.sep + "*.par")), 0)

    def tearDown(self) -> None:
        settings._set_lbsram_path(self.__original_lbsram)
        settings._set_dest_path(self.__original_dest)
        for folder in (self._lbsram_dir, self._dest_dir):
            shutil.rmtree(folder)
        super(TestLbsramBehavior, self).tearDown()

    def testSliceParFile(self):
        """Make sure the slice file will start with the LBSRAM_ID"""
        self.scan.ftseries_recons_params.ft.do_test_slice = True
        self.scan.ftseries_recons_params.ft.fixed_slice = 5

        pyhst_caller = PyHSTCaller(
            inputs={
                "data": self.scan,
                "pyhst2_params": self.scan.ftseries_recons_params,
            }
        )
        pyhst_caller.run()
        par_files = glob(self.scan.path + os.sep + "*.par")
        self.assertEqual(len(par_files), 2)
        basename = os.path.basename(self.scan.path)
        full_rec_par_file = os.path.join(self.scan.path, basename + ".par")
        self.assertTrue(full_rec_par_file in par_files)
        full_rec_params = getParametersFromParOrInfo(full_rec_par_file)
        # the .par file for the full volume should have path related
        # to the dest dir
        for key in ("FILE_PREFIX", "BACKGROUND_FILE", "FF_PREFIX", "OUTPUT_FILE"):
            param = full_rec_params[key.lower()]
            self.assertTrue(param.startswith(settings.get_dest_path()))

        middle_slice_rec_par_file = (
            basename
            + "slice_"
            + str(self.scan.ftseries_recons_params.ft.fixed_slice).zfill(4)
        )
        middle_slice_rec_par_file = os.path.join(
            self.scan.path, middle_slice_rec_par_file + ".par"
        )
        self.assertTrue(middle_slice_rec_par_file in par_files)
        slice_rec_params = getParametersFromParOrInfo(middle_slice_rec_par_file)
        # the .par file for slice should have path related to lbsram by default
        for key in ("FILE_PREFIX", "BACKGROUND_FILE", "FF_PREFIX", "OUTPUT_FILE"):
            param = slice_rec_params[key.lower()]
            self.assertTrue(param.startswith(settings.get_lbsram_path()))
