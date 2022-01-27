"""
This module makes some adjustments to the default behavior of the excellent
`fastcore.script` package to easily create functions that can be easily used
in regular code _and_ for command line interfaces with minimal additional code
"""

from upyog.imports import *
from fastcore.all import Param

__all__ = ["Param", "call_parse"]


class Param(Param):
    def __init__(
        self,
        help=None,
        type=None,
        opt=True,
        action=None,
        nargs=None,
        const=None,
        choices=None,
        required=None,
        default=None,
        metavar="",
    ):
        if type == fastcore.store_true or action == "store_true":
            type, action, default, metavar = None, "store_true", False, None
        if type == fastcore.store_false or action == "store_false":
            type, action, default, metavar = None, "store_false", True, None
        if (
            type
            and isinstance(type, typing.Type)
            and issubclass(type, enum.Enum)
            and not choices
        ):
            choices = list(type)
        fastcore.store_attr()


SCRIPT_INFO = SimpleNamespace(func=None)


class Formatter(argparse.RawDescriptionHelpFormatter, argparse.HelpFormatter):
    ...


def anno_parser(func, prog=None, from_name=False):
    "Look at params (annotated with `Param`) in func and return an `ArgumentParser`"
    cols = shutil.get_terminal_size((120, 30))[0]
    fmtr = partial(Formatter, max_help_position=cols // 2, width=cols)
    p = argparse.ArgumentParser(
        description=func.__doc__, prog=prog, formatter_class=fmtr
    )
    for k, v in inspect.signature(func).parameters.items():
        param = func.__annotations__.get(k, fastcore.Param())
        param.set_default(v.default)
        p.add_argument(f"{param.pre}{k}", **param.kwargs)
    p.add_argument(f"--pdb", help=argparse.SUPPRESS, action="store_true")
    # p.add_argument(f"--xtra", help=argparse.SUPPRESS, type=str)
    return p


def call_parse(func):
    "Decorator to create a simple CLI from `func` using `anno_parser`"
    mod = inspect.getmodule(inspect.currentframe().f_back)
    if not mod:
        return func

    @functools.wraps(func)
    def _f(*args, **kwargs):
        mod = inspect.getmodule(inspect.currentframe().f_back)
        if not mod:
            return func(*args, **kwargs)
        if not SCRIPT_INFO.func and mod.__name__ == "__main__":
            SCRIPT_INFO.func = func.__name__
        if len(sys.argv) > 1 and sys.argv[1] == "":
            sys.argv.pop(1)
        p = anno_parser(func)
        args = p.parse_args().__dict__
        xtra = fastcore.otherwise(args.pop("xtra", ""), fastcore.eq(1), p.prog)
        tfunc = fastcore.trace(func) if args.pop("pdb", False) else func
        tfunc(**fastcore.merge(args, fastcore.args_from_prog(func, xtra)))

    if mod.__name__ == "__main__":
        setattr(mod, func.__name__, _f)
        SCRIPT_INFO.func = func.__name__
        return _f()
    else:
        return _f
