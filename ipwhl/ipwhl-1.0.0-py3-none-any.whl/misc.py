# Miscellaneous helpers
# Copyright (C) 2021  Nguyễn Gia Phong
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from contextlib import contextmanager
from functools import partial, reduce
from os import PathLike
from shlex import join
from subprocess import (STDOUT, CalledProcessError,
                        SubprocessError, check_output)
from tempfile import NamedTemporaryFile
from typing import IO, Callable, Iterator, Union
from urllib.request import urlopen

__all__ = ['compose', 'download', 'ipfs']
CHUNK_SIZE = 8192


def compose(*callables: Callable) -> Callable:
    """Return the composite callable."""
    return reduce(lambda f, g: lambda x: f(g(x)), callables)


@contextmanager
def download(url: str) -> Iterator[IO[bytes]]:
    """Download file from given URL and return its context manager."""
    with NamedTemporaryFile() as fo:
        with urlopen(url) as fi:
            for chunk in iter(partial(fi.read, CHUNK_SIZE), b''):
                fo.write(chunk)
        fo.flush()
        yield fo


def ipfs(*args: Union[str, PathLike]) -> str:
    """Run given IPFS command and return the output."""
    try:
        return check_output(('ipfs', *args),
                            encoding='utf-8', stderr=STDOUT)
    except CalledProcessError as e:
        message = f'{join(map(str, e.cmd))} [{e.returncode}]: {e.output}'
        raise SubprocessError(message) from None
