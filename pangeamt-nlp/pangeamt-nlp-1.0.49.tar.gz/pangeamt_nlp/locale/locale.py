class Locale:
    def __init__(self, locale: str):
        self._locale = locale

    @staticmethod
    def to_lang(locale: str) -> str:
        return locale.lower()[0:2]

    @staticmethod
    def to_dialect(locale: str) -> str:
        return locale.lower()[0:5]


