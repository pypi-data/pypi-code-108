# -*- coding: utf-8 -*-
from pip_services3_expressions.io.IScanner import IScanner
from pip_services3_expressions.tokenizers.ITokenizer import ITokenizer
from pip_services3_expressions.tokenizers.IWordState import IWordState
from pip_services3_expressions.tokenizers.Token import Token
from pip_services3_expressions.tokenizers.TokenType import TokenType
from pip_services3_expressions.tokenizers.utilities.CharReferenceMap import CharReferenceMap
from pip_services3_expressions.tokenizers.utilities.CharValidator import CharValidator


class GenericWordState(IWordState):
    """
    A wordState returns a word from a scanner. Like other states, a tokenizer transfers the job
    of reading to this state, depending on an initial character. Thus, the tokenizer decides
    which characters may begin a word, and this state determines which characters may appear
    as a second or later character in a word. These are typically different sets of characters;
    in particular, it is typical for digits to appear as parts of a word, but not
    as the initial character of a word.

    By default, the following characters may appear in a word.
    The method :func:`set_word_chars` allows customizing this.

    .. list-table::
        :header-rows: 1
        :widths: 10, 10

        * - From
          - To

        * - 'a'
          - 'z'
        * - 'A'
          - 'Z'
        * - '0'
          - '9'
    
    as well as: minus sign, underscore, and apostrophe.
    """

    def __init__(self):
        """
        Constructs a word state with a default idea of what characters
        are admissible inside a word (as described in the class comment).
        """
        self.__map = CharReferenceMap()
        self.set_word_chars(ord('a'), ord('z'), True)
        self.set_word_chars(ord('A'), ord('Z'), True)
        self.set_word_chars(ord('0'), ord('9'), True)
        self.set_word_chars(ord('-'), ord('-'), True)
        self.set_word_chars(ord('_'), ord('_'), True)
        self.set_word_chars(0x00c0, 0x00ff, True)
        self.set_word_chars(0x0100, 0xfffe, True)

    def next_token(self, scanner: IScanner, tokenizer: ITokenizer) -> Token:
        """
        Ignore word (such as blanks and tabs), and return the tokenizer's next token.
        
        :param scanner: A textual string to be tokenized.
        :param tokenizer: A tokenizer class that controls the process.
        :return: The next token from the top of the stream.
        """
        line = scanner.peek_line()
        column = scanner.peek_column()
        token_value = ''
        next_symbol = scanner.read()

        while self.__map.lookup(next_symbol):
            token_value = token_value + chr(next_symbol)
            next_symbol = scanner.read()

        if not CharValidator.is_eof(next_symbol):
            scanner.unread()

        return Token(TokenType.Word, token_value, line, column)

    def set_word_chars(self, from_symbol: int, to_symbol: int, enable: bool):
        """
        Establish characters in the given range as valid characters for part of a word after
        the first character. Note that the tokenizer must determine which characters are valid
        as the beginning character of a word.

        :param from_symbol: First character index of the interval.
        :param to_symbol: Last character index of the interval.
        :param enable: **True** if this state should use characters in the given range.
        """
        self.__map.add_interval(from_symbol, to_symbol, enable)

    def clear_word_chars(self):
        """
        Clears definitions of word chars.
        """
        self.__map.clear()
