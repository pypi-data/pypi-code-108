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

"""contain the AxisProcess
"""

__authors__ = ["C.Nemoz", "H.Payno"]
__license__ = "MIT"
__date__ = "19/03/2019"

from .params import (
    AxisRP,
    DEFAULT_CMP_TAKE_LOG,
    DEFAULT_CMP_OVERSAMPLING,
    DEFAULT_CMP_SUBSAMPLING_Y,
    DEFAULT_CMP_THETA,
)
from .mode import AxisMode
from .projectiontype import ProjectionType
from .anglemode import CorAngleMode
from tomwer.core.process.task import Task
from processview.core.superviseprocess import SuperviseProcess
from tomwer.core.scan.scanbase import TomwerScanBase
from processview.core.manager import ProcessManager
from processview.core.manager import DatasetState
from tomwer.core.scan.scanfactory import ScanFactory
import logging
from tomwer.core.utils import logconfig
import numpy
from typing import Union
from tomwer.utils import docstring
from tomwer.core.utils import image
import tomwer.version
from tomwer.core.scan.hdf5scan import HDF5TomoScan
from tomwer.core.process.reconstruction.nabu.utils import check_sinogram_half
from nabu.estimation.cor import (
    CenterOfRotation,
    CenterOfRotationAdaptiveSearch,
    CenterOfRotationGrowingWindow,
    CenterOfRotationSlidingWindow,
)
from nabu.pipeline.estimators import SinoCORFinder

try:
    from nabu.pipeline.estimators import CompositeCOREstimator
except ImportError:
    has_composite_cor_finder = False
else:
    has_composite_cor_finder = True
from silx.io.url import DataUrl
from tomoscan.io import HDF5File
from silx.io.utils import h5py_read_dataset
import nabu

_logger = logging.getLogger(__name__)
if not has_composite_cor_finder:
    _logger.warning("No composite cor finder found at nabu level")
# vertically, work on a window having only a percentage of the frame.
pc_height = 10.0 / 100.0
# horizontally. Global method supposes the COR is more or less in center
# % of the detector:

pc_width = 50.0 / 100.0


def adapt_tomwer_scan_to_nabu(scan: TomwerScanBase):
    """simple util to convert tomwer scan to a nabu DataAnalizer and
    updating infos regarding flat and dark if needed
    """
    dataset_infos = scan.to_nabu_dataset_analyser()
    if nabu.version > "2021.1.0" and isinstance(scan, HDF5TomoScan):
        # since this version nabu does not the load of dark / flat mean/median
        # directly in the function but outside. So we need an extra call to
        # update_dataset_info_flats_darks
        from nabu.resources.nxflatfield import update_dataset_info_flats_darks

        update_dataset_info_flats_darks(
            dataset_infos,
            processes_file=scan.get_relative_file(
                "nabu_processes.h5", with_dataset_prefix=True
            ),
            flatfield_mode=None,
        )
    return dataset_infos


def compute_cor_nabu_growing_window(
    radio_1: numpy.ndarray,
    radio_2: numpy.ndarray,
    side: str,
    padding_mode,
    flip_frame_2_lr=True,
    horz_fft_width=False,
):
    """
    Call nabu.preproc.alignement.CenterOfRotationGrowingWindow.find_shift

    :param radio_1:
    :param radio_2:
    :param padding_mode: padding mode
    :param str side: side of the cor
    :param bool flip_frame_2_lr: if True will left-right flip the second frame
    :param horz_fft_width:

    :return:
    """
    nabu_class = CenterOfRotationGrowingWindow(horz_fft_width=horz_fft_width)
    # value return is relative
    return nabu_class.find_shift(
        img_1=radio_1,
        img_2=numpy.fliplr(radio_2) if flip_frame_2_lr else radio_2,
        side=side,
        roi_yxhw=None,
        padding_mode=padding_mode,
        median_filt_shape=None,
    )


