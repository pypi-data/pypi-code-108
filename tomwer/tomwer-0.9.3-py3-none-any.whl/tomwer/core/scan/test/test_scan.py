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

import unittest
import logging
import tempfile
import numpy
import fabio.edfimage
import contextlib
from tomwer.core.scan.edfscan import EDFTomoScan
from tomwer.core.scan.scanfactory import ScanFactory
from tomwer.core.process.task import Task
from tomwer.test.utils import UtilsTest
from tomwer.core.utils.scanutils import MockEDF
from tomwer.core.process.reconstruction.nabu import nabuslices
import shutil
import os
from multiprocessing import Process

logging.disable(logging.INFO)


class TestScanFactory(unittest.TestCase):
    """Make sure the Scan factory is correctly working. Able to detect the valid
    scan type for a given file / directory
    """

    def test_no_scan(self):
        scan_dir = tempfile.mkdtemp()
        with self.assertRaises(ValueError):
            ScanFactory.create_scan_object(scan_dir)

    def test_scan_edf(self):
        scan_dir = UtilsTest.getEDFDataset("test10")
        scan = ScanFactory.create_scan_object(scan_dir)
        self.assertTrue(isinstance(scan, EDFTomoScan))


class FTSerieReconstructionTest(unittest.TestCase):
    """unit test for the FTSerieReconstruction functions"""

    def setUp(self):
        def saveData(data, _file, folder):
            file_desc = fabio.edfimage.EdfImage(data=data)
            file_desc.write(os.path.join(folder, _file))

        unittest.TestCase.setUp(self)
        self.folderTwoFlats = tempfile.mkdtemp()
        self.folderOneFlat = tempfile.mkdtemp()

        self.darkData = numpy.arange(100).reshape(10, 10)
        self.flatField_0 = numpy.arange(start=10, stop=110).reshape(10, 10)
        self.flatField_600 = numpy.arange(start=-10, stop=90).reshape(10, 10)
        self.flatField = numpy.arange(start=0, stop=100).reshape(10, 10)

        # save configuration one
        saveData(self.darkData, "darkHST.edf", self.folderTwoFlats)
        saveData(self.flatField_0, "refHST_0000.edf", self.folderTwoFlats)
        saveData(self.flatField_600, "refHST_0600.edf", self.folderTwoFlats)

        # save configuration two
        saveData(self.darkData, "darkHST.edf", self.folderOneFlat)
        saveData(self.flatField, "refHST.edf", self.folderOneFlat)

        self.acquiOneFlat = EDFTomoScan(self.folderOneFlat)
        self.acquiTwoFlats = EDFTomoScan(self.folderTwoFlats)

    def tearDown(self):
        for f in (self.folderOneFlat, self.folderTwoFlats):
            shutil.rmtree(f)
        unittest.TestCase.tearDown(self)

    def testGetDark(self):
        self.assertTrue(numpy.array_equal(self.acquiOneFlat.getDark(), self.darkData))
        self.assertTrue(numpy.array_equal(self.acquiTwoFlats.getDark(), self.darkData))

    def testGetFlat(self):
        # check one flat file with two ref
        self.assertTrue(numpy.array_equal(self.acquiOneFlat.getFlat(), self.flatField))

        # check two flat files
        self.assertTrue(
            numpy.array_equal(
                self.acquiTwoFlats.getFlat(), numpy.arange(100).reshape(10, 10)
            )
        )
        self.assertTrue(
            numpy.array_equal(
                self.acquiTwoFlats.getFlat(index=300), numpy.arange(100).reshape(10, 10)
            )
        )
        self.assertTrue(
            numpy.array_equal(self.acquiTwoFlats.getFlat(index=600), self.flatField_600)
        )
        self.assertTrue(
            numpy.array_equal(self.acquiTwoFlats.getFlat(index=0), self.flatField_0)
        )


