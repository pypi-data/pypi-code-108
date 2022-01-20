from regex import regex

from pangeamt_nlp.processor.base.normalizer_base import NormalizerBase
from pangeamt_nlp.seg import Seg


class DeleteRepeatedPunctNorm(NormalizerBase):

    NAME = "delete_repeated_punct_norm"

    DESCRIPTION_TRAINING = """
        Deletes repeated : and ;, as well as when it is interwoven with .
        For example "Hi;.;" becomes "Hi;"
    """

    DESCRIPTION_DECODING = """
        Deletes repeated : and ;, as well as when it is interwoven with .
        For example "Hi;.;" becomes "Hi;
        Note that this postprocess is especially relevant during decoding, because it corrects typical MT mistakes"
    """

    PUNCT_SYMBOLS = [r";", r":"]

    def _normalize(self, text):
        res_seg = text

        # 1) remove repetitions
        for symbol in self.PUNCT_SYMBOLS:
            r1 = symbol + r"+"
            r1_res = symbol
            res_seg = regex.sub(r1, r1_res, res_seg)

        # 2) remove situations as ".;"
        for symbol in self.PUNCT_SYMBOLS:
            r1 = r"\.*" + symbol + "\.*"
            r1_res = symbol
            res_seg = regex.sub(r1, r1_res, res_seg)

        # 3) removing repetitions (new ones can be created due to previous step)
        for symbol in self.PUNCT_SYMBOLS:
            r1 = symbol + r"+"
            r1_res = symbol
            res_seg = regex.sub(r1, r1_res, res_seg)
        return res_seg

    # Called when training
    def process_train(self, seg: Seg) -> None:
        seg.src = self._normalize(seg.src)
        if seg.tgt is not None:
            seg.tgt = self._normalize(seg.tgt)

    # Called when using model (before calling model to translate)
    def process_src_decoding(self, seg: Seg) -> None:
        seg.src = self._normalize(seg.src)

    # Called when using model (before calling model to translate)
    def process_tgt_decoding(self, seg: Seg) -> None:
        seg.tgt = self._normalize(seg.tgt)

