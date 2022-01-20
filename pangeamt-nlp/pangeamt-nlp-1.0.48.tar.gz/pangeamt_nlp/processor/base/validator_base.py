from pangeamt_nlp.processor.base.processor_base import ProcessorBase
from pangeamt_nlp.seg import Seg


class ValidatorBase(ProcessorBase):
    def __init__(self, src_lang, tgt_lang):
        super().__init__(ProcessorBase.TYPE_VALIDATOR, src_lang, tgt_lang)

    def validate(self, seg: Seg) -> bool:
        cls = self.__class__
        raise ValueError(f'validate method is missing in {cls}')
