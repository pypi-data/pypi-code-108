from pangeamt_nlp.processor.base.normalizer_base import NormalizerBase
from pangeamt_nlp.seg import Seg
import copy

# Note Hans: the code for identifying the numbers (in NumberIdentificationHelpers) is quite complex because
# the characters which guide the search (, . space etc) also structure sentences. Some rather ad-hoc
# decisions were made to have the code return more or less sensible results most of the time. (see unit tests)
# This makes this code hard to maintain/understand (it's not complicated in si, but because many little rules
# are combined it is hard to understand the global picture).
# The general idea of the code is:
#   1) Identify characters which could have the role of decimal separator. It is guaranteed that what comes after this
#       character conforms to a valid number-assuming the character is a decimal separator- (e.g. not accepting as
#       decimal character the , in 1,254654.012), but no guarantees are made on what comes before
#   2) Identify the characters which could have the role of thousands separator and group them if they belong to the
#       same number. It is guaranteed that what comes before this character conforms to a valid number (not accepting
#       the 2 . from 1,5465213.000.254 for example), but no guarantees are made on what comes after (which could be
#       a decimal part)
#   3)  Combine these two lists of potential characters to create the final list of numbers
#   Note: there can be ambiguity(100,500 can be 100,5 or 100500). This ambiguity is solved on a per-language basis
#       if the separators for the language are available
from pangeamt_nlp.utils.get_all_whitespaces import get_unicode_space_characters


class NumberInfoInText:
    """Describes a number within a text: its start index and end index, as well as the indices of any characters
    which are used to denote thousand separations (as in 1,000,000) and the index of the decimal character (if
    available)
    """
    def __init__(self, text, start_i, end_i, thousands_sep_indices=None, comma_sep_index=-1):
        if thousands_sep_indices is None:
            thousands_sep_indices = []
        self.text = text
        self.start_i = start_i
        self.end_i = end_i
        self.thousands_sep_indices = copy.deepcopy(thousands_sep_indices)
        self.comma_sep_index = comma_sep_index

    def get_number_text(self):
        return self.text[self.start_i:self.end_i]

    def has_comma_sep(self):
        return self.comma_sep_index >= 0

    def __str__(self):
        res = self.get_number_text() + "<-- from text " + self.text
        return res

    def __repr__(self):
        return self.__str__()


