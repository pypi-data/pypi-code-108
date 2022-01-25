import binascii
import hashlib
import hmac
import socket
import sys
import time
import threading
from PyQt5.QtCore import pyqtSignal, QObject

sys.path.append('../')
from common.utils import *
from common.variables import *
from common.errors import ServerError

logger = logging.getLogger('client_file')
socket_lock = threading.Lock()


class ClientTransport(threading.Thread, QObject):
    '''
    Класс реализующий транспортную подсистему клиентского
    модуля. Отвечает за взаимодействие с сервером.
    '''

    new_msg = pyqtSignal(dict)
    connection_lost = pyqtSignal()
    message_205 = pyqtSignal()

    def __init__(self, port, ip_address, database, username, passwd, keys):
        threading.Thread.__init__(self)
        QObject.__init__(self)

        self.database = database
        self.transport = None
        self.username = username
        self.password = passwd
        self.keys = keys
        self.connection_init(port, ip_address)
        try:
            self.user_list_request()
            self.contacts_list_request()
        except OSError as err:
            if err.errno:
                logger.critical(f'Потеряно соединение с сервером:{err}.')
                raise ServerError('Потеряно соединение с сервером!')
            logger.error('Timeout соединения при обновлении списков пользователей.')

        except json.JSONDecodeError as err:
            logger.critical(f'Потеряно соединение с сервером:{err}.')
            raise ServerError('Потеряно соединение с сервером!')
        self.running = True

    def connection_init(self, port, ip):
        '''Метод отвечающий за устанновку соединения с сервером.'''
        self.transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.transport.settimeout(5)
        print(f'{self.transport}')
        connected = False
        for i in range(5):
            logger.info(f'Попытка подключения №{i + 1}')
            try:
                self.transport.connect((ip, port))
            except (OSError, ConnectionRefusedError):
                pass
            else:
                connected = True
                break
            time.sleep(1)
        if not connected:
            logger.critical('Не удалось установить соединение с сервером')
            raise ServerError('Не удалось установить соединение с сервером')
        logger.debug('Установлено соединение с сервером')
        logger.debug('Starting auth dialog.')

        passwd_bytes = self.password.encode('utf-8')
        salt = self.username.lower().encode('utf-8')
        passwd_hash = hashlib.pbkdf2_hmac('sha512', passwd_bytes, salt, 10000)
        passwd_hash_string = binascii.hexlify(passwd_hash)

        logger.debug(f'Passwd hash ready: {passwd_hash_string}')
        pubkey = self.keys.publickey().export_key().decode('ascii')

        try:
            with socket_lock:
                send_meccage(self.transport, self.create_presence(pubkey))
                ans = get_message(self.transport)
                logger.debug(f'Server response = {ans}.')
                if RESPONSE in ans:
                    if ans[RESPONSE] == 400:
                        raise ServerError(ans[ERROR])
                    elif ans[RESPONSE] == 511:
                        ans_data = ans[DATA]
                        hash = hmac.new(passwd_hash_string, ans_data.encode('utf-8'), 'MD5')
                        digest = hash.digest()
                        my_ans = RESPONSE_511
                        my_ans[DATA] = binascii.b2a_base64(
                            digest).decode('ascii')
                        send_meccage(self.transport, my_ans)
                        self.process_answer(get_message(self.transport))

        except (OSError, json.JSONDecodeError):
            logger.critical('Потеряно соединение с сервером!')
            raise ServerError('Потеряно соединение с сервером!')

        logger.info('Сервер ответил на приветственное сообщение.')

    def create_presence(self, pubkey):
        '''Метод, создающий приветственное сообщение для сервера.'''
        out = {
            ACTION: PRESENCE,
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: self.username,
                PUBLIC_KEY: pubkey
            }
        }
        logger.debug(f'Сформировано {PRESENCE} сообщение для пользователя {self.username}')
        return out

    def process_answer(self, message):
        '''Метод обработчик поступающих сообщений с сервера.'''
        logger.debug(f'{message}')
        if RESPONSE in message:
            if message[RESPONSE] == 200:
                return '200: все норм'
            elif message[RESPONSE] == 400:
                raise ServerError(f'{message[ERROR]}')
            elif message[RESPONSE] == 205:
                self.uuser_list_request()
                self.contacts_list_request()
                self.message_205.emit()
            else:
                logger.error(
                    f'Принят неизвестный код подтверждения {message[RESPONSE]}')
            logger.error(f'При обработке сервером обнаружена ошибка:{message[ERROR]}')
            return f'400:{message[ERROR]}'

        elif ACTION in message and message[ACTION] == MESSAGE and SENDER in message and DESTINATION in message \
                and MESSAGE_TEXT in message and message[DESTINATION] == self.username:
            logger.debug(
                f'Получено сообщение от пользователя {message[SENDER]}:{message[MESSAGE_TEXT]}')
            self.new_msg.emit(message)

    def contacts_list_request(self):
        '''Метод обновляющий с сервера список контактов.'''
        self.database.contacts_clear()
        logger.debug(f'Запрос контакт листа для пользователя {self.username}')
        req = {
            ACTION: GET_CONTACTS,
            TIME: time.time(),
            USER: self.username
        }
        logger.debug(f'Сформирован запрос {req}')
        with socket_lock:
            send_meccage(self.transport, req)
            ans = get_message(self.transport)
        logger.debug(f'Получен ответ {ans}')
        if RESPONSE in ans and ans[RESPONSE] == 202:
            for contact in ans[LIST_INFO]:
                self.database.add_contact(contact)
        else:
            logger.error('Не удалось обновить список контактов.')

    def user_list_request(self):
        '''Метод обновляющий с сервера список пользователей.'''
        logger.debug(f'Запрос списка известных пользователей {self.username}')
        req = {
            ACTION: USERS_REQUEST,
            TIME: time.time(),
            ACCOUNT_NAME: self.username
        }
        send_meccage(self.transport, req)
        ans = get_message(self.transport)
        if RESPONSE in ans and ans[RESPONSE] == 202:
            self.database.add_users(ans[LIST_INFO])
        else:
            logger.error('Не удалось обновить список известных пользователей.')

    def add_contact(self, contact):
        '''Метод отправляющий на сервер сведения о добавлении контакта.'''
        logger.debug(f'Создание контакта {contact}')
        req = {
            ACTION: ADD_CONTACT,
            TIME: time.time(),
            USER: self.username,
            ACCOUNT_NAME: contact
        }
        with socket_lock:
            send_meccage(self.transport, req)
            ans = get_message(self.transport)
        if RESPONSE in ans and ans[RESPONSE] == 200:
            pass
        else:
            raise ServerError('Ошибка создания контакта')
        print('Удачное создание контакта.')

    def remove_contact(self, contact):
        '''Метод отправляющий на сервер сведения о удалении контакта.'''
        logger.debug(f'Создание контакта {contact}')
        req = {
            ACTION: REMOVE_CONTACT,
            TIME: time.time(),
            USER: self.username,
            ACCOUNT_NAME: contact
        }
        with socket_lock:
            send_meccage(self.transport, req)
            ans = get_message(self.transport)
        if RESPONSE in ans and ans[RESPONSE] == 200:
            pass
        else:
            raise ServerError('Ошибка удаления клиента')
        print('Удачное удаление')

    def transport_shutdown(self):
        '''Метод уведомляющий сервер о завершении работы клиента.'''
        self.running = False
        message = {
            ACTION: EXIT,
            TIME: time.time(),
            ACCOUNT_NAME: self.username
        }
        with socket_lock:
            try:
                send_meccage(self.transport, message)
            except OSError:
                pass
        logger.debug('Транспорт завершает работу.')
        time.sleep(0.5)

    def create_message(self, to_user, message):
        '''Метод создающий и отправляющий на сервер сообщения для пользователя.'''
        logger.debug(f'Начинаем формировать сообщение для: {to_user}')
        out_massage = {
            ACTION: MESSAGE,
            SENDER: self.username,
            DESTINATION: to_user,
            TIME: time.time(),
            MESSAGE_TEXT: message
        }
        logger.debug(f'Сформированно сообщение серверу: {out_massage}')
        with socket_lock:
            try:
                send_meccage(self.transport, out_massage)
                logger.info(f'Отправлено сообщение для пользователя {to_user}')
            except:
                logger.critical('Потеряно соединение с сервером.')

    def key_request(self, user):
        '''Метод запрашивающий с сервера публичный ключ пользователя.'''
        logger.debug(f'Запрос публичного ключа для {user}')
        req = {
            ACTION: PUBLIC_KEY_REQUEST,
            TIME: time.time(),
            ACCOUNT_NAME: user
        }
        with socket_lock:
            send_meccage(self.transport, req)
            ans = get_message(self.transport)
        if RESPONSE in ans and ans[RESPONSE] == 511:
            return ans[DATA]
        else:
            logger.error(f'Не удалось получить ключ собеседника{user}.')

    def run(self):
        '''Метод содержащий основной цикл работы транспортного потока.'''
        while self.running:
            logger.debug('Запущен процесс - приёмник собщений с сервера.')
            time.sleep(1)
            message = None
            with socket_lock:
                try:
                    self.transport.settimeout(0.5)
                    message = get_message(self.transport)
                except OSError as err:
                    if err.errno:
                        logger.critical(f'Потеряно соединение с сервером:{err}.')
                        self.running = False
                        self.connection_lost.emit()
                except (
                ConnectionError, ConnectionAbortedError, ConnectionResetError, json.JSONDecodeError, TypeError) as err:
                    logger.debug(f'Потеряно соединение с сервером:{err}.')
                    self.running = False
                    self.connection_lost.emit()
                finally:
                    self.transport.settimeout(5)
            if message:
                logger.debug(f'Принято сообщение с сервера: {message}')
                self.process_answer(message)
