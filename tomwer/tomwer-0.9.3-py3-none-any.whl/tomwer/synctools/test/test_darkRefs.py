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
__date__ = "11/12/2017"


import os
import shutil
import tempfile
import fabio
import numpy
from silx.gui.utils.testutils import TestCaseQt
from tomwer.core.utils.scanutils import MockEDF
from tomwer.core.process.reconstruction.darkref.darkrefs import DarkRefs
from tomwer.core.process.reconstruction.darkref.params import DKRFRP
from tomwer.core.process.reconstruction.darkref.params import Method
from tomwer.core.scan.scanfactory import ScanFactory
from tomwer.test.utils import UtilsTest


class TestDarkRefsBehavior(TestCaseQt):
    """Test that the Darks and reference are correctly computed from the
    DarksRefs class
    """

    def setUp(self):
        TestCaseQt.setUp(self)
        self.datasetsID = "test10"
        self.tmpDir = tempfile.mkdtemp()
        self.thRef = {}
        """number of theoretical ref file the algorithm should create"""
        self.thDark = {}
        """number of theoretical dark file the algorithm should create"""
        self.dataset_folder = os.path.join(self.tmpDir, self.datasetsID)

        dataDir = UtilsTest.getEDFDataset(self.datasetsID)
        shutil.copytree(dataDir, self.dataset_folder)
        files = os.listdir(self.dataset_folder)
        for _f in files:
            if _f.startswith(("refHST", "darkHST", "dark.edf")):
                os.remove(os.path.join(self.dataset_folder, _f))

        self.recons_params = DKRFRP()
        self.recons_params._set_remove_opt(False)

    def tearDown(self):
        self.qapp.processEvents()
        self.darkRef = None
        shutil.rmtree(self.tmpDir)
        TestCaseQt.tearDown(self)

    def testDarkCreation(self):
        """Test that the dark is correctly computed"""
        self.recons_params.ref_calc_method = Method.none
        self.recons_params.dark_calc_method = Method.median

        dar_ref_process = DarkRefs(
            inputs={
                "dark_ref_params": self.recons_params,
                "force_sync": True,
                "darkhst_prefix": "darkHST",
                "data": self.dataset_folder,
            }
        )
        dar_ref_process.run()
        self.qapp.processEvents()
        if os.path.basename(self.dataset_folder) == "test10":
            self.assertTrue("darkend0000.edf" in os.listdir(self.dataset_folder))
            self.assertTrue("dark.edf" in os.listdir(self.dataset_folder))
            self.assertEqual(
                len(
                    dar_ref_process.getDarkHSTFiles(
                        self.dataset_folder, prefix=self.recons_params.dark_prefix
                    )
                ),
                1,
            )
            self.assertEqual(
                len(
                    dar_ref_process.getRefHSTFiles(
                        self.dataset_folder, prefix=self.recons_params.ref_prefix
                    )
                ),
                0,
            )

    def testRefCreation(self):
        """Test that the dark is correctly computed"""
        self.recons_params.ref_calc_method = Method.median
        self.recons_params.dark_calc_method = Method.none

        dar_ref_process = DarkRefs(
            inputs={
                "dark_ref_params": self.recons_params,
                "force_sync": True,
                "darkhst_prefix": "darkHST",
                "data": self.dataset_folder,
            }
        )

        dar_ref_process.run()
        self.qapp.processEvents()
        self.assertTrue("darkend0000.edf" in os.listdir(self.dataset_folder))
        self.assertFalse("dark0000.edf" in os.listdir(self.dataset_folder))
        self.assertTrue("refHST0000.edf" in os.listdir(self.dataset_folder))
        self.assertTrue("refHST0020.edf" in os.listdir(self.dataset_folder))
        self.assertTrue("ref0000_0000.edf" in os.listdir(self.dataset_folder))
        self.assertTrue("ref0000_0020.edf" in os.listdir(self.dataset_folder))
        self.assertTrue("ref0001_0000.edf" in os.listdir(self.dataset_folder))
        self.assertTrue("ref0001_0020.edf" in os.listdir(self.dataset_folder))

    def testRemoveOption(self):
        """Test that the remove option is working"""
        self.recons_params.ref_calc_method = Method.none
        self.recons_params.dark_calc_method = Method.none
        self.recons_params._set_remove_opt(True)
        dar_ref_process = DarkRefs(
            inputs={
                "dark_ref_params": self.recons_params,
                "force_sync": True,
                "darkhst_prefix": "darkHST",
                "data": self.dataset_folder,
            }
        )
        dar_ref_process.run()
        self.qapp.processEvents()
        self.assertFalse("darkend0000.edf" in os.listdir(self.dataset_folder))
        self.assertFalse("dark0000.edf" in os.listdir(self.dataset_folder))
        self.assertFalse("refHST0000.edf" in os.listdir(self.dataset_folder))
        self.assertFalse("refHST0020.edf" in os.listdir(self.dataset_folder))
        self.assertFalse("ref0000_0000.edf" in os.listdir(self.dataset_folder))
        self.assertFalse("ref0000_0020.edf" in os.listdir(self.dataset_folder))
        self.assertFalse("ref0001_0000.edf" in os.listdir(self.dataset_folder))
        self.assertFalse("ref0001_0020.edf" in os.listdir(self.dataset_folder))

    def testSkipOption(self):
        """Test that the overwrite option is working"""
        self.recons_params.ref_calc_method = Method.none
        self.recons_params.dark_calc_method = Method.none
        self.recons_params._set_skip_if_exist(True)

        iniRefNFile = len(
            DarkRefs.getRefHSTFiles(
                self.dataset_folder, prefix=self.recons_params.ref_prefix
            )
        )
        iniDarkNFile = len(
            DarkRefs.getDarkHSTFiles(
                self.dataset_folder, prefix=self.recons_params.dark_prefix
            )
        )

        dar_ref_process = DarkRefs(
            inputs={
                "dark_ref_params": self.recons_params,
                "force_sync": True,
                "darkhst_prefix": "darkHST",
                "data": self.dataset_folder,
            }
        )
        dar_ref_process.run()
        self.qapp.processEvents()
        refs = DarkRefs.getRefHSTFiles(
            self.dataset_folder, prefix=self.recons_params.ref_prefix
        )
        darks = DarkRefs.getDarkHSTFiles(
            self.dataset_folder, prefix=self.recons_params.dark_prefix
        )
        self.assertTrue(len(refs) == iniRefNFile)
        self.assertTrue(len(darks) == iniDarkNFile)


