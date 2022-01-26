import logging

DEFAULT_PORT = 8888
DEFAULT_IP_ADDRESS = '127.0.0.1'
ENCODING = 'utf-8'
LOGGING_LEVEL = logging.DEBUG
SERVER_DATABASE = 'sqlite:///server_base.db3'
CONNECTIONS = 5
MAX_PACKAGE_LENGTH = 1024

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

MESSAGE = 'message'
MESSAGE_TEXT = 'some text in message'
EXIT = 'exit'
GET_CONTACTS = 'get_contacts'
LIST_INFO = 'data_list'
REMOVE_CONTACT = 'remove'
ADD_CONTACT = 'add'
USERS_REQUEST = 'get_users'
PUBLIC_KEY_REQUEST = 'pubkey_need'

RESPONSE_200 = {RESPONSE: 200}
RESPONSE_202 = {RESPONSE: 202,
                LIST_INFO: None
                }
RESPONSE_400 = {
    RESPONSE: 400,
    ERROR: None
}

RESPONSE_511 = {
    RESPONSE: 511,
    DATA: None
}
