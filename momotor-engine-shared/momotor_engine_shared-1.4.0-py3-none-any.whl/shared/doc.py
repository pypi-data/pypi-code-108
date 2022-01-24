__all__ = ['annotate_docstring']


def annotate_docstring(*args, **kwargs):
    """ Decorator to help write better docstrings.

    The arguments of the decorator are applied using :py:meth:`str.format`
    to the __doc__ of the class or method decorated.

    Example:

    .. code:: python

       logger = getLogger('some.logger')

       @annotate_docstring(logger=logger)
       class SomeClass:
          \"\"\" This class does some logging on the "{logger.name}" logger
          \"\"\"

    In the example above, the docstring will read:

    .. code:: text

       This class does some logging on the "some.logger" logger

    :param args: the arguments for :py:meth:`str.format`
    :param kwargs: the keyword arguments for :py:meth:`str.format`
    :return: the decorated object with annotated doc string
    """

    def decorator(klass):
        if klass.__doc__ is not None:
            klass.__doc__ = klass.__doc__.format(*args, **kwargs)
        return klass

    return decorator
