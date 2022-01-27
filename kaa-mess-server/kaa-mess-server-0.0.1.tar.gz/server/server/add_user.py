'''
This module processing register user on the server.
'''

import hashlib
import binascii

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QPushButton, QLineEdit, \
                           QApplication, QLabel, QMessageBox


class RegisterUser(QDialog):
    def __init__(self, database_obj, server_obj):
        super().__init__()

        self.database = database_obj
        self.server = server_obj

        self.setFixedSize(175, 183)
        self.setModal(True)
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.label_username = QLabel('Enter username:', self)
        self.label_username.move(10, 10)
        self.label_username.setFixedSize(150, 15)

        self.client_name = QLineEdit(self)
        self.client_name.move(10, 30)
        self.client_name.setFixedSize(154, 20)

        self.label_password = QLabel('Enter password:', self)
        self.label_password.move(10, 55)
        self.label_password.setFixedSize(150, 15)

        self.client_password = QLineEdit(self)
        self.client_password.move(10, 75)
        self.client_password.setFixedSize(154, 20)
        self.client_password.setEchoMode(QLineEdit.Password)

        self.label_password_confirm = QLabel('Confirm password:', self)
        self.label_password_confirm.move(10, 100)
        self.label_password_confirm.setFixedSize(150, 15)

        self.client_password_confirm = QLineEdit(self)
        self.client_password_confirm.move(10, 120)
        self.client_password_confirm.setFixedSize(154, 20)
        self.client_password_confirm.setEchoMode(QLineEdit.Password)

        self.ok_button = QPushButton('Save', self)
        self.ok_button.move(10, 150)
        self.ok_button.clicked.connect(self.save_data)

        self.cancel_button = QPushButton('Exit', self)
        self.cancel_button.move(90, 150)
        self.cancel_button.clicked.connect(self.close)

        self.messages = QMessageBox()
        self.show()

    def save_data(self):
        '''Save new user in database.'''

        if not self.client_name.text():
            self.message.critical(
                self, 'Error', 'No username')
            return
        elif self.client_password.text() != self.client_password_confirm.text():
            self.messages.critical(
                self, 'Error', 'Entered passwords are not equal')
            return
        elif self.database.check_user(self.client_name.text()):
            self.message.critical(
                self, 'Error', 'User already exists')
            return
        else:
            password_bytes = self.client_password.text().encode('utf-8')
            salt = self.client_name.text().lower().encode('utf-8')
            password_hash_obj = hashlib.pbkdf2_hmac(
                'sha512', password_bytes, salt, 10000)
            self.database.add_user(
                self.client_name.text(),
                binascii.hexlify(password_hash_obj))
            self.messages.information(
                self, 'Success', 'User successfully registered')
            self.server_obj.service_update_list()
            self.close()


if __name__ == '__main__':
    APP = QApplication([])
    from server_db_storage import ServerDatabaseStorage
    database = ServerDatabaseStorage('server_base.db3')
    from core import MessageProcessor
    server = MessageProcessor('127.0.0.1', 7777, database)
    dialog_window = RegisterUser(database, server)
    APP.exec_()
