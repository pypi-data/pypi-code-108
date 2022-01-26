"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import inspect
from enum import Enum, auto
from pathlib import Path
from warnings import warn
from functools import wraps

# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.general_helper.enums import MiscEnum

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class DeprecationWarningTypus(Enum):
    ARGUMENT = auto()


def _replace_default_argument_w_NOTHING(func, arg_name: str, *args, **kwargs) -> inspect.BoundArguments:
    func_sig = inspect.signature(func)
    new_arg = func_sig.parameters[arg_name].replace(default=MiscEnum.NOTHING)
    new_params = [param_value if param_name != arg_name else new_arg for param_name, param_value in func_sig.parameters.items()]
    new_sig = func_sig.replace(parameters=new_params)
    bound_args = new_sig.bind(*args, **kwargs)
    bound_args.apply_defaults()
    return bound_args


def _make_deprication_warning(typus: DeprecationWarning, **kwargs) -> None:
    if typus is DeprecationWarningTypus.ARGUMENT:

        needed = {"arg_name", "func_name", "func"}
        if any(kwarg_name not in kwargs for kwarg_name in needed):
            missing = [pos_missing for pos_missing in needed if kwargs.get(pos_missing, None) is None]
            raise AttributeError(f"missing needed kwargs {', '.join(repr(i) for i in missing)}.")

        message_parts = [f"The argument {kwargs.get('arg_name')!r} for '{kwargs.get('func_name')}()' is deprecated"]
        if kwargs.get('not_used', False):
            message_parts.append("it is not used anymore in the actual function (does not do anything)")
        if kwargs.get('alternative_arg_name', None):
            message_parts.append(f"use the alternative {kwargs.get('alternative_arg_name')!r}")
        message = ', '.join(message_parts) + '.'

    warn(message=message, category=DeprecationWarning, stacklevel=3)


def deprecated_argument(arg_name: str, alternative_arg_name: str = None):

    def _wrapper(func):
        func_name = func.__qualname__ or func.__name__

        @wraps(func)
        def _wrapped(*args, **kwargs):
            new_bound_args = _replace_default_argument_w_NOTHING(func, arg_name, *args, **kwargs)
            args = new_bound_args.args
            kwargs = new_bound_args.kwargs
            if new_bound_args.arguments[arg_name] is not MiscEnum.NOTHING:
                _make_deprication_warning(DeprecationWarningTypus.ARGUMENT, func=func, arg_name=arg_name, func_name=func_name, not_used=True, alternative_arg_name=alternative_arg_name)
            return func(*args, **kwargs)

        return _wrapped

    return _wrapper


# region[Main_Exec]
if __name__ == '__main__':
    pass

# endregion[Main_Exec]
