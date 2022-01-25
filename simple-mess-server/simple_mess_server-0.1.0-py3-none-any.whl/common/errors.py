"""
Ошибки, которые могут возникнуть при работе сервера и клиента
"""


class NotDictError(Exception):
    def __str__(self):
        return 'Аргумент функции должен быть словарем'


class ServerError(Exception):
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return self.text
