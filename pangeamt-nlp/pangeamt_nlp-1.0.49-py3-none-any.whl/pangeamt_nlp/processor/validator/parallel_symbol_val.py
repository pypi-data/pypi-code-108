from pangeamt_nlp.processor.base.validator_base import ValidatorBase
from pangeamt_nlp.seg import Seg


class ParallelSymbolVal(ValidatorBase):
    NAME = "parallel_symbol_val"

    DESCRIPTION_TRAINING = """
            Remove a trans-unit if in source or target there is different number of symbols
        """

    DESCRIPTION_DECODING = """
            Validators do not apply to decoding.
        """

    def __init__(self, src_lang: str, tgt_lang: str) -> None:
        super().__init__(src_lang, tgt_lang)
        self._chars = {
            ':',
            ';',
            '#',
            '%',
            '[',
            ']',
            # '(',
            # ')',
            '{',
            '}',
            '<',
            '>'
        }

    def validate(self, seg: Seg) -> bool:
        for char in self._chars:
            if (char == '#' or char== ':' or char== ';') and (self.src_lang == 'en' or self.tgt_lang == 'en'):
                    continue

            if seg.src.count(char) != seg.tgt.count(char):
                return False
        return True
