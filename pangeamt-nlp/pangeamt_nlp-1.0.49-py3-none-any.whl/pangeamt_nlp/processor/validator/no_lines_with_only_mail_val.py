from pangeamt_nlp.processor.base.validator_base import ValidatorBase
from pangeamt_nlp.seg import Seg
import re


class NoLinesWithOnlyMailVal(ValidatorBase):
    NAME = "no_lines_with_only_mail_val"

    DESCRIPTION_TRAINING = """
            Filter pairs with only mail
        """

    DESCRIPTION_DECODING = """
            Validators do not apply to decoding.
        """

    def __init__(self, src_lang: str, tgt_lang: str) -> None:
        super().__init__(src_lang, tgt_lang)


    def validate(self, seg: Seg) -> bool:
        mails = re.findall(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", seg.src)

        if len(mails) > 0:
            only_mail = False
            for token in seg.src.split(" "):
                if token not in mails:
                    return True
            return False
        return True
