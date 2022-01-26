# -*- coding: utf-8 -*-
from pip_services3_expressions.io.IScanner import IScanner
from pip_services3_expressions.tokenizers.ITokenizer import ITokenizer
from pip_services3_expressions.tokenizers.Token import Token
from pip_services3_expressions.tokenizers.TokenType import TokenType
from pip_services3_expressions.tokenizers.generic.CppCommentState import CppCommentState
from pip_services3_expressions.tokenizers.utilities.CharValidator import CharValidator


class CCommentState(CppCommentState):
    """
    This state will either delegate to a comment-handling state, or return a token with just a slash in it.
    """

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
            raise Exception('Incorrect usage of CCommentState.')

        second_symbol = scanner.read()
        if second_symbol == self.STAR:
            return Token(TokenType.Comment, '/*' + self.get_multi_line_comment(scanner), line, column)
        else:
            if not CharValidator.is_eof(second_symbol):
                scanner.unread()

            if not CharValidator.is_eof(first_symbol):
                scanner.unread()

            return tokenizer.symbol_state.next_token(scanner, tokenizer)
