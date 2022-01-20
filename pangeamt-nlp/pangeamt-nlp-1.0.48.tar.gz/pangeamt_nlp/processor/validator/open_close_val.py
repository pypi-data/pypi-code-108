from pangeamt_nlp.processor.base.validator_base import ValidatorBase
from pangeamt_nlp.seg import Seg


class OpenCloseVal(ValidatorBase):
    NAME = "open_close_val"

    DESCRIPTION_TRAINING = """
            Remove a trans-unit if an opening char like [ or { or " has not a corresponding closing char
        """

    DESCRIPTION_DECODING = """
            Validators do not apply to decoding.
        """

    def __init__(self, src_lang: str, tgt_lang: str) -> None:
        super().__init__(src_lang, tgt_lang)
        self._open_close = [
            ('"', '"'),
            ('[', ']'),
            ('{', '}')
        ]
        self._open_close_oriental = [
            ('"', '"'),
            ('〈','〉'),
            ('《', '》'),
            ('「', '」'),
            ('『', '』' ),
            ('【', '】'),
            ('〔', '〕'),
            ('〖', '〗'),
            ('〘', '〙'),
            ('〚', '〛'),
            ('﹁', '﹂'),
            ('"', '"'),
            (' (', ')'),
            ('(', ')')
        ]


    def validate(self, seg: Seg) -> bool:
            # if self.src_lang == 'zh':
            #

            for open_char, close_char in self._open_close:
                if (open_char == close_char) and ((seg.src.count(open_char) & 1) == 1 or (seg.tgt.count(open_char) & 1) == 1):  # odd
                    return False
                else:
                    if (seg.src.count(open_char) != seg.src.count(close_char)) or seg.tgt.count(open_char) != seg.tgt.count(close_char):
                        return False
            return True

