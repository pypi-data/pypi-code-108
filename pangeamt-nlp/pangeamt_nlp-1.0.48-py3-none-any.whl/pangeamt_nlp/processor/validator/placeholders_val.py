from pangeamt_nlp.processor.base.validator_base import ValidatorBase
from pangeamt_nlp.seg import Seg


class PlaceholdersCounterVal(ValidatorBase):
    NAME = "placeholders_counter_val"

    DESCRIPTION_TRAINING = """
            Remove pairs with different number of placeholders
        """

    DESCRIPTION_DECODING = """
            Validators do not apply to decoding.
        """

    def __init__(self, src_lang: str, tgt_lang: str) -> None:
        super().__init__(src_lang, tgt_lang)

    def validate(self, seg: Seg) -> bool:
        if seg.src.count('｟') != seg.tgt.count('｟'):
            return False
        return True
