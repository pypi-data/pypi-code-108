import time
import warnings
from functools import wraps, update_wrapper
from typing import Any, Callable, List, Optional, TypeVar, Dict

from prototools.colorize import create_colors
from prototools.components import Border

FuncType = Callable[..., Any]
F = TypeVar('F', bound=FuncType)

PLUGINS: Dict[str, Callable] = dict()


class Counter:
    """Count the number of calls that a function does.

    Examples:
        Scripts::

            @Counter
            def update():
                print("Updated!")

            update()
            update()
            update()
        
        Output::

            Call 1 of 'update'
            Updated!
            Call 2 of 'update'
            Updated!
            Call 3 of 'update'
            Updated!
    """
    def __init__(self, function: F) -> None:
        update_wrapper(self, function)
        self.function = function
        self.calls = 0

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        self.calls += 1
        print(f"Call {self.calls} of {self.function.__name__!r}")
        return self.function(*args, **kwargs)


def debug(function: F) -> F:
    """Print the decorated function signature and its return value.

    Example:
        Script::
        
            @debug
            def say_hi(name):
                return f"Hi {name}!"

            say_hi("ProtoTools")

        Output::

            Calling: say_hi('ProtoTools')
            'say_hi' returned 'Hi ProtoTools!'
    """
    @wraps(function)
    def wrapper(*args, **kwargs):
        args_repr = [repr(a) for a in args]
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
        signature = ", ".join(args_repr + kwargs_repr)
        print(f"Calling: {function.__name__}({signature})")
        valor = function(*args, **kwargs)
        print(f"{function.__name__!r} returned {valor!r}")
        return valor
    return wrapper


