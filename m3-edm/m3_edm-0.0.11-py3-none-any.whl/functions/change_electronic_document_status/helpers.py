from typing import (
    Type,
)

from m3_edm.functions.change_electronic_document_status.caches import (
    ChangeElectronicDocumentStatusRunnerCacheStorage,
)

from web_bb.core.base.function_tools.helpers import (
    WebBBBaseRunnerHelper,
)


class ChangeElectronicDocumentStatusRunnerHelper(WebBBBaseRunnerHelper):
    """
    Помощник пусковика функции "ЭДО - Смена статуса электронного документа"
    """

    def _prepare_cache_class(self) -> Type[ChangeElectronicDocumentStatusRunnerCacheStorage]:
        """
        Возвращает класс кеша помощника пусковика
        """
        return ChangeElectronicDocumentStatusRunnerCacheStorage
