from pangeamt_nlp.processor.base.validator_base import ValidatorBase
from pangeamt_nlp.seg import Seg

class NotEmptyVal(ValidatorBase):
    NAME = "not_empty_val"

    DESCRIPTION_TRAINING = """
            Filter empty sentences
        """

    DESCRIPTION_DECODING = """
            Validators do not apply to decoding.
        """

    def __init__(self, src_lang: str, tgt_lang: str) -> None:
        super().__init__(src_lang, tgt_lang)


    def validate(self, seg: Seg) -> bool:
        if seg.src == '' or seg.tgt == '':
            return False
        return True
