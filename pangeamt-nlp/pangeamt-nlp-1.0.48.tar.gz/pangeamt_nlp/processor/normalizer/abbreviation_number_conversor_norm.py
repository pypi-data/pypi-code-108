from pangeamt_nlp.processor.base.normalizer_base import NormalizerBase
from pangeamt_nlp.seg import Seg


class AbbreviationNumberConversor(NormalizerBase):
    NAME = "abbreviation_number_conversor_norm"
    DESCRIPTION_TRAINING = """
    """
    DESCRIPTION_DECODING = """
          Replace number abbrevations between english, french and spanish.
    """

    class Replacement:
        def __init__(self, desired: str, expected: str):
            self.pairs = {
                expected: desired,
                expected.capitalize(): desired.capitalize()
            }

        def replace(self, text: str):
            for key, value in self.pairs.items():
                text = text.replace(key, value)
            return text

    def __init__(self, src_lang: str, tgt_lang: str) -> None:
        super().__init__(src_lang, tgt_lang)
        self.replacements = []
        if self.tgt_lang == 'fr':
            self.replacements = [
                self.Replacement('nº', 'n.º' ),
                self.Replacement('nº', 'no.', ),
                self.Replacement('nº', 'n.', )
            ]

        if self.tgt_lang == 'es':
            self.replacements = [
                self.Replacement('n.º', 'nº', ),
                self.Replacement('n.º', 'no.', ),
                self.Replacement('n.º', 'n.', )
            ]

        if self.tgt_lang == 'en':
            self.replacements = [
                self.Replacement('no.', 'nº', ),
                self.Replacement('no.', 'n.º', ),
                self.Replacement('no.', 'n.', )
            ]

        if self.tgt_lang == 'it':
            self.replacements = [
                self.Replacement('n.', 'nº', ),
                self.Replacement('n.', 'n.º', ),
                self.Replacement('n.', 'no.', )
            ]


    def apply_replacements(self, text: str):
        for replacement in self.replacements:
            text = replacement.replace(text)
        return text

    def process_train(self, seg: Seg) -> None:
        if seg.tgt is not None and seg.tgt != "" and seg.tgt != '\n':
            line = seg.tgt.strip().split(' ')
            for replacement in self.replacements:
                for key, value in replacement.pairs.items():
                    if key in line:
                        i = line.index(key)
                        if (i < len(line) - 1 and line[i + 1][0].isnumeric()) or line[i - 1][0].isnumeric():
                            seg.tgt = replacement.replace(seg.tgt)


    def process_src_decoding(self, seg: Seg) -> None:
        pass

    def process_tgt_decoding(self, seg: Seg) -> None:
        line = seg.tgt.strip().split(' ')
        for replacement in self.replacements:
            for key, value in replacement.pairs.items():
                if key in line:
                    i = line.index(key)
                    if  (i < len(line) -1 and line[i + 1][0].isnumeric()) or line[i - 1][0].isnumeric():
                        seg.tgt = replacement.replace(seg.tgt)
