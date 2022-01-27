from web_bb.core.base.forms import (
    AdvancedListWindow,
    BaseEditWindow,
)


class BaseElectronicDocumentListWindow(AdvancedListWindow):
    """
    Базовый класс окна реестра электронных документов
    """

    map2win = True
    automap2js = True
    enable_preview = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title = 'Электронный документооборот'


class BaseElectronicDocumentDetailWindow(BaseEditWindow):
    map2win = True
    automap2js = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.frozen_size(800, 600)
