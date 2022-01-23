"""Unit-тесты клиента"""

import sys
import os
import unittest
sys.path.append(os.path.join(os.getcwd(), '../..'))
from common.variables import RESPONSE, ERROR, USER, ACCOUNT_NAME, TIME, ACTION, PRESENCE
from client import Client
from errors import ReqFieldMissingError, ServerError


class TestClass(unittest.TestCase):
    '''
    Класс с тестами
    '''
    def setUp(self):
        # Выполнить настройку тестов (если необходимо)
        self.client = Client()  # запустим без аргументов (выберет по умолчанию)
        super().setUp()

    def tearDown(self):
        # Выполнить завершающие действия (если необходимо)
        pass
        # self.client.close()

    def test_def_presense(self):
        """Тест коректного запроса"""
        test = self.client.create_presence()
        test[TIME] = 1.1  # время необходимо приравнять принудительно
                          # иначе тест никогда не будет пройден
        self.assertEqual(test, {ACTION: PRESENCE, TIME: 1.1, USER: {ACCOUNT_NAME: 'Guest'}})

    def test_200_ans(self):
        """Тест корректтного разбора ответа 200"""
        self.assertEqual(self.client.process_response_ans({RESPONSE: 200}), '200 : OK')

    def test_400_ans(self):
        """Тест корректного разбора 400"""
        self.assertRaises(ServerError, self.client.process_response_ans({RESPONSE: 400, ERROR: 'Bad Request'}), {ERROR: '400 : Bad Request'})
        # self.assertEqual(self.client.process_response_ans({RESPONSE: 400, ERROR: 'Bad Request'}), '400 : Bad Request')

    def test_no_response(self):
        """Тест исключения без поля RESPONSE"""
        self.assertRaises(ReqFieldMissingError, self.client.process_response_ans, {ERROR: 'Bad Request'})


if __name__ == '__main__':
    unittest.main()
