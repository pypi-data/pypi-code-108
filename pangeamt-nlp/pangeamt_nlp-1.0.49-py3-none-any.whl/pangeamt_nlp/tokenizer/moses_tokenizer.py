from pangeamt_nlp.tokenizer.tokenizer_base import TokenizerBase
from sacremoses import MosesTokenizer as _MosesTokenizer
from sacremoses import MosesDetokenizer as _MosesDetokenizer


class MosesTokenizer(TokenizerBase):
    NAME = "moses"
    LANGS = [""]

    def __init__(self, lang):
        super().__init__(lang)
        self._mtk = _MosesTokenizer(lang)
        self._dtk = _MosesDetokenizer(lang)

    def tokenize(self, text):
        return (" ").join(self._mtk.tokenize(text, escape=False))

    def detokenize(self, text):
        return self._dtk.detokenize(text)
