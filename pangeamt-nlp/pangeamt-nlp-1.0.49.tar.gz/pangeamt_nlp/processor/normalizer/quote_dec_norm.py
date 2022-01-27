# ToDo Decide what to do with the universal single quote, which is also the apostrophe (many false positives) [For now: removed]
# ToDo Decide what to do with quotation dash (https://en.wikipedia.org/wiki/Quotation_mark#Quotation_dash)

# Note on code design: for now there is one non-trivial matching of quotes, for the single quote/apostrophe
# (which is based on a more complex check also incorporating the characters before and after, to differentiate
# apostrophe usage from single quote usage)
# This has been solved ad hoc.
# It could be solved nicely by defining a quote as a regex (containing look-ahead and look-behind functionality),
# and matching regexes instead of characters.
# However, this is overkill unless there is a more compelling need than for the signel apostrophe/quotation mark


from enum import Enum

from pangeamt_nlp.processor.base.normalizer_base import NormalizerBase
from pangeamt_nlp.seg import Seg


class MetaQuote(Enum):
    OPEN1 = 1
    CLOSE1 = 2
    OPEN2 = 3
    CLOSE2 = 4


class QuotesInfo:
    """Contains linguistic info as to which quotes are used in which language
    STANDARD_QUOTES_PER_LANGUAGE contains the standard quotes for each language
    ALL_QUOTE_PAIRS_PER_LANGUAGE contains all accepted quote pairs for each language
    UNIVERSAL_QUOTE_PAIRS contains those quote pairs which are accepted in all languages

    To add information for a new language:
        add info to both STANDARD_QUOTES_PER_LANGUAGE and ALL_QUOTE_PAIRS_PER_LANGUAGE
    """
    # Source: https://en.wikipedia.org/wiki/Quotation_mark

    STANDARD_QUOTES_PER_LANGUAGE = {
        "cz": {  # Not verified by linguist
            MetaQuote.OPEN1: '„',
            MetaQuote.CLOSE1: '“',
            MetaQuote.OPEN2: '‚',
            MetaQuote.CLOSE2: '‘',
        },
        "da": {  # Not verified by linguist
            MetaQuote.OPEN1: "»",
            MetaQuote.CLOSE1: "«",
            MetaQuote.OPEN2: '›',
            MetaQuote.CLOSE2: '‹',
        },
        "de": {  # Verified by Andi
            MetaQuote.OPEN1: '„',
            MetaQuote.CLOSE1: '“',
            MetaQuote.OPEN2: '‚',
            MetaQuote.CLOSE2: '‘',
        },
        "en": {  # Verified by Jess
            MetaQuote.OPEN1: "‘",
            MetaQuote.CLOSE1: "’",
            MetaQuote.OPEN2: '“',
            MetaQuote.CLOSE2: '”',
        },
        "es": {
            # Verified by Marta.
            # Note that an alternative exists (using the French quotes)
            MetaQuote.OPEN1: "“",
            MetaQuote.CLOSE1: "”",
            MetaQuote.OPEN2: '‘',
            MetaQuote.CLOSE2: '’',
        },
        "fr": {  # Verified by Cath
            MetaQuote.OPEN1: "«",
            MetaQuote.CLOSE1: "»",
            MetaQuote.OPEN2: '“',
            MetaQuote.CLOSE2: '”',
        },
        "hr": {  # Not verified by linguist, Croatian
            MetaQuote.OPEN1: "„",
            MetaQuote.CLOSE1: "”",
            MetaQuote.OPEN2: '‘',
            MetaQuote.CLOSE2: '’',
        },
        "it": {  # Not verified by linguist
            MetaQuote.OPEN1: "«",
            MetaQuote.CLOSE1: "»",
            MetaQuote.OPEN2: '“',
            MetaQuote.CLOSE2: '”',
        },
        "mt": {  # Not verified by linguist
            MetaQuote.OPEN1: "“",
            MetaQuote.CLOSE1: "”",
            MetaQuote.OPEN2: '‘',
            MetaQuote.CLOSE2: '’',
        },
        "nl": {  # Not verified by linguist
            MetaQuote.OPEN1: "“",
            MetaQuote.CLOSE1: "”",
            MetaQuote.OPEN2: "‘",
            MetaQuote.CLOSE2: "’",
        },
        "pt": {  # Not verified by linguist
            MetaQuote.OPEN1: "«",
            MetaQuote.CLOSE1: "»",
            MetaQuote.OPEN2: '“',
            MetaQuote.CLOSE2: '”',
        },
        "pl": {  # Verified by Joanna
            MetaQuote.OPEN1: '„',
            MetaQuote.CLOSE1: "”",
            MetaQuote.OPEN2: "»",
            MetaQuote.CLOSE2: "«",
        },
        "sq": {  # Not verified by linguist
            MetaQuote.OPEN1: "„",
            MetaQuote.CLOSE1: "“",
            MetaQuote.OPEN2: "‘",
            MetaQuote.CLOSE2: "’"
        },
        "ar": {  # Not verified by linguist (Second quotes to be revised)
            MetaQuote.OPEN1: "«",
            MetaQuote.CLOSE1: "»",
            MetaQuote.OPEN2: "«",
            MetaQuote.CLOSE2: "»"
        },
        "hy": {  # Not verified by linguist (Second quotes to be revised)
            MetaQuote.OPEN1: "«",
            MetaQuote.CLOSE1: "»",
            MetaQuote.OPEN2: "«",
            MetaQuote.CLOSE2: "»"
        },
        "az": {  # Not verified by linguist
            MetaQuote.OPEN1: "«",
            MetaQuote.CLOSE1: "»",
            MetaQuote.OPEN2: "„",
            MetaQuote.CLOSE2: "“"
        },
        "eu": {  # Not verified by linguist
            MetaQuote.OPEN1: "«",
            MetaQuote.CLOSE1: "»",
            MetaQuote.OPEN2: '“',
            MetaQuote.CLOSE2: '”'
        },
        "be": {  # Not verified by linguist
            MetaQuote.OPEN1: "«",
            MetaQuote.CLOSE1: "»",
            MetaQuote.OPEN2: "„",
            MetaQuote.CLOSE2: "“"
        },
        "bo": {  # Not verified by linguist
            MetaQuote.OPEN1: "《",
            MetaQuote.CLOSE1: "》",
            MetaQuote.OPEN2: "〈",
            MetaQuote.CLOSE2: "〉"
        },
        "bs": {  # Not verified by linguist
            MetaQuote.OPEN1: "”",
            MetaQuote.CLOSE1: "”",
            MetaQuote.OPEN2: "’",
            MetaQuote.CLOSE2: "’"
        },
        'bg': {  # Not verified by linguist
            MetaQuote.OPEN1: '„',
            MetaQuote.CLOSE1: '“',
            MetaQuote.OPEN2: '’',
            MetaQuote.CLOSE2: '’',
        },
        'ca': {  # Not verified by linguist
            MetaQuote.OPEN1: '«',
            MetaQuote.CLOSE1: '»',
            MetaQuote.OPEN2: '“',
            MetaQuote.CLOSE2: '”',
        },
        'cs': {  # Not verified by linguist
            MetaQuote.OPEN1: '„',
            MetaQuote.CLOSE1: '“',
            MetaQuote.OPEN2: '‚',
            MetaQuote.CLOSE2: '‘',
        },
        'zh': {  # Not verified by linguist
            MetaQuote.OPEN1: '“',
            MetaQuote.CLOSE1: '”',
            MetaQuote.OPEN2: '‘',
            MetaQuote.CLOSE2: '’',
        },
        'tw': {  # Not verified by linguist
            MetaQuote.OPEN1: '“',
            MetaQuote.CLOSE1: '”',
            MetaQuote.OPEN2: '‘',
            MetaQuote.CLOSE2: '’',
        },
        'el': {  # Not verified by linguist
            MetaQuote.OPEN1: '«',
            MetaQuote.CLOSE1: '»',
            MetaQuote.OPEN2: '“',
            MetaQuote.CLOSE2: '”',
        },
        'et': {  # Not verified by linguist (Second quotes to be revised)
            MetaQuote.OPEN1: '„',
            MetaQuote.CLOSE1: '“',
            MetaQuote.OPEN2: '„',
            MetaQuote.CLOSE2: '“'
        },
        'fa': {  # Not verified by linguist (Second quotes to be revised)
            MetaQuote.OPEN1: '«',
            MetaQuote.CLOSE1: '»',
            MetaQuote.OPEN2: '«',
            MetaQuote.CLOSE2: '»'
        },
        'ro': {  # Not verified by linguist
            MetaQuote.OPEN1: '„',
            MetaQuote.CLOSE1: '”',
            MetaQuote.OPEN2: '«',
            MetaQuote.CLOSE2: '»',
        },
        'ru': {  # Not verified by linguist
            MetaQuote.OPEN1: '«',
            MetaQuote.CLOSE1: '»',
            MetaQuote.OPEN2: '„',
            MetaQuote.CLOSE2: '”',
        },
        'sk': {  # Not verified by linguist
            MetaQuote.OPEN1: '„',
            MetaQuote.CLOSE1: '“',
            MetaQuote.OPEN2: '‚',
            MetaQuote.CLOSE2: '‘',
        },
        'sl': {  # Not verified by linguist
            MetaQuote.OPEN1: '„',
            MetaQuote.CLOSE1: '“',
            MetaQuote.OPEN2: '‚',
            MetaQuote.CLOSE2: '‘',
        },
        'sr': {  # Not verified by linguist
            MetaQuote.OPEN1: '„',
            MetaQuote.CLOSE1: '”',
            MetaQuote.OPEN2: '’',
            MetaQuote.CLOSE2: '’',
        },
        'sv': {  # Not verified by linguist
            MetaQuote.OPEN1: '”',
            MetaQuote.CLOSE1: '”',
            MetaQuote.OPEN2: '’',
            MetaQuote.CLOSE2: '’',
        },
        'ta': {  # Not verified by linguist
            MetaQuote.OPEN1: '“',
            MetaQuote.CLOSE1: '”',
            MetaQuote.OPEN2: '‘',
            MetaQuote.CLOSE2: '’',
        },
        'th': {  # Not verified by linguist
            MetaQuote.OPEN1: '“',
            MetaQuote.CLOSE1: '”',
            MetaQuote.OPEN2: '‘',
            MetaQuote.CLOSE2: '’',
        },
        'ti': {  # Not verified by linguist
            MetaQuote.OPEN1: '«',
            MetaQuote.CLOSE1: '»',
            MetaQuote.OPEN2: '‹',
            MetaQuote.CLOSE2: '›',
        },
        'tr': {  # Not verified by linguist
            MetaQuote.OPEN1: '“',
            MetaQuote.CLOSE1: '”',
            MetaQuote.OPEN2: '‘',
            MetaQuote.CLOSE2: '’',
        },
        'uk': {  # Not verified by linguist
            MetaQuote.OPEN1: '«',
            MetaQuote.CLOSE1: '»',
            MetaQuote.OPEN2: '“',
            MetaQuote.CLOSE2: '”',
        },
        'ur': {  # Not verified by linguist
            MetaQuote.OPEN1: '“',
            MetaQuote.CLOSE1: '”',
            MetaQuote.OPEN2: '‘',
            MetaQuote.CLOSE2: '’',
        },
        'ug': {  # Not verified by linguist
            MetaQuote.OPEN1: '«',
            MetaQuote.CLOSE1: '»',
            MetaQuote.OPEN2: '‹',
            MetaQuote.CLOSE2: '›',
        },
        'uz': {  # Not verified by linguist
            MetaQuote.OPEN1: '«',
            MetaQuote.CLOSE1: '»',
            MetaQuote.OPEN2: '„',
            MetaQuote.CLOSE2: '“',
        },
        'vi': {  # Not verified by linguist (Second quotes to be revised)
            MetaQuote.OPEN1: '“',
            MetaQuote.CLOSE1: '”',
            MetaQuote.OPEN2: '“',
            MetaQuote.CLOSE2: '”'
        },
        'cy': {  # Not verified by linguist
            MetaQuote.OPEN1: '‘',
            MetaQuote.CLOSE1: '’',
            MetaQuote.OPEN2: '“',
            MetaQuote.CLOSE2: '”',
        },
        'ko': {  # Not verified by linguist
            MetaQuote.OPEN1: "‘",
            MetaQuote.CLOSE1: "’",
            MetaQuote.OPEN2: '“',
            MetaQuote.CLOSE2: '”',
        },
    }

    # Source: #https://en.wikipedia.org/wiki/Quotation_mark
    ALL_QUOTE_PAIRS_PER_LANGUAGE = {
        "cz": {  # Not verified by linguist
            '„': '“',
            '‚': '‘',
            "»": "«",
            "›": "‹",
        },
        "da": {  # Not verified by linguist
            "»": "«",
            "„": "“",
            "›": "‹",
            "‚": "‘",
            '”': '”',
            "’": "’",
        },
        "de": {  # Not verified by linguist
            '„': '“',
            '‚': '‘',
            '»': '«',
            '›': '‹',
            '«': '»',  # Swiss German
            '‹': '›',  # Swiss German
        },
        "en": {  # UK English
            "‘": "’",
            '“': '”',
        },
        "es": {  # Not verified by linguist
            "“": "”",
            '‘': '’',
            '«': '»',
        },
        "fr": {  # Not verified by linguist
            '«': '»',  # French level 1/level 2
            '‹': '›',  # French alternative level 2
            '“': '”',  # French alternative level 2
            '“': '”',  # French alternative level 1
            "‘": "’",  # French alternative level 2
        },
        "hr": {
            "„": "”",
            '‘': '’',
            "»": "«",
        },
        "it": {  # Not verified by linguist
            "«": "»",
            "“": "”",
            "‘": "’",
        },
        "nl": {  # Not verified by linguist
            "“": "”",
            "‘": "’",
            "„": "”",
            ",": "’",
        },
        "mt": {  # Not verified by linguist
            "“": "”",
            '‘': '’',
        },
        "pt": {  # Not verified by linguist, Portuguese from Portugal
            '«': '»',
            '“': '”',
            '‘': '’',
        },
        "pl": {  # Verified by Joanna
            "„": "”",
            "»": "«",
        },
        "sq": {  # Not verified by linguist
            "„": "“",
            "‘": "’"
        },
        "ar": {  # Not verified by linguist
            "«": "»",
        },
        "hy": {  # Not verified by linguist
            "«": "»",
        },
        "az": {  # Not verified by linguist
            "«": "»",
            "„": "“"
        },
        "eu": {  # Not verified by linguist
            "«": "»",
            '“': '”'
        },
        "be": {  # Not verified by linguist
            "«": "»",
            "„": "“"
        },
        "bo": {  # Not verified by linguist
            "《": "》",
            "〈": "〉"
        },
        "bs": {  # Not verified by linguist
            "”": "”",
            "’": "’"
        },
        'bg': {  # Not verified by linguist
            '„': '“',
            '’': '’',
        },
        'ca': {  # Not verified by linguist
            '«': '»',
            '“': '”',
        },
        'cs': {  # Not verified by linguist
            '„': '“',
            '‚': '‘',
        },
        'zh': {  # Not verified by linguist
            '“': '”',
            '‘': '’',
        },
        'tw': {  # Not verified by linguist
            '“': '”',
            '‘': '’',
        },
        'el': {  # Not verified by linguist
            '«': '»',
            '“': '”',
        },
        'et': {  # Not verified by linguist
            '„': '“',
        },
        'fa': {  # Not verified by linguist
            '«': '»',
        },
        'ro': {  # Not verified by linguist
            '„': '”',
            '«': '»',
        },
        'ru': {  # Not verified by linguist
            '«': '»',
            '„': '”',
        },
        'sk': {  # Not verified by linguist
            '„': '“',
            '‚': '‘',
        },
        'sl': {  # Not verified by linguist
            '„': '“',
            '‚': '‘',
        },
        'sr': {  # Not verified by linguist
            '„': '”',
            '’': '’',
        },
        'sv': {  # Not verified by linguist
            '”': '”',
            '’': '’',
        },
        'ta': {  # Not verified by linguist
            '“': '”',
            '‘': '’',
        },
        'th': {  # Not verified by linguist
            '“': '”',
            '‘': '’',
        },
        'ti': {  # Not verified by linguist
            '«': '»',
            '‹': '›',
        },
        'tr': {  # Not verified by linguist
            '“': '”',
            '‘': '’',
        },
        'uk': {  # Not verified by linguist
            '«': '»',
            '“': '”',
        },
        'ur': {  # Not verified by linguist
            '“': '”',
            '‘': '’',
        },
        'ug': {  # Not verified by linguist
            '«': '»',
            '‹': '›',
        },
        'uz': {  # Not verified by linguist
            '«': '»',
            '„': '“',
        },
        'vi': {  # Not verified by linguist
            '“': '”',
        },
        'cy': {  # Not verified by linguist
            '‘': '’',
            '“': '”',
        },
        'ko': {  # Not verified by linguist
            "‘": "’",
            '“': '”',
        },

    }

    # The quotes which should be searched in every language
    UNIVERSAL_QUOTE_PAIRS = {
        '"': '"',  # Universal lazy quote (same as programming string)
        # Universal lazy quote (same as programming string) Note: matches apostrophe as well
        #   (there are some tests to reduce false positives to a hopefully acceptable level)
        "'": "'",
    }

    @classmethod
    def get_standard_quotes_for_language(cls, language_code):
        """Returns the quotation marks as they should be displated for the language (the result of the normalisation)
        If no quotation marks have been defined for the language, the standard quotation marks are returned"""
        if cls.has_standard_quotes_for_language(language_code):
            return cls.STANDARD_QUOTES_PER_LANGUAGE[language_code]
        else:
            raise ValueError(
                "No quotes are defined for language with language_code " + language_code)

    @classmethod
    def get_all_quote_pairs_for_language(cls, language_code):
        """Returns all possible quotation mark combinations (opening and closing quote) that can (reasonibly) be
        encountered in text written in the given language"""
        # Always include the universal quotes. Note: they can be overwritten later on (meaning the closing quote can
        # in theory change, although I do not think this likely
        quotes = cls.UNIVERSAL_QUOTE_PAIRS
        if cls.has_quote_pairs_for_language(language_code):
            quote_pairs = cls.ALL_QUOTE_PAIRS_PER_LANGUAGE[language_code]
        else:
            raise ValueError(
                "No quotes are defined for language with language_code " + language_code)
        for open_quote, close_quote in quote_pairs.items():
            quotes[open_quote] = close_quote
        # For safety: explicitly adding the normalised version of the quotes to be used in output as well
        # Although supposedly it should have been added to the options
        norm_quotes = cls.get_standard_quotes_for_language(language_code)
        quotes[norm_quotes[MetaQuote.OPEN1]] = norm_quotes[MetaQuote.CLOSE1]
        quotes[norm_quotes[MetaQuote.OPEN2]] = norm_quotes[MetaQuote.CLOSE2]
        return quotes

    @classmethod
    def has_quote_pairs_for_language(cls, language_code):
        return language_code in cls.ALL_QUOTE_PAIRS_PER_LANGUAGE.keys()

    @classmethod
    def has_standard_quotes_for_language(cls, language_code):
        return language_code in cls.STANDARD_QUOTES_PER_LANGUAGE.keys()

    @classmethod
    def get_standard_open_quotes_for_language(cls, language_code):
        """Returns the standard characters used as opening quotes in the specified language
        The first character is the opening quote at hierarchy level 1. The second at level 2
        (-> a quote within a quote)"""
        quotes = cls.get_standard_quotes_for_language(language_code)
        res = []
        res.append(quotes[MetaQuote.OPEN1])
        res.append(quotes[MetaQuote.OPEN2])
        return res

    @classmethod
    def get_standard_close_quotes_for_language(cls, language_code):
        """Returns the standard characters used as closing quotes in the specified language
        The first character is the closing quote at hierarchy level 1. The second at level 2
        (-> a quote within a quote)"""
        quotes = cls.get_standard_quotes_for_language(language_code)
        res = []
        res.append(quotes[MetaQuote.CLOSE1])
        res.append(quotes[MetaQuote.CLOSE2])
        return res


