"""
Serialize parameters defined by a :class:`argparse.ArgumentParser`.
"""

from argparse import ArgumentParser, Action
from chris_plugin.constants import Placeholders
from chris_plugin.types import ParameterType, ParameterSpec, Special
from chris_plugin._atypes import StoreAction, StoreTrueAction, StoreFalseAction
from typing import Optional, Any, Sequence


# noinspection PyProtectedMember
def serialize(_p: ArgumentParser) -> list[ParameterSpec]:
    """
    Serialize the parser to a list of objects
    conformant to the ChRIS plugin parameter spec.
    """
    return [serialize_action(a) for a in _p._actions if should_include(a)]


def should_include(a: Action):
    """
    Check if the given action represents the help command
    or a positional argument (inputdir, outputdir).
    """
    if a.dest == 'help':
        return False
    if len(a.option_strings) == 0:
        return False
    return True


def serialize_action(_a: Action) -> ParameterSpec:
    """
    Dispatch a serializer based on type.
    """
    if isinstance(_a, StoreAction):
        return serialize_store_action(_a)
    if isinstance(_a, StoreTrueAction) or isinstance(_a, StoreFalseAction):
        return serialize_bool_action(_a)
    raise TypeError(f'Action cannot be used with a ChRIS plugin: {_a}')


def serialize_store_action(a: StoreAction) -> ParameterSpec:
    """
    Serialize a typical action which represents a key-value option like ``--key value``
    """
    check_default_type(a)
    p_type = get_param_type(a)
    return serialize_compatible_action(
        a, type=p_type, action='store', help=expand_help(a),
        default=pick_default(p_type, a.required, a.default)
    )


def serialize_bool_action(a: StoreTrueAction | StoreFalseAction) -> ParameterSpec:
    """
    Serialize a "store_true" or "store_false" action.
    """
    return serialize_compatible_action(
        a, type='bool',
        action='store_' + str(a.const).lower(),
        help=a.help,
        default=(not a.const)
    )


# noinspection PyShadowingBuiltins
def serialize_compatible_action(
        a: Action,
        type: ParameterType,
        action: str,
        help: str,
        default: Optional[Any]
) -> ParameterSpec:
    """
    Common functionality across serializable ``Action``.
    """
    short_flag, long_flag = flags(a.option_strings)
    return ParameterSpec(
        name=a.dest,
        type=type,
        optional=(not a.required),
        flag=long_flag,
        short_flag=short_flag,
        action=action,
        help=help,
        default=default,
        ui_exposed=True
    )


def expand_help(a: Action) -> str:
    """
    Append the choices to the help string, if defined.
    """
    h = a.help if a.help else ''
    if a.choices:
        h += f' [choices: {", ".join(a.choices)}]'
    return h


def flags(option_strings: Sequence[str]) -> tuple[str, str]:
    """
    :return: the shortest and longest members of the given Sequence
    """
    sorted_options = list(option_strings)
    sorted_options.sort(key=len)
    return sorted_options[0], option_strings[-1]


def pick_default(t: ParameterType, required: bool, default: Optional[Any]) -> Any:
    if default is not None:
        return default
    if required:
        return None
    return Placeholders.get_for(t)


def get_param_type(a: StoreAction) -> ParameterType:
    if a.type is Special.path:
        return 'path'
    if a.type is Special.unextpath:
        return 'unextpath'
    if a.type is None:
        if a.default is not None:
            t = type(a.default)
        else:
            t = str
    else:
        t = a.type
    # noinspection PyTypeChecker
    return t.__name__


def check_default_type(a: StoreAction):
    """
    Cause an error if the default value is not of the specified type.
    """
    if not a.default:
        return
    if not a.type:
        return
    if not isinstance(a.default, a.type):
        raise TypeError(f'default={a.default} violates type={a.type}: {str(a)}')
