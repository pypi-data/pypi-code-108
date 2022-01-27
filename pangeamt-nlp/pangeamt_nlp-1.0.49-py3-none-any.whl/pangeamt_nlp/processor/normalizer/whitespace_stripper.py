from pangeamt_nlp.processor.base.normalizer_base import NormalizerBase
from pangeamt_nlp.seg import Seg
from pangeamt_nlp.utils.strip_and_catch_white import strip_and_catch_white


class WhitespaceStripperNormalizer(NormalizerBase):
    NAME = "white_space_stripper"
    DESCRIPTION_TRAINING = """
        Strip white spaces on source and target
    """
    DESCRIPTION_DECODING = """
         Strip white spaces on source and restore them on target
    """

    def __init__(self, src_lang: str, tgt_lang: str) -> None:
        super().__init__(src_lang, tgt_lang)

    def process_train(self, seg: Seg) -> None:
        seg.src = seg.src.strip()
        seg.tgt = seg.tgt.strip()

    def process_src_decoding(self, seg: Seg) -> None:
        text, white_left, white_right = strip_and_catch_white(seg.src)
        seg.src = text
        seg.white_left = white_left
        seg.white_right = white_right

    def process_tgt_decoding(self, seg: Seg) -> None:
        seg.tgt = seg.white_left + seg.tgt + seg.white_right
