from __future__ import annotations

from typing import Any, Callable, Optional, Type, TypeVar, Union

from decorator import decorator

from ..common import TAUTOLOGY, VOID
from .service import Service

T = TypeVar("T")
Predicate = Callable[..., bool]

ACTION = Callable[..., None]


@decorator
def before(
    func,
    do: Optional[ACTION] = VOID,
    when: Optional[Predicate] = TAUTOLOGY,
    *args: Any,
    **kwargs: Any,
):
    """
    Add a hook before decorated function's execution.
    """
    if when(*args, **kwargs):
        do(*args, **kwargs)

    return func(*args, **kwargs)


@decorator
def raises(
    func,
    do: Optional[ACTION] = VOID,
    when: Optional[Predicate] = TAUTOLOGY,
    expected_exception: Type[BaseException] = Exception,
    exception_param_name: str = "_exception_",
    *args: Any,
    **kwargs: Any,
):
    """
    Add a hook to catch expected exception.
    """
    try:
        return func(*args, **kwargs)
    except expected_exception as exception:
        if when(*args, **{exception_param_name: exception}, **kwargs):
            if isinstance(
                result := do(*args, **{exception_param_name: exception}, **kwargs),
                BaseException,
            ):
                raise result from exception
            else:
                return result


@decorator
def after(
    func,
    do: Optional[ACTION] = VOID,
    when: Optional[Predicate] = TAUTOLOGY,
    result_param_name: str = "_result_",
    *args: Any,
    **kwargs: Any,
):
    """
    Add a hook after decorated function's execution.

    Result of decorated function is available through designated `result_param_name`.
    """
    result = func(*args, **kwargs)

    if when(*args, **{result_param_name: result}, **kwargs):
        do(*args, **{result_param_name: result}, **kwargs)

    return result


ReactAt = Union[before, after, raises]


class Reaction(Service):
    """
    Reaction is an abstract class that should be subclassed to use.

    `react` or `when` should be overridden with desired behavior.

    `bind` can be called to produce a decorator that binds this handler to a function.
    """

    def when(self, *args: Any, **kwargs: Any) -> bool:
        """
        Determines whether `react` method should be called.
        """
        return True

    def react(self, *args: Any, **kwargs: Any) -> None:
        """
        Perform an action at specific timings of registered function.
        """
        pass

    def bind(self, at: ReactAt, **kwargs: Any):
        return at(do=self.react, when=self.when, **kwargs)


class _NoReaction_(Reaction):
    """
    A special subclass of Reaction that performs nothing.
    """

    def when(self, *args, **kwargs):
        return False


NO_REACTION = _NoReaction_()


@decorator
def bind_reaction(
    func,
    at: ReactAt = after,
    reaction: Union[Reaction, Callable[..., Reaction]] = NO_REACTION,
    *args: Any,
    **kwargs: Any,
):
    """
    Different from `Reaction.bind`, `bind_reaction` offers a possibility of
    dynamically resolve reaction -- besides passing a instance of `Reaction`,
    `reaction` can accept a callable that finds the reaction with the
    provided arguments.
    """
    if callable(reaction):
        reaction = reaction(*args, **kwargs)

    return reaction.bind(at, **kwargs)(func)(*args, **kwargs)


def DEFAULT_FINDER(name: str, instance: Any, *args: Any, **kwargs: Any) -> Reaction:
    return getattr(instance, name)


@decorator
def bind_named_reaction(
    func,
    at: ReactAt = after,
    name: str = "_MISSING_",
    finder: Callable[..., Reaction] = DEFAULT_FINDER,
    *args: Any,
    **kwargs: Any,
):
    """
    An extension of `bind_reaction` that supports finding a Reaction dynamically with a name string.

    The default finder will look at the attribute with specified name in
    first method argument, which is suitable for decorating class methods
    where first method argument is the class instance.
    """
    reaction: Reaction = finder(name, *args, **kwargs)
    return reaction.bind(at, **kwargs)(func)(*args, **kwargs)


if __name__ == "__main__":
    import doctest

    doctest.testmod()
