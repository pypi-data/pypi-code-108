from wrapt import decorator

from inspect import getfullargspec
from typing import Generator, Callable, Any, Union, Type

from .constants import ErrorMessages
from .methods import Methods


class Extension:
    @staticmethod
    def can_extend(target_cls: Type["Extendable"]) -> bool:
        """
        Should return a bool indicating whether this Extension can be applied to the target class
        """

        raise NotImplementedError

    @staticmethod
    def extend(target_cls: Type["Extendable"]) -> None:
        """
        Any modification of the target class should take place in this function
        """

        pass

    @staticmethod
    def _wrap(target_cls: Type["Extendable"], method_name: str,
              gen_func: Callable[["Extendable", Any, Any], Generator[None, Any, None]]) -> None:
        """
        Used to wrap an existing method on the target class.
        Passes copies of the method parameters to the generator function provided.
        The generator function should yield once,
        with the yield statement receiving a copy of the result of executing the core method
        """

        method = getattr(target_cls, method_name)
        method_args = getfullargspec(method).args

        if len(method_args) == 0 or method_args[0] != "self":
            ErrorMessages.wrap_static(method_name)

        @decorator  # This will preserve the original method signature when wrapping the method
        def wrapper(func, self, args, kwargs):
            gen = gen_func(self, *Methods.try_copy(args), **Methods.try_copy(kwargs))
            next(gen)

            result = func(*args, **kwargs)

            try:
                gen.send(Methods.try_copy(result))
            except StopIteration:
                pass

            return result

        setattr(target_cls, method_name, wrapper(method))

    @staticmethod
    def _set(target: Union[Type["Extendable"], "Extendable"], attribute_name: str, value: Any) -> None:
        """
        Used to safely add new attributes to an extendable class or instance. In contrast with assigning them directly,
        this method will raise an error if the attribute already exists (for example, if another extension added it)
        to ensure compatibility issues are flagged and can be dealt with easily
        """

        if hasattr(target, attribute_name):
            ErrorMessages.duplicate_attribute(attribute_name)

        setattr(target, attribute_name, value)