def compute_cor_nabu_growing_window_sinogram(
    scan: TomwerScanBase,
):
    """
    Call nabu.preproc.alignement.CenterOfRotationGrowingWindow.find_shift

    :param TomwerScanBase scan:
    :raises: ValueError if half acquisition with an odd number of projections

    :return:
    """
    check_sinogram_half(scan)
    corfinder = SinoCORFinder(
        adapt_tomwer_scan_to_nabu(scan),
        slice_idx=scan.axis_params.sinogram_line,
        subsampling=scan.axis_params.sinogram_subsampling,
        do_flatfield=True,
        cor_options=scan.axis_params.get_nabu_cor_options(),
        logger=_logger,
    )
    res = corfinder.find_cor(method=AxisMode.growing_window.value)
    # value return is absolute
    if scan.dim_1 is None:
        _logger.warning("unagle to find image width. Set half width to 1024")
        res = res - 1024
    else:
        res = res - scan.dim_1 // 2
    return res


def compute_scan_sino_coarse_to_fine(scan):
    """
    Compute center of rotation from `sino-coarse-to-fine` algorithm for given
    scan
    :param scan:
    :raises: ValueError if half acquisition with an odd number of projections
    :return:
    """
    check_sinogram_half(scan)
    corfinder = SinoCORFinder(
        adapt_tomwer_scan_to_nabu(scan),
        slice_idx=scan.axis_params.sinogram_line,
        subsampling=scan.axis_params.sinogram_subsampling,
        do_flatfield=True,
        cor_options=scan.axis_params.get_nabu_cor_options(),
        logger=_logger,
    )
    res = corfinder.find_cor(method=AxisMode.sino_coarse_to_fine.value)
    # value return is absolute
    if scan.dim_1 is None:
        _logger.warning("unagle to find image width. Set half width to 1024")
        res = res - 1024
    else:
        res = res - scan.dim_1 // 2
    return res


def compute_scan_composite_coarse_to_fine(scan: TomwerScanBase):
    """
    Compute center of rotation from `sino-coarse-to-fine` algorithm for given
    scan
    :param scan:
    :raises: ValueError if half acquisition with an odd number of projections
    :return:
    """
    if not has_composite_cor_finder:
        _logger.error("unable to find nabu CompositeCOREstimator")
        return None

    check_sinogram_half(scan)
    theta, subsampling_y, oversampling, take_log = get_composite_options(scan)
    corfinder = CompositeCOREstimator(
        adapt_tomwer_scan_to_nabu(scan),
        theta=theta,
        subsampling_y=subsampling_y,
        oversampling=oversampling,
        cor_options=scan.axis_params.get_nabu_cor_options(),
        logger=_logger,
        take_log=take_log,
    )
    res = corfinder.find_cor(method=AxisMode.composite_coarse_to_fine.value)
    # value return is absolute
    if scan.dim_1 is None:
        _logger.warning("unagle to find image width. Set half width to 1024")
        res = res - 1024
    else:
        res = res - scan.dim_1 // 2
    return res


def get_composite_options(scan):
    theta = scan.axis_params.composite_options.get("theta", DEFAULT_CMP_THETA)
    subsampling_y = scan.axis_params.composite_options.get(
        "subsampling_y", DEFAULT_CMP_SUBSAMPLING_Y
    )
    oversampling = scan.axis_params.composite_options.get(
        "oversampling", DEFAULT_CMP_OVERSAMPLING
    )
    take_log = scan.axis_params.composite_options.get("take_log", DEFAULT_CMP_TAKE_LOG)
    return theta, subsampling_y, oversampling, take_log


def compute_scan_cor_nabu_growing_window(scan):
    """
    Call to nabu.preproc.alignment.CenterOfRotation from the scan axis_params
    value.

    :param `.TomoBase` scan: scan to process
    :raises: ValueError if half acquisition with an odd number of projections
    :return: Union[float, None]
    """
    if not scan.axis_params.use_sinogram:
        radio_1, radio_2 = AxisProcess.get_inputs(scan=scan)
        if radio_1 is None or radio_2 is None:
            raise NoAxisUrl("Unable to find projections for nabu axis calculation")
    else:
        radio_1, radio_2 = None, None

    _logger.info(
        "compute scan axis from nabu CenterOfRotationGrowingWindow with padding "
        "mode {} and side {}. Use sinogram: {}".format(
            scan.axis_params.padding_mode,
            scan.axis_params.side,
            scan.axis_params.use_sinogram,
        )
    )

    if scan.axis_params.use_sinogram:
        return compute_cor_nabu_growing_window_sinogram(scan=scan)
    else:
        return compute_cor_nabu_growing_window(
            radio_1=radio_1.copy(),
            radio_2=radio_2.copy(),
            side=scan.axis_params.side,
            padding_mode=scan.axis_params.padding_mode,
            flip_frame_2_lr=scan.axis_params.flip_lr,
        )


