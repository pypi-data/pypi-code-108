# -*- coding: utf-8 -*-

from pip_services3_expressions.mustache.parsers.MustacheParser import MustacheParser
from pip_services3_expressions.mustache.parsers.MustacheToken import MustacheToken
from pip_services3_expressions.mustache.parsers.MustacheTokenType import MustacheTokenType


class TestMustacheParser:

    def test_lexical_analysis(self):
        parser = MustacheParser()
        parser.template = "Hello, {{{NAME}}}{{ #if ESCLAMATION }}!{{/if}}{{{^ESCLAMATION}}}.{{{/ESCLAMATION}}}"
        expected_tokens = [
            MustacheToken(MustacheTokenType.Value, "Hello, ", 0, 0),
            MustacheToken(MustacheTokenType.EscapedVariable, "NAME", 0, 0),
            MustacheToken(MustacheTokenType.Section, "ESCLAMATION", 0, 0),
            MustacheToken(MustacheTokenType.Value, "!", 0, 0),
            MustacheToken(MustacheTokenType.SectionEnd, None, 0, 0),
            MustacheToken(MustacheTokenType.InvertedSection, "ESCLAMATION", 0, 0),
            MustacheToken(MustacheTokenType.Value, ".", 0, 0),
            MustacheToken(MustacheTokenType.SectionEnd, "ESCLAMATION", 0, 0),
        ]

        tokens = parser.initial_tokens
        assert len(expected_tokens) == len(tokens)

        for i in range(len(tokens)):
            assert expected_tokens[i].type == tokens[i].type
            assert expected_tokens[i].value == tokens[i].value

    def test_syntax_analysis(self):
        parser = MustacheParser()
        parser.template = "Hello, {{{NAME}}}{{ #if ESCLAMATION }}!{{/if}}{{{^ESCLAMATION}}}.{{{/ESCLAMATION}}}"

        expected_tokens = [
            MustacheToken(MustacheTokenType.Value, "Hello, ", 0, 0),
            MustacheToken(MustacheTokenType.EscapedVariable, "NAME", 0, 0),
            MustacheToken(MustacheTokenType.Section, "ESCLAMATION", 0, 0),
            MustacheToken(MustacheTokenType.InvertedSection, "ESCLAMATION", 0, 0),
        ]

        tokens = parser.result_tokens
        assert len(expected_tokens) == len(tokens)

        for i in range(len(tokens)):
            assert expected_tokens[i].type == tokens[i].type
            assert expected_tokens[i].value == tokens[i].value

    def test_variable_names(self):
        parser = MustacheParser()
        parser.template = "Hello, {{{NAME}}}{{ #if ESCLAMATION }}!{{/if}}{{{^ESCLAMATION}}}.{{{/ESCLAMATION}}}"
        assert 2 == len(parser.variable_names)
        assert 'NAME' == parser.variable_names[0]
        assert "ESCLAMATION" == parser.variable_names[1]
