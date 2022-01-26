# -*- coding: utf-8 -*-

from pip_services3_expressions.io.IScanner import IScanner
from pip_services3_expressions.tokenizers.ITokenizer import ITokenizer
from pip_services3_expressions.tokenizers.Token import Token
from pip_services3_expressions.tokenizers.TokenType import TokenType
from pip_services3_expressions.tokenizers.generic.GenericCommentState import GenericCommentState
from pip_services3_expressions.tokenizers.utilities.CharValidator import CharValidator


class CppCommentState(GenericCommentState):
    """
    This state will either delegate to a comment-handling state, or return a token with just a slash in it.
    """

    def __init__(self):
        super(CppCommentState, self).__init__()
        self.STAR = ord('*')
        self.SLASH = ord('/')

    def get_multi_line_comment(self, scanner: IScanner) -> str:
        """
        Ignore everything up to a closing star and slash, and then return the tokenizer's next token.

        :param scanner:
        """
        result = ''
        last_symbol = 0
        next_symbol = scanner.read()

        while not CharValidator.is_eof(next_symbol):
            result += chr(next_symbol)
            if last_symbol == self.STAR and next_symbol == self.SLASH:
                break
            last_symbol = next_symbol
            next_symbol = scanner.read()
        return result

    def get_single_line_comment(self, scanner: IScanner) -> str:
        """
        Ignore everything up to an end-of-line and return the tokenizer's next token.
        """
        result = ''
        next_symbol = scanner.read()

        while not CharValidator.is_eof(next_symbol) and not CharValidator.is_eol(next_symbol):
            result = result + chr(next_symbol)
            next_symbol = scanner.read()

        if CharValidator.is_eol(next_symbol):
            scanner.unread()

        return result

    def next_token(self, scanner: IScanner, tokenizer: ITokenizer) -> Token:
        """
        Either delegate to a comment-handling state, or return a token with just a slash in it.
        
        :param scanner: A textual string to be tokenized.
        :param tokenizer: A tokenizer class that controls the process.
        :return: The next token from the top of the stream.
        """
        first_symbol = scanner.read()
        line = scanner.peek_line()
        column = scanner.peek_column()
        if first_symbol != self.SLASH:
            scanner.unread()
            raise Exception('Incorrect usage of CppCommentState.')

        second_symbol = scanner.read()
        if second_symbol == self.STAR:
            return Token(TokenType.Comment, '/*' + self.get_multi_line_comment(scanner), line, column)
        elif second_symbol == self.SLASH:
            return Token(TokenType.Comment, '//' + self.get_single_line_comment(scanner), line, column)
        else:
            if not CharValidator.is_eof(second_symbol):
                scanner.unread()
            if not CharValidator.is_eof(first_symbol):
                scanner.unread()
            return tokenizer.symbol_state.next_token(scanner, tokenizer)
