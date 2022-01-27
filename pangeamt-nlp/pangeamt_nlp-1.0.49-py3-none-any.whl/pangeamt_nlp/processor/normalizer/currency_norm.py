from pangeamt_nlp.processor.base.normalizer_base import NormalizerBase
from pangeamt_nlp.processor.normalizer.number_separator_norm import NumberInfoInText, NumberIdentificationHelpers
from pangeamt_nlp.seg import Seg


class CurrencyNumberInfoInText(NumberInfoInText):
    """Stores information about currency amounts: both the value and the currency symbol """

    def __init__(self, text, start_i, end_i, currency_symbol_start_i, currency_symbol_end_i,
                 thousands_sep_indices=None, comma_sep_index=-1):
        if not (currency_symbol_start_i == start_i or currency_symbol_end_i == end_i):
            raise ValueError("A currency number must either start or end with a currency symbol.")

        super().__init__(text, start_i, end_i, thousands_sep_indices=thousands_sep_indices,
                         comma_sep_index=comma_sep_index)
        self.currency_symbol_start_i = currency_symbol_start_i
        self.currency_symbol_end_i = currency_symbol_end_i

    def get_currency_symbol_text(self):
        return self.text[self.currency_symbol_start_i:self.currency_symbol_end_i]

    def is_currency_sign_preceeds_number(self):
        """Returns True if the currency sign is placed before the nr, false otherwise"""
        if self.currency_symbol_start_i == self.start_i:
            return True
        else:
            return False

    def get_normalised_amount_text(self, language_code):
        """
        Normalises thousand separators and comma separators if this info is available for the language
        Changes the position of the currency sign if this is information is available for the language
        When no information is available, nothing is changed"""
        norm_seps_version = self._get_version_with_normalised_separators(language_code)
        text = norm_seps_version.text
        if CurrencyNormalisationHelpers.has_currency_info_for_language(language_code):
            in_front, spacing_char = CurrencyNormalisationHelpers.get_currency_info_for_language(language_code)
            if in_front and not norm_seps_version.is_currency_sign_preceeds_number():
                new_text = text[norm_seps_version.currency_symbol_start_i:norm_seps_version.currency_symbol_end_i]
                new_text += spacing_char
                # NOte: rstrip removes space if before there was any between nr and symbol
                new_text += text[norm_seps_version.start_i:norm_seps_version.currency_symbol_start_i].rstrip()
                return new_text
            elif (not in_front) and norm_seps_version.is_currency_sign_preceeds_number():
                # Note: lstrip removes space if before there was any between symbol and nr
                new_text = text[norm_seps_version.currency_symbol_end_i:norm_seps_version.end_i].lstrip()
                new_text += spacing_char
                new_text += text[norm_seps_version.currency_symbol_start_i:norm_seps_version.currency_symbol_end_i]
                return new_text
            else:  # only check spacing, order is correct
                if in_front:
                    new_text = text[norm_seps_version.start_i:norm_seps_version.currency_symbol_end_i]
                    new_text += spacing_char
                    new_text += text[norm_seps_version.currency_symbol_end_i:norm_seps_version.end_i].lstrip()
                    return new_text
                else:
                    new_text = text[norm_seps_version.start_i:norm_seps_version.currency_symbol_start_i].rstrip()
                    new_text += spacing_char
                    new_text += text[norm_seps_version.currency_symbol_start_i:norm_seps_version.end_i]
                    return new_text
        return text

    def _get_version_with_normalised_separators(self, language_code):
        """Returns a CurrencyNumberInfoInText with the same content but where the thousand and decimal separators
        have been normalised according to the language code defined. Returns the object itself if no separators
        are defined for the language"""
        new_nr = self
        if NumberIdentificationHelpers.has_standard_separators_for_language(language_code):
            list_text = [char for char in self.text]

            thousands_sep, comma_symbol = NumberIdentificationHelpers.get_standard_separators_for_language(
                language_code)

            if self.comma_sep_index >= 0:
                list_text[self.comma_sep_index] = comma_symbol
            if len(self.thousands_sep_indices) > 0:
                for sep_index in self.thousands_sep_indices:
                    list_text[sep_index] = thousands_sep
            res_text = "".join(list_text)
            new_nr = CurrencyNumberInfoInText(res_text, self.start_i, self.end_i, self.currency_symbol_start_i,
                                              self.currency_symbol_end_i, self.thousands_sep_indices,
                                              self.comma_sep_index)
        return new_nr


