from functools import wraps


def autowire(**kwargs):
    """autowire annotation to be placed on top of __init__ method

    This decorator, by itself, doesn't do anything. However, it is used inside
    the Component creation where the arguments of this decorator are used
    to retrieve which instance has to be injected inside the new Component.

    InDepth:
    --------

    class InDepth(metaclass=Component)

        dep1: FirstComponent
        dep2: SecondComponent

        @autowire(dep1="other")
        def __init__(self, arg1, arg2, ...):
            pass

    In this example, the Component InDepth, after initialization, will have the dep1 injected
    with an instance of the Component FirstComponent that have the instance name "other".
    The field dep2 will be injected with the instance "default" of the Component SecondComponent.

    This is equivalent to use @autowire(dep1="other", dep2="default")

    This decorator will only have an effect when placed on top of a __init__ method
    inside a class that use the Component metaclass.

    :param kwargs: the parameter used for autowire instance mapping
    :return: the return of the __init__ method
    """
    def decorator_autowire(init):
        @wraps(init)
        def wrapper_decorator(*init_args, **init_kwargs):
            instance = init(*init_args, **init_kwargs)
            return instance
        return wrapper_decorator
    return decorator_autowire
