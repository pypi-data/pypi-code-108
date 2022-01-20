import unicodedata

from pangeamt_nlp.processor.base.normalizer_base import NormalizerBase
from pangeamt_nlp.seg import Seg


class UnicodeAccentNorm(NormalizerBase):

    NAME = "unicode_accent_norm"

    DESCRIPTION_TRAINING = """
        Normalises the unicode string of both target and source to NFC form: 
        all accented characters are in combined form, not in decomposed form
    """

    DESCRIPTION_DECODING = """
        Normalises the unicode string of the source to NFC form: 
        all accented characters are in combined form, not in decomposed form
    """

    def _normalize(self, text):
        return unicodedata.normalize("NFC", text)

    # Called when training
    def process_train(self, seg: Seg) -> None:
        seg.src = self._normalize(seg.src)
        if seg.tgt is not None:
            seg.tgt = self._normalize(seg.tgt)

    # Called when using model (before calling model to translate)
    def process_src_decoding(self, seg: Seg) -> None:
        seg.src = self._normalize(seg.src)

    # Called when using model (before calling model to translate)
    def process_tgt_decoding(self, seg: Seg) -> None:
        pass
