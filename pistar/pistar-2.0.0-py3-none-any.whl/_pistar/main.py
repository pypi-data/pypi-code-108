import os
import subprocess
import sys
from pathlib import Path
from typing import Optional, Union, List, Set, Sequence, Iterator, Dict

import yaml

from _pistar.agent import generate_finish_file, generate_start_file
from _pistar.caller import ExecuteInfo, CollectReport
from _pistar.collector import Collector, Module
from _pistar.config import Config
from _pistar.config.cmdline import hookimpl
from _pistar.filesystem import visit, resolve_package_path, import_from_path, ensure_remove_module
from _pistar.pistar_pytest.utils import now
from _pistar.terminal import console_output
from _pistar.terminal import console_summary_collection
from _pistar.terminal import console_testcase_end
from _pistar.terminal import console_testcase_start
from _pistar.utilities.condition.condition import ConditionManager, ConditionDef
from _pistar.utilities.constants import PISTAR_TESTCASE_EXECUTION_STATUS as PISTAR_STATUS
from _pistar.utilities.exceptions import UsageError
from _pistar.utilities.report import get_report_info, generate_report_and_finish_file
from _pistar.utilities.testcase.case import TestCase
from _pistar.utilities.testcase.case import get_result_path


class TESTCASE_TYPE:
    PISTAR = "pistar"
    PYTEST = "pytest"


COND = "condition.py"
INIT = "__init__.py"


class Session(Collector):
    _condition_manager: ConditionManager

    def __init__(self, config: Config) -> None:
        super().__init__(config=config, fspath=None)
        self.testsfailed = 0
        self.testscollected = 0

        self._initialpaths: List[Path] = []
        self._dup_paths: Set[Path] = set()
        self.cases: List[TestCase] = []
        # global condition manager
        self._condition_manager = ConditionManager()
        self._seen_conditions: Set[Path] = set()
        self.all_case_results: Dict = {}

    @classmethod
    def from_config(cls, config: Config) -> "Session":
        session: Session = cls(config=config)
        return session

    @property
    def rootpath(self) -> Path:
        """The path from which pytest was invoked."""
        return self.config.rootpath

    @property
    def outpath(self) -> Path:
        """The path to store cases output."""
        return self.config.outpath

    @property
    def condition_manager(self) -> ConditionManager:
        return self._condition_manager

    def do_collect(self, args: Optional[Sequence[str]] = None) -> Sequence[TestCase]:
        """
        Perform the collection phase for this session.

        This function is called by the default function `pistar_collection` hook
        implementation;see the documentation of this hook for more details.

        This function recursively expands any collectors collected from the
        session to their cases, and return all test cases collected.

        Exceptions raised during the collection are wrapped as class:CollectReport
        with a user-friendly string representation for exception message.
        """

        if args is None:
            args = self.config.args

        self.condition_manager.add(
            ConditionDef(self.condition_manager,
                         pi_environment.__name__,
                         "",
                         pi_environment,
                         "session")
        )

        try:
            all_paths: List[Path] = []
            for arg in args:
                fspath = check_and_absolute(self.rootpath, arg)
                all_paths.append(fspath)
            self._initialpaths = all_paths

            res = collect_proc(self)
            if res.passed:
                for col in res.result:
                    self.cases.extend(self.make_cases(col))
            else:
                console_output(res.errors)
        finally:
            self.config.hook.pistar_collect_finish(session=self)
        self.testscollected = len(self.cases)

        return self.cases

    def collect(self):
        for argpath in self._initialpaths:
            if argpath.is_dir():
                for directory in visit(str(argpath)):
                    if not directory.is_file():
                        # visit has consider the sub-directory.
                        continue

                    path = Path(directory.path)

                    self._get_condition_module(path)
                    for x in self._collect_file(path):
                        yield x

            else:
                self._get_condition_module(argpath)
                for x in self._collect_file(argpath, False):
                    yield x

    def _collect_file(
            self,
            path: Path,
            handle_dup: bool = True) -> Sequence["Module"]:
        """
        Collect and return a Module Collector for given path.
        Only handle duplicate cases when the function called from a
        directory arguments.

        :param path:
            The given module path.
        :param handle_dup:
            If it is True,return None when the path is duplicated.
        """
        if handle_dup:
            if path in self._dup_paths:
                return ()
            else:
                self._dup_paths.add(path)

        if path.suffix == ".py" and path.name not in (COND, INIT):
            mod = Module(parent=self, fspath=path)
            return [mod]
        return ()

    def _get_condition_module(self, path: Path):
        """
        Get and import condition.py for given path.If path is a file,
        use its parent path.

        All condition in parent paths will be loaded recursively if exists,
        with a reversed order.for example:

          "/foo/bar/test.py"

        the condition.py would be imported orderly if exists"

          "/condition.py"
          "/foo/condition.py"
          "/foo/bar/condition.py"

        Notice that the last condition.py is the nearest for the given path.
        """

        if path.is_file():
            directory = path.parent
        else:
            directory = path

        for parent in reversed((directory, *directory.parents)):
            condition_path = parent.joinpath(COND)
            if condition_path.is_file():
                self._import_condition(condition_path)

    def _import_condition(self, condition_path: Path):
        key = condition_path.resolve()
        if key in self._seen_conditions:
            return
        self._seen_conditions.add(key)

        pkg_path = resolve_package_path(condition_path)

        # ensure last condition module removed from sys.module
        if pkg_path is None:
            ensure_remove_module(condition_path.stem)

        dir_path = condition_path.parent.absolute()
        sys.path.insert(0, str(dir_path))

        module = import_from_path(condition_path)

        try:
            nodeid = str(condition_path.parent.relative_to(self.config.rootpath))
        except ValueError:
            nodeid = ""
        if nodeid == ".":
            nodeid = ""
        if os.sep != "/":
            nodeid = nodeid.replace(os.sep, "/")

        self._condition_manager.parse(module, nodeid=nodeid)

    def make_cases(self, node: Union[TestCase, Collector]) -> Iterator[TestCase]:

        if isinstance(node, TestCase):
            self.config.hook.pistar_modify_case(case=node)
            yield node
        else:
            report = collect_proc(node)
            if report.passed:
                for x in report.result:
                    yield from self.make_cases(x)

            if report.failed:
                self.testsfailed += 1
                result_path = get_result_path(self.config.outpath, node.fspath)
                current_time = now()
                msg = f"import error:\n{report.errors}\n"
                console_output(msg)
                generate_finish_file(result_path, current_time, current_time, PISTAR_STATUS.ERROR, msg)