def compute_cor_nabu_sliding_window(
    radio_1: numpy.ndarray,
    radio_2: numpy.ndarray,
    side: str,
    padding_mode,
    flip_frame_2_lr=True,
    horz_fft_width=False,
):
    """
    Call nabu.preproc.alignement.CenterOfRotationSlidingWindow.find_shift

    :param radio_1:
    :param radio_2:
    :param padding_mode:
    :param str side: side of the cor
    :param horz_fft_width:
    :param bool flip_frame_2_lr: if True will left-right flip the second frame
    :param half_acq_cor_guess: The approximate position of the rotation axis
                               from the image center. Optional. When given a
                               special algorithm is used which can work also
                               in half-tomo conditions.

    :return:
    """
    nabu_class = CenterOfRotationSlidingWindow(horz_fft_width=horz_fft_width)
    return nabu_class.find_shift(
        img_1=radio_1,
        img_2=numpy.fliplr(radio_2) if flip_frame_2_lr else radio_2,
        side=side,
        roi_yxhw=None,
        padding_mode=padding_mode,
        median_filt_shape=None,
    )


def compute_cor_nabu_sliding_window_sinogram(
    scan,
):
    """
    Call nabu.preproc.alignement.CenterOfRotationGrowingWindow.find_shift

    :param TomwerScanBase scan:
    :raises: ValueError if half acquisition with an odd number of projections

    :return:
    """
    check_sinogram_half(scan)
    corfinder = SinoCORFinder(
        adapt_tomwer_scan_to_nabu(scan),
        slice_idx=scan.axis_params.sinogram_line,
        subsampling=scan.axis_params.sinogram_subsampling,
        do_flatfield=True,
        cor_options=scan.axis_params.get_nabu_cor_options(),
        logger=_logger,
    )
    res = corfinder.find_cor(method=AxisMode.sliding_window.value)
    # value return is absolute
    if scan.dim_1 is None:
        _logger.warning("unagle to find image width. Set half width to 1024")
        res = res - 1024
    else:
        res = res - scan.dim_1 // 2
    return res


def compute_scan_cor_nabu_sliding_window(scan):
    """
    Call to nabu.preproc.alignment.CenterOfRotation from the scan axis_params
    value.

    :param `.TomoBase` scan: scan to process
    :raises: ValueError if half acquisition with an odd number of projections
    :return: Union[float, None]
    """
    if not scan.axis_params.use_sinogram:
        radio_1, radio_2 = AxisProcess.get_inputs(scan=scan)
        if radio_1 is None or radio_2 is None:
            raise NoAxisUrl("Unable to find projections for nabu axis calculation")
    else:
        radio_1 = radio_2 = None

    _logger.info(
        "compute scan axis from nabu CenterOfRotationSlidingWindow with padding "
        "mode {} and side {}. Use sinogram: {}".format(
            scan.axis_params.padding_mode,
            scan.axis_params.side,
            scan.axis_params.use_sinogram,
        )
    )

    if scan.axis_params.use_sinogram:
        return compute_cor_nabu_sliding_window_sinogram(scan=scan)
    else:
        return compute_cor_nabu_sliding_window(
            radio_1=radio_1.copy(),
            radio_2=radio_2.copy(),
            side=scan.axis_params.side,
            padding_mode=scan.axis_params.padding_mode,
            flip_frame_2_lr=scan.axis_params.flip_lr,
        )


def compute_cor_nabu_centered(
    radio_1: numpy.ndarray,
    radio_2: numpy.ndarray,
    padding_mode,
    flip_frame_2_lr=True,
    horz_fft_width=False,
):
    """
    Call nabu.preproc.alignement.CenterOfRotation.find_shift

    :param radio_1:
    :param radio_2:
    :param padding_mode:
    :param horz_fft_width:
    :param bool flip_frame_2_lr: if True will left-right flip the second frame
    :param half_acq_cor_guess: The approximate position of the rotation axis
                               from the image center. Optional. When given a
                               special algorithm is used which can work also
                               in half-tomo conditions.

    :return:
    """
    nabu_class = CenterOfRotation(horz_fft_width=horz_fft_width)
    return nabu_class.find_shift(
        img_1=radio_1,
        img_2=numpy.fliplr(radio_2) if flip_frame_2_lr else radio_2,
        roi_yxhw=None,
        padding_mode=padding_mode,
        median_filt_shape=None,
    )


