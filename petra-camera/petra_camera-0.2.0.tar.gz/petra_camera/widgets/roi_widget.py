# ----------------------------------------------------------------------
# Author:        yury.matveev@desy.de
# ----------------------------------------------------------------------

"""
"""

from PyQt5 import QtWidgets, QtCore
from petra_camera.gui.ROI_ui import Ui_Roi

# ----------------------------------------------------------------------
class ROI(QtWidgets.QWidget):

    delete_me = QtCore.pyqtSignal(int)
    repaint_roi = QtCore.pyqtSignal()

    # ----------------------------------------------------------------------
    def __init__(self, id, camera_device):

        super(ROI, self).__init__()

        self._ui = Ui_Roi()
        self._ui.setupUi(self)

        self.my_id = id
        self.camera_device = camera_device
        self._enable_me(camera_device.rois[id]['visible'])

        self._ui.but_delete.clicked.connect(lambda state, my_id=self.my_id: self.delete_me.emit(my_id))

        self._ui.chb_roi_enable.clicked.connect(self._enable_me)

        self._ui.chk_show_com.clicked.connect(lambda state, name='com': self._enable_cross(name))
        self._ui.chk_show_max.clicked.connect(lambda state, name='max': self._enable_cross(name))
        self._ui.chk_show_min.clicked.connect(lambda state, name='min': self._enable_cross(name))

        self._ui.sb_roi_bg.valueChanged.connect(lambda value: self.save_value('bg', value))
        self._ui.sb_roi_x.valueChanged.connect(lambda value: self.save_value('x', value))
        self._ui.sb_roi_y.valueChanged.connect(lambda value: self.save_value('y', value))
        self._ui.sb_roi_w.valueChanged.connect(lambda value: self.save_value('w', value))
        self._ui.sb_roi_h.valueChanged.connect(lambda value: self.save_value('h', value))

        self._ui.but_color.clicked.connect(self._pick_my_color)

    # ----------------------------------------------------------------------
    def _block_signals(self, flag):

        self._ui.chb_roi_enable.blockSignals(flag)
        self._ui.but_delete.blockSignals(flag)

        self._ui.chk_show_min.blockSignals(flag)
        self._ui.chk_show_com.blockSignals(flag)
        self._ui.chk_show_max.blockSignals(flag)

        self._ui.sb_roi_bg.blockSignals(flag)

        self._ui.sb_roi_h.blockSignals(flag)
        self._ui.sb_roi_w.blockSignals(flag)
        self._ui.sb_roi_x.blockSignals(flag)
        self._ui.sb_roi_y.blockSignals(flag)

    # ----------------------------------------------------------------------
    def save_value(self, param, value):

        self.camera_device.set_roi_value(self.my_id, param, value)
        self.camera_device.calculate_roi_statistics()

        self.repaint_roi.emit()

    # ----------------------------------------------------------------------
    def update_values(self):

        self._block_signals(True)
        for ui in ['max_x', 'max_y', 'max_v',
                   'min_x', 'min_y', 'min_v',
                   'com_x', 'com_y', 'com_v',
                   'fwhm_x', 'fwhm_y', 'sum']:
            if self.camera_device.rois[self.my_id]['visible']:
                try:
                    getattr(self._ui, 'le_{}'.format(ui)).setText('{}'.format(self.camera_device.rois_data[self.my_id][ui]))
                except:
                    getattr(self._ui, 'le_{}'.format(ui)).setText('')
            else:
                getattr(self._ui, 'le_{}'.format(ui)).setText('')

        for ui in ['x', 'y', 'w', 'h', 'bg']:
            getattr(self._ui, 'sb_roi_{}'.format(ui)).setValue(self.camera_device.rois[self.my_id][ui])

        for ui in ['max', 'min', 'com']:
            getattr(self._ui, 'chk_show_{}'.format(ui)).setChecked(self.camera_device.rois[self.my_id]['mark'] == ui)

        self._ui.chb_roi_enable.setChecked(self.camera_device.rois[self.my_id]['visible'])

        self._ui.but_color.setStyleSheet("QPushButton {background-color: " +
                                         f"{self.camera_device.rois[self.my_id]['color']}" + ";}")

        self._block_signals(False)

    # ----------------------------------------------------------------------
    def _pick_my_color(self):
        color = QtWidgets.QColorDialog.getColor()

        if color.isValid():
            self.camera_device.set_roi_value(self.my_id, 'color', color.name())

            self.repaint_roi.emit()

    # ----------------------------------------------------------------------
    def _enable_me(self, state):
        self._ui.chk_show_min.setEnabled(state)
        self._ui.chk_show_com.setEnabled(state)
        self._ui.chk_show_max.setEnabled(state)

        self._ui.sb_roi_bg.setEnabled(state)

        self._ui.sb_roi_h.setEnabled(state)
        self._ui.sb_roi_w.setEnabled(state)
        self._ui.sb_roi_x.setEnabled(state)
        self._ui.sb_roi_y.setEnabled(state)

        self.camera_device.set_roi_value(self.my_id, 'visible', state)

        self.repaint_roi.emit()

    # ----------------------------------------------------------------------
    def _enable_cross(self, name):
        if self.camera_device.rois[self.my_id]['mark'] == name:
            name = ''

        for ui in ['max', 'min', 'com']:
            getattr(self._ui, 'chk_show_{}'.format(ui)).setChecked(name == ui)

        self.camera_device.set_roi_value(self.my_id, 'mark', name)

        self.repaint_roi.emit()
