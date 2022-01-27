import numpy as np
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QDialog
import pyqtgraph as pg
from vpv.lib.qrangeslider import QRangeSlider
from vpv.utils.lookup_tables import Lut
from vpv.ui.views.ui_datatab import Ui_data
from vpv.ui.views.ui_change_vol_name import Ui_VolNameDialog
import copy
from vpv.common import Orientation, Layers
from functools import partial

"""
The Qt widget that controls the currently viewed volumes, heatmaps, and vector volumes. Accessed from the main 
dock widget
"""

DEFAULT_SCALE_BAR_SIZE = 14.0


class VolNameDialog(QDialog):
    name_changed_signal = QtCore.pyqtSignal(str, str)

    def __init__(self, parent, current_name):
        super(VolNameDialog, self).__init__(parent)
        self.current_name = copy.copy(current_name)
        self.ui = Ui_VolNameDialog()
        self.ui.setupUi(self)
        self.setWindowTitle('Edit volume name')
        self.ui.lineEditVolName.setText(current_name)
        self.ui.pushButtonOk.clicked.connect(self.on_ok)
        self.ui.pushButtonCancel.clicked.connect(self.on_cancel)

    def on_ok(self):
        new_name = self.ui.lineEditVolName.text()
        self.name_changed_signal.emit(self.current_name, new_name)
        self.close()

    def on_cancel(self):
        self.close()


