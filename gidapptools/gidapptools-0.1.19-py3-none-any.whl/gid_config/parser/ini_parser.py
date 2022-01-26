"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import re
from pathlib import Path

# * Third Party Imports --------------------------------------------------------------------------------->
import pyparsing as pp

# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.errors import EmptyConfigTextError, TrailingCommentError
from gidapptools.gid_config.parser.tokens import Entry, Token, Comment, Section, TokenFactory
from gidapptools.gid_config.parser.grammar import BaseIniGrammar

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class BaseIniParser:
    """
    Parser for text in `ini` format.

    Keeps normal comments, but strips inline comments. Can handle multiline values as long as they are indented. Orphaned Entries (Entries under no section) are not allowed.

    Args:
        grammar_class (BaseIniGrammar, optional): Grammar item to use, must implement the method `get_grammar`. Defaults to `BaseIniGrammar`.
        token_factory (TokenFactory, optional): Factory that transforms pyparsing results into tokens, gets directly passed to the grammar_class. Defaults to `TokenFactory`.
        key_value_separator (str, optional): The string that indicates the separation between a key and its value, gets also used for transforming back into text. Defaults to '='.
        comment_indicator (str, optional): String that indicates the start of a comment, gets also used for transforming back into text. Defaults to '#'.
        remove_all_comments (bool, optional): If the parser should remove all comments and not just inline comments in the preprocessing step. Defaults to False.

    """
    all_comment_regex_pattern = r'[ \t]*{comment_indicator}.*'
    inline_comment_regex_pattern = r"(?<=\w)[ \t]*{comment_indicator}[ \t\w]+"

    def __init__(self,
                 grammar_class: BaseIniGrammar = BaseIniGrammar,
                 token_factory: TokenFactory = None,
                 key_value_separator: str = '=',
                 comment_indicator: str = '#',
                 remove_all_comments: bool = False) -> None:

        self.comment_indicator = comment_indicator
        self.key_value_separator = key_value_separator
        self.grammar_item = grammar_class(key_value_separator=self.key_value_separator, comment_indicator=self.comment_indicator, token_factory=token_factory)
        self.remove_all_comments = remove_all_comments
        self.all_comment_regex = re.compile(self.all_comment_regex_pattern.format(comment_indicator=self.comment_indicator))
        self.inline_comment_regex = re.compile(self.inline_comment_regex_pattern.format(comment_indicator=self.comment_indicator))
        self.grammar: pp.ParserElement = None

    def _preprocess_comments(self, text: str) -> str:
        strip_regex = self.all_comment_regex if self.remove_all_comments is True else self.inline_comment_regex
        return strip_regex.sub('', text)

    def _verify(self, text: str) -> str:
        check_text = text.strip()

        if check_text == '':

            raise EmptyConfigTextError('Config text cannot be empty.')

        if check_text.splitlines()[-1].strip().startswith(self.comment_indicator):

            raise TrailingCommentError(f'Trailing comments are not allowed with {self.__class__.__name__!r}.')
        return text

    def _pre_process(self, text: str) -> str:
        text = self._preprocess_comments(text)
        text = self._verify(text)
        return text

    def _parse(self, text: str) -> list[Token]:
        temp_comments = []
        last_section = None
        data = []

        def _add_comments_to_token(token) -> None:
            nonlocal temp_comments
            if temp_comments:
                token.comments += temp_comments
                temp_comments.clear()

        def _process_section(token) -> None:
            nonlocal last_section
            _add_comments_to_token(token)
            last_section = token
            data.append(token)

        def _process_entry(token) -> None:
            _add_comments_to_token(token)
            token.key_value_separator = self.key_value_separator
            last_section.add_entry(token)

        def _process_comment(token) -> None:
            nonlocal temp_comments
            token.comment_indicator = self.comment_indicator
            temp_comments.append(token)

        process_table = {Section: _process_section,
                         Entry: _process_entry,
                         Comment: _process_comment}

        for tokens in self.grammar.search_string(text):

            for _token in tokens:

                processor = process_table[type(_token)]
                processor(_token)
        return data

    def parse(self, text: str, **kwargs) -> list[Section]:
        """
        Parses the text into a list of Sections containing the comments and Entries.

        `grammar` is created lazily at this point.

        Args:
            text (str): Text to parse, must be in `ini` format.

        Returns:
            list[Section]: A list of Section, each Section contains the comments for the Section and the Entries.
        """
        if self.grammar is None:
            self.grammar = self.grammar_item.get_grammar(**kwargs)
        text = self._pre_process(text)

        return self._parse(text)


# region[Main_Exec]


if __name__ == '__main__':
    pass
# endregion[Main_Exec]
