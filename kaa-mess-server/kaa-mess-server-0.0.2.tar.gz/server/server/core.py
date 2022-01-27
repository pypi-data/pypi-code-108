'''
This is the main module of the server side of project.
'''

import os
import sys
import hmac
import socket
import binascii

from json import JSONDecodeError
from select import select
from threading import Thread
from logging import getLogger

sys.path.append('../')
from server.descriptors import Port
from common.variables import *
from common.utils import send_message, get_message

LOG = getLogger('server_logger')


class MessageProcessor(Thread):
    port = Port()

    def __init__(self, listen_address, listen_port, database):
        self.address = listen_address
        self.port = listen_port

        self.database = database
        self.socket_obj = None
        self.clients = []
        self.listen_sockets = None
        self.error_sockets = None

        self.running_transport = True
        self.names = dict()

        super().__init__()

    def run(self):
        self.init_socket()
        while self.running_transport:
            try:
                client, client_address = self.socket_obj.accept()
            except OSError:
                pass
            else:
                LOG.info(f'Connection established with PC {client_address}')
                client.settimeout(5)
                self.clients.append(client)

            recv_data_list = []
            send_data_list = []
            serr_list = []

            try:
                if self.clients:
                    recv_data_list, self.listen_sockets, self.error_sockets = select(self.clients, self.clients, [], 0)
            except OSError as err:
                LOG.error(f'Work with socket error: {err.errno}')

            if recv_data_list:
                for client_with_message in recv_data_list:
                    try:
                        self.processing_message(
                            get_message(client_with_message), client_with_message)
                    except (OSError, JSONDecodeError, TypeError) as err:
                        LOG.debug(f'Getting data from client exception', exc_info=err)
                        self.remove_client(client_with_message)

    def remove_client(self, client):
        LOG.info(f'Client {client.getpeername()} disconnected from server')
        for name in self.names:
            if self.names[name] == client:
                self.database.user_logout(name)
                del self.names[name]
                break
        self.clients.remove(client)
        client.close()

    def init_socket(self):
        LOG.info(f'Server is running')
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.bind((self.address, self.port))
        transport.settimeout(0.5)

        self.socket_obj = transport
        self.socket_obj.listen(DEFAULT_MAX_QUEUE_LENGTH)

    def message_handler(self, message):
        if message[RECIPIENT] in self.names and self.names[message[RECIPIENT]] in self.listen_sockets:
            try:
                send_message(self.names[message[RECIPIENT]], message)
                LOG.info(f'Sent message to user {message[RECIPIENT]} from user {message[SENDER]}')
            except OSError:
                self.remove_client(message[RECIPIENT])
        elif message[RECIPIENT] in self.names and self.names[message[RECIPIENT]] not in self.listen_sockets:
            LOG.error(f'Connection with client {message[RECIPIENT]} was lost')
            self.remove_client(self.names[message[RECIPIENT]])
        else:
            LOG.error(f'User {message[RECIPIENT]} is not registered on the server')

    def processing_message(self, message, client):
        LOG.debug(f'Handle with client message')
        if ACTION in message and message[ACTION] == PRESENCE and TIME in message and USER in message:
            self.authorize_user(message, client)
        elif ACTION in message and message[ACTION] == MESSAGE and RECIPIENT in message \
                and TIME in message and SENDER in message and MESSAGE_TEXT in message \
                and self.names[message[SENDER]] == client:
            if message[RECIPIENT] in self.names:
                self.database.process_message(message[SENDER], message[RECIPIENT])
                self.message_handler(message)
                try:
                    send_message(client, RESPONSE_200)
                except OSError:
                    self.remove_client(client)
            else:
                response = RESPONSE_400
                response[ERROR] = 'User is not registered on the server'
                try:
                    send_message(client, response)
                except OSError:
                    pass
            return
        elif ACTION in message and message[ACTION] == EXIT and USER in message \
                and self.names[message[USER]] == client:
            self.remove_client(client)
        elif ACTION in message and message[ACTION] == GET_CONTACTS and USER in message \
                and self.names[message[USER]] == client:
            response = RESPONSE_202
            response[LIST_INFO] = self.database.users_contacts_list(message[USER])
            try:
                send_message(client, response)
            except OSError:
                self.remove_client(client)
        elif ACTION in message and message[ACTION] == ADD_CONTACT and USER in message \
                and self.names[message[USER]] == client:
            self.database.add_contact(message[USER], message[CONTACT])
            try:
                send_message(client, RESPONSE_200)
            except OSError:
                self.remove_client(client)
        elif ACTION in message and message[ACTION] == REMOVE_CONTACT and USER in message and CONTACT in message and self.names[message[USER]] == client:
            self.database.remove_contact(message[USER], message[CONTACT])
            try:
                send_message(client, response)
            except OSError:
                self.remove_client(client)
        elif ACTION in message and message[ACTION] == USERS_REQUEST and USER in message and self.names[message[USER]] == client:
            response = RESPONSE_202
            response[LIST_INFO] = [user[0] for user in self.database.all_users_list()]
            try:
                send_message(client, response)
            except OSError:
                self.remove_client(client)
        elif ACTION in message and message[ACTION] == PUBLIC_KEY_REQUEST and USER in message:
            response = RESPONSE_511
            response[DATA] = self.database.get_public_key(message[USER])
            if response[DATA]:
                try:
                    send_message(client, response)
                except OSError:
                    self.remove_client(client)
            else:
                response = RESPONSE_400
                response[ERROR] = 'The public key is absent'
                try:
                    send_message(client, response)
                except OSError:
                    self.remove_client(client)
        else:
            response = RESPONSE_400
            response[ERROR] = 'Incorrect request'
            try:
                send_message(client, response)
            except OSError:
                self.remove_client(client)

    def authorize_user(self, message, socket_obj):
        LOG.debug(f'Start auth process for {message[USER]}')
        if message[USER] in self.names.keys():
            response = RESPONSE_400
            response[ERROR] = 'Username is not free'
            try:
                LOG.debug(f'Username busy, sending {response}')
                send_message(socket_obj, response)
            except OSError:
                LOG.debug('OS Error')
                pass
            self.clients.remove(socket_obj)
            socket_obj.close()
        elif not self.database.check_user(message[USER]):
            response = RESPONSE_400
            response[ERROR] = 'User is not registered'
            try:
                LOG.debug(f'Unknown uwsrname, sending {response}')
                send_message(socket_obj, response)
            except OSError:
                pass
            self.clients.remove(socket_obj)
            socket_obj.close()
        else:
            LOG.debug('Correct username, starting password check')
            message_auth = RESPONSE_511
            random_string = binascii.hexlify(os.urandom(64))
            message_auth[DATA] = random_string.decode('ascii')
            hash_obj = hmac.new(self.database.get_hash(message[USER]), random_string, 'MD5')
            digest = hash_obj.digest()
            LOG.debug(f'Auth message = {message_auth}')
            try:
                send_message(socket_obj, message_auth)
                answer = get_message(socket_obj)
            except OSError as err:
                LOG.debug('Error in auth, data:', exc_info=err)
                socket_obj.close()
                return
            client_digest = binascii.a2b_base64(answer[DATA])
            if RESPONSE in answer and answer[RESPONSE] == 511 and hmac.compare_digest(digest, client_digest):
                self.names[message[USER]] = socket_obj
                client_ip, client_port = socket_obj.getpeername()
                try:
                    send_message(socket_obj, RESPONSE_200)
                except OSError:
                    self.remove_client(message[USER])
                self.database.user_login(
                    message[USER],
                    client_ip,
                    client_port,
                    message[PUBLIC_KEY])
            else:
                response = RESPONSE_400
                response[ERROR] = 'Incorrect password'
                try:
                    send_message(socket_obj, response)
                except OSError:
                    pass
                self.clients.remove(socket_obj)
                socket_obj.close()

    def service_update_list(self):
        for client in self.names:
            try:
                send_message(self.names[client], RESPONSE_205)
            except OSError:
                self.remove_client(self.names[client])

