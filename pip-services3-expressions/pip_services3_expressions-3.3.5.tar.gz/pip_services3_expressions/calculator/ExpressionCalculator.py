# -*- coding: utf-8 -*-
from typing import List, Optional

from pip_services3_expressions.calculator.CalculationStack import CalculationStack
from pip_services3_expressions.calculator.ExpressionException import ExpressionException
from pip_services3_expressions.calculator.functions.DefaultFunctionCollection import DefaultFunctionCollection
from pip_services3_expressions.calculator.functions.IFunctionCollection import IFunctionCollection
from pip_services3_expressions.calculator.parsers.ExpressionParser import ExpressionParser
from pip_services3_expressions.calculator.parsers.ExpressionToken import ExpressionToken
from pip_services3_expressions.calculator.parsers.ExpressionTokenType import ExpressionTokenType
from pip_services3_expressions.calculator.variables.IVariableCollection import IVariableCollection
from pip_services3_expressions.calculator.variables.Variable import Variable
from pip_services3_expressions.calculator.variables.VariableCollection import VariableCollection
from pip_services3_expressions.tokenizers.Token import Token
from pip_services3_expressions.variants.IVariantOperations import IVariantOperations
from pip_services3_expressions.variants.TypeUnsafeVariantOperations import TypeUnsafeVariantOperations
from pip_services3_expressions.variants.Variant import Variant


