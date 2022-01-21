#!/usr/bin/env python
# Publish declarations to IPFS
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
from contextlib import suppress
from pathlib import Path, PurePosixPath
from subprocess import SubprocessError

from packaging.utils import canonicalize_name
from tomli import loads

from .misc import download, ipfs
from .prefix import prefix


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument('src', type=Path, help='metadata root directory')
    parser.add_argument('dest', type=PurePosixPath, help='IPFS MFS path')
    args = parser.parse_args()
    files = frozenset(args.src.glob('*/*/*.toml'))
    projects = {canonicalize_name(project): project
                for project in (file.parent.name for file in files)}

    # Garbage-collect projects
    for project in ipfs('files', 'ls', args.dest).splitlines():
        if project in projects: continue
        path = args.dest / project
        ipfs('files', 'rm', '-r', path)
        print(f'removed {path}')

    # Garbage-collect wheels
    for normalized in projects:
        path = args.dest / normalized
        ipfs('files', 'mkdir', '-p', path)
        for whl in ipfs('files', 'ls', path).splitlines():
            toml = whl.replace('.whl', '.toml')
            unnormalized = projects[normalized]
            if args.src / prefix(unnormalized) / unnormalized / toml in files:
                continue
            wheel = path / whl
            ipfs('files', 'rm', wheel)
            print(f'removed {wheel}')

    for file in files:
        declaration = loads(file.read_text())
        filename = file.name.replace('.toml', '.whl')
        wheel = args.dest / canonicalize_name(file.parent.name) / filename

        # Check if wheel already exists and has the same content
        with suppress(SubprocessError):
            cid = ipfs('files', 'stat', '--hash', wheel).rstrip()
            if cid == declaration['content-id']:
                continue
            else:
                ipfs('files', 'rm', wheel)
                print(f'removed {wheel}')

        # Download to IPFS MFS
        with download(declaration['source']) as f:
            cid = ipfs('add', '-Q', f.name).rstrip()
        ipfs('files', 'cp', f'/ipfs/{cid}', wheel)
        print(f'added {cid} {wheel}')

    cid = ipfs('files', 'stat', '--hash', args.dest).rstrip()
    print(f'published to /ipfs/{cid}')


if __name__ == '__main__': main()