class CurrencyNormalisationHelpers:
    # Symbols which should be recognised as currency symbols
    CURRENCIES = {
        "€", "EUR",
        "$", "USD",
        "£", "GBP",
        "¥", "JPY", "円", "圓",
        "¥", "CNY", "元", "RMB",
        # Crown, from (https://en.wikipedia.org/wiki/Crown_(currency))
        "kr", "Íkr", "Kč", "CZK", "DKK", "FOK", "ISK", "NOK", "SEK"  
        "CHF", "Fr.", "fr."  # Swiss Franc https://en.wikipedia.org/wiki/Swiss_franc
    }

    # For each language whether the currency sign goes before (True) or after (False) the nr and
    # what token (if any) should be added in between
    CURRENCY_INFO_PER_LANGUAGE = {
        "en": (True, ""),
        "es": (False, "\u00A0"),
        "fr": (False, "\u00A0"),
        "FOR_TESTS": (True, "\u00A0"),
    }

    @classmethod
    def has_currency_info_for_language(cls, language_code):
        return language_code in cls.CURRENCY_INFO_PER_LANGUAGE.keys()

    @classmethod
    def get_currency_info_for_language(cls, language_code):
        if language_code in cls.CURRENCY_INFO_PER_LANGUAGE.keys():
            return cls.CURRENCY_INFO_PER_LANGUAGE[language_code]
        else:
            raise ValueError("No currency info has been defined for language code " + language_code)

    @classmethod
    def find_currency_symbols(cls, text):
        """Returns start and end index of all currency symbols found in the text"""
        currencies_indices = []
        for currency in cls.CURRENCIES:
            start_index = text.find(currency)
            while start_index >= 0:
                end_index = start_index + len(currency)
                currencies_indices.append((start_index, end_index))
                start_index = text.find(currency, start_index + 1)
        currencies_indices.sort()
        return currencies_indices

    @classmethod
    def find_currency_amounts(cls, text):
        """Returns a list with all currency amounts found in the text."""
        currency_symbols_positions = cls.find_currency_symbols(text)
        potential_thou_sep_combos = NumberIdentificationHelpers.find_potential_thousand_sep_combos(text)
        potential_commas = cls.find_potential_currency_commas(text)
        numbers = cls._merge_potentials_to_numbers(text, potential_commas=potential_commas,
                                                   potential_separators=potential_thou_sep_combos)

        # Check which numbers come just before or after a currency
        currency_numbers = []
        number_starts = [number.start_i for number in numbers]
        number_ends = [number.end_i for number in numbers]
        for symbol_start, symbol_end in currency_symbols_positions:
            # look behind:
            number = None
            added = False
            if symbol_start >= 0 and symbol_start in number_ends:
                number = [number for number in numbers if number.end_i == symbol_start][0]
            elif symbol_start > 0 and text[symbol_start - 1].isspace() and symbol_start - 1 in number_ends:
                number = [number for number in numbers if number.end_i == symbol_start - 1][0]
            else:
                start_nr = -1
                if symbol_start > 0 and text[symbol_start - 1].isnumeric():
                    start_nr = symbol_start - 1
                elif symbol_start > 1 and text[symbol_start - 1].isspace() and text[symbol_start - 2].isnumeric():
                    start_nr = symbol_start - 2
                if start_nr >= 0:
                    while start_nr > 0 and text[start_nr - 1].isnumeric():
                        start_nr -= 1
                    currency_number = CurrencyNumberInfoInText(text, start_nr, symbol_end,
                                                               currency_symbol_start_i=symbol_start,
                                                               currency_symbol_end_i=symbol_end
                                                               )
                    if cls.is_correct_currency(currency_number):
                        currency_numbers.append(currency_number)
                        added = True

            if number:
                currency_number = CurrencyNumberInfoInText(text, number.start_i, symbol_end,
                                                           currency_symbol_start_i=symbol_start,
                                                           currency_symbol_end_i=symbol_end,
                                                           thousands_sep_indices=number.thousands_sep_indices,
                                                           comma_sep_index=number.comma_sep_index
                                                           )
                if cls.is_correct_currency(currency_number):
                    currency_numbers.append(currency_number)
                    added = True

            # look ahead
            if not added:
                number = None
                if symbol_end < len(text) and symbol_end in number_starts:
                    number = [number for number in numbers if number.start_i == symbol_end][0]
                elif (symbol_end < len(text) - 1 and text[symbol_end].isspace()
                      and symbol_end + 1 in number_starts):
                    number = [number for number in numbers if number.start_i == symbol_end + 1][0]
                else:
                    end_nr = -1
                    if symbol_end < len(text) and text[symbol_end].isnumeric():
                        end_nr = symbol_end
                    elif symbol_end < len(text) - 1 and text[symbol_end].isspace() \
                            and text[symbol_end + 1].isnumeric():
                        end_nr = symbol_end + 1
                    if end_nr >= 0:
                        while end_nr < len(text) - 1 and text[end_nr + 1].isnumeric():
                            end_nr += 1
                        currency_number = CurrencyNumberInfoInText(text, symbol_start, end_nr + 1,
                                                                   currency_symbol_start_i=symbol_start,
                                                                   currency_symbol_end_i=symbol_end,
                                                                   )
                        if cls.is_correct_currency(currency_number):
                            currency_numbers.append(currency_number)

                if number:
                    currency_number = CurrencyNumberInfoInText(text, symbol_start, number.end_i,
                                                               currency_symbol_start_i=symbol_start,
                                                               currency_symbol_end_i=symbol_end,
                                                               thousands_sep_indices=number.thousands_sep_indices,
                                                               comma_sep_index=number.comma_sep_index
                                                               )
                    if cls.is_correct_currency(currency_number):
                        currency_numbers.append(currency_number)

        return currency_numbers

    @classmethod
    def is_correct_currency(cls, currency):
        """Checks if a given currency makes sense in the text (see code for the rules used)"""
        text = currency.text
        start_i = currency.start_i
        end_i = currency.end_i - 1

        # no nr behind or in front
        if start_i > 0 and text[start_i - 1].isnumeric():
            return False
        if end_i < len(text) - 1 and text[end_i + 1].isnumeric():
            return False
        # no comma sign with nr behind
        if end_i < len(text) - 2 and text[end_i + 1] in NumberIdentificationHelpers.COMMA_CHARS \
                and text[end_i + 2].isnumeric():
            return False
        # no comma sign with nr in front
        if start_i > 1 and text[start_i - 1] in NumberIdentificationHelpers.COMMA_CHARS \
                and text[start_i - 2].isnumeric():
            return False

        return True

    @classmethod
    def find_potential_currency_commas(cls, text):
        """Returns a list with the indices of all characters which could possibly be a comma for a currency nr"""
        potential_comma_indices = NumberIdentificationHelpers.find_potential_commas(text)
        final_pot_comma_indices = []
        for potential_comma_i in potential_comma_indices:
            last_nr_index = potential_comma_i + 1
            while last_nr_index + 1 < len(text) and text[last_nr_index + 1].isnumeric():
                last_nr_index += 1
            if last_nr_index - potential_comma_i <= 2:
                final_pot_comma_indices.append(potential_comma_i)
        return final_pot_comma_indices

    @classmethod
    def _merge_potentials_to_numbers(cls, text, potential_commas, potential_separators):
        """Merges a given list of potential comma indices and potential thousand separator indices to produce
        a list of all numbers which could possible be values belonging to a currency"""
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
                if start_i > 0 and (text[start_i - 1] in NumberIdentificationHelpers.COMMA_CHARS):
                    continue  # No valid number

            end_index = com_index + 1
            while end_index < len(text) and text[end_index].isnumeric():
                end_index += 1
            if len(matching_seps) == 1:
                number_info = NumberInfoInText(text, start_i, end_index, thousands_sep_indices=matching_seps[0],
                                               comma_sep_index=com_index)
                potential_numbers.append(number_info)

            else:
                number_info = NumberInfoInText(text, start_i, end_index, comma_sep_index=com_index)
                potential_numbers.append(number_info)

        # Handle those not part of a comma number
        for potential_seperator in new_potential_separators:
            start_index = potential_seperator[0] - 1
            while start_index > 0 and text[start_index - 1].isnumeric():
                start_index -= 1

            last_i = potential_seperator[-1]
            if last_i + 4 >= len(text) or (not text[last_i + 4].isspace() and (
                    text[last_i + 4] in NumberIdentificationHelpers.THOUSANDS_SEPARATORS
                    or text[last_i + 4] in NumberIdentificationHelpers.COMMA_CHARS)):
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


