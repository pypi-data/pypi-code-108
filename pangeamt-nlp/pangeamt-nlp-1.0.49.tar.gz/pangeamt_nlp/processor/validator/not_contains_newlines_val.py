from pangeamt_nlp.processor.base.validator_base import ValidatorBase
from pangeamt_nlp.seg import Seg


class NotContainsNewLinesVal(ValidatorBase):
    NAME = "not_contains_new_lines_val"

    DESCRIPTION_TRAINING = """
            Filter pairs with newlines
        """

    DESCRIPTION_DECODING = """
            Validators do not apply to decoding.
        """

    def __init__(self, src_lang: str, tgt_lang: str) -> None:
        super().__init__(src_lang, tgt_lang)


    def validate(self, seg: Seg) -> bool:
        if '\n' in seg.src or '\n' in seg.tgt:
            return False
        return True
