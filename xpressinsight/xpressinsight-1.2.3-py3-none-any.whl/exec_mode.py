"""
    Xpress Insight Python package
    =============================

    This is an internal file of the 'xpressinsight' package. Do not import it directly.

    This material is the confidential, proprietary, unpublished property
    of Fair Isaac Corporation.  Receipt or possession of this material
    does not convey rights to divulge, reproduce, use, or allow others
    to use it without the specific written authorization of Fair Isaac
    Corporation and use must conform strictly to the license agreement.

    Copyright (c) 2020-2022 Fair Isaac Corporation. All rights reserved.
"""

import typing
import types
import sys

from .types import check_instance_attribute_types, validate_raw_ident, validate_annotation_str

_AppBaseType = typing.Type["AppBase"]


#
class ExecModeName(type):
    @property
    def LOAD(cls) -> str:
        return "LOAD"

    @property
    def RUN(cls) -> str:
        return "RUN"

    @property
    def NONE(cls) -> str:
        return ""


class ExecMode(object, metaclass=ExecModeName):
    """
    Insight execution mode decorator. Use this decorator to decorate methods of an Insight application class.

    Examples
    --------
    Example which creates a custom execution mode called `CUSTOM_RUN` with a description and with
    `clear_input` set to `False` (making this similar to the built-in `RUN` execution mode).

    >>> @xi.ExecMode(name="CUSTOM_RUN",
    ...              descr="Custom run execution mode.",
    ...              clear_input=False)
    ... def my_custom_run_mode(self):
    ...     pass

    See Also
    --------
    ExecModeRun
    ExecModeLoad
    """

    __name: str
    __descr: str
    __clear_input: bool
    __preferred_service: str
    __threads: int

    def __init__(self, name: str, descr: str = "", clear_input: bool = False,
                 preferred_service: str = "", threads: int = 0):
        """
        Constructor for the execution mode decorator for user-defined execution modes.

        Parameters
        ----------
        name : str
            User-defined execution mode name. Must be a valid identifier (alphanumeric characters
            only, starting with a letter).
        descr : str
            A description of the execution mode.
        clear_input : bool
            Whether this execution mode causes data to be loaded directly by the model, rather than
            from the Insight server. If `True`, then this execution behaves like the default load mode,
            else behaves like the default run mode.
        preferred_service : str
            Preferred service for this execution mode.
        threads : int
            The maximum number of threads that the model should consume when running in this mode.
            Defaults to no limit specified (value 0). For more detailed information on thread based capacity scheduling
            please see the section "Scenario execution and job scheduling" in the Insight Developer Guide.
        """

        self.__name = name
        self.__descr = descr
        self.__clear_input = clear_input
        self.__preferred_service = preferred_service
        self.__threads = threads
        self.__app_method: typing.Optional[types.FunctionType] = None

        check_instance_attribute_types(self)
        validate_raw_ident(name, 'execution mode name')
        validate_annotation_str(descr, 'execution mode description')
        validate_annotation_str(preferred_service, 'execution mode preferred service')

        if name == ExecMode.LOAD and not clear_input:
            raise ValueError('The clear_input attribute of the {} execution mode must be {} but it is {}.'
                             .format(name, True, clear_input))
        elif name == ExecMode.RUN and clear_input:
            raise ValueError('The clear_input attribute of the {} execution mode must be {} but it is {}.'
                             .format(name, False, clear_input))

        if threads < 0:
            raise ValueError('The number of execution mode threads must not be negative.')

    @property
    def name(self) -> str:
        return self.__name

    @property
    def descr(self) -> str:
        return self.__descr

    @property
    def clear_input(self):
        return self.__clear_input

    @property
    def preferred_service(self):
        return self.__preferred_service

    @property
    def threads(self):
        return self.__threads

    def call(self, app: _AppBaseType) -> int:
        if self.__app_method is None:
            raise TypeError('The ExecMode method is not initialized yet.')

        return self.__app_method(app)

    def __call__(self, app_method: types.FunctionType = None) -> typing.Callable[[_AppBaseType], int]:
        """ This is the decorator function that decorates an Insight application method. """

        if not isinstance(app_method, types.FunctionType):
            raise TypeError('The ExecMode() decorator can only be used to decorate a method.')

        def exec_mode_wrapper(app: _AppBaseType) -> int:
            if not hasattr(app, 'insight'):
                raise AttributeError('The class {0} does not have the "insight" attribute. Please make sure that '
                                     'it is a subclass of xpressinsight.AppBase and that the __init__ function of '
                                     '{0} calls the __init__ function of its super class.'
                                     .format(type(app).__name__))

            if app.insight.exec_mode != '':
                raise RuntimeError(
                    'Cannot call the "{}" execution mode, because the "{}" execution mode is already running.'
                    .format(self.__name, app.insight.exec_mode) + (
                        ' In test mode, "insight.exec_mode" should be the empty string before calling an execution '
                        'mode. The execution mode automatically initializes the value of "insight.exec_mode".'
                        if app.insight.test_mode else ''))

            if self.__clear_input:
                result = app.data_connector.clear_input()
            else:
                result = app.data_connector.load_input()

            if result != 0 and result is not None:
                print('ERROR: {} failed to {} the input. Exit code: {}.'
                      .format(type(app.data_connector).__name__, 'clear' if self.__clear_input else 'load', result),
                      file=sys.stderr)
                return result

            app.insight._exec_mode = self.__name
            result = app_method(app)
            app.insight._exec_mode = ''

            if result != 0 and result is not None:
                print('ERROR: The {} method returned a non-zero exit code: {}.'.format(self.name, result),
                      file=sys.stderr)
                return result

            if self.__clear_input:
                result = app.data_connector.save_input()
            else:
                result = app.data_connector.save_result()

            if result != 0 and result is not None:
                print('ERROR: {} failed to save the {}. Exit code: {}.'
                      .format(type(app.data_connector).__name__, 'input' if self.__clear_input else 'result', result),
                      file=sys.stderr)

            return 0 if result is None else result

        self.__app_method = exec_mode_wrapper
        exec_mode_wrapper.exec_mode = self
        return exec_mode_wrapper


