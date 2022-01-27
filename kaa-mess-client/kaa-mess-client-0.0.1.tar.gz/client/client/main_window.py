'''The main module of creating GUI of the client side project part'''

import sys
import json
import base64

from logging import getLogger
from Cryptodome.PublicKey import RSA
from Cryptodome.Cipher import PKCS1_OAEP
from PyQt5.QtCore import pyqtSlot, Qt, QEvent
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QBrush, QColor
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QApplication, qApp, QListView

sys.path.append('../')
from errors import ServerError
from common.variables import *
from client.add_contact import AddContactDialog
from client.delete_contact import DelContactDialog
from client.main_window_conv import Ui_MainClientWindow


LOG = getLogger('client_logger')


class ClientMainWindow(QMainWindow):
    '''Class  of main client side window'''

    def __init__(self, database_obj, transport_obj, keys):
        super().__init__()
        self.database = database_obj
        self.transport = transport_obj

        self.decrypter = PKCS1_OAEP.new(keys)

        self.ui = Ui_MainClientWindow()
        self.ui.setupUi(self)
        self.ui.menu_exit.triggered.connect(qApp.exit)
        self.ui.btn_send.clicked.connect(self.send_message)
        self.ui.btn_add_contact.clicked.connect(self.add_contact_window)
        self.ui.menu_add_contact.triggered.connect(self.add_contact_window)
        self.ui.btn_remove_contact.clicked.connect(self.delete_contact_window)
        self.ui.menu_del_contact.triggered.connect(self.delete_contact_window)

        self.contacts_model = None
        self.history_model = None
        self.messages = QMessageBox()
        self.current_chat = None
        self.current_chat_key = None
        self.ui.list_messages.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.ui.list_messages.setWordWrap(True)

        self.ui.list_contacts.doubleClicked.connect(self.select_active_user)

        self.clients_list_update()
        self.set_disabled_input()
        self.show()

    def set_disabled_input(self):
        '''Method of setting the muted input field'''

        self.ui.label_new_message.setText('To select a recipient, double-click on it in the contact window.')
        self.ui.text_message.clear()
        if self.history_model:
            self.history_model.clear()

        self.ui.btn_clear.setDisabled(True)
        self.ui.btn_send.setDisabled(True)
        self.ui.text_message.setDisabled(True)

        self.encryptor = None
        self.current_chat = None
        self.current_chat_key = None

    def history_list_update(self):
        '''Method that show the client history'''

        history_list = sorted(
            self.database.get_client_activity_history(
                self.current_chat),
            key=lambda item: item[3])
        if not self.history_model:
            self.history_model = QStandardItemModel()
            self.ui.list_messages.setModel(self.history_model)
        self.history_model.clear()
        length = len(history_list)
        start_index = 0
        if length > 20:
            start_index = length - 20

        for i in range(start_index, length):
            item = history_list[i]
            if item[1] == 'in':
                message = QStandardItem(f'Incoming mail from {item[3].replace(microsecond=0)}:\n {item[2]}')
                message.setEditable(False)
                message.setBackground(QBrush(QColor(255, 213, 213)))
                message.setTextAlignment(Qt.AlignLeft)
                self.history_model.appendRow(message)
            else:
                message = QStandardItem(f'Outgoing mail from {item[3].replace(microsecond=0)}:\n {item[2]}')
                message.setEditable(False)
                message.setTextAlignment(Qt.AlignRight)
                message.setBackground(QBrush(QColor(204, 255, 204)))
                self.history_model.appendRow(message)
        self.ui.list_messages.scrollToBottom()

    def select_active_user(self):
        '''Active user selection method for messaging'''

        self.current_chat = self.ui.list_contacts.currentIndex().data()
        self.set_active_user()

    def set_active_user(self):
        try:
            self.current_chat_key = self.transport.key_request(
                self.current_chat)
            LOG.debug(f'Open key for {self.current_chat} was uploaded')
            if self.current_chat_key:
                self.encryptor = PKCS1_OAEP.new(
                    RSA.import_key(self.current_chat_key))
        except (OSError, json.JSONDecodeError):
            self.current_chat_key = None
            self.encryptor = None
            LOG.debug(f'Impossible to obtaine key for {self.current_chat}')
        if not self.current_chat_key:
            self.messages.warning(
                self, 'Error', 'There is no encryption key for user')
            return

        self.ui.label_new_message.setText(
            f'Enter message for {self.current_chat}')
        self.ui.btn_clear.setDisabled(False)
        self.ui.btn_send.setDisabled(False)
        self.ui.text_message.setDisabled(False)
        self.history_list_update()

    def clients_list_update(self):
        '''Method of updating users contacts list'''

        clients_contacts_list = self.database.get_all_client_contacts()
        self.contacts_model = QStandardItemModel()
        for i in sorted(clients_contacts_list):
            item = QStandardItem(i)
            item.setEditable(False)
            self.contacts_model.appendRow(item)
        self.ui.list_contacts.setModel(self.contacts_model)

    def add_contact_window(self):
        '''Method for displaying window with adding contact dialog'''

        global select_dialog
        select_dialog = AddContactDialog(self.transport, self.database)
        select_dialog.ok_button.clicked.connect(
            lambda: self.add_contact_action(select_dialog))
        select_dialog.show()

    def add_contact_action(self, item):
        '''Method of adding contact action'''

        new_contact = item.selector.currentText()
        self.add_contact(new_contact)
        item.close()

    def add_contact(self, new_contact):
        '''Method of adding contact'''

        try:
            self.transport.add_contact(new_contact)
        except ServerError as err:
            self.messages.critical(self, 'Server error', err.text)
        except OSError as err:
            if err.errno:
                self.messages.critical(self, 'Error', 'Lost connection to server!')
                self. close()
            self.messages.critical(self, 'Error', 'Connection timeout!')
        else:
            self.database.add_contact(new_contact)
            new_contact = QStandardItem(new_contact)
            new_contact.setEditable(False)
            self.contacts_model.appendRow(new_contact)
            LOG.info(f'Successfully added contact {new_contact}')
            self.messages.information(self, 'Success', 'Contact successfully aded.')

    def delete_contact_window(self):
        '''Method for displaying window with deleting contact dialog'''

        global remove_dialog
        remove_dialog = DelContactDialog(self.database)
        remove_dialog.ok_button.clicked.connect(
            lambda: self.delete_contact(remove_dialog))
        remove_dialog.show()

    def delete_contact(self, item):
        '''Method of deleting contact'''

        selected_contact = item.selector.currentText()
        try:
            self.transport.remove_contact(selected_contact)
        except ServerError as err:
            self.messages.critical(self, 'Server error', err.text)
        except OSError as err:
            if err.errno:
                self.messages.critical(self, 'Error', 'Lost connection to server!')
                self.close()
            self.messages.critical(self, 'Error', 'Connection timeout!')
        else:
            self.database.del_contact(selected_contact)
            self.clients_list_update()
            LOG.info(f'Successfully deleted contact {selected_contact}')
            self.messages.information(self, 'Success', 'Contact successfully deleted.')
            item.close()
            if selected_contact == self.current_chat:
                self.current_chat = None
                self.set_disabled_input()

    def send_message(self):
        '''Method for sending message to current active contact'''

        message_text = self.ui.text_message.toPlainText()
        self.ui.text_message.clear()
        if not message_text:
            return
        message_text_encrypted = self.encryptor.encrypt(
            message_text.encode('utf-8'))
        message_text_encrypted_base64 = base64.b64encode(
            message_text_encrypted)
        try:
            self.transport.create_message(
                self.current_chat,
                message_text_encrypted_base64.decode('ascii'))
            pass
        except ServerError as err:
            self.messages.critical(self, 'Error', err.text)
        except OSError as err:
            if err.errno:
                self.messages.critical(self, 'Error', 'Lost connection to server!')
                self.close()
            self.messages.critical(self, 'Error', 'Connection timeout!')
        except (ConnectionResetError, ConnectionAbortedError):
            self.messages.critical(self, 'Error', 'Lost connection to server!')
            self.close()
        else:
            self.database.save_message(self.current_chat, 'out', message_text)
            LOG.debug(f'Sent a message to {self.current_chat}: {message_text}')
            self.history_list_update()

    @pyqtSlot(dict)
    def message(self, message):
        encrypted_message = base64.b64decode(message[MESSAGE_TEXT])
        try:
            decrypted_message = self.decrypter.decrypt(encrypted_message)
        except (ValueError, TypeError):
            self.messages.warning(
                self,
                'ERROR',
                'Impossible to decode the message')
            return
        self.database.save_message(
            self.current_chat,
            'in',
            decrypted_message.decode('utf-8'))
        sender = message[SENDER]
        if sender == self.current_chat:
            self.history_list_update()
        else:
            if self.database.check_user_presence_in_client_contacts(sender):
                if self.messages.question(
                        self,
                        'New message',
                        f'Get new message from {sender}, open chat with him?',
                        QMessageBox.Yes,
                        QMessageBox.No) == QMessageBox.Yes:
                    self.current_chat = sender
                    self.set_active_user()
            else:
                print('NO')
                if self.messages.question(
                        self, 'New message',
                        f'Get new message from {sender}.\n'
                        f'This user is not in your contact list.\n'
                        f'Add contact and open chat with him?',
                        QMessageBox.Yes,
                        QMessageBox.No) == QMessageBox.Yes:
                    self.add_contact(sender)
                    self.current_chat = sender
                    self.database.save_message(
                        self.current_chat,
                        'in',
                        decrypted_message.decode('utf-8'))
                    self.set_active_user()

    @pyqtSlot()
    def connection_lost(self):
        self.messages.warning(
            self,
            'Connection failure',
            'User was deleted from the server')
        self.close()

    @pyqtSlot()
    def signal_205(self):
        if self.current_chat and not self.database.check_user_presence_in_known_users(self.current_chat):
            self.messages.warning(
                self,
                'Connection lost',
                'Contact was delete from the server')
            self.set_disabled_input()
            self.current_chat = None
        self.clients_list_update()

    def make_connection(self, transport_object):
        transport_object.new_message_signal.connect(self.message)
        transport_object.connection_lost_signal.connect(self.connection_lost)
        transport_object.message_205.connect(self.signal_205)

