from pangeamt_nlp.processor.base.validator_base import ValidatorBase
from pangeamt_nlp.seg import Seg


class RepeatedCharsVal(ValidatorBase):
    NAME = "repeated_chars_val"

    DESCRIPTION_TRAINING = """
            Remove pairs with chars repeated more than half the large the sentence
        """

    DESCRIPTION_DECODING = """
            Validators do not apply to decoding.
        """

    def __init__(self, src_lang: str, tgt_lang: str) -> None:
        super().__init__(src_lang, tgt_lang)

    def validate(self, seg: Seg) -> bool:
        if len(seg.src) >= 5 and len(seg.src.split(' ')) >= 3:
            for char in seg.src:
                if not char.isspace() and char:
                    count = seg.src.count(char)
                    if count >= len(seg.src) * 0.5:
                        # print(">>>>><SRC", count, "---",char, src)
                        # time.sleep(4)
                        return False
            for char in seg.tgt:
                if not char.isspace() and char:
                    count = seg.tgt.count(char)
                    if count >= len(seg.tgt) * 0.5:
                        # print(">>>>><TGT", count,"---", char, tgt)
                        # time.sleep(4)
                        return False
        return True
