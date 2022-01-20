from pangeamt_nlp.processor.base.normalizer_base import NormalizerBase
from pangeamt_nlp.seg import Seg


class DoubleQuoteNormalizer(NormalizerBase):

    NAME = "double_quote_normalizer"

    DESCRIPTION_TRAINING = """
        Replace double quotes, «» and “”, with "", both in src and tgt.
    """

    DESCRIPTION_DECODING = """
        Replace double quotes, «» and “”, with "", only applies to src.
    """

    def __init__(self, src_lang: str, tgt_lang: str) -> None:

        super().__init__(src_lang, tgt_lang)
        self._replaces = {
            "«": '"',
            "»": '"',
            "„": '"',
            "“": '"',
            "”": '"',
        }

    def normalize(self, txt: str) -> str:
        """ Normalize double quotes

        Parameters:
        txt (str): String to normalize

        Returns:
        str: Returns the string normalized

        """
        for search, replace in self._replaces.items():
            txt = txt.replace(search, replace)
        return txt

    def process_train(self, seg: Seg) -> None:
        seg.src = self.normalize(seg.src)
        seg.tgt = self.normalize(seg.tgt)

    def process_src_decoding(self, seg: Seg) -> None:
        seg.src = self.normalize(seg.src)

    def process_tgt_decoding(self, seg: Seg) -> None:
        pass
