from io import StringIO
from typing import Sequence

import attr

from _pistar.terminal import TerminalWriter


@attr.s(eq=False)
class BaseRepr:
    def __str__(self):
        io = StringIO()
        w = TerminalWriter(io)
        self.gen_repr(w)
        return io.getvalue().rstrip()

    def gen_repr(self, writer: TerminalWriter):
        raise NotImplementedError()


@attr.s(eq=False, auto_attribs=True)
class ExceptionRepr(BaseRepr):
    reprs: "ItemRepr"
    location: "LocationRepr"

    def gen_repr(self, writer: TerminalWriter):
        self.reprs.gen_repr(writer)
        writer.line("")
        self.location.gen_repr(writer)


@attr.s(eq=False)
class LocationRepr(BaseRepr):
    path = attr.ib(type=str, converter=str)
    lineno = attr.ib(type=int)
    exception = attr.ib(type=str)

    def gen_repr(self, writer: TerminalWriter):
        writer.line(f"{self.path}:{self.lineno} {self.exception}")


@attr.s(eq=False)
class ItemRepr(BaseRepr):
    lines = attr.ib(type=Sequence[str])
    errors = attr.ib(type=str)

    def gen_repr(self, writer: TerminalWriter):
        if not self.lines:
            return

        for line in self.lines:
            writer.line(line)
        if self.errors:
            writer.line(self.errors)


@attr.s(eq=False)
class AssertRepr(ItemRepr):
    def gen_repr(self, writer: TerminalWriter):
        pass
