from pangeamt_nlp.processor.base.validator_base import ValidatorBase
from pangeamt_nlp.seg import Seg
import re


class NoLinesWithOnlyUrlVal(ValidatorBase):
    NAME = "no_lines_with_only_url_val"

    DESCRIPTION_TRAINING = """
            Filter pairs with only url
        """

    DESCRIPTION_DECODING = """
            Validators do not apply to decoding.
        """

    def __init__(self, src_lang: str, tgt_lang: str) -> None:
        super().__init__(src_lang, tgt_lang)

    def validate(self, seg: Seg) -> bool:
        urls = re.findall('http[s]?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', seg.src)

        if len(urls) > 0:
            for token in seg.src.split(" "):
                if token not in urls:
                    return True
            return False
        return True
