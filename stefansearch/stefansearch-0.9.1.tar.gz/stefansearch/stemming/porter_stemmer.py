from stefansearch.stemming.stemmer import Stemmer


class PorterStemmer(Stemmer):
    """My implementation of Porter Stemming (Step 1 only)."""
    # Set of vowel characters, lowercase
    VOWELS = {'a', 'e', 'i', 'o', 'u'}

    def get_stem(self, token: str) -> str:
        # Apply Rule 1a followed by Rule 2a.
        return self._porter_2a(self._porter_1a(token))

    @staticmethod
    def _porter_1a(term: str) -> str:
        """Execute step 1a of Porter stemming"""
        # If suffix is 'us' or 'ss' do nothing
        if term.endswith('us') or term.endswith('ss'):
            return term
        # Attempt sses, ied/ies, and s rules in order.
        # Use the first one that removes a suffix.
        for rule in [PorterStemmer._p1a_sses, PorterStemmer._p1a_ied_ies, PorterStemmer._p1a_s]:
            len_suffix, stemmed_word = rule(term)
            if len_suffix > 0:
                return stemmed_word
        # No match: return original term
        return term

    @staticmethod
    def _p1a_sses(term: str) -> (int, str):
        """
        Replace 'sses' by 'ss'.

        Returns length of suffix removed, and resulting stem.
        """
        if term.endswith('sses'):
            return 4, term[:-2]
        return 0, term

    @staticmethod
    def _p1a_s(term: str) -> (int, str):
        """
        Delete 's' if the preceding word part contains a vowel not
        immediately before the 's'.

        Returns length of suffix removed, and resulting stem.
        """
        if term.endswith('s') and PorterStemmer._contains_vowel(term[:-1]) and not term[-2] in PorterStemmer.VOWELS:
            return 1, term[:-1]
        else:
            return 0, term

    @staticmethod
    def _p1a_ied_ies(term: str) -> (int, str):
        """
        Replace 'ied' or 'ies' by 'i' if preceded by more than one
        letter, otherwise by 'ie'

        Returns length of suffix removed, and resulting stem.
        """
        if term.endswith('ied') or term.endswith('ies'):
            if len(term) > 4:
                return 3, term[:-3] + 'i'
            else:
                return 3, term[:-3] + 'ie'
        return 0, term

    @staticmethod
    def _porter_2a(term: str) -> str:
        """
        Attempts to apply eed/eedly and ed/edly/ing/ingly rules.

        Returns the resulting shortest stem.
        """
        best_stem = term
        longest_suffix_rmvd = 0
        # Attempt eed/eedly, ed/edly/ing/ingly rules and track the
        # longest suffix removed
        for rule in [PorterStemmer._p1b_eed_eedly, PorterStemmer._p1b_ed_edly_ing_ingly]:
            len_suffix, stemmed_term = rule(term)
            if len_suffix > longest_suffix_rmvd:
                longest_suffix_rmvd = len_suffix
                best_stem = stemmed_term
        return best_stem

    @staticmethod
    def _p1b_eed_eedly(term: str) -> (int, str):
        """
        Replace 'eed', 'eedly' by 'ee' if it is in the part of the
        word after the first non-vowel following a vowel.

        Returns length of suffix removed, and resulting stem.
        """
        if term.endswith('eed'):
            test_word = term[:-3]
        elif term.endswith('eedly'):
            test_word = term[:-5]
        else:
            return 0, term
        first_vowel_index = PorterStemmer._find_first_vowel(test_word)
        if first_vowel_index == -1:
            return 0, term
        else:
            for index in range(first_vowel_index + 1, len(test_word)):
                if test_word[index] not in PorterStemmer.VOWELS:
                    # condition met
                    return (3, term[:-1]) if term.endswith('eed') else (5, term[:-3])
            return 0, term

    @staticmethod
    def _p1b_ed_edly_ing_ingly(term: str) -> (int, str):
        """
        Delete 'ed', 'edly', 'ing', 'ingly' if the preceeding word part
        contains a vowel, and then if the word inds in 'at', 'bl', or 'iz'
        add 'e', or if the word ends with a double letter that is not 'll',
        'ss', or 'zz', remove the last letter, or if the word is short, add 'e'

        Returns length of suffix removed, and resulting stem.
        """
        if term.endswith('ed'):
            suffix_len = 2
        elif term.endswith('edly'):
            suffix_len = 4
        elif term.endswith('ing'):
            suffix_len = 3
        elif term.endswith('ingly'):
            suffix_len = 5
        else:
            return 0, term

        # Remove suffix for further tests
        test_word = term[:-suffix_len]
        if PorterStemmer._contains_vowel(test_word):
            if test_word.endswith('at') or test_word.endswith('bl') or \
                    test_word.endswith('iz'):
                return suffix_len, test_word + 'e'
            elif len(test_word) >= 2 and test_word[-1] == test_word[-2] and \
                    test_word[-1] != 'l' and test_word[-1] != 's' and test_word[-1] != 'z':
                return suffix_len, test_word[:-1]
            elif len(test_word) < 4:
                return suffix_len, test_word + 'e'
            else:
                return suffix_len, test_word
        else:
            return 0, term

    @staticmethod
    def _contains_vowel(term: str) -> bool:
        """Return whether the given string contains a vowel"""
        return any(char in PorterStemmer.VOWELS for char in term)

    @staticmethod
    def _find_first_vowel(term: str) -> int:
        """Return index of first vowel found in the word, or -1
        if no vowel is found"""
        index = 0
        for char in term:
            if char in PorterStemmer.VOWELS:
                return index
            index += 1
        return -1
