# Copyright 2016 Medical Research Council Harwell.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# @author Neil Horner <n.horner@har.mrc.ac.uk>


from pathlib import Path
from vpv import __version__
from vpv import resources
from PyQt5 import QtGui, QtCore, QtWidgets
from vpv.ui.views.ui_main_window import Ui_MainWindow
from vpv.common import style_sheet_path, question_dialog


class Mainwindow(QtWidgets.QMainWindow, Ui_MainWindow):
    hide_view_signal = QtCore.pyqtSignal(int)
    d_pressed_signal = QtCore.pyqtSignal()
    key_up_down_signal= QtCore.pyqtSignal(bool)
    toggle_volume1_visibility_signal = QtCore.pyqtSignal()  # main image
    toggle_volume2_visibility_signal = QtCore.pyqtSignal()  # Label map or other overlay
    key_event_signal = QtCore.pyqtSignal(QtGui.QKeyEvent)

    def __init__(self, controller, appdata):
        """

        Parameters
        ----------
        controller: vpv.vpv_temp
        appdata
        """

        super(Mainwindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("VPV")
        icon_path = Path(resources.__file__).parent / 'vpv.png'
        self.setWindowIcon(QtGui.QIcon(str(icon_path)))
        self.setWindowIconText('VPV')

        self.view_layout = QtGui.QGridLayout()
        self.manager_layout = QtGui.QVBoxLayout()
        self.ui.horizontalLayoutMain.addLayout(self.manager_layout)
        self.ui.horizontalLayoutMain.addLayout(self.view_layout)

        self.controller = controller
        self.appdata = appdata
        self.view_widgets = {}  # { (row, col): widget}

        # self.installEventFilter(self)

        #### Menus #####################################################################################################

        menubar = QtGui.QMenuBar()
        view_menu = QtGui.QMenu("View", self)
        info_menu = QtGui.QMenu("Info", self)
        data_menu = QtGui.QMenu("Data", self)
        self.recent_menu = QtGui.QMenu("Recently used", self)

        self.view_fullscreen_action = QtGui.QAction('Full screen', view_menu, checkable=True)
        self.view_fullscreen_action.setChecked(False)
        self.view_fullscreen_action.triggered.connect(self.on_view_full_screen)
        view_menu.addAction(self.view_fullscreen_action)

        self.view_slider_action = QtGui.QAction('Sliders', view_menu, checkable=True)
        self.view_slider_action.setChecked(True)
        self.view_slider_action.triggered.connect(self.on_checkbox_index_slider)
        view_menu.addAction(self.view_slider_action)

        self.view_overlay_controls_action = QtGui.QAction('Overlay controls', view_menu, checkable=True)
        self.view_overlay_controls_action.triggered.connect(self.on_checkbox_overlay_controls)
        self.view_overlay_controls_action.setChecked(True)
        view_menu.addAction(self.view_overlay_controls_action)

        self.view_vol_id_action = QtGui.QAction('Show data labels', view_menu, checkable=True)
        self.view_vol_id_action.triggered.connect(self.on_action_show_data_labels)
        self.view_vol_id_action.setChecked(True)
        view_menu.addAction(self.view_vol_id_action)

        self.scale_bars_action = QtGui.QAction('Show scale bars', view_menu, checkable=True)
        self.scale_bars_action.triggered.connect(self.on_action_show_scale_bars)
        self.scale_bars_action.setChecked(True)
        view_menu.addAction(self.scale_bars_action)

        self.color_bars_action = QtGui.QAction('Show colour scale bars', view_menu, checkable=True)
        self.color_bars_action.triggered.connect(self.on_action_show_color_scale_bars)
        self.color_bars_action.setChecked(False)
        view_menu.addAction(self.color_bars_action)

        self.view_perm_crosshair_action = QtGui.QAction('Persistent crosshairs', view_menu, checkable=True)
        self.view_perm_crosshair_action.triggered.connect(self.on_action_perm_crosshair)
        self.view_perm_crosshair_action.setChecked(False)
        view_menu.addAction(self.view_perm_crosshair_action)

        self.ori_indication_visible_action = QtGui.QAction('Orientation labels', view_menu, checkable=True)
        self.ori_indication_visible_action.triggered.connect(self.on_action_orientation_labels)
        self.ori_indication_visible_action.setChecked(True)  # Todo this should be saved in appdata
        view_menu.addAction(self.ori_indication_visible_action)

        self.load_data_action = QtGui.QAction('Load data', data_menu, checkable=False)
        self.load_data_action.triggered.connect(self.controller.browse_files)
        data_menu.addAction(self.load_data_action)

        self.clear_data_action = QtGui.QAction('Clear data', data_menu, checkable=False)
        self.clear_data_action.triggered.connect(self.controller.clear_views)
        data_menu.addAction(self.clear_data_action)

        self.recent_menu.addAction('Clear')
        for r in self.appdata.get_recent_files():
            self.recent_menu.addAction(str(r))

        self.recent_menu.triggered.connect(self.on_recent_menu)

        self.version_action = QtGui.QAction('Version: {}'.format(__version__), view_menu, checkable=False)
        info_menu.addAction(self.version_action)

        self.window_title_action = QtGui.QAction('Edit Window title', info_menu, checkable=False)
        self.window_title_action.triggered.connect(self.edit_window_title)
        info_menu.addAction(self.window_title_action)

        self.show_log_action = QtGui.QAction('Show log', data_menu, checkable=False)
        self.show_log_action.triggered.connect(self.controller.show_log)
        info_menu.addAction(self.show_log_action)

        menubar.addMenu(info_menu)
        menubar.addMenu(view_menu)
        menubar.addMenu(data_menu)
        menubar.addMenu(self.recent_menu)
        self.ui.toolBar.addWidget(menubar)

        self.mouse_position_label = QtGui.QLabel(self)
        self.mouse_position_label.setStyleSheet("QLabel {color : white; }")
        self.mouse_position_label.setFixedWidth(120)
        self.mouse_position_label.show()
        self.ui.toolBar.addWidget(self.mouse_position_label)

        self.volume_pix_val_label = QtGui.QLabel(self)
        self.volume_pix_val_label.setStyleSheet("QLabel {color : white; }")
        self.volume_pix_val_label.setFixedWidth(80)
        self.ui.toolBar.addWidget(self.volume_pix_val_label)

        self.volume2_pix_val_label = QtGui.QLabel(self)
        self.volume2_pix_val_label.setStyleSheet("QLabel {color : white; }")
        self.volume2_pix_val_label.setFixedWidth(80)
        self.ui.toolBar.addWidget(self.volume2_pix_val_label)

        self.data_pix_val_label = QtGui.QLabel(self)
        self.data_pix_val_label.setStyleSheet("QLabel {color : white; }")
        self.data_pix_val_label.setFixedWidth(80)
        self.ui.toolBar.addWidget(self.data_pix_val_label)

        self.atlas_label_name_label = QtGui.QLabel(self)
        self.atlas_label_name_label.setStyleSheet("QLabel {color : white; }")
        self.atlas_label_name_label.setFixedWidth(240)
        self.ui.toolBar.addWidget(self.atlas_label_name_label)

        self.ui.toolBar.setMinimumHeight(30)

        self.setAcceptDrops(True)
        ################################################################################################################
        self.show()

        with open(style_sheet_path, 'r') as fh:
            self.setStyleSheet(fh.read())

    def edit_window_title(self):
        text, ok = QtGui.QInputDialog.getText(self, 'Change VPV window title', 'New title:')
        if ok:
            self.setWindowTitle(text)

    def show_manager(self, widget):
        self.manager_layout.addWidget(widget, 0)

    def on_action_orientation_labels(self, checked):
        self.controller.set_orientation_visibility(checked)

    def on_action_show_color_scale_bars(self, checked):
        self.controller.show_color_scale_bars(checked)

    def on_action_show_scale_bars(self, checked):
        self.controller.show_scale_bars(checked)

    def set_mouse_position_indicator(self, x, y, z):
        self.mouse_position_label.setText("x:{} y:{} z:{}".format(x, y, z))

    def set_volume_pix_intensity(self, value):
        self.volume_pix_val_label.setText('vol: {}  '.format(value))

    def set_volume2_pix_intensity(self, value):
        self.volume2_pix_val_label.setText('vol2: {}  '.format(value))

    def set_current_label(self, label: str):
        self.atlas_label_name_label.setText(label)

    def set_data_pix_intensity(self, value):
        self.data_pix_val_label.setText('data: {}  '.format(value))

    def on_recent_menu(self, action):
        if action.text() == 'Clear':
            self.appdata.clear_recent()
            self.recent_menu.clear()
            return
        self.controller.load_volumes([action.text()], 'vol') # Only works with normal image volumes for now

    def on_stats_action(self):
        self.controller.stats()

    def keyPressEvent(self, event):
        """
        Define keyboard shortcuts.
        These should be processed in the VPV main module
        """

        if self.controller.qc.is_active:  # QC-specific shortcuts
            if event.key() == QtCore.Qt.Key_AltGr:
                self.controller.qc.next_specimen()

        if event.key() == QtCore.Qt.Key_Escape:
            self.on_view_full_screen(False)  # Doesn't do anything yet
        elif event.key() == QtCore.Qt.Key_F11:
            if self.isFullScreen():
                self.on_view_full_screen(False)
            else:
                self.on_view_full_screen(True)
        elif event.key() == QtCore.Qt.Key_Space:
            self.controller.toggle_dock_widget_visibility()
        elif event.key() == QtCore.Qt.Key_L:
            self.controller.toggle_link_views()
        elif event.key() == QtCore.Qt.Key_Z:
            visible = self.view_slider_action.isChecked()
            self.view_slider_action.toggle()
            self.on_checkbox_index_slider(visible)
        elif event.key() == QtCore.Qt.Key_P:
            self.controller.take_screen_shot()
        elif event.key() == QtCore.Qt.Key_D:
            self.d_pressed_signal.emit()
        elif event.key() == QtCore.Qt.Key_2:
            self.toggle_volume2_visibility_signal.emit()
        elif event.key() == QtCore.Qt.Key_1:
            self.toggle_volume1_visibility_signal.emit()
        else:
            # TODO all events should be propagated this way to man VPV module
            self.key_event_signal.emit(event)

    def on_view_full_screen(self, checked):
        if checked:
            self.showFullScreen()
            self.view_fullscreen_action.setChecked(True)
        else:
            self.showNormal()
            self.view_fullscreen_action.setChecked(False)

    def dragEnterEvent(self, event):
        event.accept()

    def dropEvent(self, event):
        dragged_files = [(v.toLocalFile()) for v in event.mimeData().urls()]
        print(dragged_files)
        self.controller.load_data_slot(dragged_files)

    def remove_slice_view(self, row, column):
        pass

    def add_slice_view(self, slice_widget, row, column):
        """
        Add a SliceWidget object to the GraphicsLayout widget
        Volume object contains a Viewbox that contains ImageItems that holds a slice of the image
        :param slice_widget:
        :param row:
        :param column:
        """
        self.view_widgets[(row, column)] = slice_widget

        # Add the slice widget to the actual layout
        self.view_layout.addWidget(slice_widget, row, column)

    def slice_widget_visibility(self):
        """
        Recieves signal from button used to show/hide the different slice views
        The sender QPushButton is identified using sender(). The sender has the corresponding SliceWidget ref attached
        to it, which can be accessed to show/hide
        :return:
        """
        if self.sender().slice_view_ref.isHidden():
            self.sender().slice_view_ref.show()
        else:
            self.sender().slice_view_ref.hide()


    def viewlevels(self, checked):
        if checked:
            for view in self.slices:
                pass

    def opacity_change(self, value):
        opacity = 1.0 / value
        if value == 10:
            opacity = 0

    def on_checkbox_overlay_controls(self, checked):
        self.controller.control_visiblity(checked)

    def on_checkbox_index_slider(self, checked):
        """
        Show/hide slice slider on each slice widget
        :param checked:
        :return:
        """
        self.controller.set_view_controls_visibility(checked)

    def on_action_scalebar(self, checked):
        self.controller.scale_bar_visible(checked)

    def on_action_perm_crosshair(self, checked):
        self.controller.set_crosshair_permanent(checked)

    def on_action_show_data_labels(self, checked):
        self.controller.data_labels_visible(checked)

    def closeEvent(self, evnt):

        close = question_dialog(self, 'Close', 'Do you want to exit?')

        if not close:
            evnt.ignore()
        else:
            self.controller.close()

    def data_processing_slot(self):
        self.progress_dialog = QtGui.QProgressDialog('Rendering...', 'cancel', 0, 0, self)
        #p.connect_close_slot(self.controller.data_processing_finished_signal)
        self.controller.data_processing_finished_signal.connect(self.progress_dialog.close)
        self.progress_dialog.show()


class ProgressIndicator(QtCore.QThread):
    def __init__(self, parent):
        QtCore.QThread.__init__(self, parent)
        self.progress_dialog = QtGui.QProgressDialog('Rendering...', 'cancel', 0, 0, parent)


    def connect_close_slot(self, signal):
        pass
        #signal.connect(self.progress_dialog.close)

    def run(self):
        self.progress_dialog.show()

