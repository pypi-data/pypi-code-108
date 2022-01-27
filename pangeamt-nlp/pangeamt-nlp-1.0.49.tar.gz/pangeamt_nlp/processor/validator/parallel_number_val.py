from pangeamt_nlp.processor.base.validator_base import ValidatorBase
from pangeamt_nlp.seg import Seg


class ParallelNumberVal(ValidatorBase):
    NAME = "parallel_number_val"

    DESCRIPTION_TRAINING = """
            Remove a trans-unit if in source or target there is different number of chars that are in here self._chars
        """

    DESCRIPTION_DECODING = """
            Validators do not apply to decoding.
        """

    def __init__(self, src_lang: str, tgt_lang: str) -> None:
        super().__init__(src_lang, tgt_lang)

    def validate(self, seg: Seg) -> bool:
        for number in range(10):
            if seg.src.count(str(number)) != seg.tgt.count(str(number)):
                return False
        return True
