#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""TBW."""
import importlib
import logging
import typing as t
from ast import literal_eval
from collections import abc
from numbers import Number

import numpy as np

__all__ = ["evaluate_reference", "eval_range", "eval_entry"]


def evaluate_reference(reference_str: str) -> t.Callable:
    """Evaluate a module's class, function, or constant.

    :param str reference_str: the python expression to
        evaluate or retrieve the module attribute reference to.
        This is usually a reference to a class or a function.
    :return: the module attribute or object.
    :rtype: object
    :raises ImportError: if reference_str cannot be evaluated to a callable.
    """
    if not reference_str:
        raise ImportError("Empty string cannot be evaluated")

    if "." not in reference_str:
        raise ImportError("Missing module path")

    # reference to a module class, function, or constant
    module_str, function_str = reference_str.rsplit(".", 1)
    try:
        module = importlib.import_module(module_str)

        reference = getattr(module, function_str)  # type: t.Callable
        assert callable(reference)

        # if isinstance(reference, type):
        #     # this is a class type, instantiate it using default arguments.
        #     reference = reference()
    except ImportError as exc:
        raise ImportError(
            "Cannot import module: %r. exc: %s" % (module_str, str(exc))
        ) from exc
    except AttributeError as ex:
        raise ImportError(
            "Module: %s, does not contain %s" % (module_str, function_str)
        ) from ex

    return reference


def eval_range(values: t.Union[str, t.Sequence]) -> t.Sequence:
    """Evaluate a string representation of a list or numpy array.

    :param values:
    :return: list
    """
    if isinstance(values, str):
        if "numpy" in values:
            locals_dict = {"numpy": importlib.import_module("numpy")}
            globals_dict = None
            values_array = eval(values, globals_dict, locals_dict)  # type: np.ndarray

            # NOTE: the following casting is to ensure JSON serialization works
            # JSON does not accept numpy.int* or numpy.float* types.
            if values_array.dtype == float:
                values_lst = [float(value) for value in values_array]  # type: list
            elif values_array.dtype == int:
                values_lst = [int(value) for value in values_array]
            else:
                logging.warning(
                    "numpy data type is not a float or int: %r", values_array
                )
                raise NotImplementedError
        # Preventing any problems with evaluating _ as a variable in outer scope.
        elif values == "_":
            values_lst = ["_"]
        else:
            obj = eval(values)
            values_lst = list(obj)

    elif isinstance(values, abc.Sequence):
        values_lst = list(values)

    else:
        # values_lst = []
        raise NotImplementedError

    return values_lst


# TODO: Use 'numexpr.evaluate' ? See #331
def eval_entry(
    value: t.Union[str, Number, np.ndarray]
) -> t.Union[str, Number, np.ndarray]:
    """TBW.

    :param value:
    :return:
    """
    assert isinstance(value, (str, Number, list, np.ndarray))

    if isinstance(value, str):
        try:
            literal_eval(value)
        except (SyntaxError, ValueError, NameError):
            # ensure quotes in case of string literal value
            first_char = value[0]
            last_char = value[-1]

            if first_char != last_char or first_char not in ["'", '"']:
                value = '"' + value + '"'

        value = literal_eval(value)
        assert isinstance(value, (str, Number, np.ndarray))

    return value
