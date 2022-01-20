from pangeamt_nlp.processor.base.validator_base import ValidatorBase
from pangeamt_nlp.seg import Seg


class NonContainsCjkCharsVal(ValidatorBase):
    NAME = "non_contains_cjk_chars_val"

    DESCRIPTION_TRAINING = """
                Filter segments with japanese characters 
            """

    DESCRIPTION_DECODING = """
                Validators do not apply to decoding.
            """

    RANGES = [
        {"from": ord(u"\u3300"), "to": ord(u"\u33ff")},  # compatibility ideographs
        {"from": ord(u"\ufe30"), "to": ord(u"\ufe4f")},  # compatibility ideographs
        {"from": ord(u"\uf900"), "to": ord(u"\ufaff")},  # compatibility ideographs
        {"from": ord(u"\U0002F800"), "to": ord(u"\U0002fa1f")},  # compatibility ideographs
        {'from': ord(u'\u3040'), 'to': ord(u'\u309f')},  # Japanese Hiragana
        {"from": ord(u"\u30a0"), "to": ord(u"\u30ff")},  # Japanese Katakana
        {"from": ord(u"\u2e80"), "to": ord(u"\u2eff")},  # cjk radicals supplement
        {"from": ord(u"\u4e00"), "to": ord(u"\u9fff")},
        {"from": ord(u"\u3400"), "to": ord(u"\u4dbf")},
        {"from": ord(u"\U00020000"), "to": ord(u"\U0002a6df")},
        {"from": ord(u"\U0002a700"), "to": ord(u"\U0002b73f")},
        {"from": ord(u"\U0002b740"), "to": ord(u"\U0002b81f")},
        {"from": ord(u"\U0002b820"), "to": ord(u"\U0002ceaf")}  # included as of Unicode 8.0
    ]

    def __init__(self, src_lang: str, tgt_lang: str, length_factor=3) -> None:
        super().__init__(src_lang, tgt_lang)

    def is_cjk(self, char):
        return any([range["from"] <= ord(char) <= range["to"] for range in self.RANGES])

    def validate(self, seg: Seg) -> bool:
        cjk_langs = ["zh", "tw", "ja", "ko"]
        check_line = ''
        if self.src_lang not in cjk_langs:
            check_line = seg.src
        if self.tgt_lang not in cjk_langs:
            check_line = seg.tgt
        for char in check_line:
            if self.is_cjk(char):
                return False
        return True
