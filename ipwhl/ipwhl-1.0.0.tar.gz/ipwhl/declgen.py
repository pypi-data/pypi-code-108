#!/usr/bin/env python
# Generate metadata declaration
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
from email.parser import BytesHeaderParser
from pathlib import Path
from typing import Callable, Optional, Sequence, Tuple
from zipfile import ZipFile

from packaging.utils import canonicalize_name
from packaging.version import Version

from .deps import Req, Spec
from .misc import download, ipfs

__all__ = ['generate']

parse_headers = BytesHeaderParser().parse


def dist_info(filename: str) -> Callable[[str], bool]:
    """Return checker for path to filename in .dist_info."""
    return lambda p: p.endswith(f'.dist-info/{filename}') and p.count('/') == 1


def generate(url: str) -> Tuple[str, str, Optional[Spec],
                                Sequence[str], Sequence[Req]]:
    """Return wheel name, CID, Python requirements and dependencies."""
    with download(url) as wheel:
        cid = ipfs('add', '-Qn', wheel.name).rstrip()
        zipfile = ZipFile(wheel)
        wheel_headers, = filter(dist_info('WHEEL'), zipfile.namelist())
        with zipfile.open(wheel_headers) as f:
            tagset = parse_headers(f).get_all('Tag')  # type: ignore
            tags = (t.split('-') for t in tagset)
        metadata_headers, = filter(dist_info('METADATA'), zipfile.namelist())
        with zipfile.open(metadata_headers) as f:
            metadata = parse_headers(f)  # type: ignore

    name = canonicalize_name(metadata['Name']).replace('-', '_')
    version = Version(metadata['Version'])
    tag = '-'.join('.'.join(sorted(frozenset(t))) for t in zip(*tags))
    filename = f'{name}-{version}-{tag}.toml'  # XXX: build tag?
    requires_python = metadata['Requires-Python']
    # Extras in metadata pre-2.1 (PEP 566) are not properly supported.
    extras = metadata.get_all('Provides-Extra') or []
    dependencies = tuple(map(Req, metadata.get_all('Requires-Dist') or []))
    if requires_python is None:
        return filename, cid, None, extras, dependencies
    return filename, cid, Spec(requires_python), extras, dependencies


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument('src', help='URL to wheel file')
    parser.add_argument('dest', type=Path,
                        help='directory to write declaration')
    args = parser.parse_args()
    filename, cid, requires_python, extras, dependencies = generate(args.src)

    args.dest.mkdir(parents=True, exist_ok=True)
    path = args.dest / filename
    with path.open('w') as decl:
        decl.write(f'source = {args.src!r}\ncontent-id = {cid!r}\n')
        if requires_python is not None:
            decl.write(f'requires-python = {str(requires_python)!r}\n')
        decl.write(f'extras = {extras!r}\n')
        if dependencies:
            decl.write('dependencies = [\n')
            for d in dependencies:
                decl.write(f'\t{str(d)!r},\n')
            decl.write(']\n')
        else:
            decl.write('dependencies = []\n')
    print(path)


if __name__ == '__main__': main()
