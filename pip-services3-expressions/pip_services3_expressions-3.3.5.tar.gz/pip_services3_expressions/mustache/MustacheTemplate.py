# -*- coding: utf-8 -*-

from typing import List, Optional, Any

from pip_services3_expressions.mustache.MustacheException import MustacheException
from pip_services3_expressions.mustache.parsers.MustacheParser import MustacheParser
from pip_services3_expressions.mustache.parsers.MustacheToken import MustacheToken
from pip_services3_expressions.mustache.parsers.MustacheTokenType import MustacheTokenType
from pip_services3_expressions.tokenizers.Token import Token


class MustacheTemplate:
    """
    Implements an mustache template class.
    """

    def __init__(self, template: Optional[str] = None):
        """
        Constructs this class and assigns mustache template.

        :param template: The mustache template.
        """
        self.__default_variables = {}
        self.__parser: MustacheParser = MustacheParser()
        self.__auto_variables: bool = True

        if self.template is not None:
            self.template = template

    @property
    def template(self) -> str:
        """
        The mustache template.
        """
        return self.__parser.template

    @template.setter
    def template(self, value: str):
        """
        The mustache template.
        """
        self.__parser.template = value
        if self.__auto_variables:
            self.create_variables(self.__default_variables)

    @property
    def original_tokens(self) -> List[Token]:
        return self.__parser.original_tokens

    @original_tokens.setter
    def original_tokens(self, value: List[Token]):
        self.__parser.original_tokens = value
        if self.__auto_variables:
            self.create_variables(self.__default_variables)

    @property
    def auto_variables(self) -> bool:
        """
        Gets the flag to turn on auto creation of variables for specified mustache.
        """
        return self.__auto_variables

    @auto_variables.setter
    def auto_variables(self, value: bool):
        """
        Sets the flag to turn on auto creation of variables for specified mustache.
        """
        self.__auto_variables = value

    @property
    def default_variables(self) -> Any:
        """
        The list with default variables.
        """
        return self.__default_variables

    @default_variables.setter
    def default_variables(self, value: dict):
        """
        Sets list with default variables.
        """
        self.__default_variables = value

    @property
    def initial_tokens(self) -> List[MustacheToken]:
        """
        The list of original mustache tokens.
        """
        return self.__parser.initial_tokens

    @property
    def result_tokens(self) -> List[MustacheToken]:
        """
        The list of processed mustache tokens.
        """
        return self.__parser.result_tokens

    def get_variables(self, variables: Any, name: str) -> Any:
        """
        Gets a variable value from the collection of variables

        :param variables: a collection of variables.
        :param name: a variable name to get.
        :return: a variable value or **None**
        """
        if variables is None or name is None:
            return None

        name = name.lower()
        result = None

        for prop_name in variables:
            if prop_name.lower() == name:
                result = result or variables[prop_name]

        return result

    def create_variables(self, variables: Any):
        """
        Populates the specified variables list with variables from parsed mustache.
        """
        if variables is None:
            return

        for variable_name in self.__parser.variable_names:
            found = self.get_variables(variables, variable_name) is not None
            if not found:
                variables[variable_name] = None

    def clear(self):
        """
        Cleans up this calculator from all data.
        """
        self.__parser.clear()
        self.__default_variables = {}

    def evaluate(self) -> str:
        """
        Evaluates this mustache template using default variables.

        :return: the evaluated template
        """
        return self.evaluate_with_variables(None)

    def evaluate_with_variables(self, variables: Any) -> str:
        """
        Evaluates this mustache using specified variables.

        :param variables: The collection of variables
        :return: the evaluated template
        """
        variables = variables or self.__default_variables

        return self.evaluate_tokens(self.__parser.result_tokens, variables)

    def __is__defined_variable(self, variables: Any, name: str) -> bool:
        value = self.get_variables(variables, name)
        return value is not None and value != "" and value != 0 and value is not False

    def __escape_string(self, value: str) -> str:
        return value.replace('\\', '\\\\') \
            .replace('"', '\\\"') \
            .replace('/', '\\/') \
            .replace('\b', '\\b') \
            .replace('\f', '\\f') \
            .replace('\n', '\\n') \
            .replace('\r', '\\r') \
            .replace('\t', '\\t')

    def evaluate_tokens(self, tokens: List[MustacheToken], variables: Any) -> Optional[str]:
        if tokens is None:
            return None

        result = ""

        for token in tokens:
            if token.type == MustacheTokenType.Comment:
                # Skip;
                pass

            elif token.type == MustacheTokenType.Value:
                result += token.value or ""

            elif token.type == MustacheTokenType.Variable:
                value1 = self.get_variables(variables, token.value)
                result += value1 or ""

            elif token.type == MustacheTokenType.EscapedVariable:
                value2 = self.get_variables(variables, token.value)
                value2 = self.__escape_string(value2)
                result += value2 or ""

            elif token.type == MustacheTokenType.Section:
                defined1 = self.__is__defined_variable(variables, token.value)
                if defined1 and token.tokens is not None:
                    result += self.evaluate_tokens(token.tokens, variables)

            elif token.type == MustacheTokenType.InvertedSection:
                defined2 = self.__is__defined_variable(variables, token.value)
                if not defined2 and token.tokens is not None:
                    result += self.evaluate_tokens(token.tokens, variables)

            elif token.type == MustacheTokenType.Partial:
                raise MustacheException(None, "PARTIALS_NOT_SUPPORTED", "Partials are not supported", token.line,
                                        token.column)
            else:
                raise MustacheException(None, "INTERNAL", "Internal error", token.line, token.column)

        return result
