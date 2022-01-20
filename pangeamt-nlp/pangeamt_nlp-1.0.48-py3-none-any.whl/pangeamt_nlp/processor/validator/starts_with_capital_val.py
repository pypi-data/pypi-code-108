from pangeamt_nlp.processor.base.validator_base import ValidatorBase
from pangeamt_nlp.seg import Seg


class StartsWithCapitalVal(ValidatorBase):
    NAME = "starts_with_capital_val"

    DESCRIPTION_TRAINING = """
        Checks if src and target lines both start with a capitalised letter.
    """

    DESCRIPTION_DECODING = """
        Validators do not apply to decoding.
    """

    def __init__(self, src_lang: str, tgt_lang: str) -> None:
        super().__init__(src_lang, tgt_lang)

    def _is_valid(self, src, tgt):
        if src[0].islower() or tgt[0].islower():
            return False
        return True

    def validate(self, seg: Seg) -> bool:
        return self._is_valid(seg.src, seg.tgt)
