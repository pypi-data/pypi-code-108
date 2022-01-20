from pangeamt_nlp.processor.base.validator_base import ValidatorBase
from pangeamt_nlp.seg import Seg, SegCase



class OnlyChineseCharsVal(ValidatorBase):
    NAME = "only_chinese_chars_val"

    DESCRIPTION_TRAINING = """
                Filter segments that have characters different than chinese
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
        self.counter = 0

    def is_cjk(self, char):
        return any([range["from"] <= ord(char) <= range["to"] for range in self.RANGES])

    def validate(self, seg: Seg) -> bool:
        if self.src_lang not in ['zh','tw','ko','ja'] and self.tgt_lang not in ['zh','tw','ko','ja']:
            return True

        check_line = ''
        if self.src_lang in ['zh', 'tw', 'ko', 'ja']:
            check_line = seg.src
        elif self.tgt_lang in ['zh', 'tw', 'ko', 'ja']:
            check_line = seg.tgt

        not_zh = 0
        for char in check_line:
            if not self.is_cjk(char):
                not_zh += 1
                if len(check_line) * 0.5 < not_zh:
                    return False
        return True

