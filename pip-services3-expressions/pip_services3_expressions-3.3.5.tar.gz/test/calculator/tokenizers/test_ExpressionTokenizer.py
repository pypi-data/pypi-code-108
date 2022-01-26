# -*- coding: utf-8 -*-

from pip_services3_expressions.calculator.tokenizers.ExpressionTokenizer import ExpressionTokenizer
from pip_services3_expressions.tokenizers.Token import Token
from pip_services3_expressions.tokenizers.TokenType import TokenType

from test.tokenizers.TokenizerFixture import TokenizerFixture


class TestExpressionTokenizer:
    def tests_quote_token(self):
        token_string = "A'xyz'\"abc\ndeg\" 'jkl\"def'\"ab\"\"de\"'df''er'"
        expected_tokens = [
            Token(TokenType.Word, "A", 0, 0), Token(TokenType.Quoted, "xyz", 0, 0),
            Token(TokenType.Word, "abc\ndeg", 0, 0), Token(TokenType.Whitespace, " ", 0, 0),
            Token(TokenType.Quoted, "jkl\"def", 0, 0), Token(TokenType.Word, "ab\"de", 0, 0),
            Token(TokenType.Quoted, "df'er", 0, 0)
        ]

        tokenizer = ExpressionTokenizer()
        tokenizer.skip_eof = True
        tokenizer.decode_strings = True
        token_list = tokenizer.tokenize_buffer(token_string)

        TokenizerFixture.assert_are_equals_token_lists(expected_tokens, token_list)

    def test_word_token(self):
        token_string = "A'xyz'Ebf_2\n2_2"
        expected_tokens = [Token(TokenType.Word, "A", 0, 0), Token(TokenType.Quoted, "xyz", 0, 0),
                           Token(TokenType.Word, "Ebf_2", 0, 0), Token(TokenType.Whitespace, "\n", 0, 0),
                           Token(TokenType.Integer, "2", 0, 0), Token(TokenType.Word, "_2", 0, 0)]
        tokenizer = ExpressionTokenizer()
        tokenizer.skip_eof = True
        tokenizer.decode_strings = True
        token_list = tokenizer.tokenize_buffer(token_string)

        TokenizerFixture.assert_are_equals_token_lists(expected_tokens, token_list)

    def test_number_token(self):
        token_string = "123-321 .543-.76-. 123.456 123e45 543.11E+43 1e 3E-"
        expected_tokens = [
            Token(TokenType.Integer, "123", 0, 0), Token(TokenType.Symbol, "-", 0, 0),
            Token(TokenType.Integer, "321", 0, 0), Token(TokenType.Whitespace, " ", 0, 0),
            Token(TokenType.Float, ".543", 0, 0), Token(TokenType.Symbol, "-", 0, 0),
            Token(TokenType.Float, ".76", 0, 0), Token(TokenType.Symbol, "-", 0, 0),
            Token(TokenType.Symbol, ".", 0, 0), Token(TokenType.Whitespace, " ", 0, 0),
            Token(TokenType.Float, "123.456", 0, 0), Token(TokenType.Whitespace, " ", 0, 0),
            Token(TokenType.Float, "123e45", 0, 0), Token(TokenType.Whitespace, " ", 0, 0),
            Token(TokenType.Float, "543.11E+43", 0, 0), Token(TokenType.Whitespace, " ", 0, 0),
            Token(TokenType.Integer, "1", 0, 0), Token(TokenType.Word, "e", 0, 0),
            Token(TokenType.Whitespace, " ", 0, 0), Token(TokenType.Integer, "3", 0, 0),
            Token(TokenType.Word, "E", 0, 0), Token(TokenType.Symbol, "-", 0, 0)
        ]

        tokenizer = ExpressionTokenizer()
        tokenizer.skip_eof = True
        tokenizer.decode_strings = True
        token_list = tokenizer.tokenize_buffer(token_string)

        TokenizerFixture.assert_are_equals_token_lists(expected_tokens, token_list)

    def test_expression_token(self):
        token_string = "A + b / (3 - Max(-123, 1)*2)"

        tokenizer = ExpressionTokenizer()
        token_list = tokenizer.tokenize_buffer(token_string)

        assert 25 == len(token_list)
