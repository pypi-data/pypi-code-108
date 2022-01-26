# -*- coding: utf-8 -*-

import math
import random
from datetime import datetime
from typing import List

from pip_services3_expressions.calculator.ExpressionException import ExpressionException
from pip_services3_expressions.calculator.functions.DelegatedFunction import DelegatedFunction
from pip_services3_expressions.calculator.functions.FunctionCollection import FunctionCollection
from pip_services3_expressions.variants.IVariantOperations import IVariantOperations
from pip_services3_expressions.variants.Variant import Variant
from pip_services3_expressions.variants.VariantType import VariantType


class DefaultFunctionCollection(FunctionCollection):
    """
    Implements a list filled with standard functions.
    """

    def __init__(self):
        super(DefaultFunctionCollection, self).__init__()

        self.add(DelegatedFunction("Ticks", self._ticks_function_calculator))
        self.add(DelegatedFunction("TimeSpan", self._time_span_function_calculator))
        self.add(DelegatedFunction("Now", self.__now_function_calculator))
        self.add(DelegatedFunction("Date", self.__date_function_calculator))
        self.add(DelegatedFunction("DayOfWeek", self.__day_of_week_function_calculator))
        self.add(DelegatedFunction("Min", self.__min_function_calculator))
        self.add(DelegatedFunction("Max", self.__max_functional_calculator))
        self.add(DelegatedFunction("Sum", self.__sum_function_calculator))
        self.add(DelegatedFunction("If", self.__if_function_calculator))
        self.add(DelegatedFunction("Choose", self.__choose_function_calculator))
        self.add(DelegatedFunction("E", self.__e_function_calculator))
        self.add(DelegatedFunction("Pi", self.__pi_function_calculator))
        self.add(DelegatedFunction("Rnd", self.__rnd_function_calculator))
        self.add(DelegatedFunction("Random", self.__rnd_function_calculator))
        self.add(DelegatedFunction("Abs", self.__abs_function_calculator))
        self.add(DelegatedFunction("Acos", self.__acos_functional_calculator))
        self.add(DelegatedFunction("Asin", self.__asin_functional_calculator))
        self.add(DelegatedFunction("Atan", self.__atan_functional_calculator))
        self.add(DelegatedFunction("Exp", self.__exp_functional_calculator))
        self.add(DelegatedFunction("Log", self.__log_functional_calculator))
        self.add(DelegatedFunction("Ln", self.__log_functional_calculator))
        self.add(DelegatedFunction("Log10", self.__log10_functional_calculator))
        self.add(DelegatedFunction("Ceil", self.__ceil_functional_calculator))
        self.add(DelegatedFunction("Ceiling", self.__ceil_functional_calculator))
        self.add(DelegatedFunction("Floor", self.__floor_functional_calculator))
        self.add(DelegatedFunction("Round", self.__round_functional_calculator))
        self.add(DelegatedFunction("Trunc", self.__trunc_functional_calculator))
        self.add(DelegatedFunction("Truncate", self.__trunc_functional_calculator))
        self.add(DelegatedFunction("Cos", self.__cos_functional_calculator))
        self.add(DelegatedFunction("Sin", self.__sin_functional_calculator))
        self.add(DelegatedFunction("Tan", self.__tan_functional_calculator))
        self.add(DelegatedFunction("Sqr", self.__sqrt_functional_calculator))
        self.add(DelegatedFunction("Sqrt", self.__sqrt_functional_calculator))
        self.add(DelegatedFunction("Empty", self.__empty_functional_calculator))
        self.add(DelegatedFunction("Null", self.__null_functional_calculator))
        self.add(DelegatedFunction("Contains", self.__contains_functional_calculator))
        self.add(DelegatedFunction("Array", self.__array_functional_calculator))

    def _check_param_count(self, params: List[Variant], expected_param_count: int):
        """
        Checks if params contains the correct number of function parameters (must be stored on the top of the params).

        :param params: A list of function parameters.
        :param expected_param_count: The expected number of function parameters.
        """
        param_count = len(params)
        if expected_param_count != param_count:
            raise ExpressionException(None, "WRONG_PARAM_COUNT",
                                      f"Expected {expected_param_count} parameters but was found {param_count}")

    def _get_parameter(self, params: List[Variant], param_index: int) -> Variant:
        """
        Gets function parameter by it's index.

        :param params: A list of function parameters.
        :param param_index: Index for the function parameter (0 for the first parameter).
        
        :return: Function parameter value.
        """
        return params[param_index]

    def _ticks_function_calculator(self, params: List[Variant], variant_operations: IVariantOperations) -> Variant:
        self._check_param_count(params, 0)
        return Variant.from_long(int(datetime.now().timestamp() / 1000))

    def _time_span_function_calculator(self, params: List[Variant], variant_operations: IVariantOperations) -> Variant:
        param_count = len(params)
        if param_count not in [1, 3, 4, 5]:
            raise ExpressionException(None, "WRONG_PARAM_COUNT", "Expected 1, 3, 4 or 5 parameters")

        result = Variant()

        if param_count == 1:
            value = variant_operations.convert(self._get_parameter(params, 0), VariantType.Long)
            result.as_time_span = value.as_long
        elif param_count > 2:
            value1 = variant_operations.convert(self._get_parameter(params, 0), VariantType.Long)
            value2 = variant_operations.convert(self._get_parameter(params, 1), VariantType.Long)
            value3 = variant_operations.convert(self._get_parameter(params, 2), VariantType.Long)

            value4 = variant_operations.convert(self._get_parameter(params, 3),
                                                VariantType.Long) if param_count > 3 else Variant.from_long(0)
            value5 = variant_operations.convert(self._get_parameter(params, 4),
                                                VariantType.Long) if param_count > 4 else Variant.from_long(0)

            result.as_time_span = (((value1.as_long * 24 + value2.as_long)
                                    * 60 + value3.as_long) * 60 + value4.as_long) * 1000 + value5.as_long
        return result

    def __now_function_calculator(self, params: List[Variant], variant_operations: IVariantOperations) -> Variant:

        self._check_param_count(params, 0)
        return Variant.from_datetime(datetime.now())

    def __date_function_calculator(self, params: List[Variant], variant_operations: IVariantOperations) -> Variant:
        param_count = len(params)
        if param_count < 1 or param_count > 7:
            raise ExpressionException(None, "WRONG_PARAM_COUNT", "Expected from 1 to 7 parameters")

        if param_count == 1:
            value = variant_operations.convert(self._get_parameter(params, 0), VariantType.Long)
            result = Variant.from_datetime(datetime.fromtimestamp(value.as_long * 1000))
            return result

        value1 = variant_operations.convert(self._get_parameter(params, 0), VariantType.Integer)
        value2 = variant_operations.convert(self._get_parameter(params, 1),
                                            VariantType.Integer) if param_count > 1 else Variant.from_integer(1)
        value3 = variant_operations.convert(self._get_parameter(params, 2),
                                            VariantType.Integer) if param_count > 2 else Variant.from_integer(1)
        value4 = variant_operations.convert(self._get_parameter(params, 3),
                                            VariantType.Integer) if param_count > 3 else Variant.from_integer(0)
        value5 = variant_operations.convert(self._get_parameter(params, 4),
                                            VariantType.Integer) if param_count > 4 else Variant.from_integer(0)
        value6 = variant_operations.convert(self._get_parameter(params, 5),
                                            VariantType.Integer) if param_count > 5 else Variant.from_integer(0)
        value7 = variant_operations.convert(self._get_parameter(params, 6),
                                            VariantType.Integer) if param_count > 6 else Variant.from_integer(0)

        date = datetime(value1.as_integer, value2.as_integer - 1, value3.as_integer,
                        value4.as_integer, value5.as_integer, value6.as_integer, value7.as_integer)

        return Variant.from_datetime(date)

    def __day_of_week_function_calculator(self, params: List[Variant],
                                          variant_operations: IVariantOperations) -> Variant:
        self._check_param_count(params, 1)
        value = variant_operations.convert(self._get_parameter(params, 0), VariantType.DateTime)
        date = value.as_datetime
        return Variant.from_integer(date.day)

    def __min_function_calculator(self, params: List[Variant], variant_operations: IVariantOperations) -> Variant:
        param_count = len(params)
        if param_count < 2:
            raise ExpressionException(None, "WRONG_PARAM_COUNT",
                                      "Expected at least 2 parameters")
        result = self._get_parameter(params, 0)
        for i in range(1, param_count):
            value = self._get_parameter(params, i)
            if variant_operations.more(result, value).as_boolean:
                result = value

        return result

    def __max_functional_calculator(self, params: List[Variant], variant_operations: IVariantOperations) -> Variant:
        param_count = len(params)
        if param_count < 2:
            raise ExpressionException(None, "WRONG_PARAM_COUNT",
                                      "Expected at least 2 parameters")
        result = self._get_parameter(params, 0)
        for i in range(1, param_count):
            value = self._get_parameter(params, i)
            if variant_operations.less(result, value).as_boolean:
                result = value

        return result

    def __sum_function_calculator(self, params: List[Variant], variant_operations: IVariantOperations) -> Variant:
        param_count = len(params)
        if param_count < 2:
            raise ExpressionException(None, "WRONG_PARAM_COUNT",
                                      "Expected at least 2 parameters")
        result = self._get_parameter(params, 0)
        for i in range(1, param_count):
            value = self._get_parameter(params, i)
            result = variant_operations.add(result, value)

        return result

    def __if_function_calculator(self, params: List[Variant], variant_operations: IVariantOperations) -> Variant:
        self._check_param_count(params, 3)
        value1 = self._get_parameter(params, 0)
        value2 = self._get_parameter(params, 1)
        value3 = self._get_parameter(params, 2)
        condition = variant_operations.convert(value1, VariantType.Boolean)
        return value2 if condition.as_boolean else value3

    def __choose_function_calculator(self, params: List[Variant], variant_operations: IVariantOperations) -> Variant:
        param_count = len(params)
        if param_count < 3:
            raise ExpressionException(None, "WRONG_PARAM_COUNT",
                                      "Expected at least 3 parameters")

        value1 = self._get_parameter(params, 0)
        condition = variant_operations.convert(value1, VariantType.Integer)
        param_index = condition.as_integer

        if param_count < param_index + 1:
            raise ExpressionException(None, "WRONG_PARAM_COUNT",
                                      "Expected at least " + str((param_index + 1)) + " parameters")

        return self._get_parameter(params, param_index)

    def __e_function_calculator(self, params: List[Variant], variant_operations: IVariantOperations) -> Variant:
        self._check_param_count(params, 0)
        return Variant(math.e)

    def __pi_function_calculator(self, params: List[Variant], variant_operations: IVariantOperations) -> Variant:
        self._check_param_count(params, 0)
        return Variant(math.pi)

    def __rnd_function_calculator(self, params: List[Variant], variant_operations: IVariantOperations) -> Variant:
        self._check_param_count(params, 0)
        return Variant(random.random())

    def __abs_function_calculator(self, params: List[Variant], variant_operations: IVariantOperations) -> Variant:

        self._check_param_count(params, 1)
        value = self._get_parameter(params, 0)
        result = Variant()

        if value.type == VariantType.Integer:
            result.as_integer = abs(value.as_integer)
        elif value.type == VariantType.Long:
            result.as_integer = abs(value.as_long)
        elif value.type == VariantType.Float:
            result.as_integer = abs(value.as_float)
        elif value.type == VariantType.Double:
            result.as_integer = abs(value.as_double)
        else:
            value = variant_operations.convert(value, VariantType.Float)
            result.as_float = abs(value.as_float)

        return result

    def __acos_functional_calculator(self, params: List[Variant], variant_operations: IVariantOperations) -> Variant:

        self._check_param_count(params, 1)
        value = variant_operations.convert(self._get_parameter(params, 0), VariantType.Float)
        return Variant(math.acos(value.as_float))

    def __asin_functional_calculator(self, params: List[Variant], variant_operations: IVariantOperations) -> Variant:

        self._check_param_count(params, 1)
        value = variant_operations.convert(self._get_parameter(params, 0), VariantType.Float)
        return Variant(math.asin(value.as_float))

    def __atan_functional_calculator(self, params: List[Variant], variant_operations: IVariantOperations) -> Variant:
        self._check_param_count(params, 1)
        value = variant_operations.convert(self._get_parameter(params, 0), VariantType.Float)
        return Variant(math.atan(value.as_float))

    def __exp_functional_calculator(self, params: List[Variant], variant_operations: IVariantOperations) -> Variant:

        self._check_param_count(params, 1)
        value = variant_operations.convert(self._get_parameter(params, 0), VariantType.Float)
        return Variant(math.exp(value.as_float))

    def __log_functional_calculator(self, params: List[Variant], variant_operations: IVariantOperations) -> Variant:
        self._check_param_count(params, 1)
        value = variant_operations.convert(self._get_parameter(params, 0), VariantType.Float)
        return Variant(math.log(value.as_float))

    def __log10_functional_calculator(self, params: List[Variant], variant_operations: IVariantOperations) -> Variant:
        self._check_param_count(params, 1)
        value = variant_operations.convert(self._get_parameter(params, 0), VariantType.Float)
        return Variant(math.log10(value.as_float))

    def __ceil_functional_calculator(self, params: List[Variant], variant_operations: IVariantOperations) -> Variant:
        self._check_param_count(params, 1)
        value = variant_operations.convert(self._get_parameter(params, 0), VariantType.Float)
        return Variant(math.ceil(value.as_float))

    def __floor_functional_calculator(self, params: List[Variant], variant_operations: IVariantOperations) -> Variant:
        self._check_param_count(params, 1)
        value = variant_operations.convert(self._get_parameter(params, 0), VariantType.Float)
        return Variant(math.floor(value.as_float))

    def __round_functional_calculator(self, params: List[Variant], variant_operations: IVariantOperations) -> Variant:
        self._check_param_count(params, 1)
        value = variant_operations.convert(self._get_parameter(params, 0), VariantType.Float)
        return Variant(round(value.as_float))

    def __trunc_functional_calculator(self, params: List[Variant], variant_operations: IVariantOperations) -> Variant:
        self._check_param_count(params, 1)
        value = variant_operations.convert(self._get_parameter(params, 0), VariantType.Float)
        return Variant.from_integer(math.trunc(value.as_float))

    def __cos_functional_calculator(self, params: List[Variant], variant_operations: IVariantOperations) -> Variant:

        self._check_param_count(params, 1)
        value = variant_operations.convert(self._get_parameter(params, 0), VariantType.Float)
        return Variant(math.cos(value.as_float))

    def __sin_functional_calculator(self, params: List[Variant], variant_operations: IVariantOperations) -> Variant:
        self._check_param_count(params, 1)
        value = variant_operations.convert(self._get_parameter(params, 0), VariantType.Float)
        return Variant(math.sin(value.as_float))

    def __tan_functional_calculator(self, params: List[Variant], variant_operations: IVariantOperations) -> Variant:
        self._check_param_count(params, 1)
        value = variant_operations.convert(self._get_parameter(params, 0), VariantType.Float)
        return Variant(math.tan(value.as_float))

    def __sqrt_functional_calculator(self, params: List[Variant], variant_operations: IVariantOperations) -> Variant:
        self._check_param_count(params, 1)
        value = variant_operations.convert(self._get_parameter(params, 0), VariantType.Float)
        return Variant(math.sqrt(value.as_float))

    def __empty_functional_calculator(self, params: List[Variant], variant_operations: IVariantOperations) -> Variant:
        self._check_param_count(params, 1)
        value = variant_operations.convert(self._get_parameter(params, 0))
        return Variant(value.is_empty())

    def __null_functional_calculator(self, params: List[Variant], variant_operations: IVariantOperations) -> Variant:
        self._check_param_count(params, 0)
        return Variant()

    def __contains_functional_calculator(self, params: List[Variant],
                                         variant_operations: IVariantOperations) -> Variant:
        self._check_param_count(params, 2)
        container_str = variant_operations.convert(self._get_parameter(params, 0), VariantType.String)
        substring = variant_operations.convert(self._get_parameter(params, 1), VariantType.String)

        if container_str.is_empty() or container_str.is_null:
            return Variant(False)

        return Variant(substring.as_string in container_str.as_string)

    def __array_functional_calculator(self, params: List[Variant], variant_operations: IVariantOperations) -> Variant:
        return Variant.from_array(params)
