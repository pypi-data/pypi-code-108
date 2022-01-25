'''
Сборник констант
'''

import logging

DEFAULT_PORT = 7777
DEFAULT_IP_ADRESS = '127.0.0.1'
MAX_CONNECTIONS = 5
MAX_PACAGE_LEGTH = 1024
ENCODING = 'utf-8'

ACTION = 'action'
TIME = 'time'
USER = 'user'
ACCOUNT_NAME = 'account_name'
SENDER = 'sender'
DESTINATION = 'to'
DATA = 'bin'
PUBLIC_KEY = 'pubkey'

PRESENCE = 'presence'
RESPONSE = 'response'
ERROR = 'error'
RESPONDEFAULT_IP_ADRESS = 'responedefault_ip_adress'
MESSAGE = 'message'
MESSAGE_TEXT = 'mess_text'
EXIT = 'exit'
GET_CONTACTS = 'get_contacts'
LIST_INFO = 'data_list'
REMOVE_CONTACT = 'remove'
ADD_CONTACT = 'add'
USERS_REQUEST = 'get_users'
PUBLIC_KEY_REQUEST = 'pubkey_need'

RESPONSE_200 = {RESPONSE: 200}
RESPONSE_400 = {
    RESPONSE: 400,
    ERROR: None
}
RESPONSE_202 = {RESPONSE: 202,
                LIST_INFO:None
                }

RESPONSE_205 = {
    RESPONSE: 205
}

RESPONSE_511 = {
    RESPONSE: 511,
    DATA: None
}

LOGGING_LEVEL = logging.DEBUG
FORMATTER_DEFAULT = logging.Formatter('%(asctime)s %(levelname) -8s %(filename) -11s %(message)s')

SERVER_DATABASE = 'sqlite:///server_base.db3'