class NumberIdentificationHelpers:
    # First element: thousands separator. Second: comma symbol
    # Note: rules change from country to country, even within Europe (e.g. Swiss German, Austrian German, German German)
    # Note: I could not find an official source for most languages. However, the usage of space as thousand separator
    #   (either non-seperable space or thin space) is accepted (almost?) everywhere
    # Source for the linguistic information not verified by linguists:
    #   https://en.wikipedia.org/wiki/Decimal_separator#Examples_of_use

    STANDARD_SEPARATORS_PER_LANGUAGE = {
        "cs": ("\u00A0", ","),  # Not verified by linguist, czech
        "da": ("\u00A0", ","),  # Not verified by linguist
        "de": (".", ","),  # Not verified by linguist
        "en": (",", "."),  # Verified online and by myself
        "es": ("\u00A0", ","),  # Verified with Yaiza
        "fr": ("\u00A0", ","),  # Verified with Cath
        "it": ("\u00A0", ","),  # Not verified by linguist
        "nl": (".", ","), # Not verified by linguist
        "hr": (".", ","),  ## Not verified by linguist, Croatian
        "mt": (",", "."), # Maltese, not verified by linguist
        "pt": ("\u00A0", ","),  # Not verified by linguist
    }

    THOUSANDS_SEPARATORS = get_unicode_space_characters()
    THOUSANDS_SEPARATORS.extend([".", ","])
    COMMA_CHARS = [",", "."]

    @classmethod
    def get_standard_separators_for_language(cls, language_code):
        if language_code in cls.STANDARD_SEPARATORS_PER_LANGUAGE.keys():
            return cls.STANDARD_SEPARATORS_PER_LANGUAGE[language_code]
        else:
            raise ValueError("No number separators have been defined for language code " + language_code)

    @classmethod
    def has_standard_separators_for_language(cls, language_code):
        return language_code in cls.STANDARD_SEPARATORS_PER_LANGUAGE.keys()

    @classmethod
    def find_potential_thousand_sep_combos(cls, text):
        """Returns a list of lists where each list consists of the indices of thousand separators which belong to
        the same (potential) number
        Ensures that the number is valid from the left (look back), but no guarantees on what comes after"""
        res = []
        i = 0
        while i < len(text):
            char = text[i]
            if char in cls.THOUSANDS_SEPARATORS:
                if i > 0 and text[i - 1].isnumeric():
                    if i > 4 and text[i - 4:i - 1].isnumeric():
                        i += 1
                        continue
                    if i < len(text) - 5 and text[i + 1:i + 5].isnumeric():
                        i += 1
                        continue
                    if i >= 4 and text[i - 4] in cls.THOUSANDS_SEPARATORS and not text[i - 4].isspace():  # bit ad hock
                        i += 1
                        continue
                    if i < len(text) - 3 and text[i + 1:i + 4].isnumeric():
                        thousand_seps = [i]
                        j = i + 4
                        while j < len(text) - 3 and text[j] == char:
                            if text[j - 3:j].isnumeric() and text[j + 1:j + 4].isnumeric():
                                thousand_seps.append(j)
                            else:
                                break
                            j += 4
                        last_added = thousand_seps[-1]
                        if len(text) == last_added + 4 or (not text[last_added + 4].isnumeric()):
                            if len(text) > last_added+4 and char.isspace() and text[last_added + 4] == char \
                                    and text[last_added + 5].isnumeric():
                                i += 1
                                continue  # case of 123 456 7 for example. But 123,456, 891 is accepted
                            else:
                                res.append(thousand_seps)
                        i = j - 3
                        continue
            i += 1
        return res

    @classmethod
    def find_potential_commas(cls, text):
        """Returns the indices which could be a comma
        Assures that, if the part before the comma is a valid number, the entire number including the part
        behind the comma is valid. """
        potential_commas_index = []
        i = 0
        while i < len(text):
            char = text[i]
            if char in cls.COMMA_CHARS:
                if i > 0 and text[i - 1].isnumeric() and i + 1 < len(text) and text[i + 1].isnumeric():
                    # look back
                    j = i - 1
                    valid = True
                    while j >= 0 and text[j].isnumeric():
                        if text[j].isnumeric():
                            j -= 1
                        elif text[j] == char:
                            valid = False
                            break
                        break
                    if not valid:
                        continue

                    # look ahead
                    j = i + 1
                    valid = True
                    while j < len(text) and text[j].isnumeric():
                        j += 1
                    if j < len(text) and (text[j] in cls.THOUSANDS_SEPARATORS or text[j] in cls.COMMA_CHARS):
                        if j + 1 < len(text) and text[j + 1].isnumeric() and not text[j].isspace():
                            valid = False
                    if valid:
                        potential_commas_index.append(i)
            i += 1
        return potential_commas_index

    @classmethod
    def _merge_potentials_to_numbers(cls, text, potential_commas, potential_separators, language_code=None):

        new_potential_separators = [sep for sep in potential_separators]

        potential_numbers = []
        for com_index in potential_commas:
            matching_seps = [separators_indices for separators_indices in potential_separators
                             if separators_indices[-1] + 4 == com_index]

            # find start
            if len(matching_seps) == 1:
                start_i = matching_seps[0][0]
                while start_i > 0 and text[start_i - 1].isnumeric():
                    start_i -= 1
                new_potential_separators = [sep for sep in new_potential_separators if sep != matching_seps[0]]
            else:
                assert len(matching_seps) == 0  # Should never be > 1. If it is there is a logical error in the code
                start_i = com_index - 1
                while start_i > 0 and text[start_i - 1].isnumeric():
                    start_i -= 1
                if start_i > 0 and (text[start_i - 1] in cls.COMMA_CHARS):
                    continue  # No valid number

            end_index = com_index + 1
            while end_index < len(text) and text[end_index].isnumeric():
                end_index += 1
            if len(matching_seps) == 1:
                number_info = NumberInfoInText(text, start_i, end_index, thousands_sep_indices=matching_seps[0],
                                               comma_sep_index=com_index)
            else:
                number_info = NumberInfoInText(text, start_i, end_index, comma_sep_index=com_index)

            # If ambiguity (e.g. 123,456 can be interpreted as 123456), the following rule is applied:
            #   -If the language is provided, and the character used is defined as either comma symbol or
            #       thousands separator, use that interpretation
            #   -Else: give preference to comma interpretation
            equivalent_seps = [separators_indices for separators_indices in potential_separators
                               if separators_indices[0] == com_index and len(separators_indices) == 1]

            if len(equivalent_seps) > 0:
                for equivalent_sep in equivalent_seps:
                    do_comma_interp = True
                    if language_code:
                        thousands_sep, comma_symbol = cls.get_standard_separators_for_language(language_code)
                        if text[equivalent_sep[0]] == thousands_sep:  # remove the comma interpretation
                            do_comma_interp = False  # Strong false: character is usually used as thousands separator
                        elif text[equivalent_sep[0]] != comma_symbol:
                            do_comma_interp = False  # Weak False: the character is not usually used as comma symbol
                    if do_comma_interp:
                        new_potential_separators = [sep for sep in new_potential_separators
                                                    if sep not in equivalent_seps]
                        potential_numbers.append(number_info)
                    else:
                        pass  # Do not add the number here; it will be added later
            else:
                potential_numbers.append(number_info)

        # Handle those not part of a comma number
        for potential_seperator in new_potential_separators:
            start_index = potential_seperator[0] - 1
            while start_index > 0 and text[start_index - 1].isnumeric():
                start_index -= 1

            last_i = potential_seperator[-1]
            if last_i + 4 >= len(text) or (not text[last_i + 4].isspace() and (
                    text[last_i + 4] in cls.THOUSANDS_SEPARATORS or text[last_i + 4] in cls.COMMA_CHARS)):
                if last_i + 5 < len(text) and text[last_i + 5].isnumeric():
                    continue  # not valid [e.g. 123.456.12 ]
                else:
                    number_info = NumberInfoInText(text, start_index, last_i + 4,
                                                   thousands_sep_indices=potential_seperator)
                    potential_numbers.append(number_info)
            else:
                number_info = NumberInfoInText(text, start_index, last_i + 4,
                                               thousands_sep_indices=potential_seperator)
                potential_numbers.append(number_info)

        return potential_numbers

    @classmethod
    def find_numbers(cls, text, language_code=None):
        potential_commas = cls.find_potential_commas(text)
        potential_separators = cls.find_potential_thousand_sep_combos(text)
        numbers = cls._merge_potentials_to_numbers(text, potential_commas, potential_separators,
                                                   language_code=language_code)
        return numbers


