'''
This is module processing transportation (handeling)
messages between clients by server.
'''

import sys
import hashlib
import hmac
import binascii

from logging import getLogger
from json import JSONDecodeError
from threading import Thread, Lock
from PyQt5.QtCore import pyqtSignal, QObject
from socket import socket, SOCK_STREAM, AF_INET
from time import time, sleep

sys.path.append('../')
from errors import ServerError
from common.utils import send_message, get_message
from common.variables import *

LOG = getLogger('client_logger')
socket_lock = Lock()


class ClientTransport(Thread, QObject):
    new_message_signal = pyqtSignal(dict)
    message_205 = pyqtSignal()
    connection_lost_signal = pyqtSignal()

    def __init__(self, port, ip_address, database, username, password, keys):
        Thread.__init__(self)
        QObject.__init__(self)

        self.database = database
        self.username = username
        self.password = password
        self.transport = None
        self.keys = keys
        self.connection_init(port, ip_address)

        try:
            self.all_users_list_update()
            self.contacts_list_update()
        except OSError as err:
            if err.errno:
                LOG.critical('Connection with server is lost')
                raise ServerError('Connection with server is lost')
        except JSONDecodeError:
            LOG.critical('Connection with server is lost')
            raise ServerError('Connection with server is lost')
        self.running_transport = True

    def connection_init(self, port, ip):
        self.transport = socket(AF_INET, SOCK_STREAM)
        self.transport.settimeout(5)
        connected_flag = False

        for i in range(5):
            LOG.info(f'Connection attempt №{i+1}')
            try:
                self.transport.connect((ip, port))
            except (OSError, ConnectionRefusedError):
                pass
            else:
                connected_flag = True
                LOG.debug('Connection established')
                break
            sleep(1)

        if not connected_flag:
            LOG.critical('Failed to establish a connection to the server')
            raise ServerError('Failed to establish a connection to the server')

        LOG.debug('Starting authentication dialog')

        password_bytes = self.password.encode('utf-8')
        salt = self.username.lower().encode('utf-8')
        password_hash = hashlib.pbkdf2_hmac('sha512', password_bytes, salt, 10000)
        password_hash_str = binascii.hexlify(password_hash)

        LOG.debug(f'Password hash ready: {password_hash_str}')

        public_key = self.keys.publickey().export_key().decode('ascii')

        with socket_lock:
            presence = {
                ACTION: PRESENCE,
                TIME: time(),
                USER: self.username,
                PUBLIC_KEY: public_key
            }
            LOG.debug(f'Presence message = {presence}')

            try:
                send_message(self.transport, presence)
                server_answer = get_message(self.transport)
                LOG.debug(f'Server response = {server_answer}')
                if RESPONSE in server_answer:
                    if server_answer[RESPONSE] == 400:
                        raise ServerError(server_answer[ERROR])
                    elif server_answer[RESPONSE] == 511:
                        answer_data = server_answer[DATA]
                        hash_data = hmac.new(password_hash_str, answer_data.encode('utf-8'), 'MD5')
                        digest = hash_data.digest()
                        client_answer = RESPONSE_511
                        client_answer[DATA] = binascii.b2a_base64(digest).decode('ascii')
                        send_message(self.transport, client_answer)
                        self.receive_message(get_message(self.transport))
            except (OSError, JSONDecodeError) as err:
                LOG.debug(f'Connection error', exc_info=err)
                raise ServerError('Connection failure in connection process')

    def receive_message(self, message):
        LOG.debug(f'Handle server {message}')
        if RESPONSE in message:
            if message[RESPONSE] == 200:
                LOG.info('Response 200: OK')
                return
            elif message[RESPONSE] == 400:
                LOG.error(f'Obtained response from server "Response 400: {message[ERROR]}".')
                raise ServerError(f' Response 400: {message[ERROR]}')
            elif message[RESPONSE] == 205:
                self.all_users_list_update()
                self.contacts_list_update()
                self.message_205.emit()
            else:
                LOG.error(f'Obtained unknown response code {message[RESPONSE]}')
        elif ACTION in message and message[ACTION] == MESSAGE \
                and SENDER in message and RECIPIENT in message \
                and MESSAGE_TEXT in message and message[RECIPIENT] == self.username:
            LOG.debug(f'Obtained message from {message[SENDER]}:{message[MESSAGE_TEXT]}')
            self.new_message_signal.emit(message)

    def all_users_list_update(self):
        LOG.debug('All users list request')
        request_all_users = {
            ACTION: USERS_REQUEST,
            TIME: time(),
            USER: self.username
        }
        with socket_lock:
            send_message(self.transport, request_all_users)
            response = get_message(self.transport)
        if RESPONSE in response and response[RESPONSE] == 202:
            self.database.add_known_users(response[LIST_INFO])
        else:
            LOG.error('Failed to update the list of known users')

    def contacts_list_update(self):
        self.database.contacts_clear()
        LOG.debug(f'Contacts list request for user {self.username}')
        request_all_contacts = {
            ACTION: GET_CONTACTS,
            TIME: time(),
            USER: self.username
        }
        LOG.debug(f'Request generated {request_all_contacts}')
        with socket_lock:
            send_message(self.transport, request_all_contacts)
            response = get_message(self.transport)
        if RESPONSE in response and response[RESPONSE] == 202:
            for contact in response[LIST_INFO]:
                self.database.add_contact(contact)
        else:
            LOG.error('Failed to update the list of known users')

    def key_request(self, username):
        LOG.debug('Public key request')
        request = {
            ACTION: PUBLIC_KEY_REQUEST,
            TIME: time(),
            USER: username
        }
        with socket_lock:
            send_message(self.transport, request)
            server_answer = get_message(self.transport)
            if RESPONSE in server_answer and server_answer[RESPONSE] == 511:
                return server_answer[DATA]
            else:
                LOG.error(f'Contact {username} public key is not obtained')

    def add_contact(self, contact):
        LOG.debug(f'Create contact {contact} in the clients contacts list')
        request_to_add_contact = {
            ACTION: ADD_CONTACT,
            TIME: time(),
            USER: self.username,
            CONTACT: contact
        }
        with socket_lock:
            send_message(self.transport, request_to_add_contact)
            self.receive_message(get_message(self.transport))

    def remove_contact(self, contact):
        LOG.debug(f'Remove contact {contact} from the client contacts list')
        request_to_remove_contact = {
            ACTION: REMOVE_CONTACT,
            TIME: time(),
            USER: self.username,
            CONTACT: contact
        }
        with socket_lock:
            send_message(self.transport, request_to_remove_contact)
            self.receive_message(get_message(self.transport))

    def transport_shutdown(self):
        self.running_transport = False
        dict_message = {
            ACTION: EXIT,
            TIME: time(),
            USER: self.username
        }
        with socket_lock:
            try:
                send_message(self.transport, dict_message)
            except OSError:
                pass
        LOG.debug('Transport is shutting down')
        sleep(0.5)

    def create_message(self, addressee, message):
        dict_message = {
            ACTION: MESSAGE,
            TIME: time(),
            SENDER: self.username,
            RECIPIENT: addressee,
            MESSAGE_TEXT: message
        }
        LOG.debug(f'Created dict-message: {dict_message}')
        with socket_lock:
            send_message(self.transport, dict_message)
            self.receive_message(get_message(self.transport))
            LOG.info(f'Message sent to user {addressee}')

    def run(self):
        while self.running_transport:
            sleep(1)
            message = None
            with socket_lock:
                try:
                    self.transport.settimeout(0.5)
                    message = get_message(self.transport)
                except OSError as err:
                    if err.errno:
                        LOG.critical(f'Connection with server is lost')
                        self.running_transport = False
                        self.connection_lost_signal.emit()
                except (ConnectionError, ConnectionAbortedError, ConnectionResetError, JSONDecodeError, TypeError):
                    LOG.debug(f'Connection with server is lost')
                    self.running_transport = False
                    self.connection_lost_signal.emit()
                finally:
                    self.transport.settimeout(5)

            if message:
                LOG.debug(f'Obtained massage for server: {message}')
                self.receive_message(message)
