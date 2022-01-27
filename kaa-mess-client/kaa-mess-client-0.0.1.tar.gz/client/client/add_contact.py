'''
This module of creating, registering a new client in project.
'''

import sys

from PyQt5.QtCore import Qt
from logging import getLogger
from PyQt5.QtWidgets import QDialog, QLabel, QComboBox, QPushButton, QApplication

sys.path.append('../')

LOG = getLogger('client_logger')


class AddContactDialog(QDialog):
    '''Create model of adding contact to database'''

    def __init__(self, transport, database):
        super().__init__()
        self.transport = transport
        self.database = database

        self.setFixedSize(350, 120)
        self.setWindowTitle('Select a contact to add:')
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setModal(True)

        self.selector_label = QLabel('Select a contact to add:', self)
        self.selector_label.setFixedSize(200, 20)
        self.selector_label.move(10, 0)

        self.selector = QComboBox(self)
        self.selector.setFixedSize(200, 20)
        self.selector.move(10, 30)

        self.btn_refresh = QPushButton('Update list', self)
        self.btn_refresh.setFixedSize(100, 30)
        self.btn_refresh.move(60, 60)

        self.ok_button = QPushButton('Add', self)
        self.ok_button.setFixedSize(100, 30)
        self.ok_button.move(230, 20)

        self.btn_cancel = QPushButton('Cancel', self)
        self.btn_cancel.setFixedSize(100, 30)
        self.btn_cancel.move(230, 60)
        self.btn_cancel.clicked.connect(self.close)

        self.available_contacts_update()
        self.btn_refresh.clicked.connect(self.update_available_contacts)

    def available_contacts_update(self):
        '''Method create available users' contacts list'''

        self.selector.clear()
        contacts_list = set(self.database.get_all_client_contacts())
        users_list = set(self.database.get_all_known_users())
        users_list.remove(self.transport.username)
        self.selector.addItems(users_list - contacts_list)

    def update_available_contacts(self):
        '''Method update users' contacts list'''

        try:
            self.transport.user_list_update()
        except OSError:
            pass
        else:
            LOG.debug('Updating the list of users from the server is done')
            self.available_contacts_update()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    from client_db_storage import ClientDatabaseStorage
    database = ClientDatabaseStorage('test1')
    from transport import ClientTransport
    transport = ClientTransport(7777, '127.0.0.1', database, 'test1')
    window = AddContactDialog(transport, database)
    window.show()
    app.exec_()