class TestScanValidatorFindNabuFiles(unittest.TestCase):
    """
    Make sure files produced by nabu can be seen as reconstruction files
    """

    class FileCreator(contextlib.AbstractContextManager):
        def __init__(self, file_path):
            self.__file_path = file_path

        def __enter__(self):
            with open(self.__file_path, "w"):
                pass

        def __exit__(self, exc_type, exc_val, exc_tb):
            if os.path.exists(self.__file_path):
                os.remove(self.__file_path)

    def setUp(self) -> None:
        self.scan = MockEDF.mockScan(tempfile.mkdtemp(), nPagRecons=0, nRecons=0)
        assert (
            len(self.scan.get_reconstructions_paths(self.scan.path)) == 0
        ), "make sure the initial environment is clear"

    def tearDown(self) -> None:
        shutil.rmtree(self.scan.path)

    def test(self) -> None:
        for slice_index in (None, 1, 15):
            for pag_db in (None, 100, 500):
                file_name = (
                    nabuslices.SingleSliceRunner.get_file_basename_reconstruction(
                        slice_index=slice_index,
                        scan=self.scan,
                        pag=pag_db is not None,
                        db=pag_db,
                    )
                )
                for file_extension in ("npy", "npz", "hdf5"):
                    with self.subTest(
                        slice_index=slice_index,
                        pag_db=pag_db,
                        file_extension=file_extension,
                    ):
                        file_path = os.path.join(
                            self.scan.path, file_name + "." + file_extension
                        )

                        # simple context Manager which create the file
                        # and remove it when leave
                        with TestScanValidatorFindNabuFiles.FileCreator(file_path):
                            n_to_discover = 1
                            if slice_index is None:
                                n_to_discover = 0
                            self.assertEqual(
                                len(
                                    self.scan.get_reconstructions_paths(self.scan.path)
                                ),
                                n_to_discover,
                            )


class TestScanValidatorFindPyHSTFiles(unittest.TestCase):
    """Function testing the getReconstructionsPaths function is correctly
    functioning"""

    DIM_MOCK_SCAN = 10

    N_RADIO = 20
    N_RECONS = 10
    N_PAG_RECONS = 5

    def setUp(self):
        # create scan folder
        self.path = tempfile.mkdtemp()
        MockEDF.mockScan(
            scanID=self.path,
            nRadio=self.N_RADIO,
            nRecons=self.N_RECONS,
            nPagRecons=self.N_PAG_RECONS,
            dim=self.DIM_MOCK_SCAN,
        )
        basename = os.path.basename(self.path)

        # add some random files
        for _file in ("45gfdgfg1.edf", "465slicetest1.edf", "slice_ab.edf"):
            with open(os.path.join(self.path, basename + _file), "w+") as ofile:
                ofile.write("test")

    def tearDown(self):
        if os.path.isdir(self.path):
            shutil.rmtree(self.path)

    def testGetRadioPaths(self):
        nFound = len(EDFTomoScan.get_proj_urls(self.path))
        self.assertTrue(nFound == self.N_RADIO)

    def testGetReconstructionsPaths(self):
        reconstruction_found = EDFTomoScan.get_reconstructions_paths(self.path)
        self.assertEqual(len(reconstruction_found), self.N_RECONS + self.N_PAG_RECONS)

    def testGetSliceReconstruction(self):
        self.assertTrue(
            EDFTomoScan.get_index_reconstructed("dfadf_slice_32.edf", "dfadf") == 32
        )
        self.assertTrue(
            EDFTomoScan.get_index_reconstructed("dfadf_slice_slice_002.edf", "dfadf")
            == 2
        )
        self.assertTrue(
            EDFTomoScan.get_index_reconstructed("scan_3slice_0050.edf", "scan_3") == 50
        )
        self.assertTrue(
            EDFTomoScan.get_index_reconstructed("scan3slice_012.edf", "scan3") == 12
        )


