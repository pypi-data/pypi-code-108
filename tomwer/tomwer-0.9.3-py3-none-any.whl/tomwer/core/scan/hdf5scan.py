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


from .scanbase import TomwerScanBase
from tomoscan.esrf.hdf5scan import HDF5TomoScan as _tsHDF5TomoScan
from tomoscan.esrf.hdf5scan import ImageKey
from tomoscan.io import HDF5File
from processview.core.dataset import DatasetIdentifier
import functools
import json
import io
import h5py
import os
from tomwer.utils import docstring
import logging
from typing import Optional

_logger = logging.getLogger(__name__)


class _HDF5TomoScanIdentifier(DatasetIdentifier):
    def __init__(self, dataset, hdf5_file, entry):
        super().__init__(dataset)
        self.hdf5_file = os.path.realpath(os.path.abspath(hdf5_file))
        self.entry = entry

    @docstring(DatasetIdentifier)
    def long_description(self) -> str:
        return "@".join((self.entry, self.hdf5_file))

    def __str__(self):
        return "@".join((self.entry, os.path.basename(self.hdf5_file)))

    def __eq__(self, other):
        if isinstance(other, _HDF5TomoScanIdentifier):
            return self.hdf5_file == other.hdf5_file and self.entry == other.entry
        else:
            return False

    def __hash__(self):
        return hash((self.hdf5_file, self.entry))


