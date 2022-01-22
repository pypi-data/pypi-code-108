"""Unit-тесты утилит"""

import unittest
import json
from common.variables import RESPONSE, ERROR, USER, ACCOUNT_NAME, TIME, ACTION, PRESENCE, ENCODING
from common.utils import get_message, send_message


class TestSocket:
    """
    Тестовый класс для тестирования отправки и получения сообщений
    """

    def __init__(self, test_dict):
        self.test_dict = test_dict
        self.encoded_message = None
        self.received_message = None

    def send(self, message_to_send):
        json_test_message = json.dumps(self.test_dict)
        self.encoded_message = json_test_message.encode(ENCODING)
        self.received_message = message_to_send

    def recv(self, max_len):
        json_test_message = json.dumps(self.test_dict)
        return json_test_message.encode(ENCODING)


class TestUtils(unittest.TestCase):
    dict_to_send = {
        ACTION: PRESENCE,
        TIME: 1.1,
        USER: {
            ACCOUNT_NAME: 'test'
        }
    }
    dict_ok = {RESPONSE: 200}
    dict_error = {
        RESPONSE: 400,
        ERROR: 'Bad Request'
    }

    def test_send_message(self):
        test_socket = TestSocket(self.dict_to_send)
        send_message(test_socket, self.dict_to_send)
        self.assertEqual(test_socket.encoded_message, test_socket.received_message)
        self.assertRaises(TypeError, send_message, test_socket, "wrong_dictionary")

    def test_get_message(self):
        test_sock_ok = TestSocket(self.dict_ok)
        test_sock_error = TestSocket(self.dict_error)
        test_sock_not_dict = TestSocket([])
        self.assertEqual(get_message(test_sock_ok), self.dict_ok)
        self.assertEqual(get_message(test_sock_error), self.dict_error)
        self.assertRaises(ValueError, get_message, test_sock_not_dict)


if __name__ == '__main__':
    unittest.main()
