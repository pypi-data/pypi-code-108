# -*- coding: utf-8 -*-
"""
description: this module provides class BaseTestCase.
"""
import collections
import inspect
import itertools
import os
import queue
import shutil
import threading
from pathlib import Path
from typing import Callable, Dict, Type, Union, TypeVar, Optional, TYPE_CHECKING, List, Sequence, Iterator

from attr import attrs, attrib, Factory, s

from _pistar.pistar_pytest.utils import sha256, uuid4, now
from _pistar.utilities.assertion import AssertThat
from _pistar.utilities.condition.condition import ConditionManager, ConditionLookUpError
from _pistar.utilities.constants import TESTCASE_EXECUTION_STATUS as STATUS, ControlArgs
from _pistar.utilities.exceptions import (
    PassedException,
    FailedException,
    InvestigatedException,
    UnavailableException,
    BlockedException,
    UnexecutedException,
    TestCaseStatusException,
)
from _pistar.utilities.logger import Logger
from _pistar.utilities.logger.logger import ExecuteLogger
from _pistar.utilities.messages import call_begin, call_successfully, call_failed
from _pistar.utilities.exceptions.testcase import ControlUsageException, ControlArgumentTypeException, \
    UnsupportedParameterTypeException
from .assert_that import assert_that as _assert_that
from .exception import ExceptionInfo, ExcInfoFormatter
from .steps import is_teststep, has_teststep


if TYPE_CHECKING:
    from _pistar.main import Session

BASE_TEST_CASE = "BaseTestCase"


class MetaTestCase(type):
    """
    description: this class is the meta class of BastTestCase.
    """

    def __init__(cls, *args, **kwargs):
        """
        description: this function is used to execute testcase automatically
        """
        super().__init__(*args, **kwargs)

        return

    def __new__(mcs, name, bases, class_dict):
        bases = (object,) if name == BASE_TEST_CASE else bases

        new_class = type.__new__(mcs, name, bases, class_dict)

        return new_class

    def __call__(cls, *args, **kwargs):
        """
        description: this function is used for testcase introspection.
        """
        testcase = type.__call__(cls, *args, **kwargs)

        if not testcase.failure:
            def failure():
                return testcase.teardown()

            testcase.failure = failure

        return testcase


class TeststepQueue(set):
    """
    this class is used to save the teststeps and pop avaliable teststeps.
    """

    def pop_teststeps(self):
        """
        description: this member functions is uses to
                     pop the avaliable teststeps.
        """
        teststeps = {teststep for teststep in self if teststep.start()}
        self.difference_update(teststeps)
        return teststeps


