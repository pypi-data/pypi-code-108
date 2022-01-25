# Created by matveyev at 07.04.2021

from PyQt5 import QtWidgets, QtCore

from onlinexml_editor.gui.password_ui import Ui_PasswordSetup
from onlinexml_editor.general_settings import APP_NAME, DEFAULT_SUPERUSER_PASS


# ----------------------------------------------------------------------
class PasswordSetup(QtWidgets.QDialog):
    """
    """

    # ----------------------------------------------------------------------
    def __init__(self, parent):
        super(PasswordSetup, self).__init__(parent)

        self._ui = Ui_PasswordSetup()
        self._ui.setupUi(self)

    # ----------------------------------------------------------------------
    def accept(self):
        superuser_pass = QtCore.QSettings(APP_NAME).value('SuperuserPassword')
        if superuser_pass is None:
            superuser_pass = DEFAULT_SUPERUSER_PASS
        else:
            superuser_pass = str(superuser_pass)

        if str(self._ui.le_current.text()) != superuser_pass:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setText("Current password is wrong")
            msg.setWindowTitle("Error")
            msg.exec_()
            return

        if str(self._ui.le_new.text()) != str(self._ui.le_repeat.text()):
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setText("New password does not match")
            msg.setWindowTitle("Error")
            msg.exec_()
            return

        QtCore.QSettings(APP_NAME).setValue('SuperuserPassword', str(self._ui.le_new.text()))

        super(PasswordSetup, self).accept()
