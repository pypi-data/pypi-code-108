import inspect
import sys


def retrieve_argname(var: object) -> str:
    """Retrieve the name of the argument passed to the function.

    Args:
        var (object): The argument passed to the function.
    Returns:
        str: The name of the argument.

    Example:

        >>> def foo(a):
                n = retrieve_argname(a)
        ...     return f"{n}'s value is {a}"
        ...
        >>> x = 42
        >>> foo(x)
        'x's value is 42
    """
    callers_local_vars = inspect.currentframe().f_back.f_back.f_locals.items()
    return [
        var_name for var_name, var_val in callers_local_vars if var_val is var
    ][0]


def retrive_varname(var):
    callers_local_vars = inspect.currentframe().f_back.f_locals.items()
    return [
        var_name for var_name, var_val in callers_local_vars if var_val is var
    ][0]


def return_names(name=None):
    if not name:
        raise ValueError("Argument 'name' is required")
    return [n for n in sys.modules[name].__dict__ if not n.startswith("__")]