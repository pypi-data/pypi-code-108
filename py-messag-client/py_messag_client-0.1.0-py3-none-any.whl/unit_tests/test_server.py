"""Unit-тесты сервера"""

import sys
import os
import unittest
sys.path.append(os.path.join(os.getcwd(), '..'))
from common.variables import RESPONSE, ERROR, USER, ACCOUNT_NAME, TIME, ACTION, PRESENCE, RESPONDEFAULT_IP_ADDRESSSE
from server import read_news


class TestServer(unittest.TestCase):
    '''
    В сервере только 1 функция для тестирования
    '''
    err_dict = {
        RESPONSE: 400,
        ERROR: 'Bad Request'
    }
    ok_dict = {RESPONSE: 200}

    # def test_ok_check(self):o
    #     """Корректный запрос"""
    #     self.assertEqual(read_news(
    #         {ACTION: PRESENCE, TIME: 1.1, USER: {ACCOUNT_NAME: 'Guest'}}), self.ok_dict)
    #
    # def test_no_action(self):
    #     """Ошибка если нет действия"""
    #     self.assertEqual(read_news(
    #         {TIME: '1.1', USER: {ACCOUNT_NAME: 'Guest'}}), self.err_dict)
    #
    # def test_wrong_action(self):
    #     """Ошибка если неизвестное действие"""
    #     self.assertEqual(read_news(
    #         {ACTION: 'Wrong', TIME: '1.1', USER: {ACCOUNT_NAME: 'Guest'}}), self.err_dict)
    #
    # def test_no_time(self):
    #     """Ошибка, если  запрос не содержит штампа времени"""
    #     self.assertEqual(read_news(
    #         {ACTION: PRESENCE, USER: {ACCOUNT_NAME: 'Guest'}}), self.err_dict)
    #
    # def test_no_user(self):
    #     """Ошибка - нет пользователя"""
    #     self.assertEqual(read_news(
    #         {ACTION: PRESENCE, TIME: '1.1'}), self.err_dict)
    #
    # def test_unknown_user(self):
    #     """Ошибка - не Guest"""
    #     self.assertEqual(read_news(
    #         {ACTION: PRESENCE, TIME: 1.1, USER: {ACCOUNT_NAME: 'Guest1'}}), self.err_dict)

#    ----------------------------------------------
    def test_ok_check_action(self):
        """проверка на значение ACTION"""
        self.assertNotEqual(read_news({ACTION: 'hello', TIME: 1.1, USER: {ACCOUNT_NAME: 'Guest'}}), self.ok_dict)

    def test_ok_check_user(self):
        """проверка на значение User"""
        self.assertNotEqual(read_news({ACTION: PRESENCE, TIME: 1.1, USER: {ACCOUNT_NAME: 1}}), self.ok_dict)


    def test_ok_check_user(self):
        """проверка на тип данных"""
        self.assertIsInstance(read_news({ACTION: PRESENCE, TIME: 1.1, USER: {ACCOUNT_NAME: 1}}), dict)

    def test_no_action(self):
        """проверка при корректном запросе не сработает ошибка"""
        self.assertIsNot(read_news({ACTION: PRESENCE, TIME: 1.1, USER: {ACCOUNT_NAME: 'Guest'}}), self.err_dict)

    def test_ok_check_dict(self):
        """Корректный запрос сравнение словарей"""
        self.assertDictEqual(read_news({ACTION: PRESENCE, TIME: 1.1, USER: {ACCOUNT_NAME: 'Guest'}}), self.ok_dict)

    def test_ok_check_dict_err(self):
        """Не корректный запрос сравнение словарей"""
        self.assertDictEqual(read_news({ACTION: PRESENCE, TIME: 1.1, USER: {ACCOUNT_NAME: 'Guest'}}), self.err_dict)


if __name__ == '__main__':
    unittest.main()
