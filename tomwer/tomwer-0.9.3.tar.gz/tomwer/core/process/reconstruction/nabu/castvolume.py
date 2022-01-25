# coding: utf-8
###########################################################################
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
#############################################################################

"""
This module is dedicated to cast of volume from one file format to the other.
For now this handle:

* to 16 bits tiff
"""

__authors__ = ["H.Payno"]
__license__ = "MIT"
__date__ = "15/12/2021"


import os
import glob
from typing import Optional
from processview.core.superviseprocess import SuperviseProcess
from silx.io.utils import get_data
from tomwer.core.process.task import Task
from silx.utils.enum import Enum as _Enum
from tomwer.core.process.reconstruction.nabu.nabucommon import (
    NabuOutputFileFormat,
    get_file_format,
)
from nabu.io.writer import TIFFWriter
from tomwer.core.process.reconstruction.nabu.nabucommon import _NabuBaseReconstructor
from silx.io.url import DataUrl
from processview.core.manager import ProcessManager, DatasetState
import numpy
import logging
import pathlib
from tomoscan.io import HDF5File
from tomwer.io.utils.utils import get_slice_data

_logger = logging.getLogger(__name__)


class DataType(_Enum):
    UINT_16 = "uint 16"
    UINT_8 = "uint 8"


DATA_SIZE_TO_DTYPE = {
    DataType.UINT_16: numpy.uint16,
    DataType.UINT_8: numpy.uint8,
}


RESCALE_MIN_PERCENTILE = 10
RESCALE_MAX_PERCENTILE = 90

DEFAULT_OUTPUT_DIR = "{scan_basename}/cast_volume"


class CastVolumeTask(
    Task,
    SuperviseProcess,
    input_names=(
        "data",
        "configuration",
    ),
    output_names=("data",),
):
    def __init__(self, process_id=None, varinfo=None, inputs=None, name=None):
        SuperviseProcess.__init__(self, process_id=process_id)
        Task.__init__(self, varinfo=varinfo, inputs=inputs, label=name)

    def run(self):
        scan = self.inputs.data
        configuration = self.inputs.configuration
        output_data_type = DataType.from_value(configuration.get("output_data_type"))
        output_file_format = NabuOutputFileFormat.from_value(
            configuration.get("output_file_format")
        )
        output_file_path = configuration.get("output_file_path", DEFAULT_OUTPUT_DIR)
        # convert some pattern like "{scan_basename}"
        output_file_path = _NabuBaseReconstructor.format_output_location(
            location=output_file_path, scan=scan
        )

        output_data_path = configuration.get("output_data_path", None)
        overwrite = configuration.get("overwrite", False)
        rescale_min_percentile = configuration.get(
            "rescale_min_percentile", RESCALE_MIN_PERCENTILE
        )
        rescale_max_percentile = configuration.get(
            "rescale_max_percentile", RESCALE_MAX_PERCENTILE
        )
        if scan.latest_vol_reconstructions is None:
            mess = f"volume cast of {str(scan)} skipped. No volume found in latest reconstruction"
            _logger.processSkipped(mess)
            state = DatasetState.SKIPPED
        else:
            try:
                cast_volumes(
                    input_volume_urls=scan.latest_vol_reconstructions,
                    output_data_type=output_data_type,
                    output_file_format=output_file_format,
                    output_file_path=output_file_path,
                    output_data_path=output_data_path,
                    overwrite=overwrite,
                    scan=scan,
                    rescale_min_percentile=rescale_min_percentile,
                    rescale_max_percentile=rescale_max_percentile,
                )
            except Exception as e:
                mess = f"volume cast of {str(scan)} failed. Reason is {str(e)}"
                state = DatasetState.FAILED
            else:
                mess = f"volume cast of {str(scan)} succeed"
                state = DatasetState.SUCCEED

            _logger.processSkipped(mess)
            ProcessManager().notify_dataset_state(
                dataset=scan,
                process=self,
                state=state,
            )


class Cast:
    def __init__(
        self,
        input_file_format: NabuOutputFileFormat,
        output_data_type: DataType,
        output_file_format: NabuOutputFileFormat,
    ) -> None:
        self._input_file_format = input_file_format
        self._output_data_type = output_data_type
        self._output_file_format = output_file_format

    @property
    def input_file_format(self):
        return self._input_file_format

    @property
    def output_data_type(self):
        return self._output_data_type

    @property
    def output_file_format(self):
        return self._output_file_format

    def __str__(self):
        return f"""cast: \n
        - inputs: file format {self.input_file_format.value}
        - outputs: file format {self.input_file_format.value}, data size {self.output_data_type}
        """

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Cast):
            return False
        else:
            return (
                self.input_file_format == other.input_file_format
                and self.output_data_type == other.output_data_type
                and self.output_file_format == other.output_file_format
            )