class CurrencyNorm(NormalizerBase):
    """Note: cannot be used together with NumberSeparatorNorm, because they both have a different way to break
    ambiguity when identifying numbers."""
    NAME = "currency_norm"

    DESCRIPTION_TRAINING = """
        Normalises all occurrences of currency amounts if a rule for the language is explicitly present, 
        does nothing otherwise
        WARNING: DO NOT USE TOGETHER WITH NumperSeparatorNorm
    """

    DESCRIPTION_DECODING = """
        Normalises all occurrences of currency amounts if a rule for the language is explicitly present, 
        does nothing otherwise
        WARNING: DO NOT USE TOGETHER WITH NumperSeparatorNorm

    """

    def __init__(self, src_lang, tgt_lang):
        super().__init__(src_lang, tgt_lang)

    def _normalize(self, text, language_code):
        currency_amounts = CurrencyNormalisationHelpers.find_currency_amounts(text)
        sorted_currency_amounts = sorted(currency_amounts, key=lambda curr_amount: curr_amount.start_i)

        prev_end = 0
        i = 0
        res_text = ""
        while i < len(sorted_currency_amounts):
            curr_am = sorted_currency_amounts[i]
            res_text += text[prev_end:curr_am.start_i]
            res_text += curr_am.get_normalised_amount_text(language_code)
            prev_end = curr_am.end_i
            i += 1
        res_text += text[prev_end:]
        return res_text

    # Called when training
    def process_train(self, seg: Seg) -> None:
        if CurrencyNormalisationHelpers.has_currency_info_for_language(self.get_src_lang()):
            seg.src = self._normalize(seg.src, self.get_src_lang())
        if seg.tgt is not None and CurrencyNormalisationHelpers.has_currency_info_for_language(self.get_tgt_lang()):
            seg.tgt = self._normalize(seg.tgt, self.get_tgt_lang())

    # Called when using model (before calling model to translate)
    def process_src_decoding(self, seg: Seg) -> None:
        if CurrencyNormalisationHelpers.has_currency_info_for_language(self.get_src_lang()):
            seg.src = self._normalize(seg.src, self.get_src_lang())

    # Called after the model translated (in case this would be necessary; usually not the case)
    def process_tgt_decoding(self, seg: Seg) -> None:
        pass
