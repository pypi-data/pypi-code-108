from function_tools.errors import (
    BaseError,
)


class ChangeElectronicDocumentStatusError(BaseError):
    """
    Ошибка работы функции "ЭДО - Смена статуса электронного документа"
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
