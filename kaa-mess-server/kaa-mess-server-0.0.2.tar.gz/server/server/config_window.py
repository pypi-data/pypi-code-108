'''
This module processing the establishing of an app configuration.
Creates GUI of configuration server and save the settings.
'''

import os

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, \
                           QPushButton, QFileDialog, QMessageBox


class ConfigWindow(QDialog):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.initUI()

    def initUI(self):
        self.setFixedSize(365, 260)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setModal(True)

        self.db_path_label = QLabel('File path:', self)
        self.db_path_label.move(10, 10)
        self.db_path_label.setFixedSize(240, 15)

        self.db_path = QLineEdit(self)
        self.db_path.move(10, 30)
        self.db_path.setFixedSize(250, 20)
        self.db_path.setReadOnly(True)

        self.db_path_select = QPushButton('Overview...', self)
        self.db_path_select.move(275, 28)

        self.db_file_label = QLabel('Database file name:', self)
        self.db_file_label.move(10, 68)
        self.db_file_label.setFixedSize(180, 15)

        self.db_file = QLineEdit(self)
        self.db_file.move(200, 66)
        self.db_file.setFixedSize(150, 20)

        self.port_label = QLabel('Port number:', self)
        self.port_label.move(10, 108)
        self.port_label.setFixedSize(180, 15)

        self.port = QLineEdit(self)
        self.port.move(200, 108)
        self.port.setFixedSize(150, 20)

        self.ip_address_label = QLabel('IP-address to obtaine connections:', self)
        self.ip_address_label.move(10, 148)
        self.ip_address_label.setFixedSize(180, 15)

        self.ip_address_label_note = QLabel('Leave blanc to obtain from any ip-adresses', self)
        self.ip_address_label_note.move(10, 168)
        self.ip_address_label_note.setFixedSize(500, 30)

        self.ip_address = QLineEdit(self)
        self.ip_address.move(200, 148)
        self.ip_address.setFixedSize(150, 20)

        self.save_button = QPushButton('Save', self)
        self.save_button.move(190, 220)

        self.close_button = QPushButton('Close', self)
        self.close_button.move(275, 220)
        self.close_button.clicked.connect(self.close)

        self.db_path_select.clicked.connect(self.open_file_dialog)
        self.show()

        self.db_path.insert(self.config['SETTINGS']['Database_path'])
        self.db_file.insert(self.config['SETTINGS']['Database_path'])
        self.port.insert(self.config['SETTINGS']['Default_port'])
        self.ip_address.insert(self.config['SETTINGS']['Listen_address'])
        self.save_button.clicked.connect(self.save_server_config)

    def open_file_dialog(self):
        global dialog_window
        dialog_window = QFileDialog(self)
        path = dialog_window.getExistingDirectory()
        path = path.replace('/', '\\')
        self.db_path.clear()
        self.db_path.insert(path)

    def save_server_config(self):
        global config_window
        message = QMessageBox()
        self.config['SETTINGS']['Database_path'] = self.db_path.text()
        self.config['SETTINGS']['Database_file'] = self.db_file.text()
        try:
            port = int(self.port.text())
        except ValueError:
            message.warning(self, 'Error', 'Port should be an integer')
        else:
            self.config['SETTINGS']['Listen_address'] = self.ip_address.text()
            if 1023 < port < 65536:
                self.config['SETTINGS']['Default_port'] = str(port)
                dir_path = os.path.dirname(os.path.realpath(__file__))
                with open(f'{dir_path}/{"server+++.ini"}', 'w') as conf_file:
                    self.config.write(conf_file)
                    message.information(
                        self, 'OK', 'Settings successfully saved')
            else:
                message.warning(
                    self, 'Error', 'Port should be from 1024 to 65536')

