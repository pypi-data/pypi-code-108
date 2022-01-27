from typing import (
    Type,
)

from function_tools.runners import (
    LazySavingRunner,
)
from m3_edm.functions.change_electronic_document_status.helpers import (
    ChangeElectronicDocumentStatusRunnerHelper,
)
from m3_edm.functions.change_electronic_document_status.validators import (
    ChangeElectronicDocumentStatusRunnerValidator,
)


class ChangeElectronicDocumentStatusRunner(LazySavingRunner):
    """
    Пусковик функции "ЭДО - Смена статуса электронного документа"
    """

    def _prepare_validator_class(self) -> Type[ChangeElectronicDocumentStatusRunnerValidator]:
        """
        Возвращает класс валидатора пусковика
        """
        return ChangeElectronicDocumentStatusRunnerValidator

    def _prepare_helper_class(self) -> Type[ChangeElectronicDocumentStatusRunnerHelper]:
        """
        Возвращает класс помощника пусковика
        """
        return ChangeElectronicDocumentStatusRunnerHelper
