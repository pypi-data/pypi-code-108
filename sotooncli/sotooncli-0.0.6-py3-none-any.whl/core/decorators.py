import inspect

from sotooncli.core.command import ExecutableCommand, GroupCommand, SotoonCommand
from sotooncli.core.param import SotoonArgument, SotoonOption


def group(name=None, **attrs):
    attrs.setdefault("cls", GroupCommand)
    return command(name, **attrs)


def _argument_memo(f, arg):
    if isinstance(f, SotoonCommand):
        f.args.append(arg)
    else:
        if not hasattr(f, "__sotoon_args__"):
            f.__sotoon_args__ = []

        f.__sotoon_args__.append(arg)


def _option_memo(f, opt):
    if isinstance(f, SotoonCommand):
        f.opts.append(opt)
    else:
        if not hasattr(f, "__sotoon_opts__"):
            f.__sotoon_opts__ = []

        f.__sotoon_opts__.append(opt)


def argument(*param_decls, **attrs):
    def decorator(f):
        ArgumentClass = attrs.pop("cls", SotoonArgument)
        _argument_memo(f, ArgumentClass(param_decls[0], **attrs))
        return f

    return decorator


def option(*param_decls, **attrs):
    def decorator(f):
        # Issue 926, copy attrs, so pre-defined options can re-use the same cls=
        option_attrs = attrs.copy()

        if "help" in option_attrs:
            option_attrs["help"] = inspect.cleandoc(option_attrs["help"])
        OptionClass = option_attrs.pop("cls", SotoonOption)
        _option_memo(f, OptionClass(param_decls, **option_attrs))
        return f

    return decorator


def command(name=None, cls=None, **attrs):
    if cls is None:
        cls = ExecutableCommand

    def decorator(f):
        cmd = _make_command(f, name, attrs, cls)
        cmd.__doc__ = f.__doc__
        return cmd

    return decorator


def _make_command(f, name, attrs, cls):
    if isinstance(f, SotoonCommand):
        raise TypeError("Attempted to convert a callback into a command twice.")

    try:
        args = f.__sotoon_args__
        args.reverse()
        del f.__sotoon_args__
    except AttributeError:
        args = []

    try:
        opts = f.__sotoon_opts__
        opts.reverse()
        del f.__sotoon_opts__
    except AttributeError:
        opts = []

    help = attrs.get("help")

    if help is None:
        help = inspect.getdoc(f)
    else:
        help = inspect.cleandoc(help)

    attrs["help"] = help
    attrs["capsule"] = help
    attrs["execute"] = f
    return cls(
        name=name or f.__name__.lower().replace("_", "-"),
        args=args,
        opts=opts,
        **attrs,
    )
