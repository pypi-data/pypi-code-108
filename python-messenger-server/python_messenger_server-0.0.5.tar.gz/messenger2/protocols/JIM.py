from time import time
from messenger2.protocols.BaseProtocol import BaseProtocol
import json


class JIM(BaseProtocol):

    """
    JIM protocol for sending information
    """

    MAX_ACTION_LENGTH = 15
    MAX_USER_LENGTH = 25
    MAX_MESSAGE_LENGTH = 500
    NEEDED_KEYS = ['action', 'time']
    ACTION_CODES = [
        'authenticate',
        'quit',
        'presence',
        'check',
        'probe',
        'msg',
        'join',
        'leave',
        'add',
        'del',
        "get_contacts",
        "error"
    ]
    POSSIBLE_TYPES = [
        'action',
        'time',
        'message',
        'encoding',
        'send_from',
        'send_to',
        'user',
        "password",
        'response',
        'alert',
        "login",
        "public_key",
        "info"
    ]

    MESSAGE = "msg"
    PRESENCE = "presence"
    JOIN = "join"
    ADD = "add"
    DELETE = "del"
    CONTACTS = "get_contacts"
    ALERT = "error"
    QUIT = "quit"

    def __init__(self, request=None):
        self.request = None
        self.__response = {
            'action': 'response',
            'encoding': JIM.ENCODING,
            'time': time(),
            'response': 200,
            'alert': JIM.SERVER_CODES.get(200),
            'info': ""
        }
        if request is not None:
            self.request = json.loads(request.decode(encoding=self.ENCODING))

            if not JIM.__check_request(self.request):
                self.__response.update({
                    'response': 400,
                    'alert': JIM.SERVER_CODES.get(400)
                })
            else:
                self.__response.update({
                    'response': 200,
                    'alert': JIM.SERVER_CODES.get(200)
                })

    def get_request(self, action, **kwargs):
        """
        Generates request according to its action and kwargs
        :param action: JIM protocol action
        :param kwargs: possible data
        :return: encoded byte request
        """
        request = {
            'action': action,
            'encoding': JIM.ENCODING,
            'time': time(),
        }
        try:
            if kwargs is not None:
                request.update(kwargs)
            if JIM.__check_request(request):
                print("true")
                self.request = request
                return json.dumps(request).encode(JIM.ENCODING)
            else:
                raise ValueError
        except ValueError:
            print('Wrong request format or too long values')
            for key, item in kwargs.items():
                request.pop(key)
            self.request = request
            return json.dumps(request).encode(JIM.ENCODING)

    def get_response(self):
        """
        return encoded byte response
        :return: byte response
        """
        self.__response["user"] = self.get_user()
        print(self.__response)
        return json.dumps(self.__response).encode(JIM.ENCODING)

    def set_response_code(self, code):
        """
        Set response code
        :param code: code according to base protocol
        :return: None
        """
        self.__response.update({
            'response': code,
            'alert': JIM.SERVER_CODES.get(code)
        })

    def set_response_action(self, action):
        """
        Set response action
        :param action: new JIM action
        :return:
        """
        self.__response.update({
            'action': action
        })

    def set_info(self, info):
        """
        Set some additional info
        :param info: some string
        :return: None
        """
        self.__response.update({
            "info": info
        })

    def get_info(self):
        """
        Get info from request
        :return: string info
        """
        return self.request.get("info")

    def get_message_info(self):
        """
        Get message info
        :return: message, send_to and send_from
        """
        return self.request.get('message'), self.request.get(
            'send_to'), self.request.get('send_from')

    def get_user(self):
        """
        Get user from request
        :return: username
        """
        user = self.request.get('user')
        return user

    def set_user(self, user):
        """
        Set user in response
        :param user: username
        :return: None
        """
        self.__response.update(
            {"user": user}
        )

    def get_password(self):
        """
        get password from request
        :return: password
        """
        password = self.request.get("password")
        return password

    def get_public_key(self):
        """
        get public key from request
        :return: public key
        """
        public_key = self.request.get("public_key")
        return public_key

    def set_public_key(self, public_key):
        """
        set publick key in response
        :param public_key: string public key
        :return: None
        """
        self.__response.update({
            'public_key': public_key
        })

    def set_message(self, message, send_from=None):
        """
        set message in response
        :param message: message
        :param send_from: Optional
        :return: None
        """
        if send_from is None:
            self.__response.update({
                'message': message
            })
        else:
            self.__response.update({
                'message': message,
                "send_from": send_from
            })

    def set_info(self, info):
        """
        set info message in response
        :param info: some string
        :return: None
        """
        self.__response.update({
            'info': info
        })

    @staticmethod
    def __check_request(request):
        """
        check if request is valid
        :param request: JIN protocol request
        :return: True or False
        """
        for key in JIM.NEEDED_KEYS:
            if key == 'action':
                action_code = request.get(key)
                if action_code not in JIM.ACTION_CODES or len(
                        action_code) > JIM.MAX_ACTION_LENGTH:
                    return False
            if key not in request.keys():
                return False

        for key in request.keys():
            if key not in JIM.POSSIBLE_TYPES:
                return False

            if key == 'user':
                user = request.get(key)
                if user is None:
                    return False
                elif len(user) > JIM.MAX_USER_LENGTH:
                    return False

            if key == 'message':
                # print(request)
                if len(request.get(key)) > JIM.MAX_MESSAGE_LENGTH:
                    return False

        return True

    @staticmethod
    def decode_response(response):
        """
        Decode response from json
        :param response: response json
        :return:
        """
        return json.loads(response.decode(JIM.ENCODING))

    @property
    def message_type(self):
        return True if self.request.get('action') == 'msg' else False

    @property
    def join_type(self):
        return True if self.request.get('action') == 'join' else False

    @property
    def quit_type(self):
        return True if self.request.get('action') == 'quit' else False

    @property
    def presence_type(self):
        return True if self.request.get('action') == 'presence' else False

    @property
    def add_type(self):
        return True if self.request.get("action") == "add" else False

    @property
    def del_type(self):
        return True if self.request.get("action") == "del" else False

    @property
    def get_contacts_type(self):
        return True if self.request.get("action") == "get_contacts" else False

    @property
    def response_type(self):
        return True if self.request.get("action") == "response" else False

    @property
    def alert_type(self):
        return True if self.request.get("action") == "error" else False

    @property
    def response_alert_type(self):
        return True if self.__response.get("action") == "error" else False
