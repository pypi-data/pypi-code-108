import json


def get_message(client):
    '''
    Функция приёма сообщений от удалённых компьютеров.
    Принимает сообщения JSON, декодирует полученное сообщение
    и проверяет что получен словарь.
    :param client: сокет для передачи данных.
    :return: словарь - сообщение.
    '''

    from common.variables import MAX_PACAGE_LEGTH
    from common.variables import ENCODING

    encoded_response = client.recv(MAX_PACAGE_LEGTH)
    json_response = encoded_response.decode(ENCODING)
    response = json.loads(json_response)
    if isinstance(response, dict):
        return response
    else:
        raise TypeError


def send_meccage(sock, message):
    '''
    Функция отправки словарей через сокет.
    Кодирует словарь в формат JSON и отправляет через сокет.
    :param sock: сокет для передачи
    :param message: словарь для передачи
    :return: ничего не возвращает
    '''

    print(f'{message}')
    if not isinstance(message, dict):
        raise TypeError
    from common.variables import ENCODING
    js_message = json.dumps(message)
    encoded_message = js_message.encode(ENCODING)
    sock.send(encoded_message)
