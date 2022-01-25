# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2017 European Synchrotron Radiation Facility
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
__date__ = "30/09/2019"


import unittest
import tempfile
import os
import shutil
import glob
from collections import namedtuple
from tomwer.test.utils import UtilsTest
from tomwer.synctools.utils.scanstages import ScanStages
from tomwer.core.scan.scanfactory import ScanFactory
from tomwer.test.utils import skip_gui_test
import pytest

if skip_gui_test() is False:
    from tomwer.synctools.rsyncmanager import RSyncManager


_stage_desc = namedtuple(
    "_stage_desc",
    [
        "n_par_file",
        "n_edf_file",
        "n_info_file",
        "n_xml_file",
        "n_vol",
        "folder_should_exists",
    ],
)  # noqa


@pytest.mark.skipif(RSyncManager().has_rsync() is False, reason="Rsync is missing")
@pytest.mark.skipif(skip_gui_test(), reason="skip gui test")
class TestScanStagesEDF(unittest.TestCase):
    """
    test the ScanStages class for edf scans
    """

    def setUp(self) -> None:
        self.output_dir = tempfile.mkdtemp()
        dataset = "D2_H2_T2_h_"
        self.data_test_dir = UtilsTest.getEDFDataset(dataset)
        self.target_dir = os.path.join(self.output_dir, dataset)
        self.scan_stages = ScanStages(
            scan=ScanFactory.create_scan_object(self.data_test_dir)
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.output_dir)

    def testRSyncUntil(self):
        """test the rsync_until function"""
        ACQUI_NOT_STARTED = ScanStages.AcquisitionStage.ACQUI_NOT_STARTED
        # ACQUI_STARTED = ScanStages.AcquisitionStage.ACQUI_STARTED
        # ACQUI_ON_GOING = ScanStages.AcquisitionStage.ACQUI_ON_GOING
        # ACQUI_ENDED = ScanStages.AcquisitionStage.ACQUI_ENDED
        # RECONSTRUCTION_ADDED = ScanStages.AcquisitionStage.RECONSTRUCTION_ADDED
        # COMPLETE = ScanStages.AcquisitionStage.COMPLETE

        # tomo_n = 3605
        stage_res = {
            ACQUI_NOT_STARTED: _stage_desc(
                n_par_file=0,
                n_edf_file=0,
                n_info_file=0,
                n_xml_file=0,
                n_vol=0,
                folder_should_exists=False,
            ),
            # comment most of the test because take too long
            # ACQUI_STARTED: _stage_desc(
            #     n_par_file=0,
            #     n_edf_file=0,
            #     n_info_file=1,
            #     n_xml_file=0,
            #     n_vol=0,
            #     folder_should_exists=True,
            # ),
            # ACQUI_ON_GOING: _stage_desc(
            #     n_par_file=0,
            #     n_edf_file=tomo_n // 2,
            #     n_info_file=1,
            #     n_xml_file=0,
            #     n_vol=0,
            #     folder_should_exists=True,
            # ),
            # ACQUI_ENDED: _stage_desc(
            #     n_par_file=0,
            #     n_edf_file=tomo_n,
            #     n_info_file=1,
            #     n_xml_file=1,
            #     n_vol=0,
            #     folder_should_exists=True,
            # ),
            # RECONSTRUCTION_ADDED: _stage_desc(
            #     n_par_file=6,
            #     n_edf_file=tomo_n,
            #     n_info_file=2,
            #     n_xml_file=2,
            #     n_vol=1,
            #     folder_should_exists=True,
            # ),
            # COMPLETE: _stage_desc(
            #     n_par_file=6,
            #     n_edf_file=3719,  # there is several ref, darks...
            #     n_info_file=2,
            #     n_xml_file=2,
            #     n_vol=1,
            #     folder_should_exists=True,
            # ),
        }
        for stage, th_results in stage_res.items():
            with self.subTest(stage=stage):
                self.scan_stages.rsync_until(stage=stage, dest_dir=self.output_dir)
                self.assertEqual(
                    os.path.exists(self.target_dir), th_results.folder_should_exists
                )
                self.assertEqual(
                    len(glob.glob(os.path.join(self.target_dir, "*.par"))),
                    th_results.n_par_file,
                )
                self.assertEqual(
                    len(glob.glob(os.path.join(self.target_dir, "*.edf"))),
                    th_results.n_edf_file,
                )
                self.assertEqual(
                    len(glob.glob(os.path.join(self.target_dir, "*.xml"))),
                    th_results.n_xml_file,
                )
                self.assertEqual(
                    len(glob.glob(os.path.join(self.target_dir, "*.vol"))),
                    th_results.n_vol,
                )
