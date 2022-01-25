class IncorrectDataRecivedError(Exception):
    def __str__(self):
        return 'Принято некорректное сообщение от клиента'


class NonDictInputError(Exception):
    def __str__(self):
        return 'Аргумент функции должен быть словарем'


class ReqFieldMissingError(Exception):
    def __init__(self, missing_field):
        self.missing_field = missing_field

    def __str__(self):
        return f'В принятом словаре отсутствует обязательное поле {self.missing_field}'


class ServerError(Exception):
    """
    Класс - исключение, для обработки ошибок сервера.
    При генерации требует строку с описанием ошибки,
    полученную с сервера.
    """

    def __init__(self, text):
        self.text = text

    def __str__(self):
        return self.text
