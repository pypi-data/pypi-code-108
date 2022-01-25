import configparser
import os
import sys
import argparse
import threading

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

from server_file.core import MessageProcessor
from server_file.main_window import MainWindow
from server_file.server_database import DataBase
from common.variables import *
from common.decos import log

SERVER_LOGGER = logging.getLogger('server')

new_connection = False
conflag_lock = threading.Lock()


@log
def arg_parser(default_port, default_address):
    '''Парсер аргументов коммандной строки.'''
    SERVER_LOGGER.debug(
        f'Инициализация парсера аргументов коммандной строки: {sys.argv}')
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=default_port, type=int, nargs='?')
    parser.add_argument('-a', default=default_address, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p
    SERVER_LOGGER.debug('Аргументы успешно загружены.')
    return listen_address, listen_port


def config_load():
    '''Парсер конфигурационного ini файла.'''
    config = configparser.ConfigParser()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    config.read(f"{dir_path}/{'server+++.ini'}")
    if 'SETTINGS' in config:
        return config
    else:
        config.add_section('SETTINGS')
        config.set('SETTINGS', 'Default_port', str(DEFAULT_PORT))
        config.set('SETTINGS', 'Listen_Address', '')
        config.set('SETTINGS', 'Database_path', '')
        config.set('SETTINGS', 'Database_file', 'server_database.db3')
        return config


@log
def main():
    '''Основная функция'''
    config = config_load()

    listen_address, listen_port = arg_parser(
        config['SETTINGS']['Default_port'], config['SETTINGS']['Listen_Address'])

    database = DataBase(
        os.path.join(
            config['SETTINGS']['Database_path'],
            config['SETTINGS']['Database_file']))

    server = MessageProcessor(listen_address, listen_port, database)
    server.daemon = True
    server.start()

    # Создаём графическое окружение для сервера:
    server_app = QApplication(sys.argv)
    server_app.setAttribute(Qt.AA_DisableWindowContextHelpButton)
    main_window = MainWindow(database, server, config)

    server_app.exec_()
    server.running = False


if __name__ == '__main__':
    main()
