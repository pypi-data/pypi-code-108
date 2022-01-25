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
__date__ = "04/05/2021"


from tomwer.gui.reconstruction.nabu import check
from ..utils import WidgetLongProcessing
from orangewidget import gui
from orangecontrib.tomwer.orange.managedprocess import SuperviseOW
from orangewidget.settings import Setting
from orangecontrib.tomwer.orange.settings import CallbackSettingsHandler
from orangewidget.widget import Input, Output
from tomwer.core.process.reconstruction.sadeltabeta import SADeltaBetaProcess
from tomwer.synctools.stacks.reconstruction.sadeltabeta import SADeltaBetaProcessStack
from tomwer.synctools.sadeltabeta import QSADeltaBetaParams
from tomwer.synctools.axis import QAxisRP
from silx.gui import qt
from tomwer.gui.reconstruction.sadeltabeta import (
    SADeltaBetaWindow as _SADeltaBetaWindow,
)
from tomwer.core.scan.scanbase import TomwerScanBase, _TomwerBaseDock
from processview.core.manager import ProcessManager, DatasetState
import tomwer.core.process.reconstruction.sadeltabeta.sadeltabeta
from tomwer.core import settings
from tomwer.core import utils
from tomwer.core.cluster import SlurmClusterConfiguration
from tomwer.core.scan.futurescan import FutureTomwerScan
from tomwer.core.scan.hdf5scan import HDF5TomoScan
from processview.core import helpers as pv_helpers
import functools
import logging

_logger = logging.getLogger(__name__)


class SADeltaBetaWindow(_SADeltaBetaWindow):
    def __init__(self, Outputs, parent=None, process_id=None):
        _SADeltaBetaWindow.__init__(self, parent=parent)
        self.Outputs = Outputs
        self._sa_delta_beta_params = QSADeltaBetaParams()
        self._processing_stack = SADeltaBetaProcessStack(
            sa_delta_beta_params=self._sa_delta_beta_params, process_id=process_id
        )
        self._clusterConfig = None

    def setClusterConfig(self, cluster_config: dict):

        if not isinstance(
            cluster_config, (dict, type(None), SlurmClusterConfiguration)
        ):
            raise TypeError(
                f"cluster config is expected to be None, dict, {SlurmClusterConfiguration} not {type(cluster_config)}"
            )
        self._clusterConfig = cluster_config

    def _launchReconstructions(self):
        """callback when we want to launch the reconstruction of the
        slice for n cor value"""
        scan = self.getScan()
        if scan is None:
            return
        # step1: if isAutoFocus: validate automatically the scan
        # step2: update the interface if the current scan is the one displayed
        # else skip it
        callback = functools.partial(
            self._mightUpdateResult, scan, self.isAutoFocusLock()
        )
        self._processing_stack.add(
            scan=scan, configuration=self.getConfiguration(), callback=callback
        )

    def _validate(self):
        self.validateCurrentScan()

    def _mightUpdateResult(self, scan: TomwerScanBase, validate: bool):
        if not isinstance(scan, TomwerScanBase):
            raise TypeError("scan is expected to be an instance of TomwerScanBase")
        if not isinstance(validate, bool):
            raise TypeError("validate is expected to be a boolean")
        if scan == self.getScan():
            self.setDBScores(
                scan.sa_delta_beta_params.scores,
                score_method=scan.sa_delta_beta_params.score_method,
            )
            if scan.sa_delta_beta_params.autofocus is not None:
                self.setCurrentDeltaBetaValue(scan.sa_delta_beta_params.autofocus)
            ProcessManager().notify_dataset_state(
                dataset=scan,
                process=self._processing_stack,
                details="processing done. Wait for user validation",
                state=DatasetState.WAIT_USER_VALIDATION,
            )
        if validate:
            self.validateScan(scan)

    def wait_processing(self, wait_time):
        self._processing_stack._computationThread.wait(wait_time)

    def validateCurrentScan(self):
        return self.validateScan(self.getScan())

    def validateScan(self, scan):
        if scan is None:
            return
        assert isinstance(scan, TomwerScanBase)
        selected_db_value = self.getCurrentDeltaBetaValue()
        if selected_db_value is None:
            infos = "no selected delta / beta value. {} skip SADeltaBetaParams".format(
                scan
            )
            _logger.warning(infos)
            scan.sa_delta_beta_params.set_db_selected_value(None)
            pv_helpers.notify_skip(
                process=self._processing_stack, dataset=scan, details=infos
            )
        else:
            scan.sa_delta_beta_params.set_db_selected_value(selected_db_value)
            infos = "delta / beta selected for {}: {},".format(
                scan, scan.sa_delta_beta_params.value
            )
            pv_helpers.notify_succeed(
                process=self._processing_stack, dataset=scan, details=infos
            )
        SADeltaBetaProcess.process_to_tomwer_processes(
            scan=scan,
        )
        self.Outputs.data.send(scan)

    def getConfiguration(self) -> dict:
        config = super().getConfiguration()
        config["cluster_config"] = self._clusterConfig
        return config

    def setConfiguration(self, config: dict):
        # ignore slurm cluster. Defined by the upper widget
        config.pop("cluster_config", None)
        return super().setConfiguration(config)


