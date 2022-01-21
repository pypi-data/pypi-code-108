# High-level handling of wheel tags
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

import re
from typing import Any, Iterator, Optional, Tuple

from packaging.tags import (Tag, compatible_tags, cpython_tags,
                            generic_tags, mac_platforms)

MANYLINUX = re.compile(r'manylinux(1|2010|2014|_\d+_\d+)_(?P<arch>.+)')
MACOSX = re.compile(r'macosx_\d+_\d+_(?P<arch>.+)')
MACOSX_VERSION = re.compile(r'macosx_(?P<major>\d+)_(?P<minor>\d+)_.+')
MACOSX_INTEL = frozenset({'x86_64', 'i386'})
MACOSX_UNIVERSAL = frozenset({'x86_64', 'i386', 'ppc64', 'ppc', 'intel'})
MACOSX_UNIVERSAL2 = frozenset({'arm64', 'x86_64'})
# PEP 425 considers major version in Python tag only have one digit.
PYTHON = re.compile(r'([a-z]+)(\d)(\d*)')

__all__ = ['parse_platform', 'parse_interpreter', 'overlapping', 'compatags']


def parse_platform(platform_tag: str) -> Tuple[str, str]:
    """Return OS and architecture unique to the given platform tag."""
    # Windows doesn't support many architectures.
    if platform_tag == 'win_amd64': return 'windows', 'amd64'
    if platform_tag == 'win_ia64': return 'windows', 'ia64'
    if platform_tag == 'win32': return 'windows', 'x86'

    manylinux = MANYLINUX.match(platform_tag)
    if manylinux is not None:
        return 'manylinux', manylinux.group('arch')

    macosx = MACOSX.match(platform_tag)
    if macosx is not None:
        return 'macosx', macosx.group('arch')

    # TODO: support other platforms, e.g. *BSD and *nix
    os, arch = platform_tag.split('_', 1)
    return os, arch


def overlapping_platform(platform0: str, platform1: str) -> bool:
    """Return if the given tags are compatible with a same platform."""
    if 'any' in (platform0, platform1): return True
    os0, arch0 = parse_platform(platform0)
    os1, arch1 = parse_platform(platform1)
    if os0 != os1: return False
    if arch0 == arch1: return True
    if os0 != 'macosx': return False
    if 'intel' in (arch0, arch1):
        return bool({arch0, arch1} & MACOSX_INTEL)
    if 'universal' in (arch0, arch1):
        return bool({arch0, arch1} & MACOSX_UNIVERSAL)
    if 'universal2' in (arch0, arch1):
        return bool({arch0, arch1} & MACOSX_UNIVERSAL2)
    # FIXME: macosx_fat{64,32,} are not handled
    return False


def parse_interpreter(interpreter_tag: str) -> Tuple[str, int, Optional[int]]:
    """Return implementation, major and minor version of interpreter."""
    match = PYTHON.match(interpreter_tag)
    if match is None:
        raise ValueError(f'invalid interpreter tag: {interpreter_tag!r}')
    impl, major, minor = match.groups()
    return impl, int(major), int(minor) if minor else None


def equall(iterator: Iterator[Any]) -> bool:
    """Return if all items are equal."""
    try:
        first = next(iterator)
    except StopIteration:
        return True
    else:
        return all(i == first for i in iterator)


def overlapping_interpreter(*interpreters: str) -> bool:
    """Return if the given tags are compatible with a same interpreter."""
    impls, majors, minors = zip(*map(parse_interpreter, interpreters))
    return (equall(filter(lambda impl: impl != 'py', impls))
            and equall(iter(majors)) and equall(filter(None, minors)))


def overlapping_abi(abi0: str, abi1: str) -> bool:
    """Return if the given tags is compatible with a same ABI."""
    # See https://github.com/pypa/packaging/pull/231#discussion_r711718637
    if abi0 == abi1: return abi0 != 'none'
    if abi0 > abi1: abi1, abi0 = abi0, abi1
    if abi0 == 'abi3' and abi1.startswith('cp3'): return True
    return False


def overlapping(tag0: Tag, tag1: Tag) -> bool:
    """Return if the given tags are compatible with a same system."""
    if not overlapping_platform(tag0.platform, tag1.platform): return False
    if overlapping_interpreter(tag0.interpreter, tag1.interpreter): return True
    return overlapping_abi(tag0.abi, tag1.abi)


def compatags(interpreter: str, platform: str) -> Iterator[Tag]:
    """Return tags compatible with given interpreter and platform.

    The order of the sequence corresponds to priority order for the
    interpreter, from most to least important.
    """
    os, arch = parse_platform(platform)
    # Or more precisely, linked against glibc on Linux kernel
    if os == 'manylinux':
        platforms = [f'manylinux1_{arch}', f'manylinux2010_{arch}',
                     f'manylinux2014_{arch}', f'manylinux_2_24_{arch}']
    elif os == 'macosx':
        mac_version = MACOSX_VERSION.match(platform)
        assert mac_version is not None
        mac_major, mac_minor = map(int, mac_version.groups())
        platforms = list(mac_platforms((mac_major, mac_minor), arch))
    else:
        platforms = [platform]

    impl, major, minor = parse_interpreter(interpreter)
    if impl == 'cp':
        assert minor is not None
        yield from cpython_tags((major, minor), platforms=platforms)
    else:
        yield from generic_tags(interpreter, platforms=platforms)
    version = (major,) if minor is None else (major, minor)
    yield from compatible_tags(version, interpreter, platforms)