class TestRefCalculationOneSerie(TestCaseQt):
    """
    Make sure the calculation is correct for the dark and flat field
    according to the method used.
    """

    def setUp(self):
        super().setUp()
        self.tmp_dir = tempfile.mkdtemp()
        n_scans = 5
        n_info = 1
        n_xml = 1
        MockEDF.fastMockAcquisition(self.tmp_dir, n_radio=n_scans)
        reFiles = {}
        data1 = numpy.zeros((20, 10))
        data2 = numpy.zeros((20, 10)) + 100
        reFiles["ref0000_0000.edf"] = data1
        reFiles["ref0001_0000.edf"] = data2
        reFiles["ref0002_0000.edf"] = data2
        reFiles["ref0003_0000.edf"] = data2
        for refFile in reFiles:
            file_desc = fabio.edfimage.EdfImage(data=reFiles[refFile])
            file_desc.write(os.path.join(self.tmp_dir, refFile))
        assert len(os.listdir(self.tmp_dir)) is (
            len(reFiles) + n_scans + n_xml + n_info
        )

        self.recons_params = DKRFRP()
        self.darkRef = DarkRefs(
            inputs={
                "dark_ref_params": self.recons_params,
                "data": self.tmp_dir,
            }
        )
        self.darkRef.setForceSync(True)
        self.recons_params.ref_pattern = "ref*.*[0-9]{3,4}_[0-9]{3,4}"

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)
        super().tearDown()

    def testRefMedianCalculation(self):
        self.recons_params.ref_calc_method = Method.median
        self.recons_params.dark_calc_method = Method.none
        self.darkRef.run()
        refHST = os.path.join(self.tmp_dir, "refHST0000.edf")
        self.assertTrue(os.path.isfile(refHST))
        self.assertTrue(
            numpy.array_equal(fabio.open(refHST).data, numpy.zeros((20, 10)) + 100)
        )

    def testRefMeanCalculation(self):
        self.recons_params.ref_calc_method = Method.average
        self.recons_params.dark_calc_method = Method.none
        self.darkRef.run()
        refHST = os.path.join(self.tmp_dir, "refHST0000.edf")
        self.assertTrue(os.path.isfile(refHST))
        self.assertTrue(
            numpy.array_equal(fabio.open(refHST).data, numpy.zeros((20, 10)) + 75)
        )


