# Created by matveyev at 19.08.2021

import logging

from PyQt5 import QtWidgets, QtCore

from petra_camera.utils.functions import refresh_combo_box
from petra_camera.widgets.base_widget import BaseWidget
from petra_camera.widgets.marker import Marker
from petra_camera.widgets.roi_widget import ROI
from petra_camera.main_window import APP_NAME

from petra_camera.gui.MarkersROIs_ui import Ui_MarkersROIs

WIDGET_NAME = 'MarkersROIs'

logger = logging.getLogger(APP_NAME)


# ----------------------------------------------------------------------
class MarkersROIsWidget(BaseWidget):

    add_remove_roi = QtCore.pyqtSignal()
    repaint_roi = QtCore.pyqtSignal()

    add_remove_marker = QtCore.pyqtSignal()
    repaint_marker = QtCore.pyqtSignal()

    # ----------------------------------------------------------------------
    def __init__(self, parent):

        super(MarkersROIsWidget, self).__init__(parent)

        self._ui = Ui_MarkersROIs()
        self._ui.setupUi(self)

        self._ui.gb_sardana.setVisible(self._camera_device.has_counter())

        self._marker_grid = QtWidgets.QGridLayout(self._ui.layout_markers)
        self._markers_widgets = []

        self._rois, self._markers, self._statistics = None, None, None

        self._reload_rois()
        self._update_marker_layout()

        self._ui.but_add_marker.clicked.connect(self._add_marker)
        self._ui.but_add_roi.clicked.connect(self._add_roi)

        self._ui.cb_counter.currentTextChanged.connect(lambda text: self._camera_device.set_counter(text))
        self._ui.cmb_roi_as_counter.currentIndexChanged.connect(lambda ind: self._camera_device.set_counter_roi(ind))

    # ----------------------------------------------------------------------
    def update_roi_statistics(self):

        for idx in range(self._ui.tb_rois.count()):
            self._ui.tb_rois.widget(idx).update_values()

        for widget in self._markers_widgets:
            widget.update_values()

        if not self._ui.cb_counter.hasFocus():
            counter_name = self._camera_device.get_counter()
            if counter_name == '':
                counter_name = 'sum'
                self._camera_device.set_counter(counter_name)
            refresh_combo_box(self._ui.cb_counter, counter_name)

    # ----------------------------------------------------------------------
    def _add_roi_widget(self, index):
        widget = ROI(index, self._camera_device)
        widget.delete_me.connect(self._delete_roi)
        widget.repaint_roi.connect(lambda: self.repaint_roi.emit())

        self._ui.tb_rois.insertTab(index, widget, 'ROI_{}'.format(index+1))
        self._ui.tb_rois.setCurrentWidget(widget)

    # ----------------------------------------------------------------------
    def _add_roi(self):
        self._camera_device.add_roi()
        self._add_roi_widget(self._ui.tb_rois.count())
        self.add_remove_roi.emit()

        self._refresh_roi_as_counter_cmb()
        self._ui.tb_rois.setVisible(True)

    # ----------------------------------------------------------------------
    def _delete_roi(self, idx):
        self._ui.tb_rois.removeTab(idx)

        self._camera_device.delete_roi(idx)
        self.add_remove_roi.emit()

        self._ui.tb_rois.setVisible(self._camera_device.num_roi())
        self._refresh_roi_as_counter_cmb()

    # ----------------------------------------------------------------------
    def _refresh_roi_as_counter_cmb(self):
        self._ui.cmb_roi_as_counter.clear()
        if self._camera_device.num_roi():
            self._ui.cmb_roi_as_counter.setEnabled(True)
            for ind in range(self._camera_device.num_roi()):
                self._ui.cmb_roi_as_counter.addItem('ROI {}'.format(ind + 1))
            if self._camera_device.get_counter_roi() < self._camera_device.num_roi():
                self._ui.cmb_roi_as_counter.setCurrentIndex(self._camera_device.get_counter_roi())
            else:
                self._ui.cmb_roi_as_counter.setCurrentIndex(self._camera_device.num_roi()-1)
        else:
            self._ui.cmb_roi_as_counter.setEnabled(False)

    # ----------------------------------------------------------------------
    def _reload_rois(self):
        for ind in range(self._ui.tb_rois.count())[::-1]:
            self._ui.tb_rois.removeTab(ind)

        if len(self._camera_device.rois):
            self._ui.tb_rois.setVisible(True)
            for ind in range(len(self._camera_device.rois)):
                self._add_roi_widget(ind)
        else:
            self._ui.tb_rois.setVisible(False)

        self._refresh_roi_as_counter_cmb()

    # ----------------------------------------------------------------------
    def _add_marker(self):
        self._camera_device.append_marker()
        self._update_marker_layout()
        self.add_remove_marker.emit()

    # ----------------------------------------------------------------------
    def _delete_marker(self, id):

        self._camera_device.delete_marker(id)
        self._update_marker_layout()
        self.add_remove_marker.emit()

    # ----------------------------------------------------------------------
    def _update_marker_layout(self):

        layout = self._ui.layout_markers.layout()
        for i in reversed(range(layout.count())):
            item = layout.itemAt(i)
            if item:
                w = layout.itemAt(i).widget()
                if w:
                    layout.removeWidget(w)
                    w.setVisible(False)

        self._markers_widgets = []
        for ind in range(len(self._camera_device.markers)):
            widget = Marker(ind, self._camera_device)
            widget.repaint_marker.connect(lambda: self.repaint_marker.emit())
            widget.delete_me.connect(self._delete_marker)
            layout.addWidget(widget)
            self._markers_widgets.append(widget)
