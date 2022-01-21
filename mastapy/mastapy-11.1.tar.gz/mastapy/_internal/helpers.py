'''helpers.py

This is the main utility module for the Masta Python API. This module is
required to be imported by users to interact with Masta.

Examples:
    The following code demonstrates how to initialise Masta for use with
    external Python scripts:

        >>> import mastapy as mp
        >>> mp.init('my_path_to_dll_folder')

    The following code demonstrates how to define a Masta property:

        >>> import mastapy as mp
        >>> from mastapy.system_model import Design
        >>> @masta_property(name='my_masta_property')
            def my_function(design: Design) -> int:
                return 0

    The following demonstrates how to start debugging a script launched
    from Masta:

        >>> import mastapy as mp
        >>> mp.start_debugging()

Attributes:
    _MASTA_PROPERTIES (dict): Internal use only. Contains property information
'''


import inspect
import itertools
import functools
import sys
import os
import importlib
import warnings
import types

import clr
import ptvsd

from typing import Optional, Union, Tuple

from mastapy._internal.measurement_type import (
    MeasurementType, convert_measurement_to_str)
from mastapy._internal.mastapy_version_exception import MastapyVersionException
from mastapy._internal.python_net import (
    python_net_import, initialise_python_net_importing)
from mastapy._internal.version import __api_version__


__all__ = (
    'masta_property', 'masta_before', 'masta_after', 'init',
    'start_debugging', 'load_mastafile')


_MASTA_PROPERTIES = dict()
_MASTA_SETTERS = dict()
_HOOK_NAME_TO_METHOD_DICT = dict()
_HAS_ATTEMPTED_MASTAFILE_LOAD = False

_is_initialised = False

warnings.formatwarning = (
    lambda m, c, f, n, line=None:
    '{}:{}:\n{}: {}\n'.format(f, n, c.__name__, m))


class MastaInitException(Exception):
    '''MastaInitException

    Exception raised when there is an issue with initialising mastapy.
    '''


class MastaPropertyException(Exception):
    '''MastaPropertyException

    Exception raised when there is an issue with a defined Masta property.
    '''


class MastaPropertyTypeException(Exception):
    '''MastaPropertyTypeException

    Exception raised when there is an issue with the type of a defined Masta
    property.
    '''


class MastaPropertyMultiMethod(dict):
    '''MastaPropertyMultiMethod

    Class that enables multiple-dispatch of Masta properties. This allows a
    user to call both the getter and setter methods from within their code.
    '''

    def __new__(cls, func, types):
        namespace = inspect.currentframe().f_back.f_locals
        self = functools.update_wrapper(dict.__new__(cls), func)
        return namespace.get(func.__name__, self)

    def __init__(self, func, types):
        self[types] = func

    def __missing__(self, types):
        raise MastaPropertyException(
            'Failed to find method with parameters of type: {}'.format(types))

    def __call__(self, *args, **kwargs):
        subs = map(lambda x: x.__class__.__mro__, args)
        arg_combos = itertools.product(*subs)

        for combo in arg_combos:
            try:
                func = self[tuple(map(type, args))]
                value = func(*args, **kwargs)

                expected_return = func.__annotations__['return']
                if not isinstance(value, expected_return):
                    raise MastaPropertyTypeException(
                        ('Return value is of an unexpected type. Make sure the'
                         ' type matches the property\'s annotated return type.'
                         '\n\nExpected: {}\nGot: {}').format(
                             expected_return, value))

                return value
            except MastaPropertyException:
                pass

        self.__missing__(args)

    def setter(self, func):
        '''Setter for the MASTA property.

        Args:
            func: Wrapped function.
        '''

        func_spec = inspect.getfullargspec(func)
        annotations = func_spec.annotations
        arg_names = func_spec.args
        num_arguments = len(arg_names)
        num_typed_parameters = len(list(
            filter(lambda x: x != 'return', annotations)))

        if func.__name__ not in _MASTA_PROPERTIES:
            raise MastaPropertyException((
                'MASTA property setters must share the same name as their '
                'accompanying getter. No getter found called \'{}\'.').format(
                    func.__name__))

        if num_arguments != 2:
            end = 'was' if num_arguments == 1 else 'were'
            raise MastaPropertyException((
                'MASTA property setters require 2 '
                'arguments, but {} {} found.').format(num_arguments, end))

        if num_typed_parameters != 2:
            raise MastaPropertyException(
                'Both MASTA property setter parameters must be typed.')

        setter_type = annotations[arg_names[0]]
        getter_type = _MASTA_PROPERTIES[func.__name__][1]
        if setter_type != getter_type:
            raise MastaPropertyException((
                'MASTA property setters and getters must have their first '
                'parameters defined with the same type.\n'
                'Got: {}\nExpected: {}').format(
                    setter_type.__qualname__, getter_type.__qualname__))

        setter_value_type = annotations[arg_names[1]]
        getter_value_type = _MASTA_PROPERTIES[func.__name__][6]

        if not getter_value_type:
            raise MastaPropertyException((
                'MASTA property getter does not have a specified '
                'return type. Setter not expected.'))

        if setter_value_type != getter_value_type:
            raise MastaPropertyException((
                'MASTA property setters and getters must match their setting '
                'and returning types.\nGot: {}\nExpected: {}').format(
                    setter_value_type.__qualname__,
                    getter_value_type.__qualname__
                ))

        _MASTA_SETTERS[func.__name__] = func

        args = tuple(map(annotations.get, arg_names))
        self.__init__(func, args)

        return self if self.__name__ == func.__name__ else func


