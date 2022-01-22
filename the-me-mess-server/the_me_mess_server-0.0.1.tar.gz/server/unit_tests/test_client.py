"""Unittest клиента"""

# import sys
# import os
# sys.path.append(os.path.join(os.getcwd(), '..'))
import time
import unittest
from lesson_7.client import create_new_presence, process_answer
from lesson_7.common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR
from lesson_7.common.errors import ReqFieldMissingError


class TestClient(unittest.TestCase):
    """Класс с тестами"""

    this_time = time.time()

    out = create_new_presence()
    out[TIME] = this_time

    test_out = {
        ACTION: PRESENCE,
        TIME: this_time,
        USER: {
            ACCOUNT_NAME: 'Guest'
        }
    }

    def test_create_new_presence(self):
        """Тест коректного запроса"""
        self.assertEqual(self.out, self.test_out)

    def test_process_answer_res_200(self):
        """Тест корректтного разбора ответа 200"""
        self.assertEqual(process_answer({RESPONSE: 200}), '200 : OK')

    def test_process_answer_res_400(self):
        """Тест корректного разбора 400"""
        self.assertEqual(process_answer({RESPONSE: 400, ERROR: 'Bad Request'}), f'400 : Bad Request')

    def test_process_answer_res_not(self):
        """Тест исключения без поля RESPONSE"""
        self.assertRaises(ReqFieldMissingError, process_answer, {})


if __name__ == '__main__':
    unittest.main()