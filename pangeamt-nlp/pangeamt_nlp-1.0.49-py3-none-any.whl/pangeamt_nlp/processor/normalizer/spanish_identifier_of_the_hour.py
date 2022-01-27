from pangeamt_nlp.processor.base.normalizer_base import NormalizerBase
from pangeamt_nlp.seg import Seg
import re

class SpanishIdentifierOfTheHour(NormalizerBase):
    DESCRIPTION_TRAINING = """
                Normalizes the identifier of the hour in Spanish.
                
                The correct way is: a.[inseparable space]m. or p.[inseparable space]m. (No capital letters)
            """

    DESCRIPTION_DECODING = """
                
            """

    NAME = "spanish_identifier_of_the_hour"

    def __init__(self, src_lang: str, tgt_lang: str):
        super().__init__(src_lang, tgt_lang)

    def _normalize(self, text):
        res_text = []
        iterator = re.finditer(r'[apAP][\.\s]{0,2}[mM]\.?', text)
        for match in iterator:
            identifier_of_the_hour = match.group(0)
            inicial_index = text.index((identifier_of_the_hour))
            final_index = text.index(identifier_of_the_hour) + len(identifier_of_the_hour)
            is_am = ("a" == identifier_of_the_hour[0] or "A" == identifier_of_the_hour[0])
            if re.match(r'\s', text[inicial_index - 1]):
                if is_am:
                    part_of_the_res_text = re.sub(r'[aA][\.\s]{0,2}[mM]\.?', "a.\u00A0m.", text[:final_index])
                else:
                    part_of_the_res_text = re.sub(r'[pP][\.\s]{0,2}[mM]\.?', "p.\u00A0m.", text[:final_index])
                res_text.append(part_of_the_res_text)
                text = text[final_index:]
        res_text.append(text)
        return "".join(res_text)

    # Called when training
    def process_train(self, seg: Seg) -> None:
        if self.get_src_lang() == "es":
            seg.src = self._normalize(seg.src)
        if seg.tgt is not None and self.get_tgt_lang() == "es":
            seg.tgt = self._normalize(seg.tgt)

    # Called when using model (before calling model to translate)
    def process_src_decoding(self, seg: Seg) -> None:
        if self.get_src_lang() == "es":
            seg.src = self._normalize(seg.src)

    # Called after the model translated (in case this would be necessary; usually not the case)
    def process_tgt_decoding(self, seg: Seg) -> None:
        if self.get_tgt_lang() == "es":
            seg.tgt = self._normalize(seg.tgt)


