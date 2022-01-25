# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2016-2020 European Synchrotron Radiation Facility
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
__date__ = "06/08/2020"


from tomwer.core.scan.scanbase import TomwerScanBase
from tomwer.core.scan.hdf5scan import HDF5TomoScan
import tomwer.version
from silx.utils.enum import Enum as _Enum
from silx.io.url import DataUrl
from contextlib import AbstractContextManager
from multiprocessing import Queue as _MQueue
import logging
from logging.handlers import QueueListener
import datetime
import typing
import os

try:
    from tomoscan.scanbase import _FOV as FOV
except ImportError:
    from tomoscan.scanbase import FOV

_logger = logging.getLogger(__name__)


class TomwerInfo(AbstractContextManager):
    """Simple context manager to add tomwer metadata to a dict before
    writing it"""

    def __init__(self, config_dict):
        self.config = config_dict

    def __enter__(self):
        self.config["other"] = {
            "tomwer_version": tomwer.version.version,
            "date": datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        }
        return self.config

    def __exit__(self, exc_type, exc_val, exc_tb):
        del self.config["other"]["tomwer_version"]
        del self.config["other"]["date"]


class ProcessLogCM(AbstractContextManager):
    def __init__(self):
        self.q = _MQueue()
        # this is the handler for all log records
        self.handler = logging.StreamHandler()

        # ql gets records from the queue and sends them to the handler
        self.ql = QueueListener(self.q, self.handler)

        logger = logging.getLogger()
        logger.addHandler(self.handler)

    def __enter__(self):
        self.ql.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.ql.stop()
        logger = logging.getLogger()
        logger.removeHandler(self.handler)


def retrieve_lst_of_value_from_str(my_string: str, type_) -> tuple:
    """
    Return a list of value from a string like '12,23' or '(12, 23)',
    '[12;23]', '12;23' or with the pattern from:to:step like '0:10:1'

    :param str mystring:
    :return: list of single value
    """
    assert type(my_string) is str, "work on string only"
    res = []
    my_string = my_string.replace("(", "")
    my_string = my_string.replace(")", "")
    my_string = my_string.replace("[", "")
    my_string = my_string.replace("]", "")
    if my_string.count(":") == 2:
        _from, _to, _step = my_string.split(":")
        _from, _to, _step = float(_from), float(_to), float(_step)
        if _from > _to:
            tmp = _to
            _to = _from
            _from = tmp
        while _from <= _to:
            res.append(_from)
            _from += _step
        return tuple(res)
    else:
        vals = my_string.replace(" ", "")
        vals = vals.replace("_", "")
        vals = vals.replace(";", ",").split(",")
        for val in vals:
            try:
                res.append(type_(val))
            except Exception:
                pass
        return tuple(res)


def get_nabu_resources_desc(scan: TomwerScanBase, method, workers=1) -> dict:
    """
    Create the descriptor of nabu's resources

    :param TomwerScanBase scan:
    :param str method:
    :return: nabu's description of resources to be used
    """
    assert isinstance(scan, TomwerScanBase)
    res = {
        "method": method,
        "cpu_workers": workers,
        "queue": "gpu",
        "memory_per_node": "90%",
        "threads_per_node": "100%",
        "walltime": "01:00:00",
    }
    return res


def get_nabu_about_desc(overwrite) -> dict:
    """
    Create the description for nabu's about

    :param self:
    :return:
    """
    return {"overwrite_results": str(bool(overwrite))}


def get_recons_urls(
    file_prefix: str,
    location: str,
    file_format: str,
    scan: TomwerScanBase,
    slice_index: typing.Union[int, None],
    start_z: typing.Union[int, None],
    end_z: typing.Union[int, None],
):
    file_format = file_format.lower()
    if file_format in ("npy", "npz"):
        output_file_folder = os.path.join(location, file_prefix)
        file_name = ".".join((file_prefix, file_format))
        output_file_names = (os.path.join(output_file_folder, file_name),)
        scheme = "numpy"
        data_paths = (None,)
        data_slices = (None,)
    elif file_format in ("hdf5", "h5", "hdf"):
        if slice_index is not None:
            file_name = "_".join((file_prefix, str(slice_index).zfill(4)))
        else:
            file_name = file_prefix
        output_file_names = ".".join((file_name, file_format))
        output_file_names = (os.path.join(location, output_file_names),)
        scheme = "silx"
        if isinstance(scan, HDF5TomoScan):
            data_paths = "/".join((scan.entry, "reconstruction", "results", "data"))
        else:
            data_paths = "/".join(("entry", "reconstruction", "results", "data"))
        data_slices = (None,)
        data_paths = (data_paths,)
    elif file_format in ("tiff", "jp2k", "edf"):
        output_extension = file_format
        if file_format == "jp2k":
            output_extension = "jp2"
        output_file_names = []
        if slice_index is None and start_z is None and end_z is None:
            output_file = (
                os.path.join(location, file_prefix, file_prefix)
                + "."
                + output_extension
            )
            output_file_names.append(output_file)
        else:
            output_file_folder = os.path.join(location, file_prefix)

            if slice_index is None:
                if end_z == -1:
                    end_z = scan.dim_2
                else:
                    end_z = end_z + 1
                for i in range(start_z, end_z):
                    file_name = "_".join((file_prefix, str(i).zfill(4)))
                    file_name = ".".join((file_name, output_extension))
                    output_file_names.append(
                        os.path.join(output_file_folder, file_name)
                    )
            else:
                file_name = ".".join((file_prefix, output_extension))
                output_file_names.append(os.path.join(output_file_folder, file_name))
        if file_format == "edf":
            scheme = "fabio"
        else:
            scheme = "tomwer"
        data_paths = [None] * len(output_file_names)
        data_slices = [None] * len(output_file_names)
    else:
        raise ValueError("file format not managed: {}".format(file_format))

    res = []
    for output_file_name, data_path, data_slice in zip(
        output_file_names, data_paths, data_slices
    ):
        if os.path.exists(output_file_name):
            url = DataUrl(
                file_path=output_file_name,
                data_path=data_path,
                data_slice=data_slice,
                scheme=scheme,
            )
            res.append(url)
        else:
            msg = " ".join(
                (
                    "nabu output file not found. Something went " "wrong...",
                    output_file_name,
                )
            )
            _logger.warning(msg)
    return res