HANDLED_CASTS = (
    Cast(
        NabuOutputFileFormat.TIFF,
        DataType.UINT_16,
        output_file_format=NabuOutputFileFormat.TIFF,
    ),
    Cast(
        NabuOutputFileFormat.TIFF,
        DataType.UINT_8,
        output_file_format=NabuOutputFileFormat.TIFF,
    ),
    Cast(
        NabuOutputFileFormat.HDF5,
        DataType.UINT_16,
        output_file_format=NabuOutputFileFormat.TIFF,
    ),
    Cast(
        NabuOutputFileFormat.HDF5,
        DataType.UINT_8,
        output_file_format=NabuOutputFileFormat.TIFF,
    ),
)


def rescale_data(
    data: numpy.ndarray,
    dtype,
    new_min,
    new_max,
    data_min=None,
    data_max=None,
    rescale_min_percentile=RESCALE_MIN_PERCENTILE,
    rescale_max_percentile=RESCALE_MAX_PERCENTILE,
):
    if data_min is None or data_max is None:
        try:
            from silx.math.combo import min_max

            data_min, data_max = min_max(data, finite=True)
        except Exception:
            data_min = numpy.percentile(data, rescale_min_percentile)
            data_max = numpy.percentile(data, rescale_max_percentile)
    # in order to fit to percentiles
    data[data < data_min] = data_min
    data[data > data_max] = data_max
    data = ((data - data_min) / (data_max - data_min)) * (new_max - new_min) + new_min
    return data.astype(dtype)


def find_histogram(url: DataUrl, scan=None) -> tuple:
    """
    Look for histogram of the provided url. If found one return the DataUrl of the nabu histogram
    """
    if not isinstance(url, DataUrl):
        raise TypeError(
            f"url is expected to be an instance of {DataUrl} not {type(url)}"
        )
    else:
        file_dir = os.path.realpath(os.path.dirname(url.file_path()))
        histo = glob.glob(os.path.join(file_dir, "*histogram.hdf5"))
        if len(histo) >= 1:
            if len(histo) > 1:
                _logger.warning(
                    f"more than one histogram found ({histo}). Pick the first one"
                )
            file_path = os.path.join(file_dir, histo[0])
            if scan is None:
                # take the first entry found
                with HDF5File(file_path, mode="r") as h5s:
                    keys = list(h5s.keys())

                if len("keys") == 0:
                    _logger.error(
                        f"No entry found in {file_path}. Unable to find histogram"
                    )
                    return None
                else:
                    entry = keys[0]
                    if len(keys) > 1:
                        _logger.warning(
                            f"more than one entry found in {file_path}. Take the first one {keys[0]}"
                        )
            else:
                entry = scan.entry if hasattr(scan, "entry") else "entry"
            return DataUrl(
                file_path=file_path,
                data_path=f"/{entry}/histogram/results/data",
                scheme="silx",
            )
        else:
            _logger.info(f"no histogram foudn at {file_dir}")
            return None


def _get_hst_saturations(hist, bins, rescale_min_percentile, rescale_max_percentile):
    hist_cum = numpy.cumsum(hist)
    bin_index_min = numpy.searchsorted(
        hist_cum, numpy.percentile(hist_cum, rescale_min_percentile)
    )
    bin_index_max = numpy.searchsorted(
        hist_cum, numpy.percentile(hist_cum, rescale_max_percentile)
    )
    return bins[bin_index_min], bins[bin_index_max]


def _try_to_find_min_max_from_histo(
    input_volume_url, rescale_min_percentile, rescale_max_percentile, scan=None
) -> tuple:
    histogram_res_url = find_histogram(input_volume_url, scan=scan)
    data_min = data_max = None
    if histogram_res_url is not None:
        try:
            histogram = get_data(histogram_res_url)
        except Exception as e:
            _logger.error(
                f"Fail to load histogram from {histogram_res_url}. Reason is {e}"
            )
        else:
            bins = histogram[1]
            hist = histogram[0]
            data_min, data_max = _get_hst_saturations(
                hist, bins, rescale_min_percentile, rescale_max_percentile
            )
    return data_min, data_max


def cast_volumes(
    input_volume_urls: tuple,
    output_data_type: DataType,
    output_file_format: NabuOutputFileFormat,
    output_file_path: str,
    output_data_path: Optional[str] = None,
    overwrite=False,
    data_min=None,
    data_max=None,
    scan=None,
    rescale_min_percentile=RESCALE_MIN_PERCENTILE,
    rescale_max_percentile=RESCALE_MAX_PERCENTILE,
) -> tuple:
    """

    :param input_volume_urls: Iterable of DataUrl pointing to the volume to convert.
                              It expect all urls to be associated to the same volume
                              in order to compute min/max on it and rescale data.
    :param DataType output_data_type: the data type you want in output
    :param NabuOutputFileFormat output_file_format: output file format
    :param str output_file_path: path to save the result.
    :param str output_data_path: output data path for hdf5 files
    :param bool overwrite: overwrite file / dataset if already exists
    :return: tuple of created DataUrl
    :rtype: tuple
    """
    if not os.path.exists(output_file_path):
        os.makedirs(output_file_path, exist_ok=True)

    if len(input_volume_urls) == 0:
        return

    if data_min is None or data_max is None:
        data_min, data_max = _try_to_find_min_max_from_histo(
            input_volume_url=input_volume_urls[0],
            scan=scan,
            rescale_min_percentile=rescale_min_percentile,
            rescale_max_percentile=rescale_max_percentile,
        )
    # if failed to find histogram from nabu histogram file then recompute it
    if data_min is None or data_max is None:
        data_min = numpy.finfo(numpy.float64).max
        data_max = numpy.finfo(numpy.float64).min
        for input_volume_url in input_volume_urls:
            data = get_slice_data(input_volume_url)
            data_min = min(data_min, numpy.min(data))
            data_max = max(data_max, numpy.max(data))

    res = []
    for input_volume_url in input_volume_urls:
        res.append(
            cast_volume(
                input_volume_url=input_volume_url,
                output_data_type=output_data_type,
                output_file_format=output_file_format,
                output_file_path=output_file_path,
                output_data_path=output_data_path,
                overwrite=overwrite,
                data_min=data_min,
                data_max=data_max,
            )
        )
    return tuple(res)