def collect_proc(collector: Collector) -> CollectReport:
    """
    Perform Collector.collect() for any Collector.Warp all runtime
    information as CollectReport.See the documentation of CollectReport
    for more details.
    """

    info = ExecuteInfo.from_call(lambda: list(collector.collect()))
    error_info: Optional[str] = None
    if not info.exc_info:
        status = "passed"
    else:
        status = "failed"
        error_info = str(collector.error_repr(info.exc_info))

    res = info.result if not info.exc_info else None

    return CollectReport(status, error_info, res)


@hookimpl
def pistar_session_start(session: Session):
    output = session.outpath
    if not output.exists():
        os.makedirs(str(output))


@hookimpl
def pistar_main(config: Config):
    """
    description: the function is the entry of running testcases
    """
    if config.arguments.type == TESTCASE_TYPE.PYTEST:
        execute_pytest_testcases(config.arguments)
        return

    start_time = now()
    session = Session.from_config(config)
    hook = config.hook
    hook.pistar_session_start(session=session)
    hook.pistar_collection(session=session)
    hook.pistar_run_loop(session=session)
    console_summary_collection(session.all_case_results, now() - start_time, config.no_color)


@hookimpl
def pistar_collection(session: Session) -> None:
    session.do_collect()


@hookimpl
def pistar_run_loop(session: Session):
    if session.config.collectonly:
        return
    hook = session.config.hook
    for i, case in enumerate(session.cases):
        next_case = session.cases[i + 1] if i + 1 < len(session.cases) else None
        hook.pistar_run_procedure(case=case, next_case=next_case)
        report_info = get_report_info(case)
        session.all_case_results.update(generate_report_and_finish_file(case, report_info))


@hookimpl
def pistar_run_procedure(case: TestCase, next_case: Optional[TestCase]):
    hook = case.session.config.hook
    hook.pistar_run_log_begin(case=case)
    call_procedure(case, next_case)
    hook.pistar_run_log_end(case=case)


@hookimpl
def pistar_run_log_begin(case: TestCase):
    console_testcase_start(case.clazz)
    generate_start_file(case.path, str(case.session.config.outpath))


@hookimpl
def pistar_run_log_end(case: TestCase):
    console_testcase_end(case.clazz)


def check_and_absolute(root_path: Path, arg: str) -> Path:
    """
    Check path argument and return its absolute path.

    Command-line arguments can point to files or directories, for example:

      "pkg/tests/test_foo.py pkg/tests/test_bar.py"

    or directory:

      "pkg/tests/"

    This function ensures the path exists, and returns a Path:

        Path("/full/path/to/pkg/tests/test_foo.py")

    If the path doesn't exist, raise UsageError.

    """

    abspath = root_path.joinpath(arg)
    abspath: Path = Path(os.path.abspath(str(abspath)))

    if not abspath.exists():
        msg = f"file or directory not found: {abspath}"
        raise UsageError(msg)

    return abspath


def call_procedure(case: TestCase, next_case: Optional[TestCase]):
    try:
        case.initialize_step()
    except BaseException as exception:
        case.exception = TestCase.format_exception_by_pure_traceback(case.clazz.__init__)
        case.log_for_exceptions(exception, case.clazz.__init__, case.exception)
    else:
        case.execute()
        if next_case is None:
            execute_post_condition(case)


def execute_post_condition(case: TestCase):
    finish_condition = case.condition_manager.finish()
    last_step = list(case.execute_records.keys())[-1]
    case.execute_records.get(last_step)["after"] = finish_condition


def pi_environment():
    workspace = Path(os.getcwd())
    env_path = workspace.joinpath("environment.yaml")
    if not env_path.is_file():
        raise IOError("Cannot find the file environment.yaml")
    with open(env_path, mode="r", encoding="utf-8") as f:
        env = yaml.load(f, Loader=yaml.SafeLoader)
        return env


# execute pytest cases
TIMEOUT = 3600


def execute_pytest_testcases(arguments):
    """
    Run pytest test with pistar plugin.
    """
    sys.path.append(os.getcwd())

    pytest_file_list = list()
    for pytest_file in arguments.files_or_dir:
        pytest_file_list.append(pytest_file)

    command = [sys.executable, "-m", "pytest", "-v"]
    command += ["--pistar_dir=" + arguments.output]
    command += pytest_file_list

    process = subprocess.Popen(command)

    process.communicate(timeout=TIMEOUT)
