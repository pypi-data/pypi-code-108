from sacremoses import MosesPunctNormalizer as _MosesNormalizer

from pangeamt_nlp.processor.base.normalizer_base import NormalizerBase
from pangeamt_nlp.seg import Seg


class MosesNormalizerProcessor(NormalizerBase):
    NAME = "moses_normalizer"

    DESCRIPTION_TRAINING = """
        Apply the moses normalizer to source and target.
    """
    DESCRIPTION_DECODING = """
        Apply the moses normalizer to src.
    """

    def __init__(self, src_lang: str, tgt_lang: str) -> None:
        super().__init__(src_lang, tgt_lang)
        self._mn_src = _MosesNormalizer(src_lang)
        self._mn_tgt = _MosesNormalizer(tgt_lang)

    def process_train(self, seg: Seg) -> None:
        seg.src = self._mn_src.normalize(seg.src)
        seg.tgt = self._mn_tgt.normalize(seg.tgt)

    def process_src_decoding(self, seg: Seg) -> None:
        seg.src = self._mn_src.normalize(seg.src)

    def process_tgt_decoding(self, seg: Seg) -> None:
        pass
