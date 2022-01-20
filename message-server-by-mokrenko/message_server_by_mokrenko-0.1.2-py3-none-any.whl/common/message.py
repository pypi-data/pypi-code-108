""" Определяем класс для обработки сообщений"""

import json
import sys
from common.variables import MAX_PACKAGE_LENGTH, ENCODING
from common.decorators import log
from common.errors import IncorrectDataRecivedError, NonDictInputError

sys.path.append('../')


class Message:
    """
    Класс для отсылки и полуения сообщений
    """

    @staticmethod
    @log
    def get(socketfrom):
        """
        Утилита приёма и декодирования сообщения
        принимает байты выдаёт словарь, если приняточто-то другое отдаёт ошибку значения
        :param socketfrom:
        :return:
        """

        encoded_response = socketfrom.recv(MAX_PACKAGE_LENGTH)
        if isinstance(encoded_response, bytes):
            json_response = encoded_response.decode(ENCODING)
            response = json.loads(json_response)
            # print(f'Получили сообщение: {json_response}')
            if isinstance(response, dict):
                return response
            raise IncorrectDataRecivedError
        raise IncorrectDataRecivedError

    @staticmethod
    @log
    def send(socketto, message):
        """
        Утилита кодирования и отправки сообщения
        принимает словарь и отправляет его
        :param socketto:
        :param message:
        :return:
        """
        if not isinstance(message, dict):
            raise NonDictInputError

        js_message = json.dumps(message)
        encoded_message = js_message.encode(ENCODING)
        socketto.send(encoded_message)
        # print(f'Послали сообщение: {js_message}')
