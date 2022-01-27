from pangeamt_nlp.tokenizer.tokenizer_base import TokenizerBase
from MeCab import Tagger as _Tagger


class MecabTokenizer(TokenizerBase):
    NAME = "mecab"
    LANGS = ["ja"]

    def __init__(self, lang):
        super().__init__(lang)
        self._tok = _Tagger("-Owakati")

    def __getstate__(self):
        return {"_lang": self._lang}

    def __setstate__(self, state):
        for key, value in state.items():
            setattr(self, key, value)

    def __getnewargs__(self):
        return self._lang,

    def __reduce_ex__(self, protocol):
        return (
            MecabTokenizer,
            self.__getnewargs__(),
            self.__getstate__(),
            None,
            None
        )

    def tokenize(self, text):
        return self._tok.parse(text).strip()

    def detokenize(self, text):
        return ('').join(text)
