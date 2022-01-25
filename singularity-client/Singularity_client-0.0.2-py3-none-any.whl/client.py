import argparse
import logging
import os
import sys

from Crypto.PublicKey import RSA
from PyQt5.QtWidgets import QApplication, QMessageBox

from client_file.main_window import ClientMainWindow
from client_file.transp import ClientTransport
from client_file.user_name_dialog import UserNameDialog
from client_file.client_database import ClientDatabase
from common.variables import DEFAULT_IP_ADRESS, DEFAULT_PORT
from common.decos import log
from common.errors import ServerError

CLIENT_LOGGER = logging.getLogger('client_file')


@log
def arg_parser():
    """
    Парсер аргументов командной строки, возвращает кортеж из 4 элементов
    адрес сервера, порт, имя пользователя, пароль.
    Выполняет проверку на корректность номера порта.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-n', '--name', default=None, nargs='?')
    parser.add_argument('-p', '--password', default='', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_name = namespace.name
    client_passwd = namespace.password

    # проверим подходящий номер порта
    if not 1023 < server_port < 65536:
        CLIENT_LOGGER.critical(
            f'Попытка запуска клиента с неподходящим номером порта: {server_port}. '
            f'Допустимы адреса с 1024 до 65535. Клиент завершается.')

    return server_address, server_port, client_name, client_passwd


if __name__ == '__main__':
    server_adr, server_port, client_name, client_passwd = arg_parser()

    client_app = QApplication(sys.argv)
    user_name_dialog = UserNameDialog()
    if not client_name or not client_passwd:
        client_app.exec_()
        if user_name_dialog.ok_pressed:
            client_name = user_name_dialog.client_name.text()
            client_passwd = user_name_dialog.client_passwd.text()
            CLIENT_LOGGER.debug(f'Using USERNAME = {client_name}, PASSWD = {client_passwd}.')
        else:
            exit(0)

    CLIENT_LOGGER.info(
        f'Запущен клиент с парамертами: адрес сервера: {server_adr} , порт: {server_port}, имя пользователя: {client_name}')
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
    CLIENT_LOGGER.debug("Keys successfully loaded.")
    database = ClientDatabase(client_name)

    try:
        transport = ClientTransport(server_port, server_adr, database, client_name, client_passwd,
                                    keys)
    except ServerError as error:
        message = QMessageBox()
        message.critical(user_name_dialog, 'Ошибка сервера', error.text)
        print(error.text)
        exit(1)
    transport.setDaemon(True)
    transport.start()

    main_window = ClientMainWindow(database, transport, keys)
    main_window.make_connection(transport)
    main_window.setWindowTitle(f'Чат Программа alpha release - {client_name}')
    client_app.exec_()

    transport.transport_shutdown()
    transport.join()

#


#
#
# # Функция инициализатор базы данных. Запускается при запуске, загружает данные в базу с сервера.
# def database_load(sock, database, username):
#     try:
#         users_list = user_list_request(sock, username)
#     except ServerError:
#         CLIENT_LOGGER.error('Ошибка запроса списка известных пользователей.')
#     else:
#         database.add_users(users_list)
#
#     try:
#         contacts_list = contacts_list_request(sock, username)
#         CLIENT_LOGGER.info(f'Ваш список контактов {contacts_list}')
#     except ServerError:
#         CLIENT_LOGGER.error('Ошибка запроса списка контактов.')
#     else:
#         for contact in contacts_list:
#             database.add_contact(contact)
#
#
# def main():
#     server_adr, server_port, client_name = arg_parser()
#     print(f'Консольный месседжер. Клиентский модуль. Имя пользователя: {client_name}')
#     if not client_name:
#         client_name = input('Введите имя пользователя: ')
#
#     CLIENT_LOGGER.info(
#         f'Запущен клиент с парамертами: адрес сервера: {server_adr}, '
#         f'порт: {server_port}, имя пользователя: {client_name}')
#     try:
#         transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         transport.settimeout(1)
#
#         transport.connect((server_adr, server_port))
#         send_meccage(transport, create_presence(client_name))
#         answer = process_answer(get_message(transport))
#         CLIENT_LOGGER.info(f'Принят ответ от сервера:{answer}')
#     except json.JSONDecodeError:
#         CLIENT_LOGGER.error(f'Не удалось декодировать JSON от сервера')
#         sys.exit(1)
#     except ConnectionRefusedError:
#         CLIENT_LOGGER.critical(f'Не удалось подключиться к серверу {server_adr}:{server_port} '
#                                f'Сервер отверг запрос на подключение')
#         sys.exit(1)
#     except ReqFieldMissingError as missing_error:
#         CLIENT_LOGGER.error(f'В ответе сервера отсутвует необходимое поле '
#                             f'{missing_error.missing_field}')
#     else:
#         database = ClientDatabase(client_name)
#         database_load(transport, database, client_name)
#
#         module_reciver = ClientReader(client_name, transport, database)
#         module_reciver.daemon = True
#         module_reciver.start()
#
#         module_sender = ClientSender(client_name, transport, database)
#         module_sender.daemon = True
#         module_sender.start()
#         CLIENT_LOGGER.debug('Запущены процессы')
#
#         while True:
#             time.sleep(1)
#             if module_reciver.is_alive() and module_sender.is_alive():
#                 continue
#             break
#
#
# if __name__ == '__main__':