class TestRadioPath(unittest.TestCase):
    """Test static method getRadioPaths for EDFTomoScan"""

    def test(self):
        files = [
            "essai1_0008.edf",
            "essai1_0019.edf",
            "essai1_0030.edf",
            "essai1_0041.edf",
            "essai1_0052.edf",
            "essai1_0063.edf",
            "essai1_0074.edf",
            "essai1_0085.edf",
            "essai1_0096.edf",
            "essai1_.par",
            "refHST0100.edf",
            "darkend0000.edf",
            "essai1_0009.edf",
            "essai1_0020.edf",
            "essai1_0031.edf",
            "essai1_0042.edf",
            "essai1_0053.edf",
            "essai1_0064.edf",
            "essai1_0075.edf",
            "essai1_0086.edf",
            "essai1_0097.edf",
            "essai1_.rec",
            "essai1_0000.edf",
            "essai1_0010.edf",
            "essai1_0021.edf",
            "essai1_0032.edf",
            "essai1_0043.edf",
            "essai1_0054.edf",
            "essai1_0065.edf",
            "essai1_0076.edf",
            "essai1_0087.edf",
            "essai1_0098.edf",
            "essai1_slice_1023.edf",
            "essai1_0001.edf",
            "essai1_0011.edf",
            "essai1_0022.edf",
            "essai1_0033.edf",
            "essai1_0044.edf",
            "essai1_0055.edf",
            "essai1_0066.edf",
            "essai1_0077.edf",
            "essai1_0088.edf",
            "essai1_0099.edf",
            "essai1_slice.info",
            "essai1_0001.par",
            "essai1_0012.edf",
            "essai1_0023.edf",
            "essai1_0034.edf",
            "essai1_0045.edf",
            "essai1_0056.edf",
            "essai1_0067.edf",
            "essai1_0078.edf",
            "essai1_0089.edf",
            "essai1_0100.edf",
            "essai1_slice.par",
            "essai1_0002.edf",
            "essai1_0013.edf",
            "essai1_0024.edf",
            "essai1_0035.edf",
            "essai1_0046.edf",
            "essai1_0057.edf",
            "essai1_0068.edf",
            "essai1_0079.edf",
            "essai1_0090.edf",
            "essai1_0101.edf",
            "essai1_slice.xml",
            "essai1_0003.edf",
            "essai1_0014.edf",
            "essai1_0025.edf",
            "essai1_0036.edf",
            "essai1_0047.edf",
            "essai1_0058.edf",
            "essai1_0069.edf",
            "essai1_0080.edf",
            "essai1_0091.edf",
            "essai1_0102.edf",
            "essai1_.xml",
            "essai1_0004.edf",
            "essai1_0015.edf",
            "essai1_0026.edf",
            "essai1_0037.edf",
            "essai1_0048.edf",
            "essai1_0059.edf",
            "essai1_0070.edf",
            "essai1_0081.edf",
            "essai1_0092.edf",
            "essai1_0103.edf",
            "histogram_essai1_slice",
            "essai1_0005.edf",
            "essai1_0016.edf",
            "essai1_0027.edf",
            "essai1_0038.edf",
            "essai1_0049.edf",
            "essai1_0060.edf",
            "essai1_0071.edf",
            "essai1_0082.edf",
            "essai1_0093.edf",
            "essai1_0104.edf",
            "machinefile",
            "essai1_0006.edf",
            "essai1_0017.edf",
            "essai1_0028.edf",
            "essai1_0039.edf",
            "essai1_0050.edf",
            "essai1_0061.edf",
            "essai1_0072.edf",
            "essai1_0083.edf",
            "essai1_0094.edf",
            "essai1_.cfg",
            "pyhst_out.txt",
            "essai1_0007.edf",
            "essai1_0018.edf",
            "essai1_0029.edf",
            "essai1_0040.edf",
            "essai1_0051.edf",
            "essai1_0062.edf",
            "essai1_0073.edf",
            "essai1_0084.edf",
            "essai1_0095.edf",
        ]

        nbRadio = 0
        for f in files:
            nbRadio += EDFTomoScan.is_a_proj_path(f, "essai1_")
        self.assertTrue(nbRadio == 105)


