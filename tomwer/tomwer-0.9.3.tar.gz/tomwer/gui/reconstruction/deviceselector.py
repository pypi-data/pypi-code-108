from silx.gui import qt
from tomwer.core.utils.device import CudaDevice
from tomwer.core.utils.device import _CudaPlatformBase
import logging

_logger = logging.getLogger(__name__)


class _PlatformSelectorBase:
    """simple interface for platform selection"""

    def getDevices(self):
        raise NotImplementedError("Base class")

    def getSelectedDevide(self):
        raise NotImplementedError("Base class")


class CudaPlatfornComboBox(qt.QWidget, _CudaPlatformBase):
    NONE_FOUND = "no cuda compliant gpu found"

    def __init__(self, parent=None):
        super(CudaPlatfornComboBox, self).__init__(parent=parent)
        self.setLayout(qt.QHBoxLayout())

        label = qt.QLabel("GPU Device:", self)
        self.layout().addWidget(label)
        self.deviceSelector = qt.QComboBox(self)
        self.deviceSelector.addItem(CudaDevice.NONE_FOUND)
        self.layout().addWidget(self.deviceSelector)

        devices = self.getExistingDevices()
        if len(devices) > 0:
            self.deviceSelector.clear()
            for device in devices:
                self.deviceSelector.addItem(device.name)

    def getSelectedDevice(self):
        """Return platform id and device id"""
        if self.deviceSelector.currentText() == self.NONE_FOUND:
            return None
        else:
            return CudaDevice(self.deviceSelector.currentText())


class CudaPlatfornGroup(qt.QGroupBox, _CudaPlatformBase):
    """
    GroupBox listing all the existing cuda device and allow user to select the
    one to use for reconstruction
    """

    selectionChanged = qt.Signal(list)

    def __init__(self, parent=None):
        qt.QGroupBox.__init__(self, parent=parent)
        _CudaPlatformBase.__init__(self)
        self.setLayout(qt.QVBoxLayout())
        self.setTitle("GPU devices to use")
        self._devices = {}
        try:
            existing_devices = self.getExistingDevices()
        except Exception as e:
            _logger.error(e)
        else:
            for device in existing_devices:
                qcb = qt.QCheckBox(device.name)
                self.layout().addWidget(qcb)
                self._devices[device] = qcb
                qcb.stateChanged.connect(self._selectionUpdated)

    def activate_all(self):
        for device in self._devices:
            self._devices[device].setChecked(True)

    def getSelectedDevices(self):
        """

        :return: list of "CudaDevice" selected by the user
        :rtype:list
        """
        selected = []
        for device in self._devices:
            if self._devices[device].isChecked():
                selected.append(device)
            return selected

    def removeSelection(self):
        for device in self._devices:
            self._devices[device].setChecked(False)

    def setDevices(self, selection):
        """
        set selected devices.

        :param list selection: selected devices, list of "CudaDevice" or int
        """
        if selection is None:
            self.activate_all()
            return

        def device_to_index():
            res = {}
            for device, checkbox in self._devices.items():
                res[device._id] = checkbox
            return res

        indexes_to_cb = device_to_index()
        for device in selection:
            if isinstance(selection, CudaDevice):
                id_ = device.id_
            else:
                id_ = device

            if id_ in indexes_to_cb:
                indexes_to_cb[id_].setChecked(True)

        self._selectionUpdated()

    def _selectionUpdated(self, *args, **kwargs):
        self.selectionChanged.emit(self.getSelectedDevices())
