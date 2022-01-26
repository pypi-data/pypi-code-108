class RowException(Exception):

    def __init__(self):
        self.message_error = 'Укажите пожалуйста колличество строк, как целое положительное число!'

    def __str__(self):
        return self.message_error


class ConnectException(Exception):

    def __init__(self):
        self.message_error = 'Для подключения укажите корректно сервер, базу данных, схему и таблицу!'

    def __str__(self):
        return self.message_error
