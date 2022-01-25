from pathlib import Path
from typing import Iterator
from typing import Optional
from typing import TYPE_CHECKING
from typing import Union

from _pistar.config import Config
from _pistar.filesystem import ImportMismatchError
from _pistar.filesystem import import_from_path
from _pistar.utilities.testcase.case import TestCase
from _pistar.utilities.testcase.case import get_testcase_from_module
from _pistar.utilities.testcase.case import has_para_init
from _pistar.utilities.testcase.case import hasnew
from _pistar.utilities.testcase.exception import ExcInfoFormatter
from _pistar.utilities.testcase.exception import ExceptionInfo
from _pistar.utilities.testcase.exception import TraceBack
from _pistar.utilities.testcase.exception import filter_traceback
from _pistar.utilities.testcase.repr import ExceptionRepr

if TYPE_CHECKING:
    from _pistar.main import Session


class Collector:
    """
    This is the abstract class for Collector.

    Collector will collect and return its sub-collector.For example,
    Module collector collect Clazz collector.Clazz collector returns
    TestCase Finally.

    Some Error during collection are wrapped as CollectError which
    contains a custom message.
    """

    __slots__ = ("config", "fspath")

    def __init__(self, config: Config, fspath: Optional[Path]):
        if config:
            self.config: Config = config

        self.fspath = fspath

    class CollectError(Exception):
        """An error during collection, contains a custom message."""

    def collect(self):
        raise NotImplementedError()

    def error_repr(
            self,
            exc_info: ExceptionInfo[BaseException]
    ) -> Union[str, ExceptionRepr]:
        """
        Get error message during the collection phase.
        """
        # only the last traceback can be formatted.
        if isinstance(exc_info.value, self.CollectError):
            exc = exc_info.value
            return str(exc.args[0])

        tb = TraceBack([exc_info.traceback[-1]])
        exc_info.traceback = tb
        fmt = ExcInfoFormatter(exc_info=exc_info, func=None)

        error_repr = fmt.repr_exception()

        return error_repr


class Module(Collector):
    """
    Collector for Clazz collector.
    """

    def __init__(self, parent: Collector, fspath: Path):
        super().__init__(parent.config, fspath)
        self._obj = None
        self.parent: "Session" = parent

    @property
    def obj(self):
        obj = getattr(self, "_obj", None)

        if obj is None:
            obj = self._obj = self._import_case_module()

        return obj

    @property
    def outpath(self) -> Path:
        """The path to store cases output."""
        return self.config.outpath

    def collect(self) -> Iterator[Collector]:
        # collect the class finally

        if self.obj is None:
            return []

        testcase = get_testcase_from_module(self.obj, str(self.fspath.absolute()))

        if not testcase:
            return []

        return [Clazz(self, self.fspath, testcase)]

    def _import_case_module(self):
        """
        Import the module from given Path.

        We assume this function are called only once per module.
        Raised CollectorError with custom message if necessary.
        """
        try:
            module = import_from_path(self.fspath)
        except SyntaxError as e:
            raise self.CollectError(ExceptionInfo.from_current().exc_only()) from e

        except ImportMismatchError as e:

            raise self.CollectError(
                "import mismatch:\n"
                "Module %r has this __file__ attribute:\n"
                "  %s\n"
                "which is different to the file we want to collect:\n"
                "  %s\n"
                "NOTE: use a unique basename for your modules,\n"
                "or use package to organize your test structure." % e.args
            ) from e

        except ImportError as e:
            exc_info = ExceptionInfo.from_current()
            exc_info.traceback = exc_info.traceback.filter_from(filter_traceback)

            error_repr = self.error_repr(exc_info)
            msg = f"ImportError when importing module: \n'{self.fspath}'.\n" \
                  f"Hint: make sure the module have valid Python names.\n" \
                  f"Details:\n{str(error_repr)} "
            raise self.CollectError(msg) from e

        return module


class Clazz(Collector):
    """
    Clazz Collector for TestCase.

    The Collector collects the TestCase finally.
    """

    def __init__(self, parent: Collector, fspath: Path, obj=None):
        super().__init__(parent.config, fspath)
        self._obj = obj
        self.parent = parent

    @property
    def obj(self):

        return self._obj

    @property
    def outpath(self) -> Path:
        """The path to store cases output."""
        return self.config.outpath

    @property
    def name(self) -> str:
        return self._obj.__name__

    def collect(self) -> Iterator[TestCase]:
        # collect the class finally

        if self.obj is None:
            return []

        if has_para_init(self.obj) or hasnew(self.obj):
            msg = (
                f"Warning: cannot collect case {self.name}\n"
                f"from {self.fspath},\n"
                f"which has a parameterized __init__ or __new__ constructor."
            )

            raise self.CollectError(msg)

        # maybe we need to set session as a super property
        return [TestCase(self.obj, self.parent.parent)]
