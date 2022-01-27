from pangeamt_nlp.processor.base.processor_base import ProcessorBase
from pangeamt_nlp.seg import Seg


class NormalizerBase(ProcessorBase):
    def __init__(self, src_lang: str, tgt_lang: str):
        super().__init__(ProcessorBase.TYPE_TRANSFORMER, src_lang, tgt_lang)

    def process_train(self, seg: Seg) -> None:
        cls = self.__class__
        raise ValueError(
            f'"{cls}" should implement a "process_src_train" method'
        )

    def process_src_decoding(self, seg: Seg) -> None:
        cls = self.__class__
        raise ValueError(
            f'"{cls}" should implement a "process_src_decoding" method'
        )

    def process_tgt_decoding(self, seg: Seg) -> None:
        cls = self.__class__
        raise ValueError(
            f'"{cls}" should implement a "process_tgt_decoding" method'
        )
