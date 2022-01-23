from PyQt5.QtWidgets import QMainWindow, qApp, QMessageBox, QApplication, QListView
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QBrush, QColor
from PyQt5.QtCore import pyqtSlot, QEvent, Qt
from Cryptodome.Cipher import PKCS1_OAEP
from Cryptodome.PublicKey import RSA
import json
import logging
import base64
import sys

sys.path.append('../')
from client.main_window_conv import Ui_MainClientWindow
from client.add_contact import AddContactDialog
from client.del_contact import DelContactDialog
from common.errors import ServerError
from common.variables import *

logger = logging.getLogger('client')


class ClientMainWindow(QMainWindow):
    '''
    The class is the main user window.
    Contains all the basic logic of the client module.
    The window configuration is created in QT Designer and loaded from
    converted file main_window_conv.py
    '''

    def __init__(self, database, transport, keys):
        super().__init__()
        # main variables
        self.database = database
        self.transport = transport

        # message decryptor object with preloaded key
        self.decrypter = PKCS1_OAEP.new(keys)

        # Loading the window configuration from the designer
        self.ui = Ui_MainClientWindow()
        self.ui.setupUi(self)

        # The "Exit" button
        self.ui.menu_exit.triggered.connect(qApp.exit)

        # Send message button
        self.ui.btn_send.clicked.connect(self.send_message)

        # "add a contact"
        self.ui.btn_add_contact.clicked.connect(self.add_contact_window)
        self.ui.menu_add_contact.triggered.connect(self.add_contact_window)

        # Delete a contact
        self.ui.btn_remove_contact.clicked.connect(self.delete_contact_window)
        self.ui.menu_del_contact.triggered.connect(self.delete_contact_window)

        # Additional required attributes
        self.contacts_model = None
        self.history_model = None
        self.messages = QMessageBox()
        self.current_chat = None
        self.current_chat_key = None
        self.encryptor = None
        self.ui.list_messages.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff)
        self.ui.list_messages.setWordWrap(True)

        # A double click on the contact list is sent to the handler
        self.ui.list_contacts.doubleClicked.connect(self.select_active_user)

        self.clients_list_update()
        self.set_disabled_input()
        self.show()

    def set_disabled_input(self):
        ''' A method that makes input fields inactive '''
        # Надпись  - получатель.
        self.ui.label_new_message.setText(
            'Для выбора получателя дважды кликните на нем в окне контактов.')
        self.ui.text_message.clear()
        if self.history_model:
            self.history_model.clear()

        # The input field and the send button are inactive until the recipient is selected.
        self.ui.btn_clear.setDisabled(True)
        self.ui.btn_send.setDisabled(True)
        self.ui.text_message.setDisabled(True)

        self.encryptor = None
        self.current_chat = None
        self.current_chat_key = None

    def history_list_update(self):
        '''
        A method that fills in the corresponding QListView
        the history of correspondence with the current interlocutor.
        '''
        # We get the history sorted by date
        list = sorted(
            self.database.get_history(
                self.current_chat),
            key=lambda item: item[3])
        # If the model is not created, we will create it.
        if not self.history_model:
            self.history_model = QStandardItemModel()
            self.ui.list_messages.setModel(self.history_model)
        # Let's clear the old records
        self.history_model.clear()
        # We take no more than the last 20 entries.
        length = len(list)
        start_index = 0
        if length > 20:
            start_index = length - 20
        # Filling the model with records, it is also worth dividing the incoming
        # and outgoing alignment and different background.
        # displays only the last 20 messages
        for i in range(start_index, length):
            item = list[i]
            if item[1] == 'in':
                mess = QStandardItem(
                    f'Входящее от {item[3].replace(microsecond=0)}:\n {item[2]}')
                mess.setEditable(False)
                mess.setBackground(QBrush(QColor(255, 213, 213)))
                mess.setTextAlignment(Qt.AlignLeft)
                self.history_model.appendRow(mess)
            else:
                mess = QStandardItem(
                    f'Исходящее от {item[3].replace(microsecond=0)}:\n {item[2]}')
                mess.setEditable(False)
                mess.setTextAlignment(Qt.AlignRight)
                mess.setBackground(QBrush(QColor(204, 255, 204)))
                self.history_model.appendRow(mess)
        self.ui.list_messages.scrollToBottom()

    def select_active_user(self):
        ''' The method is a handler for the double-click event on the contact list. '''
        # Выбранный пользователем (даблклик) находится в выделеном элементе в
        # QListView
        self.current_chat = self.ui.list_contacts.currentIndex().data()
        # вызываем основную функцию
        self.set_active_user()

    def set_active_user(self):
        '''The method of activating the chat with the interlocutor.'''
        # We request the user's public key and create an encryption object
        try:
            self.current_chat_key = self.transport.key_request(
                self.current_chat)
            logger.debug(f'Загружен открытый ключ для {self.current_chat}')
            if self.current_chat_key:
                self.encryptor = PKCS1_OAEP.new(
                    RSA.import_key(self.current_chat_key))
        except (OSError, json.JSONDecodeError):
            self.current_chat_key = None
            self.encryptor = None
            logger.debug(f'Не удалось получить ключ для {self.current_chat}')

        # If there is no key, then the error is that it was not possible to start a chat with the user
        if not self.current_chat_key:
            self.messages.warning(
                self, 'Ошибка', 'Для выбранного пользователя нет ключа шифрования.')
            return

        # We put an inscription and activate the buttons
        self.ui.label_new_message.setText(
            f'Введите сообщенние для {self.current_chat}:')
        self.ui.btn_clear.setDisabled(False)
        self.ui.btn_send.setDisabled(False)
        self.ui.text_message.setDisabled(False)

        # Fill in the message history window for the required user.
        self.history_list_update()

    def clients_list_update(self):
        '''A method that updates the contact list.'''
        contacts_list = self.database.get_contacts()
        self.contacts_model = QStandardItemModel()
        for i in sorted(contacts_list):
            item = QStandardItem(i)
            item.setEditable(False)
            self.contacts_model.appendRow(item)
        self.ui.list_contacts.setModel(self.contacts_model)

    def add_contact_window(self):
        '''The method that creates the window is the dialog for adding a contact'''
        global select_dialog
        select_dialog = AddContactDialog(self.transport, self.database)
        select_dialog.btn_ok.clicked.connect(
            lambda: self.add_contact_action(select_dialog))
        select_dialog.show()

    def add_contact_action(self, item):
        '''The handler method for clicking the "Add" button'''
        new_contact = item.selector.currentText()
        self.add_contact(new_contact)
        item.close()

    def add_contact(self, new_contact):
        '''
        A method that adds a contact to the server and client BD.
        After updating the databases, it also updates the contents of the window.
        '''
        try:
            self.transport.add_contact(new_contact)
        except ServerError as err:
            self.messages.critical(self, 'Ошибка сервера', err.text)
        except OSError as err:
            if err.errno:
                self.messages.critical(
                    self, 'Ошибка', 'Потеряно соединение с сервером!')
                self.close()
            self.messages.critical(self, 'Ошибка', 'Таймаут соединения!')
        else:
            self.database.add_contact(new_contact)
            new_contact = QStandardItem(new_contact)
            new_contact.setEditable(False)
            self.contacts_model.appendRow(new_contact)
            logger.info(f'Успешно добавлен контакт {new_contact}')
            self.messages.information(
                self, 'Успех', 'Контакт успешно добавлен.')

    def delete_contact_window(self):
        '''A method that creates a window for deleting a contact.'''
        global remove_dialog
        remove_dialog = DelContactDialog(self.database)
        remove_dialog.btn_ok.clicked.connect(
            lambda: self.delete_contact(remove_dialog))
        remove_dialog.show()

    def delete_contact(self, item):
        '''
        A method that removes a contact from the server and client BD.
        After updating the databases, it also updates the contents of the window.
        '''
        selected = item.selector.currentText()
        try:
            self.transport.remove_contact(selected)
        except ServerError as err:
            self.messages.critical(self, 'Ошибка сервера', err.text)
        except OSError as err:
            if err.errno:
                self.messages.critical(
                    self, 'Ошибка', 'Потеряно соединение с сервером!')
                self.close()
            self.messages.critical(self, 'Ошибка', 'Таймаут соединения!')
        else:
            self.database.del_contact(selected)
            self.clients_list_update()
            logger.info(f'Успешно удалён контакт {selected}')
            self.messages.information(self, 'Успех', 'Контакт успешно удалён.')
            item.close()
            # If the active user is deleted, then deactivate the input fields.
            if selected == self.current_chat:
                self.current_chat = None
                self.set_disabled_input()

    def send_message(self):
        '''
        The function of sending a message to the current interlocutor.
        Implements message encryption and sending.
        '''
        # Text in the field, check that the field is not empty, then the message is taken
        # and the field is cleared
        message_text = self.ui.text_message.toPlainText()
        self.ui.text_message.clear()
        if not message_text:
            return
        # We encrypt the message with the recipient's key and package it in base64.
        message_text_encrypted = self.encryptor.encrypt(
            message_text.encode('utf8'))
        message_text_encrypted_base64 = base64.b64encode(
            message_text_encrypted)
        try:
            self.transport.send_message(
                self.current_chat,
                message_text_encrypted_base64.decode('ascii'))
            pass
        except ServerError as err:
            self.messages.critical(self, 'Ошибка', err.text)
        except OSError as err:
            if err.errno:
                self.messages.critical(
                    self, 'Ошибка', 'Потеряно соединение с сервером!')
                self.close()
            self.messages.critical(self, 'Ошибка', 'Таймаут соединения!')
        except (ConnectionResetError, ConnectionAbortedError):
            self.messages.critical(
                self, 'Ошибка', 'Потеряно соединение с сервером!')
            self.close()
        else:
            self.database.save_message(self.current_chat, 'out', message_text)
            logger.debug(
                f'Отправлено сообщение для {self.current_chat}: {message_text}')
            self.history_list_update()

    @pyqtSlot(dict)
    def message(self, message):
        '''
        Slot handler of incoming messages, performs decryption
        incoming messages and their saving in the message history.
        Requests the user if the message is not from the current one
        the interlocutor. If necessary, changes the interlocutor.
        '''
        # We get a string of bytes
        encrypted_message = base64.b64decode(message[MESSAGE_TEXT])
        # We decode the string, issue a message if an error occurs, and terminate the function
        try:
            decrypted_message = self.decrypter.decrypt(encrypted_message)
        except (ValueError, TypeError):
            self.messages.warning(
                self, 'Ошибка', 'Не удалось декодировать сообщение.')
            return
        # Save the message to the database and update the message history or
        # open a new chat.
        self.database.save_message(
            self.current_chat,
            'in',
            decrypted_message.decode('utf8'))

        sender = message[SENDER]
        if sender == self.current_chat:
            self.history_list_update()
        else:
            # Let's check if we have such a user in our contacts:
            if self.database.check_contact(sender):
                # If there is, we ask and want to open a chat with him and open
                # if desired
                if self.messages.question(
                    self,
                    'Новое сообщение',
                    f'Получено новое сообщение от {sender}, открыть чат с ним?',
                    QMessageBox.Yes,
                        QMessageBox.No) == QMessageBox.Yes:
                    self.current_chat = sender
                    self.set_active_user()
            else:
                print('NO')
                # If not, we ask if we want to add a user to contacts.
                if self.messages.question(
                    self,
                    'Новое сообщение',
                    f'Получено новое сообщение от {sender}.\n Данного пользователя нет в вашем контакт-листе.\n Добавить в контакты и открыть чат с ним?',
                    QMessageBox.Yes,
                        QMessageBox.No) == QMessageBox.Yes:
                    self.add_contact(sender)
                    self.current_chat = sender
                    # You need to save the message again, otherwise it will be lost,
                    # because there was no contact at the time of the previous call.
                    self.database.save_message(
                        self.current_chat, 'in', decrypted_message.decode('utf8'))
                    self.set_active_user()

    @pyqtSlot()
    def connection_lost(self):
        '''
        Slot handler for loss of connection to the server.
        Issues a warning window and shuts down the application.
        '''
        self.messages.warning(
            self,
            'Сбой соединения',
            'Потеряно соединение с сервером. ')
        self.close()

    @pyqtSlot()
    def sig_205(self):
        '''
        A slot that performs database updates at the command of the server.
        '''
        if self.current_chat and not self.database.check_user(
                self.current_chat):
            self.messages.warning(
                self,
                'Сочувствую',
                'К сожалению собеседник был удалён с сервера.')
            self.set_disabled_input()
            self.current_chat = None
        self.clients_list_update()

    def make_connection(self, trans_obj):
        '''A method for connecting signals and slots.'''
        trans_obj.new_message.connect(self.message)
        trans_obj.connection_lost.connect(self.connection_lost)
        trans_obj.message_205.connect(self.sig_205)
