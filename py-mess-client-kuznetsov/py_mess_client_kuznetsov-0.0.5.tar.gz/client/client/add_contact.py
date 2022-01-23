import sys
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QLabel, QComboBox, QPushButton, QApplication
import logging

logger = logging.getLogger('client')


class AddContactDialog(QDialog):
    '''
    Dialog for adding a user to the contact list.
    Offers the user a list of possible contacts and
    adds the selected one to the contacts.
    '''

    def __init__(self, transport, database):
        super().__init__()
        self.transport = transport
        self.database = database

        self.setFixedSize(350, 120)
        self.setWindowTitle('Выберите контакт для добавления:')
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setModal(True)

        self.selector_label = QLabel('Выберите контакт для добавления:', self)
        self.selector_label.setFixedSize(200, 20)
        self.selector_label.move(10, 0)

        self.selector = QComboBox(self)
        self.selector.setFixedSize(200, 20)
        self.selector.move(10, 30)

        self.btn_refresh = QPushButton('Обновить список', self)
        self.btn_refresh.setFixedSize(100, 30)
        self.btn_refresh.move(60, 60)

        self.btn_ok = QPushButton('Добавить', self)
        self.btn_ok.setFixedSize(100, 30)
        self.btn_ok.move(230, 20)

        self.btn_cancel = QPushButton('Отмена', self)
        self.btn_cancel.setFixedSize(100, 30)
        self.btn_cancel.move(230, 60)
        self.btn_cancel.clicked.connect(self.close)

        # Fill in the list of possible contacts
        self.possible_contacts_update()
        # Assign an action to the update button
        self.btn_refresh.clicked.connect(self.update_possible_contacts)

    def possible_contacts_update(self):
        '''
        Method of filling in the list of possible contacts.
        Creates a list of all registered users
        except for those already added to contacts and myself.
        '''
        self.selector.clear()
        # sets of all contacts and contacts of the client
        contacts_list = set(self.database.get_contacts())
        users_list = set(self.database.get_users())
        # We will remove ourselves from the list of users so that we cannot add ourselves
        users_list.remove(self.transport.username)
        # Adding a list of possible contacts
        self.selector.addItems(users_list - contacts_list)

    def update_possible_contacts(self):
        '''
        Method for updating the list of possible contacts. Requests from the server
        the list of known users and updates the contents of the window.
        '''
        try:
            self.transport.user_list_update()
        except OSError:
            pass
        else:
            logger.debug('Обновление списка пользователей с сервера выполнено')
            self.possible_contacts_update()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    from database import ClientDatabase
    database = ClientDatabase('test1')
    from transport import ClientTransport
    transport = ClientTransport(7777, '127.0.0.1', database, 'test1')
    window = AddContactDialog(transport, database)
    window.show()
    app.exec_()
