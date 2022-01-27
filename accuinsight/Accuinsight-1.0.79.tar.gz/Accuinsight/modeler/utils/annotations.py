def experimental(func):
    """
    Decorator for marking APIs experimental in the docstring.

    :param func: A function to mark
    :returns Decorated function.
    """
    notice = ".. Note:: Experimental: This method may change or " + \
             "be removed in a future release without warning.\n"
    func.__doc__ = notice + func.__doc__
    return func

