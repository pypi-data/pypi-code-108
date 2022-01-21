# ----------------------------------------------------------------------
# Author:        yury.matveev@desy.de
# ----------------------------------------------------------------------

"""
"""
APP_NAME = "2DCameraViewer"

import getpass
import shutil
import logging
import os
import psutil
import socket
import pyqtgraph as pg
from pathlib import Path

from PyQt5 import QtWidgets, QtCore

from distutils.util import strtobool

from petra_camera.widgets.about_dialog import AboutDialog
from petra_camera.widgets.camera_widget import CameraWidget
from petra_camera.utils.xmlsettings import XmlSettings

from petra_camera.roisrv.roiserver import RoiServer

from petra_camera.gui.MainWindow_ui import Ui_MainWindow

logger = logging.getLogger(APP_NAME)


# ----------------------------------------------------------------------
class PETRACamera(QtWidgets.QMainWindow):
    """
    """
    LOG_PREVIEW = "gvim"
    STATUS_TICK = 2000              # [ms]

    # ----------------------------------------------------------------------
    def __init__(self, options):
        """
        """
        super(PETRACamera, self).__init__()
        self._ui = Ui_MainWindow()
        self._ui.setupUi(self)

        self._init_menu()
        self._load_ui_settings()

        pg.setConfigOption("background", "w")
        pg.setConfigOption("foreground", "k")
        pg.setConfigOption("leftButtonPan", False)

        self.options = options
        self._settings = self.get_settings(options)
        self._device_list = self._get_cameras_list()
        self._camera_widgets = []
        self._camera_docks = []
        self._add_cameras()

        self._roi_server = []
        if self._settings.has_node('roi_server') and self._settings.option("roi_server", "enable").lower() == "true":
            try:
                self._roi_server = RoiServer(self._settings.option("roi_server", "host"),
                                             self._settings.option("roi_server", "port"),
                                             self._device_list)
                self._roi_server.start()
            except Exception as err:
                logger.exception(err)

        self.setWindowTitle("Camera Viewer ({}@{})".format(getpass.getuser(), socket.gethostname()))

        self._init_status_bar()
        self._status_timer = QtCore.QTimer(self)
        self._status_timer.timeout.connect(self._refresh_status_bar)
        self._status_timer.start(self.STATUS_TICK)

        logger.info("Initialized successfully")

    # ----------------------------------------------------------------------
    def get_settings(self, options):

        home = os.path.join(str(Path.home()), '.petra_camera')
        file_name = str(options.profile)
        if not file_name.endswith('.xml'):
            file_name += '.xml'

        if not os.path.exists(os.path.join(home, file_name)):
            file = QtWidgets.QFileDialog.getOpenFileName(self, 'Cannot find settings file, please locate it',
                                                         str(Path.home()), 'XML settings (*.xml)')
            if file[0]:
                return XmlSettings(file[0])
        else:
            return XmlSettings(os.path.join(home, file_name))

        if not os.path.exists(home):
            os.mkdir(home)

        if not os.path.exists(os.path.join(home, file_name)):
            shutil.copy(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'default_config.xml'),
                        os.path.join(home, 'default.xml'))

        return XmlSettings(os.path.join(home, 'default.xml'))

    # ----------------------------------------------------------------------
    def _get_cameras_list(self):

        cam_list = []
        for device in self._settings.get_nodes('camera_viewer', 'camera'):
            cam_list.append(device.getAttribute('name'))

        cam_list.sort()

        return cam_list

    # ----------------------------------------------------------------------
    def _add_cameras(self):
        """
        Here we making cameras widgets and docking them
        :return:
        """
        self.setCentralWidget(None)

        self.setDockOptions(QtWidgets.QMainWindow.AnimatedDocks |
                            QtWidgets.QMainWindow.AllowNestedDocks |
                            QtWidgets.QMainWindow.AllowTabbedDocks)

        self.setTabPosition(QtCore.Qt.LeftDockWidgetArea, QtWidgets.QTabWidget.North)

        for camera in self._device_list:
            try:
                widget, dock = self.add_dock(CameraWidget, f"{camera}", self, self._settings, camera)
                widget.load_ui_settings()
                dock.setStyleSheet("""QDockWidget {font-size: 14pt; font-weight: bold;}""")
                self._camera_widgets.append(widget)
                self._camera_docks.append(dock)

            except Exception as err:
                open_mgs = QtWidgets.QMessageBox()
                open_mgs.setIcon(QtWidgets.QMessageBox.Critical)
                open_mgs.setWindowTitle(f"Error")
                open_mgs.setText(f"Cannot add {camera}:\n{err}")
                open_mgs.setStandardButtons(QtWidgets.QMessageBox.Ok)
                open_mgs.exec_()

    # ----------------------------------------------------------------------
    def add_dock(self, WidgetClass, label, *args, **kwargs):
        """
        """
        widget = WidgetClass(*args, **kwargs)

        dock = QtWidgets.QDockWidget(label)
        dock.setObjectName("{0}Dock".format("".join(label.split())))
        dock.setWidget(widget)

        children = [child for child in self.findChildren(QtWidgets.QDockWidget)
                    if isinstance(child.widget(), CameraWidget)]
        if children:
            self.tabifyDockWidget(children[-1], dock)
        else:
            self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, dock)

        self.menu_cameras.addAction(dock.toggleViewAction())

        return widget, dock

    # ----------------------------------------------------------------------
    def _show_about(self):
        """
        """
        AboutDialog(self).exec_()

    # ----------------------------------------------------------------------
    def closeEvent(self, event):
        """
        """
        if self.clean_close():
            event.accept()
        else:
            event.ignore()

    # ----------------------------------------------------------------------
    def clean_close(self):
        """
        """
        logger.info("Closing the app...")

        for widget in self._camera_widgets:
            widget.clean_close()

        if hasattr(self, '_roi_server') and self._roi_server:
            logger.info("Stopping ROI server...")
            self._roi_server.stop()

        if hasattr(self, '_status_timer'):
            self._status_timer.stop()

        self._save_ui_settings()

        QtWidgets.qApp.clipboard().clear()
        logger.info("Closed properly")

        return True

    # ----------------------------------------------------------------------
    def _quit_program(self):
        """
        """
        if self.clean_close():
            QtWidgets.qApp.quit()
            # pass

    # ----------------------------------------------------------------------
    def _save_ui_settings(self):
        """Save basic GUI settings.
        """
        settings = QtCore.QSettings(APP_NAME)

        settings.setValue("MainWindow/geometry", self.saveGeometry())
        settings.setValue("MainWindow/state", self.saveState())

        settings.setValue("AutoScreen", self.auto_screen_action.isChecked())

    # ----------------------------------------------------------------------
    def _load_ui_settings(self):
        """Load basic GUI settings.
        """
        settings = QtCore.QSettings(APP_NAME)

        try:
            self.restoreGeometry(settings.value("MainWindow/geometry"))
        except:
            pass

        try:
            self.restoreState(settings.value("MainWindow/state"))
        except:
            pass

        enable_auto_screens = False
        try:
            enable_auto_screens = strtobool(settings.value("AutoScreen"))
        except:
            pass

        self.auto_screen_action.setChecked(enable_auto_screens)
        self._display_auto_screens(enable_auto_screens)

    # ----------------------------------------------------------------------
    def _display_auto_screens(self, state):
        font = self.auto_screen_action.font()

        if state:
            self.auto_screen_action.setText('Auto screens ENABLED')
        else:
            self.auto_screen_action.setText('Auto screens DISABLED')

        font.setBold(state)
        self.auto_screen_action.setFont(font)

    # ----------------------------------------------------------------------
    def _init_menu(self):

        self.menu_cameras = QtWidgets.QMenu('Cameras', self)
        self.menuBar().addMenu(self.menu_cameras)

        self.auto_screen_action = QtWidgets.QAction('', self)
        self.auto_screen_action.setCheckable(True)
        self.auto_screen_action.triggered.connect(self._display_auto_screens)
        self.menuBar().addAction(self.auto_screen_action)

        about_action = QtWidgets.QAction('About', self)
        about_action.triggered.connect(self._show_about)
        self.menuBar().addAction(about_action)

        quit_action = QtWidgets.QAction('Exit', self)
        quit_action.triggered.connect(self._quit_program)
        self.menuBar().addAction(quit_action)

    # ----------------------------------------------------------------------
    def _init_status_bar(self):
        """
        """

        processID = os.getpid()
        currentDir = os.getcwd()

        lbProcessID = QtWidgets.QLabel("PID {}".format(processID))
        lbProcessID.setStyleSheet("QLabel {color: #000066;}")
        lbCurrentDir = QtWidgets.QLabel("{}".format(currentDir))

        # resource usage
        process = psutil.Process(processID)
        mem = float(process.memory_info().rss) / (1024. * 1024.)
        cpu = process.cpu_percent()

        self._lb_resources_status = QtWidgets.QLabel("| {:.2f}MB | CPU {} % |".format(mem, cpu))


        self.statusBar().addPermanentWidget(lbProcessID)
        self.statusBar().addPermanentWidget(lbCurrentDir)
        self.statusBar().addPermanentWidget(self._lb_resources_status)

    # ----------------------------------------------------------------------
    def _refresh_status_bar(self):
        """
        """
        process = psutil.Process(os.getpid())
        mem = float(process.memory_info().rss) / (1024. * 1024.)
        cpu = psutil.cpu_percent()

        self._lb_resources_status.setText("| {:.2f}MB | CPU {} % |".format(mem,
                                                                           cpu))
