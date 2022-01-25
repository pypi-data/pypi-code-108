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
"""
This module provides global definitions and functions to manage dark and flat fields
especially for tomo experiments and workflows
"""

__authors__ = ["C. Nemoz", "H.Payno"]
__license__ = "MIT"
__date__ = "06/09/2017"

import os
import re
from glob import glob
import fabio
import numpy
from queue import Queue
from tomwer.utils import docstring
from silx.io.utils import get_data
from tomwer.core import settings
from tomwer.core import utils
from tomwer.core.process.task import Task
from processview.core.superviseprocess import SuperviseProcess
from tomwer.core.utils import getDARK_N
import logging
from tomwer.core.scan.scanbase import TomwerScanBase
from tomwer.core.scan.edfscan import EDFTomoScan
from tomwer.core.scan.hdf5scan import HDF5TomoScan
from . import params as dkrf_reconsparams
from tomwer.core.process.reconstruction.ftseries.params import ReconsParams
from tomwer.core.scan.scanfactory import ScanFactory
from tomoscan.esrf.utils import get_compacted_dataslices
from processview.core.manager import ProcessManager
from tomoscan.io import HDF5File
from processview.core.manager import DatasetState
import tomwer.version
from silx.io.utils import h5py_read_dataset
from silx.io.url import DataUrl
import typing

logger = logging.getLogger(__name__)

try:
    from tomwer.synctools.rsyncmanager import RSyncManager
except ImportError:
    logger.warning("rsyncmanager not available")
    has_rsync = True
else:
    has_rsync = False


