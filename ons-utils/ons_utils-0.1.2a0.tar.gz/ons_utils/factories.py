"""Factory functions to generate other functions.

Provides:

* :func:`args_kwargs_transformer_factory` - A factory for creating
  decorators that transform function arguments.
"""
import inspect
import functools

from typing import Any, Callable, Mapping, Optional, Sequence, Union

from .generic import list_convert


def args_kwargs_transformer_factory(
    transform_func: Callable[[Any], Any],
) -> Callable:
    """Return a decorator to transform function parameters.

    This is a factory function for generating new decorators that
    transform parameters.

    Parameters
    ----------
    transform_func : callable
        A function that takes one input and transforms it.

    Returns
    -------
    callable
        A decorator that can be used to decorate functions and transform
        their arguments before use.
    """
    # See explanation of the pattern used here:
    # https://realpython.com/primer-on-python-decorators/#both-please-but-never-mind-the-bread
    def args_kwargs_transformer_decorator(
        # The _func arg acts as a marker, noting whether the decorator
        # has been called with arguments or not.
        _func=None,
        # This * means that the remaining arguments can't be called as
        # positional arguments.
        *,
        include: Optional[Union[str, Sequence[str]]] = None,
        exclude: Optional[Union[str, Sequence[str]]] = None,
    ) -> Callable:
        """Transform arguments corresponding to given parameter names.

        Intended to be used as a decorator to transform a function's
        arguments before the function uses them within the function
        body. Can be passed with arguments to specify particular
        parameters to exclude or include in the transformations. If
        passed without arguments then all parameters will be
        transformed.

        Parameters
        ----------
        include : str or sequence of str
            The param name/s to transform. Cannot be used in conjunction
            with ``exclude``.
        exclude : str or sequence of str
            The param name/s to transform. Cannot be used in conjunction
            with ``include``.

        Returns
        -------
        callable
            The decorated function with arguments transformed.
        """
        if include and exclude:
            raise ValueError(
                'only one of include or exclude parameters can be specified'
                ' but both have been specified'
            )
        elif include:
            conditional = lambda x: x in list_convert(include)
        elif exclude:
            conditional = lambda x: x not in list_convert(exclude)
        else:
            # Returns True no matter what.
            conditional = lambda _: True

        def caller(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs) -> Callable:
                # Need an iterator to pass into the transform funcs and
                # None is not an iterator.
                args = args if args else []
                kwargs = kwargs if kwargs else {}

                # Grab the func param names as a list of strings.
                varnames = inspect.getfullargspec(func).args

                args = _transform_args(
                    args, varnames, transform_func, conditional
                )
                kwargs = _transform_kwargs(kwargs, transform_func, conditional)

                return func(*args, **kwargs)
            return wrapper

        # Remaining boilerplate to allow decorator to be called with or
        # without arguments.
        return caller if _func is None else caller(_func)

    return args_kwargs_transformer_decorator


def _transform_args(
    args: Sequence[Any],
    varnames: Sequence[str],
    transform_func: Callable[[Any], Any],
    conditional: Callable[[str], bool] = lambda _: True,
) -> Sequence[Any]:
    """Transform given args if condition is met."""
    return [
        transform_func(arg)
        if conditional(varnames[i]) and arg is not None
        else arg
        for i, arg in enumerate(args)
    ]


def _transform_kwargs(
    kwargs: Mapping[str, Any],
    transform_func: Callable[[Any], Any],
    conditional: Callable[[str], bool] = lambda _: True,
) -> Mapping[str, Any]:
    """Transform given kwargs if condition is met."""
    return {
        k: transform_func(kwarg)
        if conditional(k) and kwargs is not None
        else kwarg
        for k, kwarg in kwargs.items()
    }
