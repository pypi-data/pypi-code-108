import functools
import inspect
from typing import TypeVar, Callable, Optional, Union, cast, List, Dict, Iterator, Iterable

import attr

from _pistar.pistar_pytest.utils import now
from _pistar.terminal import TerminalWriter
from _pistar.utilities.testcase.exception import ExcInfoFormatter, dedent
from _pistar.utilities.testcase.repr import BaseRepr, LocationRepr

ConditionFunction = TypeVar("ConditionFunction", bound=Callable[..., object])


class ConditionLookUpError(LookupError):
    """Could not return a condition (missing or invalid)."""

    def __init__(self, name: str, step: Callable):
        super().__init__()
        self.name = name
        self.call = step

    def format_repr(self) -> "ConditionLookUpRepr":
        trace_line: List[str] = list()
        real_call = inspect.unwrap(self.call)
        fspath = inspect.getfile(real_call)
        sources, lineno = inspect.findsource(real_call)
        lines = dedent([line.rstrip() for line in sources])

        for line in lines[lineno:]:
            trace_line.append(f"{line.rstrip()}")
            if line.lstrip().startswith("def"):
                break

        msg = f"condition '{self.name}' not found."

        location = LocationRepr(path=fspath, lineno=lineno + 1, exception="")
        return ConditionLookUpRepr(location, msg=msg, lines=trace_line)


@attr.s(eq=False, auto_attribs=True)
class ConditionLookUpRepr(BaseRepr):
    location: "LocationRepr"
    msg: str
    lines: List[str]

    def gen_repr(self, writer: TerminalWriter):
        for line in self.lines:
            writer.line(line.rstrip())

        writer.line(f"{ExcInfoFormatter.error_marker}      {self.msg.strip()}")
        writer.line("")

        self.location.gen_repr(writer)


@attr.s(frozen=True)
class ConditionMarker:
    """
    The real implement of condition decorator.
    """

    scope = attr.ib(type=str)

    def __call__(self, function: ConditionFunction) -> ConditionFunction:

        if inspect.isclass(function):
            raise ValueError("class conditions not supported")
        if inspect.iscoroutinefunction(function):
            raise ValueError("coroutine condition not supported")

        function = can_not_call_directly(function)

        setattr(function, "_pistarconditionmarker", self)

        return function


def condition(
        condition_function: Optional[ConditionFunction] = None, *, scope="session"
) -> Union[ConditionMarker, ConditionFunction]:
    """Decorator to mark a condition factory function.

    This decorator can be used, with or without parameters, to define a
    condition function.

    Test steps can directly use condition names as parameters in which
    step the result returned from the condition function will be
    injected.

    Conditions can provide their values to test step using ``return`` or
    ``yield`` statements. When using ``yield`` the code block after the
    ``yield`` statement is executed as teardown code regardless of the test
    outcome, and must yield exactly once.

    :param condition_function:
        This is the fixed parameter for decorator to pass the decorated function.
        DO NOT USE IT!!!
    :param scope:
        The scope for which this condition is shared;Only Support session now.
    """
    condition_mark = ConditionMarker(scope)

    if condition_function:
        return condition_mark(condition_function)

    return condition_mark


def can_not_call_directly(function: ConditionFunction) -> ConditionFunction:
    """
    Wrap a given condition function.If a function decorated by
    condition were called directly,raise an error.
    """
    message = (
        f"Condition {function.__name__} called directly.\n"
        "PiStar will schedule condition function automatically "
        "when test cases request condition as parameter"
    )

    @functools.wraps(function)
    def wrap(*args, **kwargs):
        raise ValueError(message)

    wrap.__origin_func__ = function  # type: ignore[attr-defined]

    return cast(ConditionFunction, wrap)


class ConditionDef:
    """
    A container for a factory definition.
    """

    def __init__(self, conmanager: "ConditionManager", name: str, nodeid: str, func, scope):
        self._condition_manager = conmanager
        self.name = name
        self.func = func
        self.scope = scope
        self.nodeid = nodeid
        self.post_func: List[Callable[[], object]] = []
        self.cache_result = None
        self.before_start_time = None
        self.before_end_time = None
        self.after_start_time = None
        self.after_end_time = None

    def execute(self):
        if self.cache_result is not None:
            return self.cache_result
        result = [None, None]

        self.before_start_time = now()
        try:
            result[0] = self.call_condition_func()
        except BaseException as e:
            result[1] = e
        self.before_end_time = now()
        self.cache_result = result
        return result

    def finish(self):
        exception = None
        try:
            while self.post_func:
                self.after_start_time = now()
                try:
                    func = self.post_func.pop()
                    func()
                except BaseException as _exception:
                    exception = _exception
        finally:
            self.after_end_time = now()
            self.cache_result = None
            self.post_func = []
        return exception

    def call_condition_func(self):
        if inspect.isgeneratorfunction(self.func):
            generator = self.func()
            try:
                result = next(generator)
            except StopIteration as e:
                raise ValueError(f"{self.name} did not yield a value") from e
            post_yield = functools.partial(post_yield_func, self.name, generator)
            self.post_func.append(post_yield)

        else:
            result = self.func()
        return result


class ConditionManager:
    """
    pistar condition definitions and information is stored and managed
    from this class.
    """

    def __init__(self):
        self.name2confunc: Dict[str, List[ConditionDef]] = {}

    def add(self, confunc: ConditionDef):
        con_name = confunc.name
        con_list = self.name2confunc.setdefault(con_name, [])
        con_list.append(confunc)

    def execute(self, con_name, nodeid):
        if con_name in self.name2confunc:
            conditions = self.name2confunc.get(con_name)
            matched = tuple(self._matchfactories(conditions, nodeid))
            if matched:
                return matched[-1].execute()

    def finish(self):
        finish_conditions = list()
        for name, confuncs in self.name2confunc.items():
            for confunc in confuncs:
                if confunc.post_func:
                    result = confunc.finish()
                    duration = confunc.after_end_time - confunc.after_start_time
                    finish_conditions.append({name: (result, duration)})
        return finish_conditions

    def parse(
            self, obj, nodeid
    ) -> None:
        for name in dir(obj):
            con_obj = getattr(obj, name, None)
            if not hasattr(con_obj, "_pistarconditionmarker"):
                continue

            marker: ConditionMarker = getattr(con_obj, "_pistarconditionmarker", None)

            confunc = ConditionDef(
                self,
                con_obj.__name__,
                nodeid,
                con_obj.__origin_func__,
                marker.scope
            )

            self.add(confunc)

    def _matchfactories(
            self, conditions: Iterable[ConditionDef], nodeid: str
    ) -> Iterator[ConditionDef]:
        parents = set(parent_nodeids_iter(nodeid))
        for con in conditions:
            if con.nodeid in parents:
                yield con


def post_yield_func(condition_name, generator) -> None:
    try:
        next(generator)
    except StopIteration:
        pass
    else:
        raise ValueError(f"{condition_name} yield twice")


SEP = "/"


def parent_nodeids_iter(nodeid: str) -> Iterator[str]:
    """
    Return the parent node IDs of a given node ID, inclusive.

    For the node ID

        "testing/foo/test_example.py::Bar"

    the result would be

        ""
        "testing"
        "testing/foo"
        "testing/foo/test_example.py"
        "testing/foo/test_example.py::Bar"

    """
    pos = 0
    sep = SEP
    yield ""
    while True:
        at = nodeid.find(sep, pos)
        if at == -1 and sep == SEP:
            sep = "::"
        elif at == -1:
            if nodeid:
                yield nodeid
            break
        else:
            if at:
                yield nodeid[:at]
            pos = at + len(sep)
