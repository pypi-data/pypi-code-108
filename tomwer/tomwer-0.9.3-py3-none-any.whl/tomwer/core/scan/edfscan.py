# coding: utf-8
# /*##########################################################################
# Copyright (C) 2016 European Synchrotron Radiation Facility
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
#############################################################################*/


__authors__ = ["H.Payno"]
__license__ = "MIT"
__date__ = "09/08/2018"


import os
import re
from collections import OrderedDict
from math import ceil
import fabio
import numpy
import functools
import logging
from tomoscan.scanbase import FOV
from tomwer.core.process.reconstruction.darkref.settings import (
    REFHST_PREFIX,
    DARKHST_PREFIX,
)
from tomwer.core.progress import Progress
from silx.io.url import DataUrl
import silx.io.utils
from glob import glob
from .scanbase import TomwerScanBase
from tomoscan.esrf.edfscan import EDFTomoScan as _tsEDFTomoScan
from tomwer.utils import docstring
from processview.core.dataset import DatasetIdentifier
from typing import Optional

_logger = logging.getLogger(__name__)


global counter_rand
counter_rand = 1  # used to be sure to return a unique index on recons slices


class _EDFTomoScanIdentifier(DatasetIdentifier):
    def __init__(self, dataset, edf_folder):
        super().__init__(dataset)
        self.edf_folder = os.path.realpath(os.path.abspath(edf_folder))

    @docstring(DatasetIdentifier)
    def long_description(self) -> str:
        return self.edf_folder

    def __str__(self):
        return os.path.basename(self.edf_folder)

    def __eq__(self, other):
        if isinstance(other, _EDFTomoScanIdentifier):
            return self.edf_folder == other.edf_folder
        else:
            return False

    def __hash__(self):
        return hash(self.edf_folder)


