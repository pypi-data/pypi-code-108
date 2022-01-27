from pangeamt_nlp.tokenizer.tokenizer_base import TokenizerBase

class NoneTokenizer(TokenizerBase):
    NAME = "none"
    LANGS = [""]

    def __init__(self, lang):
        super().__init__(lang)

    def tokenize(self, text):
        return text

    def detokenize(self, text):
        return (" ").join(text)
