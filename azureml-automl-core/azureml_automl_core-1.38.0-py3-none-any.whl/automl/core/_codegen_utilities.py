# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Utility functions used for code generation."""
import ast
import inspect
import logging
import sys
from contextlib import contextmanager
from typing import Any, Callable, Dict, Iterable, Iterator, List, Optional, Tuple, Type

from azureml.automl.core.shared._diagnostics.contract import Contract


logger = logging.getLogger(__name__)


ImportInfoType = Tuple[str, str, Any]
import_cache = {}


def check_code_syntax(code: str) -> None:
    Contract.assert_non_empty(code, "The provided code was empty.", log_safe=True)
    node = ast.parse(code, "script.py", mode="exec")
    Contract.assert_non_empty(node, "The provided code was empty.", log_safe=True)


def get_function_source(func: Callable[..., Any]) -> List[str]:
    """
    Return the given function's source code as a list of strings.

    This function is subject to the same limitations as inspect.getsourcelines() - namely, it will not work for
    functions defined interactively.

    Imports should either be defined in the function or passed out of band.

    :param func: The function to return source code for
    :return: A list of lines containing the function source code
    """
    return inspect.getsource(func).split("\n")


def normalize_lines(lines: List[str]) -> List[str]:
    """
    Normalize a list of lines so that elements containing multiple lines are split.

    :param lines: The list of lines to normalize
    :return: A list of lines with newlines split
    """
    return "\n".join(lines).split("\n")


def indent_multiline_string(input_str: str, indent: int = 4) -> str:
    """
    Indent a multiline string to be used as a parameter value, except for the first line.

    :param input_str: The string to indent
    :param indent: The number of spaces to indent
    :return: The string with every line after the first being indented
    """
    lines = input_str.split("\n")
    if len(lines) <= 1:
        return input_str
    indented_lines = indent_lines(lines[1:], indent)
    return "\n".join([lines[0]] + indented_lines)


def indent_function_lines(lines: List[str], indent: int = 4) -> List[str]:
    """
    Indent a multiline string as if it were a function, indenting all lines except the first.

    :param lines: The string to indent
    :param indent: The number of spaces to indent
    :return: The string with every line being indented
    """
    normalized_lines = normalize_lines(lines)
    indented_lines = indent_lines(normalized_lines[1:], indent)
    return [normalized_lines[0]] + indented_lines


def indent_lines(lines: List[str], indent: int = 4) -> List[str]:
    """
    Indent a multiline string.

    :param lines: The string to indent
    :param indent: The number of spaces to indent
    :return: The string with every line being indented
    """
    normalized_lines = normalize_lines(lines)
    new_lines = [" " * indent + line for line in normalized_lines]
    return new_lines


def generate_repr_str(cls: "Type[Any]", params: Dict[str, Any], **kwargs: Any) -> str:
    """
    Generate an evaluatable string representation of this object.

    :param cls: The class of the object
    :param params: The parameters of the object (repr will be called on each value)
    :param kwargs: The parameters of the object (the value will be added as provided)
    :return: A string representation which can be executed to retrieve the same object
    """
    if len(params) == 0 and len(kwargs) == 0:
        return f"{cls.__name__}()"

    param_line = "    {}={}"

    assert set(kwargs.keys()).isdisjoint(set(params.keys()))

    init_params = [param_line.format(k, kwargs[k]) for k in kwargs] + [
        param_line.format(k, _override_repr(params[k], k)) for k in params
    ]

    init_params = [indent_multiline_string(line) for line in init_params]

    lines = [f"{cls.__name__}(\n", ",\n".join(init_params), "\n)"]
    return "".join(lines)


def get_import(obj: Any) -> ImportInfoType:
    """
    Get the information needed to import the class.

    :param obj: The object to get import information for
    :return: the module name, the class name, and the class object
    """
    # The provided object is already a callable
    if callable(obj):
        return obj.__module__, obj.__name__, obj

    # The provided object is a module.
    # __name__ will be set to the fully qualified name, so we can just split it apart
    if inspect.ismodule(obj):
        namespace_parts = obj.__name__.split(".")
        return ".".join(namespace_parts[:-1]), namespace_parts[-1], obj

    return obj.__class__.__module__, obj.__class__.__name__, obj.__class__


def get_recursive_imports(obj: Any) -> List[ImportInfoType]:
    """
    Get the information needed to import all classes required by this object.

    The object's params are traversed as a directed acyclic graph using depth-first search.
    Cycles will result in a stack overflow.

    This will not catch imports that are present in iterables which are not lists/sets/dicts.

    :param obj: The object to get import information for
    :return: a list containing module names, class names, and class objects
    """
    imports = set()
    if isinstance(obj, (list, set)):
        for item in obj:
            imports.update(get_recursive_imports(item))
    elif isinstance(obj, dict):
        for key in obj:
            imports.update(get_recursive_imports(key))
            val = obj[key]
            imports.update(get_recursive_imports(val))
    else:
        if not is_builtin_type(obj):
            imports.add(get_import(obj))
        if hasattr(obj, "_get_imports"):
            imports.update(obj._get_imports())
    return list(imports)


def is_builtin_type(obj: Any) -> bool:
    """
    Determine whether the given object is a built-in type (ints, bools, lists, dicts, etc).

    :param obj: The object to check
    :return: True if the object is a built-in type, False otherwise
    """
    module_name = obj.__class__.__module__
    return module_name in {"builtins", "__builtins__"}


