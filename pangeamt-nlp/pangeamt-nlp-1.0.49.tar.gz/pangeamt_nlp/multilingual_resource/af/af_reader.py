import pangeamt_nlp.multilingual_resource.af.af


class AfReader:
    def __init__(self, src_lang:str, tgt_lang:str):
        self._src_lang = src_lang
        self._tgt_lang = tgt_lang
        self._inverted = None

    def initialize(self, af:"pangeamt_nlp.multilingual_resource.af.af.Af"):
        error = False
        if af.header.left.lang == self._src_lang:
            if af.header.right.lang == self._tgt_lang:
                self._inverted = False
            else:
                error = True
        elif af.header.left.lang == self._tgt_lang:
            if af.header.right.lang == self._src_lang:
                self._inverted = True
            else:
                error = True
        else:
            error = True

        if error:
            raise ValueError(f'Invalid Reader language for af `{af.file}`')

    def read(self, left:str, right:str):
        if self._inverted:
            return right, left
        return left, right

    def get_src_lang(self):
        return self._src_lang
    src_lang = property(get_src_lang)

    def get_tgt_lang(self):
        return self._tgt_lang
    tgt_lang = property(get_tgt_lang)






