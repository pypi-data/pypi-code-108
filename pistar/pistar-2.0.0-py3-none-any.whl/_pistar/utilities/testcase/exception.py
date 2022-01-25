# -*- coding: utf-8 -*-
import ast
import inspect
import sys
import textwrap
import tokenize
from bisect import bisect_right
from traceback import format_exception_only, format_exception
from types import TracebackType, CodeType
from typing import Optional, Tuple, Type, TypeVar, List, Iterable, Generic, cast, Union, Callable

import attr
import py

from _pistar.utilities.exceptions import AssertionBaseException
from _pistar.utilities.testcase.repr import ItemRepr, LocationRepr, ExceptionRepr


def get_tb_source_code(tb: TracebackType):
    try:
        sources, lineno = inspect.findsource(tb.tb_frame.f_code)
    except OSError:
        return None, -1
    lines = [line.rstrip() for line in sources]
    return lines, lineno


class TracebackItem:
    """A single entry in a Traceback."""

    __slots__ = ("_origin_tb",)

    def __init__(self, origin_tb: TracebackType) -> None:
        self._origin_tb = origin_tb

    @property
    def lineno(self) -> int:
        """Crash line of the traceback"""
        return self._origin_tb.tb_lineno

    @property
    def path(self) -> str:
        """Path to the source code."""
        return self._origin_tb.tb_frame.f_code.co_filename

    def get_first_line_source(self) -> int:
        """Get the first line of this callable object"""
        return self._origin_tb.tb_frame.f_code.co_firstlineno

    @property
    def full_source(self) -> List[str]:
        full, _ = get_tb_source_code(self._origin_tb)
        return full

    @property
    def crash_source(self) -> List[str]:
        code_first_lineno = self.get_first_line_source() - 1
        crash_line = self.lineno - 1

        return self.full_source[code_first_lineno: crash_line + 1]

    @property
    def origin_tb(self):
        return self._origin_tb


class TraceBack(List[TracebackItem]):
    def __init__(self, tb: Union[TracebackType, Iterable[TracebackItem]]):
        def trace_gen(cur: Optional[TracebackType]) -> Iterable[TracebackItem]:
            _cur = cur
            while _cur is not None:
                yield TracebackItem(_cur)
                _cur = _cur.tb_next

        if isinstance(tb, TracebackType):
            super().__init__(trace_gen(tb))
        else:
            super().__init__(tb)

    def pure(self, path, first_lineno) -> "TraceBack":

        for tb in self:
            code_path = tb.path
            code_first_lineno = tb.get_first_line_source()
            if path == code_path and first_lineno == code_first_lineno:
                return TraceBack(tb.origin_tb)
        return self

    def filter_from(self, func: Callable[[TracebackItem], bool]) -> "TraceBack":
        return TraceBack(filter(func, self))


_E = TypeVar("_E", bound=BaseException, covariant=True)


@attr.s(repr=False)
class ExceptionInfo(Generic[_E]):
    """Wraps sys.exc_info() objects and offers help for navigating the traceback."""

    _exc_info = attr.ib(type=Optional[Tuple[Type["_E"], "_E", TracebackType]])

    _traceback = attr.ib(type=TraceBack, default=None)

    @classmethod
    def from_exc_info(
            cls,
            exc_info: Tuple[Type[_E], _E, TracebackType],
    ) -> "ExceptionInfo[_E]":
        """Return an ExceptionInfo for an existing exc_info tuple."""

        return cls(exc_info)

    @classmethod
    def from_current(cls) -> "ExceptionInfo[BaseException]":
        """Return an ExceptionInfo matching the current traceback."""
        exc = sys.exc_info()
        if exc[0] is None or exc[1] is None or exc[2] is None:
            raise AssertionError("no current exception")
        exc_info = (exc[0], exc[1], exc[2])
        return ExceptionInfo.from_exc_info(exc_info)

    @property
    def type(self) -> Type[_E]:
        if self._exc_info is None:
            raise AssertionError(".type can only be used after the exception exits")
        return self._exc_info[0]

    @property
    def value(self) -> _E:
        if self._exc_info is None:
            raise AssertionError(".value can only be used after the exception exits")
        return self._exc_info[1]

    @property
    def tb(self) -> TracebackType:
        if self._exc_info is None:
            raise AssertionError(".tb can only be used after the exception exits")
        return self._exc_info[2]

    @property
    def traceback(self) -> TraceBack:
        if self._traceback is None:
            self._traceback = TraceBack(self.tb)
        return self._traceback

    @traceback.setter
    def traceback(self, value):
        self._traceback = value

    @property
    def type_name(self) -> str:
        return self.type.__name__

    def exc_only(self) -> str:
        lines = format_exception_only(self.type, self.value)
        text = "".join(lines)
        text = text.rstrip()

        return text

    def exc_with_tb(self) -> str:
        lines = format_exception(self.type, self.value, self.tb)
        text = "".join(lines)
        text = text.rstrip()

        return text


