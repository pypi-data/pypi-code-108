import sys

from pangeamt_nlp.processor.base.normalizer_base import NormalizerBase
from pangeamt_nlp.processor.normalizer.quote_norm import QuotesInfo
from pangeamt_nlp.seg import Seg
import unicodedata


# Source for rules followed
from pangeamt_nlp.utils.get_all_whitespaces import get_unicode_space_characters


class FrenchPunctuationSpacerNorm(NormalizerBase):
    """To be applied after quotation character normalisation
    Adds a non-breaking space before each "?" , "!", ":" and ";" when used as punctuation (for example, not in URL)
    Adds a normal space before the opening bracket ( and the standard quotation marks as defined in
    quotenormalizer.QuotesInfo
    """

    NAME = "french_punctuation_spacer_norm"

    DESCRIPTION_TRAINING = """
        Applies the french punctuation spacer to src or tgt, checking
        with the src_lang and tgt_lang to decide where to apply it.        
    """
    DESCRIPTION_DECODING = """
        Apply the french punctuation spacer to src or tgt, checking
        with the src_lang and tgt_lang to decide where to apply it
    """

    def __init__(self, src_lang: str, tgt_lang: str, canadian=False):
        # Source:  http://grammaire.reverso.net/5_1_10_les_espaces_et_la_ponctuation.shtml
        # Addition (from Cath): before the ending quotes and after the opening quotes: non-breaking space
        super().__init__(src_lang, tgt_lang)
        self.nb_space = "\u00A0"  # non-breaking space
        self.all_spaces = get_unicode_space_characters()
        self.canadian = canadian
        if canadian:
            self.punct_with_pre_np_space = [":"]
        else:
            self.punct_with_pre_np_space = ["?", "!", ":", ";"]
        self.punct_with_pre_np_space.extend(QuotesInfo.get_standard_close_quotes_for_language("fr"))

        self.punct_with_pre_space = QuotesInfo.get_standard_open_quotes_for_language("fr")
        self.punct_with_pre_space.append("(")

        self.punct_with_post_space = QuotesInfo.get_standard_close_quotes_for_language("fr")
        self.punct_with_post_space.append(")")
        # To avoid adding spaces before a , or a . (which is a stronger rule than )
        self.exceptions_to_punct_with_post_space = [".",","]

        self.punct_with_post_np_space = QuotesInfo.get_standard_open_quotes_for_language("fr")

        # To avoid detecting URLS and other oddities
        #   Assumption: the punctuation in the source is not terrible (no things like "I'm cool.And you?Me too."
        if canadian:
            self.punct_with_obligatory_space_in_original = [":"]
        else:
            self.punct_with_obligatory_space_in_original = ["?", "!", ":", ";"]

    def _normalize(self, text):

        res = []
        i = 0
        while i < len(text):
            # Do not change the flagged punctuation if it has no spaces at all around it
            #   except if there is a quote behind
            #   ("Il dit 'fin!'" -> "il dit 'fin !'", but with correct quotes and space)
            #   (http://google.be remains as is)
            if text[i] not in self.punct_with_obligatory_space_in_original \
                    or i == 0 \
                    or i == len(text) - 1 \
                    or text[i-1].isspace() \
                    or text[i+1].isspace() \
                    or text[i+1] in QuotesInfo.get_standard_close_quotes_for_language("fr"):
                if text[i] in self.punct_with_pre_np_space:
                    if len(res) > 0 and res[-1] in self.all_spaces:  # space found
                        res[-1] = self.nb_space
                    elif len(res) > 0:  # no pre space if first char
                        res.append(self.nb_space)
                elif text[i] in self.punct_with_pre_space:
                    if len(res) > 0 and res[-1] in self.all_spaces:  # space found
                        pass # Special spaces get preference on normal spaces
                    elif len(res) > 0:  # no pre space if first char
                        res.append(" ")
                res.append(text[i])
                if text[i] in self.punct_with_post_space and i != len(text)-1:  # No space for last char:
                    if i<len(text)-1 and text[i+1] in self.exceptions_to_punct_with_post_space:
                        pass # Potentially add here logic to remove a space between a comma and a quote
                    else:
                        res.append(" ")
                        if i < len(text) - 1 and text[i + 1] in self.all_spaces:  # space found
                            i += 1  # Skip the space character
                elif text[i] in self.punct_with_post_np_space and i != len(text)-1:  # No space for last char
                    res.append(self.nb_space)
                    if i < len(text) - 1 and text[i + 1] in self.all_spaces:  # space found
                        i += 1  # Skip the space character
            else:
                res.append(text[i])
            i += 1

        return "".join(res)

    # Called when training
    def process_train(self, seg: Seg, canadian=False) -> None:
        if self.get_src_lang() == "fr" and not canadian:
            seg.src = self._normalize(seg.src)
        if seg.tgt is not None and self.get_tgt_lang() == "fr":
            seg.tgt = self._normalize(seg.tgt)

    # Called when using model (before calling model to translate)
    def process_src_decoding(self, seg: Seg, canadian=False) -> None:
        if self.get_src_lang() == "fr" and not canadian:
            seg.src = self._normalize(seg.src)

    # Normalizing for decoding for special French spaces
    def process_tgt_decoding(self, seg: Seg) -> None:
        if self.get_tgt_lang() == "fr":
            seg.tgt = self._normalize(seg.tgt)

        if self.canadian:
            seg.tgt = seg.tgt.replace(' ?', '?').replace(' !', '!').replace(' ;', ';').replace("informations", "renseignements").replace("téléphone portable", "celullaire").replace("smartphone", "téléphone intelligent")


