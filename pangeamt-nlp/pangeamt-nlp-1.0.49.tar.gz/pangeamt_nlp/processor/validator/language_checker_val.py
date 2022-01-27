from pangeamt_nlp.processor.base.validator_base import ValidatorBase
from pangeamt_nlp.utils.lang_detector import LangDetector
from pangeamt_nlp.seg import Seg


class LanguageCheckerVal(ValidatorBase):
    NAME = "language_checker_val"

    DESCRIPTION_TRAINING = """
        Remove pair of sentence if the language does not match with src_lang and tgt_lang
    """

    DESCRIPTION_DECODING = """
        Validators do not apply to decoding.
    """

    def __init__(self, src_lang: str, tgt_lang: str, only_english=False) -> None:
        super().__init__(src_lang, tgt_lang)
        self.only_english = only_english

    def validate(self, seg: Seg, ) -> bool:
        if self.only_english and (self.src_lang == 'en' or self.tgt_lang == 'en'):
            text = seg.src
            if self.tgt_lang == 'en':
                text = seg.tgt

            if len(text) > 5:
                lang_detector = LangDetector()
                src_detection = lang_detector.detect(text=text)
                # print(src_detection)
                if src_detection != 'en':
                    return False

            return True
        elif len(seg.src.split(' ')) > 5:
            lang_detector = LangDetector()
            src_detection = lang_detector.detect(text=seg.src)
            tgt_detection = lang_detector.detect(text=seg.tgt)
            if src_detection != self.src_lang or tgt_detection != self.tgt_lang:
                return False

        return True


