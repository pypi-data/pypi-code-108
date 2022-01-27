from pangeamt_nlp.tokenizer.tokenizer_base import TokenizerBase
from thai_segmenter import tokenize

class ThaiTokenizer(TokenizerBase):
    NAME = "thai"
    LANGS = ["th"]

    def __init__(self, lang):
        super().__init__(lang)

    def tokenize(self, text):
        return (' ').join(tokenize(text.strip()))

    def detokenize(self, text):
        return ('').join(text.split(' '))
