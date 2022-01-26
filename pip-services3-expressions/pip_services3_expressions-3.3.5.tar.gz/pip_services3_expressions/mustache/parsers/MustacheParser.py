# -*- coding: utf-8 -*-
from typing import List

from pip_services3_expressions.mustache.MustacheException import MustacheException
from pip_services3_expressions.mustache.parsers.MustacheErrorCode import MustacheErrorCode
from pip_services3_expressions.mustache.parsers.MustacheLexicalState import MustacheLexicalState
from pip_services3_expressions.mustache.parsers.MustacheToken import MustacheToken
from pip_services3_expressions.mustache.parsers.MustacheTokenType import MustacheTokenType
from pip_services3_expressions.mustache.tokenizers.MustacheTokenizer import MustacheTokenizer
from pip_services3_expressions.tokenizers.ITokenizer import ITokenizer
from pip_services3_expressions.tokenizers.Token import Token
from pip_services3_expressions.tokenizers.TokenType import TokenType


class MustacheParser:
    """
    Implements an mustache parser class.
    """

    def __init__(self):
        self.__tokenizer: ITokenizer = MustacheTokenizer()
        self.__template: str = ""
        self.__original_tokens: List[Token] = []
        self.__initial_tokens: List[MustacheToken] = []
        self.__current_token_index: int = None
        self.__variable_names: List[str] = []
        self.__result_tokens: List[MustacheToken] = []

    @property
    def template(self) -> str:
        """
        The mustache template.
        """
        return self.__template

    @template.setter
    def template(self, value: str):
        self.parse_string(value)

    @property
    def original_tokens(self) -> List[Token]:
        return self.__original_tokens

    @original_tokens.setter
    def original_tokens(self, value: List[Token]):
        self.parse_tokens(value)

    @property
    def initial_tokens(self) -> List[MustacheToken]:
        """
        The list of original mustache tokens.
        """
        return self.__initial_tokens

    @property
    def result_tokens(self) -> List[MustacheToken]:
        """
        The list of parsed mustache tokens.
        """
        return self.__result_tokens

    @property
    def variable_names(self) -> List[str]:
        """
        The list of found variable names.
        """
        return self.__variable_names

    def parse_string(self, mustache: str):
        """
        Sets a new mustache string and parses it into internal byte code.

        :param mustache: A new mustache string.
        """
        self.clear()
        if mustache is not None:
            self.__template = mustache.strip()
        else:
            self.__template = ""
        self.__original_tokens = self.__tokenize_mustache(self.__template)
        self.__perform_parsing()

    def parse_tokens(self, tokens: List[Token]):
        self.clear()
        self.__original_tokens = tokens
        self.__template = self.__compose_mustache(tokens)
        self.__perform_parsing()

    def clear(self):
        """
        Clears parsing results.
        """
        self.__template = None
        self.__original_tokens = []
        self.__initial_tokens = []
        self.__result_tokens = []
        self.__current_token_index = 0
        self.__variable_names = []

    def __has_more_tokens(self) -> bool:
        """
        Checks are there more tokens for processing.

        :return: **True** if some tokens are present.
        """
        return self.__current_token_index < len(self.__initial_tokens)

    def __check_for_more_tokens(self):
        """
        Checks are there more tokens available and throws exception if no more tokens available.
        """
        if not self.__has_more_tokens():
            raise MustacheException(None, MustacheErrorCode.UNEXPECTED_END, "Unexpected end of mustache.", 0, 0)

    def __get_current_token(self) -> MustacheToken:
        """
        Gets the current token object.

        :return: The current token object.
        """
        return self.initial_tokens[self.__current_token_index] if self.__current_token_index < len(
            self.__initial_tokens) else None

    def __get_next_token(self) -> MustacheToken:
        """
        Gets the next token object.

        :return: The next token object.
        """
        return self.__initial_tokens[self.__current_token_index + 1] if (self.__current_token_index + 1) < len(
            self.initial_tokens) else None

    def __move_to_next_token(self):
        """
        Moves to the next token object.
        """
        self.__current_token_index += 1

    def __add_token_to_result(self, type: MustacheTokenType, value: str, line: int, column: int) -> MustacheToken:
        """
        Adds an mustache to the result list

        :param type: The type of the token to be added.
        :param value: The value of the token to be added.
        :param line: The line where the token is.
        :param column: The column number where the token is.
        """
        token = MustacheToken(type, value, line, column)
        self.__result_tokens.append(token)
        return token

    def __tokenize_mustache(self, mustache: str) -> List[Token]:
        if mustache is not None:
            mustache = mustache.strip()
        else:
            mustache = ""
        if len(mustache) > 0:
            self.__tokenizer.skip_whitespaces = True
            self.__tokenizer.skip_comments = True
            self.__tokenizer.skip_eof = True
            self.__tokenizer.decode_strings = True
            return self.__tokenizer.tokenize_buffer(mustache)
        else:
            return []

    def __compose_mustache(self, tokens: List[Token]) -> str:
        builder = ""
        for token in tokens:
            builder = builder + token.value

        return builder

    def __perform_parsing(self):
        if len(self.__original_tokens) > 0:
            self.__complete_lexical_analysis()
            self.__perform_syntax_analysis()
            if self.__has_more_tokens():
                token = self.__get_current_token()
                raise MustacheException(None, MustacheErrorCode.ERROR_NEAR, "Syntax error near " + token.value,
                                        token.line, token.column)
            self.__lookup_variables()

    def __complete_lexical_analysis(self):
        state = MustacheLexicalState.Value
        closing_bracket = None
        operator1 = None
        operator2 = None
        variable = None

        for token in self.__original_tokens:
            token_type = MustacheTokenType.Unknown
            token_value = None

            if state == MustacheLexicalState.Comment:
                if token.value == "}}" or token.value == "}}}":
                    state = MustacheLexicalState.Closure
                else:
                    continue

            if token.type == TokenType.Special:
                if state == MustacheLexicalState.Value:
                    token_type = MustacheTokenType.Value
                    token_value = token.value
            elif token.type == TokenType.Symbol:
                if state == MustacheLexicalState.Value and (token.value == "{{" or token.value == "{{{"):
                    closing_bracket = "}}" if token.value == "{{" else "}}}"
                    state = MustacheLexicalState.Operator1
                    continue
                if state == MustacheLexicalState.Operator1 and token.value == "!":
                    operator1 = token.value
                    state = MustacheLexicalState.Comment
                    continue
                if state == MustacheLexicalState.Operator1 and (
                        token.value == '/' or token.value == '#' or token.value == "^"):
                    operator1 = token.value
                    state = MustacheLexicalState.Operator2
                    continue
                if state == MustacheLexicalState.Variable and (token.value == "}}" or token.value == "}}}"):
                    if operator1 != '/':
                        variable = operator2
                        operator2 = None
                    state = MustacheLexicalState.Closure
                    # Pass through

                if state == MustacheLexicalState.Closure and (token.value == "}}" or token.value == "}}}"):
                    if closing_bracket != token.value:
                        raise MustacheException(None, MustacheErrorCode.MISMATCHED_BRACKETS,
                                                "Mismatched brackets. Expected '" + closing_bracket + "'",
                                                token.line, token.column)

                    if operator1 == '#' and (operator2 is None or operator2 == "if"):
                        token_type = MustacheTokenType.Section
                        token_value = variable

                    if operator1 == '#' and operator2 == 'unless':
                        token_type = MustacheTokenType.InvertedSection
                        token_value = variable

                    if operator1 == "^" and operator2 is None:
                        token_type = MustacheTokenType.InvertedSection
                        token_value = variable

                    if operator1 == "/":
                        token_type = MustacheTokenType.SectionEnd
                        token_value = variable

                    if operator1 is None:
                        token_type = MustacheTokenType.Variable if closing_bracket == "}}" else MustacheTokenType.EscapedVariable
                        token_value = variable

                    if token_type == MustacheTokenType.Unknown:
                        raise MustacheException(None, MustacheErrorCode.INTERNAL, "Internal error",
                                                token.line, token.column)

                    operator1 = None
                    operator2 = None
                    variable = None
                    state = MustacheLexicalState.Value

            elif token.type == TokenType.Word:
                if state == MustacheLexicalState.Operator1:
                    state = MustacheLexicalState.Variable

                if state == MustacheLexicalState.Operator2 and (token.value == "if" or token.value == "unless"):
                    operator2 = token.value
                    state = MustacheLexicalState.Variable
                    continue

                if state == MustacheLexicalState.Operator2:
                    state = MustacheLexicalState.Variable

                if state == MustacheLexicalState.Variable:
                    variable = token.value
                    state = MustacheLexicalState.Closure
                    continue

            elif token.type == TokenType.Whitespace:
                continue

            if token_type == MustacheTokenType.Unknown:
                raise MustacheException(None, MustacheErrorCode.UNEXPECTED_SYMBOL,
                                        "Unexpected symbol '" + token.value + "'", token.line, token.column)

            self.__initial_tokens.append(MustacheToken(token_type, token_value, token.line, token.column))

        if state != MustacheLexicalState.Value:
            raise MustacheException(None, MustacheErrorCode.UNEXPECTED_END, "Unexpected end of file", 0, 0)

    def __perform_syntax_analysis(self):
        """
        Performs a syntax analysis at level 0.
        """
        self.__check_for_more_tokens()
        while self.__has_more_tokens():
            token = self.__get_current_token()
            self.__move_to_next_token()

            if token.type == MustacheTokenType.SectionEnd:
                raise MustacheException(None, MustacheErrorCode.UNEXPECTED_SECTION_END,
                                        "Unexpected section end for variable '" + token.value + "'",
                                        token.line, token.column)

            result = self.__add_token_to_result(token.type, token.value, token.line, token.column)

            if token.type == MustacheTokenType.Section or token.type == MustacheTokenType.InvertedSection:
                result.tokens.extend(self.__perform_syntax_analysis_for_section(token.value))

    def __perform_syntax_analysis_for_section(self, variable: str) -> List[MustacheToken]:
        result = []

        self.__check_for_more_tokens()
        while self.__has_more_tokens():
            token = self.__get_current_token()
            self.__move_to_next_token()

            if token.type == MustacheTokenType.SectionEnd and (token.value == variable or token.value is None):
                return result

            if token.type == MustacheTokenType.SectionEnd:
                raise MustacheException(None, MustacheErrorCode.UNEXPECTED_SECTION_END,
                                        "Unexpected section end for variable '" + variable + "'",
                                        token.line, token.column)

            result_token = MustacheToken(token.type, token.value, token.line, token.column)

            if token.type == MustacheTokenType.Section or token.type == MustacheTokenType.InvertedSection:
                result_token.tokens.append(*self.__perform_syntax_analysis_for_section(token.value))

            result.append(result_token)

        token = self.__get_current_token()

        raise MustacheException(None, MustacheErrorCode.NOT_CLOSED_SECTION,
                                "Not closed section for variable '" + variable + "'",
                                token.line, token.column)

    def __lookup_variables(self):
        """
        Retrieves variables from the parsed output.
        """
        if self.__original_tokens is None:
            return

        self.__variable_names = []
        for token in self.__initial_tokens:
            if token.type not in [MustacheTokenType.Value, MustacheTokenType.Comment] and token.value is not None:
                variable_name = token.value.lower()
                found = len(list(filter(lambda v: v.lower() == variable_name, self.__variable_names))) > 0
                if not found:
                    self.__variable_names.append(token.value)
