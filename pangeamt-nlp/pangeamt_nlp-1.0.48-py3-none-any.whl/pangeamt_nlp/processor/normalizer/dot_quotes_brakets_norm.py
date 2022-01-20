from pangeamt_nlp.processor.base.normalizer_base import NormalizerBase
from pangeamt_nlp.seg import Seg


class DotQuotesBraketsNorm(NormalizerBase):
    NAME = "dot_quotes_brakets_norm"

    DESCRIPTION_TRAINING = """Put punctuation marks outside/inside the quotes/brakets, 
                              (when these punctuation marks go just at the end of the sentence),
                              depending on the language norm.
                              
                              INSIDE -> French, English, German  "Hello world". -> "Hello world."
                              OUTSIDE -> Spanish, Arab  "Hola mundo." -> "Hola mundo".
                                                                                         """

    DESCRIPTION_DECODING = """"""

    PUNCTUATION = ["."]
    SYMBOLS = [")", '"', '“', "’", "”", "»", "«"]

    LANGUAGES_OUTSIDE = ["es", "ar", "pl"]
    LANGUAGES_INSIDE = ["fr", "en", "de"]


    def __init__(self, src_lang: str, tgt_lang: str):
        super().__init__(src_lang, tgt_lang)

    def _put_the_dot_outside(self, text: str):
        res_text = []
        i = 0
        if len(text) <= 1:
            return text
        else:
            while i < len(text) - 1:
                if text[i] in self.PUNCTUATION and text[i + 1] in self.SYMBOLS:
                    res_text.append(text[i + 1])
                    res_text.append(text[i])
                    i += 2
                else:
                    res_text.append(text[i])
                    i += 1
                    if i == len(text) - 1:
                        res_text.append(text[i])
        return "".join(res_text)

    def _put_the_dot_inside(self, text: str):
        res_text = []
        i = 0
        if len(text) <= 1:
            return text
        else:
            while i < len(text) - 1:
                if text[i] in self.SYMBOLS and text[i + 1] in self.PUNCTUATION:
                    res_text.append(text[i + 1])
                    res_text.append(text[i])
                    i += 2
                else:
                    res_text.append(text[i])
                    i += 1
                    if i == len(text) - 1:
                        res_text.append(text[i])
        return "".join(res_text)

    def _normalize(self, text, language_code):
        if language_code in self.LANGUAGES_OUTSIDE:
            return self._put_the_dot_outside(text)
        elif language_code in self.LANGUAGES_INSIDE:
            return self._put_the_dot_inside(text)
        else:
            return text

    # Called when training
    def process_train(self, seg: Seg) -> None:
        seg.src = self._normalize(seg.src, self.src_lang)
        seg.tgt = self._normalize(seg.tgt, self.tgt_lang)

    # Called when using model (before calling model to translate)
    def process_src_decoding(self, seg: Seg) -> None:
        seg.src = self._normalize(seg.src, self.src_lang)

    # Called after the model translated (in case this would be necessary; usually not the case)
    def process_tgt_decoding(self, seg: Seg) -> None:
        seg.tgt = self._normalize(seg.tgt, self.tgt_lang)
