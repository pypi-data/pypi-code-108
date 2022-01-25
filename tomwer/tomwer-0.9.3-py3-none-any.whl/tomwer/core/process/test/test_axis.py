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

__authors__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "05/04/2019"


import shutil
import tempfile
import unittest
import numpy
import os
import h5py
from tomwer.test.utils import UtilsTest
from tomwer.core.utils.scanutils import MockEDF, MockHDF5
from ..reconstruction.axis.axis import AxisProcess
from tomwer.core.scan.scanbase import TomwerScanBase
from tomwer.core.process.reconstruction.axis.params import AxisRP
from tomwer.core.process.reconstruction.axis.mode import AxisMode
from tomwer.core.scan.edfscan import EDFTomoScan
from tomwer.core.process.task import Task
from silx.io.utils import h5py_read_dataset


class _AxisDataset:
    def __init__(self, name):
        self.name = name


class TestAxisIO(unittest.TestCase):
    """Test inputs and outputs types of the handler functions"""

    @staticmethod
    def _random_calc(scan):
        return numpy.random.random()

    def setUp(self):
        self.scan_folder = tempfile.mkdtemp()

        self.scan = MockEDF.mockScan(
            scanID=self.scan_folder, nRadio=10, nRecons=1, nPagRecons=4, dim=10
        )
        self.recons_params = AxisRP()

        # set the axis url to be used
        projections = self.scan.projections
        urls = list(projections.values())
        self.scan.axis_params = AxisRP()
        self.scan.axis_params.axis_url_1 = urls[0]
        self.scan.axis_params.axis_url_2 = urls[1]

    def tearDown(self):
        shutil.rmtree(self.scan_folder)

    def testInputOutput(self):
        """Test that io using TomoBase instance work"""
        for input_type in (dict, TomwerScanBase):
            for return_dict in (True, False):
                with self.subTest(
                    return_dict=return_dict,
                    input_type=input_type,
                ):
                    input_obj = self.scan
                    if input_obj is dict:
                        input_obj = input_obj.to_dict()
                    axis_process = AxisProcess(
                        inputs={
                            "axis_params": self.recons_params,
                            "data": input_obj,
                            "return_dict": return_dict,
                        }
                    )

                    # patch the axis process
                    axis_process._CALCULATIONS_METHODS[
                        AxisMode.centered
                    ] = TestAxisIO._random_calc

                    axis_process.run()
                    out = axis_process.outputs.data
                    if return_dict:
                        self.assertTrue(isinstance(out, dict))
                    else:
                        self.assertTrue(isinstance(out, TomwerScanBase))


class TestAxis(unittest.TestCase):
    """Test the axis process"""

    def setUp(self):
        self.recons_params = AxisRP()
        self.recons_params.mode = "centered"

    def test_process_saved_edf(self):
        """Test that if process is called, the tomwer.h5 file is created
        and is correctly saving information regarding the center of position
        """
        self.tempdir = tempfile.mkdtemp()
        mock = MockEDF(scan_path=self.tempdir, n_radio=10, n_ini_radio=10)
        scan = EDFTomoScan(mock.scan_path)
        self.recons_params.mode = "centered"
        axis_process = AxisProcess(
            inputs={
                "data": scan,
                "axis_params": self.recons_params,
            }
        )

        axis_process.run()
        self.assertTrue(os.path.exists(scan.process_file))

        with h5py.File(scan.process_file, "r", swmr=True) as h5f:
            self.assertTrue("entry" in h5f)
            self.assertTrue("tomwer_process_0" in h5f["entry"])
            group_axis = h5f["entry"]["tomwer_process_0"]
            self.assertTrue("configuration" in group_axis)
            self.assertTrue("program" in group_axis)
            self.assertTrue("results" in group_axis)
            self.assertTrue("center_of_rotation" in group_axis["results"])
            axis_value = h5py_read_dataset(group_axis["results"]["center_of_rotation"])

        processes = Task.get_processes_frm_type(
            process_file=scan.process_file, process_type=AxisProcess, entry="entry"
        )
        self.assertEqual(len(processes), 1)
        self.assertEqual(processes[0].results["center_of_rotation"], axis_value)

        # make sure the process file can be loaded by an instance of AxisRP
        new_axis_params = AxisRP()
        new_axis_params.set_relative_value(-10000)
        new_axis_params.set_position_frm_par_file(
            file_path=scan.process_file, entry=None
        )
        self.assertEqual(
            new_axis_params.relative_cor_value, scan.axis_params.relative_cor_value
        )

    def test_process_saved_hdf5(self):
        """Test that if process is called, the tomwer.h5 file is created
        and is correctly saving information regarding the center of position
        """
        self.tempdir = tempfile.mkdtemp()
        dim = 10
        mock = MockHDF5(
            scan_path=self.tempdir, n_proj=10, n_ini_proj=10, scan_range=180, dim=dim
        )
        mock.add_alignment_radio(index=10, angle=90)
        mock.add_alignment_radio(index=10, angle=0)
        scan = mock.scan
        self.recons_params.mode = "centered"

        # check data url take
        axis_process = AxisProcess(
            inputs={
                "data": scan,
                "axis_params": self.recons_params,
            }
        )
        axis_process.run()
        # make sure center of position has been computed
        self.assertTrue(os.path.exists(scan.process_file))

        with h5py.File(scan.process_file, "r", swmr=True) as h5f:
            self.assertTrue("entry" in h5f)
            self.assertTrue("tomwer_process_0" in h5f["entry"])
            group_axis = h5f["entry"]["tomwer_process_0"]
            self.assertTrue("configuration" in group_axis)
            self.assertTrue("program" in group_axis)
            self.assertTrue("results" in group_axis)
            self.assertTrue("center_of_rotation" in group_axis["results"])
            axis_value = h5py_read_dataset(group_axis["results"]["center_of_rotation"])
        self.assertTrue(-dim / 2 <= axis_value <= dim / 2)
        processes = Task.get_processes_frm_type(
            process_file=scan.process_file, process_type=AxisProcess
        )
        self.assertEqual(len(processes), 1)
        self.assertEqual(processes[0].results["center_of_rotation"], axis_value)

        # make sure the process file can be loaded by an instance of AxisRP
        new_axis_params = AxisRP()
        new_axis_params.set_relative_value(-10000)
        new_axis_params.set_position_frm_par_file(file_path=scan.process_file)
        self.assertEqual(
            new_axis_params.relative_cor_value, scan.axis_params.relative_cor_value
        )


