import binascii
import hashlib
import hmac
import json
import logging
import sys
import threading
from socket import socket, AF_INET, SOCK_STREAM
from time import time, sleep

from PyQt5.QtCore import pyqtSignal, QObject

sys.path.append('../')
from common.utils import send_message, get_message
from common.variables import *
from common.decos import Log
from common.errors import ServerError

client_log = logging.getLogger('client')
sock_lock = threading.Lock()


class MessengerClient(threading.Thread, QObject):
    """
    Класс-поток для сообщения с сервером.
    """
    new_message = pyqtSignal(dict)
    connection_lost = pyqtSignal()

    def __init__(self, user_name, password, connection_ip, connection_port, database, keys):
        threading.Thread.__init__(self)
        QObject.__init__(self)

        self.user_name = user_name
        self.password = password
        self.keys = keys
        self.db = database
        self.socket = None
        self.create_connection(connection_ip, connection_port)

        # Обновляем таблицы известных пользователей и контактов
        try:
            self.get_user_list()
            self.get_contact_list()
        except OSError as err:
            if err.errno:
                client_log.critical(f'Потеряно соединение с сервером.')
                raise ServerError('Потеряно соединение с сервером.')
            client_log.error('Timeout соединения при обновлении списков пользователей.')
        except json.JSONDecodeError:
            client_log.critical(f'Потеряно соединение с сервером.')
            raise ServerError('Потеряно соединение с сервером.')
        self.running = True

    @Log()
    def create_connection(self, ip, port):
        """
        Функция пытается установить соединение с сервером
        из полученных ip-адреса и порта и отправляет на сервер запрос
        на авторизацию.
        """
        try:
            self.socket = socket(AF_INET, SOCK_STREAM)
            self.socket.settimeout(5)
            self.socket.connect((ip, port))

        except (ConnectionRefusedError, ConnectionError):
            client_log.critical(f'Не удалось установить соединение с сервером {ip}:{port}')
            raise ServerError('Не удалось установить соединение с сервером')

        else:
            client_log.info(f'Соединение с сервером {ip}:{port}')
            client_log.info('Запуск процедуры авторизации.')

            password_hash = hashlib.pbkdf2_hmac('sha512',
                                                self.password.encode(ENCODING),
                                                self.user_name.encode(ENCODING),
                                                10000)
            passwd_hash_string = binascii.hexlify(password_hash)
            pubkey = self.keys.publickey().export_key().decode('ascii')

            message = self.create_presence_message(pubkey)

            try:
                with sock_lock:
                    send_message(self.socket, message)
                    answer = get_message(self.socket)
                    if RESPONSE in answer:
                        if answer[RESPONSE] == 400:
                            client_log.error(f'Ошибка авторизации. {answer[ERROR]}')
                            raise ServerError(answer[ERROR])
                        elif answer[RESPONSE] == 511:
                            data = answer[DATA]
                            digest = hmac.new(passwd_hash_string, data.encode(ENCODING), 'MD5').digest()
                            my_answer = RESPONSE_511
                            my_answer[DATA] = binascii.b2a_base64(digest).decode('ascii')
                            send_message(self.socket, my_answer)
                            self.read_response(get_message(self.socket))
                            client_log.info('Авторизация прошла успешно.')
            except (OSError, json.JSONDecodeError):
                client_log.critical('Сбой соединения в процессе авторизации.')
                raise ServerError('Сбой соединения в процессе авторизации.')

    @Log()
    def create_presence_message(self, pubkey):
        """
        Функция формирует presence-сообщение для сервера.
        :param pubkey: публичный ключ пользователя.
        """
        message = {
            ACTION: PRESENCE,
            TIME: time(),
            USER: {
                ACCOUNT_NAME: self.user_name,
                PUBLIC_KEY: pubkey
            }
        }
        client_log.debug(f'Создано приветственное сообщение серверу от {self.user_name}')
        return message

    @Log()
    def get_contact_list(self):
        """
        Функция отправляет запрос серверу на получение списка контактов пользователя.
        """
        message = {
            ACTION: GET_CONTACTS,
            TIME: time(),
            FROM: self.user_name
        }
        client_log.debug(f'Запрос списка контактов от {self.user_name}')
        with sock_lock:
            send_message(self.socket, message)
            answer = get_message(self.socket)
        client_log.debug(f'Получен ответ на запрос списка контактов {answer}')
        if RESPONSE in answer and answer[RESPONSE] == 202:
            for contact in answer[ALERT]:
                self.db.add_contact(contact)
        else:
            client_log.error('Не удалось обновить список контактов.')

    @Log()
    def get_user_list(self):
        """
        Функция отправляет запрос серверу на получение списка известных пользователей.
        """
        client_log.debug(f'Запрос списка известных пользователей от {self.user_name}.')
        message = {
            ACTION: GET_USERS,
            TIME: time(),
            FROM: self.user_name
        }
        with sock_lock:
            send_message(self.socket, message)
            answer = get_message(self.socket)
        if RESPONSE in answer and answer[RESPONSE] == 202:
            self.db.add_all_users(answer[ALERT])
        else:
            client_log.error('Не удалось обновить список известных пользователей.')

    def key_request(self, user):
        """
        Запрашивает публичный ключ пользователя.
        """
        client_log.debug(f'Запрос публичного ключа для {user}')
        req = {
            ACTION: PUBLIC_KEY_REQUEST,
            TIME: time(),
            ACCOUNT_NAME: user
        }
        with sock_lock:
            send_message(self.socket, req)
            ans = get_message(self.socket)
        if RESPONSE in ans and ans[RESPONSE] == 511:
            return ans[DATA]
        else:
            client_log.error(f'Не удалось получить ключ пользователя {user}.')

    @Log()
    def add_contact(self, nickname):
        """
        Функция добавляет контакт в список контактов.
        """
        message = {
            ACTION: ADD_CONTACT,
            FROM: self.user_name,
            TIME: time(),
            LOGIN: nickname
        }
        client_log.debug(f'Отправлен запрос на добавление контакта {nickname} в список контактов.')

        with sock_lock:
            send_message(self.socket, message)
            self.read_response(get_message(self.socket))

    @Log()
    def del_contact(self, nickname):
        """
        Функция удаляет контакт из списка контактов.
        """
        message = {
            ACTION: DEL_CONTACT,
            FROM: self.user_name,
            TIME: time(),
            LOGIN: nickname
        }
        client_log.debug(f'Отправлен запрос на удаление контакта {nickname} из списка контактов.')

        with sock_lock:
            send_message(self.socket, message)
            self.read_response(get_message(self.socket))

    @Log()
    def create_user_message(self, recipient, message_text):
        """
        Функция формирует сообщение пользователя и отправляет его.
        """
        message = {
            ACTION: MSG,
            TIME: time(),
            FROM: self.user_name,
            TO: recipient,
            TEXT: message_text
        }
        client_log.debug(f'Создано сообщение от {self.user_name} для {recipient}')

        with sock_lock:
            send_message(self.socket, message)
            self.read_response(get_message(self.socket))
            client_log.info(f'Отрправлено сообщение {message}')

    @Log()
    def connection_shutdown(self):
        """
        Функция закрывает соединение с сервером.
        """
        self.running = False
        message = {
            ACTION: EXIT,
            TIME: time(),
            FROM: self.user_name
        }
        with sock_lock:
            try:
                send_message(self.socket, message)
            except OSError:
                pass
        client_log.debug('Завершение работы.')
        sleep(0.5)

    @Log()
    def read_response(self, message):
        """
        Функция принимает сообщение сервера, разбирает его
        и выводит соответствующий результат.
        """
        client_log.debug(f'Разбор ответа сервера: {message}')
        # Если пришол ответ сервера на запрос:
        if RESPONSE in message:
            if message[RESPONSE] == 200:
                client_log.info('Получен код подтверждения сервера 200')
                return
            elif message[RESPONSE] == 400:
                raise ServerError(f'{message[ERROR]}')
            else:
                client_log.debug(f'Принят неизвестный код подтверждения {message[RESPONSE]}')

        # Если пришло текстовое сообщение от пользователя:
        elif (ACTION in message and message[ACTION] == MSG
                and TIME in message and FROM in message
                and TEXT in message
                and TO in message and message[TO] == self.user_name):
            client_log.info(f'Получено сообщение {message}')
            self.new_message.emit(message)

    def run(self):
        """
        Основная функция-процесс для приёмки сообщений.
        """
        client_log.info(f'Запуск процесса для приёмки сообщений.')
        while self.running:
            sleep(1)
            with sock_lock:
                try:
                    self.socket.settimeout(0.5)
                    message = get_message(self.socket)
                except OSError as err:
                    if err.errno:
                        client_log.critical(f'Потеряно соединение с сервером.')
                        self.running = False
                        self.connection_lost.emit()
                except (ConnectionError, ConnectionAbortedError,
                        ConnectionResetError, json.JSONDecodeError, TypeError):
                    client_log.debug(f'Потеряно соединение с сервером.')
                    self.running = False
                    self.connection_lost.emit()
                else:
                    client_log.debug(f'Принято сообщение с сервера: {message}')
                    self.read_response(message)
                finally:
                    self.socket.settimeout(5)