class TestRefCalculationThreeSerie(TestCaseQt):
    """
    Make sure the calculation is correct for the dark and flat field
    according to the method used.
    """

    def setUp(self):
        super().setUp()
        self.tmp_dir = tempfile.mkdtemp()
        MockEDF.fastMockAcquisition(folder=self.tmp_dir, n_radio=1)
        reFiles = {}
        self.series = (0, 10, 200)
        for serie in self.series:
            data1 = numpy.zeros((20, 10)) + serie
            data2 = numpy.zeros((20, 10)) + 100 + serie
            reFiles["ref0000_" + str(serie).zfill(4) + ".edf"] = data1
            reFiles["ref0001_" + str(serie).zfill(4) + ".edf"] = data2
            reFiles["ref0002_" + str(serie).zfill(4) + ".edf"] = data2
            reFiles["ref0003_" + str(serie).zfill(4) + ".edf"] = data2
            for refFile in reFiles:
                file_desc = fabio.edfimage.EdfImage(data=reFiles[refFile])
                file_desc.write(os.path.join(self.tmp_dir, refFile))

        self.recons_params = DKRFRP()
        self.darkRef = DarkRefs(
            inputs={
                "dark_ref_params": self.recons_params,
                "data": self.tmp_dir,
                "force_sync": True,
            }
        )
        self.recons_params.ref_pattern = "ref*.*[0-9]{3,4}_[0-9]{3,4}"

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)
        super().tearDown()

    def testRefMedianCalculation(self):
        self.recons_params.ref_calc_method = Method.median
        self.recons_params.dark_calc_method = Method.none
        self.darkRef.run()
        for serie in self.series:
            refHST = os.path.join(self.tmp_dir, "refHST" + str(serie).zfill(4) + ".edf")
            self.assertTrue(os.path.isfile(refHST))
            self.assertTrue(
                numpy.array_equal(
                    fabio.open(refHST).data, numpy.zeros((20, 10)) + 100 + serie
                )
            )

    def testRefMeanCalculation(self):
        self.recons_params.ref_calc_method = Method.average
        self.recons_params.dark_calc_method = Method.none
        self.darkRef.run()
        for serie in self.series:
            refHST = os.path.join(self.tmp_dir, "refHST" + str(serie).zfill(4) + ".edf")
            self.assertTrue(os.path.isfile(refHST))
            self.assertTrue(
                numpy.array_equal(
                    fabio.open(refHST).data, numpy.zeros((20, 10)) + 75 + serie
                )
            )


class TestDarkCalculationOneFrame(TestCaseQt):
    """Make sure computation of the Dark is correct"""

    def setUp(self):
        super().setUp()
        self.tmp_dir = tempfile.mkdtemp()
        n_scan = 1
        n_info = 1
        n_xml = 1
        MockEDF.fastMockAcquisition(self.tmp_dir, n_radio=n_scan)
        file_desc = fabio.edfimage.EdfImage(data=numpy.zeros((20, 10)) + 10)

        file_desc.write(os.path.join(self.tmp_dir, "darkend0000.edf"))
        assert len(os.listdir(self.tmp_dir)) is (1 + n_scan + n_info + n_xml)
        self.recons_params = DKRFRP()
        self.darkRef = DarkRefs(
            inputs={
                "dark_ref_params": self.recons_params,
                "force_sync": True,
                "data": self.tmp_dir,
            }
        )

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)
        super().tearDown()

    def testDarkMeanCalculation(self):
        self.recons_params.ref_calc_method = Method.none
        self.recons_params.dark_calc_method = Method.average

        self.darkRef.run()
        refHST = os.path.join(self.tmp_dir, "dark.edf")
        self.assertTrue(os.path.isfile(refHST))
        self.assertTrue(
            numpy.array_equal(fabio.open(refHST).data, numpy.zeros((20, 10)) + 10)
        )

    def testDarkMedianCalculation(self):
        self.recons_params.ref_calc_method = Method.none
        self.recons_params.dark_calc_method = Method.median

        self.darkRef.run()
        refHST = os.path.join(self.tmp_dir, "dark.edf")
        self.assertTrue(os.path.isfile(refHST))

        self.assertTrue(
            numpy.array_equal(fabio.open(refHST).data, numpy.zeros((20, 10)) + 10)
        )


