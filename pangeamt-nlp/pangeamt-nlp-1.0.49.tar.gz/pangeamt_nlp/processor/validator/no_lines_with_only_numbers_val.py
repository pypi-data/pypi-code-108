import string

from pangeamt_nlp.processor.base.validator_base import ValidatorBase
from pangeamt_nlp.seg import Seg


class NoLinesWithOnlyNumbersVal(ValidatorBase):
    NAME = "no_lines_with_only_numbers_val"

    DESCRIPTION_TRAINING = """
            Filter paris with only numbers
        """

    DESCRIPTION_DECODING = """
            Validators do not apply to decoding.
        """

    def __init__(self, src_lang: str, tgt_lang: str) -> None:
        super().__init__(src_lang, tgt_lang)
        self.counter = 0

    def validate(self, seg: Seg) -> bool:
        no_numbers = 0
        for char in seg.src:
            if not char.isdigit() and char not in string.punctuation and not char == "–" and not char == " " and not char == "—":
                no_numbers += 1
        # print ("NO NUMS:"+str(no_numbers),src, "\n")
        if no_numbers <= 1:
            self.counter += 1
            return False
        return True
