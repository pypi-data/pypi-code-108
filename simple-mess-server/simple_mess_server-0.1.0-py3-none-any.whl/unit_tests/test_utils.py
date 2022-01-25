"""
Unit-тесты для модуля utils.py
"""

import json
import os
import sys
import unittest
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR

sys.path.append(os.path.join(os.getcwd(), '..'))
from common.variables import *
from common.utils import get_message, send_message
from common.errors import NotDictError


class TestUtils(unittest.TestCase):
    test_message = {
        ACTION: PRESENCE,
        TIME: 1,
        USER: {
            'account_name': 'User',
            'password': ''
        }
    }
    test_correct_response = {
        RESPONSE: 200,
        TIME: 1,
        ALERT: 'Соединение прошло успешно'
    }
    test_error_response = {
        RESPONSE: 400,
        TIME: 1,
        ERROR: 'Ошибка соединения'
    }

    # инициализируем тестовые сокеты для клиента и для сервера
    server_socket = None
    client_socket = None

    def setUp(self) -> None:
        # Создаем тестовый сокет для сервера
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.server_socket.bind((DEFAULT_LISTEN_ADDRESSES, DEFAULT_PORT))
        self.server_socket.listen(MAX_USERS)
        # Создаем тестовый сокет для клиента
        self.client_socket = socket(AF_INET, SOCK_STREAM)
        self.client_socket.connect((DEFAULT_IP, DEFAULT_PORT))

    def tearDown(self) -> None:
        # Закрываем созданные сокеты
        self.client_socket.close()
        self.server_socket.close()

    def test_send_wrong_message_from_client(self):
        """
        Проверяем исключение, если на входе не словарь
        """
        self.assertRaises(NotDictError, send_message, self.client_socket, 'not dict')

    def test_send_message_client_server(self):
        """
        Проверяем отправку корректного сообщения
        """
        client, client_address = self.server_socket.accept()
        # Отправляем сообщение
        send_message(self.client_socket, self.test_message)
        # Получаем и раскодируем сообщение
        test_response = client.recv(MAX_PACKAGE_LENGTH)
        test_response = json.loads(test_response.decode(ENCODING))
        client.close()
        # Проверяем соответствие изначального сообщения и прошедшего отправку
        self.assertEqual(self.test_message, test_response)

    def test_get_message_200(self):
        """
        Корректрая расшифровка коректного словаря
        """
        # Отправляем клиенту тестовый ответ о корректной отправке данных
        client, client_address = self.server_socket.accept()
        message = json.dumps(self.test_correct_response)
        client.send(message.encode(ENCODING))
        client.close()
        # получаем ответ
        response = get_message(self.client_socket)
        # сравниваем отправленный и полученный ответ
        self.assertEqual(self.test_correct_response, response)

    def test_get_message_400(self):
        """
        Корректрая расшифровка ошибочного словаря
        """
        # Отправляем клиенту тестовый ответ об ошибке
        client, client_address = self.server_socket.accept()
        message = json.dumps(self.test_error_response)
        client.send(message.encode(ENCODING))
        client.close()
        # получаем ответ
        response = get_message(self.client_socket)
        # сравниваем отправленный и полученный ответ
        self.assertEqual(self.test_error_response, response)

    def test_get_message_not_dict(self):
        """
        Проверяем возникновение ошибки, если пришедший объект не словарь
        """
        client, client_address = self.server_socket.accept()
        # Отправляем клиенту строку, вместо словаря
        message = json.dumps('not dict')
        client.send(message.encode(ENCODING))
        client.close()

        self.assertRaises(NotDictError, get_message, self.client_socket)

    def test_get_message_dict(self):
        """
        Проверяет является ли возвращаемый объект словарем
        """
        client, client_address = self.server_socket.accept()
        message = json.dumps(self.test_correct_response)
        client.send(message.encode(ENCODING))
        client.close()

        self.assertIsInstance(get_message(self.client_socket), dict)


if __name__ == '__main__':
    unittest.main()
