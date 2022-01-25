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
__date__ = "04/03/2019"

import tomwer.core.process.reconstruction.axis
from ..utils import WidgetLongProcessing
from orangewidget import gui
from orangecontrib.tomwer.orange.managedprocess import SuperviseOW
from orangewidget.settings import Setting
from orangecontrib.tomwer.orange.settings import CallbackSettingsHandler
from orangewidget.widget import Input, Output
from processview.gui.processmanager import ProcessManager
from processview.core.manager import DatasetState
from processview.core import helpers as pv_helpers
from tomwer.core.process.reconstruction.axis.mode import AxisMode
from tomwer.synctools.stacks.reconstruction.axis import AxisProcessStack
from tomwer.core.process.reconstruction.axis import AxisProcess
from tomwer.synctools.axis import QAxisRP
from tomwer.gui.reconstruction.axis import AxisWindow
from tomwer.core.scan.scanbase import TomwerScanBase
from tomwer.core.scan.hdf5scan import HDF5TomoScan
from tomwer.core.scan.scanbase import _TomwerBaseDock
from silx.gui import qt
from tomwer.core import settings
from tomwer.core import utils
import functools
import copy

import logging

logger = logging.getLogger(__name__)


class AxisOW(SuperviseOW, WidgetLongProcessing):
    """
    Widget used to defined the center of rotation axis to be used for a
    reconstruction.

    :param bool _connect_handler: True if we want to store the modifications
                      on the setting. Need for unit test since
                      keep alive qt widgets.
    """

    name = "default center of rotation"
    id = "orange.widgets.tomwer.axis"
    description = "use to compute the center of rotation"
    icon = "icons/axis.png"
    priority = 14
    keywords = [
        "tomography",
        "axis",
        "tomwer",
        "reconstruction",
        "rotation",
        "position",
        "center of position",
    ]

    ewokstaskclass = tomwer.core.process.reconstruction.axis.AxisProcess

    want_main_area = True
    resizing_enabled = True
    allows_cycle = True
    compress_signal = False

    settingsHandler = CallbackSettingsHandler()

    sigScanReady = qt.Signal(TomwerScanBase)
    """Signal emitted when a scan is ready"""

    _rpSetting = Setting(dict())
    "AxisRP store as dict"
    # this one is keep for backward compatibility. Will be removed on 0.10 I guess

    static_input = Setting({"data": None, "axis_params": None})

    class Inputs:
        data = Input(name="data", type=TomwerScanBase, doc="one scan to be process")
        data_recompute_axis = Input(
            name="change recons params",
            type=_TomwerBaseDock,
            doc="recompute delta / beta",
        )

    class Outputs:
        data = Output(name="data", type=TomwerScanBase, doc="one scan to be process")

    def __init__(self, parent=None, axis_params=None):
        """

        :param parent: QWidget parent or None
        :param _connect_handler: used for CI, because if connected fails CI
        :param QAxisRP axis_params: reconstruction parameters
        """
        if axis_params is not None:
            if not isinstance(axis_params, QAxisRP):
                raise TypeError(
                    "axis_params should be an instance of "
                    "QAxisRP. Not {}".format(type(axis_params))
                )
        self._axis_params = axis_params or QAxisRP()

        # handle settings
        axis_params_settings = self.static_input.get("axis_params", None)
        if axis_params_settings is None:
            axis_params_settings = self._rpSetting
        if axis_params_settings != dict():
            try:
                self._axis_params.load_from_dict(axis_params_settings)
            except Exception as e:
                logger.error("fail to load reconstruction settings:", str(e))
        gui_settings = self.static_input.get("gui", None)
        if gui_settings is None:
            gui_settings = self._rpSetting.get("gui", {})

        self.__lastAxisProcessParamsCache = None
        # used to memorize the last (reconstruction parameters, scan)
        self.__scan = None
        self.__skip_exec = False
        self._n_skip = 0
        self._patches = []
        """patches for processing"""

        WidgetLongProcessing.__init__(self)
        SuperviseOW.__init__(self, parent)
        self._processingStack = AxisProcessStack(
            axis_params=self._axis_params, process_id=self.process_id
        )

        self._widget = AxisWindow(parent=self, axis_params=self._axis_params)

        self._layout = gui.vBox(self.mainArea, self.name).layout()
        self._layout.setContentsMargins(0, 0, 0, 0)

        self._layout.addWidget(self._widget)

        # expose API
        self.setMode = self._widget.setMode
        self.getRadioMode = self._widget.getRadioMode
        self.getEstimatedCor = self._widget.getEstimatedCor
        self.getAxis = self._widget.getAxis
        self.setValueLock = self._widget.setValueLock
        self._setModeLockFrmSettings = self._widget._setModeLockFrmSettings
        self._setValueLockFrmSettings = self._widget._setValueLockFrmSettings

        # load settings
        if "mode_is_lock" in gui_settings:
            mode_lock = gui_settings["mode_is_lock"]
            # if the mode is manual or read ignore lock
            if not (
                mode_lock is True
                and self.getRadioMode() in (AxisMode.manual, AxisMode.read)
            ):
                self._setModeLockFrmSettings(mode_lock)

        if "value_is_lock" in gui_settings:
            if gui_settings["value_is_lock"] is True:
                self._setValueLockFrmSettings(bool(gui_settings["value_is_lock"]))
        # expose API
        self._applyBut = self._widget._axisWidget._controlWidget._applyBut
        # connect Signal / Slot
        self._widget.sigComputationRequested.connect(self.__compute)
        self._widget.sigApply.connect(self.__validate)
        self._widget.sigAxisEditionLocked.connect(self.__lockReconsParams)
        self._processingStack.sigComputationStarted.connect(self._processingStart)
        self._processingStack.sigComputationEnded.connect(self._scanProcessed)

        self._axis_params.sigChanged.connect(self._updateSettingsVals)
        self._widget.sigAxisEditionLocked.connect(self._updateSettingsVals)
        self._widget.sigMethodChanged.connect(self._updateSettingsVals)
        self._widget.sigLockModeChanged.connect(self._updateSettingsVals)

    def _processingStart(self, *args, **kwargs):
        WidgetLongProcessing._startProcessing(self)

    def _scanProcessed(self, scan, future_scan):
        assert isinstance(scan, TomwerScanBase)
        WidgetLongProcessing._endProcessing(self, scan)
        if self.isValueLock() or self.isModeLocked():
            self.__scan = scan
            self.__validate()
        else:
            pm = ProcessManager()
            # handle previous scan if not validated yey: skip it
            if (
                self.__scan is not None
                and pm.get_dataset_state(dataset=self.__scan, process=self)
                != DatasetState.SUCCEED
            ):
                pm.notify_dataset_state(
                    dataset=self.__scan,
                    process=self,
                    state=DatasetState.SKIPPED,
                    details="Scan was waiting for validation. Has been replaced by another scan. No scan stack on Axis process",
                )

            # handle the new scan
            # retrieve details to keep them in `memory`
            self.__scan = scan
            details = pm.get_dataset_details(dataset=self.__scan, process=self)
            details = "Wait for user validation. " + details
            pm.notify_dataset_state(
                dataset=self.__scan,
                process=self,
                state=DatasetState.WAIT_USER_VALIDATION,
                details=details,
            )
            self.activateWindow()
            self.raise_()
            self.show()

    def __compute(self):
        if self.__scan:
            dict_for_cache = self._axis_params.to_dict().copy()
            dict_for_cache.pop("POSITION_VALUE")
            params_cache = (
                dict_for_cache,
                str(self.__scan),
            )
            # check mode is not locked or manual and value is still here
            if (
                params_cache == self.__lastAxisProcessParamsCache
            ) and self._processingStack.is_computing():
                logger.error(
                    "Parameters and scan are the same as last request. Please wait until the processing is done."
                )
            else:
                self.__lastAxisProcessParamsCache = params_cache
                callback = functools.partial(self._updatePosition, self.__scan)
                self._processingStack.add(
                    scan=self.__scan,
                    configuration=self._axis_params.to_dict(),
                    callback=callback,
                )

    def __validate(self):
        """Validate the current scan and move the scan to the next process.
        The Axis will process the next scan in the stack.
        """
        if self.__scan:
            if self.getRadioMode() is AxisMode.manual:
                if (
                    self.__scan._axis_params.frame_width is None
                    and self.__scan.dim_1 is not None
                ):
                    self.__scan._axis_params.frame_width = self.__scan.dim_1

                self.__scan._axis_params.set_relative_value(
                    self._axis_params.relative_cor_value
                )
                pv_helpers.notify_succeed(
                    process=self,
                    dataset=self.__scan,
                    details="axis calculation defined for {}: {} (using {})"
                    "".format(
                        str(self.__scan.path),
                        str(self.__scan.axis_params.relative_cor_value),
                        "manual",
                    ),
                )
            # validate the center of rotation
            pm = ProcessManager()
            # retrieve details to keep them in memory
            details = pm.get_dataset_details(dataset=self.__scan, process=self)
            state = pm.get_dataset_state(dataset=self.__scan, process=self)
            if state in (DatasetState.ON_GOING, DatasetState.WAIT_USER_VALIDATION):
                # update the state to SUCCEED
                ProcessManager().notify_dataset_state(
                    dataset=self.__scan,
                    process=self,
                    state=DatasetState.SUCCEED,
                    details=details,
                )
            self.accept()
            self.scan_ready(scan=self.__scan)
        self.hide()

    def __lockReconsParams(self, lock):
        self.lock_position_value(lock)

    def scan_ready(self, scan):
        assert isinstance(scan, TomwerScanBase)
        self.Outputs.data.send(scan)
        self.sigScanReady.emit(scan)

    def _informNoProjFound(self, scan):
        msg = qt.QMessageBox(self)
        msg.setIcon(qt.QMessageBox.Warning)
        text = (
            "Unable to find url to compute the axis of `%s`" % scan.path
            or "no path given"
        )
        text += ", please select them from the `axis input` tab"
        msg.setText(text)
        msg.exec_()

    def _updateSettingsVals(self):
        self._rpSetting = self._axis_params.to_dict()
        self._rpSetting["gui"] = {
            "mode_is_lock": self.isModeLocked(),
            "value_is_lock": self.isValueLock(),
        }
        self.static_input = {
            "data": None,
            "axis_params": self._axis_params.to_dict(),
            "gui": {
                "mode_is_lock": self.isModeLocked(),
                "value_is_lock": self.isValueLock(),
            },
        }

    def _skip_exec(self, b):
        """util function used for unit test. If activate, skip the call to
        self.exec() in process"""
        self.__skip_exec = b

    @property
    def recons_params(self):
        return self._axis_params

    def _instanciateReconsParams(self):
        return QAxisRP()

    def _lock_axis_controls(self, lock):
        """

        :param bool lock: lock the axis controls to avoid modification of the
                          requested options, method... of the axis calculation
                          when this value is under calculation.
        """
        self._widget.setLocked(lock)

    def isValueLock(self):
        """
        Check if the cor value has been lock. If so we simply copy the cor
        value and move to the next scan
        """
        return self._widget.isValueLock()

    def isModeLocked(self):
        """
        Check if the mode has been lock or not. If lock then call the
        algorithm and does not wait for any user feedback
        """
        return self._widget.isModeLock()

    @Inputs.data
    def new_data_in(self, scan):
        if scan is None:
            return
        scan_ = copy.copy(scan)
        if not (
            settings.isOnLbsram(scan)
            and utils.isLowOnMemory(settings.get_lbsram_path())
        ):
            set_position = False  # avoid shift reset
            self._widget.setScan(scan=scan_, set_position=set_position)
        elif scan_.axis_params is None:
            scan_.axis_params = QAxisRP()
        self.process(scan=scan_)

    def process(self, scan):
        if scan is None:
            return
        self.__scan = scan
        self._axis_params.frame_width = scan.dim_1
        if (
            settings.isOnLbsram(scan)
            and utils.isLowOnMemory(settings.get_lbsram_path()) is True
        ):
            self._updatePosition(scan=scan)
            self.scan_ready(scan=scan)
        elif self.__skip_exec:
            self._n_skip += 1
            if self.isValueLock():
                scan._axis_params.set_relative_value(
                    self._axis_params.relative_cor_value
                )
                cor = scan._axis_params.relative_cor_value
                if isinstance(scan, HDF5TomoScan):
                    entry = scan.entry
                else:
                    entry = "entry"
                with scan.acquire_process_file_lock():
                    ap = AxisProcess(
                        process_id=self.process_id,
                        inputs={
                            "data": None,
                        },
                    )
                    try:
                        AxisProcess._register_process(
                            process_file=scan.process_file,
                            entry=entry,
                            process=ap,
                            results={
                                "center_of_rotation": cor if cor is not None else "-"
                            },
                            configuration=self._axis_params.to_dict(),
                            process_index=scan.pop_process_index(),
                            overwrite=True,
                        )
                    except Exception as e:
                        logger.warning(f"Fail to register Axis process. Error is {e}")
                    ProcessManager().notify_dataset_state(
                        dataset=scan,
                        process=ap,
                        state=DatasetState.SUCCEED,
                    )
            else:
                processing_class = AxisProcess(
                    inputs={
                        "axis_params": self._axis_params,
                        "data": self.__scan,
                    }
                )
                for patch in self._patches:
                    mode, function = patch
                    processing_class._CALCULATIONS_METHODS[mode] = function
                processing_class.run()
            self._updatePosition(scan=self.__scan)
            if self.isModeLocked() or self.isValueLock():
                self.scan_ready(scan=scan)

        elif self.isValueLock():
            entry = scan.entry if isinstance(scan, HDF5TomoScan) else "entry"
            cor = self._axis_params.relative_cor_value
            scan.axis_params.set_relative_value(cor)
            scan._axis_params.mode = "manual"
            try:
                AxisProcess._register_process(
                    process_file=scan.process_file,
                    entry=entry,
                    process=AxisProcess,
                    results={"center_of_rotation": cor if cor is not None else "-"},
                    configuration=self._axis_params.to_dict(),
                    process_index=scan.pop_process_index(),
                    overwrite=True,
                )
            except Exception as e:
                logger.warning(f"Fail to register Axis process. Error is {e}")
            ProcessManager().notify_dataset_state(
                dataset=scan,
                process=AxisProcess(
                    process_id=self.process_id,
                    inputs={
                        "data": None,
                    },
                ),
                state=DatasetState.SUCCEED,
            )
            self.scan_ready(scan=scan)

        elif self.isModeLocked():
            callback = functools.partial(self._updatePosition, scan)
            self._processingStack.add(
                scan=scan, configuration=self._axis_params.to_dict(), callback=callback
            )
        else:
            self.activateWindow()
            self.raise_()
            self.show()

    def _updatePosition(self, scan):
        if scan.axis_params is not None:
            self._widget.setPosition(
                frm=None, value=scan.axis_params.relative_cor_value
            )

    @Inputs.data_recompute_axis
    def reprocess(self, scan):
        """Recompute the axis for scan"""
        if scan is not None:
            # for now The behavior for reprocessing is the sama as for processing
            if hasattr(scan, "instance"):
                self.process(scan=scan.instance)
            else:
                self.process(scan=scan)

    def close(self):
        self._processingStack.stop()
        self._processingStack.wait_computation_finished()
        self._widget = None
        self._processingStack = None
        super().close()

    def patch_calc_method(self, mode, function):
        self._patches.append((mode, function))

    def keyPressEvent(self, event):
        """The event has to be filtered since we have some children
         that can be edited using the 'enter' key as defining the cor manually
        (see #481)). As we are in a dialog this automatically trigger
        'accepted'. See https://forum.qt.io/topic/5080/preventing-enter-key-from-triggering-ok-in-qbuttonbox-in-particular-qlineedit-qbuttonbox/5
        """
        if event.key() != qt.Qt.Key_Enter:
            super().keyPressEvent(event)