class EDFTomoScan(_tsEDFTomoScan, TomwerScanBase):
    """
    Class used to represent a tomography acquisition with hdf5 files.

    :param Union[str, None] scan: path of the scan
    """

    def __init__(self, scan, overwrite_proc_file=False):
        _tsEDFTomoScan.__init__(self, scan=scan)
        TomwerScanBase.__init__(self)

        self._dark = None
        self._process_file = self.get_process_file_name(self)
        self._init_index_process_file(overwrite_proc_file=overwrite_proc_file)

        if scan is not None:
            self.update()

    @staticmethod
    def get_process_file_name(scan):
        if scan.path is not None:
            basename = os.path.basename(scan.path)
            basename = "_".join((basename, "tomwer_processes.h5"))
            return os.path.join(scan.path, basename)
        else:
            return None

    def clear_caches(self):
        _tsEDFTomoScan.clear_caches(self)
        TomwerScanBase.clear_caches(self)
        self._dark = None

    @staticmethod
    def directory_contains_scan(directory, src_pattern, dest_pattern):
        """
        Check if the given directory is holding an acquisition

        :param str directory: directory we want to check
        :param str src_pattern: buffer name pattern ('lbsram')
        :param dest_pattern: output pattern (''). Needed because some
                             acquisition can split the file produce between
                             two directories. This is the case for edf,
                             where .info file are generated in /data/dir
                             instead of /lbsram/data/dir
        :return: does the given directory contains any acquisition
        :rtype: bool
        """
        aux = directory.split(os.path.sep)
        info_name = os.path.join(directory, aux[-1] + EDFTomoScan.INFO_EXT)

        if src_pattern:
            info_name = info_name.replace(src_pattern, dest_pattern, 1)
        return os.path.isfile(info_name)

    def data_flat_field_correction(self, data, index=None):
        """
        Apply the flat field correction on the given data.

        :param numpy.ndarray data: radio to correct
        :return numpy.ndarray: corrected data
        """
        dark = self.getDark()
        flat = self.getFlat()
        return self._flat_field_correction(
            data=data,
            dark=dark,
            flat1=flat,
            flat2=None,
            index_flat1=-1,
            index_flat2=-1,
            index_proj=index,
        )

    def update(self):
        """update list of radio and reconstruction by parsing the scan folder"""
        _tsEDFTomoScan.update(self)
        self.reconstructions = EDFTomoScan.get_reconstructions_paths(self.path)

    def projections_with_angle(self):
        return self.get_proj_angle_url()

    @staticmethod
    def get_reconstructions_paths(scanID, withIndex=False):
        """
        Return the dict of files:
        * fitting with a reconstruction pattern and ending by .edf
        * .vol files

        :param scanID: is the path to the folder of acquisition
        :param bool withIndex: if False then return a list of slices otherwise
            return a dict with the index of the slice reconstructed.
        """

        def containsDigits(input):
            return any(char.isdigit() for char in input)

        if (scanID is None) or (not os.path.isdir(scanID)):
            if withIndex is True:
                return {}
            else:
                return []

        pyhst_files = TomwerScanBase.get_pyhst_recons_file(scanID)
        if pyhst_files is not None:
            return TomwerScanBase.getReconstructedFilesFromParFile(
                pyhst_files, with_index=withIndex
            )
        else:
            folderBasename = os.path.basename(scanID)
            files = {} if withIndex is True else []
            if os.path.isdir(scanID):
                for f in os.listdir(scanID):
                    if (
                        f.endswith(TomwerScanBase.VALID_RECONS_EXTENSION)
                        and f.startswith(folderBasename)
                        and "slice_" in f
                    ):
                        local_str = f
                        for extension in TomwerScanBase.VALID_RECONS_EXTENSION:
                            if local_str.endswith(extension):
                                local_str = local_str.rsplit(extension, 1)[0]
                        if "slice_" in local_str:
                            if "slice_pag_" in local_str:
                                indexStr = local_str.split("slice_pag_")[-1].split("_")[
                                    0
                                ]
                            else:
                                indexStr = local_str.split("slice_")[-1].split("_")[0]
                            if containsDigits(indexStr):
                                gfile = os.path.join(scanID, f)
                                assert os.path.isfile(gfile)
                                if withIndex is True:
                                    files[
                                        EDFTomoScan.get_index_reconstructed(f, scanID)
                                    ] = gfile
                                else:
                                    files.append(gfile)
                    if f.endswith(".vol"):
                        if withIndex is True:
                            files[
                                EDFTomoScan.get_index_reconstructed(f, scanID)
                            ] = os.path.join(scanID, f)
                        else:
                            files.append(os.path.join(scanID, f))
            return files

    def load_from_dict(self, desc):
        _tsEDFTomoScan.load_from_dict(self, desc)
        TomwerScanBase.load_from_dict(self, desc)
        return self

    def _get_scheme(self):
        """

        :return: scheme to read url
        :rtype: str
        """
        return "fabio"

    @docstring(TomwerScanBase.get_sinogram)
    @functools.lru_cache(maxsize=16, typed=True)
    def get_sinogram(self, line, subsampling=1):
        """

        extract the sinogram from projections

        :param line: which sinogram we want
        :type: int
        :param subsampling: subsampling to apply if any. Allows to skip some io
        :type: int
        :return: sinogram from the radio lines
        :rtype: numpy.array
        """
        _logger.info(
            "compute sinogram for line %s of %s (subsampling: %s)"
            % (line, self.path, subsampling)
        )
        assert isinstance(line, int)
        if self.tomo_n is not None and self.dim_2 is not None and line > self.dim_2:
            raise ValueError("requested line %s is not in the scan")
        else:
            y_dim = ceil(self.tomo_n / subsampling)
            sinogram = numpy.empty((y_dim, self.dim_1))
            proj_urls = self.get_proj_angle_url()
            assert len(proj_urls) >= self.tomo_n
            proj_sort = list(proj_urls.keys())
            proj_sort = list(filter(lambda x: not isinstance(x, str), proj_sort))
            proj_sort.sort()
            advancement = Progress(
                name="compute sinogram for %s, line=%s,"
                "sampling=%s" % (os.path.basename(self.path), line, subsampling)
            )
            advancement.setMaxAdvancement(len(proj_sort))
            for i_proj, proj in enumerate(proj_sort):
                if i_proj % subsampling == 0:
                    url = proj_urls[proj]
                    radio = silx.io.utils.get_data(url)
                    radio = self.data_flat_field_correction(radio)
                    sinogram[i_proj // subsampling] = radio[line]
                advancement.increaseAdvancement(1)
            return sinogram

    @functools.lru_cache(maxsize=3)
    def getFlat(self, index=None):
        """
        If projectionI is not requested then return the mean value. Otherwise
        return the interpolated value for the requested projection.

        :param Union[int,None] index: index of the projection for which we want
                                      the flat
        :return: Flat field value or None if can't deduce it
        """
        data = self._extractFromOneFile("refHST.edf", what="flat")
        if data is not None:
            return data

        data = self._extractFromPrefix(REFHST_PREFIX, what="flat", proI=index)
        if data is not None:
            return data

        _logger.warning("Cannot retrieve flat file from %s" % self.path)
        return None

    @docstring(TomwerScanBase.get_proj_angle_url)
    def get_proj_angle_url(self, use_cache: bool = True):
        if not use_cache:
            self._cache_proj_urls = None

        if self._cache_proj_urls is None:
            self._cache_proj_urls = _tsEDFTomoScan.get_proj_angle_url(self)
        return self._cache_proj_urls

    @functools.lru_cache()
    def getDark(self):
        """
        For now only deal with one existing dark file.

        :return: image of the dark if existing. Else None
        """
        if self._dark is None:
            # first try to retrieve data from dark.edf file or darkHST.edf files
            self._dark = self._extractFromOneFile("dark.edf", what="dark")
            if self._dark is None:
                self._dark = self._extractFromOneFile("darkHST.edf", what="dark")
            if self._dark is None:
                self._dark = self._extractFromPrefix(DARKHST_PREFIX, what="dark")
            if self._dark is None:
                self._dark = self._extractFromPrefix("darkend", what="dark")

            if self._dark is None:
                _logger.warning("Cannot retrieve dark file from %s" % self.path)

        return self._dark

    def _extractFromOneFile(self, f, what):
        if self.path is None:
            return None
        path = os.path.join(self.path, f)
        if os.path.exists(path):
            _logger.info("Getting %s from %s" % (what, f))
            try:
                data = fabio.open(path).data
            except Exception:
                return None
            else:
                if data.ndim == 2:
                    return data
                elif data.ndim == 3:
                    _logger.warning(
                        "%s file contains several images. Taking "
                        "the mean value" % what
                    )
                    return numpy.mean(data.ndim)
        else:
            return None

    @staticmethod
    def guess_index_frm_EDFFile_name(_file):
        name = _file
        if name.endswith(".edf"):
            name = name.rstrip(".edf")
        ic = []
        while name[-1].isdigit():
            ic.append(name[-1])
            name = name[:-1]

        if len(ic) == 0:
            return None
        else:
            orignalOrder = ic[::-1]
            return int("".join(orignalOrder))

    def _extractFromPrefix(self, pattern, what, proI=None):
        if self.path is None:
            return None
        files = glob(os.path.join(self.path, pattern + "*.edf"))
        if len(files) == 0:
            return None
        else:
            d = {}
            for f in files:
                index = self.guess_index_frm_EDFFile_name(f)
                if index is None:
                    _logger.error("cannot retrieve projection index for %s" "" % f)
                    return None
                else:
                    d[index] = fabio.open(f).data

            if len(files) == 1:
                return d[list(d.keys())[0]]

            oProj = OrderedDict(sorted(d.items()))
            # for now we only deal with interpolation between the higher
            # and the lower acquired file ()
            lowPI = list(oProj.keys())[0]
            uppPI = list(oProj.keys())[-1]

            lowPD = oProj[lowPI]
            uppPD = oProj[uppPI]

            if len(oProj) > 2:
                _logger.info(
                    "Only bordering projections (%s and %s) will "
                    "be used for extracting %s" % (lowPI, uppPI, what)
                )

            uppPI = uppPI
            index = proI
            if index is None:
                index = (uppPI - lowPI) / 2

            if (index >= lowPI) is False:
                index = lowPI
                _logger.warning(
                    "ProjectionI not in the files indexes"
                    "range (projectionI >= lowerProjIndex)"
                )

            if (index <= uppPI) is False:
                index = uppPI
                _logger.warning(
                    "ProjectionI not in the files indexes"
                    "range upperProjIndex >= projectionI"
                )

            # simple interpolation
            _nRef = uppPI - lowPI
            lowPI = lowPI

            w0 = (lowPI + (uppPI - index)) / _nRef
            w1 = index / _nRef

            return w0 * lowPD + w1 * uppPD

    @staticmethod
    def get_index_reconstructed(reconstructionFile, scanID):
        """Return the slice reconstructed of a file from her name

        :param str reconstructionFile: the name of the file
        """
        folderBasename = os.path.basename(scanID)
        if reconstructionFile.endswith(".edf") and reconstructionFile.startswith(
            folderBasename
        ):
            localstring = reconstructionFile.rstrip(".edf")
            # remove the scan
            localstring = re.sub(folderBasename, "", localstring)
            s = localstring.split("_")
            if s[-1].isdigit():
                return int(s[-1])
            else:
                _logger.warning(
                    "Fail to find the slice reconstructed for "
                    "file %s" % reconstructionFile
                )
        else:
            global counter_rand
            counter_rand = counter_rand + 1
            return counter_rand

    @docstring(_tsEDFTomoScan.to_dict)
    def to_dict(self):
        res = _tsEDFTomoScan.to_dict(self)
        res.update(TomwerScanBase.to_dict(self))
        return res

    @docstring(TomwerScanBase._deduce_transfert_scan)
    def _deduce_transfert_scan(self, output_dir):
        if os.path.basename(output_dir) != os.path.basename(self.path):
            raise ValueError(
                "Transfert to a new EDFTomoScan requires an "
                "equal basename. Current path is {}, requested "
                "one is {}".format(self.path, output_dir)
            )
        return EDFTomoScan(scan=output_dir)

    def __str__(self):
        return self.path

    # Dataset implementation

    @staticmethod
    def from_dataset_identifier(identifier):
        """Return the Dataset from a identifier"""
        if not isinstance(identifier, _EDFTomoScanIdentifier):
            raise TypeError(
                "identifier should be an instance of " "_HDF5TomoScanIdentifier"
            )
        return EDFTomoScan(scan=identifier.edf_folder)

    @docstring(TomwerScanBase)
    def get_dataset_identifier(self) -> DatasetIdentifier:
        return _EDFTomoScanIdentifier(dataset=self, edf_folder=self.path)

    @docstring(TomwerScanBase)
    def get_nabu_dataset_info(self, binning=1, binning_z=1, proj_subsampling=1):
        return {
            "hdf5_entry": "",
            "location": self.path,
            "binning": binning,
            "binning_z": binning_z,
            "projections_subsampling": proj_subsampling,
        }

    @docstring(TomwerScanBase)
    def to_nabu_dataset_analyser(self):
        from nabu.resources.dataset_analyzer import EDFDatasetAnalyzer

        analyzer = EDFDatasetAnalyzer(location=self.path)
        n_angles = analyzer.n_angles
        if analyzer.rotation_angles is None:
            if self.field_of_view is FOV.HALF:
                angles = numpy.linspace(0, 2 * numpy.pi, n_angles, True)
            else:
                angles = numpy.linspace(0, numpy.pi, n_angles, False)

        analyzer.rotation_angles = angles
        return analyzer

    @docstring(TomwerScanBase)
    def scan_dir_name(self) -> Optional[str]:
        """for 'this/is/my/acquisition' returns 'acquisition'"""
        if self.path is not None:
            return self.path.split(os.sep)[-1]
        else:
            return None

    @docstring(TomwerScanBase)
    def scan_basename(self) -> Optional[str]:
        """for 'this/is/my/acquisition' returns 'acquisition'"""
        if self.path is not None:
            return self.path
        else:
            return None

    @docstring(TomwerScanBase)
    def scan_parent_dir_basename(self) -> Optional[str]:
        if self.path is not None:
            try:
                return os.path.dirname(self.path)
            except Exception:
                return None
        else:
            return None


def _get_urls_list(radio):
    """create the list of urls contained in a .edf file"""
    with fabio.open(radio) as edf_reader:
        if edf_reader.nframes == 1:
            return [DataUrl(file_path=radio, scheme="fabio")]
        else:
            res = []
            for iframe in range(edf_reader.nframes):
                res.append(
                    DataUrl(file_path=radio, data_slice=[iframe], scheme="fabio")
                )
            return res
