class BilingualReader():
    def __init__(self, src_lang, tgt_lang):
        self._src_lang = src_lang
        self._tgt_lang = tgt_lang
        self._inverted = False

    def initialize(self, bilingual):
        error = False
        if bilingual.lang_1 == self._src_lang:
            if bilingual.lang_2 == self._tgt_lang:
                self._inverted = False
            else:
                error = True
        elif bilingual.lang_1  == self._tgt_lang:
            if bilingual.lang_2 == self._src_lang:
                self._inverted = True
            else:
                error = True
        else:
            error = True

        if error:
            raise ValueError(f'Invalid Reader language ({self._src_lang}, {self._tgt_lang}) for bilingual (`{bilingual.file_1}[{bilingual.lang_1}]`, `{bilingual.file_2}[{bilingual.lang_2}]`)')

    def read(self, text_1, text_2):
        if self._inverted:
            return text_2, text_1
        return text_1, text_2

