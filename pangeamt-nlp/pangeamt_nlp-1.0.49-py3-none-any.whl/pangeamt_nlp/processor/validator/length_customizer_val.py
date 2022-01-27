from pangeamt_nlp.processor.base.validator_base import ValidatorBase
from pangeamt_nlp.seg import Seg


class LengthCustomizerVal(ValidatorBase):
    NAME = "length_customizer_val"

    DESCRIPTION_TRAINING = """
        Remove pair of sentences with less than a minimum and more than a maximum length \n
        parameters: minimum(int) by default 0, maximum(int) by default 200
    """

    DESCRIPTION_DECODING = """
        Validators do not apply to decoding.
    """

    def __init__(self, src_lang: str, tgt_lang: str, minimum = 0, maximum = 200) -> None:
        super().__init__(src_lang, tgt_lang)
        self._min = int(minimum)
        self._max = int(maximum)

    def validate(self, seg: Seg) -> bool:
        if len(seg.tgt.split(" ")) > self._max  or len(seg.tgt.split(" ")) < self._min:
            return False
        return True


