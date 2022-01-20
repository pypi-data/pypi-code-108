import typing
from stefansearch.tokenizing.tokenizer import Tokenizer


class AlphanumericTokenizer(Tokenizer):
    """
    A simple tokenizer that splits on non-alphanumeric characters.

    Can optionally be configured to return lowercased-tokens via
    the `make_lower` argument.

    TODO: RESEARCH WHETHER LOWERCASING IS ACTUALLY EFFECTIVE.
      SEE: https://nlp.stanford.edu/IR-book/html/htmledition/capitalizationcase-folding-1.html
    """
    def __init__(self, lowercase: bool = False):
        self._make_lower = lowercase

    def tokenize_string(self, string: str) -> typing.Generator[str, None, None]:
        in_token = False
        token_start = None
        for i, char in enumerate(string):
            is_tokenizable = self._is_tokenizable(char)
            if is_tokenizable and not in_token:
                # Start of next token
                in_token = True
                token_start = i
            elif in_token and not is_tokenizable:
                # End of current token
                in_token = False
                yield string[token_start:i].lower() if self._make_lower else string[token_start:i]
        # Get potential final token
        if in_token:
            yield string[token_start:len(string)].lower() if self._make_lower else string[token_start:len(string)]

    @staticmethod
    def _is_tokenizable(char: str) -> bool:
        """
        Return whether a char meets the rules for being in a token.

        `char` must have length of one!
        """
        if len(char) != 1:
            raise ValueError('`char` must have length one')
        return (
            'a' <= char <= 'z' or
            'A' <= char <= 'Z' or
            '0' <= char <= '9'
        )