class TestDarkCalculation(TestCaseQt):
    """Make sure computation of the Dark is correct"""

    def setUp(self):
        super().setUp()
        self.tmp_dir = tempfile.mkdtemp()
        n_scan = 1
        n_xml = 1
        n_info = 1
        MockEDF.fastMockAcquisition(os.path.join(self.tmp_dir), n_radio=n_scan)

        file_desc = fabio.edfimage.EdfImage(data=numpy.zeros((20, 10)))
        file_desc.append_frame(data=(numpy.zeros((20, 10)) + 100))
        file_desc.append_frame(data=(numpy.zeros((20, 10)) + 100))
        file_desc.append_frame(data=(numpy.zeros((20, 10)) + 100))

        file_desc.write(os.path.join(self.tmp_dir, "darkend0000.edf"))
        assert len(os.listdir(self.tmp_dir)) is (1 + n_scan + n_xml + n_info)
        self.recons_params = DKRFRP()
        self.darkRef = DarkRefs(
            inputs={
                "data": self.tmp_dir,
                "dark_ref_params": self.recons_params,
                "force_sync": True,
            }
        )

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)
        super().tearDown()

    def testDarkMeanCalculation(self):
        self.recons_params.ref_calc_method = Method.none
        self.recons_params.dark_calc_method = Method.average

        self.darkRef.run()
        refHST = os.path.join(self.tmp_dir, "dark.edf")
        self.assertTrue(os.path.isfile(refHST))
        self.assertTrue(
            numpy.array_equal(fabio.open(refHST).data, numpy.zeros((20, 10)) + 75)
        )

    def testDarkMedianCalculation(self):
        self.recons_params.ref_calc_method = Method.none
        self.recons_params.dark_calc_method = Method.median

        self.darkRef.run()
        refHST = os.path.join(self.tmp_dir, "dark.edf")
        self.assertTrue(os.path.isfile(refHST))

        self.assertTrue(
            numpy.array_equal(fabio.open(refHST).data, numpy.zeros((20, 10)) + 100)
        )


class TestDarkAccumulation(TestCaseQt):
    """
    Make sure computation for dark in accumulation are correct
    """

    def setUp(self):
        super().setUp()
        self.dataset = "bone8_1_"
        dataDir = UtilsTest.getEDFDataset(self.dataset)
        self.outputdir = tempfile.mkdtemp()
        shutil.copytree(src=dataDir, dst=os.path.join(self.outputdir, self.dataset))
        self.darkFile = os.path.join(self.outputdir, self.dataset, "dark.edf")
        # create a single 'bone8_1_' to be a valid acquisition directory
        MockEDF.fastMockAcquisition(os.path.join(self.outputdir, self.dataset))
        assert os.path.isfile(self.darkFile)
        with fabio.open(self.darkFile) as dsc:
            self.dark_reference = dsc.data
        # remove dark file
        os.remove(self.darkFile)

        self.recons_params = DKRFRP()
        self.recons_params.ref_calc_method = Method.none
        self.recons_params.dark_calc_method = Method.median
        self.recons_params.dark_pattern = "darkend*"
        self.recons_params.dark_prefix = "dark.edf"

    def tearDown(self):
        shutil.rmtree(self.outputdir)
        super().tearDown()

    def testComputation(self):
        """Test data bone8_1_ from id16b containing dark.edf of reference
        and darkend"""
        dark_ref_process = DarkRefs(
            inputs={
                "data": os.path.join(self.outputdir, self.dataset),
                "force_sync": True,
            }
        )

        dark_ref_process.run()
        self.assertTrue(os.path.isfile(self.darkFile))
        with fabio.open(self.darkFile) as dsc:
            self.computed_dark = dsc.data
        self.assertTrue(numpy.array_equal(self.computed_dark, self.dark_reference))


