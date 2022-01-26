# -*- coding: utf-8 -*-
from typing import List

from pip_services3_commons.convert import IntegerConverter, FloatConverter

from pip_services3_expressions.calculator.SyntaxErrorCode import SyntaxErrorCode
from pip_services3_expressions.calculator.SyntaxException import SyntaxException
from pip_services3_expressions.calculator.parsers.ExpressionToken import ExpressionToken
from pip_services3_expressions.calculator.parsers.ExpressionTokenType import ExpressionTokenType
from pip_services3_expressions.calculator.tokenizers.ExpressionTokenizer import ExpressionTokenizer
from pip_services3_expressions.tokenizers.ITokenizer import ITokenizer
from pip_services3_expressions.tokenizers.Token import Token
from pip_services3_expressions.tokenizers.TokenType import TokenType
from pip_services3_expressions.variants.Variant import Variant


class ExpressionParser:
    """
    Implements an expression parser class.
    """

    def __init__(self):
        """
        Defines a list of operators.
        """
        self.__OPERATORS: List[str] = [
            "(", ")", "[", "]", "+", "-", "*", "/", "%", "^",
            "=", "<>", "!=", ">", "<", ">=", "<=", "<<", ">>",
            "AND", "OR", "XOR", "NOT", "IS", "IN", "NULL", "LIKE", ","
        ]

        self.__OPERATOR_TYPES: List[ExpressionTokenType] = [
            ExpressionTokenType.LeftBrace, ExpressionTokenType.RightBrace,
            ExpressionTokenType.LeftSquareBrace, ExpressionTokenType.RightSquareBrace,
            ExpressionTokenType.Plus, ExpressionTokenType.Minus,
            ExpressionTokenType.Star, ExpressionTokenType.Slash,
            ExpressionTokenType.Percent, ExpressionTokenType.Power,
            ExpressionTokenType.Equal, ExpressionTokenType.NotEqual,
            ExpressionTokenType.NotEqual, ExpressionTokenType.More,
            ExpressionTokenType.Less, ExpressionTokenType.EqualMore,
            ExpressionTokenType.EqualLess, ExpressionTokenType.ShiftLeft,
            ExpressionTokenType.ShiftRight, ExpressionTokenType.And,
            ExpressionTokenType.Or, ExpressionTokenType.Xor,
            ExpressionTokenType.Not, ExpressionTokenType.Is,
            ExpressionTokenType.In, ExpressionTokenType.Null,
            ExpressionTokenType.Like, ExpressionTokenType.Comma
        ]

        self.__tokenizer: ITokenizer = ExpressionTokenizer()
        self.__expression: str = ''
        self.__original_tokens: List[Token] = []
        self.__initial_tokens: List[ExpressionToken] = []
        self.__current_token_index: int = 0
        self.__variable_names: List[str] = []
        self.__result_tokens: List[ExpressionToken] = []

    @property
    def expression(self) -> str:
        """
        The expression string.
        """
        return self.__expression

    @expression.setter
    def expression(self, value: str):
        self.parse_string(value)

    @property
    def original_tokens(self) -> List[Token]:
        return self.__original_tokens

    @original_tokens.setter
    def original_tokens(self, value: List[Token]):
        self.__original_tokens = value

    @property
    def initial_tokens(self) -> List[ExpressionToken]:
        """
        The list of original expression tokens.
        """
        return self.__initial_tokens

    @property
    def result_tokens(self) -> List[ExpressionToken]:
        """
        The list of parsed expression tokens.
        """
        return self.__result_tokens

    @property
    def variable_names(self) -> List[str]:
        """
        The list of found variable names.
        """
        return self.__variable_names

    def parse_string(self, expression: str):
        """
        Sets a new expression string and parses it into internal byte code.

        :param expression: A new expression string.
        """
        self.clear()
        self.__expression = expression.strip() if expression is not None else ''
        self.__original_tokens = self.__tokenize_expression(self.__expression)
        self.__perform_parsing()

    def parse_tokens(self, tokens: List[Token]):
        self.clear()
        self.__original_tokens = tokens
        self.__expression = self.__compose_expression(tokens)
        self.__perform_parsing()

    def clear(self):
        """
        Clears parsing results.
        """
        self.__expression = None
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
            raise SyntaxException(None, SyntaxErrorCode.UNEXPECTED_END, 'Unexpected end of expression.', 0, 0)

    def __get_current_token(self) -> ExpressionToken:
        """
        Gets the current token object.

        :return: The current token object.
        """
        return self.__initial_tokens[self.__current_token_index] if self.__current_token_index < len(
            self.__initial_tokens) else None

    def __get_next_token(self) -> ExpressionToken:
        """
        Gets the next token object.

        :return: The next token object.
        """
        return self.__initial_tokens[self.__current_token_index + 1] if (self.__current_token_index + 1) < len(
            self.__initial_tokens) else None

    def __move_to_next_token(self):
        """
        Moves to the next token object.
        """
        self.__current_token_index += 1

    def __add_token_to_result(self, type, value, line, column):
        """
        Adds an expression to the result list

        :param type: The type of the token to be added.
        :param value: The value of the token to be added.
        :param line: The line number where the token is.
        :param column: The column number where the token is.
        """
        self.__result_tokens.append(ExpressionToken(type, value, line, column))

    def __match_tokens_with_types(self, *types) -> bool:
        """
        Matches available tokens types with types from the list.
        If tokens matches then shift the list.
        
        :param types: A list of token types to compare.
        :return: **True** if token types match.
        """
        matches = False
        for i in range(0, len(types)):
            if self.__current_token_index + i < len(self.__initial_tokens):
                matches = self.__initial_tokens[self.__current_token_index + i].type == types[i]
            else:
                matches = False
                break
        if matches:
            self.__current_token_index += len(types)
        return matches

    def __tokenize_expression(self, expression: str) -> List[Token]:
        expression = expression.strip() if expression is not None else ''
        if len(expression) > 0:
            self.__tokenizer.skip_whitespaces = True
            self.__tokenizer.skip_comments = True
            self.__tokenizer.skip_eof = True
            self.__tokenizer.decode_strings = True
            return self.__tokenizer.tokenize_buffer(expression)
        else:
            return []

    def __compose_expression(self, tokens: List[Token]) -> str:
        builder = ''
        for token in tokens:
            builder += token.value
        return builder

    def __perform_parsing(self):
        if len(self.__original_tokens) > 0:
            self.__complete_lexical_analysis()
            self.__perform_syntax_analysis()
            if self.__has_more_tokens():
                token = self.__get_current_token()
                raise SyntaxException(None, SyntaxErrorCode.ERROR_NEAR, f'Syntax error near {token.value}',
                                      token.line,
                                      token.column)

    def __complete_lexical_analysis(self):
        """
        Tokenizes the given expression and prepares an initial tokens list.
        """
        for token in self.__original_tokens:
            token_type = ExpressionTokenType.Unknown
            token_value = Variant.Empty()
            if token.type in [TokenType.Comment, TokenType.Whitespace]:
                continue
            elif token.type == TokenType.Keyword:
                temp = token.value.upper()
                if temp == 'TRUE':
                    token_type = ExpressionTokenType.Constant
                    token_value = Variant.from_boolean(True)
                elif temp == 'FALSE':
                    token_type = ExpressionTokenType.Constant
                    token_value = Variant.from_boolean(False)
                else:
                    for index in range(len(self.__OPERATORS)):
                        if temp == self.__OPERATORS[index]:
                            token_type = self.__OPERATOR_TYPES[index]
                            break
            elif token.type == TokenType.Word:
                token_type = ExpressionTokenType.Variable
                token_value = Variant.from_string(token.value)
            elif token.type == TokenType.Integer:
                token_type = ExpressionTokenType.Constant
                token_value = Variant.from_integer(IntegerConverter.to_integer(token.value))
            elif token.type == TokenType.Float:
                token_type = ExpressionTokenType.Constant
                token_value = Variant.from_float(FloatConverter.to_float(token.value))
            elif token.type == TokenType.Quoted:
                token_type = ExpressionTokenType.Constant
                token_value = Variant.from_string(token.value)
            elif token.type == TokenType.Symbol:
                temp = token.value.upper()
                for i in range(len(self.__OPERATORS)):
                    if temp == self.__OPERATORS[i]:
                        token_type = self.__OPERATOR_TYPES[i]
                        break

            if token_type == ExpressionTokenType.Unknown:
                raise SyntaxException(None, SyntaxErrorCode.UNKNOWN_SYMBOL, "Unknown symbol " + token.value,
                                      token.line,
                                      token.column)

            self.__initial_tokens.append(ExpressionToken(token_type, token_value, token.line, token.column))

    def __perform_syntax_analysis(self):
        """
        Performs a syntax analysis at level 0.
        """
        self.__check_for_more_tokens()
        self.__perform_syntax_analysis_at_level1()
        while self.__has_more_tokens():
            token = self.__get_current_token()
            if token.type in [ExpressionTokenType.And, ExpressionTokenType.Or, ExpressionTokenType.Xor]:
                self.__move_to_next_token()
                self.__perform_syntax_analysis_at_level1()
                self.__add_token_to_result(token.type, Variant.Empty(), token.line, token.column)
                continue
            break

    def __perform_syntax_analysis_at_level1(self):
        """
        Performs a syntax analysis at level 1.
        """
        self.__check_for_more_tokens()
        token = self.__get_current_token()
        if token.type == ExpressionTokenType.Not:
            self.__move_to_next_token()
            self.__perform_syntax_analysis_at_level2()
            self.__add_token_to_result(token.type, Variant.Empty(), token.line, token.column)
        else:
            self.__perform_syntax_analysis_at_level2()

    def __perform_syntax_analysis_at_level2(self):
        """
        Performs a syntax analysis at level 2.
        """
        self.__check_for_more_tokens()
        self.__perform_syntax_analysis_at_level3()
        while self.__has_more_tokens():
            token = self.__get_current_token()
            if token.type in [ExpressionTokenType.Equal, ExpressionTokenType.NotEqual, ExpressionTokenType.More,
                              ExpressionTokenType.Less, ExpressionTokenType.EqualMore, ExpressionTokenType.EqualLess]:
                self.__move_to_next_token()
                self.__perform_syntax_analysis_at_level3()
                self.__add_token_to_result(token.type, Variant.Empty(), token.line, token.column)
                continue
            break

    def __perform_syntax_analysis_at_level3(self):
        """
        Performs a syntax analysis at level 3.
        """
        self.__check_for_more_tokens()
        self.__perform_syntax_analysis_at_level4()
        while self.__has_more_tokens():
            token = self.__get_current_token()
            if token.type in [ExpressionTokenType.Plus, ExpressionTokenType.Minus, ExpressionTokenType.Like]:
                self.__move_to_next_token()
                self.__perform_syntax_analysis_at_level4()
                self.__add_token_to_result(token.type, Variant.Empty(), token.line, token.column)
            elif self.__match_tokens_with_types(ExpressionTokenType.Is, ExpressionTokenType.Less):
                self.__perform_syntax_analysis_at_level4()
                self.__add_token_to_result(ExpressionTokenType.NotLike, Variant.Empty(), token.line, token.column)
            elif self.__match_tokens_with_types(ExpressionTokenType.Is, ExpressionTokenType.Null):
                self.__add_token_to_result(ExpressionTokenType.IsNull, Variant.Empty(), token.line, token.column)
            elif self.__match_tokens_with_types(ExpressionTokenType.Is, ExpressionTokenType.Not,
                                                ExpressionTokenType.Null):
                self.__add_token_to_result(ExpressionTokenType.IsNotNull, Variant.Empty(), token.line, token.column)
            elif self.__match_tokens_with_types(ExpressionTokenType.Not, ExpressionTokenType.In):
                self.__perform_syntax_analysis_at_level4()
                self.__add_token_to_result(ExpressionTokenType.NotIn, Variant.Empty(), token.line, token.column)
            else:
                break

    def __perform_syntax_analysis_at_level4(self):
        """
        Performs a syntax analysis at level 4.
        """
        self.__check_for_more_tokens()
        self.__perform_syntax_analysis_at_level5()
        while self.__has_more_tokens():
            token = self.__get_current_token()
            if token.type in [ExpressionTokenType.Star, ExpressionTokenType.Slash, ExpressionTokenType.Percent]:
                self.__move_to_next_token()
                self.__perform_syntax_analysis_at_level5()
                self.__add_token_to_result(token.type, Variant.Empty(), token.line, token.column)
                continue
            break

    def __perform_syntax_analysis_at_level5(self):
        """
        Performs a syntax analysis at level 5.
        """
        self.__check_for_more_tokens()
        self.__perform_syntax_analysis_at_level6()
        while self.__has_more_tokens():
            token = self.__get_current_token()
            if token.type in [ExpressionTokenType.Power, ExpressionTokenType.In, ExpressionTokenType.ShiftLeft,
                              ExpressionTokenType.ShiftRight]:
                self.__move_to_next_token()
                self.__perform_syntax_analysis_at_level6()
                self.__add_token_to_result(token.type, Variant.Empty(), token.line, token.column)
                continue
            break

    def __perform_syntax_analysis_at_level6(self):
        """
        Performs a syntax analysis at level 6.
        """
        self.__check_for_more_tokens()
        # Process unary '+' or '-'.
        unary_token = self.__get_current_token()
        if unary_token.type == ExpressionTokenType.Plus:
            unary_token = None
            self.__move_to_next_token()
        elif unary_token.type == ExpressionTokenType.Minus:
            unary_token = ExpressionToken(ExpressionTokenType.Unary, unary_token.value,
                                          unary_token.line, unary_token.column)
            self.__move_to_next_token()
        else:
            unary_token = None

        self.__check_for_more_tokens()

        # Identify function calls.
        primitive_token = self.__get_current_token()
        next_token = self.__get_next_token()
        if primitive_token.type == ExpressionTokenType.Variable and \
                next_token is not None and next_token.type == ExpressionTokenType.LeftBrace:
            primitive_token = ExpressionToken(ExpressionTokenType.Function, primitive_token.value,
                                              primitive_token.line, primitive_token.column)

        if primitive_token.type == ExpressionTokenType.Constant:
            self.__move_to_next_token()
            self.__add_token_to_result(primitive_token.type, primitive_token.value,
                                       primitive_token.line, primitive_token.column)
        elif primitive_token.type == ExpressionTokenType.Variable:
            self.__move_to_next_token()

            temp = primitive_token.value.as_string
            if temp not in self.__variable_names:
                self.__variable_names.append(temp)

            self.__add_token_to_result(primitive_token.type, primitive_token.value,
                                       primitive_token.line, primitive_token.column)

        elif primitive_token.type == ExpressionTokenType.LeftBrace:
            self.__move_to_next_token()
            self.__perform_syntax_analysis()
            self.__check_for_more_tokens()
            primitive_token = self.__get_current_token()
            if primitive_token.type != ExpressionTokenType.RightBrace:
                raise SyntaxException(None, SyntaxErrorCode.MISSED_CLOSE_PARENTHESIS, "Expected ')' was not found",
                                      primitive_token.line, primitive_token.column)
            self.__move_to_next_token()

        elif primitive_token.type == ExpressionTokenType.Function:
            self.__move_to_next_token()
            token = self.__get_current_token()
            if token.type != ExpressionTokenType.LeftBrace:
                raise SyntaxException(None, SyntaxErrorCode.INTERNAL, "Internal error.",
                                      token.line, token.column)
            param_count = 0

            do = True
            while do:
                self.__move_to_next_token()
                token = self.__get_current_token()
                if token is None or token.type == ExpressionTokenType.RightBrace:
                    break
                param_count += 1
                self.__perform_syntax_analysis()
                token = self.__get_current_token()
                if not (token is not None and token.type == ExpressionTokenType.Comma):
                    do = False

            self.__check_for_more_tokens()

            if token.type != ExpressionTokenType.RightBrace:
                raise SyntaxException(None, SyntaxErrorCode.MISSED_CLOSE_PARENTHESIS, "Expected ')' was not found.",
                                      token.line, token.column)

            self.__move_to_next_token()

            self.__add_token_to_result(ExpressionTokenType.Constant, Variant(param_count),
                                       primitive_token.line, primitive_token.column)
            self.__add_token_to_result(primitive_token.type, primitive_token.value,
                                       primitive_token.line, primitive_token.column)
        else:
            raise SyntaxException(None, SyntaxErrorCode.ERROR_AT, "Syntax error at " + primitive_token.value,
                                  primitive_token.line, primitive_token.column)

        if unary_token is not None:
            self.__add_token_to_result(unary_token.type, Variant.Empty(), unary_token.line, unary_token.column)

        # Process [] operator.
        if self.__has_more_tokens():
            primitive_token = self.__get_current_token()
            if primitive_token.type == ExpressionTokenType.LeftSquareBrace:
                self.__move_to_next_token()
                self.__perform_syntax_analysis()
                self.__check_for_more_tokens()
                primitive_token = self.__get_current_token()
                if primitive_token.type != ExpressionTokenType.RightSquareBrace:
                    raise SyntaxException(None, SyntaxErrorCode.MISSED_CLOSE_PARENTHESIS, "Expected ']' was not found",
                                          primitive_token.line, primitive_token.column)
                self.__move_to_next_token()
                self.__add_token_to_result(ExpressionTokenType.Element, Variant.Empty(),
                                           primitive_token.line, primitive_token.column)
