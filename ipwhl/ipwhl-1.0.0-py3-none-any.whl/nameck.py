#!/usr/bin/env python
# Check IPWHL metadata files organization
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

from argparse import ArgumentParser
from itertools import combinations, product
from os import walk
from os.path import join, splitext
from pathlib import Path
from sys import stderr
from typing import FrozenSet, Iterator, Optional

from packaging.tags import Tag
from packaging.utils import (InvalidWheelFilename, canonicalize_name,
                             parse_wheel_filename)

from .prefix import prefix
from .tags import overlapping


def project_name(root: str, dirpath: str) -> Optional[str]:
    """Return the project name if dirpath is valid for one."""
    try:
        *parent, dirprefix, name = Path(dirpath).parts
    except ValueError:  # not enough values to unpack
        return None
    if Path(join(*parent)) != Path(root): return None
    if dirprefix == prefix(name):
        return name
    else:
        return None


def tagset(project: str, filename: str) -> Optional[FrozenSet[Tag]]:
    """Return tags if filename is valid for TOML declaration."""
    root, ext = splitext(filename)
    if ext != '.toml': return None
    try:
        name, version, build, tags = parse_wheel_filename(f'{root}.whl')
    except InvalidWheelFilename:
        return None
    if name != canonicalize_name(project): return None
    return tags


def find_invalid(root: str) -> Iterator[str]:
    """Return an iterator of violating paths."""
    for dirpath, dirnames, filenames in walk(root):
        # We only consider what can be tracked by git.
        if not filenames: continue
        project = project_name(root, dirpath)
        if project is None:
            yield dirpath
            continue
        declarations = []
        for filename in filenames:
            path, tags = join(dirpath, filename), tagset(project, filename)
            if tags is None:
                yield path
            else:
                declarations.append((path, tags))
        for (p0, tags0), (p1, tags1) in combinations(declarations, 2):
            if any(overlapping(t0, t1) for t0, t1 in product(tags0, tags1)):
                yield f'{p0} {p1}'


def main() -> int:
    parser = ArgumentParser()
    parser.add_argument('dir', help='metadata root directory')
    args = parser.parse_args()
    invalid = tuple(find_invalid(args.dir))
    if not invalid: return 0
    print('\n'.join(invalid), file=stderr)
    return 1


if __name__ == '__main__': exit(main())