class SADeltaBetaOW(SuperviseOW, WidgetLongProcessing):
    """
    Widget for semi-automatic delta / beta calculation

    behavior within a workflow:
    * no delta / beta value will be loaded even if an "axis" window exists on
    the upper stream.
    * if autofocus option is lock:
       * launch the series of reconstruction (with research width defined)
         and the estimated center of rotation if defined. Once the
         reconstruction is ended and if the autofocus button is still lock
         it will select the cor with the highest
         value and mode to workflow downstream.
    * hint: you can define a "multi-step" half-automatic center of rotation
       research by creating several "sa_delta_beta" widget and reducing the research
       width.

    Details about :ref:`sadeltabeta score calculation`
    """

    name = "semi automatic delta/beta calculation"
    id = "orange.widgets.tomwer.sa_delta_beta"
    description = (
        "compute several delta / beta value to get the optimal "
        "delta / beta value (before reconstructing a volume for "
        "example."
    )
    icon = "icons/delta_beta_range.png"
    priority = 22
    keywords = [
        "tomography",
        "semi automatic",
        "half automatic",
        "axis",
        "delta-beta",
        "delta/beta",
        "delta",
        "beta",
        "tomwer",
        "reconstruction",
        "position",
        "center of rotation",
        "sadeltabetaaxis",
        "sa_delta_beta_axis",
        "sa_delta_beta",
        "sadeltabeta",
    ]

    ewokstaskclass = (
        tomwer.core.process.reconstruction.sadeltabeta.sadeltabeta.SADeltaBetaProcess
    )

    want_main_area = True
    resizing_enabled = True
    allows_cycle = True
    compress_signal = False

    settingsHandler = CallbackSettingsHandler()

    sigScanReady = qt.Signal(TomwerScanBase)
    """Signal emitted when a scan is ready"""

    _rpSetting = Setting(dict())
    "settings store as dict"

    static_input = Setting({"data": None, "sa_delta_beta_params": None})

    class Inputs:
        data = Input(name="data", type=TomwerScanBase, default=True, multiple=False)
        data_recompute = Input(
            name="change recons params",
            type=_TomwerBaseDock,
            doc="recompute delta / beta",
        )
        cluster_in = Input(
            name="cluster_config",
            type=SlurmClusterConfiguration,
            doc="slurm cluster to be used",
            multiple=False,
        )

    class Outputs:
        data = Output(name="data", type=TomwerScanBase)

        future_out = Output(
            name="future_data",
            type=FutureTomwerScan,
            doc="data with some remote processing",
        )

    def __init__(self, parent=None):
        """

        :param parent: QWidget parent or None
        """
        SuperviseOW.__init__(self, parent)
        WidgetLongProcessing.__init__(self)

        self._layout = gui.vBox(self.mainArea, self.name).layout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._widget = SADeltaBetaWindow(
            Outputs=self.Outputs, parent=self, process_id=self.process_id
        )
        self._layout.addWidget(self._widget)

        sa_delta_beta_params = self.static_input.get("sa_delta_beta_params", None)
        if sa_delta_beta_params is None:
            sa_delta_beta_params = self._rpSetting
        self.setConfiguration(sa_delta_beta_params)

        # connect signal / slot
        self._widget.sigConfigurationChanged.connect(self._updateSettings)
        self.destroyed.connect(self._widget.stop)
        self._widget._processing_stack.sigComputationStarted.connect(
            self._startProcessing
        )
        self._widget._processing_stack.sigComputationEnded.connect(self._endProcessing)
        # expose API
        self.wait_processing = self._widget.wait_processing

    def setConfiguration(self, configuration):
        if "workflow" in configuration:
            autofocus_lock = configuration["workflow"].get("autofocus_lock", None)
            if autofocus_lock is not None:
                self._widget.lockAutofocus(autofocus_lock)
            del configuration["workflow"]
        self._widget.setConfiguration(configuration)

    def getCurrentCorValue(self):
        return self._widget.getCurrentCorValue()

    def load_sinogram(self):
        self._widget.loadSinogram()

    def compute(self):
        self._widget.compute()

    def lockAutofocus(self, lock):
        self._widget.lockAutofocus(lock=lock)

    def isAutoFocusLock(self):
        return self._widget.isAutoFocusLock()

    @Inputs.data
    def process(self, scan):
        if scan is None:
            return
        if scan.axis_params is None:
            scan.axis_params = QAxisRP()
        if scan.sa_delta_beta_params is None:
            scan.sa_delta_beta_params = QSADeltaBetaParams()
        self._skipCurrentScan(new_scan=scan)

        # check scan can be processed
        if isinstance(scan, HDF5TomoScan):
            if not check.check_flat_series(
                scan, logger=_logger, user_input=settings.isOnLbsram(scan=scan)
            ):
                self.Outputs.data.send(scan)
                return
            if not check.check_dark_series(
                scan, logger=_logger, user_input=settings.isOnLbsram(scan=scan)
            ):
                self.Outputs.data.send(scan)
                return

        if settings.isOnLbsram(scan) and utils.isLowOnMemory(
            settings.get_lbsram_path()
        ):
            self.notify_skip(
                scan=scan,
                details="sa-delta-beta has been skiped for {} because "
                "of low space in lbsram".format(scan),
            )
            self.Outputs.data.send(scan)
        else:
            self._widget.setScan(scan=scan)
            self.notify_pending(scan)
            self.activateWindow()
            if self.isAutoFocusLock():
                self.compute()
            else:
                self.raise_()
                self.show()

    def _skipCurrentScan(self, new_scan):
        scan = self._widget.getScan()
        # if the same scan has been run several scan
        if scan is None or str(scan) == str(new_scan):
            return
        current_scan_state = ProcessManager().get_dataset_state(
            dataset_id=scan.get_dataset_identifier(), process=self
        )
        if current_scan_state in (
            DatasetState.PENDING,
            DatasetState.WAIT_USER_VALIDATION,
        ):
            details = "Was pending and has been replaced by another scan."
            self.notify_skip(scan=scan, details=details)
            self.Outputs.data.send(scan)

    @Inputs.data_recompute
    def reprocess(self, dataset):
        self.lockAutofocus(False)
        self.process(scan=dataset)

    @Inputs.cluster_in
    def setCluster(self, cluster):
        self._widget.setClusterConfig(cluster_config=cluster)

    def validateCurrentScan(self):
        self._widget.validateCurrentScan()

    def _updateSettings(self):
        config = self._widget.getConfiguration()
        config.pop("cluster_config", None)
        self._rpSetting = config
        self._rpSetting["workflow"] = {
            "autofocus_lock": self._widget.isAutoFocusLock(),
        }
        # keep for backward compatibility

        self.static_input = {
            "data": None,
            "sa_delta_beta_params": self._widget.getConfiguration(),
        }
        self.static_input["sa_delta_beta_params"]["workflow"] = {
            "autofocus_lock": self._widget.isAutoFocusLock(),
        }

    def close(self):
        self.stop()
        self._widget = None
        super().close()

    def stop(self):
        self._widget.stop()

    def getConfiguration(self):
        return self._widget.getConfiguration()
