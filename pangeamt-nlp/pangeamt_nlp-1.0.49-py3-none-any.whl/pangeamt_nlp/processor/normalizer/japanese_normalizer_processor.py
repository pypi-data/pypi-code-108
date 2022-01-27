import neologdn as _neologdn

from pangeamt_nlp.processor.base.normalizer_base import NormalizerBase
from pangeamt_nlp.seg import Seg


class JapaneseNormalizer(NormalizerBase):
    NAME = "japanese_normalizer"

    DESCRIPTION_TRAINING = """
        Apply the normalizer process to the source or the target, checking
        with the src_lang and tgt_lang to decide where to apply it.
    """

    DESCRIPTION_DECODING = """
        Apply the normalizer process to src if src_lang is japanese, do nothing
        otherwise.
    """

    def __init__(self, src_lang: str, tgt_lang: str) -> None:
        if src_lang is not "ja" and tgt_lang is not "ja":
            raise ValueError("Japanese Normalizer processor requires Japanese")

        super().__init__(src_lang, tgt_lang)

    def process_train(self, seg: Seg) -> None:
        if self.src_lang == "ja":
            seg.src = _neologdn.normalize(seg.src, repeat=1)
        else:
            seg.tgt = _neologdn.normalize(seg.tgt, repeat=1)

    def process_src_decoding(self, seg: Seg) -> None:
        if self.src_lang == "ja":
            seg.src = _neologdn.normalize(seg.src, repeat=1)

    def process_tgt_decoding(self, seg: Seg) -> None:
        pass