class DarkRefs(
    Task, SuperviseProcess, Queue, input_names=("data",), output_names=("data",)
):
    """Compute median/mean dark and ref from originals (dark and ref files)"""

    WHAT_REF = "refs"
    WHAT_DARK = "dark"

    VALID_WHAT = (WHAT_REF, WHAT_DARK)
    """Tuple of valid option for What"""

    info_suffix = ".info"

    TOMO_N = "TOMO_N"

    def __init__(self, process_id=None, varinfo=None, inputs=None, label=None):
        """

        :param str file_ext:
        :param reconsparams: reconstruction parameters
        :type reconsparams: Union[None, ReconsParams, DKRFRP]
        """
        Task.__init__(self, varinfo=varinfo, inputs=inputs, label=label)
        SuperviseProcess.__init__(self, process_id=process_id)
        Queue.__init__(self)

        if inputs is None:
            inputs = {}
        if "recons_params" in inputs or "reconsparams" in inputs:
            raise ValueError(
                "wrong key: recons_params / reconsparams use dark_ref_params instead"
            )
        self._recons_params = inputs.get("dark_ref_params", None)
        if self._recons_params is None:
            self._recons_params = dkrf_reconsparams.DKRFRP()
        elif isinstance(self._recons_params, dict):
            self._recons_params = dkrf_reconsparams.DKRFRP.from_dict(
                self._recons_params
            )
        if not isinstance(self._recons_params, dkrf_reconsparams.DKRFRP):
            raise TypeError(
                f"'reconsparams' should be an instance of {dkrf_reconsparams.DKRFRP} or {dict}. Not {type(self._recons_params)}"
            )
        self._file_ext = inputs.get("file_ext", ".edf")
        if not type(self._file_ext) is str:
            raise TypeError("'file_ext' is expected to be a string")

        self._forceSync = inputs.get("force_sync", False)
        self.__new_hdf5_entry_created = False
        "used to know if the process has generated a new entry or not"

    @property
    def recons_params(self):
        return self._recons_params

    def set_recons_params(self, recons_params):
        if isinstance(recons_params, ReconsParams):
            self._recons_params = recons_params.dkrf
        elif isinstance(recons_params, dkrf_reconsparams.DKRFRP):
            self._recons_params = recons_params
        else:
            raise TypeError(
                "recons_params should be an instance of " "ReconsParams or DKRFRP"
            )

    def setPatternRecons(self, pattern):
        self._patternReconsFile = pattern

    def _instanciateReconsParams(self):
        return ReconsParams(empty=True)

    def setForceSync(self, b):
        self._forceSync = True

    @staticmethod
    def getRefHSTFiles(directory, prefix, file_ext=".edf"):
        """

        :return: the list of existing refs files in the directory according to
                 the file pattern.
        """
        assert isinstance(directory, str)
        res = []
        if os.path.isdir(directory) is False:
            logger.error(
                directory + " is not a directory. Cannot extract " "RefHST files"
            )
            return res

        for file in os.listdir(directory):
            if file.startswith(prefix) and file.endswith(file_ext):
                res.append(os.path.join(directory, file))
                assert os.path.isfile(res[-1])
        return res

    @staticmethod
    def getDarkHSTFiles(directory, prefix, file_ext=".edf"):
        """

        :return: the list of existing refs files in the directory according to
                 the file pattern.
        """
        res = []
        if os.path.isdir(directory) is False:
            logger.error(
                directory + " is not a directory. Cannot extract " "DarkHST files"
            )
            return res
        for file in os.listdir(directory):
            _prefix = prefix
            if prefix.endswith(file_ext):
                _prefix = prefix.rstrip(file_ext)
            if file.startswith(_prefix) and file.endswith(file_ext):
                _file = file.lstrip(_prefix).rstrip(file_ext)
                if _file == "" or _file.isnumeric() is True:
                    res.append(os.path.join(directory, file))
                    assert os.path.isfile(res[-1])
        return res

    @staticmethod
    def getDarkPatternTooltip():
        return (
            "define the pattern to find, using the python `re` library.\n"
            "For example: \n"
            "   - `.*conti_dark.*` to filter files containing `conti_dark` sentence\n"
            "   - `darkend[0-9]{3,4}` to filter files named `darkend` followed by three or four digit characters (and having the .edf extension)"
        )

    @staticmethod
    def getRefPatternTooltip():
        return (
            "define the pattern to find, using the python `re` library.\n"
            "For example: \n"
            "   - `.*conti_ref.*` for files containing `conti_dark` sentence\n"
            "   - `ref*.*[0-9]{3,4}_[0-9]{3,4}` to filter files named `ref` followed by any character and ending by X_Y where X and Y are groups of three or four digit characters."
        )

    @staticmethod
    def properties_help():
        return """
        - refs: 'None', 'Median', 'Average', 'First', 'Last' \n
        - dark: 'None', 'Median', 'Average', 'First', 'Last' \n
        """

    def set_configuration(self, properties):
        # No properties stored for now
        if "dark" in properties:
            self._recons_params.dark_calc_method = properties["dark"]
        if "refs" in properties:
            self._recons_params.ref_calc_method = properties["refs"]
        if "_rpSetting" in properties:
            self._recons_params.load_from_dict(properties["_rpSetting"])
        else:
            self._recons_params.load_from_dict(properties)

    @staticmethod
    def get_darks_frm_process_file(
        process_file, entry=None, as_url: bool = False
    ) -> typing.Union[None, dict]:
        """

        :param str process_file: path to the process file
        :param entry: entry to read in the process file if more than one
        :param bool as_url: if true then an url will be used instead of a
                            numpy.array
        :return: dictionary with index in the sequence as key and numpy array
                 as value (or url if as_url set to True)
        """
        if entry is None:
            with HDF5File(process_file, "r", swmr=True) as h5f:
                entries = DarkRefs._get_process_nodes(root_node=h5f, process=DarkRefs)
                if len(entries) == 0:
                    logger.info("unable to find a DarkRef process in %s" % process_file)
                    return None
                elif len(entries) > 1:
                    raise ValueError("several entry found, entry should be " "specify")
                else:
                    entry = list(entries.keys())[0]
                    logger.info("take %s as default entry" % entry)

        with HDF5File(process_file, "r", swmr=True) as h5f:
            if entry not in h5f.keys():
                logger.info("no dark found for {}".format(entry))
                return {}
            dark_nodes = DarkRefs._get_process_nodes(
                root_node=h5f[entry], process=DarkRefs
            )
            index_to_path = {}
            for key, index in dark_nodes.items():
                index_to_path[index] = key

            if len(dark_nodes) == 0:
                return {}
            # take the last processed dark ref
            last_process_index = sorted(list(dark_nodes.values()))[-1]
            last_process_dark = index_to_path[last_process_index]
            if (len(index_to_path)) > 1:
                logger.debug(
                    "several processing found for dark-ref,"
                    "take the last one: %s" % last_process_dark
                )

            res = {}
            if "results" in h5f[last_process_dark].keys():
                results_node = h5f[last_process_dark]["results"]
                if "darks" in results_node.keys():
                    darks = results_node["darks"]
                    for index in darks:
                        if as_url is True:
                            res[int(index)] = DataUrl(
                                file_path=process_file,
                                data_path="/".join((darks.name, index)),
                                scheme="silx",
                            )
                        else:
                            res[int(index)] = h5py_read_dataset(darks[index])
            return res

    @staticmethod
    def get_flats_frm_process_file(
        process_file, entry=None, as_url: bool = False
    ) -> typing.Union[None, dict]:
        """

        :param process_file:
        :param entry: entry to read in the process file if more than one
        :param bool as_url: if true then an url will be used instead of a
                            numpy.array
        :return:
        """
        if entry is None:
            with HDF5File(process_file, "r", swmr=True) as h5f:
                entries = DarkRefs._get_process_nodes(root_node=h5f, process=DarkRefs)
                if len(entries) == 0:
                    logger.info("unable to find a DarkRef process in %s" % process_file)
                    return None
                elif len(entries) > 1:
                    raise ValueError("several entry found, entry should be " "specify")
                else:
                    entry = list(entries.keys())[0]
                    logger.info("take %s as default entry" % entry)

        with HDF5File(process_file, "r", swmr=True) as h5f:
            if entry not in h5f.keys():
                logger.info("no flats found for {}".format(entry))
                return {}
            dkref_nodes = DarkRefs._get_process_nodes(
                root_node=h5f[entry], process=DarkRefs
            )
            index_to_path = {}
            for key, index in dkref_nodes.items():
                index_to_path[index] = key

            if len(dkref_nodes) == 0:
                return {}
            # take the last processed dark ref
            last_process_index = sorted(dkref_nodes.values())[-1]
            last_process_dkrf = index_to_path[last_process_index]
            if (len(index_to_path)) > 1:
                logger.debug(
                    "several processing found for dark-ref,"
                    "take the last one: %s" % last_process_dkrf
                )

            res = {}
            if "results" in h5f[last_process_dkrf].keys():
                results_node = h5f[last_process_dkrf]["results"]
                if "flats" in results_node.keys():
                    flats = results_node["flats"]
                    for index in flats:
                        if as_url is True:
                            res[int(index)] = DataUrl(
                                file_path=process_file,
                                data_path="/".join((flats.name, index)),
                                scheme="silx",
                            )
                        else:
                            res[int(index)] = h5py_read_dataset(flats[index])
            return res

    def run(self):
        scan = self.inputs.data
        if scan is None:
            self.outputs.data = None
            return

        if type(scan) is str:
            assert os.path.exists(scan)
            scan = ScanFactory.create_scan_object(scan_path=scan)
        elif isinstance(scan, TomwerScanBase):
            pass
        elif isinstance(scan, dict):
            scan = ScanFactory.create_scan_object_frm_dict(scan)
        else:
            raise TypeError(
                "scan should be an instance of TomoBase or path to " "scan dircetory"
            )
        # copy the current parameters to the scan ftseries_recons_params
        if scan.ftseries_recons_params is None:
            scan.ftseries_recons_params = self._instanciateReconsParams()
        assert isinstance(self._recons_params, dkrf_reconsparams.DKRFRP)
        assert isinstance(scan.ftseries_recons_params, ReconsParams)
        assert self._recons_params is not None

        scan.ftseries_recons_params.copy(self._recons_params)

        ProcessManager().notify_dataset_state(
            dataset=scan,
            process=self,
            state=DatasetState.ON_GOING,
        )
        logger.processStarted("start dark and ref for {}" "".format(str(scan)))
        if (
            settings.isOnLbsram(scan)
            and utils.isLowOnMemory(settings.get_lbsram_path()) is True
        ):
            mess = (
                "low memory, do compute dark and flat field mean/median "
                "for %s" % scan.path
            )
            logger.processSkipped(mess)
            ProcessManager().notify_dataset_state(
                dataset=scan,
                process=self,
                state=DatasetState.SKIPPED,
                details=mess,
            )
            self.outputs.data = None
            return

        if not (scan and os.path.exists(scan.path)):
            mess = "folder {} is not existing".format(scan.path)
            logger.warning(mess)
            ProcessManager().notify_dataset_state(
                dataset=scan, process=self, state=DatasetState.FAILED, details=mess
            )

            self.outputs.data = None
            return
        whats = (DarkRefs.WHAT_REF, DarkRefs.WHAT_DARK)
        modes = (
            self.recons_params.ref_calc_method,
            self.recons_params.dark_calc_method,
        )

        for what, mode in zip(whats, modes):
            self._originalsDark = []
            self._originalsRef = []
            logger.debug(
                "compute {what} using mode {mode} for {scan}"
                "".format(what=what, mode=mode, scan=str(scan))
            )
            self.compute(scan=scan, what=what, mode=mode)
        try:
            for what, mode in zip(whats, modes):
                self._originalsDark = []
                self._originalsRef = []
                self.compute(scan=scan, what=what, mode=mode)
        except Exception as e:
            info = "Fail computing dark and ref for {}. Reason is {}".format(
                str(scan), e
            )
            self.process.notify_to_state_to_managed(
                dataset=scan, state=DatasetState.SUCCEED, details=info
            )
            logger.processFailed(info)
            self.outputs.data = None
            return
        results = {}
        interpretations = {}
        if (
            self.recons_params.dark_calc_method is not dkrf_reconsparams.Method.none
            and scan.normed_darks is not None
        ):
            # cast darks and flats keys from int (index) to str
            o_darks = scan.normed_darks
            f_darks = {}
            for index, data in o_darks.items():
                f_darks[str(index)] = data
                interpretations["/".join(("darks", str(index)))] = "image"
            results["darks"] = f_darks
            # EDFTomoscan are already saved
            if not isinstance(scan, EDFTomoScan):
                scan.save_reduced_darks(f_darks)
        if (
            self.recons_params.ref_calc_method is not dkrf_reconsparams.Method.none
            and scan.normed_flats is not None
        ):
            results["flats"] = scan.normed_flats
            o_flats = scan.normed_flats
            f_flats = {}
            for index, data in o_flats.items():
                f_flats[str(index)] = data
                interpretations["/".join(("flats", str(index)))] = "image"
            results["flats"] = f_flats
            # EDFTomoscan are already saved
            if not isinstance(scan, EDFTomoScan):
                scan.save_reduced_flats(f_flats)

        if len(results) > 0:
            # if some processing to be registered
            if scan.process_file is not None and not (
                isinstance(scan, HDF5TomoScan) and not self.__new_hdf5_entry_created
            ):
                with scan.acquire_process_file_lock():
                    entry = "entry"
                    if hasattr(scan, "entry"):
                        entry = scan.entry
                    self.register_process(
                        process_file=scan.process_file,
                        entry=entry,
                        configuration=self.recons_params.to_dict(),
                        results=results,
                        interpretations=interpretations,
                        process_index=scan.pop_process_index(),
                        overwrite=True,
                    )
        logger.processSucceed("Dark and ref succeeded for {}" "".format(str(scan)))
        self.notify_to_state_to_managed(
            dataset=scan, state=DatasetState.SUCCEED, details=None
        )

        if self._return_dict:
            self.outputs.data = scan.to_dict()
        else:
            self.outputs.data = scan

    def compute(self, scan, what, mode):
        if isinstance(scan, EDFTomoScan):
            self.compute_edf(scan, what=what, mode=mode)
        elif isinstance(scan, HDF5TomoScan):
            self.compute_hdf5(scan, what=what, mode=mode)
        else:
            raise ValueError("scan type is not recognized ofr %s" % scan)

    def compute_hdf5(self, scan, what, mode):
        """Compute the requested what in the given mode for `directory`

        :param str directory: path of the scan
        :param what: what to compute (ref or dark)
        :param mode: how to compute it (median or average...)
        """

        def get_series(scan, what: str) -> list:
            """return a list of dictionary. on the dictionary we have indexes
            as key and url as value"""
            if what == "dark":
                raw_what = scan.darks
            else:
                raw_what = scan.flats
            if len(raw_what) == 0:
                return []
            else:
                series = []
                indexes = sorted(raw_what.keys())
                # a serie is defined by contiguous indexes
                current_serie = {indexes[0]: raw_what[indexes[0]]}
                current_index = indexes[0]
                for index in indexes[1:]:
                    if index == current_index + 1:
                        current_index = index
                    else:
                        series.append(current_serie)
                        current_serie = {}
                        current_index = index
                    current_serie[index] = raw_what[index]
                if len(current_serie) > 0:
                    series.append(current_serie)
                return series

        if mode is dkrf_reconsparams.Method.median:
            method_ = numpy.median
        elif mode is dkrf_reconsparams.Method.average:
            method_ = numpy.mean
        elif mode is dkrf_reconsparams.Method.none:
            return None
        elif mode is dkrf_reconsparams.Method.first:
            method_ = "raw"
        elif mode is dkrf_reconsparams.Method.last:
            method_ = "raw"
        else:
            raise ValueError(
                "Mode {mode} for {what} is not managed" "".format(mode=mode, what=what)
            )
        raw_series = get_series(scan, what)
        if len(raw_series) == 0:
            logger.warning("No %s found for %s" % (what, scan))
            return

        def load_data_serie(urls):
            if mode is dkrf_reconsparams.Method.first and len(urls) > 0:
                urls_keys = sorted(urls.keys())
                urls = {
                    urls_keys[0]: urls[urls_keys[0]],
                }
            if mode is dkrf_reconsparams.Method.last and len(urls) > 0:
                urls_keys = sorted(urls.keys())
                urls = {
                    urls_keys[-1]: urls[urls_keys[-1]],
                }

            cpt_slices = get_compacted_dataslices(urls)
            url_set = {}
            for url in cpt_slices.values():
                path = url.file_path(), url.data_path(), str(url.data_slice())
                url_set[path] = url

            n_elmts = 0
            for url in url_set.values():
                my_slice = url.data_slice()
                n_elmts += my_slice.stop - my_slice.start

            data = None
            start_z = 0
            for url in url_set.values():
                my_slice = url.data_slice()
                my_slice = slice(my_slice.start, my_slice.stop, 1)
                new_url = DataUrl(
                    file_path=url.file_path(),
                    data_path=url.data_path(),
                    data_slice=my_slice,
                    scheme="silx",
                )
                loaded_data = get_data(new_url)

                # init data if dim is not know
                if data is None:
                    data = numpy.empty(
                        shape=(
                            n_elmts,
                            scan.dim_2 or loaded_data.shape[-2],
                            scan.dim_1 or loaded_data.shape[-1],
                        )
                    )
                if loaded_data.ndim == 2:
                    data[start_z, :, :] = loaded_data
                    start_z += 1
                elif loaded_data.ndim == 3:
                    delta_z = my_slice.stop - my_slice.start
                    data[start_z:delta_z, :, :] = loaded_data
                    start_z += delta_z
                else:
                    raise ValueError("Dark and ref raw data should be 2D or 3D")

            return data

        res = {}
        # res: index: sequence when the serie was taken

        self.__new_hdf5_entry_created = False
        # flag to know if we could load all dark and flats from a previous
        # process file or if we add to create a new entry
        for serie_ in raw_series:
            serie_index = min(serie_)
            if what == "dark" and len(res) > 0:
                continue
            old_data = None
            has_p_file = os.path.exists(scan.process_file)
            if (
                has_p_file
                and what == DarkRefs.WHAT_DARK
                and not self.recons_params.overwrite_dark
            ):
                old_data = DarkRefs.get_darks_frm_process_file(
                    scan.process_file, entry=scan.entry
                )
            elif (
                has_p_file
                and what == DarkRefs.WHAT_REF
                and not self.recons_params.overwrite_ref
            ):
                old_data = DarkRefs.get_flats_frm_process_file(
                    scan.process_file, entry=scan.entry
                )
            if old_data is not None and serie_index in old_data:
                logger.info("load {} from existing data".format(what))
                res[serie_index] = old_data[serie_index]
                continue
            self.__new_hdf5_entry_created = True
            serie_data = load_data_serie(serie_)
            if method_ == "raw":
                res[serie_index] = serie_data.reshape(-1, serie_data.shape[-1])
            else:
                res[serie_index] = method_(serie_data, axis=0)
        if what == "dark":
            scan.set_normed_darks(res)
        else:
            scan.set_normed_flats(res)

    def compute_edf(self, scan, what, mode):
        """Compute the requested what in the given mode for `directory`

        :param str directory: path of the scan
        :param what: what to compute (ref or dark)
        :param mode: how to compute it (median or average...)
        """
        directory = scan.path
        assert type(directory) is str

        def removeFiles():
            """Remove orignals files fitting the what (dark or ref)"""
            if what is DarkRefs.WHAT_DARK:
                # In the case originals has already been found for the median
                # calculation
                if len(self._originalsDark) > 0:
                    files = self._originalsDark
                else:
                    files = getOriginals(DarkRefs.WHAT_DARK)
            elif what is DarkRefs.WHAT_REF:
                if len(self._originalsRef) > 0:
                    files = self._originalsRef
                else:
                    files = getOriginals(DarkRefs.WHAT_REF)
            else:
                logger.error(
                    "the requested what (%s) is not recognized. "
                    "Can't remove corresponding file" % what
                )
                return

            _files = set(files)
            if len(files) > 0:
                if has_rsync:
                    logger.info(
                        "ask RSyncManager for removal of %s files in %s"
                        % (what, directory)
                    )
                    # for lbsram take into account sync from data watcher
                    if directory.startswith(settings.get_lbsram_path()):
                        for f in files:
                            _files.add(
                                f.replace(
                                    settings.get_lbsram_path(),
                                    settings.get_dest_path(),
                                    1,
                                )
                            )
                    RSyncManager().removesync_files(
                        dir=directory, files=_files, block=self._forceSync
                    )
                else:
                    for _file in _files:
                        try:
                            os.remove(_file)
                        except Exception as e:
                            logger.error(e)

        def getOriginals(what):
            if what is DarkRefs.WHAT_REF:
                try:
                    pattern = re.compile(self.recons_params.ref_pattern)
                except Exception:
                    pattern = None
                    logger.error(
                        "Fail to compute regular expresion for %s"
                        % self.recons_params.ref_pattern
                    )
            elif what is DarkRefs.WHAT_DARK:
                re.compile(self.recons_params.dark_pattern)
                try:
                    pattern = re.compile(self.recons_params.dark_pattern)
                except Exception:
                    pattern = None
                    logger.error(
                        "Fail to compute regular expresion for %s"
                        % self.recons_params.dark_pattern
                    )

            filelist_fullname = []
            if pattern is None:
                return filelist_fullname
            for file in os.listdir(directory):
                if pattern.match(file) and file.endswith(self._file_ext):
                    if (
                        file.startswith(self.recons_params.ref_prefix)
                        or file.startswith(self.recons_params.dark_prefix)
                    ) is False:
                        filelist_fullname.append(os.path.join(directory, file))
            return sorted(filelist_fullname)

        def setup():
            """setup parameter to process the requested what

            :return: True if there is a process to be run, else false
            """

            def getNDigits(_file):
                file_without_scanID = _file.replace(os.path.basename(directory), "", 1)
                return len(re.findall(r"\d+", file_without_scanID))

            def dealWithPCOTomo():
                filesPerSerie = {}
                if self.nfiles % self.nacq == 0:
                    assert self.nacq < self.nfiles
                    self.nseries = self.nfiles // self.nacq
                    self.series = self.fileNameList
                else:
                    logger.warning("Fail to deduce series")
                    return None, None

                linear = getNDigits(self.fileNameList[0]) < 2
                if linear is False:
                    # which digit pattern contains the file number?
                    lastone = True
                    penulti = True
                    for first_files in range(self.nseries - 1):
                        digivec_1 = re.findall(r"\d+", self.fileNameList[first_files])
                        digivec_2 = re.findall(
                            r"\d+", self.fileNameList[first_files + 1]
                        )
                        if lastone:
                            lastone = (int(digivec_2[-1]) - int(digivec_1[-1])) == 0
                        if penulti:
                            penulti = (int(digivec_2[-2]) - int(digivec_1[-2])) == 0

                    linear = not penulti

                if linear is False:
                    digivec_1 = re.findall(r"\d+", self.fileNameList[self.nseries - 1])
                    digivec_2 = re.findall(r"\d+", self.fileNameList[self.nseries])
                    # confirm there is 1 increment after self.nseries in the uperlast last digit patern
                    if (int(digivec_2[-2]) - int(digivec_1[-2])) != 1:
                        linear = True

                # series are simple sublists in main filelist
                # self.series = []
                if linear is True:
                    is_there_digits = len(re.findall(r"\d+", self.fileNameList[0])) > 0
                    if is_there_digits:
                        serievec = set([re.findall(r"\d+", self.fileNameList[0])[-1]])
                    else:
                        serievec = set(["0000"])
                    for i in range(self.nseries):
                        if is_there_digits:
                            serie = re.findall(
                                r"\d+", self.fileNameList[i * self.nacq]
                            )[-1]
                            serievec.add(serie)
                            filesPerSerie[serie] = self.fileNameList[
                                i * self.nacq : (i + 1) * self.nacq
                            ]
                        else:
                            serievec.add("%04d" % i)
                # in the sorted filelist, the serie is incremented, then the acquisition number:
                else:
                    self.series = self.fileNameList[0 :: self.nseries]
                    serievec = set([re.findall(r"\d+", self.fileNameList[0])[-1]])
                    for serie in serievec:
                        # serie = re.findall(r'\d+', self.fileNameList[i])[-1]
                        # serievec.add(serie)
                        filesPerSerie[serie] = self.fileNameList[0 :: self.nseries]
                serievec = list(sorted(serievec))

                if len(serievec) > 2:
                    logger.error(
                        "DarkRefs do not deal with multiple scan."
                        " (scan %s)" % directory
                    )
                    return None, None
                assert len(serievec) <= 2
                if len(serievec) > 1:
                    key = serievec[-1]
                    tomoN = self.getInfo(self.TOMO_N)
                    if tomoN is None:
                        logger.error(
                            "Fail to found information %s. Can't "
                            "rename %s" % (self.TOMO_N, key)
                        )
                    del serievec[-1]
                    serievec.append(str(tomoN).zfill(4))
                    filesPerSerie[serievec[-1]] = filesPerSerie[key]
                    del filesPerSerie[key]
                    assert len(serievec) == 2
                    assert len(filesPerSerie) == 2

                return serievec, filesPerSerie

            # start setup function
            if mode == dkrf_reconsparams.Method.none:
                return False
            if what == "dark":
                self.out_prefix = self.recons_params.dark_prefix
                self.info_nacq = "DARK_N"
            else:
                self.out_prefix = self.recons_params.ref_prefix
                self.info_nacq = "REF_N"

            # init
            self.nacq = 0
            """Number of acquisition runned"""
            self.files = 0
            """Ref or dark files"""
            self.nframes = 1
            """Number of frame per ref/dark file"""
            self.serievec = ["0000"]
            """List of series discover"""
            self.filesPerSerie = {}
            """Dict with key the serie id and values list of files to compute
            for median or mean"""
            self.infofile = ""
            """info file of the acquisition"""

            # sample/prefix and info file
            self.prefix = os.path.basename(directory)
            extensionToTry = (DarkRefs.info_suffix, "0000" + DarkRefs.info_suffix)
            for extension in extensionToTry:
                infoFile = os.path.join(directory, self.prefix + extension)
                if os.path.exists(infoFile):
                    self.infofile = infoFile
                    break

            if self.infofile == "":
                logger.debug("fail to found .info file for %s" % directory)

            """
            Set filelist
            """
            # do the job only if not already done and overwrite not asked
            self.out_files = sorted(glob(directory + os.sep + "*." + self._file_ext))

            self.filelist_fullname = getOriginals(what)
            self.fileNameList = []
            [
                self.fileNameList.append(os.path.basename(_file))
                for _file in self.filelist_fullname
            ]
            self.fileNameList = sorted(self.fileNameList)
            self.nfiles = len(self.filelist_fullname)
            # if nothing to process
            if self.nfiles == 0:
                logger.info(
                    "no %s for %s, because no file to compute found" % (what, directory)
                )
                return False

            self.fid = fabio.open(self.filelist_fullname[0])
            self.nframes = self.fid.nframes
            self.nacq = 0
            # get the info of number of acquisitions
            if self.infofile != "":
                self.nacq = self.getInfo(self.info_nacq)

            if self.nacq == 0:
                self.nacq = self.nfiles

            self.nseries = 1
            if self.nacq > self.nfiles:
                # get ready for accumulation and/or file multiimage?
                self.nseries = self.nfiles
            if self.nacq < self.nfiles and getNDigits(self.fileNameList[0]) < 2:
                self.nFilePerSerie = self.nseries
                self.serievec, self.filesPerSerie = dealWithPCOTomo()
            else:
                self.series = self.fileNameList
                self.serievec = _getSeriesValue(self.fileNameList)
                self.filesPerSerie, self.nFilePerSerie = groupFilesPerSerie(
                    self.filelist_fullname, self.serievec
                )

            if self.filesPerSerie is not None:
                for serie in self.filesPerSerie:
                    for _file in self.filesPerSerie[serie]:
                        if what == "dark":
                            self._originalsDark.append(os.path.join(scan.path, _file))
                        elif what == "ref":
                            self._originalsRef.append(os.path.join(scan.path, _file))

            return self.serievec is not None and self.filesPerSerie is not None

        def _getSeriesValue(fileNames):
            assert len(fileNames) > 0
            is_there_digits = len(re.findall(r"\d+", fileNames[0])) > 0
            series = set()
            i = 0
            for fileName in fileNames:
                if is_there_digits:
                    name = fileName.rstrip(self._file_ext)
                    file_index = name.split("_")[-1]
                    rm_not_numeric = re.compile(r"[^\d.]+")
                    file_index = rm_not_numeric.sub("", file_index)
                    series.add(file_index)
                else:
                    series.add("%04d" % i)
                    i += 1
            return list(series)

        def groupFilesPerSerie(files, series):
            def findFileEndingWithSerie(poolFiles, serie):
                res = []
                for _file in poolFiles:
                    _f = _file.rstrip(".edf")
                    if _f.endswith(serie):
                        res.append(_file)
                return res

            def checkSeriesFilesLength(serieFiles):
                length = -1
                for serie in serieFiles:
                    if length == -1:
                        length = len(serieFiles[serie])
                    elif len(serieFiles[serie]) != length:
                        logger.error("Series with inconsistant number of ref files")

            assert len(series) > 0
            if len(series) == 1:
                return {series[0]: files}, len(files)
            assert len(files) > 0

            serieFiles = {}
            unattributedFiles = files.copy()
            for serie in series:
                serieFiles[serie] = findFileEndingWithSerie(unattributedFiles, serie)
                [unattributedFiles.remove(_f) for _f in serieFiles[serie]]

            if len(unattributedFiles) > 0:
                logger.error("Failed to associate %s to any serie" % unattributedFiles)
                return {}, 0

            checkSeriesFilesLength(serieFiles)

            return serieFiles, len(serieFiles[list(serieFiles.keys())[0]])

        def process():
            """process calculation of the what"""
            if mode is dkrf_reconsparams.Method.none:
                return
            shape = fabio.open(self.filelist_fullname[0]).shape

            for i in range(len(self.serievec)):
                largeMat = numpy.zeros(
                    (self.nframes * self.nFilePerSerie, shape[0], shape[1])
                )

                if what == "dark" and len(self.serievec) == 1:
                    fileName = self.out_prefix
                    if fileName.endswith(self._file_ext) is False:
                        fileName = fileName + self._file_ext
                else:
                    fileName = (
                        self.out_prefix.rstrip(self._file_ext)
                        + self.serievec[i]
                        + self._file_ext
                    )
                fileName = os.path.join(directory, fileName)
                if os.path.isfile(fileName):
                    if (
                        what == "refs" and self.recons_params.overwrite_ref is False
                    ) or (
                        what == "dark" and self.recons_params.overwrite_dark is False
                    ):
                        logger.info("skip creation of %s, already existing" % fileName)
                        continue

                if self.nFilePerSerie == 1:
                    fSerieName = os.path.join(directory, self.series[i])
                    header = {"method": mode.name + " on 1 image"}
                    header["SRCUR"] = utils.getClosestSRCurrent(
                        scan_dir=directory, refFile=fSerieName
                    )
                    if self.nframes == 1:
                        largeMat[0] = fabio.open(fSerieName).data
                    else:
                        handler = fabio.open(fSerieName)
                        dShape = (self.nframes, handler.dim2, handler.dim1)
                        largeMat = numpy.zeros(dShape)
                        for iFrame in range(self.nframes):
                            largeMat[iFrame] = handler.getframe(iFrame).data
                else:
                    header = {
                        "method": mode.name + " on %d images" % self.nFilePerSerie
                    }
                    header["SRCUR"] = utils.getClosestSRCurrent(
                        scan_dir=directory, refFile=self.series[i][0]
                    )
                    for j, fName in zip(
                        range(self.nFilePerSerie), self.filesPerSerie[self.serievec[i]]
                    ):
                        file_BigMat = fabio.open(fName)
                        if self.nframes > 1:
                            for fr in range(self.nframes):
                                jfr = fr + j * self.nframes
                                largeMat[jfr] = file_BigMat.getframe(fr).getData()
                        else:
                            largeMat[j] = file_BigMat.data
                if mode == dkrf_reconsparams.Method.median:
                    data = numpy.median(largeMat, axis=0)
                elif mode == dkrf_reconsparams.Method.average:
                    data = numpy.mean(largeMat, axis=0)
                elif mode == dkrf_reconsparams.Method.first:
                    data = largeMat[0]
                elif mode == dkrf_reconsparams.Method.last:
                    data = largeMat[-1]
                elif mode == dkrf_reconsparams.Method.none:
                    return
                else:
                    raise ValueError(
                        "Unrecognized calculation type request {}" "".format(mode)
                    )

                self.nacq = getDARK_N(directory) or 1
                if what == "dark" and self.nacq > 1:  # and self.nframes == 1:
                    data = data / self.nacq
                    # add one to add to avoid division by zero
                    # data = data + 1
                file_desc = fabio.edfimage.EdfImage(data=data, header=header)
                i += 1
                _ttype = numpy.uint16 if what == "dark" else numpy.int32
                file_desc.write(fileName, force_type=_ttype)

        if directory is None:
            return
        if setup():
            logger.info("start proccess darks and flat fields for %s" % scan.path)
            process()
            logger.info("end proccess darks and flat fields")

        self._store_result(what=what, scan=scan)
        if (what == "dark" and self.recons_params.remove_dark is True) or (
            what == "refs" and self.recons_params.remove_ref is True
        ):
            removeFiles()

    def _store_result(self, what, scan):
        try:
            if what == "dark":
                dark = DarkRefs.getDarkHSTFiles(
                    directory=scan.path, prefix=self.recons_params.dark_prefix
                )
                dark_1 = fabio.open(dark[0]).data
                scan.set_normed_darks({0: dark_1})
            else:
                refs = DarkRefs.getRefHSTFiles(
                    directory=scan.path, prefix=self.recons_params.ref_prefix
                )
                refs_dict = {}
                if len(refs) == 1:
                    ref_1 = fabio.open(refs[0]).data
                    refs_dict[0] = ref_1
                elif len(refs) >= 2:
                    ref_1 = fabio.open(refs[0]).data
                    refs_dict[0] = ref_1
                    ref_f = fabio.open(refs[-1]).data
                    refs_dict[len(scan.projections)] = ref_f
                scan.set_normed_flats(refs_dict)
        except Exception as e:
            logger.info(e)

    def getInfo(self, what):
        with open(self.infofile) as file:
            infod = file.readlines()
            for line in infod:
                if what in line:
                    return int(line.split("=")[1])
        # not found:
        return 0

    def getDarkFiles(self, directory):
        """

        :return: the list of existing darks files in the directory according to
                 the file pattern.
        """
        patternDark = re.compile(self.recons_params.dark_pattern)

        res = []
        for file in os.listdir(directory):
            if patternDark.match(file) is not None and file.endswith(self._file_ext):
                res.append(os.path.join(directory, file))
        return res

    def getRefFiles(self, directory):
        """

        :return: the list of existing refs files in the directory according to
                 the file pattern.
        """
        patternRef = re.compile(self.recons_params.ref_pattern)

        res = []
        for file in os.listdir(directory):
            if patternRef.match(file) and file.endswith(self._file_ext):
                res.append(os.path.join(directory, file))
        return res

    @docstring(Task.program_name)
    @staticmethod
    def program_name():
        return "tomwer_dark_refs"

    @docstring(Task.program_version)
    @staticmethod
    def program_version():
        return tomwer.version.version

    @docstring(Task.definition)
    @staticmethod
    def definition():
        return "Compute mean or median dark and refs per each serie"


