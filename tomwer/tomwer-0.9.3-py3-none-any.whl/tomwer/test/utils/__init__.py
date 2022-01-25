#!/usr/bin/python
# coding: utf-8
#
#    Project: Azimuthal integration
#             https://github.com/pyFAI/pyFAI
#
#    Copyright (C) 2015 European Synchrotron Radiation Facility, Grenoble, France
#
#    Principal author:       Jérôme Kieffer (Jerome.Kieffer@ESRF.eu)
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


__doc__ = """test module for pyFAI."""
__authors__ = ["Jérôme Kieffer", "Valentin Valls", "Henri Payno"]
__license__ = "MIT"
__copyright__ = "European Synchrotron Radiation Facility, Grenoble, France"
__date__ = "07/02/2017"

import os
import shutil
import fileinput
from tomwer.core.utils import DownloadDataset, url_base
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class UtilsTest(object):
    """
    Static class providing useful stuff for preparing tests.
    """

    timeout = 100  # timeout in seconds for downloading datasets.tar.bz2

    def __init__(self):
        self.installed = False

    @classmethod
    def dataDownloaded(cls, archive_folder, archive_file):
        return cls.dataIsHere(archive_folder=archive_folder) or cls.dataIsDownloaded(
            archive_file=archive_file
        )

    @classmethod
    def dataIsHere(cls, archive_folder):
        return os.path.isdir(archive_folder)

    @classmethod
    def dataIsDownloaded(cls, archive_file):
        return os.path.isfile(archive_file)

    @classmethod
    def getEDFDataset(cls, folderID):
        path = os.path.abspath(
            os.path.join(cls.getDatasets(name="edf_datasets"), folderID)
        )
        if os.path.isdir(path):
            return path
        else:
            raise RuntimeError("Coul'd find folder containing scan %s" % folderID)

    @classmethod
    def getH5Dataset(cls, folderID):
        path = os.path.abspath(
            os.path.join(cls.getDatasets(name="h5_datasets"), folderID)
        )
        if os.path.exists(path):
            return path
        else:
            raise RuntimeError("Coul'd find folder containing scan %s" % folderID)

    @classmethod
    def getBlissDataset(cls, folderID):
        path = os.path.abspath(
            os.path.join(cls.getDatasets(name="bliss_acq"), folderID)
        )
        if os.path.exists(path):
            return path
        else:
            raise RuntimeError("Coul'd find folder containing scan %s" % folderID)

    @classmethod
    def getRecDatasets(cls):
        path = os.path.abspath(
            cls.getDatasets(
                name="rec_HA-700_45.4_136keV_BM5_burrow_GSA-1-44_021_avg-2_"
            )
        )
        if os.path.exists(path):
            return path
        else:
            raise RuntimeError("Coul'd find folder containing rec")

    @classmethod
    def getOrangeTestFile(cls, folderID):
        path = os.path.abspath(os.path.join(cls.getOrangeTestFiles(), folderID))
        if os.path.isfile(path):
            return path
        else:
            raise RuntimeError("Coul'd find folder containing scan %s" % folderID)

    @classmethod
    def getOrangeTestFiles(cls):
        return cls.getDatasets(name="orangetestfiles")

    @classmethod
    def getOrangeExecTestFile(cls, folderID):
        path = os.path.abspath(os.path.join(cls.getOrangeExecTestFiles(), folderID))
        if os.path.isfile(path):
            return path
        else:
            raise RuntimeError("Coul'd find folder containing scan %s" % folderID)

    @classmethod
    def getOrangeExecTestFiles(cls):
        return cls.getDatasets(name="ows_test_exec")

    @classmethod
    def getDatasets(cls, name="datasets"):
        """
        Downloads the requested image from Forge.EPN-campus.eu

        @param: name of the image.
        For the RedMine forge, the filename contains a directory name that is removed
        @return: full path of the locally saved file
        """
        archive_file = name + ".tar.bz2"
        archive_folder = "".join((os.path.dirname(__file__), "/" + name + "/"))
        archive_file = os.path.join(archive_folder, archive_file)

        # download if needed
        if not cls.dataDownloaded(
            archive_folder=archive_folder, archive_file=archive_file
        ):
            DownloadDataset(
                dataset=os.path.basename(archive_file),
                output_folder=archive_folder,
                timeout=cls.timeout,
            )

            if not os.path.isfile(archive_file):
                raise RuntimeError(
                    "Could not automatically download test images %s!\n"
                    "If you are behind a firewall, please set both environment "
                    "variable http_proxy and https_proxy. "
                    "This even works under windows ! \n Otherwise please try "
                    "to download the images manually from \n%s/%s"
                    % (archive_file, url_base, archive_file)
                )

        # decompress if needed
        if os.path.isfile(archive_file):
            logger.info("decompressing %s." % archive_file)
            outdir = "".join((os.path.dirname(__file__)))
            shutil.unpack_archive(archive_file, extract_dir=outdir, format="bztar")
            os.remove(archive_file)
        else:
            logger.info("not trying to decompress it")
        return archive_folder

    @classmethod
    def hasInternalTest(cls, dataset):
        """
        The id of the internal test is to have some large scan accessible
        which are stored locally. This should be used only for unit test that
        can be skipped
        """
        if "TOMWER_ADDITIONAL_TESTS_DIR" not in os.environ:
            return False
        else:
            dir = os.path.join(os.environ["TOMWER_ADDITIONAL_TESTS_DIR"], dataset)
        return os.path.isdir(dir)

    @classmethod
    def getInternalTestDir(cls, dataset):
        if cls.hasInternalTest(dataset) is False:
            return None
        else:
            return os.path.join(os.environ["TOMWER_ADDITIONAL_TESTS_DIR"], dataset)


def rebaseParFile(filePath, scanOldPath, scanNewPath):
    """
    Change some variables on the oar file to rebase it like if it was acquire
    in scanNewPath and allow pyhst reconstruction.
    """
    assert os.path.isfile(filePath)

    with fileinput.FileInput(filePath, inplace=True, backup=".bak") as file:
        for line in file:
            print(line.replace(scanOldPath, scanNewPath))


def rebaseAcquisition(src, dst):
    """Copy the acquisition from src to dst by changing the ID of the acquisition
    on all files and sub-folders"""

    def copyDir(_dirSrc, _dirDst, srcID, dstID):
        assert os.path.exists(_dirDst) is False
        os.makedirs(_dirDst)
        for _file in os.listdir(_dirSrc):
            _filePath = os.path.join(_dirSrc, _file)
            if os.path.isdir(_filePath):
                copyDir(
                    _dirSrc=_filePath,
                    _dirDst=os.path.join(_dirDst, _file.replace(srcID, dstID, 1)),
                    srcID=srcID,
                    dstID=dstID,
                )
            else:
                shutil.copyfile(
                    src=_filePath,
                    dst=os.path.join(_dirDst, _file.replace(srcID, dstID, 1)),
                )

    # cp folder then copy files
    assert os.path.isdir(src)
    srcID = os.path.basename(src)
    dstID = os.path.basename(dst)
    copyDir(_dirSrc=src, _dirDst=dst, srcID=srcID, dstID=dstID)


def skip_gui_test():
    return os.environ.get("_TOMWER_NO_GUI_UNIT_TESTS", "False") == "True"


def skip_orange_workflows_test():
    return os.environ.get("_TOMWER_NO_ORANGE_WORKFLOWS_UNIT_TESTS", "False") == "True"
