import binascii
import hmac
import json
import logging
import os
import select
import sys
import threading
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from time import time

sys.path.append('../')
from common.utils import send_message, get_message
from common.variables import *
from common.decos import Log
from common.descriptors import PortDescriptor

server_log = logging.getLogger('server')


class Server(threading.Thread):
    """
    Основной класс сервера.
    Принимает содинения, словари - пакеты
    от клиентов, обрабатывает поступающие сообщения.
    Работает в качестве отдельного потока.
    """
    listen_port = PortDescriptor()

    def __init__(self, listen_addr, listen_port, database):
        self.listen_addr = listen_addr
        self.listen_port = listen_port
        self.db = database

        self.socket = None

        self.listen_sockets = None
        self.error_sockets = None

        self.running = True

        self.clients = []
        self.names = dict()

        super().__init__()

    @Log()
    def init_socket(self):
        """ Инициализация серверного секета """
        server_log.info('Запуск сервера.')

        # Создаём сокет и начинаем прослушивание
        server_socket = socket(AF_INET, SOCK_STREAM)
        server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        server_socket.bind((self.listen_addr, self.listen_port))
        server_socket.settimeout(TIMEOUT)

        self.socket = server_socket
        self.socket.listen(MAX_USERS)
        server_log.info(f'Сервер запущен. Прослушиваемые адреса: {self.listen_addr}. '
                        f'Порт подключения: {self.listen_port}')

    @Log()
    def run(self):
        """
        Основной цикл обработки сообщений сервером.
        Устанавливает соединение с клиентами,
        получает сообщения и отправдяет их на дальнейшую обработку.
        """
        self.init_socket()

        while self.running:
            try:
                # Получаем данные клиента
                client, client_address = self.socket.accept()
            except OSError:
                pass
            else:
                server_log.info(f'Установлено соединение клиентом {client_address}')
                self.clients.append(client)

            # Создаём списки клиентов, ожидающих обработки
            read_lst = []
            try:
                if self.clients:
                    read_lst, self.listen_sockets, self.error_sockets = select.select(
                        self.clients, self.clients, [], 0)
            except OSError as e:
                server_log.error(f'Ошибка работы с сокетами: {e.errno}')

            # Получаем сообщения пользователей
            if read_lst:
                for sending_client in read_lst:
                    try:
                        self.create_response(get_message(sending_client), sending_client)

                    except (OSError, json.JSONDecodeError, TypeError) as e:
                        server_log.info(f'Ошибка обработки сообщения.', exc_info=e)
                        self.remove_client(sending_client)

    @Log()
    def remove_client(self, client):
        """
        Метод обработчик клиента с которым прервана связь.
        Ищет клиент и удаляет его из списков и базы.
        """
        server_log.info(f'Клиент {client.getpeername()} отключился от сервера.')
        for name in self.names:
            if self.names[name] == client:
                self.db.user_logout(name)
                del self.names[name]
                break
        self.clients.remove(client)
        client.close()

    @Log()
    def process_message(self, message):
        """
        Метод отправки сообщения клиенту.
        """
        if (message[TO] in self.names and
                self.names[message[TO]] in self.listen_sockets):
            try:
                send_message(self.names[message[TO]], message)
                server_log.info(f'Отправлено сообщение от {message[FROM]} для {message[TO]}.')
            except OSError:
                self.remove_client(message[TO])

        elif (message[TO] in self.names and
                self.names[message[TO]] not in self.listen_sockets):
            server_log.error(f'Связь с клиентом {message[TO]} потеряна.')
            self.remove_client(self.names[message[TO]])

        else:
            server_log.error(f'Пользователь {message[TO]} не зарегистрирован на сервере.')

    @Log()
    def create_response(self, message, client):
        """
        Функция проверяет поля сообщения на соответствие JIM-формату
        и отправляет сообщение на обработку
        :param client: сокет пользователя
        :param message: сообщение в виде словаря
        """
        server_log.debug(f'Разбор сообщения {message}')

        # Если получено presence-сообщение, сообщаем об успешном подключении
        if (ACTION in message and message[ACTION] == PRESENCE
                and TIME in message and USER in message
                and isinstance(message[USER], dict)):
            server_log.info(f'Принято presence-сообщение от: {message[USER]["account_name"]}')
            self.authorize_user(message, client)

        # Если получено текстовое сообщение отправляем его получателю
        elif (ACTION in message and message[ACTION] == MSG
                and TIME in message and FROM in message
                and TO in message and TEXT in message):
            server_log.info(f'Принято сообщение: {message[TEXT]}. От: {message[FROM]}')
            if message[TO] in self.names:
                self.db.update_actions_history(message[FROM], message[TO])
                self.process_message(message)
                try:
                    send_message(client, RESPONSE_200)
                except OSError:
                    self.remove_client(client)
            else:
                response = RESPONSE_400
                response[ERROR] = 'Пользователь не зарегистрирован на сервере.'
                try:
                    send_message(client, response)
                except OSError:
                    pass
            return

        # Если пользователь запрашивает список пользователей
        elif (ACTION in message and message[ACTION] == GET_USERS
                and FROM in message):
            server_log.info(f'Получен запрос списка пользователей от {message[FROM]}')
            response = RESPONSE_202
            response[ALERT] = self.db.get_all_users()
            try:
                send_message(client, response)
                server_log.info(f'Клиенту {message[FROM]} отправлен список пользователей')
            except OSError:
                self.remove_client(client)

        # Если пользователь запрашивает контакт-лист
        elif ACTION in message and message[ACTION] == GET_CONTACTS and FROM in message:
            server_log.info(f'Получен запрос списка контактов от {message[FROM]}')
            contact_list = self.db.get_user_contacts(message[FROM])
            response = RESPONSE_202
            response[ALERT] = contact_list
            try:
                send_message(client, response)
                server_log.info(f'Клиенту {message[FROM]} отправлен список контактов')
            except OSError:
                self.remove_client(client)

        # Если пользователь хочет добавить контакт в контакт-лист
        elif (ACTION in message and message[ACTION] == ADD_CONTACT
                and FROM in message and LOGIN in message):
            self.db.add_contact(message[FROM], message[LOGIN])
            try:
                send_message(client, RESPONSE_200)
                server_log.info(f'Пользователь {message[LOGIN]} добавлен в '
                                f'список контактов пользователя {message[FROM]}')
            except OSError:
                self.remove_client(client)

        # Если пользователь хочет удалить контакт
        elif (ACTION in message and message[ACTION] == DEL_CONTACT
                and FROM in message and LOGIN in message):
            self.db.delete_contact(message[FROM], message[LOGIN])
            try:
                send_message(client, RESPONSE_200)
                server_log.info(f'Пользователь {message[LOGIN]} удален из '
                                f'списка контактов пользователя {message[FROM]}')
            except OSError:
                self.remove_client(client)

        # Если получено сообщение о выходе, отключаем клиента
        elif ACTION in message and message[ACTION] == EXIT and FROM in message:
            self.remove_client(client)
            server_log.info(f'Клиент {client} отключился от сервера.')

        # Если это запрос публичного ключа пользователя
        elif (ACTION in message and message[ACTION] == PUBLIC_KEY_REQUEST
              and ACCOUNT_NAME in message):
            response = RESPONSE_511
            response[DATA] = self.db.get_pubkey(message[ACCOUNT_NAME])
            if response[DATA]:
                try:
                    send_message(client, response)
                except OSError:
                    self.remove_client(client)
            else:
                response = RESPONSE_400
                response[ERROR] = 'Нет публичного ключа для данного пользователя'
                try:
                    send_message(client, response)
                except OSError:
                    self.remove_client(client)

        else:
            response = RESPONSE_400
            response[TIME] = time()
            response[ERROR] = 'Некорректный запрос.'
            try:
                send_message(client, response)
                server_log.info(f'Сформировано сообщение об ошибке для клиента {client}')
            except OSError:
                self.remove_client(client)

    def authorize_user(self, message, sock):
        """
        Метод реализующий авторизацию пользователей.
        """
        # Если имя пользователя уже занято то возвращаем 400
        server_log.debug(f'Авторизация пользователя {message[USER]}')
        if message[USER][ACCOUNT_NAME] in self.names.keys():
            response = RESPONSE_400
            response[ERROR] = 'Имя пользователя уже занято.'
            try:
                server_log.debug(f'Имя пользователя {message[USER][ACCOUNT_NAME]} уже занято.')
                send_message(sock, response)
            except OSError:
                pass
            self.clients.remove(sock)
            sock.close()

        # Проверяем что пользователь зарегистрирован на сервере.
        elif not self.db.check_user(message[USER][ACCOUNT_NAME]):
            response = RESPONSE_400
            response[ERROR] = 'Пользователь не зарегистрирован.'
            try:
                server_log.debug(f'Пользователь {message[USER][ACCOUNT_NAME]} не зарегистрирован.')
                send_message(sock, response)
            except OSError:
                pass
            self.clients.remove(sock)
            sock.close()

        # Проводим авторизацию пользователя
        else:
            message_auth = RESPONSE_511
            # Набор байтов в hex представлении
            random_string = binascii.hexlify(os.urandom(64))
            message_auth[DATA] = random_string.decode('ascii')
            # Создаём хэш пароля и связки с рандомной строкой,
            # сохраняем серверную версию ключа
            serv_hash = hmac.new(self.db.get_hash(message[USER][ACCOUNT_NAME]), random_string, 'MD5')
            digest = serv_hash.digest()
            server_log.debug(f'Подготовлено авторизационное сообщение = {message_auth}')
            try:
                send_message(sock, message_auth)
                answer = get_message(sock)
            except OSError as err:
                server_log.debug('Ошибка авторизации:', exc_info=err)
                sock.close()
                return

            client_digest = binascii.a2b_base64(answer[DATA])
            # Если ответ клиента корректный, то сохраняем его в список пользователей.
            if (RESPONSE in answer and answer[RESPONSE] == 511
                    and hmac.compare_digest(digest, client_digest)):
                self.names[message[USER][ACCOUNT_NAME]] = sock
                client_ip, client_port = sock.getpeername()
                try:
                    send_message(sock, RESPONSE_200)
                except OSError:
                    self.remove_client(message[USER][ACCOUNT_NAME])

                # добавляем пользователя в список активных и сохраняем открытый ключ
                self.db.user_login(message[USER][ACCOUNT_NAME], client_ip, client_port, message[USER][PUBLIC_KEY])

            else:
                response = RESPONSE_400
                response[ERROR] = 'Неверный пароль.'
                try:
                    send_message(sock, response)
                except OSError:
                    pass
                self.clients.remove(sock)
                sock.close()
