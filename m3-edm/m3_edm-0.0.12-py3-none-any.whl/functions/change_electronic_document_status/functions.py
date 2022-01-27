from function_tools.functions import (
    LazySavingFunction,
)


class ChangeElectronicDocumentStatusFunction(LazySavingFunction):
    """
    Функция "ЭДО - Смена статуса электронного документа"
    """

    verbose_name = 'ЭДО - Смена статуса электронного документа'

    def __init__(
        self,
        *args,
        notice: str,
        **kwargs,
    ):
        self._notice = notice

        super().__init__(*args, **kwargs)

    def _prepare(self):
        """
        Выполнение действий функций системы
        """
        if self.result.has_not_errors:
            self._change_document_status()
            self._log_changing_document_status()

    def _change_document_status(self):
        """
        Смена статуса документа
        """
        raise NotImplementedError

    def _log_changing_document_status(self):
        """
        Логирование смены статуса документа
        """
        raise NotImplementedError
