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
__date__ = "05/07/2017"


import socket
import os
from tomwer.core import settings
import tomwer.version
from tomwer.core.process.task import BaseProcessInfo
import logging
from .rpcserver import DataListenerThread
from nxtomomill import converter as nxtomomill_converter
from tomwer.core.scan.hdf5scan import HDF5TomoScan
from tomoscan.io import HDF5File
from silx.io.utils import h5py_read_dataset
from ewokscore.task import Task as EwoksTask
import typing

try:
    # new HDF5Config class
    from nxtomomill.io.config import TomoHDF5Config as HDF5Config
except ImportError:
    from nxtomomill.io.config import HDF5Config

try:
    from nxtomomill.converter import _Acquisition

    _SCAN_NUMBER_PATH = _Acquisition._SCAN_NUMBER_PATH
except ImportError:
    from nxtomomill.converter.hdf5.acquisition.baseaquisition import BaseAcquisition

    _SCAN_NUMBER_PATH = BaseAcquisition._SCAN_NUMBER_PATH

_logger = logging.getLogger(__name__)


def nxtomomill_input_callback(entry, desc):
    """note: for the data listener we want to avoid any user intereaction.
    In order to avoid any time lost"""
    if entry == "energy":
        _logger.warning("Energy is missing {}. set to {}".format(entry, 19.0))
        return 19.0
    else:
        _logger.warning("missing {}. Won't be set".format(entry))
        return None


class _DataListenerTaskPlaceHolder(EwoksTask, output_names=["data"]):
    pass


