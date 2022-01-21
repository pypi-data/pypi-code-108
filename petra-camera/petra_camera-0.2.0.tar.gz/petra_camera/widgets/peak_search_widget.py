# Created by matveyev at 19.08.2021

from PyQt5 import QtCore

from petra_camera.widgets.base_widget import BaseWidget

from petra_camera.gui.PeakSearch_ui import Ui_PeakSearch

WIDGET_NAME = 'PeakSearch'


# ----------------------------------------------------------------------
class PeakSearchWidget(BaseWidget):

    refresh_image = QtCore.pyqtSignal()

    # ----------------------------------------------------------------------
    def __init__(self, parent):

        super(PeakSearchWidget, self).__init__(parent)

        self._ui = Ui_PeakSearch()
        self._ui.setupUi(self)

        self._load_camera_settings()

        self._ui.chk_peak_search.clicked.connect(lambda: self._peak_search_modified('chk_peak_search'))
        self._ui.rb_abs_threshold.clicked.connect(lambda: self._peak_search_modified('mode'))
        self._ui.rb_rel_threshold.clicked.connect(lambda: self._peak_search_modified('mode'))
        self._ui.sl_rel_threshold.valueChanged.connect(lambda: self._peak_search_modified('sl_rel'))
        self._ui.sb_rel_threshold.editingFinished.connect(lambda: self._peak_search_modified('sb_rel'))
        self._ui.sl_abs_threshold.valueChanged.connect(lambda: self._peak_search_modified('sl_abs'))
        self._ui.sb_abs_threshold.editingFinished.connect(lambda: self._peak_search_modified('sb_abs'))

    # ----------------------------------------------------------------------
    def _load_camera_settings(self):

        self._ui.chk_peak_search.setChecked(self._camera_device.peak_search['search'])
        self._ui.rb_rel_threshold.setChecked(self._camera_device.peak_search['search_mode'])
        self._ui.rb_abs_threshold.setChecked(not self._camera_device.peak_search['search_mode'])
        self._ui.sl_rel_threshold.setValue(self._camera_device.peak_search['rel_threshold'])
        self._ui.sb_rel_threshold.setValue(self._camera_device.peak_search['rel_threshold'])
        self._ui.sl_abs_threshold.setValue(self._camera_device.peak_search['abs_threshold'])
        self._ui.sb_abs_threshold.setValue(self._camera_device.peak_search['abs_threshold'])

    # ----------------------------------------------------------------------
    def _peak_search_modified(self, ui):

        state = self._ui.chk_peak_search.isChecked()
        self._camera_device.set_peak_search_value('search', state)
        mode = self._ui.rb_rel_threshold.isChecked()
        self._camera_device.set_peak_search_value('search_mode', mode)

        if ui == 'sl_abs':
            threshold = self._ui.sl_abs_threshold.value()
            self._ui.sb_abs_threshold.blockSignals(True)
            self._ui.sb_abs_threshold.setValue(threshold)
            self._ui.sb_abs_threshold.blockSignals(False)
        elif ui == 'sb_abs':
            threshold = self._ui.sb_abs_threshold.value()
            self._ui.sl_abs_threshold.blockSignals(True)
            self._ui.sl_abs_threshold.setValue(threshold)
            self._ui.sl_abs_threshold.blockSignals(False)
        elif ui == 'sl_rel':
            threshold = self._ui.sl_rel_threshold.value()
            self._ui.sl_rel_threshold.blockSignals(True)
            self._ui.sl_rel_threshold.setValue(threshold)
            self._ui.sl_rel_threshold.blockSignals(False)
        elif ui == 'sb_rel':
            threshold = self._ui.sb_rel_threshold.value()
            self._ui.sl_rel_threshold.blockSignals(True)
            self._ui.sl_rel_threshold.setValue(threshold)
            self._ui.sl_rel_threshold.blockSignals(False)

        if mode:
            threshold = self._ui.sl_rel_threshold.value()
            self._camera_device.set_peak_search_value('rel_threshold', threshold)
            self._ui.sl_abs_threshold.setEnabled(False)
            self._ui.sb_abs_threshold.setEnabled(False)
            self._ui.sl_rel_threshold.setEnabled(True)
            self._ui.sb_rel_threshold.setEnabled(True)
        else:
            threshold = self._ui.sl_abs_threshold.value()
            self._camera_device.set_peak_search_value('abs_threshold', threshold)
            self._ui.sl_abs_threshold.setEnabled(True)
            self._ui.sb_abs_threshold.setEnabled(True)
            self._ui.sl_rel_threshold.setEnabled(False)
            self._ui.sb_rel_threshold.setEnabled(False)

        self.refresh_image.emit()

    # ----------------------------------------------------------------------
    def _block_signals(self, flag):

        self._ui.sl_rel_threshold.blockSignals(flag)
        self._ui.sb_rel_threshold.blockSignals(flag)
        self._ui.sl_abs_threshold.blockSignals(flag)
        self._ui.sb_abs_threshold.blockSignals(flag)
        self._ui.rb_abs_threshold.blockSignals(flag)
        self._ui.rb_rel_threshold.blockSignals(flag)
        self._ui.chk_peak_search.blockSignals(flag)