class TestGetReconstructionPath(unittest.TestCase):
    """Test static method getReconstructionPaths for EDFTomoScan"""

    def setUp(self):
        self.tmpDir = tempfile.mkdtemp()
        self.dir = os.path.join(self.tmpDir, "scan_3")
        os.makedirs(self.dir)

    def tearDown(self):
        shutil.rmtree(self.tmpDir)

    def test1(self):
        """Make sure he can read 3 simple slice"""
        file_desc = fabio.edfimage.EdfImage(data=numpy.random.random((100, 100)))

        file_desc.write(os.path.join(self.dir, "scan_3slice_0050.edf"))
        file_desc.write(os.path.join(self.dir, "scan_3slice_0000.edf"))
        file_desc.write(os.path.join(self.dir, "scan_3slice_0010.edf"))
        assert len(os.listdir(self.dir)) == 3
        self.assertEqual(
            len(
                EDFTomoScan.get_reconstructions_paths(
                    os.path.join(self.tmpDir, "scan_3")
                )
            ),
            3,
        )

    def test2(self):
        """Make sure he can read a paganin and non-paganin at the same time"""
        file_desc = fabio.edfimage.EdfImage(data=numpy.random.random((100, 100)))

        file_desc.write(os.path.join(self.dir, "scan_3slice_0050.edf"))
        file_desc.write(os.path.join(self.dir, "scan_3slice_pag_0050.edf"))
        assert len(os.listdir(self.dir)) == 2
        self.assertEqual(
            len(
                EDFTomoScan.get_reconstructions_paths(
                    os.path.join(self.tmpDir, "scan_3")
                )
            ),
            2,
        )


class TestPaganinPath(unittest.TestCase):
    """Test static method getIndexReconstructed from EDFTomoScan"""

    def setUp(self):
        self.tmpDir = tempfile.mkdtemp()

        self.dir = os.path.join(self.tmpDir, "scan25")
        os.makedirs(self.dir)

    def tearDown(self):
        shutil.rmtree(self.tmpDir)

    def testPagFile(self):
        open(os.path.join(self.dir, "scan25slice_pag_db0500_0115.edf"), "a").close()
        self.assertEqual(len(EDFTomoScan.get_reconstructions_paths(self.dir)), 1)
        self.assertEqual(
            EDFTomoScan.get_index_reconstructed(
                "scan25slice_pag_db0500_0115.edf", scanID=self.dir
            ),
            115,
        )


class TestGetSinogram(unittest.TestCase):
    """Test functions relative to sinogram"""

    def setUp(self) -> None:
        self.tmp_dir = tempfile.mkdtemp()
        mock = MockEDF(
            scan_path=self.tmp_dir, scene="arange", n_radio=4, n_ini_radio=4, dim=2
        )
        mock.end_acquisition()
        self.scan = EDFTomoScan(scan=mock.scan_path)
        self.assertEqual(len(self.scan.projections), 4)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp_dir)

    def testGetSinogram(self):
        self.assertEqual(self.scan.tomo_n, 4)
        sinogram_1 = self.scan.get_sinogram(line=1)
        self.assertEqual(sinogram_1.shape, (4, 2))
        th_res = numpy.array([[2, 3], [6, 7], [10, 11], [14, 15]])
        self.assertTrue(numpy.array_equal(sinogram_1, th_res))


class TestSeveralWriteWithThreading(unittest.TestCase):
    class DummyProcess(Task):
        @staticmethod
        def program_name():
            """Name of the program used for this processing"""
            return "dummy program"

        @staticmethod
        def program_version():
            """version of the program used for this processing"""
            return "0.0.0"

        @staticmethod
        def definition():
            """definition of the process"""
            return "no definition"

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self._file = os.path.join(self.tmp_dir, "XXXtomwer_processes.h5")

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)

    def testSeveralWrite(self):
        processes = []
        for i in range(20):
            args = (
                self._file,
                TestSeveralWriteWithThreading.DummyProcess,
                "entry0000",
                {"info": "no configuration"},
                {"data": numpy.random.random(2000)},
                i,
                None,
                True,
            )
            processes.append(Process(target=Task._register_process, args=args))
        for process in processes:
            process.start()
        for process in processes:
            process.join()