class ManageData(QtGui.QWidget):
    data_processing_signal = QtCore.pyqtSignal()
    data_processing_finished_signal = QtCore.pyqtSignal()
    roi_signal = QtCore.pyqtSignal(list, list, list)
    ui_changed_signal = QtCore.pyqtSignal()
    scale_bar_color_signal = QtCore.pyqtSignal(QtGui.QColor)
    gradient_editor_signal = QtCore.pyqtSignal()
    load_metadata_signal = QtCore.pyqtSignal()

    def __init__(self, controller, model, mainwindow, appdata):
        super(ManageData, self).__init__(mainwindow)
        self.ui = Ui_data()
        self.ui.setupUi(self)
        self.views = controller.views
        self.mainwindow = mainwindow
        self.appdata = appdata
        lut = Lut()
        self.controller = controller  # run_vpv.py

        self.hotred = lut._hot_red_blue()[0]
        self.hotblue = lut._hot_red_blue()[1]

        self.model = model
        self.volume_ids = None
        self.luts = Lut()

        self.ui.labelFdrThresholds.hide()

        self._link_views = True
        self.ui.checkBoxLinkViews.setChecked(True)

        self.vector_mag_slider = QRangeSlider((0, 0, 0))
        # Just need one handle, so hide the minimum handle
        self.vector_mag_slider.head.setDisabled(True)
        self.ui.horizontalLayoutMagnitudeSlider.insertWidget(1, self.vector_mag_slider)

        self.vector_mag_slider.setMin(0)
        self.vector_mag_slider.setMax(10.0)
        self.vector_mag_slider.setStart(0)
        self.vector_mag_slider.setEnd(10.0)

        # The lower volume levels slider and Combo boxes
        self.volume_levels_slider = QRangeSlider((255, 255, 255))
        self.ui.horizontalLayoutVol1Levels.insertWidget(1, self.volume_levels_slider)

        # upper volume levels slider and comboboxes
        self.volume_levels_slider2 = QRangeSlider((255, 255, 255))
        self.ui.horizontalLayoutVol2Levels.insertWidget(1, self.volume_levels_slider2)

        # data sliders
        self.data_levels_positive_slider = QRangeSlider((0, 255, 0))
        pos_bg = 'background: qlineargradient(x1: 0.2, x2: 1,stop: 0 #FFFFFF, stop: 1  #FF0000);'
        self.data_levels_positive_slider.handle.setStyleSheet(pos_bg)
        self.ui.horizontalLayoutDataSliders.insertWidget(1, self.data_levels_positive_slider)

        self.data_levels_negative_slider = QRangeSlider((0, 255, 0))
        neg_bg = 'background: qlineargradient(x1: 0.2, x2: 1,stop: 0 #0000FF, stop: 1  #FFFFFF);'
        self.data_levels_negative_slider.handle.setStyleSheet(neg_bg)
        self.ui.horizontalLayoutDataSliders.insertWidget(0, self.data_levels_negative_slider)

        self.ui.pushButtonManagerGrey.hide()
        self.ui.pushButtonManagerCyan.hide()
        self.ui.pushButtonManagerOrange.hide()

        self.six_views_visible = False

        self.ui.checkBox6Views.setChecked(False)

        self.blob_table = QtGui.QTableWidget(self)
        self.ui.verticalLayoutConnectedComponents.addWidget(self.blob_table, 0)

        self.blob_table.setColumnCount(3)
        self.blob_table.setHorizontalHeaderLabels(['Count', 'Mean', 'location'])

        self.ui.doubleSpinBoxVoxelSize.setMaximum(1000.0)
        self.ui.doubleSpinBoxVoxelSize.setValue(DEFAULT_SCALE_BAR_SIZE)
        self.ui.doubleSpinBoxVoxelSize.setKeyboardTracking(False)
        self.ui.doubleSpinBoxVoxelSize.valueChanged.connect(self.set_voxel_size)

        self.ui.doubleSpinBoxScaleBarLength.setMaximum(10000)
        self.ui.doubleSpinBoxScaleBarLength.setValue(1000)
        self.ui.doubleSpinBoxScaleBarLength.setKeyboardTracking(False)

        self.colour_bar = ColorScaleBar(self.ui.verticalLayoutColorScale, self.hotblue, self.hotred)
        self.ui.vol2ControlsWidget.hide()
        self.ui.vectorWidget.hide()
        self.ui.dataWidget.hide()

        self.ui.doubleSpinBoxNegThresh.setMaximum(0)
        self.ui.doubleSpinBoxNegThresh.setMinimum(-100)
        self.ui.doubleSpinBoxNegThresh.setSingleStep(0.1)

        self.ui.doubleSpinBoxPosThresh.setSingleStep(0.1)

        self.ui.doubleSpinBoxVol2Opacity.setRange(0.0, 1.0)
        self.ui.doubleSpinBoxVol2Opacity.setSingleStep(0.1)
        self.ui.doubleSpinBoxVol2Opacity.setValue(1.0)

        self.ui.pushButtonLoadAtlasMeta.clicked.connect(self.load_atlas_meta_slot)

        self.connect_signal_slots()

    def load_atlas_meta_slot(self):
        self.load_metadata_signal.emit()

    def connect_signal_slots(self):
        self.ui.pushButtonRecalcConnectComponents.clicked.connect(self.controller.recalc_connected_components)
        self.ui.comboBoxVolume.activated['QString'].connect(partial(self.modify_layer, Layers.vol1, 'set_volume'))

        self.ui.checkBoxVisibilityVol2.clicked.connect(partial(self.modify_layer, Layers.vol2, 'set_visibility'))
        self.ui.checkBoxVisibilityHeatmap.clicked.connect(partial(self.modify_layer, Layers.heatmap, 'set_visibility'))

        self.ui.checkBoxLinkViews.clicked.connect(self.on_link_views)

        self.ui.comboBoxOrientation.activated['QString'].connect(self.on_orientation)

        self.ui.pushButtonScreenShot.clicked.connect(self.controller.take_screen_shot)

        self.ui.pushButtonVectorMagnitudeFilter.pressed.connect(self.lower_magnitude_changed)

        self.volume_levels_slider.startValueChanged.connect(self.lower_level_volume_changed)
        self.volume_levels_slider.endValueChanged.connect(self.upper_level_volume_changed)
        self.ui.comboBoxVolumeLut.activated['QString'].connect(self.on_vol_lut_changed)
        self.volume_levels_slider2.startValueChanged.connect(self.lower_level_volume2_changed)
        self.volume_levels_slider2.endValueChanged.connect(self.upper_level_volume2_changed)

        self.ui.comboBoxVolume2.activated['QString'].connect(self.volume2_changed)
        self.ui.comboBoxVolumeLut2.activated['QString'].connect(self.on_vol2_lut_changed)
        self.ui.comboBoxLutHeatmap.activated['QString'].connect(self.on_heatmap_lut_changed)

        self.ui.comboBoxData.activated['QString'].connect(self.data_changed)

        # connect the levels slider to the model
        self.data_levels_negative_slider.startValueChanged.connect(self.data_negative_lower_changed)
        self.data_levels_negative_slider.endValueChanged.connect(self.data_negative_higher_changed)

        self.data_levels_positive_slider.startValueChanged.connect(self.data_positive_lower_changed)
        self.data_levels_positive_slider.endValueChanged.connect(self.data_positive_higher_changed)

        self.ui.pushButtonManagerRed.clicked.connect(self.showRedViewManagerSlot)
        self.ui.pushButtonManagerBlue.clicked.connect(self.showBlueViewManagerSlot)
        self.ui.pushButtonManagerGreen.clicked.connect(self.showGreenViewManagerSlot)
        self.ui.pushButtonManagerOrange.clicked.connect(self.showOrangeViewManagerSlot)
        self.ui.pushButtonManagerGrey.clicked.connect(self.showYellowViewManagerSlot)
        self.ui.pushButtonManagerCyan.clicked.connect(self.showCyanViewManagerSlot)

        self.ui.checkBoxLeftView.clicked.connect(self.left_view_visibility)
        self.ui.checkBoxCentralView.clicked.connect(self.central_view_visibility)
        self.ui.checkBoxRightView.clicked.connect(self.right_view_visibility)
        # connect the vector controls
        self.ui.comboBoxVectors.activated['QString'].connect(self.vector_changed)
        self.ui.spinBoxVectorScale.valueChanged['QString'].connect(self.vector_scale_changed)
        self.ui.spinBoxVectorSubsampling.valueChanged.connect(self.vector_subsampling_changed)
        self.ui.pushButtonVectorColor.pressed.connect(self.vector_change_color)

        self.blob_table.cellClicked.connect(self.on_connected_table_clicked)
        self.ui.doubleSpinBoxScaleBarLength.valueChanged.connect(self.set_scalebar_length)

        self.ui.checkBoxShowVol2Controls.clicked.connect(self.vol2_controls_visibility)
        self.ui.checkBoxShowVectorControls.clicked.connect(self.vector_controls_visibility)
        self.ui.checkBoxShowDataControls.clicked.connect(self.data_controls_visibility)

        self.ui.pushButtonEditVolName.clicked.connect(self.on_change_vol_name)

        self.ui.pushButtonScaleBarColor.clicked.connect(self.on_scalebar_color)

        self.ui.doubleSpinBoxNegThresh.valueChanged.connect(self.on_neg_thresh_spin)

        self.ui.checkBox6Views.clicked.connect(self.show2Rows)

        self.ui.doubleSpinBoxPosThresh.valueChanged.connect(self.on_pos_thresh_spin)
        self.ui.checkBoxScaleBarLabel.clicked.connect(self.on_scalebar_label_checked)

        self.ui.doubleSpinBoxVol2Opacity.valueChanged.connect(partial(self.modify_layer, Layers.vol2, 'set_opacity'))

    def on_scalebar_label_checked(self, checked):
        for view in self.views.values():
            view.scale_bar_visible = checked

    def activate_tab(self):
            pass

    def on_neg_thresh_spin(self, value):
        self.data_levels_negative_slider.setEnd(value)

    def on_pos_thresh_spin(self, value):
        self.data_levels_positive_slider.setStart(value)

    def on_pos_lut(self):
        print('gradient in dm')
        self.gradient_editor_signal.emit() # called 5/6 times on one click

    def on_scalebar_color(self):
        color = QtGui.QColorDialog.getColor()
        self.scale_bar_color_signal.emit(color)

    def on_change_vol_name(self):
        vol = self.controller.current_view.layers[Layers.vol1].vol
        if vol:
            dlg = VolNameDialog(self, vol.name)
            dlg.name_changed_signal.connect(self.change_vol_name)
            dlg.show()

    def change_vol_name(self, current_name, new_name):
        vol = self.controller.current_view.layers[Layers.vol1].vol

        if vol and new_name:
            self.controller.model.change_vol_name(current_name, new_name)
            self.controller.update_slice_views()
            self.update()

    # def mouse_pressed(self, view_index, x, y, orientation, vol_id):
    #     self.annotations.mouse_pressed_annotate(view_index, x, y, orientation, vol_id)

    def data_controls_visibility(self, checked):
        if checked:
            self.ui.dataWidget.show()
        else:
            self.ui.dataWidget.hide()

    def vector_controls_visibility(self, checked):
        if checked:
            self.ui.vectorWidget.show()
        else:
            self.ui.vectorWidget.hide()

    def vol2_controls_visibility(self, checked):
        if checked:
            self.ui.vol2ControlsWidget.show()
        else:
            self.ui.vol2ControlsWidget.hide()

    def show_color_scale_bars(self, isvisible=True):
        """
        Make color scale bar figure. A bit of a mess at the moment. Will tody up
        """
        if not self.controller.current_view.layers[Layers.heatmap].vol:
            return
        if not isvisible:
            self.colour_bar.hide()
            return
        else:
            self.colour_bar.show()

    def set_scalebar_length(self, length):
        for view in self.views.values():
            view.set_scalebar_size(length)

    def set_voxel_size(self, voxel_size):
        for view in self.views.values():
            view.set_voxel_size(voxel_size)

    def lower_magnitude_changed(self):
        value = self.vector_mag_slider.getRange()[0]
        if not self.link_views:
            self.current_slice_view.layers[Layers.vectors].set_magnitude_cutoff(value, 10.0)
        else:
            for view in self.views.values():
                view.layers[Layers.heatmap].set_magnitude_cutoff(value, 10.0)
        #self.update_slice_views()

    def vector_subsampling_changed(self, value):
        if self.link_views:
            for view in self.views.values():
                view.layers[Layers.vectors].set_subsampling(value)
        else:
            self.controller.current_view.layers[Layers.vectors].set_subsampling(value)

    def vector_scale_changed(self, value):
        if self.link_views:
            for view in self.views.values():
                view.layers[Layers.vectors].set_scale(value)
        else:
            self.controller.current_view.layers[Layers.vectors].set_scale(value)

    def vector_change_color(self):
        col = QtGui.QColorDialog.getColor()

        if col.isValid():
            self.modify_layer(Layers.vectors, 'set_arrow_color', col)

    def showRedViewManagerSlot(self):
        self.switch_selected_view(0)

    def showBlueViewManagerSlot(self):
        self.switch_selected_view(1)

    def showGreenViewManagerSlot(self):
        self.switch_selected_view(2)

    def showOrangeViewManagerSlot(self):
        self.switch_selected_view(3)

    def showYellowViewManagerSlot(self):
        self.switch_selected_view(4)

    def showCyanViewManagerSlot(self):
        self.switch_selected_view(5)

    def on_fdr_button_clicked(self, t):
        """
        Upon clicking the fdr threshold button the signal with the corresponding t value arives here
        Set the threshold on the current Heatmap volume

        Parameters
        ----------
        t: float
            the t-statistic
        """
        self.modify_layer(Layers.heatmap, 'set_t_threshold', t)

    def volume_changed(self, vol_name):
        """
        When volume is changed from the combobox
        """

        self.modify_layer(Layers.vol1, 'set_volume', vol_name)

    def volume2_changed(self, vol_name):
        """
        When volume is changed from the combobox
        """
        self.modify_layer(Layers.vol2, 'set_volume', vol_name)

    def data_changed(self, vol_name):
        """
        """
        self.modify_layer(Layers.heatmap, 'set_volume', vol_name)
        self.update_connected_components(vol_name)

    def update_connected_components(self, vol_name):
        self.blob_table.clear()
        self.blob_table.setRowCount(0) # clear
        self.blob_table.setHorizontalHeaderLabels(['Count', 'Mean', 'location x:x, y:y, z:z'])

        # set the connected component list
        if vol_name != 'None':
            conn = self.model.getdata(vol_name).connected_components

            for i, (size_mean, bbox) in enumerate(conn.items()):
                self.blob_table.insertRow(i)
                bbox_string = ', '.join(str(x) for x in bbox)
                self.blob_table.setItem(i, 0, QtGui.QTableWidgetItem(str(size_mean[0])))
                self.blob_table.setItem(i, 1, QtGui.QTableWidgetItem(str(size_mean[1])))
                self.blob_table.setItem(i, 2, QtGui.QTableWidgetItem(bbox_string))

        self.blob_table.resizeColumnsToContents()

    def on_connected_table_clicked(self, row, _):
        roi_widget = self.blob_table.item(row, 2)
        roi_str = roi_widget.text()
        roi = [x.strip() for x in roi_str.split(', ')]
        self.roi_signal.emit(roi[0:2], roi[2:4], roi[4:6])

    def vector_changed(self, vol_name):
        self.modify_layer(Layers.vectors, 'set_volume', vol_name)

    def switch_selected_view(self, slice_id):
        """
        update the slice manager with data from a slice view
        :param slice_id: Id of the SliceWidget that this current widget was activated from
        """

        self.ui.pushButtonManagerRed.setStyleSheet("background-color: #FFDEDE")
        self.ui.pushButtonManagerBlue.setStyleSheet("background-color: #D2C9FF")
        self.ui.pushButtonManagerGreen.setStyleSheet("background-color: #C9FFCB")
        self.ui.pushButtonManagerOrange.setStyleSheet("background-color: #FFF3A6")
        self.ui.pushButtonManagerGrey.setStyleSheet("background-color: #FFFFFF")
        self.ui.pushButtonManagerCyan.setStyleSheet("background-color: #ABFFFE")

        if slice_id == 0:
            self.ui.pushButtonManagerRed.setStyleSheet("background-color: red")
        elif slice_id == 1:
            self.ui.pushButtonManagerBlue.setStyleSheet("background-color: blue")
        elif slice_id == 2:
            self.ui.pushButtonManagerGreen.setStyleSheet("background-color: green")
        elif slice_id == 3:
            self.ui.pushButtonManagerOrange.setStyleSheet("background-color: orange")
        elif slice_id == 4:
            self.ui.pushButtonManagerGrey.setStyleSheet("background-color: grey")
        elif slice_id == 5:
            self.ui.pushButtonManagerCyan.setStyleSheet("background-color: cyan")
        self.controller.set_current_view(slice_id)
        self.update()
        self.show()

    def update(self):
        """
        Update the view manager for the current Slice view.
        Called when viewing a new orthogonal view
        """
        self.populate_volume_controls()
        self.populate_heatmap_controls()
        self.populate_vector_controls()


    def refresh_data_comboboxes(self):
        """
        """
        self.populate_volume_controls()
        self.populate_heatmap_controls()
        self.annotations.update()

    def populate_heatmap_controls(self):
        self.ui.comboBoxData.clear()
        self.ui.comboBoxData.addItems(self.model.data_id_list())
        self.ui.comboBoxData.addItem("None")
        self.ui.comboBoxOrientation.setCurrentIndex(self.ui.comboBoxOrientation.findText(
            self.controller.current_orientation().name))
        self.ui.comboBoxLutHeatmap.clear()
        self.ui.comboBoxLutHeatmap.addItems(self.luts.heatmap_lut_list())
        # self.update_connected_components()  TODO: how signal update
        self.update_data_controls()

    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clear_layout(item.layout())

    def update_fdr_buttons(self):
        """
        When the heatmap volume has been changed, check for the presence of q->t threshold mapping dict and set buttons if present

        """
        slice_layers = self.controller.current_view.layers
        heatmap_vol = slice_layers[Layers.heatmap].vol
        if not heatmap_vol:
            return

        row = 0
        col = 0

        self.clear_layout(self.ui.gridLayoutFdrButtons)

        if heatmap_vol.fdr_thresholds:
            self.ui.labelFdrThresholds.show()
            group = QtGui.QButtonGroup(self)
            for q, t in heatmap_vol.fdr_thresholds.items():
                try:
                    float(t)
                except (ValueError, TypeError):
                    continue
                button = QtGui.QPushButton(str(q))
                group.addButton(button)
                button.clicked.connect(partial(self.on_fdr_button_clicked, t))
                self.ui.gridLayoutFdrButtons.addWidget(button, row, col)
                col += 1
                if col > 5:
                    row += 1
                    col = 0
        else:
            self.ui.labelFdrThresholds.hide()

    def populate_volume_controls(self):
        """
        when a new view manager is activatewd from a new slice view
        :return:
        """
        self.ui.comboBoxVolume.clear()
        self.ui.comboBoxVolume.addItems(self.model.volume_id_list())
        self.ui.comboBoxVolume.addItem("None")
        # do the luts
        self.ui.comboBoxVolumeLut.clear()
        # Lookup table combobox
        self.ui.comboBoxVolumeLut.addItems(self.luts.lut_list())

        self.ui.comboBoxVolume2.clear()
        self.ui.comboBoxVolume2.addItems(self.model.volume_id_list())
        self.ui.comboBoxVolume2.addItem("None")
        # do the luts
        self.ui.comboBoxVolumeLut2.clear()
        # Lookup table combobox
        self.ui.comboBoxVolumeLut2.addItems(self.luts.lut_list())

        self.update_volume_controls()

    def populate_vector_controls(self):
        self.ui.comboBoxVectors.clear()
        self.ui.comboBoxVectors.addItems(self.model.vector_id_list())
        self.ui.comboBoxVectors.addItem("None")
        self.update_vector_controls()

    def update_vector_controls(self):
        vol = self.controller.current_view.layers[Layers.vectors].vol
        if vol:
            self.ui.spinBoxVectorSubsampling.setValue(vol.subsampling)
            self.ui.spinBoxVectorScale.setValue(vol.scale)
            self.ui.comboBoxVectors.setCurrentIndex(self.ui.comboBoxVectors.findText(vol.name))
        else:
             self.ui.comboBoxVectors.setCurrentIndex( self.ui.comboBoxVectors.findText('None'))

    def update_volume_controls(self):
        slice_layers = self.controller.current_view.layers
        vol1 = slice_layers[Layers.vol1].vol

        if vol1:
            min_, max_ = [round(x, 2) for x in vol1.intensity_range()]
            lower, upper = [round(x, 2) for x in vol1.levels]
            self.volume_levels_slider.setMin(min_)
            self.volume_levels_slider.setMax(max_)
            self.volume_levels_slider.setStart(lower)
            self.volume_levels_slider.setEnd(upper)
            self.volume_levels_slider.update()
            self.ui.comboBoxVolume.setCurrentIndex(
                self.ui.comboBoxVolume.findText(vol1.name))
            self.ui.comboBoxVolumeLut.setCurrentIndex(
                self.ui.comboBoxVolumeLut.findText(slice_layers[Layers.vol1].lut[1]))
        else:  # No volume
            self.ui.comboBoxVolume.setCurrentIndex(self.ui.comboBoxVolume.findText('None'))

        vol2 = slice_layers[Layers.vol2].vol
        if vol2:
            min_, max_ = [round(x, 2) for x in vol2.intensity_range()]
            lower, upper = [round(x, 2) for x in vol2.levels]
            self.volume_levels_slider2.setMin(min_)
            self.volume_levels_slider2.setMax(max_)
            self.volume_levels_slider2.setStart(lower)
            self.volume_levels_slider2.setEnd(upper)
            self.volume_levels_slider2.update()
            self.ui.comboBoxVolume2.setCurrentIndex(self.ui.comboBoxVolume2.findText(vol2.name))
            self.ui.comboBoxVolumeLut2.setCurrentIndex(
                self.ui.comboBoxVolumeLut2.findText(slice_layers[Layers.vol2].lut[1]))
        else:  # No second volume overlay
            self.ui.comboBoxVolume2.setCurrentIndex(self.ui.comboBoxVolume2.findText('None'))

    def update_color_scale_bar(self):
        vol = self.controller.current_view.layers[Layers.heatmap].vol
        if vol:
            neg_lower, neg_upper = [round(x, 2) for x in vol.neg_levels]
            pos_lower, pos_upper = [round(x, 2) for x in vol.pos_levels]
            self.colour_bar.update(pos_upper,  pos_lower, neg_upper,neg_lower)

    def update_data_controls(self):
        vol = self.controller.current_view.layers[Layers.heatmap].vol
        self.update_fdr_buttons()
        if vol:
            min_, max_ = [round(x, 2) for x in vol.intensity_range()]
            neg_min_nonzero, pos_min_nonzero = vol.non_zero_mins
            neg_lower, neg_upper = [round(x, 2) for x in vol.neg_levels]
            pos_lower, pos_upper = [round(x, 2) for x in vol.pos_levels]
            # print min_, max_, neg_lower, pos_lower, pos_upper

            # if there are no values for negative or positive stats, we need to inactivate the respective sliders
            # as we can't have sliders with min=0 and max = 0

            self.ui.comboBoxData.setCurrentIndex(self.ui.comboBoxData.findText(vol.name))

            try:
                if pos_upper > 0.0:
                    self.data_levels_positive_slider.setEnabled(True)
                    self.data_levels_positive_slider.setMin(pos_min_nonzero)
                    self.data_levels_positive_slider.setMax(max_)
                    self.data_levels_positive_slider.setStart(pos_lower)
                    self.data_levels_positive_slider.setEnd(pos_upper)
                    self.data_levels_positive_slider.update()
                    pos_bg = 'background: qlineargradient(x1: 0, x2: 1,stop: 0 #222222, stop: 0.5 #FF0000, stop: 1.0 #FFFFFF  );'
                    self.data_levels_positive_slider.handle.setStyleSheet(pos_bg)
                else:  # no positive values, set to grey
                    self.data_levels_positive_slider.setEnabled(False)
                    pos_bg = 'background: qlineargradient(x1: 0.2, x2: 1,stop: 0 #ADADAD, stop: 1  #ADADAD);'
                    self.data_levels_positive_slider.handle.setStyleSheet(pos_bg)
                if neg_lower < 0.0:
                    self.data_levels_negative_slider.setEnabled(True)
                    self.data_levels_negative_slider.setMin(min_)
                    self.data_levels_negative_slider.setMax(neg_min_nonzero)
                    self.data_levels_negative_slider.setStart(neg_lower)
                    self.data_levels_negative_slider.setEnd(neg_upper)
                    self.data_levels_negative_slider.update()
                    neg_bg = 'background: qlineargradient(x1: 0, x2: 1,stop: 0 #FFFFFF, stop: 0.5  #0000FF, stop: 1 #222222);'
                    self.data_levels_negative_slider.handle.setStyleSheet(neg_bg)
                else:  # no negative values, set to grey
                    self.data_levels_negative_slider.setEnabled(False)
                    neg_bg = 'background: qlineargradient(x1: 0.2, x2: 1,stop: 0 #ADADAD, stop: 1  #ADADAD);'
                    self.data_levels_negative_slider.handle.setStyleSheet(neg_bg)
            except TypeError:
                # The slider is raising a type error. Not sure why at the moment
                print('Slider error')
            self.update_color_scale_bar()
            self.ui.doubleSpinBoxNegThresh.setValue(neg_upper)
            self.ui.doubleSpinBoxPosThresh.setValue(pos_lower)
        else:
            self.ui.comboBoxData.setCurrentIndex(self.ui.comboBoxData.findText('None'))

    def modify_layer(self, layer_idx: Layers, method: str, *args):
        """
        Instead of of replicating all the functions in the layers here, we get the method to call on the layers by
        str and getattr

        Parameters
        ----------
        layer_idx
            The enum specifying whch layer to target
        method
            The method in the Layer subclasses to call
        args
            Any arguments to pass on

        """
        if self.link_views:
            for view in self.views.values():
                getattr(view.layers[layer_idx], method)(*args)
        else:
            getattr(self.controller.current_view.layers[layer_idx], method)(*args)

        self.update_slice_views()
        self.update_volume_controls()
        self.update_data_controls()
        self.update_vector_controls()

    def lower_level_volume_changed(self, value):
        self.controller.current_view.layers[Layers.vol1].vol.set_lower_level(value)
        self.update_slice_views()

    def upper_level_volume_changed(self, value):
        self.controller.current_view.layers[Layers.vol1].vol.set_upper_level(value)
        self.update_slice_views()

    def lower_level_volume2_changed(self, value):
        self.controller.current_view.layers[Layers.vol2].vol.set_lower_level(value)
        self.update_slice_views()

    def upper_level_volume2_changed(self, value):
        if self.controller.current_view.layers[Layers.vol2].vol:
            self.controller.current_view.layers[Layers.vol2].vol.set_upper_level(value)
            self.update_slice_views()

    def update_data_lut(self, which, value):
        vol = self.controller.current_view.layers[Layers.heatmap].vol
        if vol:
            if which == 'neg_lower':
                vol.set_lower_negative_lut(value)
            elif which == 'neg_upper':
                vol.set_upper_negative_lut(value)
            elif which == 'pos_lower':
                vol.set_lower_positive_lut(value)
            elif which == 'pos_upper':
                vol.set_upper_positive_lut(value)
        self.update_slice_views()

    def data_negative_lower_changed(self, value):
        self.update_data_lut('neg_lower', value)

    def data_negative_higher_changed(self, value):
        self.update_data_lut('neg_upper', value)
        self.ui.doubleSpinBoxNegThresh.setValue(value)

    def data_positive_lower_changed(self, value):
        self.update_data_lut('pos_lower', value)
        self.ui.doubleSpinBoxPosThresh.setValue(value)

    def data_positive_higher_changed(self, value):
        self.update_data_lut('pos_upper', value)

    # def modify_tstat_lut(self, index, value):
    #     self.update_slice_views()

    def on_vol_lut_changed(self, lut_name):
        self.modify_layer(Layers.vol1, 'set_lut', lut_name)

    def on_vol2_lut_changed(self, lut_name):
        self.modify_layer(Layers.vol2, 'set_lut', lut_name)

    def on_heatmap_lut_changed(self, lut_name):
        """
        The heatmap LUT is stored on the volume not on the layer
        Parameters
        ----------
        lut_name str:
            the name of the LUT
        """
        vol = self.controller.current_view.layers[Layers.heatmap].vol
        vol.set_lut(lut_name)
        self.update_slice_views()

    def update_slice_views(self):
        self.update_color_scale_bar()
        for view in self.views.values():
            view.update_view()

    def clear(self):
        self.blob_table.clear()

    def set_current_sliceview(self, slice_id):
        self.current_slice_view = self.model.slice_views[slice_id]

    def on_link_views(self, checked):
        self.link_views = checked

    @property
    def link_views(self):
        return self._link_views

    @link_views.setter
    def link_views(self, checked):
        self._link_views = checked
        self.ui.checkBoxLinkViews.setChecked(checked)

    def left_view_visibility(self, checked):
        if checked:
            self.views[0].show()
            if self.six_views_visible:
                self.views[3].show()
        else:
            self.views[0].hide()
            if self.six_views_visible:
                self.views[3].hide()

    def central_view_visibility(self, checked):
        if checked:
            self.views[1].show()
            if self.six_views_visible:
                self.views[4].show()
        else:
            self.views[1].hide()
            if self.six_views_visible:
                self.views[4].hide()

    def right_view_visibility(self, checked):
        if checked:
            self.views[2].show()
            if self.six_views_visible:
                self.views[5].show()
        else:
            self.views[2].hide()
            if self.six_views_visible:
                self.views[5].hide()

    def show2Rows(self, checked):
        if checked:
            self.six_views_visible = True
            self.views[3].show()
            self.views[4].show()
            self.views[5].show()
            self.ui.pushButtonManagerOrange.show()
            self.ui.pushButtonManagerGrey.show()
            self.ui.pushButtonManagerCyan.show()
        else:
            self.six_views_visible = False
            self.views[3].hide()
            self.views[4].hide()
            self.views[5].hide()
            self.ui.pushButtonManagerOrange.hide()
            self.ui.pushButtonManagerGrey.hide()
            self.ui.pushButtonManagerCyan.hide()
        self.controller.update_slice_views()

    def on_interpolate(self, checked):
        self.model.set_interpolation(checked)
        self.update_slice_views()

    def on_orientation(self, orientation: str):
        """
        Activated when the orientation combobox is changed
        :return:
        """
        # convert the str to an enum member

        orientation = Orientation[orientation]

        if self.link_views:
            for v in self.views.values():
                v.set_orientation(orientation)
        else:
            v = self.controller.current_view
            v.set_orientation(orientation)


