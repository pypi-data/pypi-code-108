#
# diffoscope: in-depth comparison of files, archives, and directories
#
# Copyright © 2021‒2022 Chris Lamb <lamby@debian.org>
# Copyright © 2021 Sergei Trofimovich
#
# diffoscope is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# diffoscope is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with diffoscope.  If not, see <https://www.gnu.org/licenses/>.

import binascii
import dis
import io
import marshal
import re
import struct
import time
import types

from diffoscope.difference import Difference

from .missing_file import MissingFile
from .utils.file import File

re_memory_address = re.compile(r" at 0x\w+(?=, )")


class PycFile(File):
    DESCRIPTION = "Python .pyc files"
    FILE_TYPE_RE = re.compile(r"^python .*byte-compiled$")

    def compare_details(self, other, source=None):
        if isinstance(other, MissingFile):
            return []

        try:
            return [
                Difference.from_text(
                    describe_pyc(self.path),
                    describe_pyc(other.path),
                    self.path,
                    other.path,
                    source="Python bytecode",
                )
            ]
        except ValueError as exc:
            self.add_comment("Could not decompile bytecode: {}".format(exc))
            return []


def describe_pyc(filename):
    with open(filename, "rb") as f:
        return "\n".join(parse_pyc(f))


def parse_pyc(f):
    magic = f.read(4)
    yield "magic:    {}".format(hexlify(magic))

    f.seek(4, 1)
    moddate = f.read(4)
    modtime = time.asctime(time.gmtime(struct.unpack("<L", moddate)[0]))
    yield "moddate:  {} ({} UTC)".format(hexlify(moddate), modtime)

    filesz = f.read(4)
    filesz = struct.unpack("<L", filesz)
    yield f"files sz: {filesz[0]}"

    code = marshal.load(f)
    yield from show_code(code)


def show_code(code, indent=""):
    yield f"{indent}code"

    indent += "   "

    for x in ("argcount", "nlocals", "stacksize", "flags"):
        yield "{}{: <10}: {!r}".format(indent, x, getattr(code, f"co_{x}"))

    yield from show_hex("code", code.co_code, indent=indent)
    s = io.StringIO()
    dis.disassemble(code, file=s)
    for x in s.getvalue().splitlines():
        yield "{}{}".format(indent, re_memory_address.sub("", x))

    yield f"{indent}consts"
    for const in code.co_consts:
        if isinstance(const, types.CodeType):
            yield from show_code(const, f"{indent}   ")
        else:
            yield f"   {indent}{const!r}"

    for x in (
        "names",
        "varnames",
        "freevars",
        "cellvars",
        "filename",
        "name",
        "firstlineno",
    ):
        yield "{}{: <10} {!r}".format(indent, x, getattr(code, f"co_{x}"))

    yield from show_hex("lnotab", code.co_lnotab, indent=indent)


def show_hex(label, val, indent):
    val = hexlify(val)

    if len(val) < 60:
        yield f"{indent}{label} {val}"
        return

    yield f"{indent}{label}"
    for i in range(0, len(val), 60):
        yield "{}   {}".format(indent, val[i : i + 60])


def hexlify(val):
    return "0x{}".format(binascii.hexlify(val).decode("utf-8"))