def obsolete(message: str) -> None:
    """Decorate an obsolote function and sends a warning message.

    Example:
        Script::

            @obsolete("use 'g()' instead")
            def f():
                return "version 1.0"

            print(f())

        Output::

            DeprecationWarning: 
            Function 'f' is obsolete!, use 'g()' instead
    
    """
    def inner(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            warnings.warn(
                f"\nFunction '{function.__name__}' is obsolete!, {message}",
                category=DeprecationWarning, 
                stacklevel=2,
                )
            return function(*args, **kwargs)
        return wrapper
    return inner


def register(function: F) -> F:
    """Register a function as a plug-in.
    
    Example:
        Script::

            from prototools.decorators import PLUGINS, register

            @register
            def f():
                pass

            print(PLUGINS)

        OUTPUT::

            {'f': <function f at 0x00000258176C64C8>}
    """
    PLUGINS[function.__name__] = function
    return function


def slow_down(_function: F = None, *, seconds: int = 1):
    """Sleep 'n' seconds before calling the function.
    
    Example:
        Script::

            @slow_down(seconds=2)
            def f(n):
                if n < 1:
                    prin("End!")
                else:
                    print(n)
                    f(n-1)

            f(3)

        Output::
            
                3
                2
                1
                End!
    """
    def inner(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            time.sleep(seconds)
            return function(*args, **kwargs)
        return wrapper
    
    if _function is None:
        return inner
    else:
        return inner(_function)


def timer(
    _function: F = None,
    *,
    fg: Optional[str] = None,
    bg: Optional[str] = None,
):
    """Print the runtime of the decorated function.

    Args:
        fg (str, optional): Foreground color.
        bg (str, optional): Background color.

    Example:
        Script::

            @timer
            def f(n):
                for _ in range(n):
                    sum([x**2 for x in range(10_000)])

            f(10)

        Output::

            Finished 'f' in 0.0289 secs
    """
    def inner(function):
        if fg is None:
            colorize_ = create_colors(fg="white")
        else:
            colorize_ = create_colors(fg=fg)
        if bg:
            colorize_ = create_colors(fg=fg, bg=bg)
        @wraps(function)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            value = function(*args, **kwargs)
            end_time = time.time()
            run_time = end_time - start_time
            print(colorize_(
                f"Finished '{function.__name__!r}' in {run_time:.4f} secs"
            ))
            return value
        return wrapper
    if _function is None:
        return inner
    else:
        return inner(_function)


def repeat(_function: F = None, *, n: int = 2):
    """Repeat 'n' times the decorated function.

    Args:
        n (int): Number of repetitions.

    Example:
        Script::

            @repeat(4)
            def say_hi(name):
                print(f"Hi {name}!")

            say_hi("ProtoTools")

        Output::
            
            Hi ProtoTools!
            Hi ProtoTools!
            Hi ProtoTools!
            Hi ProtoTools!
    """
    def inner(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            for _ in range(n):
                value = function(*args, **kwargs)
            return value
        return wrapper
    if _function is None:
        return inner
    else:
        return inner(_function)


def singleton(cls):
    """Make a class a Singleton class (only one instance).
    
    Example:
        Script::

            @singleton
            class T:
                pass

        >>> a = T()
        >>> b = T()
        >>> id(a)
        2031647265608
        >>> id(b)
        2031647265608
        >>> a is b
        True
    """
    @wraps(cls)
    def wrapper(*args, **kwargs):
        if not wrapper.instance:
            wrapper.instance = cls(*args, **kwargs)
        return wrapper.instance
    wrapper.instance = None
    return wrapper


def banner(title: str, width = int, style: str = None):
    """Print a banner.

    Args:
        Title(str): Title of the banner.
        width (int): Ancho del banner.
        style (str, optional): Border style.

    Example:
        Script::

            @banner("ProtoTools", 12)
            def mensaje():
                return None

            mensaje()

        Output::

            ══════════════════
                ProtoTools    
            ══════════════════
    """
    if style is None:
        style = "double"
    border = Border(style)
    def inner(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            print(border.horizontal * width)
            value = function(*args, **kwargs)
            print(title.center(width))
            print(border.horizontal * width)
            return value
        return wrapper
    return inner


def inject(
    f: F,
    _function: F = None,
    *,
    values: List[Any] = None,
    after: bool = True
):
    """Inject a function into another function.

    Args:
        f (Callable): The function to inject.
        values (List[Any]): Function's arguments.
        after (bool): If True, inject after the function; otherwise,
            inject before the function.

    Example:
        Script::

            def f(s):
                print(s)

            @inject(f, values=("Ending",))
            @inject(f, values=("Starting",), after=False)
            def g(n):
                print(n**2)

            g(2)

        Output::

            Starting
            4
            Ending
    """
    def inner(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            if after:
                value = function(*args, **kwargs)
                if values is None:
                    f()
                else:
                    f(*values)
            else:
                if values is None:
                    f()
                else:
                    f(*values)
                value = function(*args, **kwargs)
            return value
        return wrapper
    if _function is None:
        return inner
    else:
        return inner(_function)


def retry(
    _function: F = None,
    *,
    tries: int = 3,
    default: Optional[Any] = None
):
    """Retry a function if it raises an exception.

    Args:
        tries (int): Number of tries.
        defualt (Any, optional): Default value.
    
    Example:
        Script::

            from random import randint

            @retry(tries=3, default=0)
            def f():
                rnd = randint(1, 10)
                if rnd > 5:
                    return rnd
                else:
                    raise ValueError("Random number is less than 5")
            
            print(f())

        Output::

            Retrying (1): Random number is less than 5
            Retrying (2): Random number is less than 5
            8
    
    """
    def inner(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            for _ in range(tries - wrapper.n):
                try:
                    return function(*args, **kwargs)
                except Exception as e:
                    wrapper.n += 1
                    print(f"Retrying ({wrapper.n}): {e}")
                    pass
            if default is not None:
                return default
            else:
                return function(*args, **kwargs)
        wrapper.n = 0
        return wrapper
    if _function is None:
        return inner
    else:
        return inner(_function)