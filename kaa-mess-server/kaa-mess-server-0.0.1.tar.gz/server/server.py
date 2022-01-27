import os
import sys

from PyQt5.QtCore import Qt
from logging import getLogger
from argparse import ArgumentParser
from configparser import ConfigParser
from PyQt5.QtWidgets import QApplication

from common.variables import *
from decorators import log_decorator
from server.core import MessageProcessor
from server.main_window import MainWindow
from server.server_db_storage import ServerDatabaseStorage

LOG = getLogger('server_logger')


@log_decorator
def args_parser(default_port, default_address):
    '''Command line arguments parser'''

    parser = ArgumentParser()
    parser.add_argument('-p', default=default_port, type=int)
    parser.add_argument('-a', default=default_address)
    namespace = parser.parse_args(sys.argv[1:])
    return namespace.a, namespace.p


@log_decorator
def config_load():
    '''Config file parser'''

    config = ConfigParser()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    config.read(f'{dir_path}/{"server+++.ini"}')
    if 'SETTINGS' in config:
        return config
    else:
        config.add_section('SETTINGS')
        config.set('SETTINGS', 'Default_port', str(DEFAULT_PORT))
        config.set('SETTINGS', 'Listen_address', '')
        config.set('SETTINGS', 'Database_path', '')
        config.set('SETTINGS', 'Database_file', 'server_database.db3')
        return config


@log_decorator
def main():
    '''The main function of server module'''

    config = config_load()
    listen_address, listen_port = args_parser(
        config['SETTINGS']['Default_port'],
        config['SETTINGS']['Listen_address']
    )
    database = ServerDatabaseStorage(
        os.path.join(
            config['SETTINGS']['Database_path'],
            config['SETTINGS']['Database_file']))

    server = MessageProcessor(listen_address, listen_port, database)
    server.daemon = True
    server.start()

    server_app = QApplication(sys.argv)
    server_app.setAttribute(Qt.AA_DisableWindowContextHelpButton)
    main_window = MainWindow(database, server, config)

    server_app.exec_()
    server.running_transport = False


if __name__ == '__main__':
    main()

