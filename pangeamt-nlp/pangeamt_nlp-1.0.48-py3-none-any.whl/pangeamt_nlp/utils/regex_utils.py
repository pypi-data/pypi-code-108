# Based on package regexutils (https://github.com/Pangeamt/regexutils/)

from regex import regex

class SingleWordRegexBuilder:
    """Creates regexes which can be used to match individual words
    Contains functionality for the creation of disjunctive regexes: regexes which consist of a series of or-options
        Useful for example when creating a regex which matches any of a list of words (e.g. all countries in the world)
    """

    def __init__(self, word_sep_tokens=r"([\p{P}\s])"):
        """Take care to define the possible separators a valid regex between square brackets
            (making them separate options), as in the standard value"""
        self._possibilities = []
        self.separators = word_sep_tokens

    def build(self):
        """Returns the total regex, ensuring it only matches words and not subwords ("Hi" will match
        string "I say Hi" but not "I say Hiii" or "I say aHi"""
        if len(self._possibilities) == 0:
            return ""
        regex_start = "(?<=^|" + self.separators + ")(" #look behind
        regex_end = ")(?=" + self.separators + "|$)" #Look ahead: any punctuation after the match is not consumed
        if len(self._possibilities) == 1:
            return regex_start + self._possibilities[0] + regex_end
        res = regex_start
        for i in range(0, len(self._possibilities)-1):
            pos = self._possibilities[i]
            res += "(" + pos + ")" + "|"
        res += "(" + self._possibilities[-1] + ")" + regex_end
        return res

    def build_as_part(self):
        """Returns the total regex as is, without taking into account whether or not it starts at the beginning
        of a word and ends at the end of a word"""
        if len(self._possibilities) == 0:
            return ""
        if len(self._possibilities) == 1:
            return self._possibilities[0]
        res = "("
        for i in range(0, len(self._possibilities)-1):
            pos = self._possibilities[i]
            res += pos + "|"
        res += "(" + self._possibilities[-1] + "))"
        return res

    def add_option(self, new_regex):
        self._possibilities.append(new_regex)

    def add_list_options_as_regex(self, options):
        to_add = self.gen_list_options_as_regex(options)
        self._possibilities.append(to_add)

    @staticmethod
    def gen_list_options_as_regex(options):
        res = r"("
        first = True
        for option in options:
            if not first:
                res += "|"
            res = res + option
            first = False
        res += ")"
        return res


class RegexMatcher:
    """Class which stores a compiled regex and which can apply it to text and return a list of matches
    Extend this class to create specific classes which implement a regex
    The implementing subclass should pass its regex to this class's constructor (using super)
    It can be applied to a text by using the match method"""

    def __init__(self, matcher_regex):
        """matcher_regex must be a compiled regex"""
        self.matcher_regex = matcher_regex

    def match(self, text):
        """Applies a regex and returns a list of matches"""
        res_iter = self.matcher_regex.finditer(text)
        res = []
        for elem in res_iter:
            res.append(elem)
        return res

