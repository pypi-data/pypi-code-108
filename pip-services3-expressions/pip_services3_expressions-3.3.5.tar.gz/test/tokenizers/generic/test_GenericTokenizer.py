# -*- coding: utf-8 -*-

from pip_services3_expressions.tokenizers.Token import Token
from pip_services3_expressions.tokenizers.TokenType import TokenType
from pip_services3_expressions.tokenizers.generic.GenericTokenizer import GenericTokenizer
from test.tokenizers.TokenizerFixture import TokenizerFixture


class TestGenericTokenizer:

    def test_expressions(self):
        token_string = 'A+B/123 - \t "xyz"\n <>-10.11# This is a comment'
        expected_tokens = [
            Token(TokenType.Word, 'A', 0, 0),
            Token(TokenType.Symbol, "+", 0, 0),
            Token(TokenType.Word, "B", 0, 0),
            Token(TokenType.Symbol, "/", 0, 0),
            Token(TokenType.Integer, "123", 0, 0),
            Token(TokenType.Whitespace, " ", 0, 0),
            Token(TokenType.Symbol, "-", 0, 0),
            Token(TokenType.Whitespace, " \t ", 0, 0),
            Token(TokenType.Quoted, '"xyz"', 0, 0),
            Token(TokenType.Whitespace, "\n ", 0, 0),
            Token(TokenType.Symbol, "<>", 0, 0),
            Token(TokenType.Float, "-10.11", 0, 0),
            Token(TokenType.Comment, "# This is a comment", 0, 0),
            Token(TokenType.Eof, None, 0, 0)
        ]
        tokenizer = GenericTokenizer()
        token_list = tokenizer.tokenize_buffer(token_string)

        TokenizerFixture.assert_are_equals_token_lists(expected_tokens, token_list)

    def test_word_token(self):
        token_string = 'A"xyz"Ebf_2\n2x_2'
        expected_tokens = [
            Token(TokenType.Word, "A", 0, 0),
            Token(TokenType.Quoted, "xyz", 0, 0),
            Token(TokenType.Word, "Ebf_2", 0, 0),
            Token(TokenType.Whitespace, "\n", 0, 0),
            Token(TokenType.Integer, "2", 0, 0),
            Token(TokenType.Word, "x_2", 0, 0)
        ]
        tokenizer = GenericTokenizer()
        tokenizer.skip_eof = True
        tokenizer.decode_strings = True
        token_list = tokenizer.tokenize_buffer(token_string)

        TokenizerFixture.assert_are_equals_token_lists(expected_tokens, token_list)

    def test_number_token(self):
        token_string = "123-321 .543-.76-. -123.456"
        expected_tokens = [
            Token(TokenType.Integer, "123", 0, 0),
            Token(TokenType.Integer, "-321", 0, 0),
            Token(TokenType.Whitespace, " ", 0, 0),
            Token(TokenType.Float, ".543", 0, 0),
            Token(TokenType.Float, "-.76", 0, 0),
            Token(TokenType.Symbol, "-", 0, 0),
            Token(TokenType.Symbol, ".", 0, 0),
            Token(TokenType.Whitespace, " ", 0, 0),
            Token(TokenType.Float, "-123.456", 0, 0)
        ]
        tokenizer = GenericTokenizer()
        tokenizer.skip_eof = True
        tokenizer.decode_strings = True
        token_list = tokenizer.tokenize_buffer(token_string)

        TokenizerFixture.assert_are_equals_token_lists(expected_tokens, token_list)

    def test_expression_token(self):
        token_string = "A + b / (3 - Max(-123, 1)*2)"

        tokenizer = GenericTokenizer()
        token_list = tokenizer.tokenize_buffer(token_string)

        assert 24 == len(token_list)

    def test_expression_token2(self):
        token_string = "1>2"
        expected_tokens = [
            Token(TokenType.Integer, "1", 0, 0),
            Token(TokenType.Symbol, ">", 0, 0),
            Token(TokenType.Integer, "2", 0, 0),
        ]

        tokenizer = GenericTokenizer()
        tokenizer.skip_eof = True
        token_list = tokenizer.tokenize_buffer(token_string)

        TokenizerFixture.assert_are_equals_token_lists(expected_tokens, token_list)