def requires_normed_dark_and_flat(scan: TomwerScanBase, logger_=None) -> tuple:
    """helper function: If no dark / flat are computed yet then will pick the first
    dark and the first flat.

    Expected usage: for tomwer application which requires some time and flat and to avoid some warnings
    within standalones.

    :params TomwerScanBase scan: scan for which we want to get quick dark and flat
    :params Optional[Logger] logger_: if provided will add some warning when attempt to get normed flat / normed dark.
    :returns: tuple of what was missing and has been computed
    """
    computed = []
    if scan.normed_flats in (None, {}):
        # set the first flat found
        recons_params = dkrf_reconsparams.DKRFRP()
        recons_params.overwrite_dark = False
        recons_params.overwrite_ref = False
        recons_params.dark_calc_method = dkrf_reconsparams.Method.none
        recons_params.flat_calc_method = dkrf_reconsparams.Method.first

        drp = DarkRefs(
            inputs={
                "data": scan,
                "dark_ref_params": recons_params,
            }
        )
        if logger_ is not None:
            logger.warning(
                "No 'calculated' flat found. Will try to pick the first flat found as the `calculated` flat."
            )
        drp.run()
        computed.append("flat")

    if scan.normed_darks in (None, {}):
        # set the first dark found
        recons_params = dkrf_reconsparams.DKRFRP()
        recons_params.overwrite_dark = False
        recons_params.overwrite_ref = False
        recons_params.dark_calc_method = dkrf_reconsparams.Method.first
        recons_params.flat_calc_method = dkrf_reconsparams.Method.none

        drp = DarkRefs(
            inputs={
                "data": scan,
                "dark_ref_params": recons_params,
            }
        )
        if logger_ is not None:
            logger.warning(
                "No 'calculated' dark found. Will try to pick the first flat found as the `calculated` dark."
            )
        drp.run()
        computed.append("dark")

    return tuple(computed)
