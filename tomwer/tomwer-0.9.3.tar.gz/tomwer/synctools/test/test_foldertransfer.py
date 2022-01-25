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


from tomwer.synctools.datatransfert import ScanTransfer
from tomwer.core.scan.scanfactory import ScanFactory
from tomwer.core.utils import rebaseParFile
from tomwer.core.utils.scanutils import MockEDF
from tomwer.test.utils import UtilsTest
from tomwer.core.scan.hdf5scan import HDF5TomoScan
from nxtomomill import converter as nxtomomill_converter
from silx.gui.utils.testutils import TestCaseQt
from glob import glob
import unittest
import os
import tempfile
import shutil
import logging
import pytest

try:
    from tomwer.synctools.rsyncmanager import RSyncManager
except ImportError:
    has_rsync = False
else:
    has_rsync = True

logging.disable(logging.INFO)


class TestEDFDataTransfert(TestCaseQt):
    """
    Test that the folder transfert process is valid
    """

    def setUp(self):
        TestCaseQt.setUp(self)
        self.sourcedir = tempfile.mkdtemp()
        self.n_file = 10
        MockEDF.fastMockAcquisition(self.sourcedir, n_radio=self.n_file)
        self.scan = ScanFactory.create_scan_object(self.sourcedir)
        assert os.path.isdir(self.sourcedir)
        self.targettedir = tempfile.mkdtemp()
        assert os.path.isdir(self.targettedir)
        self.outputdir = os.path.join(
            self.targettedir, os.path.basename(self.sourcedir)
        )

    def tearDown(self):
        if os.path.isdir(self.sourcedir):
            shutil.rmtree(self.sourcedir)
        if os.path.isdir(self.targettedir):
            shutil.rmtree(self.targettedir)
        TestCaseQt.tearDown(self)

    def testMoveFiles(self):
        """
        simple test that files are moved
        """
        folder_trans_process = ScanTransfer(
            inputs={
                "data": self.scan,
                "turn_off_print": True,
                "copying": False,
                "dest_dir": self.targettedir,
                "noRsync": True,
            }
        )
        folder_trans_process.run()
        self.assertTrue(os.path.isdir(self.outputdir))
        self.assertTrue(self.checkDataCopied())

    def testCopyFiles(self):
        """
        Simple test that file are copy and deleted
        """
        folder_trans_process = ScanTransfer(
            inputs={
                "data": self.scan,
                "turn_off_print": True,
                "copying": False,
                "dest_dir": self.targettedir,
                "noRsync": True,
                "move": False,
            }
        )
        folder_trans_process.run()
        self.assertTrue(self.checkDataCopied())

    def testMoveFilesForce(self):
        """
        Test the force option of folderTransfert
        """
        assert not os.path.isdir(self.outputdir)
        assert os.path.isdir(self.scan.path)
        folder_trans_process = ScanTransfer(
            inputs={
                "data": self.scan,
                "turn_off_print": True,
                "copying": False,
                "dest_dir": self.targettedir,
                "noRsync": True,
                "move": True,
                "force": False,
            }
        )
        folder_trans_process.run()

        MockEDF.fastMockAcquisition(self.sourcedir, n_radio=self.n_file)
        folder_trans_process = ScanTransfer(
            inputs={
                "data": self.scan,
                "turn_off_print": True,
                "copying": False,
                "dest_dir": self.targettedir,
                "noRsync": True,
                "move": True,
                "force": False,
            }
        )
        with self.assertRaises(shutil.Error):
            self.assertRaises(folder_trans_process.run())

        folder_trans_process = ScanTransfer(
            inputs={
                "data": self.scan,
                "turn_off_print": True,
                "copying": False,
                "dest_dir": self.targettedir,
                "noRsync": True,
                "move": True,
                "force": True,
            }
        )
        folder_trans_process.run()
        self.assertTrue(self.checkDataCopied())

    def testCopyFilesForce(self):
        """
        Test the force option for the copy files process
        """
        assert not os.path.isdir(self.outputdir)
        os.makedirs(self.outputdir)
        assert os.path.isdir(self.outputdir)

        folder_trans_process = ScanTransfer(
            inputs={
                "data": self.scan,
                "turn_off_print": True,
                "copying": False,
                "dest_dir": self.targettedir,
                "noRsync": True,
                "move": False,
                "force": False,
            }
        )
        folder_trans_process.run()
        self.assertTrue(self.checkDataCopied())

        MockEDF.fastMockAcquisition(self.sourcedir, n_radio=self.n_file)
        self.assertTrue(self.scan.path == self.sourcedir)

        folder_trans_process = ScanTransfer(
            inputs={
                "data": self.scan,
                "turn_off_print": True,
                "copying": False,
                "dest_dir": self.targettedir,
                "noRsync": True,
                "move": False,
                "force": False,
            }
        )

        with self.assertRaises(FileExistsError):
            self.assertRaises(folder_trans_process.run())

        folder_trans_process = ScanTransfer(
            inputs={
                "data": self.scan,
                "turn_off_print": True,
                "copying": False,
                "dest_dir": self.targettedir,
                "noRsync": True,
                "move": False,
                "force": True,
            }
        )
        folder_trans_process.run()
        self.assertTrue(self.checkDataCopied())

    def checkDataCopied(self):
        outputFiles = os.listdir(self.outputdir)
        inputFile = glob(self.sourcedir)
        # + 3 because .info and .xml are count + one tomwer_processes file
        return (
            (len(inputFile) == 0)
            and (len(outputFiles) == (self.n_file + 3))
            and (not os.path.isdir(self.sourcedir))
        )


