from sacremoses import MosesPunctNormalizer as _MosesPunctNormalizer

from pangeamt_nlp.processor.base.normalizer_base import NormalizerBase
from pangeamt_nlp.seg import Seg


class PunctProcessor(NormalizerBase):
    NAME = "punct_normalizer"

    DESCRIPTION_TRAINING = """
        Apply the punct process to src and tgt.
    """
    DESCRIPTION_DECODING = """
        Apply the punct process to src.
    """

    def __init__(self, src_lang: str, tgt_lang: str):
        super().__init__(src_lang, tgt_lang)

        self._mpn_src = _MosesPunctNormalizer(src_lang)
        self._mpn_tgt = _MosesPunctNormalizer(tgt_lang)

    def process_train(self, seg: Seg) -> None:
        seg.src = self._mpn_src.normalize(seg.src)
        seg.tgt = self._mpn_tgt.normalize(seg.tgt)

    def process_src_decoding(self, seg: Seg) -> None:
        seg.src = self._mpn_src.normalize(seg.src)

    def process_tgt_decoding(self, seg: Seg) -> None:
        pass
