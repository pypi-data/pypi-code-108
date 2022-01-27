'''
Main project module of the client side logic.

This module contains the statements of establishing connection with server
and processing GUI of client program window.
'''

import os
import sys
import argparse
from logging import getLogger
from Cryptodome.PublicKey import RSA
from PyQt5.QtWidgets import QApplication, QMessageBox

from common.variables import *
from errors import ServerError
from decorators import log_decorator
from client.transport import ClientTransport
from client.main_window import ClientMainWindow
from client.client_db_storage import ClientDatabaseStorage
from client.start_window import StartUserNameEnteringWindow

LOG = getLogger('client_logger')


@log_decorator
def arg_parser():
    '''Command line arguments parser'''

    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-n', '--name', default=None, nargs='?')
    parser.add_argument('-p', '--password', default='', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])

    if not 1023 < namespace.port < 65536:
        LOG.critical(
            f'Valid addresses are 1024 to 65535. The client finishes.')
        exit(1)
    return namespace.addr, namespace.port, namespace.name, namespace.password


if __name__ == '__main__':
    server_address, server_port, client_name, client_password = arg_parser()
    client_app = QApplication(sys.argv)

    # Start users' authorization dialog
    start_window = StartUserNameEnteringWindow()

    if not client_name or not client_password:
        client_app.exec_()
        if start_window.ok_button_pressed:
            client_name = start_window.client_name.text()
            client_password = start_window.client_password.text()
        else:
            exit(0)

    LOG.info(
        f'Launched client with parameters: ip_address: {server_address} , '
        f'port: {server_port}, username: {client_name}'
    )

    dir_path = os.path.dirname(os.path.realpath(__file__))
    key_file = os.path.join(dir_path, f'{client_name}.key')

    if not os.path.exists(key_file):
        keys = RSA.generate(2048, os.urandom)
        with open(key_file, 'wb') as key:
            key.write(keys.export_key())
    else:
        with open(key_file, 'rb') as key:
            keys = RSA.import_key(key.read())
    LOG.debug('Keys successfully loaded')
    database = ClientDatabaseStorage(client_name)

    try:
        transport = ClientTransport(
            server_port,
            server_address,
            database,
            client_name,
            client_password,
            keys)
    except ServerError as error:
        message = QMessageBox()
        message.critical(start_window, 'Server Error', error.text)
        exit(1)
    transport.setDaemon(True)
    transport.start()

    del start_window

    main_window = ClientMainWindow(database, transport, keys)
    main_window.make_connection(transport)
    client_app.exec_()

    transport.transport_shutdown()
    transport.join()

