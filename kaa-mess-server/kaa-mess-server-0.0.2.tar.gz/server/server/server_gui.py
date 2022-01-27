'''
This module response for GUI of the server.
'''

import os
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QApplication, QLabel, \
                            QTableView, QDialog, QPushButton, QLineEdit, \
                            QFileDialog, QMessageBox


def gui_create_model(database):
    list_users = database.active_users_list()
    list_table = QStandardItemModel()
    list_table.setHorizontalHeaderLabels(['Contact name', 'IP Address', 'Port', 'Connection time'])
    for row in list_users:
        username, ip_address, port, connection_time = row
        username = QStandardItem(username)
        username.setEditable(False)
        ip_address = QStandardItem(ip_address)
        ip_address.setEditable(False)
        port = QStandardItem(str(port))
        port.setEditable(False)
        connection_time = QStandardItem(str(connection_time.replace(microsecond=0)))
        connection_time.setEditable(False)
        list_table.appendRow([username, ip_address, port, connection_time])
    return list_table


def create_statistic_model(database):
    history_objects_list = database.users_activity_history_list()
    list_table = QStandardItemModel()
    list_table.setHorizontalHeaderLabels(
        ['Client name', 'Last entrance', 'Sent messages', 'Recieved messages']
    )
    for row in history_objects_list:
        username, last_seen, sent, recieved = row
        username = QStandardItem(username)
        username.setEditable(False)
        last_seen = QStandardItem(str(last_seen.replace(microsecond=0)))
        last_seen.setEditable(False)
        sent = QStandardItem(sent)
        sent.setEditable(False)
        recieved = QStandardItem(str(recieved))
        recieved.setEditable(False)
        list_table.appendRow([username, last_seen, sent, recieved])
    return list_table


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        exitAction = QAction('Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(qApp.quit)

        self.refresh_button = QAction('Refresh list', self)
        self.clients_activity_history_button = QAction('Clients activity history', self)
        self.server_config_button = QAction('Server settings', self)

        self.statusBar()

        self.toolbar = self.addToolBar('MainBar')
        self.toolbar.addAction(exitAction)
        self.toolbar.addAction(self.refresh_button)
        self.toolbar.addAction(self.clients_activity_history_button)
        self.toolbar.addAction(self.server_config_button)

        self.setFixedSize(800, 600)
        self.setWindowTitle('Messaging Server alpha release')

        self.label = QLabel('List of connected clients:', self)
        self.label.setFixedSize(400, 15)
        self.label.move(10, 35)

        self.active_users_table = QTableView(self)
        self.active_users_table.move(10, 55)
        self.active_users_table.setFixedSize(780, 400)

        self.show()


class UsersActivityHistoryWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Clients statistics')
        self.setFixedSize(600, 700)
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.close_button = QPushButton('Close', self)
        self.close_button.move(250, 650)
        self.close_button.clicked.connect(self.close)

        self.users_activity_history_table = QTableView(self)
        self.users_activity_history_table.move(10, 10)
        self.users_activity_history_table.setFixedSize(580, 620)

        self.show()


class ServerConfigWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setFixedSize(365, 260)
        self.setWindowTitle('Server settings')

        self.db_path_label = QLabel('Root to the database file', self)
        self.db_path_label.move(10, 10)
        self.db_path_label.setFixedSize(240, 15)

        self.db_path = QLineEdit(self)
        self.db_path.setFixedSize(250, 20)
        self.db_path.move(10, 30)
        self.db_path.setReadOnly(True)

        self.db_path_select = QPushButton('Overview...', self)
        self.db_path_select.move(275, 28)

        def open_file_dialog_window():
            global dialog_window
            dialog_window = QFileDialog(self)
            path = dialog_window.getExistingDirectory()
            path = path.replace('/', '\\')
            self.db_path.insert(path)

        self.db_path_select.clicked.connect(open_file_dialog_window)

        self.db_file_label = QLabel('Database file name:', self)
        self.db_file_label.move(10, 68)
        self.db_file_label.setFixedSize(180, 15)

        self.db_file = QLineEdit(self)
        self.db_file.move(200, 66)
        self.db_file.setFixedSize(150, 20)

        self.port_label = QLabel('Port number for connection:', self)
        self.port_label.move(10, 108)
        self.port_label.setFixedSize(180, 15)

        self.port = QLineEdit(self)
        self.port.move(200, 108)
        self.port.setFixedSize(150, 20)

        self.ip_address_label = QLabel('IP-address for connection:', self)
        self.ip_address_label.move(10, 148)
        self.ip_address_label.setFixedSize(180, 15)

        self.ip_address_label_note = QLabel(
            'Live this field blanc if you want to recieve connections from different addresses', self)
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

        self.show()

if __name__ == '__main__':
    # app = QApplication(sys.argv)
    # main_window = MainWindow()
    # main_window.statusBar().showMessage('Test Statusbar Message')
    # test_list = QStandardItemModel(main_window)
    # test_list.setHorizontalHeaderLabels(['Имя Клиента', 'IP Адрес', 'Порт', 'Время подключения'])
    # test_list.appendRow(
    #     [QStandardItem('test1'), QStandardItem('192.198.0.5'), QStandardItem('23544'), QStandardItem('16:20:34')])
    # test_list.appendRow(
    #     [QStandardItem('test2'), QStandardItem('192.198.0.8'), QStandardItem('33245'), QStandardItem('16:22:11')])
    # main_window.active_users_table.setModel(test_list)
    # main_window.active_users_table.resizeColumnsToContents()
    # app.exec_()

    # ----------------------------------------------------------
    # app = QApplication(sys.argv)
    # dial = ServerConfigWindow()
    #
    # app.exec_()

    # ----------------------------------------------------------
    app = QApplication(sys.argv)
    window = UsersActivityHistoryWindow()
    test_list = QStandardItemModel(window)
    test_list.setHorizontalHeaderLabels(
        ['Имя Клиента', 'Последний раз входил', 'Отправлено', 'Получено'])
    test_list.appendRow(
        [QStandardItem('test1'), QStandardItem('Fri Dec 12 16:20:34 2020'), QStandardItem('2'), QStandardItem('3')])
    test_list.appendRow(
        [QStandardItem('test2'), QStandardItem('Fri Dec 12 16:23:12 2020'), QStandardItem('8'), QStandardItem('5')])
    window.users_activity_history_table.setModel(test_list)
    window.users_activity_history_table.resizeColumnsToContents()

    app.exec_()
