"""Программа-клиент"""
from socket import socket
import sys
import os
from Cryptodome.PublicKey import RSA
from PyQt5.QtWidgets import QApplication, QMessageBox
import json
import time
import argparse
import threading
import logs.config_client_log
from common.variables import *
from common.utils import *
from common.transport import Transport
from common.decorators import logc, log
from common.errors import IncorrectDataRecivedError, ReqFieldMissingError, ServerError
from common.metaclasses import ClientVerifier
import socket
from client.database import ClientDatabase
from client.client_transport import ClientTransport
from client.main_window import ClientMainWindow
from client.start_dialog import UserNameDialog

# Инициализация клиентского логера
LOGGER = Transport.set_logger_type('client')


@log
def arg_parser():
    """Создаём парсер аргументов коммандной строки
    и читаем параметры, возвращаем 3 параметра
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-n', '--name', default=None, nargs='?')
    parser.add_argument('-p', '--password', default='', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_name = namespace.name
    client_passwd = namespace.password

    return server_address, server_port, client_name, client_passwd


class Client(threading.Thread, Transport, metaclass=ClientVerifier):
    """
    Класс определеят свойства и методы для клиента.
    """

    # для работы проверки класса в метаклассе

    def __init__(self, ipaddress, port, client_name):
        self.LOGGER = Transport.set_logger_type('client')
        Transport.__init__(self, ipaddress, port)
        self.ipaddress = self.ipaddress or DEFAULT_IP_ADDRESS
        self.client_name = client_name
        """Сообщаем о запуске"""
        print(f'Консольный месседжер. Клиентский модуль. Имя пользователя: {self.client_name}')
        # Если имя пользователя не было задано, необходимо запросить пользователя.
        if not client_name:
            self.client_name = input('Введите имя пользователя: ')
        else:
            print(f'Клиентский модуль запущен с именем: {self.client_name}')

        threading.Thread.__init__(self)

        self.LOGGER.info(
            f'Запущен клиент с парамертами: адрес сервера: {self.ipaddress}, '
            f'порт: {self.port}, имя пользователя: {self.client_name}')

    @logc
    def init(self):
        """
        Метод инициализации клиента
        :return:
        """
        try:
            # Таймаут 1 секунда, необходим для освобождения сокета.
            self.socket.settimeout(1)
            self.socket.connect((self.ipaddress, self.port))
        except ServerError as error:
            self.LOGGER.error(f'Не удалось соединиться с сервером по адресу {self.ipaddress} на порту {self.port}. '
                              f'Сервер вернул ошибку {error.text}')
            return -1
        except (ConnectionRefusedError, ConnectionError):
            self.LOGGER.critical(
                f'Не удалось подключиться к серверу {self.ipaddress}:{self.port}, '
                f'конечный компьютер отверг запрос на подключение.')
            return -1
        except socket.timeout:
            self.LOGGER.critical(
                f'Не удалось подключиться к серверу {self.ipaddress}:{self.port}, '
                f'Сервер недоступен. Проверьте запущен ли он.')
            return -1

        self.LOGGER.info(f'Клиент соединился с сервером {self.socket}')

    @logc
    def message_from_server(self, sock, my_username):
        """Функция - обработчик сообщений других пользователей, поступающих с сервера"""
        while True:
            try:
                message = self.get(sock)
                if ACTION in message and message[ACTION] == MESSAGE and \
                        SENDER in message and DESTINATION in message \
                        and MESSAGE_TEXT in message and message[DESTINATION] == my_username:
                    print(f'\nПолучено сообщение от пользователя {message[SENDER]}:'
                          f'\n{message[MESSAGE_TEXT]}')
                    self.LOGGER.info(f'Получено сообщение от пользователя {message[SENDER]}:'
                                     f'\n{message[MESSAGE_TEXT]}')
                else:
                    self.LOGGER.error(f'Получено некорректное сообщение с сервера: {message}')
            except IncorrectDataRecivedError:
                self.LOGGER.error(f'Не удалось декодировать полученное сообщение.')
            except (OSError, ConnectionError, ConnectionAbortedError,
                    ConnectionResetError, json.JSONDecodeError):
                self.LOGGER.critical(f'Потеряно соединение с сервером.')
                break

    @logc
    def create_message(self, sock, account_name='Guest'):
        """
        Функция запрашивает кому отправить сообщение и само сообщение,
        и отправляет полученные данные на сервер
        :param sock:
        :param account_name:
        :return:
        """
        to_user = input('Введите получателя сообщения: ')
        message = input('Введите сообщение для отправки: ')
        message_dict = {
            ACTION: MESSAGE,
            SENDER: account_name,
            DESTINATION: to_user,
            TIME: time.time(),
            MESSAGE_TEXT: message
        }
        self.LOGGER.debug(f'Сформирован словарь сообщения: {message_dict}')
        try:
            self.send(sock, message_dict)
            self.LOGGER.info(f'Отправлено сообщение для пользователя {to_user}')
        except Exception:
            self.LOGGER.critical('Потеряно соединение с сервером.')
            sys.exit(1)

    @logc
    def user_interactive(self, sock, username):
        """Функция взаимодействия с пользователем, запрашивает команды, отправляет сообщения"""
        self.print_help()
        while True:
            command = input('Введите команду: ')
            if command == 'message':
                self.create_message(sock, username)
            elif command == 'help':
                self.print_help()
            elif command == 'exit':
                self.send(sock, self.create_exit_message(username))
                print('Завершение соединения.')
                self.LOGGER.info('Завершение работы по команде пользователя.')
                # Задержка неоходима, чтобы успело уйти сообщение о выходе
                time.sleep(0.5)
                break
            else:
                print('Команда не распознана, попробойте снова. help - вывести поддерживаемые команды.')

    @logc
    def create_presence(self, account_name='Guest'):
        """
        Функция генерирует запрос о присутствии клиента
        :param account_name:
        :return:
        """
        out = {
            ACTION: PRESENCE,
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: account_name
            }
        }
        self.LOGGER.debug(f'Сформировано {PRESENCE} сообщение для пользователя {account_name}')
        return out

    @logc
    def process_message(self, message):
        """
        Функция разбирает ответ сервера
        :param message:
        :return:
        """

        self.LOGGER.debug(f'Разбор сообщения от сервера: {message}')
        if RESPONSE in message:
            if message[RESPONSE] == 200:
                return '200 : OK'
            elif message[RESPONSE] == 400:
                raise ServerError(f'400 : {message[ERROR]}')
        raise ReqFieldMissingError(RESPONSE)

    @logc
    # Функция инициализатор базы данных. Запускается при запуске, загружает данные в базу с сервера.
    def database_load(self, database):
        # Загружаем список известных пользователей
        try:
            self.users_list = Transport.user_list_request(self.socket, self.client_name)
        except ServerError:
            self.LOGGER.error('Ошибка запроса списка известных пользователей.')
        else:
            database.add_users(self.users_list)

        # Загружаем список контактов
        try:
            self.contacts_list = Transport.contacts_list_request(self.socket, self.client_name)
        except ServerError:
            self.LOGGER.error('Ошибка запроса списка контактов.')
        else:
            for contact in self.contacts_list:
                database.add_contact(contact)

    @logc
    def run(self):
        """
            Обработчик событий от сервера
            :return:
        """

        try:
            message_to_server = self.create_presence(self.client_name)
            self.send(self.socket, message_to_server)
            self.LOGGER.info(f'Послалали сообщение на сервер {message_to_server}')
            answer = self.process_message(self.get(self.socket))
            self.LOGGER.info(f'Установлено соединение с сервером. Ответ сервера: {answer}')
            # print(answer)
        except (ValueError, json.JSONDecodeError):
            self.LOGGER.error('Не удалось декодировать сообщение сервера.')
            sys.exit(1)
        except ServerError as error:
            self.LOGGER.error(f'При установке соединения сервер вернул ошибку: {error.text}')
            sys.exit(1)
        except ReqFieldMissingError as missing_error:
            self.LOGGER.error(f'В ответе сервера отсутствует необходимое поле '
                              f'{missing_error.missing_field}')
            sys.exit(1)
        except (ConnectionRefusedError, ConnectionError):
            self.LOGGER.critical(
                f'Не удалось подключиться к серверу {self.ipaddress}:{self.port}, '
                f'конечный компьютер отверг запрос на подключение.')
            sys.exit(1)
        else:

            # Инициализация БД
            database = ClientDatabase(self.client_name)
            self.database_load(database)

            # # затем запускаем отправку сообщений и взаимодействие с пользователем.
            # user_interface = threading.Thread(target=self.user_interactive, args=(self.socket, self.client_name))
            # user_interface.daemon = True
            # user_interface.start()
            # Если соединение с сервером установлено корректно, запускаем поток взаимодействия с пользователем
            module_sender = ClientSender(self.client_name, self.socket, database)
            module_sender.daemon = True
            module_sender.start()
            self.LOGGER.debug('Запущены процессы')

            # # Если соединение с сервером установлено корректно,
            # # запускаем клиенский процесс приёма сообщний
            # receiver = threading.Thread(target=self.message_from_server, args=(self.socket, self.client_name))
            # receiver.daemon = True
            # receiver.start()

            # затем запускаем поток - приёмник сообщений.
            module_receiver = ClientReader(self.client_name, self.socket, database)
            module_receiver.daemon = True
            module_receiver.start()

            # Watchdog основной цикл, если один из потоков завершён,
            # то значит или потеряно соединение или пользователь
            # ввёл exit. Поскольку все события обработываются в потоках,
            # достаточно просто завершить цикл.
            while True:
                time.sleep(1)
                # if receiver.is_alive() and user_interface.is_alive():
                if module_receiver.is_alive() and module_sender.is_alive():
                    continue
                break


def main():
    # Сообщаем о запуске
    # print('Консольный месседжер. Клиентский модуль.')

    # Загружаем параметы коммандной строки
    server_address, server_port, client_name, client_passwd = arg_parser()
    LOGGER.debug('Args loaded')

    # Создаём клиентское приложение
    client_app = QApplication(sys.argv)

    # Если имя пользователя не было указано в командной строке, то запросим его
    start_dialog = UserNameDialog()

    # Если имя пользователя не было указано в командной строке то запросим его
    if not client_name or not client_passwd:
        client_app.exec_()
        # Если пользователь ввёл имя и нажал ОК, то сохраняем ведённое и удаляем объект, инааче выходим
        if start_dialog.ok_pressed:
            client_name = start_dialog.client_name.text()
            client_passwd = start_dialog.client_passwd.text()
            LOGGER.debug(f'Using USERNAME = {client_name}, PASSWD = {client_passwd}.')
        else:
            exit(0)

    # Записываем логи
    LOGGER.info(
        f'Запущен клиент с параметрами: адрес сервера: {server_address} , порт: {server_port},'
        f' имя пользователя: {client_name}')

    # Загружаем ключи с файла, если же файла нет, то генерируем новую пару.
    dir_path = os.path.dirname(os.path.realpath(__file__))
    key_file = os.path.join(dir_path, f'{client_name}.key')
    if not os.path.exists(key_file):
        keys = RSA.generate(2048, os.urandom)
        with open(key_file, 'wb') as key:
            key.write(keys.export_key())
    else:
        with open(key_file, 'rb') as key:
            keys = RSA.import_key(key.read())

    # !!!keys.publickey().export_key()
    LOGGER.debug("Keys successfully loaded.")

    # Создаём объект базы данных
    database = ClientDatabase(client_name)

    # Создаём объект - транспорт и запускаем транспортный поток
    try:
        transport = ClientTransport(
            server_port,
            server_address,
            database,
            client_name,
            client_passwd,
            keys)
        LOGGER.debug("Transport ready.")
    except ServerError as error:
        message = QMessageBox()
        message.critical(start_dialog, 'Ошибка сервера', error.text)
        exit(1)
    transport.setDaemon(True)
    transport.start()

    # Удалим объект диалога за ненадобностью
    del start_dialog

    # Создаём GUI
    main_window = ClientMainWindow(database, transport, keys)
    main_window.make_connection(transport)
    main_window.setWindowTitle(f'Чат Программа alpha release - {client_name}')
    client_app.exec_()

    # Раз графическая оболочка закрылась, закрываем транспорт
    transport.transport_shutdown()
    transport.join()


if __name__ == '__main__':
    main()
