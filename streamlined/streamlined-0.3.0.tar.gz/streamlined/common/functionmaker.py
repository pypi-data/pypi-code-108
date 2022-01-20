from itertools import chain
from typing import Callable, TypeVar

from decorator import FunctionMaker

T = TypeVar("T")


def create_identity_function(parameter_name: str) -> Callable[[T], T]:
    """
    Create a function that takes a parameter with given name and
    return that argument.

    New function will be named: `get_<parameter_name>`

    >>> get_foo = create_identity_function('foo')
    >>> get_foo('bar')
    'bar'
    """
    return FunctionMaker.create(
        f"get_{parameter_name}({parameter_name})",
        f"return {parameter_name}",
        dict(),
        addsource=True,
    )


def rewrite_function_parameters(
    function: Callable[..., T], function_newname: str, *args: str, **kwargs: str
) -> Callable[..., T]:
    """
    Provide functionality to rewrite a function's parameter list.

    >>> exponent = rewrite_function_parameters(pow, 'exponent', 'x', 'y')
    >>> exponent(2, 4) == pow(2, 4)
    True
    """
    parameters = ", ".join(chain(args, kwargs.values()))
    arguments = ", ".join(
        chain(args, (f"{arg_name}={param_name}" for arg_name, param_name in kwargs.items()))
    )
    return FunctionMaker.create(
        f"{function_newname}({parameters})",
        f"return function({arguments})",
        dict(function=function, _call_=function),
        addsource=True,
    )


if __name__ == "__main__":
    import doctest

    doctest.testmod()
