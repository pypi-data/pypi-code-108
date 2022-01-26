"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
from pathlib import Path

# * Third Party Imports --------------------------------------------------------------------------------->
import pyparsing as pp

# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.gid_config.parser.tokens import TokenFactory

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class BaseIniGrammar:
    """
    Builds the pyparsing Grammar for the Parser.

    Args:
        key_value_separator (str, optional): The string that indicates the separation between a key and its value, gets also used for transforming back into text. Defaults to '='.
        comment_indicator (str, optional): String that indicates the start of a comment, gets also used for transforming back into text. Defaults to '#'.
        token_factory (TokenFactory, optional): Factory that transforms pyparsing results into tokens, gets set as `set_parse_action`s. Defaults to None.
    """
    l_sqr_bracket = pp.Literal("[").suppress()
    r_sqr_bracket = pp.Literal("]").suppress()

    section_name_excluded_chars = ['[', ']', '.']
    section_name_extra_chars = ['\t']

    key_name_exclusion_chars = ['[', ']', '.']
    key_name_extra_chars = [" "]

    value_exclusion_chars = [" "]
    value_extra_chars = [' ', '\t']
    base_chars = {"section": {"exclude": section_name_excluded_chars,
                              "extra": section_name_extra_chars},
                  "key": {"exclude": key_name_exclusion_chars,
                          "extra": key_name_extra_chars},
                  "value": {"exclude": value_exclusion_chars,
                            "extra": value_extra_chars}}

    def __init__(self,
                 key_value_separator: str = '=',
                 comment_indicator: str = '#',
                 token_factory: TokenFactory = None) -> None:
        self.token_factory = TokenFactory() if token_factory is None else token_factory
        self.raw_key_value_separator = key_value_separator
        self.key_value_separator = pp.Suppress(self.raw_key_value_separator)
        self.raw_comment_indicator = comment_indicator
        self.comment_indicator = pp.Suppress(self.raw_comment_indicator)

    def get_chars_for(self, kind: str) -> str:
        exclude = self.base_chars[kind]['exclude'] + [self.raw_key_value_separator, self.raw_comment_indicator]
        extra = self.base_chars[kind]['extra']
        return ''.join(char for char in pp.printables if char not in exclude) + ''.join(extra)

    @property
    def section_name(self) -> pp.ParserElement:
        section_name = pp.AtLineStart(self.l_sqr_bracket + pp.Word(self.get_chars_for('section')) + self.r_sqr_bracket)
        return section_name.set_results_name('section_name')

    @property
    def key(self) -> pp.ParserElement:
        key = pp.AtLineStart(pp.Word(init_chars=self.get_chars_for("key").replace('[', ''), body_chars=self.get_chars_for('key'))) + self.key_value_separator
        return key

    @property
    def value(self) -> pp.ParserElement:
        value = pp.OneOrMore(pp.Word(init_chars=self.get_chars_for("value").replace('[', ''), body_chars=self.get_chars_for('value')),
                             stop_on=self.key | self.section_name | self.comment).set_parse_action(''.join)

        return value

    @ property
    def entry(self) -> pp.ParserElement:
        entry = self.key + pp.Optional(self.value)
        return entry.set_results_name('entry')

    @ property
    def comment(self) -> pp.ParserElement:
        comment = self.comment_indicator + pp.rest_of_line
        return comment.set_results_name('comment')

    def get_grammar(self, **kwargs) -> pp.ParserElement:
        all_elements = pp.MatchFirst([self.section_name, self.entry, self.comment])
        # all_elements = self.section_name | self.entry | self.comment
        return all_elements.set_parse_action(self.token_factory.parse_action)


# region[Main_Exec]

if __name__ == '__main__':
    x = BaseIniGrammar()
    y = """[debug]

current_testing_channel = bot-testing




[this]

# a key comment
that = 40
something = blah
[sosos]

a_value_with_spaces = this is a test
"""
    print(list(x.get_grammar().scan_string(y)))

# endregion[Main_Exec]