class DataListener(BaseProcessInfo):
    # TODO: update this, DataListener is not properly a task
    """
    class able to connect with a redis database.
    During an acquisition at esrf the redis database expose the scan under
    acquisition. This allow use to know when a scan is finished.

    In order to insure connection the machine need to know where is located
    the 'bacon server'
    (see https://bliss.gitlab-pages.esrf.fr/bliss/master/bliss_data_life.html).
    This is why the 'BEACON_HOST' environment variable should be defined.

    For example for id19 - lbs 191 we have:
    export BEACON_HOST="europa"
    On id19 - europa we would have
    export BEACON_HOST="localhost"
    """

    TIMOUT_READ_FILE = 30
    "When the event 'scan_ended' is received all data might not have been write" " yet"

    def __init__(self):
        super().__init__()
        self._host = settings.JSON_RPC_HOST
        # if host is None then use hostname
        if self._host is None:
            self._host = socket.gethostname()
        self._port = settings.JSON_RPC_PORT
        self._listening_thread = None

    @staticmethod
    def program_name():
        """Name of the program used for this processing"""
        return "data listener"

    @staticmethod
    def program_version():
        """version of the program used for this processing"""
        return tomwer.version.version

    @staticmethod
    def definition():
        """definition of the process"""
        "convert bliss sequence with a proposal to a NXTomo nexus file"

    @property
    def port(self):
        return self._port

    @property
    def host(self):
        return self._host

    def get_listening_thread(self):
        """
        return the listening thread to ear at tango server
        """
        if self._listening_thread is None:
            self._listening_thread = self.create_listening_thread()
        return self._listening_thread

    def create_listening_thread(self):
        """
        Procedure to create the listening thread
        :return: listening thread
        """
        return DataListenerThread(host=self.host, port=self.port)

    def delete_listening_thread(self):
        """
        Procedure to delete the listening thread
        """
        if hasattr(self, "_listening_thread"):
            if self._listening_thread is not None:
                self._listening_thread.stop()
                self._listening_thread.join(5)
            del self._listening_thread
        self._listening_thread = None

    def set_configuration(self, properties):
        # for now the NXProcess cannot be tune
        if isinstance(properties, HDF5Config):
            self._settings = properties.to_dict()
        elif isinstance(properties, dict):
            self._settings = properties
        else:
            raise TypeError("invalid type: {}".format(type(properties)))

    def run(self):
        pass

    def process_sample_file(
        self,
        sample_file: str,
        entry: str,
        proposal_file: str,
        master_sample_file: typing.Union[str, None],
    ) -> tuple:
        """

        :param sample_file: file to be converted
        :param entry: entry in the tango .h5 file to be converter
        :return: tuple scan succeeded.
        """
        if not os.path.isfile(sample_file):
            raise ValueError("Given file {} does not exists.".format(sample_file))
        scans = []
        for mf_emf in self.convert(bliss_file=sample_file, entry=entry):
            master_file, entry_master_file = mf_emf
            if master_file is not None and entry_master_file is not None:
                scan = HDF5TomoScan(scan=master_file, entry=entry_master_file)

                try:
                    # register process.
                    # also store the source 'scan' folder. This information will
                    # be needed by the datatransfert if some given later.
                    source_scans = DataListener._get_scan_sources(sample_file, entry)
                    self.register_process(
                        process_file=scan.process_file,
                        entry=scan.entry,
                        results={"output_file": scan.master_file, "entry": scan.entry},
                        configuration={
                            "sample_file": sample_file,
                            "entry": entry,
                            "source_scans": source_scans,
                            "file_proposal": proposal_file,
                            "master_sample_file": master_sample_file,
                        },
                        process_index=scan.pop_process_index(),
                        overwrite=True,
                    )
                except Exception as e:
                    _logger.error(e)

                self._signal_scan_ready(scan)
                scans.append(scan)
        return tuple(scans)

    @staticmethod
    def _get_scan_sources(bliss_file, entry) -> list:
        """Return the list of scans dir for this bliss_file / entry"""

        def get_scan_indexes():
            with HDF5File(bliss_file, "r", swmr=True) as h5f:
                entry_node = h5f[entry]
                if _SCAN_NUMBER_PATH in entry_node:
                    return h5py_read_dataset(entry_node[_SCAN_NUMBER_PATH])
                else:
                    raise ValueError("Unable to find scan number indexes")

        scans_indexes = get_scan_indexes()
        res = []
        for scans_index in scans_indexes:
            # Bad hack
            # TODO: we should find a better way to retrieve source. From
            # virtual dataset I don't see it. Maybe from symbolic link.
            scan_folder_name = "scan" + str(scans_index).zfill(4)
            scan_folder_name = os.path.join(
                os.path.dirname(bliss_file), scan_folder_name
            )
            res.append(scan_folder_name)
        return res

    @staticmethod
    def get_proposal_file(process_file, entry):
        """Return the proposal file of the experimentation if registred by the
        data listener"""
        if entry is None:
            with HDF5File(process_file, "r", swmr=True) as h5f:
                entries = BaseProcessInfo._get_process_nodes(
                    root_node=h5f, process=DataListener
                )
                if len(entries) == 0:
                    _logger.info(
                        "unable to find a DarkRef process in %s" % process_file
                    )
                    return None
                elif len(entries) > 1:
                    raise ValueError("several entry found, entry should be " "specify")
                else:
                    entry = list(entries.keys())[0]
                    _logger.info("take %s as default entry" % entry)

        with HDF5File(process_file, "r", swmr=True) as h5f:
            dl_nodes = BaseProcessInfo._get_process_nodes(
                root_node=h5f[entry], process=DataListener
            )
            index_to_path = {}
            for key, index in dl_nodes.items():
                index_to_path[index] = key

            if len(dl_nodes) == 0:
                return None
            # take the last processed dark ref
            last_process_index = sorted(dl_nodes.values())[-1]
            last_process_dl = index_to_path[last_process_index]
            if (len(index_to_path)) > 1:
                _logger.debug(
                    "several processing found for data listener,"
                    "take the last one: %s" % last_process_dl
                )

            if "configuration" in h5f[last_process_dl].keys():
                results_node = h5f[last_process_dl]["configuration"]
                if "file_proposal" in results_node.keys():
                    try:
                        fp = h5py_read_dataset(
                            results_node["file_proposal"]
                        )  # .decode("UTF-8")
                    except AttributeError:
                        return None
                    else:
                        return fp
                else:
                    return None
            return None

    # TODO the 3 static functions get_proposal_file, get_sample_file and
    # get_source_scans are sharing a lot of source code and should
    # be 'concatenate'
    @staticmethod
    def get_sample_file(process_file, entry):
        """Return the proposal file of the experimentation if registred by the
        data listener"""
        if entry is None:
            with HDF5File(process_file, "r", swmr=True) as h5f:
                entries = BaseProcessInfo._get_process_nodes(
                    root_node=h5f, process=DataListener
                )
                if len(entries) == 0:
                    _logger.info(
                        "unable to find a DarkRef process in %s" % process_file
                    )
                    return None
                elif len(entries) > 1:
                    raise ValueError("several entry found, entry should be " "specify")
                else:
                    entry = list(entries.keys())[0]
                    _logger.info("take %s as default entry" % entry)

        with HDF5File(process_file, "r", swmr=True) as h5f:
            dl_nodes = BaseProcessInfo._get_process_nodes(
                root_node=h5f[entry], process=DataListener
            )
            index_to_path = {}
            for key, value in dl_nodes.items():
                index_to_path[key] = key

            if len(dl_nodes) == 0:
                return None
            # take the last processed dark ref
            last_process_index = sorted(dl_nodes.keys())[-1]
            last_process_dl = index_to_path[last_process_index]
            if (len(index_to_path)) > 1:
                _logger.debug(
                    "several processing found for data listener,"
                    "take the last one: %s" % last_process_dl
                )

            if "configuration" in h5f[last_process_dl].keys():
                results_node = h5f[last_process_dl]["configuration"]
                if "sample_file" in results_node.keys():
                    return h5py_read_dataset(
                        results_node["sample_file"]
                    )  # .decode("UTF-8")
                else:
                    return None
            return None

    @staticmethod
    def get_master_sample_file(process_file, entry):
        """Return the proposal file of the experimentation if registred by the
        data listener"""
        if entry is None:
            with HDF5File(process_file, "r", swmr=True) as h5f:
                entries = BaseProcessInfo._get_process_nodes(
                    root_node=h5f, process=DataListener
                )
                if len(entries) == 0:
                    _logger.info(
                        "unable to find a DarkRef process in %s" % process_file
                    )
                    return None
                elif len(entries) > 1:
                    raise ValueError("several entry found, entry should be " "specify")
                else:
                    entry = list(entries.keys())[0]
                    _logger.info("take %s as default entry" % entry)

        with HDF5File(process_file, "r", swmr=True) as h5f:
            dl_nodes = BaseProcessInfo._get_process_nodes(
                root_node=h5f[entry], process=DataListener
            )
            index_to_path = {}
            for key, value in dl_nodes.items():
                index_to_path[key] = key

            if len(dl_nodes) == 0:
                return None
            # take the last processed dark ref
            last_process_index = sorted(dl_nodes.keys())[-1]
            last_process_dl = index_to_path[last_process_index]
            if (len(index_to_path)) > 1:
                _logger.debug(
                    "several processing found for data listener,"
                    "take the last one: %s" % last_process_dl
                )

            if "configuration" in h5f[last_process_dl].keys():
                results_node = h5f[last_process_dl]["configuration"]
                if "master_sample_file" in results_node.keys():
                    return h5py_read_dataset(
                        results_node["master_sample_file"]
                    )  ##.decode("UTF-8")
                else:
                    return None
            return None

    @staticmethod
    def get_source_scans(process_file, entry):
        """Return the list of 'bliss scan directory' created for holding this
        specific sequence data
        """
        if entry is None:
            with HDF5File(process_file, "r", swmr=True) as h5f:
                entries = BaseProcessInfo._get_process_nodes(
                    root_node=h5f, process=DataListener
                )
                if len(entries) == 0:
                    _logger.info(
                        "unable to find a DarkRef process in %s" % process_file
                    )
                    return None
                elif len(entries) > 1:
                    raise ValueError("several entry found, entry should be " "specify")
                else:
                    entry = list(entries.keys())[0]
                    _logger.info("take %s as default entry" % entry)

        with HDF5File(process_file, "r", swmr=True) as h5f:
            dl_nodes = BaseProcessInfo._get_process_nodes(
                root_node=h5f[entry], process=DataListener
            )
            index_to_path = {}
            for key, index in dl_nodes.items():
                index_to_path[index] = key

            if len(dl_nodes) == 0:
                return {}
            # take the last processed dark ref
            last_process_index = sorted(dl_nodes.values())[-1]
            last_process_dl = index_to_path[last_process_index]
            if (len(index_to_path)) > 1:
                _logger.debug(
                    "several processing found for data listener,"
                    "take the last one: %s" % last_process_dl
                )

            if "configuration" in h5f[last_process_dl].keys():
                results_node = h5f[last_process_dl]["configuration"]
                if "source_scans" in results_node.keys():
                    tmp_res = h5py_read_dataset(results_node["source_scans"])

                    def conv(my_str):
                        if hasattr(my_str, "decode"):
                            return my_str.decode("UTF-8")
                        else:
                            return my_str

                    res = [conv(mystr) for mystr in tmp_res]
                    return res
                else:
                    return None
            return None

    def convert(self, bliss_file: str, entry: str) -> tuple:
        """

        :param bliss_file: file to be converted
        :param entry: entry in the tango .h5 file to be converter
        :return: tuple (output file, output file entry). Both are set to None
                 if conversion fails.
        """
        from tomwer.core.process.control.nxtomomill import NxTomomillProcess

        conf = self.get_configuration()
        if conf is None:
            conf = {}
        configuration = HDF5Config.from_dict(conf)
        if configuration.output_file is None:
            output_file_path = NxTomomillProcess.deduce_output_file_path(
                bliss_file, entry=entry, outputdir=None
            )
        else:
            output_file_path = configuration.output_file

        if os.path.exists(output_file_path):
            if not self._ask_user_for_overwritting(output_file_path):
                return ((None, None),)

        if entry.startswith("/"):
            entries = (entry,)
        else:
            entries = ("/" + entry,)

        # work around: we need to wait a bit before converting the file
        # otherwise it looks like the file might not be ended to be
        # write
        def sequence_is_finished():
            try:
                with HDF5File(bliss_file, "r", swmr=True) as h5f:
                    end_scan_path = "/".join((entry, "end_time"))
                    return end_scan_path in h5f
            except Exception:
                return False

        timeout = self.TIMOUT_READ_FILE
        import time

        while timeout > 0 and not sequence_is_finished():
            timeout = timeout - 0.2
            time.sleep(0.2)

        if timeout <= 0:
            _logger.error(
                "unable to access {}@{}. (Write never ended)".format(entry, bliss_file)
            )
            return ((None, None),)
        # one more delay to insure we can read it
        time.sleep(4)

        # force some parameters
        configuration.input_file = bliss_file
        configuration.output_file = output_file_path
        configuration.entries = entries
        configuration.single_file = False
        configuration.overwrite = True
        configuration.request_input = True
        configuration.file_extension = ".nx"
        try:
            convs = nxtomomill_converter.from_h5_to_nx(
                configuration=configuration,
                input_callback=nxtomomill_input_callback,
                progress=None,
            )
        except Exception as e:
            _logger.error(
                "Fail to convert from tango file: %s to NXTomo."
                "Conversion error is: %s" % (bliss_file, e)
            )
            return ((None, None),)
        else:
            return convs

    def _ask_user_for_overwritting(self, file_path):
        res = None
        while res not in ("Y", "n"):
            res = input(
                "The process will overwrite %s. Do you agree ? (Y/n)" "" % file_path
            )

        return res == "Y"

    def _signal_scan_ready(self, scan):
        assert isinstance(scan, HDF5TomoScan)
        pass

    def activate(self, activate=True):
        """
        activate or deactivate the thread. When deactivate call join and
        delete the thread

        :param bool activate:
        """
        if activate:
            if self._listening_thread is not None:
                _logger.info("listening is already activate")
            else:
                assert isinstance(self, DataListener)
                if not self.is_port_available():
                    raise OSError("Port already used")
                self.get_listening_thread().start()
        else:
            if self._listening_thread is None:
                return
            else:
                self.delete_listening_thread()

    def is_active(self):
        if self._listening_thread is None:
            return False
        else:
            return True

    def is_port_available(self):
        """

        :return: True if the port is available else False
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return not s.connect_ex((self._host, self._port)) == 0
