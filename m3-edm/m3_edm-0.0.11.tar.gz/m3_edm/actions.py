from m3_edm.models import (
    BaseElectronicDocument,
)
from m3_edm.providers import (
    BaseElectronicDocumentProvider,
)
from m3_edm.proxies import (
    BaseElectronicDocumentCardProxy,
    BaseElectronicDocumentListProxy,
)

from web_bb.core.base.actions import (
    AdvancedRecordListPack,
)


class BaseElectronicDocumentPack(AdvancedRecordListPack):
    """
    Базовый пак экшенов для работы с реестром ЭДО
    """

    url = ''
    shortname = ''
    title = ''
    title_plural = ''

    provider = BaseElectronicDocumentProvider(
        data_source=BaseElectronicDocument,
        card_proxy=BaseElectronicDocumentCardProxy,
        list_proxy=BaseElectronicDocumentListProxy,
    )