class NumberSeparatorNorm(NormalizerBase):
    """Note: cannot be used together with CurrencyNorm, because they both have a different way to break
    ambiguity when identifying numbers."""

    NAME = "number_separator_norm"

    DESCRIPTION_TRAINING = """
        Normalizes all numbers in both source and target to conform to the rules of the language concerning the
        separators for thousand and the decimal character (e.g. 1.000.100,05 or 1,000,100.05). Reverts to a 
        standard rule if no explicit rules for the language are defined.
        WARNING: DO NOT USE TOGETHER WITH CurrencyNorm
    """

    DESCRIPTION_DECODING = """
        Normalizes all numbers in the source to conform to the rules of the language concerning the
        separators for thousands and the decimal character (e.g. 1.000.100,05 or 1,000,100.05). Reverts to a 
        standard rule if no explicit rules for the language are defined
        WARNING: DO NOT USE TOGETHER WITH CurrencyNorm

    """

    def __init__(self, src_lang, tgt_lang):
        super().__init__(src_lang, tgt_lang)

    def _normalize(self, text, language_code):
        numbers = NumberIdentificationHelpers.find_numbers(text)
        list_text = [char for char in text]

        thousands_sep, comma_symbol = NumberIdentificationHelpers.get_standard_separators_for_language(language_code)

        for number in numbers:
            if number.comma_sep_index >= 0:
                list_text[number.comma_sep_index] = comma_symbol
            if len(number.thousands_sep_indices) > 0:
                for sep_index in number.thousands_sep_indices:
                    list_text[sep_index] = thousands_sep
        return "".join(list_text)

    # Called when training
    def process_train(self, seg: Seg) -> None:
        if NumberIdentificationHelpers.has_standard_separators_for_language(self.get_src_lang()):
            seg.src = self._normalize(seg.src, self.get_src_lang())
        if seg.tgt is not None and NumberIdentificationHelpers.has_standard_separators_for_language(self.get_tgt_lang()):
            seg.tgt = self._normalize(seg.tgt, self.get_tgt_lang())

    # Called when using model (before calling model to translate)
    def process_src_decoding(self, seg: Seg) -> None:
        if NumberIdentificationHelpers.has_standard_separators_for_language(self.get_src_lang()):
            seg.src = self._normalize(seg.src, self.get_src_lang())

    # Called after the model translated (in case this would be necessary; usually not the case)
    def process_tgt_decoding(self, seg: Seg) -> None:
        pass
