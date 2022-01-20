from pangeamt_nlp.processor.base.validator_base import ValidatorBase
from pangeamt_nlp.seg import Seg


class EndsWithPunctVal(ValidatorBase):
    NAME = "ends_with_punct_val"

    DESCRIPTION_TRAINING = """
        Checks if src and target lines both end in punctuation (.?!) and that it is the same.
    """

    DESCRIPTION_DECODING = """
        Validators do not apply to decoding.
    """

    def __init__(self, src_lang: str, tgt_lang: str, mode = 'a') -> None:
        super().__init__(src_lang, tgt_lang)
        self.mode = mode
        self.valid_punct = ["?".encode('utf-8'), "!".encode('utf-8'), ".".encode('utf-8'),';'.encode('utf-8'),":".encode('utf-8'), "。".encode('utf-8')]
        self.orietnal_lang = ['ja', 'zh', 'zh_Hans']

    def _is_valid(self, src, tgt):
        if self.mode == 'a':
            if src[-1].encode('utf-8') in self.valid_punct:
                if src[-1].encode('utf-8') == b'\xe3\x80\x82':
                    if tgt[-1].encode('utf-8') == ".".encode('utf-8'):
                        return True

                if self.src_lang in self.orietnal_lang and self.tgt_lang not in self.orietnal_lang:
                    if src[-1].encode('utf-8') == "。".encode('utf-8') and tgt[-1].encode('utf-8') == ".".encode('utf-8'):
                        return True

                if self.tgt_lang in self.orietnal_lang and self.src_lang not in self.orietnal_lang:
                    if tgt[-1].encode('utf-8') == "。".encode('utf-8') and src[-1].encode('utf-8') == ".".encode('utf-8'):
                        return True

                if src[-1].encode('utf-8') == tgt[-1].encode('utf-8'):
                    return True
            return False
        else:
            if src[-1].encode('utf-8') in self.valid_punct:
                if src[-1].encode('utf-8') == b'\xe3\x80\x82':
                    if tgt[-1].encode('utf-8') == ".".encode('utf-8'):
                        return True

                if self.src_lang in self.orietnal_lang and self.tgt_lang not in self.orietnal_lang:
                    if src[-1].encode('utf-8') == "。".encode('utf-8'):
                        if tgt[-1].encode('utf-8') == ".".encode('utf-8'):
                            return True
                        else:
                            return False

                if src[-1].encode('utf-8') == tgt[-1].encode('utf-8'):
                    return True

    def validate(self, seg: Seg) -> bool:
        return self._is_valid(seg.src, seg.tgt)