class ExcInfoFormatter:
    """
    Format an ExceptionInfo to get caller stack we really concern about.
    """

    space_prefix = "    "
    flow_marker = ">"
    error_marker = "E"

    def __init__(self, exc_info: ExceptionInfo, func: object, abspath: bool = False):
        self._exc_info = exc_info
        self._func = func
        self._abspath = abspath

    def pure_traceback(self) -> None:
        """
        Try to cut traceback from the target function.Nothing to do if ExceptionInfo
        does not contain target function.
        """

        if self._func is None:
            # consider some scenario (NameError in a module)
            # which does not have a callable.
            return

        code = get_origin_code(self._func)
        file_name = code.co_filename
        lineno = code.co_firstlineno
        traceback = self._exc_info.traceback

        new_traceback = traceback.pure(path=file_name, first_lineno=lineno)

        if new_traceback is not traceback:
            self._exc_info.traceback = new_traceback

    def repr_exception(self) -> ExceptionRepr:
        """
        The entry to get an exception repr.
        :return: ExceptionRepr.
        """
        self.pure_traceback()

        # now we only show the first traceback only
        item = self._exc_info.traceback[0]
        item_repr = self.repr_traceback_item(item)
        location_repr = self.repr_location(item)
        return ExceptionRepr(item_repr, location_repr)

    def repr_traceback_item(self, item: TracebackItem) -> ItemRepr:
        """
        Get the item repr from a traceback item.
        Notices that different interpreter return disparate crash lineno,
        get crash statement range here.

        Consider the code:

        1      self.assert_that(1)\
        2         .is_equal_to(2)\
        3         .is_equal_to(1)

        In python 3.9.2,interpreter gives line 1 for this crash statement,
        gives line 2 in 3.10,however.

        :param item:
            The tracback item.
        :return:
            formatted ItemRepr.
        """
        # get source firstly, and the mark the crash line.
        source = item.full_source
        start = item.get_first_line_source() - 1

        statement_lineno, end = get_statement_range(source, item.lineno - 1)

        focus = dedent(source[start:end])
        stat_index = statement_lineno - start
        crash_index = item.lineno - 1 - start
        if issubclass(self._exc_info.type, AssertionBaseException):
            marked = self._mark_assert(focus, crash_index, stat_index)
            # only message when use assert_that
            errors = self.error_marker + "   " + str(self._exc_info.value)

        else:
            marked = self._mark_vanilla(focus, crash_index)
            errors = self.error_marker + "   " + self._exc_info.exc_only()

        return ItemRepr(lines=marked, errors=errors)

    def repr_location(self, item: TracebackItem) -> LocationRepr:
        path = self._makepath(item.path)
        return LocationRepr(path, item.lineno, self._exc_info.type_name)

    def _mark_assert(self, source: List[str], crash_index: int, stat_index: int):
        """
        Mark the real crash function for pistar assertion statement.

        Usually the assertion are lines like these:

        "     self.assert_that(1)\"
        "         .is_equal_to(2)\"
        "                  ^^^"
        "         .is_equal_to(1)"

        """

        exc = cast(AssertionBaseException, self._exc_info.value)

        # consider call of "self.assert_that()"
        count = 1 + exc.count

        row_index, row_offset = find_crash_assert(source, stat_index, count)

        padding = "".center(row_offset - 3, " ") + "^^^"
        source.insert(row_index + 1, padding)

        return self._mark_vanilla(source, crash_index)

    def _mark_vanilla(self, source: List[str], crash_index: int):
        source_list = list()
        for line in source[:crash_index]:
            source_list.append(self.space_prefix + line)
        source_list.append(self.flow_marker + "   " + source[crash_index])
        for line in source[crash_index + 1:]:
            source_list.append(self.space_prefix + line)

        return source_list

    def _makepath(self, path):

        if not self._abspath:
            try:
                best_rel_path = py.path.local().bestrelpath(path)

            except OSError:
                return path
            if len(best_rel_path) < len(str(path)):
                path = best_rel_path
        return path


