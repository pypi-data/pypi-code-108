"""NanamiLang Tokenizer Class"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)

import re
import datetime
from typing import List

from nanamilang.token import Token
from nanamilang.shortcuts import (
    ASSERT_IS_INSTANCE_OF,
    ASSERT_COLLECTION_IS_NOT_EMPTY,
    UNTERMINATED_STR,
    UNTERMINATED_SYMBOL, UNTERMINATED_SYMBOL_AT_EOF
)


class Tokenizer:
    """NanamiLang Tokenizer"""

    _integer_number_pattern: str = r'^-?\d+$'
    _identifier_name_pattern: str = r'^\D\S*$'
    _date_pattern: str = r'^\d{4}-\d{2}-\d{2}$'
    _bin_number_pattern: str = r'^[0-1]{8}$'
    _hex_number_pattern: str = r'^[a-f0-9]{8}$'
    _float_number_pattern: str = r'^-?\d+\.\d+$'
    _boolean_valid_values: list = ['true', 'false']

    _literal_characters: List[str] = [
        '!', '?', '$', '%',
        '*', '/', '+', '-', '=', '>', '<', '_', '.']

    _name: str
    _line_no: int = 1
    _char_no: int = 0
    _pointer: int = -1
    _source_view: List[str] = None

    def __init__(self,
                 name: str,
                 source: str) -> None:
        """
        Initialize a new NanamiLang Tokenizer instance

        :param source: your NanamiLang program source code
        """

        ASSERT_IS_INSTANCE_OF(name, str)
        ASSERT_COLLECTION_IS_NOT_EMPTY(name)

        self._name = name

        ASSERT_IS_INSTANCE_OF(source, str)
        ASSERT_COLLECTION_IS_NOT_EMPTY(source)

        self._source_view = list(source)

        # Finish initialization at casting source to a list

    def _increment_line_no_and_reset_char_no(self) -> None:
        """
        NanamiLang Tokenizer
        increment self._line_no && also reset self._char_no
        """

        self._char_no = 0
        self._line_no += 1

    def _move_pointer_next(self) -> None:
        """NanamiLang Tokenizer, increment self._pointer"""

        self._pointer += 1

    def _move_pointer_next_and_increment_char_no(self) -> None:
        """
        NanamiLang Tokenizer
        increment self._pointer, increment self._char_no as well
        """

        self._pointer += 1
        self._char_no += 1

    def tokenize(self) -> List[Token]:
        """NanamiLang Tokenizer, return a Token instances collection"""

        # First, initialize an empty tokens list
        tokenized: List[Token] = []

        # And do not forget to reset a pointer (cursor)
        self._pointer = -1

        # Collecting while we can move our pointer next
        while self._has_next_symbol():
            tokenized = tokenized + self._get_next_token_list()

        return tokenized or [Token(Token.Nil, 'nil')]

        # In case there are no tokens to return, just return [Token.Nil]

    def _hash_sym_started_literal_or_an_invalid_token(self,
                                                      literal: str) -> Token:
        """NanamiLang Tokenizer, return literal token or Token.Invalid"""

        # Store current position into a tuple
        position = (self._name, self._line_no, self._char_no)

        # Try to match a Date literal
        if re.match(self._date_pattern, literal):
            return Token(Token.Date,
                         datetime.datetime.fromisoformat(literal),
                         _position=position)
        # Try to match an IntegerNumber (2-base) literal
        if re.match(self._bin_number_pattern, literal):
            return Token(Token.IntegerNumber,
                         int(literal, base=2), _position=position)
        # Try to match an IntegerNumber (16-base) literal
        if re.match(self._hex_number_pattern, literal):
            return Token(Token.IntegerNumber,
                         int(literal, base=16), _position=position)

        return self._invalid_token_with_current_symbol('Unable to tokenize literal')

    def _literal_or_an_invalid_token(self, literal: str) -> Token:
        """NanamiLang Tokenizer, return literal token or Token.Invalid"""

        # Store current position into a tuple
        position = (self._name, self._line_no, self._char_no)

        # Try to match a FloatNumber literal
        if re.match(self._float_number_pattern, literal):
            return Token(
                Token.FloatNumber,
                float(literal), _position=position)
        # Try to match an IntegerNumber (10-base) literal
        if re.match(self._integer_number_pattern, literal):
            return Token(
                Token.IntegerNumber,
                int(literal, base=10), _position=position)
        # Try to match a Boolean literal
        if literal in self._boolean_valid_values:
            return Token(Token.Boolean,
                         literal == 'true', _position=position)
        # Try to match a Nil literal
        if literal == 'nil':
            return Token(Token.Nil, literal, _position=position)
        # Try to match an Identifier (may become Function, Macro or Undefined)
        if re.match(self._identifier_name_pattern, literal):
            return Token(Token.Identifier, literal, _position=position)

        return self._invalid_token_with_current_symbol('Unable to tokenize literal')

    def _invalid_token_with_current_symbol(self, reason: str) -> Token:
        """NanamiLang Tokenizer, a [Token(Token.Invalid) ...] list return shortcut"""

        return Token(
            Token.Invalid,
            _raw_symbol=self._curr_symbol(),
            _valid=False, _reason=reason, _position=(self._name, self._line_no, self._char_no))

    def _get_next_token_list(self) -> List[Token]:
        """NanamiLang Tokenizer, get next token list"""

        self._move_pointer_next_and_increment_char_no()

        # Here 'symbol(s)' and 'character(s)' match the same

        # END-LINE-COMMENT HANDLING ############################################################
        # If current symbol is ';' (semi-colon, a valid end-line-comment-start marker in a LISP)
        #   While has next symbol <------------------------------------------------------------|
        #     If next symbol is '\n' (new-line)                                                |
        #       Increment line-number counter && reset line-character-number counter           |
        #  <--- <break>                                                                        |
        #  |  Move pointer next                                                                |
        #  |  <continue> otherwise <-----------------------------------------------------------|
        #  |--> <return> an empty token list (and let the self.tokenize() meth handle emptiness)
        if self._curr_symbol_is(';'):
            while self._has_next_symbol():
                if self._next_symbol_is('\n'):
                    self._increment_line_no_and_reset_char_no()
                    break
                self._move_pointer_next()
            return []
        ########################################################################################
        # If current character is '(' ------------------------------> <return> [Token.ListBegin]
        if self._curr_symbol_is('('):
            return [Token(Token.ListBegin)]
        # If current character is '(' --------------------------------> <return> [Token.ListEnd]
        if self._curr_symbol_is(')'):
            return [Token(Token.ListEnd)]
        # If current character is '['
        #   <return> Vector start tokens list  [Token.ListBegin, Token.Identifier 'make-vector']
        if self._curr_symbol_is('['):
            return [Token(Token.ListBegin), Token(Token.Identifier, 'make-vector')]
        # If current character is ']' --------------------------------> <return> [Token.ListEnd]
        if self._curr_symbol_is(']'):
            return [Token(Token.ListEnd)]
        # If current character is '{'
        #   Return HashMap start tokens list  [Token.ListBegin, Token.Identifier 'make-hashmap']
        if self._curr_symbol_is('{'):
            return [Token(Token.ListBegin), Token(Token.Identifier, 'make-hashmap')]
        # If current character is '}' --------------------------------> <return> [Token.ListEnd]
        if self._curr_symbol_is('}'):
            return [Token(Token.ListEnd)]
        # INLINE-COMMENT (START) HANDLING       ################################################
        # HASH-SET (START) HANDLING             ################################################
        # HASH SYMBOL STARTED LITERALS HANDLING ################################################
        # If current symbol is '#' (hash)
        #   If has next symbol
        #     If next symbol is '_' (underscore)
        #       Move pointer next && increment line-character-number counter
        #       <return> ------------------------> [Token.ListBegin, Token.Identifier 'comment']
        #     If next symbol is '{' (opening-curly-bracket)
        #       Move pointer next && increment line-character-number counter
        #       <return> -------------------> [Token.ListBegin, Token.Identifier 'make-hashset']
        #     If next symbol is neither a separator ('\n', \'t', ' ') nor closing bracket symbol
        #       Initialize accumulative with an empty string
        #       While has next symbol <--------------------------------------------------------|
        #         If next symbol is neither a separator nor closing bracket                    |
        #           Append next symbol to accumulative                                         |
        #           Move pointer next and increment line-character-number counter              |
        #           <continue> <---------------------------------------------------------------|
        #     -> <break> otherwise
        #     < <return> _hash_sym_started_literal_or_an_invalid_token() dispatched tokens list
        #     Otherwise, <return> [Token.Invalid] with an "UNTERMINATED_SYMBOL('#')" error]
        #   Otherwise, <return> [Token.Invalid] with an "UNTERMINATED_SYMBOL_AT_EOF('#')" error]
        if self._curr_symbol_is('#'):
            if self._has_next_symbol():
                if self._next_symbol_is('_'):
                    self._move_pointer_next_and_increment_char_no()
                    return [Token(Token.ListBegin), Token(Token.Identifier, 'comment')]
                if self._next_symbol_is('{'):
                    self._move_pointer_next_and_increment_char_no()
                    return [Token(Token.ListBegin), Token(Token.Identifier, 'make-hashset')]
                if not self._next_sym_is_either_sep_or_closing_bracket():
                    accumulative = ''
                    while self._has_next_symbol():
                        if not self._next_sym_is_either_sep_or_closing_bracket():
                            accumulative += self._next_symbol()
                            self._move_pointer_next_and_increment_char_no()
                        else:
                            break
                    return [self._hash_sym_started_literal_or_an_invalid_token(accumulative)]
                return [self._invalid_token_with_current_symbol(UNTERMINATED_SYMBOL('#'))]
            return [self._invalid_token_with_current_symbol(UNTERMINATED_SYMBOL_AT_EOF('#'))]
        # STRING HANDLING ######################################################################
        # (handle separately from LITERAL (1 block bellow) to handle an unterminated string lit)
        # If current symbol is '"'         (double-quote, a valid string-start-marker in a LISP)
        #   If has next symbol
        #     Initialize value accumulator with empty string
        #     While has next symbol <----------------------------------------------------------|
        #       If next character isnt '"' (double-quote)                                      |
        #         Append next symbol to value accumulator                                      |
        #         Move pointer next && increment line-character-number-counter                 |
        #         <continue> <-----------------------------------------------------------------|
        #  <--- <break> otherwise
        #  ->| < check for unterminated string >
        #    | Move pointer next (to prevent errors)
        #    | <return> [Token.String <with-an-accumulated-string-value>] otherwise
        #   Otherwise, <return> [Token.Invalid containing UNTERMINATED_SYMBOL_AT_EOF('"') error]
        if self._curr_symbol_is('"'):
            if self._has_next_symbol():
                accumulative = ''
                while self._has_next_symbol():
                    if not self._next_symbol_is('"'):
                        accumulative += self._next_symbol()
                        self._move_pointer_next_and_increment_char_no()
                    else:
                        break
                # check for unterminated string ################################################
                if self._has_next_symbol():
                    if not self._next_symbol_is('"'):
                        return [self._invalid_token_with_current_symbol(UNTERMINATED_STR())]
                else:
                    if not self._curr_symbol_is('"'):
                        return [self._invalid_token_with_current_symbol(UNTERMINATED_STR())]
                ################################################################################
                self._move_pointer_next()
                return [Token(Token.String, accumulative)]
            return [self._invalid_token_with_current_symbol(UNTERMINATED_SYMBOL_AT_EOF('"'))]
        # KEYWORD HANDLING #####################################################################
        # (handle separately from LITERAL (1 block bellow) to handle an unterminated ':' symbol)
        # If current symbol is ':'               (colon, a valid keyword-start-marker in a LISP)
        #   If has next symbol
        #     If next symbol is valid literal character
        #       Initialize value accumulator with empty string
        #       While has next symbol <--------------------------------------------------------|
        #         If next symbol is valid literal character                                    |
        #           Append next symbol to value accumulator                                    |
        #           Move pointer next && increment line-character-number counter               |
        #           <continue> <---------------------------------------------------------------|
        #  <----- <break> otherwise
        #  ---> <return> [Token.Keyword <with-an-accumulated-keyword-value>]
        #     Otherwise, <return> [Token.Invalid] with am "UNTERMINATED_SYMBOL(':')" error]
        #   Otherwise, <return> [Token.Invalid] with am "UNTERMINATED_SYMBOL_AT_EOF(':')" error]
        if self._curr_symbol_is(':'):
            if self._has_next_symbol():
                if self._next_sym_is_a_lit_character():
                    accumulative = ''
                    while self._has_next_symbol():
                        if self._next_sym_is_a_lit_character():
                            accumulative += self._next_symbol()
                            self._move_pointer_next_and_increment_char_no()
                        else:
                            break
                    return [Token(Token.Keyword, accumulative)]
                return [self._invalid_token_with_current_symbol(UNTERMINATED_SYMBOL(':'))]
            return [self._invalid_token_with_current_symbol(UNTERMINATED_SYMBOL_AT_EOF(':'))]
        # SYMBOL HANDLING ######################################################################
        # (handle separately from LITERAL (1 block bellow) to handle an unterminated ''' symbol)
        # If current symbol is '''         (single-quote, a valid symbol-start-marker in a LISP)
        #   If has next symbol
        #     If next symbol is valid literal character
        #       Initialize value accumulator with empty string
        #       While has next symbol <--------------------------------------------------------|
        #         If next symbol is valid literal character                                    |
        #           Append next symbol to value accumulator                                    |
        #           Move pointer next && increment line-character-number counter               |
        #           <continue> <---------------------------------------------------------------|
        #  <----- <break> otherwise
        #  ---> <return> [Token.Symbol <with-an-accumulated-keyword-value>]
        #     Otherwise, <return> [Token.Invalid] with am "UNTERMINATED_SYMBOL(''')" error]
        #   Otherwise, <return> [Token.Invalid] with am "UNTERMINATED_SYMBOL_AT_EOF(''')" error]
        if self._curr_symbol_is('\''):
            if self._has_next_symbol():
                if self._next_sym_is_a_lit_character():
                    accumulative = ''
                    while self._has_next_symbol():
                        if self._next_sym_is_a_lit_character():
                            accumulative += self._next_symbol()
                            self._move_pointer_next_and_increment_char_no()
                        else:
                            break
                    return [Token(Token.Symbol, accumulative)]
                return [self._invalid_token_with_current_symbol(UNTERMINATED_SYMBOL('\''))]
            return [self._invalid_token_with_current_symbol(UNTERMINATED_SYMBOL_AT_EOF('\''))]
        # LITERAL HANDLING #####################################################################
        # If current symbol is valid literal character
        #   Initialize value accumulator with current symbol
        #   While has next symbol <------------------------------------------------------------|
        #     If next symbol is valid literal character                                        |
        #       Append next symbol to value accumulator                                        |
        #       Move pointer next && increment line-character-number counter                   |
        #       <continue> <-------------------------------------------------------------------|
        # <-- <break> otherwise
        # > <return> literal token (_literal_or_an_invalid_token) (could return a Invalid token)
        if self._curr_sym_is_a_lit_character():
            accumulative = self._curr_symbol()
            while self._has_next_symbol():
                if self._next_sym_is_a_lit_character():
                    accumulative += self._next_symbol()
                    self._move_pointer_next_and_increment_char_no()
                else:
                    break
            return [self._literal_or_an_invalid_token(accumulative)]
        # SPECIAL CHARACTERS HANDLING ##########################################################
        # If current symbol is '\n' (new-line), ' ' (space) or '\t' (tabulate)
        #   If current symbol is '\n' (new-line)
        #     Reset line-character-number counter, increment line-number counter
        #   <return> an empty tokens list (and let the self.tokenize(...) meth handle emptiness)
        if self._curr_sym_in([' ', '\t', '\n']):
            if self._curr_symbol_is('\n'):
                self._increment_line_no_and_reset_char_no()
            return []
        # If we do not know what the current symbol is, just return a [Token.Invalid] list
        return [self._invalid_token_with_current_symbol('Has encountered an unknown character')]
        ########################################################################################

    def _next_symbol(self) -> str:
        """NanamiLang Tokenizer, return the source view next symbol"""

        return self._source_view[self._pointer + 1]

    def _curr_symbol(self) -> str:
        """NanamiLang Tokenizer, return the source view current symbol"""

        return self._source_view[self._pointer]

    def _next_symbol_is(self, c: str) -> bool:
        """NanamiLang Tokenizer, does the source view next symbol is"""

        return self._source_view[self._pointer + 1] == c

    def _curr_symbol_is(self, c: str) -> bool:
        """NanamiLang Tokenizer, does the source view current symbol is"""

        return self._source_view[self._pointer] == c

    def _has_next_symbol(self) -> bool:
        """NanamiLang Tokenizer, does the source view have a next symbol?"""

        return self._pointer + 1 < len(self._source_view)

    def _next_sym_in(self, collection: List[str]) -> bool:
        """NanamiLang Tokenizer, does the next source view symbol in...?"""

        return self._next_symbol() in collection

    def _curr_sym_in(self, collection: List[str]) -> bool:
        """NanamiLang Tokenizer, does the next source view in ...?"""

        return self._curr_symbol() in collection

    def _next_sym_matches_with(self, sym_pattern: str) -> bool:
        """NanamiLang Tokenizer, does the next source view symbol match with ...?"""

        return bool(re.match(sym_pattern, self._next_symbol()))

    def _curr_sym_matches_with(self, sym_pattern: str) -> bool:
        """NanamiLang Tokenizer, does the current source view symbol match with ...?"""

        return bool(re.match(sym_pattern, self._curr_symbol()))

    def _next_sym_is_a_lit_character(self) -> bool:
        """NanamiLang Tokenizer, is the next source view symbol a valid literal character?"""

        return self._next_sym_matches_with(r'[a-zA-Z0-9]') or self._next_sym_in(self._literal_characters)

    def _curr_sym_is_a_lit_character(self) -> bool:
        """NanamiLang Tokenizer, is the current source view symbol a valid literal character?"""

        return self._curr_sym_matches_with(r'[a-zA-Z0-9]') or self._curr_sym_in(self._literal_characters)

    def _next_sym_is_either_sep_or_closing_bracket(self) -> bool:
        """NanamiLang Tokenizer, whether the next symbol is either separator or a closing bracket or not?"""

        return self._next_sym_in([' ', '\t', '\n', ')', ']', '}'])

    def _curr_sym_is_either_sep_or_closing_bracket(self) -> bool:
        """NanamiLang Tokenizer, whether the current symbol is either separator or a closing bracket or not """
        return self._curr_sym_in([' ', '\t', '\n', ')', ']', '}'])
