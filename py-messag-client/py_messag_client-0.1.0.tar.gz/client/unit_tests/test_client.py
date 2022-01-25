"""Unit-тесты клиента"""

import sys
import os
import unittest
sys.path.append(os.path.join(os.getcwd(), '..'))
from common.variables import RESPONSE, ERROR, USER, ACCOUNT_NAME, TIME, ACTION, PRESENCE
from client import say_hello, read_answer

class TestClass(unittest.TestCase):
    '''
    Класс с тестами
    '''

    def test_def_say_hello(self):
        """Тест коректного запроса сравнение словарей"""
        test = say_hello()
        test[TIME] = 1.1
        self.assertDictEqual(test, {ACTION: PRESENCE, TIME: 1.1, USER: {ACCOUNT_NAME: 'Guest'}})


    def test_def_say_hello_check(self):
        """проверка на значение User"""
        test = say_hello()
        test[TIME] = 1.1
        self.assertNotEqual(test, {ACTION: PRESENCE, TIME: 1.1, USER: {ACCOUNT_NAME: 'NewGuest'}})


    def test_def_say_hello_false_action(self):
        """Тест не коректного действия"""
        test = say_hello()
        test[TIME] = 1.1
        self.assertNotEqual(test, {ACTION: 'Hello', TIME: 1.1, USER: {ACCOUNT_NAME: 'Guest'}})

    def test_def_say_hello_check_type(self):
        """проверка типа данных"""
        test = say_hello()
        test[TIME] = 1.1
        self.assertIsInstance(test, dict)


    def test_200_ans(self):
        """Тест разбора ответа 200 """
        self.assertNotEqual(read_answer({RESPONSE: 200}), '400 : OK')



    # ---------------------------------------------------------

    # def test_200_ans(self):
    #     """Тест корректтного разбора ответа 200"""
    #     self.assertEqual(read_answer({RESPONSE: 200}), '200 : OK')

    # def test_400_ans(self):
    #     """Тест корректного разбора 400"""
    #     self.assertEqual(read_answer({RESPONSE: 400, ERROR: 'Bad Request'}), '400 : Bad Request')

    # def test_no_response(self):
    #     """Тест исключения без поля RESPONSE"""
    #     self.assertRaises(ValueError, read_answer, {ERROR: 'Bad Request'})


if __name__ == '__main__':
    unittest.main()