class BaseTestCase(metaclass=MetaTestCase):
    """
    this class is the base class of testcase.
    """

    __execution_status = None
    __start_time = None
    __end_time = None
    __assertion_list = None
    __action_word_information = None
    __status_dictionary = None
    __globals = None
    __log_path = None
    __report_path = None
    _no_color = None
    testcase_result_path = None
    failure = None

    user_logger = None
    debug: Callable[[str], None] = None
    info: Callable[[str], None] = None
    warning: Callable[[str], None] = None
    error: Callable[[str], None] = None
    critical: Callable[[str], None] = None

    @classmethod
    def __initialize__(cls):
        """
        description: this is the constructor of the class BaseTestCase.
        """
        # initialize the logger
        cls.__assertion_list = list()
        cls.__action_word_information = collections.defaultdict(list)

        cls.__status_dictionary = {
            STATUS.PASSED: PassedException,
            STATUS.FAILED: FailedException,
            STATUS.BLOCKED: BlockedException,
            STATUS.INVESTIGATED: InvestigatedException,
            STATUS.UNAVAILABLE: UnavailableException,
            STATUS.UNEXECUTED: UnexecutedException,
        }

        cls.user_logger = Logger(
            name=cls.__name__,
            logger_format="[%(asctime)s] [%(levelname)s] [%(pathname)s:%(lineno)d]\n%(message)s",
            output_path=cls.__log_path,
            no_color=cls._no_color
        )

        cls.debug: Callable[[str], None] = cls.user_logger.debug
        cls.info: Callable[[str], None] = cls.user_logger.info
        cls.warning: Callable[[str], None] = cls.user_logger.warning
        cls.error: Callable[[str], None] = cls.user_logger.error
        cls.critical: Callable[[str], None] = cls.user_logger.critical

    @property
    def status(self):
        """
        description: user can fetch testcase status with this attribute.
        """
        return self.__execution_status

    @status.setter
    def status(self, value):
        """
        description: if user set this attribute, raise corresponding exception.
        """
        frame = inspect.currentframe()
        line_number = frame.f_back.f_lineno
        raise self.__status_dictionary[value](line_number)

    @property
    def logger_path(self):
        """
        description: this function is used to get logger_path.
        """
        return self.__log_path

    def setup(self):
        """
        description: this is the setup of testcase.
        """
        return

    def teardown(self):
        """
        description: this is the teardown of testcase.
        """
        return

    def assert_that(self, value) -> AssertThat:
        """
        description: this member function is used to make assertion.
        arguments:
            value:
                type: any
                description: the value to be asserted
        return:
            type: assert_that
            description: if assertion is passed, return itself,
                         if it is failed, raise exception
        """
        return _assert_that(value=value, testcase=self)

    def append_action_word_execution_information(
            self,
            module_name,
            caller_name,
            action_word_name,
            time_consuming):
        """
        description: this function is used to add action word information into
                     member variable __action_word_information.
        arguments:
            module_name:
                type: str
                description: the module name of the action word
            action_word_name:
                type: str
                description: the name of the action word
            time_consuming:
                type: float
                description: the time consuming of action word execution,
                             unit is second
        """
        self.__action_word_information[".".join(
            [module_name, caller_name, action_word_name])].append(time_consuming)

    @property
    def execution_status(self):
        """
        description: return the execution status of this testcase.
        """
        return self.__execution_status

    @property
    def action_word_information(self):
        """
        description: return the action word information of this testcase.
        """
        return self.__action_word_information

    @classmethod
    def __parse_arguments__(cls, output, no_color=False):
        """
        description: this function is used to parse the command from console.
        todo:move this function out of the case class.
        """
        cls._no_color = no_color
        output_abspath = os.path.abspath(output)
        if not os.path.exists(output_abspath):
            os.makedirs(output_abspath)

        cls.testcase_result_path = os.path.join(
            output_abspath, sha256(inspect.getfile(cls)))
        if os.path.exists(cls.testcase_result_path):
            shutil.rmtree(cls.testcase_result_path)
        os.makedirs(cls.testcase_result_path)
        report_path = os.path.join(cls.testcase_result_path, uuid4() + ".html")
        logger_path = os.path.join(
            cls.testcase_result_path,
            uuid4() + "-attachment.log")
        cls.__log_path = logger_path
        cls.__report_path = report_path


def get_result_path(output_path, rel_path):
    result_path = output_path.joinpath(sha256(str(rel_path.absolute())))
    result_path.mkdir(parents=True, exist_ok=True)
    return result_path


@attrs
class TestCaseStepRecord:
    condition_result_cache = attrib(type=dict, default=Factory(dict))
    start_time = attrib(type=int, default=None)
    end_time = attrib(type=int, default=None)
    status_code = attrib(type=str, default=None)
    exception = attrib(type=dict, default=Factory(dict))


T = TypeVar("T", bound=BaseTestCase)


class TestCaseController:
    """
    description: the control decorator implementation
    """

    def __init__(self, rigorous=None):
        self.rigorous = rigorous

    def __call__(self, cls: Type[T], *args, **kwargs):
        self.__type_check(cls)
        cls._rigorous = self.rigorous
        return cls

    def __type_check(self, cls: Type[T]):
        """
        description: check the validity of the control decorator
        """
        # the control decorator should only be used for test cases
        try:
            is_case = issubclass(cls, BaseTestCase)
        except TypeError as e:
            raise ControlUsageException from e
        else:
            if is_case is not True:
                raise ControlUsageException

        # the control decorator argument 'rigorous' should be of Boolean type
        if self.rigorous is not None and not isinstance(self.rigorous, bool):
            raise ControlArgumentTypeException("rigorous", self.rigorous, bool)


def control(cls: Union[Type[T], None] = None, *, rigorous: bool = None):
    """
    description: the control decorator used to decorate test case
    """
    controller = TestCaseController(rigorous=rigorous)

    # when the control decorator has no arguments, cls is the class which be
    # wrapped, otherwise cls is None
    if cls:
        return controller(cls=cls)

    return controller