class TestAxisRP(unittest.TestCase):
    """Test the class used for AxisProcess configuration"""

    def setUp(self):
        self.axis_rp = AxisRP()
        self.tmp_folder = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp_folder)

    def testSetPositionFromParFile(self):
        """Test that the position can be managed from a par file"""
        old_value = self.axis_rp.value_ref_tomwer

        with self.assertRaises(ValueError):
            self.axis_rp.set_position_frm_par_file("ghost_file.par", force=False)
        self.assertEqual(self.axis_rp.value_ref_tomwer, old_value)

        existing_empty_file = os.path.join(self.tmp_folder, "par_file.par")
        with open(existing_empty_file, "w") as _file:
            _file.write("toto")

        with self.assertRaises(KeyError):
            self.axis_rp.set_position_frm_par_file(existing_empty_file, force=False)
        self.assertEqual(self.axis_rp.value_ref_tomwer, old_value)

        valid_par_file = os.path.join(
            UtilsTest.getEDFDataset("scan_3_"), "scan_3_slice.par"
        )
        assert os.path.isfile(valid_par_file)
        self.axis_rp.set_position_frm_par_file(valid_par_file, force=False)
        self.assertEqual(self.axis_rp.value_ref_tomwer, 1024.742042)

        self.axis_rp.set_position_frm_par_file(existing_empty_file, force=True)
        self.assertEqual(self.axis_rp.value_ref_tomwer, None)

        self.axis_rp.set_position_frm_par_file("ghost_file.par", force=True)
        self.assertEqual(self.axis_rp.value_ref_tomwer, None)

        self.axis_rp.set_position_frm_par_file(valid_par_file, force=True)
        self.assertEqual(self.axis_rp.value_ref_tomwer, 1024.742042)


class TestSinogramAlgorithm(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_folder = tempfile.mkdtemp()
        dim = 512
        self.scan = MockHDF5(
            scan_path=self.tmp_folder,
            n_proj=10,
            n_ini_proj=10,
            create_ini_dark=True,
            create_final_ref=True,
            scan_range=360,
            dim=dim,
        ).scan

    def tearDown(self):
        shutil.rmtree(self.tmp_folder)

    def test_growing_window_sinogram(self):
        recons_params = AxisRP()
        axis_process = AxisProcess(
            inputs={"axis_params": recons_params, "data": self.scan}
        )
        recons_params.mode = AxisMode.growing_window
        recons_params.use_sinogram = True
        recons_params.sinogram_subsampling = 1
        axis_process.run()

    def test_sliding_window(self):
        recons_params = AxisRP()
        axis_process = AxisProcess(
            inputs={"axis_params": recons_params, "data": self.scan}
        )
        recons_params.mode = AxisMode.sliding_window
        recons_params.side = "left"
        recons_params.sinogram_subsampling = 1
        recons_params.use_sinogram = True
        axis_process.run()

    def test_sino_coarse_to_fine(self):
        recons_params = AxisRP()
        axis_process = AxisProcess(
            inputs={"axis_params": recons_params, "data": self.scan}
        )
        recons_params.mode = AxisMode.sino_coarse_to_fine
        recons_params.sinogram_subsampling = 1
        recons_params.sinogram_line = 2
        axis_process.run()
