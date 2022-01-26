import sys
sys.path.append('../')
from common.utils import *
from common.variables import *
import unittest
from errors import NonDictInputError


# Тестовый класс для тестирования отпраки и получения, при создании требует словарь, который будет прогонятся
# через тестовую функцию
class TestSocket:
    def __init__(self, test_dict):
        self.testdict = test_dict

    # тестовая функция отправки, корретно  кодирует сообщение, так-же сохраняет что должно было отправлено в сокет.
    def send(self, message_to_send):
        json_test_message = json.dumps(self.testdict)
        self.encoded_message = json_test_message.encode(ENCODING)
        self.receved_message = message_to_send

    def recv(self, max_len):
        json_test_message = json.dumps(self.testdict)
        return json_test_message.encode(ENCODING)


# Тестовый класс, собственно выполняющий тестирование.
class Tests(unittest.TestCase):
    test_dict_send = {
        ACTION: PRESENCE,
        TIME: 111111.111111,
        USER: {
            ACCOUNT_NAME: 'test_test'
        }
    }
    test_dict_recv_ok = {RESPONSE: 200}
    test_dict_recv_err = {
        RESPONSE: 400,
        ERROR: 'Bad Request'
    }

    # тестируем корректность работы фукции отправки,создадим тестовый сокет и проверим корректность отправки словаря
    def test_send_message(self):
        # экземпляр тестового словаря, хранит собственно тестовый словарь
        test_socket = TestSocket(self.test_dict_send)
        # вызов тестируемой функции, результаты будут сохранены в тестовом сокете
        send_message(test_socket, self.test_dict_send)
        # проверка корретности кодирования словаря. сравниваем результат довренного кодирования и результат от тестируемой функции
        self.assertEqual(test_socket.encoded_message, test_socket.receved_message)
        # дополнительно, проверим генерацию исключения, при не словаре на входе.
        self.assertRaises(NonDictInputError, send_message, test_socket, 1111)

    # тест функции приёма сообщения
    def test_get_message(self):
        test_sock_ok = TestSocket(self.test_dict_recv_ok)
        test_sock_err = TestSocket(self.test_dict_recv_err)
        # тест корректной расшифровки корректного словаря
        self.assertEqual(get_message(test_sock_ok), self.test_dict_recv_ok)
        # тест корректной расшифровки ошибочного словаря
        self.assertEqual(get_message(test_sock_err), self.test_dict_recv_err)


if __name__ == '__main__':
    unittest.main()
