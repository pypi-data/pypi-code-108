#!/usr/bin/env python
# Check metadata declaration
# Copyright (C) 2021-2022  Nguyễn Gia Phong
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

from contextlib import suppress
from itertools import compress
from operator import itemgetter
from pathlib import Path
from sys import stderr, stdin
from typing import Any, Callable, Iterable, Iterator, Type
from urllib.error import HTTPError, URLError

from packaging.requirements import InvalidRequirement
from packaging.specifiers import InvalidSpecifier
from tomli import TOMLDecodeError, loads

from .declgen import generate
from .deps import Req, Spec
from .misc import compose


def invalid_field(truth: Any, raw: Any, transform: Callable = lambda x: x,
                  exceptions: Iterable[Type[Exception]] = (),
                  *, optional: bool = False) -> bool:
    """Test the field's validity, with exceptions treated as invalid."""
    if optional and truth is None and raw is None: return False
    with suppress(*exceptions): return truth != transform(raw)
    return True


def check(path: Path) -> Iterator[str]:
    """Return issues with the declaration path points to, if any."""
    try:
        declaration = loads(path.read_text())
    except TOMLDecodeError:
        yield 'format'
        return
    try:
        filename, cid, requires_python, extras, dependencies = generate(
            declaration['source'])
    except (KeyError, HTTPError, URLError):
        yield 'source'
        return

    if invalid_field(filename, path.name): yield 'filename'
    if invalid_field(cid, declaration, itemgetter('content-id'), [KeyError]):
        yield 'content-id'
    if invalid_field(requires_python, declaration.get('requires-python'),
                     Spec, [InvalidSpecifier], optional=True):
        yield 'requires-python'
    if invalid_field(frozenset(dependencies), declaration,
                     compose(lambda reqs: frozenset(map(Req, reqs)),
                             itemgetter('dependencies')),
                     [KeyError, InvalidRequirement]):
        yield 'dependencies'

    try:
        declared_extras = frozenset(declaration['extras'])
    except KeyError:
        yield 'extras'
    else:
        all_extras = frozenset(extras)
        if declared_extras == all_extras:
            pass
        elif declared_extras.issubset(all_extras):
            ignored_extras = all_extras - declared_extras
            print(f"{path}: extras ({', '.join(ignored_extras)})")
        else:
            yield 'extras'


def main() -> int:
    paths = tuple(map(compose(Path, str.rstrip), stdin))
    invalid = tuple(map(compose(tuple, check), paths))
    if not any(invalid): return 0
    for path, reasons in compress(zip(paths, invalid), invalid):
        print(f"{path}: {', '.join(reasons)}", file=stderr)
    return 1


if __name__ == '__main__': exit(main())
