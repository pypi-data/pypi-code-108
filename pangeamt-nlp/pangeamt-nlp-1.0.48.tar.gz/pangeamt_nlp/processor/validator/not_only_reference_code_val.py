import sys
import unicodedata

from pangeamt_nlp.processor.base.validator_base import ValidatorBase
from pangeamt_nlp.seg import Seg
import regex


class NotOnlyReferenceCodeVal(ValidatorBase):
    NAME = "not_only_reference_code_val"

    DESCRIPTION_TRAINING = """
            Filter segments which consist only of a reference code (genre ABC-125-13-45-65 for example)
            Allows up to 3 lowercased character outside the detected code, and up to 20 uppercased or punctuation
            characters
        """

    DESCRIPTION_DECODING = """
            Validators do not apply to decoding.
        """

    def __init__(self, src_lang: str, tgt_lang: str, max_non_code_lower_case_chars=3, max_non_code_chars=15) -> None:
        super().__init__(src_lang, tgt_lang)
        self.punct_chars = self._get_unicode_punct_characters()
        self.max_non_code_lower_case_chars = max_non_code_lower_case_chars
        self.max_non_code_chars = max_non_code_chars

    @staticmethod
    def get_codes_regex():
        res = r"(\S*\d+([\p{p}/][\dA-Z]+)+)"  # \S: non-white space, \d: digit, \p{p}: punctuation
        return res

    @classmethod
    def _get_unicode_punct_characters(cls):
        """ Returns all unicode characters which are in one of the Punctuation (P) categories """
        puncts = set()
        for i in range(sys.maxunicode + 1):
            if unicodedata.category(chr(i))[0] == 'P':
                puncts.add(chr(i))
        return puncts

    def _is_valid(self, text):

        matches = regex.finditer(self.get_codes_regex(), text)
        total_matched_chars = 0
        non_matched_string = ""
        last_match_end = 0
        for match in matches:
            non_matched_string = non_matched_string + text[last_match_end:match.start()]
            total_matched_chars += len(match.group())
            last_match_end = match.end()
        non_matched_string = non_matched_string + text[last_match_end:]

        if len(non_matched_string) >= self.max_non_code_chars:
            return True
        if total_matched_chars == 0:
            return True
        else:
            puncts = 0
            spaces = 0
            caps = 0
            for char in non_matched_string:
                if char in self.punct_chars:
                    puncts += 1
                if char.isspace():
                    spaces += 1
                if char.isupper():
                    caps += 1
            if len(non_matched_string)-puncts-spaces-caps > self.max_non_code_lower_case_chars:
                return True
        return False

    def validate(self, seg: Seg) -> bool:
        return self._is_valid(seg.src) and self._is_valid(seg.tgt)

