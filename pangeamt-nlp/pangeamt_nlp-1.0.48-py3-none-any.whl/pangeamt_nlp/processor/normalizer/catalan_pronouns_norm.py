from pangeamt_nlp.processor.base.normalizer_base import NormalizerBase
from pangeamt_nlp.seg import Seg
from pangeamt_nlp.utils.strip_and_catch_white import strip_and_catch_white


class CatalanPronouns(NormalizerBase):
    NAME = "catalan_pronouns_norm"
    DESCRIPTION_TRAINING = """
          Tokenizing Catalan pronouns that are suffix joint by - to the verb
    """
    DESCRIPTION_DECODING = """
          Tokenizing Catalan pronouns that are suffix joint by - to the verb
    """

    def __init__(self, src_lang: str, tgt_lang: str) -> None:
        super().__init__(src_lang, tgt_lang)

    def process_train(self, seg: Seg) -> None:
        if self.src_lang == 'ca':
            seg.src = seg.src.replace("-me", " -me").replace("-te", " -te").replace("-se", " -se").replace("-nos", " -nos").replace("-vos", " -vos").\
                replace("-lo", " -lo").replace("-los", " -los").replace("-la", " -la").replace("-les", " -les").\
                replace("-ho", " -ho").replace("-li", " -li").replace("-ne", " -ne").replace("-hi", " -hi")
        #TODO maybe we should think about a version with Catalan as target but it will require to detokenize it later
#        if self.tgt_lang == 'ca':
#            seg.tgt = seg.src.replace("-me", " -me").replace("-te", " -te").replace("-se", " -se").replace("-nos", " -nos").replace("-vos", " -vos").\
#                replace("-lo", " -lo").replace("-los", " -los").replace("-la", " -la").replace("-les", " -les").\
#                replace("-ho", " -ho").replace("-li", " -li").replace("-ne", " -ne").replace("-hi", " -hi")

    def process_src_decoding(self, seg: Seg) -> None:
        if self.src_lang == 'ca':
            seg.src = seg.src.replace("-me", " -me").replace("-te", " -te").replace("-se", " -se").replace("-nos", " -nos").replace("-vos", " -vos").\
                replace("-lo", " -lo").replace("-los", " -los").replace("-la", " -la").replace("-les", " -les").\
                replace("-ho", " -ho").replace("-li", " -li").replace("-ne", " -ne").replace("-hi", " -hi")

    def process_tgt_decoding(self, seg: Seg) -> None:
        pass