def generate_import_statements(imports: Iterable[ImportInfoType]) -> List[str]:
    """
    Generate import statements for the given list of import tuples.

    Import statements will be deduplicated and sorted in lexicographical order.

    :param imports: An iterable containing tuples of (module name, object name, object)
    :return: a list of strings containing import statements
    """
    deduplicate_set = set()
    output = []
    for x in imports:
        statement = generate_import_statement(x)
        if statement in deduplicate_set:
            continue
        output.append(statement)
        deduplicate_set.add(statement)
    return sorted(output)


def generate_import_statement(import_info: ImportInfoType) -> str:
    """
    Generate an import statement for the given import tuple.

    If the module name is in a private namespace (starts with an underscore), the parent namespace is traversed
    until the object name is found in a public namespace. If the parent public namespaces do not contain the object,
    the private namespace will be used.

    Results from this function are cached on (module name, object name).

    :param import_info: A tuple of (module name, object name, object)
    :return: a string containing an import statement
    """
    module_name, obj_name, obj = import_info
    key = (module_name, obj_name)

    if key not in import_cache:
        module_namespace = module_name.split(".")
        while module_namespace[-1].startswith("_"):
            if len(module_namespace) == 1:
                break
            module = sys.modules.get(".".join(module_namespace[:-1]), None)
            if obj_name not in dir(module):
                break
            module_namespace = module_namespace[:-1]
        statement = f"from {'.'.join(module_namespace)} import {obj_name}"
        import_cache[key] = statement

    return import_cache[key]


def _sklearn_repr(self: Any, N_CHAR_MAX: int = sys.maxsize) -> str:
    return generate_repr_str(self.__class__, self.get_params(deep=False))


def reformat_dict(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply string representation workarounds to a dictionary for specific edge cases.

    :param params: The dictionary to reformat
    :return: A copy of the dictionary, with problematic values fixed
    """
    return {key: _apply_repr_workarounds(value, key) or value for key, value in params.items()}


def _apply_repr_workarounds(obj: Any, key_name: str) -> Optional[str]:
    """
    Apply any specific workarounds needed for proper string representation on this object.

    If no workaround was applied, return None. This is because indiscriminately applying repr(obj) otherwise may
    result in nonfunctional code, so the caller must handle this case explicitly.

    :param obj: The object to generate a string for
    :param key_name: The parameter name for which this object is for
    :return: A string representation of the object, if a workaround was applied, else None
    """
    if obj.__class__.__name__ == "ndarray":
        # This object uses numpy ndarray, so just make sure indentation is correct.
        # Note that ndarrays are represented using numpy.array() in repr, so that must be imported instead.
        return indent_multiline_string(repr(obj), len(key_name) + 1)

    # Handle NaN without us having to have spurious "from numpy import nan"
    # How this check works: https://stackoverflow.com/a/44154660
    if obj != obj:
        return "numpy.nan"

    # Handle timeseries param dict.
    # Anything of type pd.DateOffset needs to call freqstr.
    if isinstance(obj, dict):
        obj = obj.copy()
        for key in obj:
            if hasattr(obj[key], "freqstr"):
                obj[key] = obj[key].freqstr
        return repr(obj)

    # Handle all the workarounds needing string representation below.
    repr_str = repr(obj)

    # This is a bit of a temporary workarounds to handle numpy dtype objects.
    # We can't monkeypatch dtype objects because they use native code + __slots__, which makes them unpatchable
    # TODO: interface to handle custom code generation behavior for non-AutoML objects
    if key_name == "dtype" and repr_str.startswith("<"):
        return f"{obj.__module__}.{obj.__name__}"

    # Workaround to handle DataTransformer._wrap_in_lst
    # One generic way to do this is to pickle the function and dump the string, but that's not acceptable here
    # Second way to handle this is to use inspect.getsource(), but then we would need to define another function
    # in the generated code and code gen doesn't currently have a signaling mechanism to allow for this.
    # Third way is to use a lambda, but that makes the resulting model unpicklable.
    if key_name == "tokenizer" and "._wrap_in_lst" in repr_str:
        return "DataTransformer._wrap_in_lst"

    return None


def _override_repr(obj: Any, key_name: str) -> str:
    """
    Generate an evaluatable string representation of this object, overriding __repr__() for sklearn BaseEstimators.

    :param obj: The object to generate a string for
    :param key_name: The parameter name for which this object is for
    :return: A string representation of the object
    """
    with use_custom_repr():
        # _apply_repr_workarounds will return None if no workaround was applied. Fallback to repr(obj) in that case.
        repr_str = _apply_repr_workarounds(obj, key_name) or repr(obj)

        return repr_str


@contextmanager
def use_custom_repr(cls: Any = None, func: Callable[..., str] = _sklearn_repr) -> Iterator[Callable[..., str]]:
    """
    Override __repr__ methods in external code and install needed workarounds.

    :return:
    """
    if cls is None:
        from sklearn.base import BaseEstimator

        cls = BaseEstimator

    old_values = {}
    set_option = None

    try:
        import pandas as pd
        set_option = pd.set_option
        desired_values = {
            "display.max_seq_items": None,
            "display.width": 120
        }
        for key in desired_values:
            old_values[key] = pd.get_option(key)
            set_option(key, desired_values[key])
    except ImportError:
        logger.warning("Unable to set pandas options.")

    old_repr = cls.__repr__
    cls.__repr__ = func
    try:
        yield old_repr
    finally:
        cls.__repr__ = old_repr

    if set_option is not None:
        for key in old_values:
            set_option(key, old_values[key])