@pytest.mark.skipif(RSyncManager().has_rsync() is False, reason="Rsync is missing")
class TestHDFDataTransfert(unittest.TestCase):
    """Make sure we can transfer data from bliss acquisition"""

    def setUp(self):
        self.input_dir = tempfile.mkdtemp()
        self.output_dir = tempfile.mkdtemp()
        shutil.copytree(
            UtilsTest.getBlissDataset(folderID="sample"),
            os.path.join(self.input_dir, "sample"),
        )

        self._proposal_file = os.path.join(
            self.input_dir, "sample", "ihpayno_sample.h5"
        )
        assert os.path.exists(self._proposal_file)
        self._sample_file = os.path.join(
            self.input_dir, "sample", "sample_29042021", "sample_29042021.h5"
        )
        assert os.path.exists(self._sample_file)
        self._sample_file_entry = "/1.1"

        output_file_path = os.path.join(
            self.input_dir, "sample", "sample_29042021", "nx_file.nx"
        )
        # convert it to nx
        files_entries = nxtomomill_converter.h5_to_nx(
            input_file_path=self._sample_file,
            output_file=output_file_path,
            entries=(self._sample_file_entry,),
            single_file=False,
            ask_before_overwrite=False,
            request_input=False,
            file_extension=".nx",
        )
        assert len(files_entries) == 1
        output_file_path, entry = files_entries[0]
        assert os.path.exists(output_file_path)
        assert os.path.isfile(output_file_path)
        self.scan = HDF5TomoScan(scan=output_file_path, entry=entry)

        # register information regarding origin of the file
        from tomwer.core.process.control.datalistener import DataListener

        source_scans = DataListener._get_scan_sources(
            self._sample_file, self._sample_file_entry
        )
        DataListener._register_process(
            process_file=self.scan.process_file,
            process=DataListener,
            entry=self.scan.entry,
            results={"output_file": self.scan.master_file, "entry": self.scan.entry},
            configuration={
                "sample_file": self._sample_file,
                "entry": self._sample_file_entry,
                "source_scans": source_scans,
                "file_proposal": self._proposal_file,
            },
            process_index=self.scan.pop_process_index(),
            overwrite=True,
        )

    def tearDown(self):
        for dir_ in (self.input_dir, self.output_dir):
            shutil.rmtree(dir_)

    def testDataTransfert(self):
        process = ScanTransfer(
            inputs={
                "data": self.scan,
                "dest_dir": os.path.join(self.output_dir, "sample"),
                "force_sync": True,
            }
        )
        process.run()
        output_scan = os.path.join(
            self.output_dir, "sample", "sample_29042021", "scan0002"
        )
        output_proposal_file = os.path.join(
            self.output_dir, "sample", "ihpayno_sample.h5"
        )
        output_sample_file = os.path.join(
            self.output_dir, "sample", "sample_29042021", "sample_29042021.h5"
        )
        self.assertTrue(os.path.exists(output_scan))
        self.assertEqual(len(os.listdir(output_scan)), 3)
        self.assertTrue(os.path.exists(output_proposal_file))
        self.assertTrue(os.path.exists(output_sample_file))
        other_scan_dir = os.path.join(self.output_dir, "sample", "scan0004")
        self.assertFalse(os.path.exists(other_scan_dir))


