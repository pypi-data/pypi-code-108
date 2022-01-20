from pangeamt_nlp.processor.base.validator_base import ValidatorBase
from pangeamt_nlp.tokenizer.mecab_tokenizer import MecabTokenizer
from pangeamt_nlp.seg import Seg
import re


class LengthFactorVal(ValidatorBase):
    NAME = "length_factor_val"

    DESCRIPTION_TRAINING = """
            Remove pair if length factor is high between src and tgt
            Parameters: length_factor(int) by default 3
        """

    DESCRIPTION_DECODING = """
            Validators do not apply to decoding.
        """

    def __init__(self, src_lang: str, tgt_lang: str, length_factor=3) -> None:
        super().__init__(src_lang, tgt_lang)
        self._length_factor = float(length_factor)
        self._mecab_tokenizer = MecabTokenizer("ja")

    def validate(self, seg: Seg) -> bool:
        if self.src_lang == "ja" or self.tgt_lang == "ja":
            if self.src_lang == "ja":
                sentence_src = self._mecab_tokenizer.tokenize(seg.src).split()
                sentence_tgt = re.findall(r"\w+|[^\w\s]", seg.tgt, re.UNICODE)
            else:
                sentence_src = re.findall(r"\w+|[^\w\s]", seg.src, re.UNICODE)
                sentence_tgt = self._mecab_tokenizer.tokenize(seg.tgt).split()
            if len(sentence_src) > len(sentence_tgt) * self._length_factor or \
                    len(sentence_tgt) > len(sentence_src) * self._length_factor:
                    return False

        elif len(seg.src) > len(seg.tgt) * self._length_factor or len(seg.tgt) > len(seg.src) * self._length_factor:
            return False
        return True