def find_crash_assert(source: List[str], stat_index: int, count: int) -> Tuple[int, int]:
    """
    Find the real crash lineno and offset.
    Use a stack to match the brackets.
    """
    helper: List[str] = list()
    row_index = stat_index
    row_offset = 0
    for row, col in _travel(source, stat_index):
        c = source[row][col]
        if c == "(":
            if not helper:
                # update row_offset when meeting first "("
                row_index = row
                row_offset = col
                count = count - 1
            helper.append(c)
        if c == ")":
            helper.pop()
        if count == 0:
            break

    while True:
        # ignore while space and white line
        if row_offset == 0:
            row_index = row_index - 1
            row_offset = len(source[row_index])

        if source[row_index][row_offset - 1].isalpha():
            break

        row_offset = row_offset - 1

    return row_index, row_offset


def _travel(s: List[str], begin: int = 0):
    row = len(s)
    for i in range(row):
        if i < begin:
            continue
        col = len(s[i])
        for j in range(col):
            yield i, j


def dedent(lines: Iterable[str]) -> List[str]:
    return textwrap.dedent("\n".join(lines)).splitlines()


def get_origin_code(obj: object) -> CodeType:
    try:
        return obj.__code__  # type: ignore[attr-defined]
    except AttributeError as e:
        raise TypeError("no code object found!") from e


def get_statement_start_end(lineno: int, node: ast.AST) -> Tuple[int, Optional[int]]:
    # Use ast.walk to get all statements linenos.
    # AST's line numbers start lineno at 1.
    linenos: List[int] = []
    for x in ast.walk(node):
        if isinstance(x, (ast.stmt, ast.ExceptHandler)):
            # handle if x has decorator.
            # in python3.9,define statement‘s start lineno excludes decorator line,
            # however 3.7 includes.Put decorator line to the list.
            if isinstance(x, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                for d in x.decorator_list:
                    linenos.append(d.lineno - 1)
            linenos.append(x.lineno - 1)
            for name in ("finalbody", "orelse"):
                val: Optional[List[ast.stmt]] = getattr(x, name, None)
                if val:
                    # Treat the finally/orelse part as its own statement.
                    linenos.append(val[0].lineno - 1 - 1)

    # ast.walk use BFS to travel all nodes.
    # we need to sort the list.
    linenos.sort()
    insert_index = bisect_right(linenos, lineno)
    start = linenos[insert_index - 1]
    if insert_index >= len(linenos):
        end = None
    else:
        end = linenos[insert_index]
    return start, end


def get_statement_range(source: List[str], lineno: int) -> Tuple[int, int]:
    content = "\n".join(source)
    node = ast.parse(content)

    start, end = get_statement_start_end(lineno, node)

    if end is None:
        end = len(source)

    if end > start + 1:
        # modify the real end of this statement.
        # ignore the possible decorator for next block.
        end = block_end(source, start, end)

    # pop comments and empty lines
    while end:
        line = source[end - 1].lstrip()
        if line.startswith("#") or not line:
            end -= 1
        else:
            break
    return start, end


def block_end(source: List[str], start: int, end: int) -> int:
    """
    Extract the block of code and return the real end of this block.
    This algorithm is modified from inspect.getblock.
    """
    block_finder = inspect.BlockFinder()
    block_finder.started = source[start][0].isspace()
    it = ((x + "\n") for x in source[start:end])
    try:
        tokens = tokenize.generate_tokens(lambda: next(it))
        for token in tokens:
            block_finder.tokeneater(*token)
    except (inspect.EndOfBlock, IndentationError):
        end = block_finder.last + start
    except Exception:
        return end
    return end


def filter_traceback(item: TracebackItem) -> bool:
    """Return True if a TracebackItem instance should be included in tracebacks.

    We hide traceback of python interpreter.
    """

    filename = item.path
    is_internal = "<" in filename and ">" in filename
    if is_internal:
        return False

    return True
