# Created by matveyev at 07.04.2021

import os

from PyQt5 import QtWidgets, QtCore

from onlinexml_editor.gui.settings_ui import Ui_AppSettings
from onlinexml_editor.password import PasswordSetup
from onlinexml_editor.general_settings import APP_NAME, DEFAULT_SUPERUSER_PASS


# ----------------------------------------------------------------------
class AppSettings(QtWidgets.QDialog):
    """
    """

    # ----------------------------------------------------------------------
    def __init__(self, parent):
        super(AppSettings, self).__init__(parent)

        self._ui = Ui_AppSettings()
        self._ui.setupUi(self)

        self.online_path = ''

        settings = QtCore.QSettings(APP_NAME)

        try:
            self.restoreGeometry(settings.value("Settings/geometry"))
        except:
            pass

        path = settings.value('OnlinePath')
        if path is not None:
            self._ui.le_online_path.setText(str(path))

        try:
            if bool(settings.value("DefaultSuperuser")):
                self._ui.rb_superuser.setChecked(True)
            else:
                self._ui.rb_regular_user.setChecked(True)
        except:
            pass

        self._ui.bg_user_role.buttonClicked.connect(self._change_role)
        self._ui.cmd_online_path.clicked.connect(self._change_online_path)
        self._ui.cmd_superuser_pass.clicked.connect(self._set_pass)

    # ----------------------------------------------------------------------
    def _block_signals(self, flag):
        self._ui.rb_superuser.blockSignals(flag)
        self._ui.rb_regular_user.blockSignals(flag)
        self._ui.le_lib_path.blockSignals(flag)
        self._ui.le_online_path.blockSignals(flag)

    # ----------------------------------------------------------------------
    def _set_pass(self):
        PasswordSetup(self).exec_()

    # ----------------------------------------------------------------------
    def _change_role(self, button):
        superuser_pass = QtCore.QSettings(APP_NAME).value('SuperuserPassword')
        if superuser_pass is None:
            superuser_pass = DEFAULT_SUPERUSER_PASS
        else:
            superuser_pass = str(superuser_pass)

        self._block_signals(True)
        if button == self._ui.rb_superuser:
            text, okPressed = QtWidgets.QInputDialog.getText(self, "Password", "Superuser password:",
                                                             QtWidgets.QLineEdit.Password, "")
            if okPressed and text != '':
                if text != superuser_pass:
                    self._ui.rb_regular_user.setChecked(True)
                else:
                    self._ui.rb_superuser.setChecked(True)

        self._block_signals(False)

    # ----------------------------------------------------------------------
    def _change_online_path(self):
        file, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Online.xml file', os.getcwd(), 'online.xml (online.xml)')
        if file:
            self._ui.le_online_path.setText(file)

    # ----------------------------------------------------------------------
    def accept(self):
        all_ok = True
        error_text = ''

        self.online_path = str(self._ui.le_online_path.text())

        if not os.path.exists(self.online_path):
            all_ok *= False
            error_text += 'The online.xml path does not exist\n'

        if not all_ok:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setText("Cannot save settings due to following errors:")
            msg.setInformativeText(error_text)
            msg.setWindowTitle("Error")
            msg.exec_()
            return

        settings = QtCore.QSettings(APP_NAME)
        settings.setValue('OnlinePath', self.online_path)

        if self._ui.rb_superuser.isChecked():
            settings.setValue('DefaultSuperuser', True)
        else:
            settings.setValue('DefaultSuperuser', False)

        QtCore.QSettings(APP_NAME).setValue("Settings/geometry", self.saveGeometry())
        super(AppSettings, self).accept()

    # ----------------------------------------------------------------------
    def reject(self):
        QtCore.QSettings(APP_NAME).setValue("Settings/geometry", self.saveGeometry())
        super(AppSettings, self).reject()