class TestCase:
    """A Class responsible for setting up and executing a pistar test case.

    param case_obj:
        The origin pistar test case derived from BaseTestCase.
    param arguments:
        The console parameter.
    """

    _start_time = None
    _end_time = None
    __execution_status = None

    execute_records = dict()

    @property
    def name(self):
        return self.clazz.__name__

    @property
    def end_time(self):
        return self._end_time

    @property
    def clazz(self) -> Type[BaseTestCase]:
        return self.__clazz

    @property
    def execution_status(self):
        return self.__execution_status

    @property
    def path(self) -> str:
        """case file absolute path."""
        return inspect.getfile(self.clazz)

    @property
    def nodeid(self) -> str:
        p = Path(self.path)
        try:
            nodeid = str(p.parent.relative_to(self.session.config.rootpath))
        except ValueError:
            nodeid = ""
        if nodeid == ".":
            nodeid = ""
        if os.sep != "/":
            nodeid = nodeid.replace(os.sep, "/")

        return nodeid

    @property
    def start_time(self):
        return self._start_time

    @property
    def condition_manager(self) -> ConditionManager:
        return self._con_manager

    def debug(self, message):
        if getattr(self, "logger", None):
            self.logger.debug(message)

    def info(self, message):
        if getattr(self, "logger", None):
            self.logger.info(message)

    def warning(self, message):
        if getattr(self, "logger", None):
            self.logger.warning(message)

    def error(self, message):
        if getattr(self, "logger", None):
            self.logger.error(message)

    def critical(self, message):
        if getattr(self, "logger", None):
            self.logger.critical(message)

    def __init__(self, case_obj, session: "Session"):
        self.execute_records = dict()
        self.exception = dict()
        self.execution_exceptions = list()
        self.__exception_instance_queue = queue.Queue()
        self._con_manager = session.condition_manager

        self.session = session
        self.instance = None
        self.setup = None
        self.teardown = None
        self.failure = None

        if session.config.debug:
            self.__logger_path = os.path.join(
                os.getcwd(), "logs", "pistar.log")
            self.logger = ExecuteLogger(
                name=case_obj.__name__,
                logger_format="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
                output_path=self.__logger_path,
            )

        self.__clazz = case_obj

    def initialize_step(self):
        self.__clazz.__parse_arguments__(self.session.config.outpath, self.session.config.no_color)
        self.__clazz.__initialize__()
        self.instance = self.__clazz()
        self.setup = self.instance.setup
        self.teardown = self.instance.teardown
        self.failure = self.instance.failure

        self.__schedule_step()

    def log_for_exceptions(self,
                           _exception: BaseException,
                           dependence: Callable,
                           pure_traceback_exception: Dict[str,
                                                          str]) -> None:
        """
        description: Used to output complete exception information and
        pure script exception information to framework log
        """
        self.clazz.error(f'{pure_traceback_exception["detail"]}')
        self.debug(call_failed(dependence.__name__, _exception))

    @staticmethod
    def format_exception_by_pure_traceback(
            dependence: Callable) -> Dict[str, str]:
        """
        description: Format the complete exception information to get the
        pure exception information on the script side
        """
        exc_info = ExceptionInfo.from_current()
        fmt = ExcInfoFormatter(exc_info=exc_info, func=dependence)

        exception_title = exc_info.exc_only()
        if isinstance(exc_info.value, ConditionLookUpError):
            exc_repr = exc_info.value.format_repr()
        else:
            exc_repr = fmt.repr_exception()
        exception_detail = str(exc_repr)
        exception = dict()
        exception["title"] = exception_title
        exception["detail"] = exception_detail
        exception["lineno"] = exc_repr.location.lineno
        return exception

    def __set_manual_status(self, exception):
        """
        description: when the result is manually specified by self.status
        in the test case script, the test case result is set according to the
        corresponding exception class

        :param exception: exception class corresponding to manual status
        :type exception: TestCaseStatusException
        """
        if isinstance(exception, PassedException):
            self.__execution_status = STATUS.PASSED
            self.instance.info(exception)
        elif isinstance(exception, FailedException):
            self.__execution_status = STATUS.FAILED
            self.instance.error(exception)
        elif isinstance(exception, InvestigatedException):
            self.__execution_status = STATUS.INVESTIGATED
            self.instance.error(exception)
        elif isinstance(exception, UnavailableException):
            self.__execution_status = STATUS.UNAVAILABLE
            self.instance.error(exception)
        elif isinstance(exception, BlockedException):
            self.__execution_status = STATUS.BLOCKED
            self.instance.error(exception)
        elif isinstance(exception, UnexecutedException):
            self.__execution_status = STATUS.UNEXECUTED
            self.instance.error(exception)

    def __schedule_step(self):
        teststep_queue = list()

        child = self.instance.__class__
        for attribute_name in child.__dict__:
            if is_teststep(child.__dict__.get(attribute_name)):
                teststep_queue.append(getattr(self.instance, attribute_name))

        self.teststep_queue = TeststepQueue(teststep_queue)

    def __run(self,
              dependence: Callable) -> Union[TestCaseStatusException,
                                             BaseException,
                                             None]:
        start_time = now()
        try:
            self.debug(call_begin(dependence.__name__))
            dependence()
            self.debug(call_successfully(dependence.__name__))
        except PassedException as _exception:
            exception_inst = _exception
            self.__set_manual_status(_exception)
            exception_stack_info = None
            status_code = STATUS.PASSED
            self.debug(call_successfully(dependence.__name__))
        except TestCaseStatusException as _exception:
            exception_inst = _exception
            self.__set_manual_status(_exception)
            exception_stack_info = TestCase.format_exception_by_pure_traceback(
                dependence)
            status_code = self.__execution_status
            self.log_for_exceptions(
                _exception, dependence, exception_stack_info)
        except BaseException as _exception:
            exception_inst = _exception
            self.__execution_status = STATUS.FAILED
            exception_stack_info = TestCase.format_exception_by_pure_traceback(
                dependence)
            status_code = self.__execution_status
            self.log_for_exceptions(
                _exception, dependence, exception_stack_info)
        else:
            exception_inst = None
            exception_stack_info = None
            status_code = STATUS.PASSED
        end_time = now()
        if exception_stack_info:
            self.execution_exceptions.append(exception_stack_info)
        self._set_execute_records(
            dependence,
            TestCaseStepRecord(
                start_time=start_time,
                end_time=end_time,
                status_code=status_code,
                exception=exception_stack_info),
        )

        return exception_inst

    def _fill_conditions(self, step: Callable):
        args = list(inspect.signature(step).parameters)
        condition_result = dict()
        condition_result_cache = dict()
        nodeid = self.nodeid

        def _ignore_paras(seq: Sequence) -> Iterator:
            # if parameters have tuple args or dict kwargs,
            # use parameters firstly, not condition.
            parameters = getattr(step, "parameters", None)

            if not parameters:
                return seq
            para = parameters[0]

            if isinstance(para, dict):
                return itertools.dropwhile(lambda it: it in para, seq)

            if isinstance(para, tuple):
                return seq[len(para):]

            raise UnsupportedParameterTypeException(parameter=para)

        for arg in _ignore_paras(args):
            if arg in self.condition_manager.name2confunc:
                result = self.condition_manager.execute(arg, nodeid)
                if result is None:
                    raise ConditionLookUpError(name=arg, step=step)
                if result[1]:
                    condition_result[arg] = None
                    raise result[1]
                else:
                    condition_result[arg] = result[0]
                    condition_result_cache[arg] = result
            else:

                raise ConditionLookUpError(name=arg, step=step)

        return condition_result, condition_result_cache

    def __get_thread(self, test_step: Callable):
        def teststep_thread():
            start_time = now()
            self.debug(call_begin(test_step.__name__))
            condition_result_cache = {}
            try:
                condition_result, condition_result_cache = self._fill_conditions(test_step)
                test_step(**condition_result)
            except PassedException as _exception:
                exception_inst = _exception
                self.__set_manual_status(_exception)
                exception_stack_info = None
                status_code = STATUS.PASSED
                self.debug(call_successfully(test_step.__name__))
            except TestCaseStatusException as _exception:
                exception_inst = _exception
                self.__set_manual_status(_exception)
                exception_stack_info = TestCase.format_exception_by_pure_traceback(
                    inspect.unwrap(test_step))
                status_code = self.__execution_status
                self.log_for_exceptions(
                    _exception, test_step, exception_stack_info)
            except BaseException as _exception:
                exception_inst = _exception
                self.__execution_status = STATUS.FAILED
                exception_stack_info = TestCase.format_exception_by_pure_traceback(
                    inspect.unwrap(test_step))
                status_code = self.__execution_status
                self.log_for_exceptions(
                    _exception, test_step, exception_stack_info)
                self._set_test_step_status(test_step)
            else:
                status_code = STATUS.PASSED
                exception_inst = None
                exception_stack_info = None
                self.debug(call_successfully(test_step.__name__))
            if exception_stack_info:
                self.execution_exceptions.append(exception_stack_info)
            end_time = now()

            self._set_execute_records(
                test_step,
                TestCaseStepRecord(
                    condition_result_cache=condition_result_cache,
                    start_time=start_time,
                    end_time=end_time,
                    status_code=status_code,
                    exception=exception_stack_info,
                ),
            )
            self.__exception_instance_queue.put(exception_inst)

        return teststep_thread

    def _set_test_step_status(self, test_step):
        #  when test case configured by '@control(rigorous=False)',let test step be marked as 'end'
        #  even if it has exceptions
        if getattr(self.instance, ControlArgs.RIGOROUS, None) is False:
            test_step.end.value = True

    def _set_execute_records(
            self,
            step: Callable,
            tc_step_record: TestCaseStepRecord):
        """
        description: Set the execution result for each step
        :param step: setup,teardown,failure or test step
        :type step: Callable
        :param tc_step_record: record for one step
        :type tc_step_record: TestCaseStepRecord
        :return: None
        """
        self.execute_records[step.__name__] = {
            "before": tc_step_record.condition_result_cache,
            "start_time": tc_step_record.start_time,
            "end_time": tc_step_record.end_time,
            "status_code": tc_step_record.status_code,
            "exception": tc_step_record.exception,
        }

    def execute(self):
        self._start_time = now()
        self.__execution_status = STATUS.BLOCKED

        exception_inst = self.__run(self.setup)
        if isinstance(exception_inst, PassedException):
            self.__run(self.teardown)
        elif exception_inst:
            self.__run(self.failure)
        else:

            exception_inst = self._loop()

            if exception_inst and not isinstance(
                    exception_inst, PassedException):
                self.__execution_status = STATUS.FAILED
                self.__run(self.failure)
            else:
                self.__execution_status = STATUS.PASSED
                self.__run(self.teardown)
        self._end_time = now()

    def _loop(self):
        threads = list()
        ts_last_exception = None
        for _ in range(len(self.teststep_queue)):
            teststeps = self.teststep_queue.pop_teststeps()
            for teststep in teststeps:
                thread = threading.Thread(target=self.__get_thread(teststep))
                threads.append(thread)
                thread.start()

            exception_inst = self.__exception_instance_queue.get()
            if exception_inst:
                ts_last_exception = exception_inst
            # TestCaseStatusException priority is greater than @control
            control_status = getattr(self.instance, ControlArgs.RIGOROUS, None)
            if (exception_inst and control_status is not False) or \
                    (isinstance(exception_inst, TestCaseStatusException) and control_status is False):
                break
        return ts_last_exception


def is_test_case(obj) -> bool:
    """Return True is the object is a Pistar TestCase and has test_step function."""
    return inspect.isclass(obj) and issubclass(
        obj, BaseTestCase) and has_teststep(obj)


def get_testcase_from_module(module, abs_path) -> Optional[BaseTestCase]:
    """
    description: the function is used to get the testcase class in the module
    """
    for item in dir(module):
        if item.startswith("_"):
            continue
        obj = getattr(module, item, None)
        if is_test_case(obj) and inspect.getfile(obj) == abs_path:
            return obj
    return None


def hasinit(obj: object) -> bool:
    init: object = getattr(obj, "__init__", None)
    return init != object.__init__


def hasnew(obj: object) -> bool:
    new: object = getattr(obj, "__new__", None)
    return new != object.__new__


def has_para_init(obj: object) -> bool:
    if hasinit(obj):
        new = getattr(obj, "__init__", None)
        sig = inspect.signature(new)
        return len(sig.parameters) > 1
    return False
