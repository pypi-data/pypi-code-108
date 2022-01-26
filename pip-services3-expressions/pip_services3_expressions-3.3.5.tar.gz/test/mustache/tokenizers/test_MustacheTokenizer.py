# -*- coding: utf-8 -*-
from pip_services3_expressions.mustache.tokenizers.MustacheTokenizer import MustacheTokenizer
from pip_services3_expressions.tokenizers.Token import Token
from pip_services3_expressions.tokenizers.TokenType import TokenType
from test.tokenizers.TokenizerFixture import TokenizerFixture


class TestMustacheTokenizer:

    def test_template_1(self):
        token_string = "Hello, {{ Name }}!"
        expected_tokens = [
            Token(TokenType.Special, "Hello, ", 0, 0),
            Token(TokenType.Symbol, "{{", 0, 0),
            Token(TokenType.Whitespace, " ", 0, 0),
            Token(TokenType.Word, "Name", 0, 0),
            Token(TokenType.Whitespace, " ", 0, 0),
            Token(TokenType.Symbol, "}}", 0, 0),
            Token(TokenType.Special, "!", 0, 0),
        ]

        tokenizer = MustacheTokenizer()
        tokenizer.skip_eof = True
        token_list = tokenizer.tokenize_buffer(token_string)

        TokenizerFixture.assert_are_equals_token_lists(expected_tokens, token_list)

    def test_template_2(self):
        token_string = "Hello, {{{ Name }}}!"
        expected_tokens = [
            Token(TokenType.Special, "Hello, ", 0, 0),
            Token(TokenType.Symbol, "{{{", 0, 0),
            Token(TokenType.Whitespace, " ", 0, 0),
            Token(TokenType.Word, "Name", 0, 0),
            Token(TokenType.Whitespace, " ", 0, 0),
            Token(TokenType.Symbol, "}}}", 0, 0),
            Token(TokenType.Special, "!", 0, 0),
        ]

        tokenizer = MustacheTokenizer()
        tokenizer.skip_eof = True
        token_list = tokenizer.tokenize_buffer(token_string)

        TokenizerFixture.assert_are_equals_token_lists(expected_tokens, token_list)

    def test_template_3(self):
        token_string = "{{ Name }}}"
        expected_tokens = [
            Token(TokenType.Symbol, "{{", 0, 0),
            Token(TokenType.Whitespace, " ", 0, 0),
            Token(TokenType.Word, "Name", 0, 0),
            Token(TokenType.Whitespace, " ", 0, 0),
            Token(TokenType.Symbol, "}}}", 0, 0)
        ]

        tokenizer = MustacheTokenizer()
        tokenizer.skip_eof = True
        token_list = tokenizer.tokenize_buffer(token_string)

        TokenizerFixture.assert_are_equals_token_lists(expected_tokens, token_list)

    def test_template_4(self):
        token_string = "Hello, World!"
        expected_tokens = [
            Token(TokenType.Special, "Hello, World!", 0, 0)
        ]

        tokenizer = MustacheTokenizer()
        tokenizer.skip_eof = True
        token_list = tokenizer.tokenize_buffer(token_string)

        TokenizerFixture.assert_are_equals_token_lists(expected_tokens, token_list)
