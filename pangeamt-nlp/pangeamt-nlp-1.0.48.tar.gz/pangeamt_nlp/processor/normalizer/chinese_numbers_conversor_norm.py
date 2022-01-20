from pangeamt_nlp.processor.base.normalizer_base import NormalizerBase
from pangeamt_nlp.seg import Seg, SegCase

import re as _re
from pycnnum import cn2num as _cn2num

class ChineseNumbersConversorNorm(NormalizerBase):
    NAME = "chinese_numbers_conversor_norm"

    DESCRIPTION_TRAINING = """"""

    DESCRIPTION_DECODING = """
        Converse chinese number to arabic numbers
    """

    def __init__(self, src_lang: str, tgt_lang: str) -> None:
        super().__init__(src_lang, tgt_lang)

    def _get_numbers(self, text):
        return set(_re.findall(r'[十百千万亿一二三四五六七八九]+', text))

    def cn2ar(self, text):
        for seq in self._get_numbers(text):
            if len(seq) > 2:
                text = text.replace(
                    seq, str(_cn2num(seq, numbering_type="mid"))
                )
        return text

    def process_train(self, seg: Seg) -> None:
        pass

    def process_src_decoding(self, seg: Seg) -> None:
        seg.src = self.cn2ar(seg.src)

    def process_tgt_decoding(self, seg: Seg) -> None:
        seg.tgt = self.cn2ar(seg.tgt)