def compute_scan_cor_nabu_centered(scan):
    """
    Call to nabu.preproc.alignment.CenterOfRotation from the scan axis_params
    value.

    :param `.TomoBase` scan: scan to process
    :return: Union[float, None]

    """
    assert scan.axis_params is not None
    radio_1, radio_2 = AxisProcess.get_inputs(scan=scan)
    if radio_1 is None or radio_2 is None:
        raise NoAxisUrl("Unable to find projections for nabu axis calculation")

    _logger.info(
        "compute scan axis from nabu CenterOfRotation with padding "
        "mode %s" % scan.axis_params.padding_mode
    )

    return compute_cor_nabu_centered(
        radio_1=radio_1.copy(),
        radio_2=radio_2.copy(),
        padding_mode=scan.axis_params.padding_mode,
        flip_frame_2_lr=scan.axis_params.flip_lr,
    )


def compute_cor_nabu_global(
    radio_1: numpy.ndarray,
    radio_2: numpy.ndarray,
    padding_mode,
    flip_frame_2_lr=True,
    horz_fft_width=False,
):
    """
    Call nabu.preproc.alignement.CenterOfRotation.find_shift

    :param radio_1:
    :param radio_2:
    :param padding_mode:
    :param horz_fft_width:
    :param bool flip_frame_2_lr: if True will left-right flip the second frame
    :return:
    """
    nabu_class = CenterOfRotationAdaptiveSearch(horz_fft_width=horz_fft_width)
    return nabu_class.find_shift(
        img_1=radio_1,
        img_2=numpy.fliplr(radio_2) if flip_frame_2_lr else radio_2,
        roi_yxhw=None,
        padding_mode=padding_mode,
        median_filt_shape=None,
    )


def compute_scan_cor_nabu_global(scan):
    """
    Call to nabu.preproc.alignment.CenterOfRotation from the scan axis_params
    value.

    :param `.TomoBase` scan: scan to process
    :return: Union[float, None]

    """
    assert scan.axis_params is not None
    radio_1, radio_2 = AxisProcess.get_inputs(scan=scan)
    if radio_1 is None or radio_2 is None:
        raise NoAxisUrl("Unable to find projections for nabu axis calculation")

    _logger.info(
        "compute scan axis from nabu CenterOfRotation with padding "
        "mode %s" % scan.axis_params.padding_mode
    )

    return compute_cor_nabu_global(
        radio_1=radio_1.copy(),
        radio_2=radio_2.copy(),
        padding_mode=scan.axis_params.padding_mode,
        flip_frame_2_lr=scan.axis_params.flip_lr,
    )


def get_stdmax_column(x: numpy.ndarray) -> float:
    """

    :param x:
    :return: column index of the maximal standard deviation
    """
    kernel_size = 5
    length = len(x)
    r = range(length - kernel_size)
    y = numpy.empty(length - kernel_size)
    for i in r:
        s = numpy.std(x[i : i + kernel_size])
        y[i] = s

    return y.argmax()


class NoAxisUrl(Exception):
    pass


