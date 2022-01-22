"""Unittest сервера"""

# import sys
# import os
# sys.path.append(os.path.join(os.getcwd(), '..'))
import time
import unittest

from lesson_7.common.variables import TIME, ACTION, PRESENCE, USER, ACCOUNT_NAME, RESPONSE, ERROR
from lesson_7.my_testing_codes.old_files.server import process_client_message


class TestServer(unittest.TestCase):
    """В сервере только 1 функция для тестирования"""

    response_ok = {RESPONSE: 200}
    response_err = {
        RESPONSE: 400,
        ERROR: 'Bad Request'
    }
    message_to_server = {
        'ok': {
            ACTION: PRESENCE,
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: 'Guest'
            }},
        'not_action': {
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: 'Guest'
            }},
        'action_not_presence': {
            ACTION: 'not presence',
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: 'Guest'
            }},
        'not_time': {
            ACTION: PRESENCE,
            USER: {
                ACCOUNT_NAME: 'Guest'
            }},
        'not_user': {
            ACTION: PRESENCE,
            TIME: time.time(),
        },
        'account_name_not_Guest': {
            ACTION: PRESENCE,
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: 'Not Guest'
            }},
    }

    def test_process_client_message_ok(self):
        """Корректный запрос"""
        self.assertEqual(process_client_message(self.message_to_server['ok']), self.response_ok)

    def test_process_client_message_not_action(self):
        """Ошибка если нет действия"""
        self.assertEqual(process_client_message(self.message_to_server['not_action']), self.response_err)

    def test_process_client_message_action_not_presence(self):
        """Ошибка если неизвестное действие"""
        self.assertEqual(process_client_message(self.message_to_server['action_not_presence']), self.response_err)

    def test_process_client_message_not_time(self):
        """Ошибка, если  запрос не содержит штампа времени"""
        self.assertEqual(process_client_message(self.message_to_server['not_time']), self.response_err)

    def test_process_client_message_not_user(self):
        """Ошибка - нет пользователя"""
        self.assertEqual(process_client_message(self.message_to_server['not_user']), self.response_err)

    def test_process_client_message_account_name_not_Guest(self):
        """Ошибка - не Guest"""
        self.assertEqual(process_client_message(self.message_to_server['account_name_not_Guest']), self.response_err)


if __name__ == '__name__':
    unittest.main()