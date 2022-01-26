# -*- coding: utf-8 -*-

from abc import ABC
from typing import List

from pip_services3_expressions.io.IScanner import IScanner
from . import ICommentState
from .INumberState import INumberState
from .IQuoteState import IQuoteState
from .ISymbolState import ISymbolState
from .IWhitespaceState import IWhitespaceState
from .IWordState import IWordState
from .Token import Token


class ITokenizer(ABC):
    """
    A tokenizer divides a string into tokens. This class is highly customizable with regard
    to exactly how this division occurs, but it also has defaults that are suitable for many
    languages. This class assumes that the character values read from the string lie in
    the range 0-255. For example, the Unicode value of a capital A is 65,
    so  **chr(65)** prints out a capital A.

    The behavior of a tokenizer depends on its character state table. This table is an array
    of 256 :class:`TokenizerState <pip_services3_expressions.tokenizers.ITokenizerState.ITokenizerState>` states. The state table decides which state to enter
    upon reading a character from the input string.

    For example, by default, upon reading an 'A', a tokenizer will enter a "word" state.
    This means the tokenizer will ask a :class:`WordState <pip_services3_expressions.tokenizers.IWordState.IWordState>` object to consume the 'A',
    along with the characters after the 'A' that form a word. The state's responsibility
    is to consume characters and return a complete token.

    The default table sets a SymbolState for every character from 0 to 255,
    and then overrides this with:

    .. list-table::
        :header-rows: 1
        :widths: 10, 10, 25

        * - From
          - To
          - State

        * - 0
          - ' '
          - whitespaceState
        * - 'a',    
          - 'z'
          - wordState
        * - 'A'
          - 'Z'
          - wordState
        * - 160
          - 255
          - wordState
        * - '0'
          - '9'
          - numberState
        * - '-'
          - '-'
          - numberState
        * - '.'
          - '.'
          - numberState
        * - '"'
          - '"'
          - quoteState
        * - '\''
          - '\''
          - quoteState
        * - '/'
          - '/'
          - slashState

    In addition to allowing modification of the state table, this class makes each of the states
    above available. Some of these states are customizable. For example, wordState allows customization
    of what characters can be part of a word, after the first character.
    """

    # Skip unknown characters
    skip_unknown: bool

    # Skips whitespaces.
    skip_whitespaces: bool

    # Skips comments.
    skip_comments: bool

    # Skips End-Of-File token at the end of stream.
    skip_eof: bool

    # Merges whitespaces.
    merge_whitespaces: bool

    # Unifies numbers: "Integers" and "Floats" makes just "Numbers"
    unify_numbers: bool

    # Decodes quoted strings.
    decode_strings: bool

    # A token state to process comments.
    comment_state: ICommentState

    #  A token state to process numbers.
    number_state: INumberState

    # A token state to process quoted strings.
    quote_state: IQuoteState

    # A token state to process symbols (single like "=" or multi-character like "<>")
    symbol_state: ISymbolState

    # A token state to process white space delimiters.
    whitespace_state: IWhitespaceState

    # A token state to process words or indentificators.
    word_state: IWordState

    # The stream scanner to tokenize.
    scanner: IScanner

    def has_next_token(self) -> bool:
        """
        Checks if there is the next token exist.

        :return: **True** if scanner has the next token.
        """

    def next_token(self) -> Token:
        """
        Gets the next token from the scanner.

        :return: Next token of **null** if there are no more tokens left.
        """

    def tokenize_stream(self, scanner: IScanner) -> List[Token]:
        """
        Tokenizes a textual stream into a list of token structures.

        :param scanner: A textual stream to be tokenized.
        :return: A list of token structures.
        """

    def tokenize_buffer(self, buffer: str) -> List[Token]:
        """
        Tokenizes a string buffer into a list of tokens structures.

        :param buffer: A string buffer to be tokenized.
        :return: A list of token structures.
        """

    def tokenize_stream_to_string(self, scanner: IScanner) -> List[str]:
        """
        Tokenizes a textual stream into a list of strings.

        :param scanner: A textual stream to be tokenized.
        :return: A list of token strings.
        """

    def tokenize_buffer_to_strings(self, buffer: str) -> List[str]:
        """
        Tokenizes a string buffer into a list of strings.
        
        :param buffer: A string buffer to be tokenized.
        :return: A list of token strings.
        """
