#!/usr/bin/env python3
# -*- coding: utf-8, vim: expandtab:ts=4 -*-

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os

from typing import Tuple


def copy_stubs(from_dir: str, to_dir: str, change: Tuple[str, str]) -> None:
    from_dir, to_dir = map(lambda x: x.strip(), (from_dir, to_dir))
    change_from, change_to = map(lambda x: x.strip(), change)

    if not os.path.exists(to_dir) or not os.path.isdir(to_dir):
        raise RuntimeError('TO dir does not exist: {}'.format(to_dir))

    try:
        file_list = os.listdir(from_dir)
    except FileNotFoundError:
        raise RuntimeError('FROM dir does not exist: {}'.format(from_dir))
    except NotADirectoryError:
        raise RuntimeError('FROM dir is not a directory: {}'.format(from_dir))

    for filename_old in file_list:

        print('')
        print(' ' * 3, filename_old)

        filename, _ = os.path.splitext(filename_old)

        filename_new = filename.replace(change_from, change_to) + '.txt'

        print(' ->', filename_new)

        path_new = os.path.join(to_dir, filename_new)

        if os.path.isfile(path_new):
            print(' ', '#', 'Already existed.')
            continue

        with open(path_new, 'wt') as fh_new:
            print('', file=fh_new)

        print(' ', '#', 'Done.')

    print('')


def main():
    src_dir = input('Source dir: ')
    dest_dir = input('Destination dir: ')

    replace = input('Replace: ')
    replace_with = input('Replace with: ')

    try:
        copy_stubs(src_dir, dest_dir, (replace, replace_with))
    except RuntimeError as err:
        print(err)


if __name__ == '__main__':
    main()
