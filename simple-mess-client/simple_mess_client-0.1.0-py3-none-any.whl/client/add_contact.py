import logging
import sys
from PyQt5.QtWidgets import QDialog, QLabel, QComboBox, QPushButton, QApplication
from PyQt5.QtCore import Qt

client_log = logging.getLogger('client')


class AddContactDialog(QDialog):
    """
    Диалоговое окно выбора контакта для добавления.
    """
    def __init__(self, connection, database):
        super().__init__()
        self.connection = connection
        self.database = database

        self.setFixedSize(350, 110)
        self.setWindowTitle('Добавление контакта')
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setModal(True)

        self.selector_label = QLabel('Выберите контакт для добавления:', self)
        self.selector_label.setFixedSize(200, 20)
        self.selector_label.move(10, 0)

        self.selector = QComboBox(self)
        self.selector.setFixedSize(210, 20)
        self.selector.move(10, 30)

        self.btn_refresh = QPushButton('Обновить', self)
        self.btn_refresh.setFixedSize(100, 30)
        self.btn_refresh.move(60, 60)

        self.btn_ok = QPushButton('Добавить', self)
        self.btn_ok.setFixedSize(100, 30)
        self.btn_ok.move(230, 20)

        self.btn_cancel = QPushButton('Отмена', self)
        self.btn_cancel.setFixedSize(100, 30)
        self.btn_cancel.move(230, 60)
        self.btn_cancel.clicked.connect(self.close)

        self.possible_contacts_update()
        self.btn_refresh.clicked.connect(self.update_possible_contacts)

    def possible_contacts_update(self):
        """
        Функция заполнение списка возможных контактов.
        """
        self.selector.clear()
        contacts_list = set(self.database.get_contacts())
        users_list = set(self.database.get_users())
        users_list.remove(self.connection.user_name)
        self.selector.addItems(users_list - contacts_list)

    def update_possible_contacts(self):
        """
        Функция обновление списка возможных контактов.
        """
        try:
            self.connection.get_user_list()
        except OSError:
            pass
        else:
            client_log.debug('Обновление списка пользователей с сервера выполнено')
            self.possible_contacts_update()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    from client_db import ClientStorage
    db = ClientStorage('test1')
    from transport import MessengerClient
    transport = MessengerClient('test1', '127.0.0.1', 7777, db)
    window = AddContactDialog(transport, db)
    window.show()
    app.exec_()
