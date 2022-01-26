"""

Супер мелкие функции, которые нужны от 3 использований

"""
import hashlib
import json
from itertools import islice
import jwt


def chunks_generator(iterable, count_items_in_chunk):
    """
    Очень внимательно! Не дает обходить дважды

    :param iterable:
    :param count_items_in_chunk:
    :return:
    """
    iterator = iter(iterable)
    for first in iterator:  # stops when iterator is depleted
        def chunk():  # construct generator for next chunk
            yield first  # yield element from for loop
            for more in islice(iterator, count_items_in_chunk - 1):
                yield more  # yield more elements from the iterator

        yield chunk()  # in outer generator, yield next chunk


def chunks(list_, count_items_in_chunk):
    """
    разбить list (l) на куски по n элементов

    :param list_:
    :param count_items_in_chunk:
    :return:
    """
    for i in range(0, len(list_), count_items_in_chunk):
        yield list_[i:i + count_items_in_chunk]


def pretty_json(obj):
    """
    Представить объект в вище json красиво отформатированной строки
    :param obj:
    :return:
    """
    return json.dumps(obj, sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False)


def decode_jwt(input_text, secure_key):
    """
    Раскодирование строки на основе ключа
    :param input_text: исходная строка
    :param secure_key: секретный ключ
    :return:
    """
    if input_text is None:
        return None

    encoded = (input_text.split(":")[1]).encode('utf-8')
    decoded = jwt.decode(encoded, secure_key)
    return decoded['sub']


def file_hash_sum(file_full_path: str) -> str:
    """
    Хэш от содержимого файла
    :param file_full_path: полный путь к файлу
    :return: Хэш строкой
    """
    with open(file_full_path, "rb") as f:
        h = hashlib.sha256()
        while True:
            data = f.read(8192)
            if not data:
                break
            h.update(data)
    return h.hexdigest()