def masta_property(
        name: str,
        *,
        description: Optional[str] = '',
        symbol: Optional[str] = '',
        measurement: Optional[Union[str, MeasurementType]] = ''):
    '''Decorator method for creating MASTA properties in Python

    Args:
        name (str): The name of the property displayed in Masta
        description (str, optional): The description of what the property does.
        symbol (str, optional): The symbol for the property displayed in Masta.
        measurement (str|MeasurementType, optional): Unit the property
            displayed in, in Masta.
    '''

    def _masta_property_decorator(func):
        func_spec = inspect.getfullargspec(func)
        args = func_spec.args
        annotations = func_spec.annotations
        num_typed_parameters = len(list(
            filter(lambda x: x != 'return', annotations)))

        if len(args) < 1 or num_typed_parameters < 1:
            raise MastaPropertyException((
                'MASTA property found without a typed parameter. '
                'MASTA properties must include one typed parameter.'))

        if len(args) > 1:
            raise MastaPropertyException((
                'Too many parameters found in MASTA property description. '
                'Only one is supported.'))

        parameter = annotations.get(args[0], None)
        returns = annotations.get('return', None)

        if parameter:
            is_old_type = not parameter.__module__.startswith('mastapy')
            m = (convert_measurement_to_str(measurement)
                 if isinstance(measurement, MeasurementType)
                 else measurement)

            frame = inspect.stack()[1]

            _MASTA_PROPERTIES[func.__name__] = (
                func, parameter, name, description, symbol,
                m, returns, is_old_type, frame.filename)

        return MastaPropertyMultiMethod(func, (parameter,))

    return _masta_property_decorator


def load_mastafile():
    '''Executes a mastafile.py file from the local directory if found.'''

    global _HAS_ATTEMPTED_MASTAFILE_LOAD, _HOOK_NAME_TO_METHOD_DICT

    if 'mastafile' not in sys.modules and not _HAS_ATTEMPTED_MASTAFILE_LOAD:
        _HAS_ATTEMPTED_MASTAFILE_LOAD = True

        try:
            path_to_mastafile = os.path.realpath('mastafile.py')

            if not os.path.exists(path_to_mastafile):
                path_to_mastafile = next(
                    filter(
                        lambda x: os.path.exists(x),
                        map(
                            lambda x: os.path.join(x, 'mastafile.py'),
                            sys.path)),
                    None)

            os.chdir(os.path.dirname(path_to_mastafile))
            mastafile_loader = importlib.machinery.SourceFileLoader(
                'mastafile_module', path_to_mastafile)
            mastafile_module = types.ModuleType(mastafile_loader.name)
            mastafile_loader.exec_module(mastafile_module)
            _HOOK_NAME_TO_METHOD_DICT = dict(inspect.getmembers(
                mastafile_module, predicate=inspect.isfunction))
        except (IOError, OSError, TypeError):
            # No mastafile.py file has been found.
            # This is an optional feature, so ignore the error!
            pass


def masta_before(name: str):
    '''Decorator method for adding hooks to properties that are called before
    the property is called. Hooking methods must be defined in a mastafile.py
    file.

    Args:
        name (str): The name of the hooking method in mastafile.py
    '''

    def _masta_before_decorator(func):

        def _decorator(*args, **kwargs):
            hook = _HOOK_NAME_TO_METHOD_DICT.get(name, None)

            if not hook:
                raise MastaPropertyException(
                    'Failed to find hooking method \'{}\'.'.format(name))

            hook(*args, **kwargs)
            return func(*args, **kwargs)
        return _decorator

    return _masta_before_decorator


def masta_after(name: str):
    '''Decorator method for adding hooks to properties that are called after
    the property is called. Hooking methods must be defined in a mastafile.py
    file.

    Args:
        name (str): The name of the hooking method in mastafile.py
    '''

    def _masta_after_decorator(func):

        def _decorator(*args, **kwargs):
            hook = _HOOK_NAME_TO_METHOD_DICT.get(name, None)

            if not hook:
                raise MastaPropertyException(
                    'Failed to find hooking  method \'{}\'.'.format(name))

            x = func(*args, **kwargs)
            hook(*args, **kwargs)
            return x
        return _decorator

    return _masta_after_decorator


def _strip_pre_release(value: str) -> str:
    letters = ['a', 'b', 'rc', 'post']
    letter = next(filter(lambda x: x in value, letters), None)

    if letter:
        i = value.index(letter)
        value = value[:i]
        return value if value else '0'
    else:
        return value


