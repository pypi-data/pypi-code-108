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
__date__ = "24/01/2017"


import os
import shutil
import tempfile
import unittest

from tomwer.core.process.reconstruction.axis import AxisProcess
from tomwer.core.process.reconstruction.axis.params import AxisRP
from tomwer.core.process.reconstruction.axis.mode import AxisMode
from tomwer.core.process.reconstruction.darkref.darkrefs import DarkRefs
from tomwer.core.process.reconstruction.ftseries import Ftseries
from tomwer.core.process.reconstruction.ftseries.params import ReconsParams
from tomwer.core.process.reconstruction.darkref.params import DKRFRP, Method
from tomwer.core.scan.edfscan import EDFTomoScan
from tomwer.core.utils.scanutils import MockEDF


class TestTomoReconsWorkflow(unittest.TestCase):
    """Test several tomography reconstruction workflow and make sure they
    are correctly processed. Focus on ReconsParams values"""

    def setUp(self):
        super().setUp()
        # axis reconstruction parameters
        self._axis_rp = AxisRP()
        self._axis_rp_id = id(self._axis_rp)

        # darkref reconstruction parameters
        self._darkref_rp = DKRFRP()
        self._darkref_rp_id = id(self._darkref_rp)

        # ftseries reconstruction parameters
        self._ftseries_rp = ReconsParams()
        self._ftseries_rp_id = id(self._ftseries_rp)

        self._check_default_values()

        # change the value of calculation mode and axis mode
        self._axis_rp.mode = AxisMode.centered
        self._darkref_rp.dark_calc_method = Method.median
        self._ftseries_rp.dkrf.dark_calc_method = Method.median

        # define scans
        self._scans_dir = tempfile.mkdtemp()

        def create_scan(dataset):
            _folder = os.path.join(self._scans_dir, dataset)
            os.makedirs(_folder)
            MockEDF.fastMockAcquisition(_folder, n_radio=10)
            return EDFTomoScan(scan=_folder)

        self.scan_a = create_scan("scanA")
        self.scan_b = create_scan("scanB")
        self.scan_01_dft_rp = ReconsParams()
        self.scan_10_dft_rp = ReconsParams()
        self._recons_params_dft = {
            self.scan_a.path: self.scan_01_dft_rp,
            self.scan_b.path: self.scan_10_dft_rp,
        }
        self.scans = (self.scan_a, self.scan_b)

    def tearDown(self):
        shutil.rmtree(self._scans_dir)
        super().tearDown()

    def _check_default_values(self):
        assert self._darkref_rp.dark_calc_method is Method.average
        assert self._ftseries_rp.dkrf.dark_calc_method is Method.average
        assert id(self._darkref_rp) != id(self._ftseries_rp)

    def _process_axis(self, scan, initial_recons_params):
        """execute the axis process and check results"""
        self._axis_process = AxisProcess(
            inputs={
                "axis_params": self._axis_rp,
                "data": scan,
            }
        )
        self._axis_process.run()
        if initial_recons_params is not None:
            # make sure a new instance of tomo_recons_param has not been changed
            self.assertTrue(
                id(scan.ftseries_recons_params) is id(self._recons_params_dft[scan])
            )

        # test value of the parameter has been modify
        self.assertTrue(scan.axis_params.mode is AxisMode.centered)

    def _process_darkref(self, scan, initial_recons_params):
        """execute the darkref process and check results"""
        self._darkref_process = DarkRefs(
            inputs={
                "force_sync": True,
                "data": scan,
                "dark_ref_params": self._darkref_rp,
            }
        )

        self._darkref_process.run()
        if initial_recons_params is not None:
            # make sure a new instance of tomo_recons_param has not been changed
            self.assertTrue(
                id(scan.ftseries_recons_params) is id(self._recons_params_dft[scan])
            )

        # test that modifications only affect the axis reconstruction parameters
        if initial_recons_params is None:
            self.assertTrue(scan.ftseries_recons_params.paganin is None)

        self.assertTrue(
            scan.ftseries_recons_params.dkrf.dark_calc_method is Method.median
        )

    def _process_ftseries(self, scan, initial_recons_params):
        """execute the ftseries process and check results"""
        self._ftseries_process = Ftseries(
            inputs={
                "force_sync": True,
                "mock_mode": True,
                "data": scan,
                "pyhst2_params": self._ftseries_rp,
            }
        )
        self.assertTrue(
            id(self._ftseries_process.recons_params) == self._ftseries_rp_id
        )

        self.assertEqual(id(self._ftseries_rp), self._ftseries_rp_id)
        self.assertEqual(id(self._ftseries_process.recons_params), self._ftseries_rp_id)

        self._ftseries_process.run()
        if initial_recons_params is not None:
            # make sure a new instance of tomo_recons_param has not been changed
            self.assertTrue(
                id(scan.ftseries_recons_params) is id(self._recons_params_dft[scan])
            )

        if initial_recons_params is None:
            self.assertTrue(scan.ftseries_recons_params.paganin is not None)

        # ftseries should take values from the dkrf and axis objects
        self.assertTrue(
            id(self._ftseries_process.recons_params) == self._ftseries_rp_id
        )
        # make sure ftseries loaded values from axis and dkrf
        self.assertTrue(
            self._ftseries_rp.dkrf.dark_calc_method
            == scan.ftseries_recons_params.dkrf.dark_calc_method
        )
        # make sure dkrf value is unchanged
        self.assertTrue(
            scan.ftseries_recons_params.dkrf.dark_calc_method is Method.median
        )

    def test_axis_darkrefs_ftseries(self):
        """Test that the workflow axis -> darkrefs -> ftseries is valid
        regarding the reconstruction parameters used"""
        for initial_recons_params in (None,):
            with self.subTest(initial_recons_params=initial_recons_params):
                if initial_recons_params is not None:
                    for (key, value) in initial_recons_params.items():
                        key.ftseries_recons_params = value
                        assert id(value) is id(key.ftseries_recons_params)

                for scan in self.scans:
                    assert isinstance(scan, EDFTomoScan)
                    self._process_axis(
                        scan=scan, initial_recons_params=initial_recons_params
                    )
                    self._process_darkref(
                        scan=scan, initial_recons_params=initial_recons_params
                    )
                    self._process_ftseries(
                        scan=scan, initial_recons_params=initial_recons_params
                    )
                    scan.ftseries_recons_params.to_unique_recons_set()

    def test_axis_ftseries(self):
        """Test that the workflow axis -> ftseries sis valid regarding
        the reconstruction parameters used"""
        for initial_recons_params in (None,):
            with self.subTest(initial_recons_params=initial_recons_params):
                if initial_recons_params is not None:
                    for (key, value) in initial_recons_params.items():
                        key.ftseries_recons_params = value
                        assert id(value) is id(key.ftseries_recons_params)

                for scan in self.scans:
                    assert isinstance(scan, EDFTomoScan)
                    self._process_axis(
                        scan=scan, initial_recons_params=initial_recons_params
                    )
                    self._process_ftseries(
                        scan=scan, initial_recons_params=initial_recons_params
                    )
                    scan.ftseries_recons_params.to_unique_recons_set()

    def test_darkrefs_ftseries(self):
        """Test that the workflow darkrefs -> ftseries sis valid regarding
        the reconstruction parameters used"""
        for initial_recons_params in (None,):
            with self.subTest(initial_recons_params=initial_recons_params):
                if initial_recons_params is not None:
                    for (key, value) in initial_recons_params.items():
                        key.ftseries_recons_params = value
                        assert id(value) is id(key.ftseries_recons_params)

                for scan in self.scans:
                    assert isinstance(scan, EDFTomoScan)
                    self._process_darkref(
                        scan=scan, initial_recons_params=initial_recons_params
                    )
                    scan.ftseries_recons_params.to_unique_recons_set()
                    self._process_ftseries(
                        scan=scan, initial_recons_params=initial_recons_params
                    )
                    scan.ftseries_recons_params.to_unique_recons_set()
