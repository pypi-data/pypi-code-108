"""
Модуль для запуска клиентской части мессенджера.
параметры командной строки:
addr          — ip-адрес сервера;
port          — tcp-порт на сервере, по умолчанию 7777;
-n --name     — имя пользователя;
-p --password — пароль.
"""
import argparse
import logging
import os
from sys import argv, exit

from Cryptodome.PublicKey import RSA
from PyQt5.QtWidgets import QApplication

from client.client_db import ClientStorage
from client.main_window import ClientMainWindow
from client.start_dialog import UserNameDialog
from client.transport import MessengerClient
from common.decos import Log
from common.errors import ServerError
from common.variables import *

client_log = logging.getLogger('client')


@Log()
def get_client_settings():
    """
    Получает параметры клиента из командной сторки
    или назначает параметры по умолчанию.
    Возвращает порт и ip-адрес сервера, имя пользователя и пароль
    """
    args = argparse.ArgumentParser()
    args.add_argument('address', default=DEFAULT_IP, nargs='?')
    args.add_argument('port', type=int, default=DEFAULT_PORT, nargs='?')
    args.add_argument('-n', '--name', default=None, nargs='?')
    args.add_argument('-p', '--password', default='', nargs='?')
    namespace = args.parse_args(argv[1:])
    connection_ip = namespace.address
    connection_port = namespace.port
    user_name = namespace.name
    user_password = namespace.password

    if not (1024 < connection_port < 65535):
        client_log.critical(f'Неверное значение порта {connection_port}.\n'
                            f'Порт должен находиться в диапазоне от 1024 до 65535.')
        exit(1)

    client_log.debug(f'Получены параметры подключения {connection_ip}:{connection_port}')

    return connection_ip, connection_port, user_name, user_password


@Log()
def main():
    """
    Основная функция для запуска клиентской части мессенджера.
    """
    conn_ip, conn_port, user_name, user_password = get_client_settings()

    client_app = QApplication(argv)

    if not user_name or not user_password:
        start_dialog = UserNameDialog()
        client_app.exec_()
        if start_dialog.ok_pressed:
            user_name = start_dialog.client_name.text()
            user_password = start_dialog.client_pass.text()
            del start_dialog
        else:
            exit(0)

    dir_path = os.path.dirname(os.path.realpath(__file__))
    key_file = os.path.join(dir_path, f'{user_name}.key')
    if not os.path.exists(key_file):
        keys = RSA.generate(2048, os.urandom)
        with open(key_file, 'wb') as key:
            key.write(keys.export_key())
    else:
        with open(key_file, 'rb') as key:
            keys = RSA.import_key(key.read())

    client_db = ClientStorage(user_name)

    # Создаём подключение
    try:
        connection = MessengerClient(user_name, user_password, conn_ip, conn_port, client_db, keys)
    except ServerError as error:
        print(error.text)
        exit(1)
    connection.setDaemon(True)
    connection.start()

    client_log.info(f'Запущен клиент для пользователя {user_name}.'
                    f'Адрес подключения: {conn_ip}, порт:{conn_port}')

    # GUI
    main_window = ClientMainWindow(client_db, connection, keys)
    main_window.make_connection(connection)
    main_window.setWindowTitle(f'Добро пожаловать, {user_name}')
    client_app.exec_()

    connection.connection_shutdown()
    connection.join()


if __name__ == '__main__':
    main()
