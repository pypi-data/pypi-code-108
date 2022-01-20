from pangeamt_nlp.processor.base.normalizer_base import NormalizerBase
from pangeamt_nlp.seg import Seg


class ConvertEmptyLines(NormalizerBase):
    NAME = "convert_empty_lines_postprocess"

    DESCRIPTION_TRAINING = """"""

    DESCRIPTION_DECODING = """
        Convert an empty line from src to an empty line in decoding
    """

    def __init__(self, src_lang: str, tgt_lang: str) -> None:
        super().__init__(src_lang, tgt_lang)

    def process_train(self, seg: Seg) -> None:
        pass

    def process_src_decoding(self, seg: Seg) -> None:
        pass

    def process_tgt_decoding(self, seg: Seg) -> None:
        if seg.src_raw == "\n" or seg.src_raw.isspace() or seg.src_raw == "":
            seg.tgt = ""