import sys
import unicodedata

from regex import regex

from pangeamt_nlp.processor.base.normalizer_base import NormalizerBase
from pangeamt_nlp.seg import Seg
from pangeamt_nlp.utils.regex_utils import RegexMatcher, SingleWordRegexBuilder


class SpanishDemonstrativePronounsMatcher(RegexMatcher):
    # Source: https://www.spanishdict.com/guia/los-pronombres-demostrativos-en-ingles
    #   (verified by Yaiza for correctness)
    WORDS_TO_MATCH_LOWERCASED = [
        "sólo",

        "ésto",
        "ésta",
        "éstos",
        "éstas",

        "éste",

        "aquél",
        "aquéllo",
        "aquélla",
        "aquéllos",
        "aquéllas",

        "ése",
        "éso",
        "ésa",
        "ésas",
        "ésos",
    ]

    def __init__(self):
        regex_builder = SingleWordRegexBuilder(word_sep_tokens=r"([\p{P}\s])") #All punctuation and white space chars
        regex_builder.add_list_options_as_regex(self.WORDS_TO_MATCH_LOWERCASED)
        tot_regex = regex_builder.build()
        matcher_regex = regex.compile(tot_regex, flags=regex.IGNORECASE)
        super().__init__(matcher_regex)


class SpanishOutdatedAccentsStripperNorm(NormalizerBase):

    NAME = "spanish_outdated_accents_stripper_norm"

    DESCRIPTION_TRAINING = """
        Removes the accents from those words where it is unambiguously known that they should no longer have them
        according to the new (2010) rules for Spanish ortography.
        Is applied to the source or target only if the source or respectively target language is Spanish      
        ASSUMES the accents have been normalised to their NFC form (accented letters = 1 character)  
    """

    DESCRIPTION_DECODING = """
        Removes the accents from those words where it is unambiguously known that they should no longer have them
        according to the new (2010) rules for Spanish ortography.
        Is applied to the source only if the source language is Spanish        
        ASSUMES the accents have been normalised to their NFC form (accented letters = 1 character)  

    """


    def __init__(self, src_lang, tgt_lang):
        super().__init__(src_lang, tgt_lang)
        self.matcher = SpanishDemonstrativePronounsMatcher()

    # Adopted from BERT's tokenization (https://github.com/google-research/bert/blob/master/tokenization.py)
    @staticmethod
    def strip_accents(text, start_index=0, end_index=-1):
        """Strips the accents from the defined substring of the given text.
        Works for text both in unicode NFD and NFC format"""
        if end_index == -1:
            end_index = len(text)
        text_to_consider = text[start_index:end_index]
        # NDF normalisation transforms all characters to their split format (e.g. é becomes two characters: e and the
        #   "add accent to previous character" character (Unicode category "Mn")
        norm_text = unicodedata.normalize("NFD", text_to_consider)
        output = []
        for char in norm_text:
            cat = unicodedata.category(char)
            if cat == "Mn":
                continue
            output.append(char)

        res_text = text[0:start_index] + "".join(output) + text[end_index:]
        return res_text

    def _normalize(self, text):
        """Assumption: the text is in NFC format"""
        matches = self.matcher.match(text)
        res_text = text
        for match in matches:
            res_text = self.strip_accents(res_text, match.start(), match.end())
        return res_text

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
        pass