class HDF5TomoScan(_tsHDF5TomoScan, TomwerScanBase):
    """
    This is the implementation of a TomoBase class for an acquisition stored
    in a HDF5 file.

    For now several property of the acquisition is accessible thought a getter
    (like get_scan_range) and a property (scan_range).

    This is done to be compliant with TomoBase instanciation. But his will be
    replace progressively by properties at the 'TomoBase' level

    :param scan: scan directory or scan masterfile.h5
    :type: Union[str,None]
    """

    _TYPE = "hdf5"

    def __init__(self, scan, entry, index=None, overwrite_proc_file=False):
        TomwerScanBase.__init__(self)
        _tsHDF5TomoScan.__init__(self, scan=scan, entry=entry, index=index)
        self._reconstruction_urls = None
        self._projections_with_angles = None
        self._process_file = self.get_process_file_name(self)
        self._init_index_process_file(overwrite_proc_file=overwrite_proc_file)

    @staticmethod
    def get_process_file_name(scan):
        if scan.path is not None:
            basename, _ = os.path.splitext(scan.master_file)
            basename = os.path.basename(basename)
            basename = "_".join((basename, "tomwer_processes.h5"))
            return os.path.join(scan.path, basename)
        else:
            return None

    @staticmethod
    def directory_contains_scan(directory, src_pattern=None, dest_pattern=None):
        """

        Check if the given directory is holding an acquisition

        :param str directory: directory we want to check
        :param str src_pattern: buffer name pattern ('lbsram')
        :param dest_pattern: output pattern (''). Needed because some
                             acquisition can split the file produce between
                             two directories. This is the case for edf,
                             where .info file are generated in /data/dir
                             instead of /lbsram/data/dir
        :type: str
        :return: does the given directory contains any acquisition
        :rtype: bool
        """
        master_file = os.path.join(directory, os.path.basename(directory))
        if os.path.exists("master_file.hdf5"):
            return True
        else:
            return os.path.exists(master_file + ".h5")

    def is_abort(self, src_pattern, dest_pattern):
        """
        Check if the acquisition have been aborted. In this case the directory
        should contain a [scan].abo file

        :param str src_pattern: buffer name pattern ('lbsram')
        :param dest_pattern: output pattern (''). Needed because some
                             acquisition can split the file produce between
                             two directories. This is the case for edf,
                             where .info file are generated in /data/dir
                             instead of /lbsram/data/dir
        :return: True if the acquisition have been abort and the directory
                 should be abort
        """
        # for now there is no abort definition in .hdf5
        return False

    @staticmethod
    def from_dict(_dict):
        path = _dict[HDF5TomoScan.DICT_PATH_KEY]
        entry = _dict[HDF5TomoScan._DICT_ENTRY_KEY]

        scan = HDF5TomoScan(scan=path, entry=entry)
        scan.load_from_dict(_dict=_dict)
        return scan

    @docstring(TomwerScanBase)
    def load_from_dict(self, _dict):
        """

        :param _dict:
        :return:
        """
        if isinstance(_dict, io.TextIOWrapper):
            data = json.load(_dict)
        else:
            data = _dict
        if not (self.DICT_TYPE_KEY in data and data[self.DICT_TYPE_KEY] == self._TYPE):
            raise ValueError("Description is not an EDFScan json description")

        _tsHDF5TomoScan.load_from_dict(self, _dict)
        TomwerScanBase.load_from_dict(self, _dict)
        return self

    @docstring(TomwerScanBase)
    def to_dict(self) -> dict:
        ddict = _tsHDF5TomoScan.to_dict(self)
        ddict.update(TomwerScanBase.to_dict(self))
        return ddict

    def update(self):
        """update list of radio and reconstruction by parsing the scan folder"""
        if self.master_file is None:
            return
        if not os.path.exists(self.master_file):
            return
        _tsHDF5TomoScan.update(self)
        self.reconstructions = self.get_reconstructions_urls()

    def _get_scheme(self):
        """

        :return: scheme to read url
        :rtype: str
        """
        return "silx"

    def is_finish(self):
        return len(self.projections) >= self.tomo_n

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
        # force load of normed flats and normed darks
        self.normed_flats
        self.normed_darks
        return _tsHDF5TomoScan.get_sinogram(self, line=line, subsampling=subsampling)

    @property
    def normed_darks(self):
        if self._normed_darks is None:
            if self.process_file is not None and os.path.exists(self.process_file):
                from tomwer.core.process.reconstruction.darkref.darkrefs import (
                    DarkRefs,
                )  # avoid cyclic import

                normed_darks = DarkRefs.get_darks_frm_process_file(
                    process_file=self.process_file, entry=self.entry
                )
                if normed_darks is not None:
                    self.set_normed_darks(darks=normed_darks)
        return self._normed_darks

    @property
    def normed_flats(self):
        if self._normed_flats is None:
            if self.process_file is not None and os.path.exists(self.process_file):
                from tomwer.core.process.reconstruction.darkref.darkrefs import (
                    DarkRefs,
                )  # avoid cyclic import

                normed_flats = DarkRefs.get_flats_frm_process_file(
                    process_file=self.process_file, entry=self.entry
                )
                if normed_flats is not None:
                    self.set_normed_flats(flats=normed_flats)
        return self._normed_flats

    @docstring(TomwerScanBase.get_proj_angle_url)
    def get_proj_angle_url(self, use_cache: bool = True):
        if not use_cache:
            self._cache_proj_urls = None

        if self._cache_proj_urls is None:
            frames = self.frames
            if frames is None:
                return {}

            self._cache_proj_urls = {}
            for frame in frames:
                if frame.image_key is ImageKey.PROJECTION:
                    if frame.is_control:
                        self._cache_proj_urls[
                            "{} (1)".format(frame.rotation_angle)
                        ] = frame.url
                    else:
                        self._cache_proj_urls[str(frame.rotation_angle)] = frame.url
        return self._cache_proj_urls

    @docstring(TomwerScanBase._deduce_transfert_scan)
    def _deduce_transfert_scan(self, output_dir):
        new_master_file_path = os.path.join(
            output_dir, os.path.basename(self.master_file)
        )
        return HDF5TomoScan(scan=new_master_file_path, entry=self.entry)

    def data_flat_field_correction(self, data, index=None):
        flats = self.normed_flats
        flat1 = flat2 = None
        index_flat1 = index_flat2 = None
        if flats is not None:
            flat_indexes = sorted(list(flats.keys()))
            if len(flats) > 0:
                index_flat1 = flat_indexes[0]
                flat1 = flats[index_flat1]
            if len(flats) > 1:
                index_flat2 = flat_indexes[-1]
                flat2 = flats[index_flat2]
        darks = self.normed_darks
        dark = None
        if darks is not None and len(darks) > 0:
            # take only one dark into account for now
            dark = list(darks.values())[0]
        return self._flat_field_correction(
            data=data,
            dark=dark,
            flat1=flat1,
            flat2=flat2,
            index_flat1=index_flat1,
            index_flat2=index_flat2,
            index_proj=index,
        )

    @docstring(_tsHDF5TomoScan.ff_interval)
    @property
    def ff_interval(self):
        """
        Make some assumption to compute the flat field interval:
        """

        def get_first_two_ff_indexes():
            if self.flats is None:
                return None, None
            else:
                self._last_flat_index = None
                self._first_serie_flat_index = None
                for flat_index in self.flats:
                    if self._last_flat_index is None:
                        self._last_flat_index = flat_index
                    elif flat_index == self._last_flat_index + 1:
                        self._last_flat_index = flat_index
                        continue
                    else:
                        return self._last_flat_index, flat_index
            return None, None

        first_serie_index, second_serie_index = get_first_two_ff_indexes()
        if first_serie_index is None:
            return 0
        elif second_serie_index is not None:
            return second_serie_index - first_serie_index - 1
        else:
            return 0

    def __str__(self):
        return "@".join((self.entry, self.master_file))

    def projections_with_angle(self):
        """projections / radio, does not include the return projections"""
        if self._projections_with_angles is None:
            if self.frames:
                proj_frames = tuple(
                    filter(
                        lambda x: x.image_key == ImageKey.PROJECTION
                        and x.is_control is False,
                        self.frames,
                    )
                )
                self._projections_with_angles = {}
                for proj_frame in proj_frames:
                    self._projections_with_angles[
                        proj_frame.rotation_angle
                    ] = proj_frame.url
        return self._projections_with_angles

    @staticmethod
    def is_nexus_nxtomo_file(file_path: str) -> bool:
        if h5py.is_hdf5(file_path):
            return len(HDF5TomoScan.get_nxtomo_entries(file_path)) > 0

    @staticmethod
    def get_nxtomo_entries(file_path: str) -> tuple:
        if not h5py.is_hdf5(file_path):
            return tuple()
        else:
            res = []
            with HDF5File(file_path, mode="r", swmr=True, libver="latest") as h5s:
                for entry_name, node in h5s.items():
                    if isinstance(node, h5py.Group):
                        if HDF5TomoScan.entry_is_nx_tomo(node):
                            res.append(entry_name)
            return tuple(res)

    @staticmethod
    def entry_is_nx_tomo(entry: h5py.Group):
        return ("beam" in entry and "instrument" in entry and "sample" in entry) or (
            hasattr(entry, "attrs")
            and "definition" in entry.attrs
            and entry.attrs["definition"] == "NXtomo"
        )

    @staticmethod
    def is_nxdetector(grp: h5py.Group):
        """
        Check if the grp is an nx detector

        :param h5py.Group grp:
        :return: True if this is the definition of a group
        :rtype: bool
        """
        if hasattr(grp, "attrs"):
            if "NX_class" in grp.attrs and grp.attrs["NX_class"] == "NXdetector":
                return True
        return False

    # Dataset implementation

    @staticmethod
    def from_dataset_identifier(identifier):
        """Return the Dataset from a identifier"""
        if not isinstance(identifier, _HDF5TomoScanIdentifier):
            raise TypeError(
                "identifier should be an instance of " "_HDF5TomoScanIdentifier"
            )
        return HDF5TomoScan(scan=identifier.hdf5_file, entry=identifier.entry)

    @docstring(TomwerScanBase)
    def get_dataset_identifier(self) -> DatasetIdentifier:
        return _HDF5TomoScanIdentifier(
            dataset=self, hdf5_file=self.master_file, entry=self.entry
        )

    @docstring(TomwerScanBase)
    def get_nabu_dataset_info(self, binning=1, binning_z=1, proj_subsampling=1):
        if not isinstance(binning, int):
            raise TypeError("binning should be an int. Not {}".format(type(binning)))
        if not isinstance(binning_z, int):
            raise TypeError(
                "binning_z should be an int. Not {}".format(type(binning_z))
            )
        if not isinstance(proj_subsampling, int):
            raise TypeError(
                "proj_subsampling should be an int. Not {}".format(
                    type(proj_subsampling)
                )
            )
        return {
            "hdf5_entry": self.entry,
            "location": os.path.basename(self.master_file),
            "binning": binning,
            "binning_z": binning_z,
            "projections_subsampling": proj_subsampling,
        }

    @docstring(TomwerScanBase)
    def to_nabu_dataset_analyser(self):
        from nabu.resources.dataset_analyzer import HDF5DatasetAnalyzer

        return HDF5DatasetAnalyzer(
            location=self.master_file, extra_options={"hdf5_entry": self.entry}
        )

    @docstring(TomwerScanBase)
    def scan_dir_name(self) -> Optional[str]:
        """for 'this/is/my/file.h5' returns 'my'"""
        if self.master_file is not None:
            return os.path.dirname(self.master_file).split(os.sep)[-1]
        else:
            return None

    @docstring(TomwerScanBase)
    def scan_basename(self):
        if self.master_file is not None:
            try:
                return os.path.dirname(self.master_file)
            except Exception:
                return None
        else:
            return None

    @docstring(TomwerScanBase)
    def scan_parent_dir_basename(self):
        if self.master_file is not None:
            try:
                return os.path.dirname(os.path.dirname(self.master_file))
            except Exception:
                return None
        else:
            return None