def _convert_version_to_tuple(
        version: Optional[Union[str, Tuple[int]]]) -> Tuple[int]:
    if isinstance(version, str):
        version = tuple(map(
            lambda x: int(_strip_pre_release(x)), version.split('.')))

    v_len = len(version)
    if v_len < 3:
        version += (0,) * (3 - v_len)

    return version


def _match_versions():
    versioning = python_net_import('SMT.MastaAPI', 'UtilityMethods')

    if hasattr(versioning, 'ReleaseVersionString'):
        release_version_str = versioning.ReleaseVersionString
    else:
        versioning = python_net_import('SMT.MastaAPI', 'Versioning')
        release_version_str = versioning.APIReleaseVersionString

    api_version = release_version_str.split(' ')[0]
    message = ('This version of mastapy ({0}) is not supported by the version '
               'of MASTA you are trying to initialise it with.\n\n'
               'You must use either MASTA {0} or newer.\n').format(
                   api_version)

    current_version = _convert_version_to_tuple(api_version)
    backwards_version = (10, 3, 0)
    no_backwards_compatibility = current_version < backwards_version

    if no_backwards_compatibility and api_version != __api_version__:
        raise MastapyVersionException(message) from None


def _init_runtime(path_to_dll_folder: str):
    version = ''.join(map(str, sys.version_info[:2]))
    python_runtime_dll = 'Python.Runtime{}.dll'.format(version)
    python_runtime_path = os.path.join(path_to_dll_folder, python_runtime_dll)

    if not os.path.exists(python_runtime_path):
        raise MastaInitException((
            'Failed to load Python runtime environment '
            'at path \'{}\'.').format(python_runtime_path))

    assembly = clr.AddReference(python_runtime_path)

    binding_flags = python_net_import('System.Reflection', 'BindingFlags')
    assembly_manager = assembly.GetType('Python.Runtime.AssemblyManager')

    bf = (binding_flags.Public
          | binding_flags.Static
          | binding_flags.InvokeMethod)
    method = assembly_manager.GetMethod('Initialize', bf)

    if method:
        method.Invoke(None, None)


def init(path_to_dll_folder: str):
    '''Initialises the Python to MASTA API interop

    Args:
        path_to_dll_folder (str): Path to your MASTA folder that includes the
            SMT.MastaAPI.dll file
    '''
    global _is_initialised

    if _is_initialised:
        return

    full_path = path_to_dll_folder

    if not os.path.isdir(full_path):
        raise MastaInitException((
            'Failed to initialise mastapy. Provided '
            'path \'{}\' is not a directory.').format(full_path)) from None

    api_name = 'SMT.MastaAPI.{}.dll'.format(__api_version__)
    utility_api_name = 'SMT.MastaAPIUtility.{}.dll'.format(__api_version__)
    full_path = os.path.join(path_to_dll_folder, api_name)
    utility_full_path = os.path.join(path_to_dll_folder, utility_api_name)

    is_legacy_naming = False

    if not os.path.exists(full_path):
        api_name = 'MastaAPI.dll'
        utility_api_name = 'MastaAPIUtility.dll'
        full_path = os.path.join(path_to_dll_folder, api_name)
        utility_full_path = os.path.join(path_to_dll_folder, utility_api_name)

        if not os.path.exists(full_path):
            raise MastaInitException((
                'Failed to initialise mastapy. Failed to find API DLL of '
                'expected version {}. Do you have the correct version of '
                'mastapy installed?').format(__api_version__)) from None

        is_legacy_naming = True

    initialise_python_net_importing(utility_full_path)

    _init_runtime(path_to_dll_folder)
    clr.AddReference(os.path.join(path_to_dll_folder, 'Utility.dll'))
    clr.AddReference(full_path)
    clr.AddReference(utility_full_path)

    utility_methods = python_net_import('SMT.MastaAPI', 'UtilityMethods')
    utility_methods.InitialiseApiAccess(path_to_dll_folder)

    if path_to_dll_folder not in os.environ['PATH']:
        os.environ['PATH'] += os.pathsep + path_to_dll_folder

    if is_legacy_naming:
        _match_versions()

    _is_initialised = True


def start_debugging(
    host: Optional[str] = 'localhost', port: Optional[int] = 5678,
        timeout: Optional[int] = 10):
    '''Starts Python debugging using PTVSD

    Args:
        host (str, optional): Debug server IP address. Defaults to 'localhost'
        port (int, optional): Debug server port. Defaults to 5678
        timeout (int, optional): How long the program will wait for a debugger
            to attach in seconds. Defaults to 10

    Note:
        Execution will pause until either a debugger is attached to the Python
        process, or the timout expires.
    '''

    print((
        'Waiting for debugger to attach at {}:{} (execution will time out '
        'in {} seconds)...').format(host, port, timeout))
    ptvsd.enable_attach(address=(host, port), redirect_output=True)
    ptvsd.wait_for_attach(timeout)