class ExpressionCalculator:
    """
    Implements an expression calculator class.
    """

    def __init__(self, expression: str = None):
        """
        Constructs this class and assigns expression string.

        :param expression: The expression string.
        """

        self.__default_variables: IVariableCollection = VariableCollection()
        self.__default_functions: IFunctionCollection = DefaultFunctionCollection()
        self.__variant_operations: IVariantOperations = TypeUnsafeVariantOperations()
        self.__parser: ExpressionParser = ExpressionParser()
        self.__auto_variables: bool = True

        if expression is not None:
            self.expression = expression

    @property
    def expression(self) -> str:
        """
        The expression string.
        """
        return self.__parser.expression

    @expression.setter
    def expression(self, value: str):
        """
        The expression string.
        """
        self.__parser.expression = value
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
        Gets the flag to turn on auto creation of variables for specified expression.
        """
        return self.__auto_variables

    @auto_variables.setter
    def auto_variables(self, value: bool):
        self.__auto_variables = value

    @property
    def variant_operations(self) -> IVariantOperations:
        """
        Gets the manager for operations on variant values.
        """
        return self.__variant_operations

    @variant_operations.setter
    def variant_operations(self, value: IVariantOperations):
        """
        Sets the manager for operations on variant values.
        """
        self.__variant_operations = value

    @property
    def default_variables(self) -> IVariableCollection:
        """
        The list with default variables.
        """
        return self.__default_variables

    @property
    def default_functions(self) -> IFunctionCollection:
        """
        The list with default functions.
        """
        return self.__default_functions

    @property
    def initial_tokens(self) -> List[ExpressionToken]:
        return self.__parser.initial_tokens

    @property
    def result_tokens(self) -> List[ExpressionToken]:
        """
        The list of processed expression tokens.
        """
        return self.__parser.result_tokens

    def create_variables(self, variables: IVariableCollection):
        """
        Populates the specified variables list with variables from parsed expression.

        :param variables: The list of variables to be populated.
        """
        for variable_name in self.__parser.variable_names:
            if variables.find_by_name(variable_name) is None:
                variables.add(Variable(variable_name))

    def clear(self):
        """
        Cleans up this calculator from all data.
        """
        self.__parser.clear()
        self.__default_variables.clear()

    def evaluate(self) -> Variant:
        """
        Evaluates this expression using default variables and functions.
        """
        return self.evaluate_with_variables_and_functions(None, None)

    def evaluate_with_variables(self, variables: IVariableCollection) -> Variant:
        """
        Evaluates this expression using specified variables.

        :param variables: The list of variables
        """
        return self.evaluate_with_variables_and_functions(variables, None)

    def evaluate_with_variables_and_functions(self, variables: Optional[IVariableCollection],
                                              functions: Optional[IFunctionCollection]) -> Variant:
        """
        Evaluates this expression using specified variables and functions.

        :param variables: The list of variables
        :param functions: The list of functions
        """
        stack = CalculationStack()
        variables = variables or self.__default_variables
        functions = functions or self.__default_functions

        for token in self.result_tokens:
            if self.__evaluate_constant(token, stack):
                continue
            if self.__evaluate_variable(token, stack, variables):
                continue
            if self.__evaluate_function(token, stack, functions):
                continue
            if self.__evaluate_logical(token, stack):
                continue
            if self.__evaluate_arithmetical(token, stack):
                continue
            if self.__evaluate_boolean(token, stack):
                continue
            if self.__evaluate_other(token, stack):
                continue

            raise ExpressionException(None, "INTERNAL", "Internal error", token.line, token.column)

        if stack.length != 1:
            raise ExpressionException(None, "INTERNAL", "Internal error", 0, 0)

        return stack.pop()

    def __evaluate_constant(self, token: ExpressionToken, stack: CalculationStack) -> bool:
        if token.type != ExpressionTokenType.Constant:
            return False

        stack.push(token.value)
        return True

    def __evaluate_variable(self, token: ExpressionToken, stack: CalculationStack,
                            variables: IVariableCollection) -> bool:
        if token.type != ExpressionTokenType.Variable:
            return False

        variable = variables.find_by_name(token.value.as_string)
        if variable is None:
            raise ExpressionException(None, "VAR_NOT_FOUND", "Variable " + token.value.as_string + " was not found.",
                                      token.line, token.column)

        stack.push(variable.value)
        return True

    def __evaluate_function(self, token: ExpressionToken, stack: CalculationStack,
                            functions: IFunctionCollection) -> bool:
        if token.type != ExpressionTokenType.Function:
            return False

        func = functions.find_by_name(token.value.as_string)
        if func is None:
            raise ExpressionException(None, "FUNC_NOT_FOUND", "Function " + token.value.as_string + " was not found.")

        # Retrieve function parameters
        params = []
        param_count = stack.pop().as_integer
        while param_count > 0:
            params.insert(0, stack.pop())
            param_count -= 1

        function_result = func.calculate(params, self.__variant_operations)
        stack.push(function_result)

        return True

    def __evaluate_logical(self, token: ExpressionToken, stack: CalculationStack) -> bool:

        if token.type == ExpressionTokenType.And:
            value2 = stack.pop()
            value1 = stack.pop()
            stack.push(self.__variant_operations.add(value1, value2))
            return True
        elif token.type == ExpressionTokenType.Or:
            value2 = stack.pop()
            value1 = stack.pop()
            stack.push(self.__variant_operations.or_(value1, value2))
            return True
        elif token.type == ExpressionTokenType.Xor:
            value2 = stack.pop()
            value1 = stack.pop()
            stack.push(self.__variant_operations.xor(value1, value2))
            return True
        elif token.type == ExpressionTokenType.Not:
            stack.push(self.__variant_operations.not_(stack.pop()))
            return True
        else:
            return False

    def __evaluate_arithmetical(self, token: ExpressionToken, stack: CalculationStack) -> bool:

        if token.type == ExpressionTokenType.Plus:
            value2 = stack.pop()
            value1 = stack.pop()
            stack.push(self.__variant_operations.add(value1, value2))
            return True
        elif token.type == ExpressionTokenType.Minus:
            value2 = stack.pop()
            value1 = stack.pop()
            stack.push(self.__variant_operations.sub(value1, value2))
            return True
        elif token.type == ExpressionTokenType.Star:
            value2 = stack.pop()
            value1 = stack.pop()
            stack.push(self.__variant_operations.mul(value1, value2))
            return True
        elif token.type == ExpressionTokenType.Slash:
            value2 = stack.pop()
            value1 = stack.pop()
            stack.push(self.__variant_operations.div(value1, value2))
            return True
        elif token.type == ExpressionTokenType.Percent:
            value2 = stack.pop()
            value1 = stack.pop()
            stack.push(self.__variant_operations.mod(value1, value2))
            return True
        elif token.type == ExpressionTokenType.Power:
            value2 = stack.pop()
            value1 = stack.pop()
            stack.push(self.__variant_operations.pow(value1, value2))
            return True
        elif token.type == ExpressionTokenType.Unary:
            stack.push(self.__variant_operations.negative(stack.pop()))
            return True
        elif token.type == ExpressionTokenType.ShiftLeft:
            value2 = stack.pop()
            value1 = stack.pop()
            stack.push(self.__variant_operations.lsh(value1, value2))
            return True
        elif token.type == ExpressionTokenType.ShiftRight:
            value2 = stack.pop()
            value1 = stack.pop()
            stack.push(self.__variant_operations.rsh(value1, value2))
            return True
        else:
            return False

    def __evaluate_boolean(self, token: ExpressionToken, stack: CalculationStack) -> bool:
        if token.type == ExpressionTokenType.Equal:
            value2 = stack.pop()
            value1 = stack.pop()
            stack.push(self.__variant_operations.equal(value1, value2))
            return True
        elif token.type == ExpressionTokenType.NotEqual:
            value2 = stack.pop()
            value1 = stack.pop()
            stack.push(self.__variant_operations.not_equal(value1, value2))
            return True
        elif token.type == ExpressionTokenType.More:
            value2 = stack.pop()
            value1 = stack.pop()
            stack.push(self.__variant_operations.more(value1, value2))
            return True
        elif token.type == ExpressionTokenType.Less:
            value2 = stack.pop()
            value1 = stack.pop()
            stack.push(self.__variant_operations.less(value1, value2))
            return True
        elif token.type == ExpressionTokenType.EqualMore:
            value2 = stack.pop()
            value1 = stack.pop()
            stack.push(self.__variant_operations.more_equal(value1, value2))
            return True
        elif token.type == ExpressionTokenType.EqualLess:
            value2 = stack.pop()
            value1 = stack.pop()
            stack.push(self.__variant_operations.less_equal(value1, value2))
            return True
        else:
            return False

    def __evaluate_other(self, token: ExpressionToken, stack: CalculationStack) -> bool:

        if token.type == ExpressionTokenType.In:
            value2 = stack.pop()
            value1 = stack.pop()
            stack.push(self.__variant_operations.in_(value2, value1))
            return True
        elif token.type == ExpressionTokenType.NotIn:
            value2 = stack.pop()
            value1 = stack.pop()
            rvalue = self.__variant_operations.in_(value2, value1)
            rvalue = Variant.from_boolean(not rvalue.as_boolean)
            stack.push(rvalue)
            return True
        elif token.type == ExpressionTokenType.Element:
            value2 = stack.pop()
            value1 = stack.pop()
            rvalue = self.__variant_operations.get_element(value1, value2)
            stack.push(rvalue)
            return True
        elif token.type == ExpressionTokenType.IsNull:
            rvalue = Variant(stack.pop().is_null())
            stack.push(rvalue)
            return True
        elif token.type == ExpressionTokenType.IsNotNull:
            rvalue = Variant(not stack.pop().is_null())
            stack.push(rvalue)
            return True
        else:
            return False