def cast_volume(
    input_volume_url: DataUrl,
    output_data_type: DataType,
    output_file_format: NabuOutputFileFormat,
    output_file_path: str,
    output_data_path: Optional[str] = None,
    overwrite=False,
    data_min=None,
    data_max=None,
    scan=None,
    rescale_min_percentile=RESCALE_MIN_PERCENTILE,
    rescale_max_percentile=RESCALE_MAX_PERCENTILE,
) -> DataUrl:
    if not isinstance(input_volume_url, DataUrl):
        raise TypeError(
            f"first parameter 'input_volume_url' is expected to be a DataUrl not {type(input_volume_url)}"
        )
    output_data_type = DataType.from_value(output_data_type)
    output_file_format = NabuOutputFileFormat.from_value(output_file_format)
    if not isinstance(output_file_path, (str, pathlib.Path)):
        raise TypeError(
            f"output_file_path is expected to be a str not {type(output_file_path)}"
        )
    if output_data_path is not None and not isinstance(
        output_data_path, (str, pathlib.Path)
    ):
        raise TypeError(
            f"output_data_path is expected to be a str not {type(output_data_path)}"
        )

    if not isinstance(overwrite, bool):
        raise TypeError(f"overwrite is expected to be a bool not {type(overwrite)}")

    cast = Cast(
        input_file_format=get_file_format(input_volume_url.file_path()),
        output_data_type=output_data_type,
        output_file_format=output_file_format,
    )
    if cast not in HANDLED_CASTS:
        handled_cast = "\n".join([str(c_) for c_ in HANDLED_CASTS])
        raise ValueError(
            f"cast {str(cast)} \n is not handled. Handled cast are {handled_cast} \n"
        )
    if data_min is None or data_max is None:
        data_min, data_max = _try_to_find_min_max_from_histo(
            input_volume_url=input_volume_url, scan=scan
        )
    data = get_slice_data(input_volume_url)
    if output_data_type is DataType.UINT_16:
        data = rescale_data(
            data=data,
            new_min=numpy.iinfo(numpy.uint16).min,
            new_max=numpy.iinfo(numpy.uint16).max,
            dtype=numpy.uint16,
            data_min=data_min,
            data_max=data_max,
            rescale_min_percentile=rescale_min_percentile,
            rescale_max_percentile=rescale_max_percentile,
        )
        data = data.astype(dtype=DATA_SIZE_TO_DTYPE[output_data_type])
    elif output_data_type is DataType.UINT_8:
        data = rescale_data(
            data=data,
            new_min=numpy.iinfo(numpy.uint8).min,
            new_max=numpy.iinfo(numpy.uint8).max,
            dtype=numpy.uint8,
            data_min=data_min,
            data_max=data_max,
            rescale_min_percentile=rescale_min_percentile,
            rescale_max_percentile=rescale_max_percentile,
        )
        data = data.astype(dtype=DATA_SIZE_TO_DTYPE[output_data_type])
    else:
        raise ValueError(f"{output_data_type} is not handled")

    # deduce output file path
    # for now we can only save to a directory under the same name or
    # to a file for which the path is provided already
    if os.path.isdir(output_file_path):
        original_name = os.path.basename(input_volume_url.file_path())
        original_name_with_new_ext = ".".join(
            [os.path.splitext(original_name)[0], output_file_format.value]
        )
        output_file_path = os.path.join(output_file_path, original_name_with_new_ext)
    if os.path.exists(output_file_path):
        if overwrite:
            os.remove(output_file_path)
        else:
            raise OSError("output file alrady exists ({output_file_path})")
    if output_file_format is NabuOutputFileFormat.TIFF:
        tiff_writer = TIFFWriter(output_file_path)
        tiff_writer.write(data)
        return DataUrl(
            file_path=output_file_path, scheme="cv2"
        )  # use cv2 because fabio seems to be unhappy to read float16 dataset.
    else:
        raise ValueError(f"{output_file_format} is not handled")
