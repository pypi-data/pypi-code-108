from PySide2.QtWidgets import QDialog
from PySide2.QtCore import QFile, Signal
from PySide2.QtUiTools import QUiLoader
from messenger2 import config
import os
from messenger2.server.gui.alert_window import AlertWindow
from messenger2.common.security.hash_password import get_hash_from_password


class RegisterWindow(QDialog):
    """
    Window for register new user
    """
    add_contact = Signal(dict)

    def __init__(self, database, core):
        super(RegisterWindow, self).__init__()
        self.database = database
        self.core = core
        self.alert = None
        self.ui = None
        self.setUI(os.path.join(config.SERVER_UI_DIR, "register_user.ui"))

    def setUI(self, ui_file):
        """
        Set up ui form ui file
        :param ui_file: path to ui file
        :return: None
        """
        ui = QFile(ui_file)
        ui.open(QFile.ReadOnly)
        loader = QUiLoader()
        self.ui = loader.load(ui)
        ui.close()

        self.ui.cancel_btn.clicked.connect(self.close)
        self.ui.register_btn.clicked.connect(self.register_user)

    def register_user(self):
        """
        Register new uer in system
        :return: None
        """
        username = self.ui.user_edit.text()
        password = self.ui.pwd_edit.text()
        repeat_password = self.ui.repeat_pwd_edit.text()
        if len(username) != 0:
            if password == repeat_password and len(
                    password) != 0 and len(repeat_password) != 0:
                if self.database.check_user(login=username):
                    self.alert = AlertWindow(
                        info_msg="Такой пользователь уже существует")
                else:
                    password = get_hash_from_password(
                        password=password, salt=username)
                    self.add_contact.emit(
                        {"user": username, "password": password})
                    self.alert = AlertWindow(info_msg="Пользователь добавлен")
                self.alert.show()
                self.close()
            else:
                self.alert = AlertWindow(info_msg="Пароли не совпадают")
                self.alert.show()
        else:
            self.alert = AlertWindow(info_msg="Не указано имя пользователя")
            self.alert.show()

    def close(self) -> bool:
        """
        Close window
        :return: bool
        """
        return self.ui.close()

    def show(self) -> None:
        """show gui"""
        self.ui.show()