class TestPCOTomo(TestCaseQt):
    """Test processing of DKRF are correct"""

    def setUp(self):
        TestCaseQt.setUp(self)
        self.tmp_dir = tempfile.mkdtemp()
        MockEDF.fastMockAcquisition(self.tmp_dir)

        self.recons_params = DKRFRP()
        self.recons_params.ref_calc_method = Method.none
        self.recons_params.dark_calc_method = Method.none
        self.recons_params.dark_pattern = ".*_dark_.*"
        self.recons_params.ref_pattern = ".*_ref_.*"
        self.recons_params._set_remove_opt(True)

    def copyDataset(self, dataset):
        folder = os.path.join(self.tmp_dir, dataset)
        shutil.copytree(os.path.join(UtilsTest.getEDFDataset(dataset)), folder)
        self.scan = ScanFactory.create_scan_object(scan_path=folder)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)
        TestCaseQt.tearDown(self)

    def testDark3Scan(self):
        """
        Make sure the processing dark field for
        pcotomo_3scan_refdarkbeg_end_download are correct
        """
        self.dataset = "pcotomo_3scan_refdarkbeg_end_download"
        self.copyDataset(self.dataset)
        _file = os.path.join(
            self.tmp_dir, "pcotomo_3scan_refdarkbeg_end_download", "dark.edf"
        )
        if os.path.isfile(_file):
            os.remove(_file)
        self.recons_params.dark_calc_method = Method.median
        dar_ref_process = DarkRefs(
            inputs={
                "dark_ref_params": self.recons_params,
                "data": self.scan,
                "darkhst_prefix": "darkHST",
                "force_sync": True,
            }
        )
        dar_ref_process.run()
        darkHSTFiles = DarkRefs.getDarkHSTFiles(
            self.scan.path, prefix=self.recons_params.dark_prefix
        )
        self.assertEqual(len(darkHSTFiles), 2)
        dark0000 = os.path.join(self.scan.path, "dark0000.edf")
        dark1000 = os.path.join(self.scan.path, "dark1000.edf")
        self.assertTrue(dark0000 in darkHSTFiles)
        self.assertTrue(dark1000 in darkHSTFiles)

    def testRef3Scan(self):
        """
        Make sure the processing flat field for
        pcotomo_3scan_refdarkbeg_end_download are correct
        """
        self.dataset = "pcotomo_3scan_refdarkbeg_end_download"
        self.copyDataset(self.dataset)
        self.recons_params.ref_calc_method = Method.median
        dar_ref_process = DarkRefs(
            inputs={
                "dark_ref_params": self.recons_params,
                "data": self.scan,
                "darkhst_prefix": "darkHST",
                "force_sync": True,
            }
        )
        dar_ref_process.run()
        refHSTFiles = DarkRefs.getRefHSTFiles(
            self.scan.path, prefix=self.recons_params.ref_prefix
        )
        self.assertEqual(len(refHSTFiles), 2)
        f0000 = os.path.join(self.scan.path, "refHST0000.edf")
        self.assertTrue(f0000 in refHSTFiles)
        f1000 = os.path.join(self.scan.path, "refHST1000.edf")
        self.assertTrue(f1000 in refHSTFiles)

    def testDark2x2Scan(self):
        self.dataset = "pcotomo_2x2scan_refdarkbeg_end_conti"
        self.copyDataset(self.dataset)
        self.recons_params.dark_calc_method = Method.median
        dar_ref_process = DarkRefs(
            inputs={
                "dark_ref_params": self.recons_params,
                "data": self.scan,
                "darkhst_prefix": "darkHST",
                "force_sync": True,
            }
        )
        dar_ref_process.run()

    def testRef2x2Scan(self):
        self.dataset = "pcotomo_2x2scan_refdarkbeg_end_conti"
        self.copyDataset(self.dataset)
        self.recons_params.ref_calc_method = Method.median
        dar_ref_process = DarkRefs(
            inputs={
                "dark_ref_params": self.recons_params,
                "data": self.scan,
                "darkhst_prefix": "darkHST",
                "force_sync": True,
            }
        )
        dar_ref_process.run()
