from pangeamt_nlp.processor.base.normalizer_base import NormalizerBase
from pangeamt_nlp.seg import Seg


class EllipsisNorm(NormalizerBase):

    NAME = "ellipsis_norm"

    DESCRIPTION_TRAINING = """
        Replaces all sequences of three dots (...) with the ellipsis sign (\u2026), if it occurs alone 
        (so it will not normalise "...." or "......")
    """

    DESCRIPTION_DECODING = """
        Replaces all sequences of three dots (...) with the ellipsis sign (\u2026), if it occurs alone 
        (so it will not normalise "...." or "......")
    """

    def __init__(self, src_lang, tgt_lang):
        super().__init__(src_lang, tgt_lang)
        self.in_chars = "..."
        self.out_char = "\u2026" # …

    def _normalize(self, text):
        res_text = []
        i = 0
        while i < len(text)-2:
            if text[i:i+3] == self.in_chars:
                if i == 0 or text[i-1] != ".":
                    if i == len(text)-3 or text[i+3] != ".":
                        res_text.append(self.out_char)
                        i += 3
                        continue
            res_text.append(text[i])
            i += 1
        res_text.append(text[i:len(text)])
        return "".join(res_text)

    # Called when training
    def process_train(self, seg: Seg) -> None:
        seg.src = self._normalize(seg.src)
        if seg.tgt is not None:
            seg.tgt = self._normalize(seg.tgt)

    # Called when using model (before calling model to translate)
    def process_src_decoding(self, seg: Seg) -> None:
        seg.src = self._normalize(seg.src)

    # Called after the model translated (in case this would be necessary; usually not the case)
    def process_tgt_decoding(self, seg: Seg) -> None:
        pass
