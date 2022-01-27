from typing import (
    Type,
)

from function_tools.managers import (
    RunnerManager,
)
from m3_edm.functions.change_electronic_document_status.runners import (
    ChangeElectronicDocumentStatusRunner,
)


class ChangeElectronicDocumentStatusRunnerManager(RunnerManager):
    """
    Менеджер пускателя функций системы "ЭДО - Смена статуса электронного документа"
    """

    def _prepare_runner_class(self) -> Type[ChangeElectronicDocumentStatusRunner]:
        """
        Возвращает класс пускателя функции "ЭДО - Смена статуса электронного документа"
        """
        return ChangeElectronicDocumentStatusRunner

    def _prepare_runner(self, *args, **kwargs):
        """
        Создание функции "ЭДО - Смена статуса электронного документа" и добавление ее в очередь исполнения пускателя
        """
        raise NotImplementedError
