from pangeamt_nlp.processor.base.normalizer_base import NormalizerBase
from pangeamt_nlp.seg import Seg
from pangeamt_nlp.utils.strip_and_catch_white import strip_and_catch_white


class SpanishSentencesNorm(NormalizerBase):
    NAME = "spanish_sentences_norm"
    DESCRIPTION_TRAINING = """
    """
    DESCRIPTION_DECODING = """
          Replace sentences like "Estados Miembros" by "Estados Miembro"
    """

    class Replacement:
        def __init__(self, desired: str, expected: str):
            self.pairs = {
                expected: desired,
                expected.lower(): desired.lower(),
                expected.upper(): desired.upper(),
                expected.capitalize(): desired.capitalize()
            }

        def replace(self, text: str):
            for key, value in self.pairs.items():
                text = text.replace(key, value)
            return text

    def __init__(self, src_lang: str, tgt_lang: str) -> None:
        super().__init__(src_lang, tgt_lang)
        if self.tgt_lang == "es":
            self.replacements = [
                self.Replacement('Estados Miembro', 'Estados Miembros'),
                self.Replacement('Estados miembro', 'Estados miembros'),
                self.Replacement('por esta razón', 'por este motivo'),
                self.Replacement('por esta razón', 'por ello'),
            ]

    def apply_replacements(self, text: str):
        for replacement in self.replacements:
            text = replacement.replace(text)
            if text.startswith("o "):
                text = "u "+text[len("o "):]
            if text.startswith("O "):
                text = "U "+text[len("O "):]
            if "o" in text.split(" "):
                    text = text.replace(' o o', ' u o')
        return text

    def process_train(self, seg: Seg) -> None:
        pass

    def process_src_decoding(self, seg: Seg) -> None:
        pass

    def process_tgt_decoding(self, seg: Seg) -> None:
        if self.tgt_lang == "es":
            seg.tgt = self.apply_replacements(seg.tgt)