class TestPreTransfert(unittest.TestCase):
    """Test the pretransfert actions"""

    def setUp(self):
        unittest.TestCase.setUp(self)
        folderDataset = UtilsTest.getEDFDataset("scan_3_")
        self.tmpdir = tempfile.mkdtemp()
        self.outputfolder = tempfile.mkdtemp()
        scan_path = os.path.join(self.tmpdir, "scan_3_")
        shutil.copytree(src=folderDataset, dst=scan_path)
        self.scan = ScanFactory.create_scan_object(scan_path=scan_path)

    def tearDown(self):
        unittest.TestCase.tearDown(self)
        for _dir in (self.tmpdir, self.outputfolder):
            if os.path.exists(_dir):
                shutil.rmtree(_dir)

    def testParFile(self):
        """Make sure the scan_3_.par is correctly updated when moved"""
        parDict = self.getParDict(os.path.join(self.scan.path, "scan_3_.par"))
        assert (
            parDict["file_prefix"]
            == "/data/visitor/mi1226/id19/nemoz/henri/scan_3_/scan_3_"
        )
        assert (
            parDict["ff_prefix"]
            == "/data/visitor/mi1226/id19/nemoz/henri/scan_3_/refHST"
        )
        rebaseParFile(
            os.path.join(self.scan.path, "scan_3_.par"),
            oldfolder="/data/visitor/mi1226/id19/nemoz/henri/scan_3_",
            newfolder=self.scan.path,
        )
        parDict = self.getParDict(os.path.join(self.scan.path, "scan_3_.par"))
        self.assertTrue(
            parDict["file_prefix"] == os.path.join(self.scan.path, "scan_3_")
        )
        self.assertTrue(parDict["ff_prefix"] == os.path.join(self.scan.path, "refHST"))
        folderTrans = ScanTransfer(
            inputs={
                "turn_off_print": True,
                "copying": False,
                "dest_dir": self.outputfolder,
                "data": self.scan,
                "move": False,
                "force": True,
                "noRsync": True,
            }
        )

        folderTrans.run()
        parDict = self.getParDict(
            os.path.join(self.outputfolder, "scan_3_", "scan_3_.par")
        )
        self.assertTrue(
            parDict["file_prefix"]
            == os.path.join(self.outputfolder, "scan_3_", "scan_3_")
        )
        self.assertTrue(
            parDict["ff_prefix"] == os.path.join(self.outputfolder, "scan_3_", "refHST")
        )

    @staticmethod
    def getParDict(_file):
        assert os.path.isfile(_file)
        ddict = {}
        f = open(_file, "r")
        lines = f.readlines()
        for line in lines:
            if "=" not in line:
                continue
            line_str = line.rstrip().replace(" ", "")
            line_str = line_str.split("#")[0]
            key, value = line_str.split("=")
            ddict[key.lower()] = value
        return ddict
