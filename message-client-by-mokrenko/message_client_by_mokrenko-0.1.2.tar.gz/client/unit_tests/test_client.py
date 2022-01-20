"""Unit-тесты клиента"""

import sys
import os
import time
import unittest

sys.path.append(os.path.join(os.getcwd(), '..'))
from common.variables import RESPONSE, ERROR, USER, ACCOUNT_NAME, TIME, ACTION, PRESENCE
from client import Client


class TestClient(unittest.TestCase):
    '''
    Класс с тестами
    '''

    def test_def_presense(self):
        """Тест коректного запроса"""
        test = Client.create_presence()
        tt = time.time()
        test[TIME] = tt  # время необходимо приравнять принудительно
        # иначе тест никогда не будет пройден
        self.assertEqual(test, {ACTION: PRESENCE, TIME: tt, USER: {ACCOUNT_NAME: 'Guest'}})

    def test_time_type(self):
        """Тип значения атрибута time должно быть float"""
        self.assertNotEqual(isinstance(Client.create_presence()[TIME], float), False)

    def test_200_ans(self):
        """Тест корректтного разбора ответа 200"""
        self.assertEqual(Client.process_message({RESPONSE: 200}), '200 : OK')

    def test_400_ans(self):
        """Тест корректного разбора 400"""
        self.assertEqual(Client.process_message({RESPONSE: 400, ERROR: 'Bad Request'}), '400 : Bad Request')

    def test_no_response(self):
        """Тест исключения без поля RESPONSE"""
        self.assertRaises(ValueError, Client.process_message, {ERROR: 'Bad Request'})


if __name__ == '__main__':
    unittest.main()
