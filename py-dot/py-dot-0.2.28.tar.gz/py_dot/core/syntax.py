from functools import wraps

def outer_of(inner_decorator):
    """ Create Decorator as Outer Wrapped of argument

    >>> def foo(f):
    ...    def d():
    ...        print('inner')
    ...        return f()
    ...
    ...    return d
    ...
    ...
    ...@outer_of(foo)
    ...def bar(f):
    ...    def d():
    ...        print('outer')
    ...        return f()
    ...
    ...    return d
    ...
    ...@bar
    ...def bar_and_foo():
    ...    pass

    :param inner_decorator: Inner Decorator of Outer Decorator
    :return:
    """

    def outer_wrap(outer_decorator):
        def inner_wrap(callback):
            child_decorated = outer_decorator(inner_decorator(callback))

            @wraps(callback)
            def decorated_wrap(*args, **child_kwargs):
                return child_decorated(*args, **child_kwargs)

            return decorated_wrap

        return inner_wrap

    return outer_wrap
