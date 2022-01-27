from pangeamt_nlp.tokenizer.tokenizer_base import TokenizerBase
import jieba as _jieba


class JiebaTokenizer(TokenizerBase):
    NAME = "jieba"
    LANGS = ["zh", "tw"]

    def __init__(self, lang):
        super().__init__(lang)

    def tokenize(self, text):
        return (" ").join(_jieba.cut(text)).strip()

    def detokenize(self, text):
        return ('').join(text)
