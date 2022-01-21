# Created by matveyev at 19.08.2021
"""
  Widget for individual camera.
  Has 4 dockable widgets: Frame viewer, Settings, ROI & Marker, PeakSearch.
  Also has his own datasource instance

"""

import logging

from functools import partial
from PyQt5 import QtCore, QtWidgets, QtGui

from petra_camera.utils.errors import report_error

from petra_camera.main_window import APP_NAME
from petra_camera.widgets.frame_viewer import FrameViewer
from petra_camera.widgets.settings_widget import SettingsWidget
from petra_camera.widgets.marker_roi import MarkersROIsWidget
from petra_camera.widgets.peak_search_widget import PeakSearchWidget

from petra_camera.devices.datasource2d import DataSource2D
from petra_camera.gui.CameraWidget_ui import Ui_CameraWindow

logger = logging.getLogger(APP_NAME)

# ----------------------------------------------------------------------
class CameraWidget(QtWidgets.QMainWindow):

    REFRESH_PERIOD = 1000 # how often we update the ROIs statistics and sync the settings with Tango

    # ----------------------------------------------------------------------
    def __init__(self, parent, settings, my_name):
        """
        """
        super(CameraWidget, self).__init__(parent)

        self.settings = settings
        self.camera_name = my_name
        self._parent = parent

        self.camera_device = DataSource2D(self)
        state, msg = self.camera_device.new_device_proxy(self.camera_name, self._parent.auto_screen_action.isChecked())
        if not state:
            raise RuntimeError(f'{msg}')

        self._ui = Ui_CameraWindow()
        self._ui.setupUi(self)
        self._init_ui()

        self._refresh_view_timer = QtCore.QTimer(self)
        self._refresh_view_timer.timeout.connect(self._refresh_view)
        self._refresh_view_timer.start(self.REFRESH_PERIOD)

    # ----------------------------------------------------------------------
    def block_hist_signals(self, flag):
        """
            during the picture update in Frame viewer we need to disconnect histogram signals in Setting
        :param flag: bool
        :return:
        """
        self._settings_widget.block_hist_signals(flag)

    # ----------------------------------------------------------------------
    def _start_stop_live_mode(self):
        """

        :return: None
        """

        try:
            self._frame_viewer.start_stop_live_mode(self._parent.auto_screen_action.isChecked())
        except Exception as err:
            self._log.exception(err)
            report_error(err)

    # ----------------------------------------------------------------------
    def clean_close(self):
        """

        :return: None
        """
        logger.info(f"Closing {self.camera_name}...")

        self._settings_widget.close()
        self._frame_viewer.close(self._parent.auto_screen_action.isChecked())

        self.camera_device.close_camera()

        self._frame_viewer.save_ui_settings(self.camera_name)
        self._settings_widget.save_ui_settings(self.camera_name)
        self._markerroi_widget.save_ui_settings(self.camera_name)
        self._peak_search_widget.save_ui_settings(self.camera_name)

        self._save_ui_settings()

        logger.info(f"{self.camera_name} closed.")

    # ----------------------------------------------------------------------
    def _refresh_view(self):
        """

        :return: None
        """

        try:
            state = self.camera_device.is_running()
            if state is None:
                self._action_start_stop.setIcon(QtGui.QIcon(":/ico/play_16px.png"))
                self._action_start_stop.setEnabled(False)
            elif state:
                self._action_start_stop.setIcon(QtGui.QIcon(":/ico/stop.png"))
                self._action_start_stop.setEnabled(True)
            else:
                self._action_start_stop.setIcon(QtGui.QIcon(":/ico/play_16px.png"))
                self._action_start_stop.setEnabled(True)
        except Exception as err:
            logger.exception(f"Exception: camera state: {err}")

        if self._settings_widget.isVisible():
            self._settings_widget.refresh_view()

    # ----------------------------------------------------------------------
    def _display_fps(self, fps):
        """

        :param fps: value, int
        :return: None
        """
        self._lb_fps.setText("{:.2f} FPS".format(fps))

    # ----------------------------------------------------------------------
    def _viewer_cursor_moved(self, x, y):
        """

        :param x: mouse coordinate
        :param y: mouse coordinate
        :return: None
        """
        self._lb_cursor_pos.setText("({:.2f}, {:.2f})".format(x, y))

    # ----------------------------------------------------------------------
    # -------------------- UI initialization -------------------------------
    # ----------------------------------------------------------------------
    def _init_ui(self):

        self._init_tool_bar()

        self._init_status_bar()

        self._load_docks()

        self._connect_signals()

    # ----------------------------------------------------------------------
    def _load_docks(self):
        """
         here we loads all widgets, dock them
        """
        self.setCentralWidget(None)

        self.setDockOptions(QtWidgets.QMainWindow.AnimatedDocks |
                            QtWidgets.QMainWindow.AllowNestedDocks |
                            QtWidgets.QMainWindow.AllowTabbedDocks)

        self._frame_viewer, self._frameViewer_dock = \
            self._add_dock(FrameViewer, "Frame", self)

        self._settings_widget, self._settings_dock = \
            self._add_dock(SettingsWidget, "Settings", self)

        self._markerroi_widget, self._markerroi_dock = \
            self._add_dock(MarkersROIsWidget, "Markers/ROIs", self)

        self._peak_search_widget, self._peak_search_dock = \
            self._add_dock(PeakSearchWidget, "Peak Search", self)

        # after all widgets are loaded we restore the user layout
        self._frame_viewer.load_ui_settings(self.camera_name)
        self._settings_widget.load_ui_settings(self.camera_name)
        self._markerroi_widget.load_ui_settings(self.camera_name)
        self._peak_search_widget.load_ui_settings(self.camera_name)

        # link between picture and histogram
        self._settings_widget.set_frame_to_hist(self._frame_viewer.get_image_view())
        self._frame_viewer.set_hist(self._settings_widget.get_hist())

    # ----------------------------------------------------------------------
    def _connect_signals(self):
        """
            connect signals between widgets
        :return: None
        """

        self._frame_viewer.new_fps.connect(self._display_fps)
        self._frame_viewer.cursor_moved.connect(self._viewer_cursor_moved)

        self.camera_device.new_frame.connect(self._frame_viewer.new_frame)

        self.camera_device.update_roi_statistics.connect(self._markerroi_widget.update_roi_statistics)
        self.camera_device.update_roi_statistics.connect(self._frame_viewer.repaint_roi)

        self.camera_device.update_peak_search.connect(self._frame_viewer.repaint_peak_search)

        self.camera_device.got_error.connect(lambda err_msg: report_error(err_msg, self, True))

        self._markerroi_widget.add_remove_marker.connect(self._frame_viewer.add_remove_marker)
        self._markerroi_widget.repaint_marker.connect(self._frame_viewer.repaint_marker)

        self._markerroi_widget.add_remove_roi.connect(self._frame_viewer.add_remove_roi)
        self._markerroi_widget.repaint_roi.connect(self._frame_viewer.repaint_roi)

        self._action_start_stop.triggered.connect(self._start_stop_live_mode)
        self._action_print_image.triggered.connect(self._frame_viewer.print_image)
        self._action_copy_image.triggered.connect(self._frame_viewer.to_clipboard)

        self._saveImgAction.triggered.connect(self._frame_viewer.save_to_image)
        self._saveAsciiAction.triggered.connect(partial(self._frame_viewer.save_to_file, fmt="csv"))
        self._saveNumpyAction.triggered.connect(partial(self._frame_viewer.save_to_file, fmt="npy"))

    # ----------------------------------------------------------------------
    def _add_dock(self, WidgetClass, label, *args, **kwargs):

        widget = WidgetClass(*args, **kwargs)

        dock = QtWidgets.QDockWidget(label)
        dock.setObjectName("{0}Dock".format("".join(label.split())))
        dock.setStyleSheet("""QDockWidget {font-size: 11pt; font-weight: normal}""")
        dock.setWidget(widget)

        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, dock)

        self.tool_bar.addAction(dock.toggleViewAction())

        return widget, dock

    # ----------------------------------------------------------------------
    def _make_save_menu(self, parent):
        """
        Args:
            parent (QWidget)
        """
        saveMenu = QtWidgets.QMenu(parent)

        self._saveImgAction = saveMenu.addAction("Image")

        self._saveAsciiAction = saveMenu.addAction("ASCII")

        self._saveNumpyAction = saveMenu.addAction("Numpy")

        return saveMenu

    # ----------------------------------------------------------------------
    def _init_tool_bar(self):
        """
        """

        self.tool_bar = QtWidgets.QToolBar("Main toolbar", self)
        self.tool_bar.setObjectName("CameraViewer_ToolBar")

        self._action_start_stop = QtWidgets.QAction(self)
        self._action_start_stop.setIcon(QtGui.QIcon(":/ico/play_16px.png"))
        self._action_start_stop.setText("Start/Stop")

        self.tool_bar.addAction(self._action_start_stop)
        self.tool_bar.addSeparator()

        # image saving
        self._tbSaveScan = QtWidgets.QToolButton(self)
        self._tbSaveScan.setIcon(QtGui.QIcon(":/ico/save.png"))
        self._tbSaveScan.setToolTip("Save")

        self._saveMenu = self._make_save_menu(self._tbSaveScan)
        self._tbSaveScan.setMenu(self._saveMenu)
        self._tbSaveScan.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        self.tool_bar.addWidget(self._tbSaveScan)

        self._action_print_image = QtWidgets.QAction(self)
        self._action_print_image.setIcon(QtGui.QIcon(":/ico/print.png"))
        self._action_print_image.setText("Print Image")
        self._action_print_image.setEnabled(False)
        self.tool_bar.addAction(self._action_print_image)

        self._action_copy_image = QtWidgets.QAction(self)
        self._action_copy_image.setIcon(QtGui.QIcon(":/ico/copy.png"))
        self._action_copy_image.setText("Copy to Clipboard")
        self.tool_bar.addAction(self._action_copy_image)

        self.tool_bar.addSeparator()
        self.tool_bar.addWidget(QtWidgets.QLabel('Widgets:'))

        self.addToolBar(self.tool_bar)

    # ----------------------------------------------------------------------
    def _init_status_bar(self):

        self._lb_cursor_pos = QtWidgets.QLabel("")

        self._lb_fps = QtWidgets.QLabel("FPS: -")
        self._lb_fps.setMinimumWidth(70)

        self.statusBar().addPermanentWidget(self._lb_cursor_pos)
        self.statusBar().addPermanentWidget(self._lb_fps)

    # ----------------------------------------------------------------------
    def _save_ui_settings(self):
        """Save basic GUI settings.
        """
        settings = QtCore.QSettings(APP_NAME)

        settings.setValue(f"{self.camera_name}/geometry", self.saveGeometry())
        settings.setValue(f"{self.camera_name}/state", self.saveState())

    # ----------------------------------------------------------------------
    def load_ui_settings(self):
        """Load basic GUI settings.
        """
        settings = QtCore.QSettings(APP_NAME)

        try:
            self.restoreGeometry(settings.value(f"{self.camera_name}/geometry"))
        except:
            pass

        try:
            self.restoreState(settings.value(f"{self.camera_name}/state"))
        except:
            pass
