class ProcessorBase:
    TYPE_TRANSFORMER = 0
    TYPE_VALIDATOR = 1

    def __init__(self, type, src_lang: str, tgt_lang: str):
        self._type = type
        self._src_lang = src_lang
        self._tgt_lang = tgt_lang

    def get_type(self) -> int:
        return self._type

    type = property(get_type)

    def get_src_lang(self) -> str:
        return self._src_lang

    src_lang = property(get_src_lang)

    def get_tgt_lang(self) -> str:
        return self._tgt_lang

    tgt_lang = property(get_tgt_lang)