class _NabuMode(_Enum):
    FULL_FIELD = "standard acquisition"
    HALF_ACQ = "half acquisition"


class _NabuStages(_Enum):
    INI = "initialization"
    PRE = "pre-processing"
    PHASE = "phase"
    PROC = "processing"
    POST = "post-processing"
    VOLUME = "volume"

    @staticmethod
    def getStagesOrder():
        return (
            _NabuStages.INI,
            _NabuStages.PRE,
            _NabuStages.PHASE,
            _NabuStages.PROC,
            _NabuStages.POST,
        )

    @staticmethod
    def getProcessEnum(stage):
        """Return the process Enum associated to the stage"""
        stage = _NabuStages.from_value(stage)
        if stage is _NabuStages.INI:
            raise NotImplementedError()
        elif stage is _NabuStages.PRE:
            return _NabuPreprocessing
        elif stage is _NabuStages.PHASE:
            return _NabuPhase
        elif stage is _NabuStages.PROC:
            return _NabuProcessing
        elif stage is _NabuStages.POST:
            return _NabuPostProcessing
        raise NotImplementedError()


class _NabuPreprocessing(_Enum):
    """Define all the preprocessing action possible and the order they
    are applied on"""

    FLAT_FIELD_NORMALIZATION = "flat field normalization"
    CCD_FILTER = "hot spot correction"

    @staticmethod
    def getPreProcessOrder():
        return (
            _NabuPreprocessing.FLAT_FIELD_NORMALIZATION,
            _NabuPreprocessing.CCD_FILTER,
        )


class _NabuPhase(_Enum):
    """Define all the phase action possible and the order they
    are applied on"""

    PHASE = "phase retrieval"
    UNSHARP_MASK = "unsharp mask"
    LOGARITHM = "logarithm"

    @staticmethod
    def getPreProcessOrder():
        return (_NabuPhase.PHASE, _NabuPhase.UNSHARP_MASK, _NabuPhase.LOGARITHM)


class _NabuProcessing(_Enum):
    """Define all the processing action possible"""

    RECONSTRUCTION = "reconstruction"

    @staticmethod
    def getProcessOrder():
        return (_NabuProcessing.RECONSTRUCTION,)


class ConfigurationLevel(_Enum):
    REQUIRED = "required"
    OPTIONAL = "optional"
    ADVANCED = "advanced"

    def _get_num_value(self) -> int:
        if self is self.REQUIRED:
            return 0
        elif self is self.OPTIONAL:
            return 1
        elif self is self.ADVANCED:
            return 2

    def __le__(self, other):
        assert isinstance(other, ConfigurationLevel)
        return self._get_num_value() <= other._get_num_value()


class _NabuPostProcessing(_Enum):
    """Define all the post processing action available"""

    SAVE_DATA = "save"

    @staticmethod
    def getProcessOrder():
        return (_NabuPostProcessing.SAVE_DATA,)


class _NabuReconstructionMethods(_Enum):
    FBP = "FBP"


class _NabuPhaseMethod(_Enum):
    """
    Nabu phase method
    """

    PAGANIN = "Paganin"
    NONE = "None"


class _NabuFBPFilterType(_Enum):
    RAMLAK = "ramlak"


class _NabuPaddingType(_Enum):
    ZEROS = "zeros"
    EDGES = "edges"


class _RingCorrectionMethod(_Enum):
    NONE = "None"
    MUNCH = "munch"


def check_sinogram_half(scan: TomwerScanBase):
    """
    check if the scan is compliant to compute a sinogram with nabu.
    If this is an half acquisition it requires a
    :param TomwerScanBase scan:
    :raises: Value error if scan is half acquisition and with an odd number of
             projections
    """
    if scan.field_of_view is FOV.HALF and len(scan.projections) % 2 != 0:
        raise ValueError(
            "{} is half acquisition and an even number of projections is expected".format(
                str(scan)
            )
        )
