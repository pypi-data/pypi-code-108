from pangeamt_nlp.processor.base.normalizer_base import NormalizerBase
from pangeamt_nlp.seg import Seg
import re


class FrenchEnglishQuotesPostprocess(NormalizerBase):
    NAME = "french_englishquotes_postprocess"

    DESCRIPTION_TRAINING = """"""

    DESCRIPTION_DECODING = """
        Transform French quotes into English quotes
    """

    def __init__(self, src_lang: str, tgt_lang: str) -> None:
        super().__init__(src_lang, tgt_lang)

    def process_train(self, seg: Seg) -> None:
        pass

    def process_src_decoding(self, seg: Seg) -> None:
        pass

    def process_tgt_decoding(self, seg: Seg) -> None:
        if self.tgt_lang == 'fr':
            seg.tgt = seg.tgt.replace("« ", "“").replace(" »","”").replace("« ", "“").replace(" »", "”")
