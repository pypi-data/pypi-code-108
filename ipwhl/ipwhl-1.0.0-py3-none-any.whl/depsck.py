#!/usr/bin/env python
# Check for dependencies satisfaction
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
from collections import defaultdict
from contextlib import suppress
from pathlib import Path
from sys import stderr, stdin
from typing import (Dict, FrozenSet, Iterable, Iterator, List,
                    Mapping, NamedTuple, Optional, Sequence, Tuple)

from packaging.markers import Marker
from packaging.tags import Tag
from packaging.utils import canonicalize_name, parse_wheel_filename
from packaging.version import Version
from tomli import loads

from .deps import Req, Spec
from .misc import compose
from .tags import compatags, parse_interpreter, parse_platform

OS_NAME = dict(manylinux='posix', macosx='posix', windows='nt')
SYS_PLATFORM = dict(manylinux='linux', windows='win32', macosx='darwin')
PLATFORM_SYSTEM = dict(manylinux='Linux', macosx='Darwin', windows='Windows')
IMPLEMENTATION_NAME = dict(py='Python', cp='CPython', pp='PyPy',
                           ip='IronPython', jy='Jython')


class Dist(NamedTuple):
    """Distribution's metadata to check for dependencies on a platform."""
    name: str
    version: Version
    build_tag: tuple
    tags: FrozenSet[Tag]
    requires_python: Spec
    extras: FrozenSet[str]
    dependencies: FrozenSet[Req]


def collect(root: Path) -> Dict[Tag, List[Dist]]:
    """Find all distributions whose declaration in given directory."""
    dists = defaultdict(list)
    for file in root.glob('*/*/*.toml'):
        identifier = parse_wheel_filename(file.name.replace('.toml', '.whl'))
        decl = loads(file.read_text())
        dist = Dist(*identifier, Spec(decl.get('requires-python', '')),
                    frozenset(decl['extras']),
                    frozenset(map(Req, decl['dependencies'])))
        for tag in dist.tags: dists[tag].append(dist)
    return dict(dists)


def splitenv(environment: str) -> Tuple[str, str]:
    """Return interpreter tag and platform tag."""
    interpreter, platform = environment.rstrip().split(maxsplit=1)
    return interpreter, platform


def mkenv(interpreter: str, platform: str) -> Dict[str, str]:
    """Generate environment for requirement marker evaluation."""
    impl, python_major, python_minor = parse_interpreter(interpreter)
    assert python_minor is not None
    implementation_name = IMPLEMENTATION_NAME[impl]
    implementation_version = f'{python_major}.{python_minor}.0'
    os, arch = parse_platform(platform)
    return dict(os_name=OS_NAME.get(os, os),
                sys_platform=SYS_PLATFORM.get(os, os),
                platform_machine=arch,
                platform_python_implementation=implementation_name,
                platform_release='',  # unsupported
                platform_system=PLATFORM_SYSTEM.get(os, os.capitalize()),
                platform_version='',  # unsupported
                python_version=f'{python_major}.{python_minor}',
                python_full_version=implementation_version,
                implementation_name=implementation_name.lower(),
                implementation_version=implementation_version)


def relevant(marker: Optional[Marker], environment: Dict[str, str],
             extras: Iterable[str]) -> bool:
    """Return of the marker is relevant on given environment."""
    if marker is None: return True
    return any(marker.evaluate({**environment, 'extra': extra})
               for extra in extras)


def check(environments: Iterable[Tuple[str, str]],
          distributions: Mapping[Tag, Sequence[Dist]]) -> Iterator[str]:
    """Return broken environments with missing dependencies."""
    for interpreter, platform in environments:
        env = mkenv(interpreter, platform)
        tags = frozenset(compatags(interpreter, platform))
        concerned = {dist.name: dist
                     for tag, dists in distributions.items()
                     if tag in tags
                     for dist in dists}
        for dist in concerned.values():
            for req in dist.dependencies:
                extras = dist.extras or frozenset({''})
                if not relevant(req.marker, env, extras): continue
                with suppress(KeyError):
                    candidate = concerned[canonicalize_name(req.name)].version
                    if req.specifier.contains(candidate, prereleases=True):
                        continue
                yield f'{interpreter} {platform}: {str(req)}'


def main() -> int:
    parser = ArgumentParser()
    parser.add_argument('dists', metavar='dir', type=compose(collect, Path),
                        help='metadata root directory')
    broken = tuple(check(map(splitenv, stdin), parser.parse_args().dists))
    if not broken: return 0
    print('\n'.join(broken), file=stderr)
    return 1


if __name__ == '__main__': exit(main())
