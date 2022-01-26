# -*- coding: utf-8 -*-

from pip_services3_expressions.tokenizers.utilities.CharValidator import CharValidator


class TestCharValidator:

    def test_is_eof(self):
        assert CharValidator.is_eof(0xffff) is True
        assert CharValidator.is_eof(ord('A')) is False

    def test_is_eol(self):
        assert CharValidator.is_eol(10) is True
        assert CharValidator.is_eol(13) is True
        assert CharValidator.is_eof(ord('A')) is False

    def test_is_digit(self):
        assert CharValidator.is_digit(ord('0')) is True
        assert CharValidator.is_digit(ord('7')) is True
        assert CharValidator.is_digit(ord('9')) is True
        assert CharValidator.is_digit(ord('A')) is False