class QuoteDecNorm(NormalizerBase):
    DESCRIPTION_TRAINING = """
        Normalises the quotes for both the source and target language. After normalisation only two types of quotes 
        remain for each language: the level 1 and level 2 quotes defined for it.
    """

    DESCRIPTION_DECODING = """
        Normalises the quotes of the source (leaves target unchanged). After normalisation only two types of quotes 
        remain: the level 1 and level 2 quotes defined for the language.
    """

    NAME = "quote_dec_norm"

    def __init__(self, src_lang: str, tgt_lang: str):
        """Initialise the quote normalizer.
        The output of the normalization will be the respective standard quotes of the source and target language
        Based on the quote pairs defined for each language"""
        super().__init__(src_lang, tgt_lang)

    def _normalize(self, text, language_code):
        """"Normalizes all quotes to the normalized form defined for the language"""
        if text is None:
            return text
        metaquotes_dict = self._identify_quotes(text, language_code)
        correct_quotes = QuotesInfo.get_standard_quotes_for_language(
            language_code)
        res_text = self._fill_in_quotes(text, metaquotes_dict, correct_quotes)
        return res_text

    def _fill_in_quotes(self, text, metaquotes_dict, correct_quotes):
        """Given a dictionary of where to put which kind of quotes, put the correct quotes in the text"""
        norm_text_list = list(text)
        for index, metaquote_value in metaquotes_dict.items():
            norm_text_list[index] = correct_quotes[metaquote_value]
        norm_text = "".join(norm_text_list)
        return norm_text

    @classmethod
    def _is_apostrophe_on_index(cls, i, text):
        apostrophe_symbols = ["'", "’"]  # straight and curved quote
        if text[i] not in apostrophe_symbols:
            return False
        else:
            if i > 0 and text[i - 1].isalpha():
                if i < len(text) - 1 and text[i + 1].isalpha():
                    return True
        return False

    def _identify_quotes(self, text, language_code):
        """Identify the indices of characters which are quotes. Only quotes which both open and close are considered.
        Differentiates between quotes at the base level and quotes at the second level. Quotes at a deeper hierarchy
        are not considered"""
        metaquotes_dict = dict()
        quote_pairs = QuotesInfo.get_all_quote_pairs_for_language(
            language_code)

        i = 0
        while i < len(text):
            if text[i] in quote_pairs.keys():
                # WARNING: AD HOC FIX
                if text[i] == "'":
                    if self._is_apostrophe_on_index(i, text):
                        i += 1
                        continue
                closing_quote = quote_pairs[text[i]]
                closing_quote_index = text.find(closing_quote, i + 1)
                # WARNING: AD HOC FIX
                while closing_quote_index >= 0 and self._is_apostrophe_on_index(
                        closing_quote_index, text):
                    closing_quote_index = text.find(closing_quote,
                                                    closing_quote_index + 1)
                # Only consider quotes which are closed
                if closing_quote_index >= 0:
                    metaquotes_dict[i] = MetaQuote.OPEN1
                    metaquotes_dict[closing_quote_index] = MetaQuote.CLOSE1
                    # Checking if there are level 2 quotes
                    j = i + 1
                    while j < closing_quote_index:
                        if text[j] in quote_pairs.keys():
                            # WARNING: AD HOC FIX
                            if text[j] == "'":
                                if self._is_apostrophe_on_index(j, text):
                                    j += 1
                                    continue
                            closing_quote_level2 = quote_pairs[text[j]]
                            closing_quote_level2_index = text.find(
                                closing_quote_level2, j + 1,
                                closing_quote_index)
                            while closing_quote_level2_index >= 0 and \
                                    self._is_apostrophe_on_index(
                                        closing_quote_level2_index, text):
                                closing_quote_level2_index = text.find(
                                    closing_quote_level2,
                                    closing_quote_level2_index + 1)
                            # Only consider quotes which are closed
                            if closing_quote_level2_index > 0:
                                metaquotes_dict[j] = MetaQuote.OPEN2
                                metaquotes_dict[
                                    closing_quote_level2_index] = MetaQuote.CLOSE2
                                # Assume there are never quotes of level 3
                                j = closing_quote_level2_index + 1
                            else:
                                j = j + 1
                        else:
                            j = j + 1
                    i = closing_quote_index + 1
                else:
                    i += 1
            else:
                i += 1
        return metaquotes_dict

    # Called when training
    def process_train(self, seg: Seg) -> None:
        pass

    # Called when u sing model (before calling model to translate)
    def process_src_decoding(self, seg: Seg) -> None:
        pass

    # Called after the model translated (in case this would be necessary; usually not the case)
    # ToDo: place this code elsewhere--this spacing mistake is made by the detokenizer, not by this normalizer,
    #   so solving it here introduces an ugly dependency on code which is not directly related to this package
    # ToDo: check what should be done with other languages
    # ToDo: make cleaner (define list of symbols and apply a for instead of cascading?)
    def process_tgt_decoding(self, seg: Seg) -> None:
        seg.tgt = self._normalize(seg.tgt, self.get_tgt_lang())
        if self.tgt_lang == 'en' or self.tgt_lang == 'es':
            seg.tgt = seg.tgt.replace("‘ ", "‘").replace(' ’', '’').replace(
                '“ ', '“').replace(' ”', '”') \
                .replace('< ', '<').replace(' >', '>')
        if self.tgt_lang == "uk" or self.tgt_lang == "ru":
            seg.tgt = seg.tgt.replace(' ’ ', '’')
