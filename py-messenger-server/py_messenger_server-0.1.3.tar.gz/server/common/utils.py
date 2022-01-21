"""Функции приема и передачи сообщений через сокеты"""

import json
import sys

from common.decorators import Log


@Log()
def get_message(client):
    """ Утилита приёма и декодирования сообщения принимает байты выдаёт словарь,
        если принято что-то другое отдаёт ошибку значения

    """

    encoded_response = client.recv(MAX_PACKAGE_LENGTH)
    if isinstance(encoded_response, bytes):
        json_response = encoded_response.decode(ENCODING)
        response = json.loads(json_response)
        if isinstance(response, dict):
            return response
        raise ValueError
    raise ValueError


@Log()
def send_message(sock, message):
    """  Функция отправки словарей через сокет. Кодирует словарь в формат JSON и отправляет через сокет

    """
    if not isinstance(message, dict):
        raise TypeError
    js_message = json.dumps(message)
    encoded_message = js_message.encode(ENCODING)
    sock.send(encoded_message)
