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


import numpy
import logging
import typing
import json
import io
import os
from glob import glob
from silx.io.url import DataUrl
from tomwer.core.utils.locker import FileLockerManager, FileLockerContext
from tomwer.core.utils.ftseriesutils import orderFileByLastLastModification
from tomoscan.io import HDF5File
from processview.core.dataset import Dataset
from typing import Optional

logger = logging.getLogger(__name__)


class TomwerScanBase(Dataset):
    """
    Simple interface to extend the tomoscan.TomwerScanBase with
    specific functions
    """

    _DICT_DARK_REF_KEYS = "dark_ref_params"

    _DICT_PYHST2_KEYS = "pyhst2_params"

    _DICT_LAMINO_RP_KEY = "lamino_params"

    _DICT_NABU_RP_KEY = "nabu_params"

    _DICT_AXIS_KEYS = "axis_params"

    _DICT_SA_AXIS_KEYS = "sa_axis_params"

    _DICT_SA_DELTA_BETA_KEYS = "sa_delta_beta_params"

    _DICT_PROCESS_INDEX_KEY = "next_process_index"

    VALID_RECONS_EXTENSION = ".edf", ".npy", ".npz", ".hdf5", ".tiff", ".jp2"

    def __init__(self, overwrite_proc_file=False):
        self._reconstructions = []

        self._nabu_params = None
        """nabu reconstruction parameters"""
        self._ftseries_params = None
        """pyhst reconstruction parameters"""
        self._lamino_params = None
        """Set of reconstructions parameters for laminography"""
        self._axis_params = None
        """Axis parameters"""
        self._saaxis_params = None
        """Information relative to saaxis"""
        self._sa_delta_beta_params = None
        """Information regarding sa_delta_beta_params"""
        self._dark_ref_params = None
        """Information regarding dark - ref reconstruction"""
        self._process_file = None
        """file storing processes applied on the scan, with their configuration
        and result"""
        self._cache_proj_urls = None
        """cache for the projection urls"""
        self._cache_radio_axis = {}
        """cache for the radio axis. Key is tuple (mode, nearest), value is
        (url1, url2)"""
        self._normed_darks = None
        """darks normed. Dict: key is the index in the sequence and value is
        the mean or median dark"""
        self._normed_flats = None
        """flats normed. Dict: key is the index in the sequence and value is
        the mean or median dark"""
        self._notify_ffc_rsc_missing = True
        """Should we notify the user if ffc fails because cannot find dark or
        flat. Used to avoid several warnings. Only display one"""
        self._latest_reconstructions = []
        """list of url related to latest reconstruction from nabu or pyhst"""
        self._latest_vol_reconstructions = []

    def _init_index_process_file(self, overwrite_proc_file=False):
        if (
            not overwrite_proc_file
            and self.process_file is not None
            and os.path.exists(self.process_file)
        ):
            with HDF5File(self.process_file, mode="r", swmr=True) as h5s:
                self._process_index = len(h5s.items())
        else:
            self._process_index = 0

    def clear_caches(self):
        self._cache_proj_urls = None
        self._notify_ffc_rsc_missing = True

    @staticmethod
    def get_process_file_name(scan):
        raise NotImplementedError("Base class")

    @property
    def normed_darks(self):
        return self._normed_darks

    def set_normed_darks(self, darks):
        self._normed_darks = darks

    @property
    def normed_flats(self):
        return self._normed_flats

    def set_normed_flats(self, flats):
        self._normed_flats = flats

    def _flat_field_correction(
        self,
        data,
        index_proj: typing.Union[int, None],
        dark,
        flat1,
        flat2,
        index_flat1: int,
        index_flat2: int,
    ):
        """
        compute flat field correction for a provided data from is index
        one dark and two flats (require also indexes)
        """
        assert type(data) is numpy.ndarray
        can_process = True

        if dark is None:
            if self._notify_ffc_rsc_missing:
                logger.error("cannot make flat field correction, dark not found")
            can_process = False

        if dark is not None and dark.ndim != 2:
            logger.error(
                "cannot make flat field correction, dark should be of " "dimension 2"
            )
            can_process = False

        if flat1 is None:
            if self._notify_ffc_rsc_missing:
                logger.error("cannot make flat field correction, flat not found")
            can_process = False
        else:
            if flat1.ndim != 2:
                logger.error(
                    "cannot make flat field correction, flat should be of "
                    "dimension 2"
                )
                can_process = False
            if flat2 is not None and flat1.shape != flat2.shape:
                logger.error("the tow flats provided have different shapes.")
                can_process = False

        if dark is not None and flat1 is not None and dark.shape != flat1.shape:
            logger.error("Given dark and flat have incoherent dimension")
            can_process = False

        if dark is not None and data.shape != dark.shape:
            logger.error(
                "Image has invalid shape. Cannot apply flat field" "correction it"
            )
            can_process = False

        if can_process is False:
            self._notify_ffc_rsc_missing = False
            return data

        if flat2 is None:
            flat_value = flat1
        else:
            # compute weight and clip it if necessary
            if index_proj is None:
                w = 0.5
            else:
                w = (index_proj - index_flat1) / (index_flat2 - index_flat1)
                w = min(1, w)
                w = max(0, w)
            flat_value = flat1 * w + flat2 * (1 - w)

        div = flat_value - dark
        div[div == 0] = 1
        return (data - dark) / div

    def acquire_process_file_lock(self):
        """create a FileLocker context manager to insure safe write to the
        process file"""
        if self.process_file is None:
            raise ValueError("No processing file defined")
        file_locker = FileLockerManager().get_locker(file_=self.process_file)
        return FileLockerContext(file_locker)

    @property
    def reconstructions(self):
        """list of reconstruction files"""
        return self._reconstructions

    @reconstructions.setter
    def reconstructions(self, reconstructions):
        self._reconstructions = reconstructions

    @property
    def ftseries_recons_params(self):
        return self._ftseries_params

    @ftseries_recons_params.setter
    def ftseries_recons_params(self, recons_params):
        self._ftseries_params = recons_params

    @property
    def nabu_recons_params(self):
        return self._nabu_params

    @nabu_recons_params.setter
    def nabu_recons_params(self, recons_params):
        self._nabu_params = recons_params

    @property
    def lamino_recons_params(self):
        return self._lamino_params

    @lamino_recons_params.setter
    def lamino_recons_params(self, recons_params):
        self._lamino_params = recons_params

    @property
    def axis_params(self):
        return self._axis_params

    @axis_params.setter
    def axis_params(self, parameters):
        self._axis_params = parameters

    @property
    def saaxis_params(self):
        return self._saaxis_params

    @saaxis_params.setter
    def saaxis_params(self, saaxis_params):
        self._saaxis_params = saaxis_params

    @property
    def sa_delta_beta_params(self):
        return self._sa_delta_beta_params

    @sa_delta_beta_params.setter
    def sa_delta_beta_params(self, sa_delta_beta_params):
        self._sa_delta_beta_params = sa_delta_beta_params

    # TODO: change name. Should be generalized to return Dataurl
    def getReconstructedFilesFromParFile(self, with_index):
        raise NotImplementedError("Base class")

    def projections_with_angle(self):
        raise NotImplementedError("Base class")

    def scan_dir_name(self) -> Optional[str]:
        """return name of the directory containing the acquisition"""
        raise NotImplementedError("Base class")

    def scan_basename(self) -> Optional[str]:
        """return basename of the directory containing the acquisition"""
        raise NotImplementedError("Base class")

    def scan_parent_dir_basename(self) -> Optional[str]:
        """return parent basename of the directory containing the acquisition"""
        raise NotImplementedError("Base class")

    def pop_process_index(self) -> int:
        """Return and lock the next free process index"""
        process_index = self._process_index
        self._process_index += 1
        return process_index

    def getRadiosForAxisCalc(
        self, mode, nearest: bool = True, use_cache: bool = True
    ) -> tuple:
        """
        Return the radios for axis calculation and the requested mode.

        :param: angles we want to use for COR calculation. Can be 0-180,
                 90-180 or manual. If manual will return the 'most' appropriate
        :type: CorAngleMode
        :param nearest: if True then, pick the closest angle from the requested
                        one. If False, return (None, None) if the the angles
                        does not exists.
        :type: bool
        :return: couple of `opposite` radios that can be used for axis
                 calculation.
        :rtype: tuple(AxisResource, AxisResource)
        """
        if not use_cache:
            del self._cache_radio_axis[(mode, nearest)]

        def compute():
            from ..process.reconstruction.axis.params import (
                AxisResource,
            )  # avoid cyclic import
            from ..process.reconstruction.axis.anglemode import CorAngleMode

            _mode = CorAngleMode.from_value(mode)
            if self.path is None:
                return None, None

            radios_with_angle = self.projections_with_angle()

            if _mode is CorAngleMode.use_0_180:
                couples = ((0, 180),)
            elif _mode is CorAngleMode.use_90_270:
                couples = ((90, 270),)
            else:
                couples = ((0, 180), (90, 270))

            for couple in couples:
                if (
                    couple[0] in radios_with_angle.keys()
                    and couple[1] in radios_with_angle.keys()
                ):
                    radio_0 = AxisResource(radios_with_angle[couple[0]])
                    radio_1 = AxisResource(radios_with_angle[couple[1]])
                    return radio_0, radio_1

            def find_nearest(angles, angle):
                if len(angles) == 0:
                    return None
                angles = numpy.asarray(angles)
                dist = numpy.abs(angles - angle)
                idx = dist.argmin()
                if isinstance(idx, numpy.ndarray):
                    idx = idx[0]
                return angles[idx]

            if nearest is True:
                angles = []
                # filter str value (0(1)...)
                [
                    angles.append(value)
                    for value in radios_with_angle.keys()
                    if numpy.issubdtype(type(value), numpy.number)
                ]
                nearest_c1 = find_nearest(angles=angles, angle=couples[0][0])
                nearest_c2 = find_nearest(angles=angles, angle=couples[0][1])
                if nearest_c1 is not None and nearest_c2 is not None:
                    radio_0 = AxisResource(radios_with_angle[nearest_c1])
                    radio_1 = AxisResource(radios_with_angle[nearest_c2])
                    return radio_0, radio_1
            return None, None

        if (mode, nearest) not in self._cache_radio_axis:
            radio_0, radio_1 = compute()
            self._cache_radio_axis[(mode, nearest)] = (radio_0, radio_1)
        return self._cache_radio_axis[(mode, nearest)]

    def data_flat_field_correction(self, data, index=None):
        """Apply flat field correction on the given data

        :param numpy.ndarray data: the data to apply correction on
        :param Uion[int, None] index: index of the data in the acquisition
                                      sequence
        :return: corrected data
        :rtype: numpy.ndarray
        """
        raise NotImplementedError("Base class")

    def getReconsParamList(self):
        """

        :return: reconstruction parameters
        :rtype: ReconsParamList
        """
        raise NotImplementedError("Base class")

    @property
    def process_file(self) -> str:
        """

        :return: file used to store the processes launch by tomwer
        """
        return self._process_file

    @property
    def process_file_url(self) -> DataUrl:
        """

        :return: DataUrl of the process file
        """
        return DataUrl(
            file_path=self._process_file, data_path=self.entry or "entry", scheme="silx"
        )

    def to_dict(self):
        res = {}
        # ftseries reconstruction parameters
        if self.ftseries_recons_params:
            res[self._DICT_PYHST2_KEYS] = self.ftseries_recons_params.to_dict()
        else:
            res[self._DICT_PYHST2_KEYS] = None
        # nabu reconstruction parameters
        if self._nabu_params:
            res[self._DICT_NABU_RP_KEY] = self.nabu_recons_params.to_dict()
        else:
            res[self._DICT_NABU_RP_KEY] = None
        # axis reconstruction parameters
        if self.axis_params is None:
            res[self._DICT_AXIS_KEYS] = None
        else:
            res[self._DICT_AXIS_KEYS] = self.axis_params.to_dict()
        # saaxis reconstruction parameters
        if self.saaxis_params is None:
            res[self._DICT_SA_AXIS_KEYS] = None
        else:
            res[self._DICT_SA_AXIS_KEYS] = self.saaxis_params.to_dict()
        # sa delta-beta reconstruction parameters
        if self._sa_delta_beta_params is None:
            res[self._DICT_SA_DELTA_BETA_KEYS] = None
        else:
            res[self._DICT_SA_DELTA_BETA_KEYS] = self.sa_delta_beta_params.to_dict()
        # dark ref
        if self._dark_ref_params is None:
            res[self._DICT_DARK_REF_KEYS] = None
        else:
            res[self._DICT_DARK_REF_KEYS] = self._dark_ref_params.to_dict()
        # process index
        res[self._DICT_PROCESS_INDEX_KEY] = self._process_index

        # lamino reconstruction parameters
        res[self._DICT_LAMINO_RP_KEY] = self.lamino_recons_params
        return res

    def load_from_dict(self, desc):
        from tomwer.core.process.reconstruction.ftseries.params import (
            ReconsParams,
        )  # avoid cyclic import
        from tomwer.core.process.reconstruction.axis.params import (
            AxisRP,
        )  # avoid cyclic import

        if isinstance(desc, io.TextIOWrapper):
            data = json.load(desc)
        else:
            data = desc
        if not (self.DICT_PATH_KEY in data and data[self.DICT_TYPE_KEY] == self._TYPE):
            raise ValueError("Description is not an EDFScan json description")

        assert self.DICT_PATH_KEY in data
        assert self._DICT_LAMINO_RP_KEY in data
        # load pyhst2 parameters
        recons_param_data = data[self._DICT_PYHST2_KEYS]
        if recons_param_data is not None:
            self.ftseries_recons_params = ReconsParams.from_dict(recons_param_data)
        self.lamino_recons_params = data[self._DICT_LAMINO_RP_KEY]
        # load axis reconstruction parameters
        axis_params = data.get(self._DICT_AXIS_KEYS, None)
        if axis_params is not None:
            self.axis_params = AxisRP.from_dict(axis_params)
        # load nabu reconstruction parameters
        if self._DICT_NABU_RP_KEY in data:
            self._nabu_params = data[self._DICT_NABU_RP_KEY]
        # load dark-ref parameters
        dark_ref_params = data.get(self._DICT_DARK_REF_KEYS, None)
        if dark_ref_params is not None:
            from tomwer.core.process.reconstruction.darkref.params import DKRFRP

            self._dark_ref_params = DKRFRP.from_dict(dark_ref_params)
        # load saaxis parameters
        saaxis_params = data.get(self._DICT_SA_AXIS_KEYS, None)
        if saaxis_params is not None:
            from tomwer.core.process.reconstruction.saaxis.params import SAAxisParams

            self._saaxis_params = SAAxisParams.from_dict(saaxis_params)
        # load sa delta beta parameters
        sa_delta_beta_params = data.get(self._DICT_SA_DELTA_BETA_KEYS, None)
        if sa_delta_beta_params is not None:
            from tomwer.core.process.reconstruction.sadeltabeta.params import (
                SADeltaBetaParams,
            )

            self._sa_delta_beta_params = SADeltaBetaParams.from_dict(
                sa_delta_beta_params
            )

        self._process_index = data[self._DICT_PROCESS_INDEX_KEY]

    def equal(self, other):
        """

        :param :class:`.ScanBase` other: instance to compare with
        :return: True if instance are equivalent
        :note: we cannot use the __eq__ function because this object need to be
               pickable
        """
        return (
            isinstance(other, self.__class__)
            or isinstance(self, other.__class__)
            and self.type == other.type
            and self.ftseries_recons_params == other.ftseries_recons_params
            and self.lamino_recons_params == other.lamino_recons_params
            and self.nabu_recons_params == other.nabu_recons_params
            and self.path == other.path
        )

    def get_sinogram(self, line, progress=None):
        """
        extract the sinogram from projections

        :param line: which sinogram we want
        :type: int
        :return: sinogram from the radio lines
        :rtype: numpy.array
        """
        raise NotImplementedError("Base class")

    def __str__(self):
        raise NotImplementedError("Base class")

    @staticmethod
    def get_pyhst_recons_file(scanID):
        """Return the .par file used for the current reconstruction if any.
        Otherwise return None"""
        if scanID == "":
            return None

        if scanID is None:
            raise RuntimeError("No current acquisition to validate")
        assert type(scanID) is str
        assert os.path.isdir(scanID)
        folderID = os.path.basename(scanID)
        # look for fasttomo files ending by slice.par
        parFiles = glob(os.path.join(scanID + folderID) + "*_slice.par")
        if len(parFiles) > 0:
            return orderFileByLastLastModification(scanID, parFiles)[-1]
        else:
            return None

    def _deduce_transfert_scan(self, output_dir):
        """
        Create the scan that will be generated if this scan is
        copy to the output_dir

        :param str output_dir:
        """
        raise NotImplementedError("Base class")

    def get_proj_angle_url(self, use_cache: bool = True):
        """
        retrieve the url for each projections (including the alignement /
        return one) and associate to each (if possible) the angle.
        Alignment angle are set as angle (1) to specify that this is an
        alignment one.
        :param bool use_cache:
        :return: dictionary with angle (str or int) as key and url as value
        :rtype: dict
        """
        raise NotImplementedError("Base class")

    def get_reconstructions_urls(self):
        """

        :return: list of urls that contains reconstruction from nabu or pyhst
        :rtype: list
        """

        def containsDigits(input):
            return any(char.isdigit() for char in input)

        if (self.path is None) or (not os.path.isdir(self.path)):
            return []
        results = []
        # parse .npy, .npz and .edf, .vol, *.hdf5 files
        folderBasename = os.path.basename(self.path)
        pyhst_files = TomwerScanBase.get_pyhst_recons_file(self.path)
        if pyhst_files is not None:
            results.extend(
                TomwerScanBase.getReconstructedFilesFromParFile(
                    pyhst_files, with_index=False
                )
            )

        def get_recons_url_from_folder(folder, check_url=False):
            """
            retrieve all the url from a folder.

            :param str folder:
            :param bool check_url: if True before adding an url try to open it
                                   and insure is valid
            :return:
            """
            res = []
            for f in os.listdir(folder):
                full_file_path = os.path.join(folder, f)
                if f.startswith(folderBasename) and "slice_" in f:
                    if os.path.isdir(full_file_path):
                        res.extend(get_recons_url_from_folder(full_file_path))
                    elif f.endswith(TomwerScanBase.VALID_RECONS_EXTENSION):
                        local_str = f
                        for extension in TomwerScanBase.VALID_RECONS_EXTENSION:
                            if local_str.endswith(extension):
                                local_str = local_str.rsplit(extension, 1)[0]
                                break
                        if "slice_pag_" in local_str:
                            indexStr = local_str.split("slice_pag_")[-1].split("_")[0]
                        else:
                            indexStr = local_str.split("slice_")[-1].split("_")[0]
                        if containsDigits(indexStr):
                            gfile = os.path.join(folder, f)
                            assert os.path.isfile(gfile)
                            if gfile.lower().endswith(".edf"):
                                url = DataUrl(file_path=full_file_path, scheme="fabio")
                                res.append(url)

                        if f.lower().endswith((".npy", "npz")):
                            url = DataUrl(file_path=full_file_path, scheme="numpy")
                            res.append(url)
                        elif f.lower().endswith((".jp2", ".jp2", ".tiff")):
                            url = DataUrl(file_path=full_file_path, scheme="tomwer")
                            res.append(url)
                        elif f.lower().endswith(
                            (".h5", ".hdf5", ".nx", ".nexus", ".nx5", ".hdf")
                        ):
                            entry = getattr(self, "entry", "entry")
                            url = DataUrl(
                                file_path=full_file_path,
                                scheme="silx",
                                data_path="/".join(
                                    (entry, "reconstruction", "results", "data")
                                ),
                            )
                            if check_url is True:
                                try:
                                    with HDF5File(
                                        full_file_path, "r", swmr=True
                                    ) as h5f:
                                        if entry not in h5f:
                                            logger.info(
                                                "{} does not exists".format(url)
                                            )
                                            continue
                                except Exception:
                                    logger.info("unable to check {}".format(url))
                                else:
                                    logger.info("{} checked".format(url))
                                    res.append(url)
                            else:
                                res.append(url)
                if f.endswith(".vol"):
                    url = DataUrl(file_path=os.path.join(self.path, f), scheme="tomwer")
                    res.append(url)
            return res

        if os.path.isdir(self.path):
            results.extend(get_recons_url_from_folder(self.path))

        return results

    @property
    def latest_reconstructions(self):
        """List of latest reconstructions"""
        return self._latest_reconstructions

    @property
    def latest_vol_reconstructions(self):
        """List of latest reconstructions"""
        return self._latest_vol_reconstructions

    def clear_latest_reconstructions(self):
        self._latest_reconstructions = []

    def set_latest_reconstructions(self, urls: typing.Iterable):
        self._latest_reconstructions = urls

    def add_latest_reconstructions(self, urls: typing.Iterable):
        self._latest_reconstructions.extend(urls)

    def clear_latest_vol_reconstructions(self):
        self._latest_vol_reconstructions = []

    def set_latest_vol_reconstructions(self, urls):
        self._latest_vol_reconstructions = urls

    def add_latest_vol_reconstructions(self, urls):
        self._latest_vol_reconstructions.extend(urls)

    def _update_latest_recons_urls(self, old_path, new_path):
        new_urls = []
        for recons_url in self._latest_reconstructions:
            new_urls.append(
                DataUrl(
                    file_path=recons_url.path().replace(old_path, new_path, 1),
                    data_path=recons_url.data_path(),
                    data_slice=recons_url.data_slice(),
                    scheme=recons_url.scheme(),
                )
            )
        self._latest_reconstructions = new_urls

    def get_url_proj_index(self, url):
        """Return the index in the acquisition from the url"""

        def invert_dict(ddict):
            res = {}
            if ddict is not None:
                for key, value in ddict.items():
                    assert isinstance(value, DataUrl)
                    res[value.path()] = key
            return res

        proj_inv_url_to_index = invert_dict(self.projections)
        alig_inv_url_to_index = invert_dict(self.alignment_projections)
        if url.path() in proj_inv_url_to_index:
            return proj_inv_url_to_index[url.path()]
        elif url.path() in alig_inv_url_to_index:
            return alig_inv_url_to_index[url.path()]
        else:
            return None

    def set_process_index_frm_tomwer_process_file(self):
        """
        Set the process_index to the last index find in the tomwer_process_file
        + 1
        """
        from tomwer.core.process.task import Task

        if os.path.exists(self.process_file):
            with HDF5File(self.process_file, mode="r") as h5s:
                if not hasattr(self, "entry"):
                    entry = "entry"
                else:
                    entry = self.entry
                if entry in h5s:
                    node = h5s[entry]
                    pn = Task._get_process_nodes(
                        root_node=node, process=None, version=None
                    )
                    indexes = pn.values()
                    if len(indexes) > 0:
                        self._process_index = max(indexes) + 1
                        logger.debug(
                            "set process_index from tomwer process file"
                            "to {}".format(self._process_index)
                        )

    def get_nabu_dataset_info(self, binning=1, binning_z=1, proj_subsampling=1):
        """

        :return: nabu dataset descriptor
        :rtype: dict
        """
        raise NotImplementedError("Base class")

    def to_nabu_dataset_analyser(self):
        """Return the equivalent DatasetAnalyzer for nabu"""
        raise NotImplementedError("Base class")


class _TomwerBaseDock(object):
    """
    Internal class to make difference between a simple TomoBase output and
    an output for a different processing (like scanvalidator.UpdateReconsParam)
    """

    def __init__(self, tomo_instance):
        self.__instance = tomo_instance

    @property
    def instance(self):
        return self.__instance