class ExecModeLoad(ExecMode):
    """
    Decorator class for the built-in `LOAD` execution mode. Use this decorator to decorate exactly one class method
    of an Insight application.

    The `ExecModeLoad` is a shortcut for `ExecMode` where `name` is set to `LOAD` and `clear_input`
    is set to `True`.

    Examples
    --------
    Example of defining a load mode.

    >>> @xi.ExecModeLoad(descr="Loads input data.")
    ... def load(self):
    ...     pass

    See Also
    --------
    ExecMode
    ExecModeRun
    """

    def __init__(self, descr: str = "The built-in execution mode LOAD.", preferred_service: str = "", threads: int = 0):
        """
        Constructor for the `LOAD` execution mode decorator.

        Parameters
        ----------
        descr : str
            A description of the execution mode.
        preferred_service : str
            Preferred service for this execution mode.
        threads : int
            The maximum number of threads that the model should consume when running in this mode.
            Defaults to no limit specified (value 0). For more detailed information on thread based capacity scheduling
            please see the section "Scenario execution and job scheduling" in the Insight Developer Guide.
        """

        super().__init__(name="LOAD", descr=descr, clear_input=True, preferred_service=preferred_service,
                         threads=threads)


class ExecModeRun(ExecMode):
    """
    Decorator class for the built-in `RUN` execution mode. Use this decorator to decorate exactly one class method
    of an Insight application.

    The `ExecModeRun` is a shortcut for `ExecMode` where `name` is set to `RUN` and `clear_input`
    is set to `False`.

    Examples
    --------
    Example of defining a run mode.

    >>> @xi.ExecModeRun(descr="Computes the results.")
    ... def run(self):
    ...     pass

    See Also
    --------
    ExecMode
    ExecModeLoad
    """

    def __init__(self, descr: str = "The built-in execution mode RUN.", preferred_service: str = "", threads: int = 0):
        """
        Constructor for the `RUN` execution mode decorator.

        Parameters
        ----------
        descr : str
            A description of the execution mode.
        preferred_service : str
            Preferred service for this execution mode.
        threads : int
            The maximum number of threads that the model should consume when running in this mode.
            Defaults to no limit specified (value 0). For more detailed information on thread based capacity scheduling
            please see the section "Scenario execution and job scheduling" in the Insight Developer Guide.
        """

        super().__init__(name="RUN", descr=descr, clear_input=False, preferred_service=preferred_service,
                         threads=threads)
