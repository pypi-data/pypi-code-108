from . import VerboseManager


def verbosedecorator(n_steps: int, counter=False):
    """
    A decorator that starts and finishes verbose processes on your behalf.
    The function that verbosedecorator is attached to must have 'verbose' entered as a **kwarg.

    Parameters:
    -----------
    n_steps: int
        the number of verbose steps in your function (including those in subprocesses).
    counter: bool = False


    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                verbose = kwargs['verbose']
            except KeyError:
                verbose = 0

            verbose_manager = VerboseManager.instance(counter=counter)
            verbose_manager.start(n_steps, verbose)
            func(*args, **kwargs)
            verbose_manager.finish(func.__name__.title())

        return wrapper
    return decorator
