# -*- coding: utf-8 -*-
from pip_services3_expressions.csv.CsvTokenizer import CsvTokenizer
from pip_services3_expressions.tokenizers.Token import Token
from pip_services3_expressions.tokenizers.TokenType import TokenType
from test.tokenizers.TokenizerFixture import TokenizerFixture


class TestCsvTokenizer:

    def test_tokenizer_with_default_parameters(self):
        token_string = "\n\r\"John \"\"Da Man\"\"\",Repici,120 Jefferson St.,Riverside, NJ,08075\r\n" \
                       + "Stephen,Tyler,\"7452 Terrace \"\"At the Plaza\"\" road\",SomeTown,SD, 91234\r" \
                       + ",Blankman,,SomeTown, SD, 00298\n"

        expected_tokens = [
            Token(TokenType.Eol, "\n\r", 0, 0),
            Token(TokenType.Quoted, "\"John \"\"Da Man\"\"\"", 0, 0), Token(TokenType.Symbol, ",", 0, 0),
            Token(TokenType.Word, "Repici", 0, 0), Token(TokenType.Symbol, ",", 0, 0),
            Token(TokenType.Word, "120 Jefferson St.", 0, 0), Token(TokenType.Symbol, ",", 0, 0),
            Token(TokenType.Word, "Riverside", 0, 0), Token(TokenType.Symbol, ",", 0, 0),
            Token(TokenType.Word, " NJ", 0, 0), Token(TokenType.Symbol, ",", 0, 0),
            Token(TokenType.Word, "08075", 0, 0), Token(TokenType.Eol, "\r\n", 0, 0),
            Token(TokenType.Word, "Stephen", 0, 0), Token(TokenType.Symbol, ",", 0, 0),
            Token(TokenType.Word, "Tyler", 0, 0), Token(TokenType.Symbol, ",", 0, 0),
            Token(TokenType.Quoted, "\"7452 Terrace \"\"At the Plaza\"\" road\"", 0, 0),
            Token(TokenType.Symbol, ",", 0, 0),
            Token(TokenType.Word, "SomeTown", 0, 0), Token(TokenType.Symbol, ",", 0, 0),
            Token(TokenType.Word, "SD", 0, 0), Token(TokenType.Symbol, ",", 0, 0),
            Token(TokenType.Word, " 91234", 0, 0), Token(TokenType.Eol, "\r", 0, 0),
            Token(TokenType.Symbol, ",", 0, 0),
            Token(TokenType.Word, "Blankman", 0, 0), Token(TokenType.Symbol, ",", 0, 0),
            Token(TokenType.Symbol, ",", 0, 0),
            Token(TokenType.Word, "SomeTown", 0, 0), Token(TokenType.Symbol, ",", 0, 0),
            Token(TokenType.Word, " SD", 0, 0), Token(TokenType.Symbol, ",", 0, 0),
            Token(TokenType.Word, " 00298", 0, 0), Token(TokenType.Eol, "\n", 0, 0)
        ]
        tokenizer = CsvTokenizer()
        tokenizer.skip_eof = True
        token_list = tokenizer.tokenize_buffer(token_string)

        TokenizerFixture.assert_are_equals_token_lists(expected_tokens, token_list)

    def test_tokenizer_with_overriden_parameters(self):
        token_string = "\n\r\'John, \'\'Da Man\'\'\'\tRepici\t120 Jefferson St.\tRiverside\t NJ\t08075\r\n" \
                       + "Stephen\t\"Tyler\"\t\'7452 \t\nTerrace \'\'At the Plaza\'\' road\'\tSomeTown\tSD\t 91234\r" \
                       + "\tBlankman\t\tSomeTown \'xxx\t\'\t SD\t 00298\n"

        expected_tokens = [
            Token(TokenType.Eol, "\n\r", 0, 0),
            Token(TokenType.Quoted, "\'John, \'\'Da Man\'\'\'", 0, 0), Token(TokenType.Symbol, "\t", 0, 0),
            Token(TokenType.Word, "Repici", 0, 0), Token(TokenType.Symbol, "\t", 0, 0),
            Token(TokenType.Word, "120 Jefferson St.", 0, 0), Token(TokenType.Symbol, "\t", 0, 0),
            Token(TokenType.Word, "Riverside", 0, 0), Token(TokenType.Symbol, "\t", 0, 0),
            Token(TokenType.Word, " NJ", 0, 0), Token(TokenType.Symbol, "\t", 0, 0),
            Token(TokenType.Word, "08075", 0, 0), Token(TokenType.Eol, "\r\n", 0, 0),
            Token(TokenType.Word, "Stephen", 0, 0), Token(TokenType.Symbol, "\t", 0, 0),
            Token(TokenType.Quoted, "\"Tyler\"", 0, 0), Token(TokenType.Symbol, "\t", 0, 0),
            Token(TokenType.Quoted, "\'7452 \t\nTerrace \'\'At the Plaza\'\' road\'", 0, 0),
            Token(TokenType.Symbol, "\t", 0, 0),
            Token(TokenType.Word, "SomeTown", 0, 0), Token(TokenType.Symbol, "\t", 0, 0),
            Token(TokenType.Word, "SD", 0, 0), Token(TokenType.Symbol, "\t", 0, 0),
            Token(TokenType.Word, " 91234", 0, 0), Token(TokenType.Eol, "\r", 0, 0),
            Token(TokenType.Symbol, "\t", 0, 0),
            Token(TokenType.Word, "Blankman", 0, 0), Token(TokenType.Symbol, "\t", 0, 0),
            Token(TokenType.Symbol, "\t", 0, 0),
            Token(TokenType.Word, "SomeTown ", 0, 0), Token(TokenType.Quoted, "\'xxx\t\'", 0, 0),
            Token(TokenType.Symbol, "\t", 0, 0),
            Token(TokenType.Word, " SD", 0, 0), Token(TokenType.Symbol, "\t", 0, 0),
            Token(TokenType.Word, " 00298", 0, 0), Token(TokenType.Eol, "\n", 0, 0)
        ]

        # tokenizer = CsvTokenizer()
        # tokenizer.field_separators = [ord('\t')]
        # tokenizer.quote_symbols = [ord('\''), ord('\"')]
        # tokenizer.end_of_line = "\n"
        # tokenizer.skip_eof = True
        # token_list = tokenizer.tokenize_buffer(token_string)
        #
        # TokenizerFixture.assert_are_equals_token_lists(expected_tokens, token_list)