class ColorScaleBar(object):
    def __init__(self, layout, neg_lut, pos_lut):
        self.color_scale_widget = pg.GraphicsLayoutWidget()
        self.color_scale_widget.setMaximumSize(150, 300)
        self.color_scale_widget.setMinimumSize(150, 300)
        self.color_scale_widget.hide()
        self.layout = layout
        self.layout.addWidget(self.color_scale_widget)
        self.color_scale_view = self.color_scale_widget.addViewBox(row=0, col=0, enableMouse=False, lockAspect=True)
        self.font = QtGui.QFont('Arial', 13, QtGui.QFont.Bold)
        self.neg_lut = neg_lut
        self.pos_lut = pos_lut
        self.pushButtonInvertColor = QtGui.QPushButton('Invert color')
        self.pushButtonInvertColor.clicked.connect(self.on_invert)
        self.layout.addWidget(self.pushButtonInvertColor)
        self.pushButtonInvertColor.hide()
        self.neg_text_coords = [10, 13]
        self.pos_text_coords = [10, 210]
        self.tstat_label_coords = [-5, 140]

    def update(self, max_pos, min_neg, min_pos, max_neg):
 
        if self.color_scale_view:
            self.color_scale_widget.removeItem(self.color_scale_view)
        self.color_scale_view = self.color_scale_widget.addViewBox(row=0, col=0, enableMouse=False, lockAspect=True)

        self.min_pos_text = pg.TextItem(str(round(min_pos, 2)))
        self.min_neg_text = pg.TextItem(str(round(min_neg, 2)))

        self.max_pos_text = pg.TextItem(str(round(max_pos, 2)))
        self.max_neg_text = pg.TextItem(str(round(max_neg, 2)))

        rgba_pos = []
        for x in range(0, self.pos_lut.shape[1]):
            col = self.pos_lut[:, x]
            slice_ = np.array([col])
            rgba_pos.append(slice_.T)

        rgba_neg = []
        for x in range(0, self.neg_lut.shape[1]):
            col = self.neg_lut[:, x]
            slice_ = np.array([col])
            rgba_neg.append(slice_.T)

        pos_img = np.dstack(tuple(rgba_pos)).astype(np.uint8)
        neg_img = np.dstack(tuple(rgba_neg)).astype(np.uint8)

        full_img = np.rot90(np.vstack((neg_img, pos_img)))

        remove_padding = 0
        # remove the black section of the colormap from the negative scale
        remove_start = int(full_img.shape[1] / 2 - remove_padding)
        remove_end = int(full_img.shape[1] / 2 + remove_padding)
        remove_range = range(remove_start, remove_end)

        full_img = np.delete(full_img, remove_range, axis=1)

        ii = pg.ImageItem(full_img)
        ii.setRect(QtCore.QRect(0, 0, 10, 200))

        self.color_scale_view.addItem(self.max_pos_text)
        self.color_scale_view.addItem(self.min_neg_text)
        self.color_scale_view.addItem(self.min_pos_text)
        self.color_scale_view.addItem(self.max_neg_text)
        self.max_pos_text.setFont(self.font)
        self.min_neg_text.setFont(self.font)
        self.min_pos_text.setFont(self.font)
        self.max_neg_text.setFont(self.font)

        self.max_neg_text.setPos(*self.neg_text_coords)
        self.max_pos_text.setPos(*self.pos_text_coords)
        #min_neg_text.setPos(10, 60)

        self.color_scale_view.addItem(ii)

        # Find how far up the color map the minimum positive  is
        min_pos_y = (full_img.shape[1] / 2) + 20
        min_pos_y_mapped = self.color_scale_view.mapFromItemToView(ii, QtCore.QPointF(40, min_pos_y))
        self.min_pos_text.setPos(9, min_pos_y_mapped.y())

        min_neg_y = full_img.shape[1] / 2 + 80
        min_neg_y_mapped = self.color_scale_view.mapFromItemToView(ii, QtCore.QPointF(40, min_neg_y))
        self.min_neg_text.setPos(13, min_neg_y_mapped.y())

        self.label = pg.TextItem('t-statistics', angle=-90)
        self.label.setFont(self.font)
        self.color = 'white'
        #self.label.setText('t-statistics', self.color)
        self.color_scale_view.addItem(self.label)
        self.label.setPos(*self.tstat_label_coords)
        self.inverted = False


    def redraw(self):
        pass

    def on_invert(self):
        if self.inverted:
            self.inverted = False
            self.label.textItem.setDefaultTextColor(QtGui.QColor(0, 0, 0))
            self.max_pos_text.textItem.setDefaultTextColor(QtGui.QColor(0, 0, 0))
            self.min_pos_text.textItem.setDefaultTextColor(QtGui.QColor(0, 0, 0))
            self.max_neg_text.textItem.setDefaultTextColor(QtGui.QColor(0, 0, 0))
            self.min_neg_text.textItem.setDefaultTextColor(QtGui.QColor(0, 0, 0))
            self.color_scale_widget.setBackground(QtGui.QColor(255, 255, 255))

        else:
            self.inverted = True
            self.label.textItem.setDefaultTextColor(QtGui.QColor(255, 255, 255))
            self.max_pos_text.textItem.setDefaultTextColor(QtGui.QColor(255, 255, 255))
            self.min_pos_text.textItem.setDefaultTextColor(QtGui.QColor(255, 255, 255))
            self.max_neg_text.textItem.setDefaultTextColor(QtGui.QColor(255, 255, 255))
            self.min_neg_text.textItem.setDefaultTextColor(QtGui.QColor(255, 255, 255))
            self.color_scale_widget.setBackground(QtGui.QColor(0, 0, 0))

    def hide(self):
        self.pushButtonInvertColor.hide()
        self.color_scale_widget.hide()
        self.pushButtonInvertColor.hide()

    def show(self):
        self.pushButtonInvertColor.show()
        self.color_scale_widget.show()
        self.pushButtonInvertColor.show()

    def set_minimum_value(self, value):
        pass

    def set_maximum_value(self, value):
        pass