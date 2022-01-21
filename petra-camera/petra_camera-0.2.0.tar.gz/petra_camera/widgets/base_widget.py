# Created by matveyev at 19.08.2021

import logging

from PyQt5 import QtCore, QtWidgets

from petra_camera.main_window import APP_NAME

WIDGET_NAME = None
SAVE_STATE_UIS = []

logger = logging.getLogger(APP_NAME)


# ----------------------------------------------------------------------
class BaseWidget(QtWidgets.QWidget):

    # ----------------------------------------------------------------------
    def __init__(self, camera_widget):

        super(BaseWidget, self).__init__(camera_widget)

        self._parent = camera_widget
        self._settings = camera_widget.settings
        self._camera_device = camera_widget.camera_device

    # ----------------------------------------------------------------------
    def save_ui_settings(self, camera_name):
        """
        """
        settings = QtCore.QSettings(APP_NAME)
        for uis in SAVE_STATE_UIS:
            settings.setValue(f"{WIDGET_NAME}_{camera_name}/f{uis}", getattr(self._ui, uis).saveState())

        settings.setValue(f"{WIDGET_NAME}_{camera_name}/geometry", self.saveGeometry())

    # ----------------------------------------------------------------------
    def load_ui_settings(self, camera_name):
        """
        """
        settings = QtCore.QSettings(APP_NAME)
        for uis in SAVE_STATE_UIS:
            try:
                getattr(self._ui, uis).restoreState(settings.value(f"{WIDGET_NAME}_{camera_name}/f{uis}"))
            except:
                pass

        try:
            self.restoreGeometry(settings.value(f"{WIDGET_NAME}_{camera_name}/geometry"))
        except:
            pass
