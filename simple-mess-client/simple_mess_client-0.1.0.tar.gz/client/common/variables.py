"""
Настройки по умолчанию и описание
JIM-протокола для передачи сообщений
"""

DEFAULT_PORT = 7777
DEFAULT_IP = '127.0.0.1'
DEFAULT_LISTEN_ADDRESSES = ''
TIMEOUT = 0.5

MAX_PACKAGE_LENGTH = 4096
MAX_USERS = 10

ENCODING = 'utf-8'

# JIM-протокол
ACTION = 'action'
TIME = 'time'
TO = 'to'
FROM = 'from'
TEXT = 'message'
USER = 'user'
LOGIN = 'user_login'
RESPONSE = 'response'
ALERT = 'alert'
ERROR = 'error'
DATA = 'bin'
ACCOUNT_NAME = 'account_name'
PUBLIC_KEY = 'pubkey'

# Действия (actions)
PRESENCE = 'presence'
MSG = 'msg'
EXIT = 'quit'
GET_CONTACTS = 'get_contacts'
GET_USERS = 'get_users'
ADD_CONTACT = 'add_contact'
DEL_CONTACT = 'del_contact'
PUBLIC_KEY_REQUEST = 'pubkey_need'

# Ответы сервера
RESPONSE_200 = {
    RESPONSE: 200,
    ALERT: None
}

RESPONSE_202 = {
    RESPONSE: 202,
    ALERT: None
}

RESPONSE_400 = {
    RESPONSE: 400,
    ERROR: None
}

RESPONSE_511 = {
    RESPONSE: 511,
    DATA: None
}