class AxisProcess(
    Task, SuperviseProcess, input_names=("data",), output_names=("data",)
):
    """
    Process used to compute the center of rotation of a scan

    :param axis_params: parameters to configure the axis process
    :type: AxisRP
    """

    _CALCULATIONS_METHODS = {
        AxisMode.centered: compute_scan_cor_nabu_centered,
        AxisMode.global_: compute_scan_cor_nabu_global,
        AxisMode.sliding_window: compute_scan_cor_nabu_sliding_window,
        AxisMode.growing_window: compute_scan_cor_nabu_growing_window,
        AxisMode.sino_coarse_to_fine: compute_scan_sino_coarse_to_fine,
        AxisMode.composite_coarse_to_fine: compute_scan_composite_coarse_to_fine,
    }

    def __init__(self, process_id=None, varinfo=None, inputs=None, label=None):
        Task.__init__(self, varinfo=varinfo, inputs=inputs, label=label)
        if "recons_params" in inputs:
            raise KeyError("do not use 'recons_params' but use 'axis_params' instead")
        axis_params = inputs.get("axis_params", None)
        if isinstance(axis_params, dict):
            axis_params = AxisRP.from_dict(axis_params)
        elif not (axis_params is None or isinstance(axis_params, AxisRP)):
            raise TypeError(
                "'axis_params' is expected to be None or an instance of AxisRP or a dict"
            )

        SuperviseProcess.__init__(self, process_id=process_id)
        self._mode_calculation_fct = {}
        """dict with function pointer to call for making the mode calculation.
        Function should have only one 'scan' parameter as input"""

        self._axis_params = axis_params or AxisRP()
        """Axis reconstruction parameters to apply"""
        self._locked = False
        """Boolean used to lock reconstruction parameters edition"""
        self._recons_params_before_lock = None
        """Recons parameters register before locking the position"""

    def set_configuration(self, configuration):
        self.set_recons_params(
            recons_params=AxisRP.from_dict(configuration["_rpSetting"])
        )

    def set_recons_params(self, recons_params):
        assert isinstance(recons_params, AxisRP)
        self._axis_params = recons_params

    def lock_position_value(self, lock=True):
        """
        lock the position currently computed or defined by the user.
        In this case we will lock the axis as defined 'fixed' with the current
        value

        :param bool lock: if true lock the currently existing position value
        """
        self._locked = lock
        if lock:
            self._recons_params_before_lock = self._axis_params.to_dict()
            if self._axis_params not in (AxisMode.manual, AxisMode.read):
                self._axis_params.mode = AxisMode.manual
        else:
            if self._recons_params_before_lock:
                self._axis_params.load_from_dict(
                    self._recons_params_before_lock
                )  # noqa

    def run(self):
        """
        Compute the position value then get ready to the next. And call

        .. note:: this simply call `compute`.
                  But this is needed for the AxisProcessThreaded class
        """
        scan = self.inputs.data
        if scan is None:
            return

        if isinstance(scan, TomwerScanBase):
            scan = scan
        elif isinstance(scan, dict):
            scan = ScanFactory.create_scan_object_frm_dict(scan)
        else:
            raise ValueError("input type {} is not managed".format(scan))

        _logger.info("start axis calculation for %s" % scan.path)
        self._axis_params.frame_width = scan.dim_1
        cor = error = None
        try:
            scan_res = self.compute(scan=scan)
        except Exception as e:
            raise e
            scan_res = None
            error = e
        else:
            if isinstance(scan_res, TomwerScanBase):
                cor = scan_res.axis_params.relative_cor_value
            elif scan_res is None:
                if scan.axis_params.relative_cor_value is not None:
                    cor = scan.axis_params.relative_cor_value
            elif isinstance(scan_res, float):
                cor = scan_res
            else:
                assert isinstance(scan_res, dict)
                b_dict = scan_res
                if TomwerScanBase._DICT_AXIS_KEYS in scan_res:
                    b_dict = scan_res["axis_params"]
                cor = b_dict["POSITION_VALUE"]
        finally:
            if cor != "...":
                self._process_end(scan, cor=cor, error=error)
        self.outputs.data = scan_res

    def reprocess(self, scan):
        """
        Reprocess the scan. For now simply call process

        :param scan:
        """
        return self.process(scan=scan)

    def _process_end(self, scan, cor, error=None):
        assert isinstance(scan, TomwerScanBase)
        if scan.process_file is not None:
            entry = "entry"
            if isinstance(scan, HDF5TomoScan):
                entry = scan.entry
            with scan.acquire_process_file_lock():
                self.register_process(
                    process_file=scan.process_file,
                    entry=entry,
                    results={"center_of_rotation": cor if cor is not None else "-"},
                    configuration=self._axis_params.to_dict(),
                    process_index=scan.pop_process_index(),
                    overwrite=True,
                )

        try:
            extra = {
                logconfig.DOC_TITLE: self._scheme_title,
                logconfig.SCAN_ID: scan.path,
            }
            if error is not None:
                info = " ".join(
                    (
                        "fail to compute axis position for scan",
                        str(scan.path),
                        "reason is ",
                        str(error),
                    )
                )
                _logger.processFailed(info, extra=extra)
                ProcessManager().notify_dataset_state(
                    dataset=scan, process=self, state=DatasetState.FAILED, details=info
                )
            elif scan.axis_params.relative_cor_value is None:
                info = " ".join(
                    ("fail to compute axis position for scan", str(scan.path))
                )
                _logger.processFailed(info, extra=extra)
                ProcessManager().notify_dataset_state(
                    dataset=scan, process=self, state=DatasetState.FAILED, details=info
                )
            else:
                info = "axis calculation defined for {}: {} (using {})" "".format(
                    str(scan.path),
                    str(scan.axis_params.relative_cor_value),
                    scan.axis_params.mode.value,
                )
                _logger.processSucceed(info, extra=extra)
                ProcessManager().notify_dataset_state(
                    dataset=scan, process=self, state=DatasetState.SUCCEED, details=info
                )
        except Exception as e:
            _logger.error(e)

    @staticmethod
    def get_inputs_urls(scan):
        """Make sure we have valid projections to be used for axis calculation

        :param TomwerScanBase scan: scan to check
        :raise: NoAxisUrl if fails to found
        :return: the two projections to be used for axis calculation
        :rtype: tuple of AxisResource
        """
        if (
            scan.axis_params
            and scan.axis_params.axis_url_1
            and scan.axis_params.axis_url_1.url
        ):
            return scan.axis_params.axis_url_1, scan.axis_params.axis_url_2
        else:
            _radio_1, _radio_2 = scan.getRadiosForAxisCalc(
                mode=CorAngleMode.manual_selection
            )
        return _radio_1, _radio_2

    @staticmethod
    def get_inputs(scan):
        assert isinstance(scan, TomwerScanBase)
        radio_1, radio_2 = AxisProcess.get_inputs_urls(scan=scan)
        if radio_1 and radio_2:
            mess = " ".join(
                ("input radios are", radio_1.url.path(), "and", radio_2.url.path())
            )
            _logger.info(mess)
            log_ = scan.axis_params.projection_type is ProjectionType.transmission

            # if necessary normalize data
            if radio_1.normalized_data is None:
                radio_1.normalize_data(scan, log_=log_)
            if radio_2.normalized_data is None:
                radio_2.normalize_data(scan, log_=log_)

            if scan.axis_params.paganin_preproc:
                data_1 = radio_1.normalized_data_paganin
                data_2 = radio_2.normalized_data_paganin
            else:
                data_1 = radio_1.normalized_data
                data_2 = radio_2.normalized_data

            if scan.axis_params.scale_img2_to_img1:
                data_2 = image.scale_img2_to_img1(img_1=data_1, img_2=data_2)
            return data_1, data_2
        else:
            _logger.info("fail to find any inputs")
            return None, None

    def compute(self, scan, wait=True):
        """
        Compute the position value for the scan

        :param TomwerScanBase scan:
        :param bool wait: used for threaded process. True if we want to end the
                          computation before releasing hand.
        :return: scan as a TomoBase
        """
        assert scan is not None
        if isinstance(scan, dict):
            _logger.warning("convert scan from a dict")
            _scan = ScanFactory.create_scan_object_frm_dict(scan)
        else:
            _scan = scan
        assert isinstance(_scan, TomwerScanBase)
        # if the scan has no tomo reconstruction parameters yet create them
        if _scan.axis_params is None:
            _scan.axis_params = AxisRP()

        # copy axis recons parameters. We skip the axis_url which are specific
        # to the scan
        _scan.axis_params.copy(
            self._axis_params, copy_axis_url=False, copy_flip_lr=False
        )
        assert scan.axis_params is not None
        return self._process_computation(scan=_scan)

    def scan_ready(self, scan):
        _logger.info(scan, "processed")

    def _process_computation(self, scan):
        """

        :param TomwerScanBase scan: scan for which we want to compute the axis
                              position.
        :return: scan as a TomoBase or a dict if _return_dict activated
        """
        _logger.info("compute center of rotation for %s" % scan.path)
        try:
            position = self.compute_axis_position(scan)
        except NotImplementedError as e:
            scan.axis_params.set_relative_value(None)
            raise e
        except ValueError as e:
            scan_name = scan.path or "undef scan"
            scan.axis_params.set_relative_value(None)
            raise Exception(
                "Fail to compute axis position for {} reason is {}"
                "".format(scan_name, e)
            )
        else:
            scan.axis_params.set_relative_value(position)
            self._axis_params.frame_width = scan.dim_1
            self._axis_params.set_relative_value(position)
            scan_name = scan.path or "undef scan"
            if scan.axis_params.use_sinogram:
                method = "sinogram"
            else:
                method = scan.axis_params.mode.value
            mess = (
                "Compute axis position ({value}) with {method} for {scan_name}".format(
                    value=str(scan.axis_params.relative_cor_value),
                    method=method,
                    scan_name=scan_name,
                )
            )
            _logger.info(mess)
        if self._return_dict:
            return scan.to_dict()
        else:
            return scan

    def setMode(self, mode, value):
        if mode is AxisMode.manual:
            self._axis_params.cor_position = value
        else:
            raise NotImplementedError("mode not implemented yet")

    def define_calculation_mode(self, mode, fct_pointer):
        """Register the function to call of the given mode

        :param AxisMode mode: the mode to register
        :param fct_pointer: pointer to the function to call
        """
        self._mode_calculation_fct[mode] = fct_pointer

    def compute_axis_position(self, scan):
        """

        :param scan: scan for which we compute the center of rotation
        :type: TomoScan
        :return: position of the rotation axis. Use the `.AxisMode` defined
                 by the `.ReconsParams` of the `.AxisProcess`
        :rtype: float or None (if fail to compute the axis position)
        """
        mode = self._axis_params.mode
        if mode in (AxisMode.manual, AxisMode.read):
            # If mode is read or manual the position_value is not computed and
            # we will keep the actual one (should have been defined previously)
            res = self._axis_params.relative_cor_value
        elif mode in self._CALCULATIONS_METHODS:
            _logger.info("use radios, mode is %s" % mode.value)
            res = self._CALCULATIONS_METHODS[mode](scan)
        else:
            raise NotImplementedError("Method for", mode, "is not defined")
        return res

    @docstring(Task.program_name)
    @staticmethod
    def program_name():
        return "tomwer_axis"

    @docstring(Task.program_version)
    @staticmethod
    def program_version():
        return tomwer.version.version

    @docstring(Task.definition)
    @staticmethod
    def definition():
        return "Compute center of rotation"

    @staticmethod
    def get_cor_frm_process_file(
        process_file, entry, as_url=False
    ) -> Union[None, float]:
        """
        Read cor position from a tomwer_process file

        :param process_file:
        :param entry:
        :return:
        """
        if entry is None:
            with HDF5File(process_file, "r", swmr=True) as h5f:
                entries = AxisProcess._get_process_nodes(
                    root_node=h5f, process=AxisProcess
                )
                if len(entries) == 0:
                    _logger.info("unable to find a Axis process in %s" % process_file)
                    return None
                elif len(entries) > 1:
                    raise ValueError("several entry found, entry should be " "specify")
                else:
                    entry = list(entries.keys())[0]
                    _logger.info("take %s as default entry" % entry)

        with HDF5File(process_file, "r", swmr=True) as h5f:
            axis_nodes = AxisProcess._get_process_nodes(
                root_node=h5f[entry], process=AxisProcess
            )
            index_to_path = {}
            for key, index in axis_nodes.items():
                index_to_path[index] = key

            if len(axis_nodes) == 0:
                return None
            # take the last processed dark ref
            last_process_index = sorted(list(axis_nodes.values()))[-1]
            last_process_dark = index_to_path[last_process_index]
            if (len(index_to_path)) > 1:
                _logger.debug(
                    "several processing found for dark-ref,"
                    "take the last one: %s" % last_process_dark
                )

            res = None
            if "results" in h5f[last_process_dark].keys():
                results_node = h5f[last_process_dark]["results"]
                if "center_of_rotation" in results_node.keys():
                    if as_url:
                        res = DataUrl(
                            file_path=process_file,
                            data_path="/".join((results_node, "center_of_rotation")),
                            scheme="h5py",
                        )
                    else:
                        res = h5py_read_dataset(results_node["center_of_rotation"])
            return res
