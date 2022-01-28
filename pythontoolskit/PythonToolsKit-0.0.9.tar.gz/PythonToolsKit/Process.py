#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###################
#    This package implements tools to build python package and tools.
#    Copyright (C) 2022  Maurice Lambert

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
###################

r"""
This package implements tools to build python package and tools.

>>> for line, error, code in real_time_process_output("./program1 && ./program2", shell=True): print(line)
...
b"<output line 1>"
b"<output line 2>"
b"<output line ...>"
b"<output line n>"
>>> print(code, error)
0, b"<error lines>"
>>> for line, error, code in real_time_process_output('python -c "print(input());print(input())"', input=b'test\n', timeout=2, shell=True): print(line)
...
b'test\n'
>>> print(code, error)
1 b'Traceback (most recent call last):\r\n  File "<string>", line 1, in <module>\r\nEOFError: EOF when reading a line\r\n'
>>> for line, error, code in real_time_process_output('python -c "print(input());print(input())"', input=b'test\ntest2\n', timeout=2, shell=True): print(line)
...
b'test\r\n'
b'test2\r\n'
>>> print(code, error)
0 b''
>>>
"""

__version__ = "0.0.1"
__author__ = "Maurice Lambert"
__author_email__ = "mauricelambert434@gmail.com"
__maintainer__ = "Maurice Lambert"
__maintainer_email__ = "mauricelambert434@gmail.com"
__description__ = """
This package implements tools to build python package and tools.
"""
license = "GPL-3.0 License"
__url__ = "https://github.com/mauricelambert/PythonToolsKit"

copyright = """
PythonToolsKit  Copyright (C) 2022  Maurice Lambert
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions.
"""
__license__ = license
__copyright__ = copyright

__all__ = ["real_time_process_output"]

from collections.abc import Iterator
from subprocess import Popen, PIPE
from threading import Timer
from typing import Tuple


def real_time_process_output(
    *args, input: bytes = b"", timeout: int = 0, **kwargs
) -> Iterator[Tuple[bytes, bytes, int]]:

    """
    This function returns lines of process in real time.

    args and kwargs are sent to subprocess.Popen.
    """

    process = Popen(*args, stdin=PIPE, stdout=PIPE, stderr=PIPE, **kwargs)
    poll = process.poll

    if timeout:
        timer = Timer(timeout, process.kill)

    stdin = process.stdin
    flush = stdin.flush
    flush()
    stdin.write(input)
    flush()
    stdin.close()

    stdout = process.stdout
    readline = stdout.readline

    data = readline()

    while poll() is None:
        yield data, None, None
        data = readline()

    timer.cancel()
    yield stdout.read(), process.stderr.read(), process.returncode
