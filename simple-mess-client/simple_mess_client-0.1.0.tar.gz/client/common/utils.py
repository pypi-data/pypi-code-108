"""
Общие функции клиента и сервера
"""
import json
from common.variables import MAX_PACKAGE_LENGTH, ENCODING
from common.decos import Log
from common.errors import NotDictError


@Log()
def send_message(socket_obj, message):
    """
    Функция, осуществляющая кодирование и отправку сообщений между
    клиентами
    :param socket_obj: объект сокета для обмена сообщениями
    :param message: словарь с атрибутами сообщения
    """
    if not isinstance(message, dict):
        raise NotDictError
    msg = json.dumps(message)
    socket_obj.send(msg.encode(ENCODING))


@Log()
def get_message(socket_obj):
    """
    Функция принимает и декодирует сообщение
    :param socket_obj: объект сокета для обмена сообщениями
    :return: словарь с атрибутами сообщения
    """
    response = socket_obj.recv(MAX_PACKAGE_LENGTH)
    # проверяеи пришедшие данные
    if isinstance(response, bytes):
        response = json.loads(response.decode(ENCODING))
        # Проверяем результат декодирования
        if isinstance(response, dict):
            return response
        raise NotDictError
    raise ValueError
