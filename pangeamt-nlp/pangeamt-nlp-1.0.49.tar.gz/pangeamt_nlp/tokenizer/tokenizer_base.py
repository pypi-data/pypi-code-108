class TokenizerBase:
    def __init__(self, lang):
        self._lang = lang

    def tokenize(self, text: str):
        cls = self.__class__
        raise ValueError(f'"{cls}" should implement a "tokenize" method')

    def detokenize(self, text: str):
        cls = self.__class__
        raise ValueError(f'"{cls}" should implement a "detokenize" method')

    def get_lang(self):
        return self._lang

    lang = property(get_lang)
