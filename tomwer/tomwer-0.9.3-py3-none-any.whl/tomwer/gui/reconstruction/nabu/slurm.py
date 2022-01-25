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
__date__ = "11/10/2021"


from silx.gui import qt
from tomwer.core.settings import SlurmSettings
from tomwer.core.utils.slurm import is_slurm_available


class SlurmSettingsDialog(qt.QDialog):
    sigConfigChanged = qt.Signal()
    """Signal emit when the SlurmSetting changed"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setLayout(qt.QVBoxLayout())
        self._mainWidget = SlurmSettingsWidget(parent=self)
        self.layout().addWidget(self._mainWidget)

        # buttons for validation
        self._buttons = qt.QDialogButtonBox(self)
        types = qt.QDialogButtonBox.Close
        self._buttons.setStandardButtons(types)
        self.layout().addWidget(self._buttons)

        self._buttons.button(qt.QDialogButtonBox.Close).clicked.connect(self.close)

        # connect signal /slot
        self._mainWidget.sigConfigChanged.connect(self._configChanged)

    def _configChanged(self, *args, **kwargs):
        self.sigConfigChanged.emit()

    def isSlurmActive(self):
        return self._mainWidget.isSlurmActive()

    def getConfiguration(self) -> dict:
        return self._mainWidget.getConfiguration()

    def setConfiguration(self, config: dict) -> None:
        self._mainWidget.setConfiguration(config=config)


class SlurmSettingsWidget(qt.QWidget):
    """Widget used to define Slurm configuration to be used"""

    sigConfigChanged = qt.Signal()
    """Signal emit when the SlurmSetting changed"""

    def __init__(self, parent=None) -> None:
        super().__init__(parent=parent)
        self.setLayout(qt.QFormLayout())

        # slurm active
        self._slurmCB = qt.QCheckBox("active slurm", self)
        self._slurmCB.setToolTip(
            "If active reconstruction will be launched in another slurm node"
        )
        self.layout().addRow(self._slurmCB)

        # ncores active
        self._nCores = qt.QSpinBox(self)
        self._nCores.setRange(1, 100)
        self.layout().addRow("number of core requested", self._nCores)

        # n workers
        self._nWorkers = qt.QSpinBox(self)
        self._nWorkers.setRange(1, 100)
        self.layout().addRow("number of worker requested", self._nWorkers)

        # memory
        self._memory = qt.QSpinBox(self)
        self._memory.setRange(1, 10000)
        self._memory.setSuffix("GB")
        self.layout().addRow("memory requested", self._memory)

        # gpu
        self._nGpu = qt.QSpinBox(self)
        self._nGpu.setRange(1, 10)
        self.layout().addRow("number of GPU requested", self._nGpu)

        # queues
        self._queue = qt.QLineEdit("", self)
        self.layout().addRow("queue", self._queue)

        # set up the gui
        self._slurmCB.setChecked(is_slurm_available())
        self._slurmCB.setEnabled(is_slurm_available())
        # if slurm is not available lock the option
        self._nCores.setValue(SlurmSettings.N_CORES_PER_WORKER)
        self._nWorkers.setValue(SlurmSettings.N_WORKERS)
        self._memory.setValue(SlurmSettings.MEMORY_PER_WORKER)
        self._queue.setText(SlurmSettings.QUEUE)
        self._nGpu.setValue(SlurmSettings.N_GPUS_PER_WORKER)

        # connect signal / slot
        self._slurmCB.toggled.connect(self._configurationChanged)
        self._nCores.valueChanged.connect(self._configurationChanged)
        self._nWorkers.valueChanged.connect(self._configurationChanged)
        self._queue.textEdited.connect(self._configurationChanged)
        self._nGpu.valueChanged.connect(self._configurationChanged)

    def _configurationChanged(self, *args, **kwargs):
        self.sigConfigChanged.emit()

    def isSlurmActive(self):
        return self._slurmCB.isChecked()

    def getNCores(self) -> int:
        return self._nCores.value()

    def setNCores(self, n: int) -> None:
        self._nCores.setValue(n)

    def getNWorkers(self) -> int:
        return self._nWorkers.value()

    def setNWorkers(self, n) -> None:
        self._nWorkers.setValue(n)

    def getMemory(self) -> int:
        return self._memory.value()

    def setMemory(self, memory: int) -> None:
        self._memory.setValue(memory)

    def getQueue(self) -> str:
        return self._queue.text()

    def setQueue(self, text: str) -> None:
        self._queue.setText(text)

    def getNGPU(self) -> int:
        return self._nGpu.value()

    def setNGPU(self, n: int) -> None:
        self._nGpu.setValue(n)

    def setConfiguration(self, config: dict) -> None:
        old = self.blockSignals(True)
        active_slurm = config.get("active_slurm", None)
        if active_slurm is not None:
            self._slurmCB.setChecked(active_slurm)

        n_cores = config.get("cores", None)
        if n_cores is not None:
            self.setNCores(n_cores)

        n_workers = config.get("n_workers", None)
        if n_workers is not None:
            self.setNWorkers(n_workers)

        memory = config.get("memory", None)
        if memory is not None:
            self.setMemory(memory)

        queue_ = config.get("queue", None)
        if queue_ is not None:
            self.setQueue(queue_)

        n_gpu = config.get("n_gpus", None)
        if n_gpu is not None:
            self.setNGPU(n_gpu)

        self.blockSignals(old)
        self.sigConfigChanged.emit()

    def getConfiguration(self) -> dict:
        return {
            "active_slurm": self.isSlurmActive(),
            "cores": self.getNCores(),
            "n_workers": self.getNWorkers(),
            "memory": self.getMemory(),
            "queue": self.getQueue(),
            "n_gpus": self.getNGPU(),
        }
