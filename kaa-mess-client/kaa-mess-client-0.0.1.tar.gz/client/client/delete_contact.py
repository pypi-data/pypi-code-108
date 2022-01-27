'''This module contains classes and method of processing
deleting certain contact in users contact list.
'''

import sys

from PyQt5.QtCore import Qt
from logging import getLogger
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QDialog, QLabel, QComboBox, QPushButton, QApplication

LOG = getLogger('client_logger')


class DelContactDialog(QDialog):
    def __init__(self, database):
        super().__init__()
        self.database = database

        self.setFixedSize(350, 120)
        self.setWindowTitle('Select a contact to delete:')
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setModal(True)

        self.selector_label = QLabel('Select a contact to delete:', self)
        self.selector_label.setFixedSize(200, 20)
        self.selector_label.move(10, 0)

        self.selector = QComboBox(self)
        self.selector.setFixedSize(200, 20)
        self.selector.move(10, 30)

        self.ok_button = QPushButton('Delete', self)
        self.ok_button.setFixedSize(100, 30)
        self.ok_button.move(230, 20)

        self.btn_cancel = QPushButton('Cancel', self)
        self.btn_cancel.setFixedSize(100, 30)
        self.btn_cancel.move(230, 60)
        self.btn_cancel.clicked.connect(self.close)

        self.selector.addItems(sorted(self.database.get_all_client_contacts()))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DelContactDialog(database)
    window.show()
    app.exec_()

