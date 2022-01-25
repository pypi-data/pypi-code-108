#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copy source file time_hdr to temporary file and remove the type: ignore
comments to allow full type checking with wrapt

"""
import sys
import os


def remove_file(path_to_file_to_remove):
    os.remove(path_to_file_to_remove)


def remove_type_ignore(path_to_read_file, path_to_write_file) -> None:
    with open(path_to_read_file, 'r') as file:  # open for read
        file_lines = file.readlines()

    search_text = 'type: ignore'
    replace_text = ' '
    for idx, file_line in enumerate(file_lines):
        if search_text in file_line:
            file_lines[idx] = file_lines[idx].replace(search_text,
                                                      replace_text)

    with open(path_to_write_file, 'w') as file:
        file.writelines(file_lines)


def main() -> None:
    if sys.argv[1] == '--pre':
        # sys.argv[2] is file path to source file to read
        # sys.argv[3] is file path to destination to write modified source file
        remove_type_ignore(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == '--post':
        # sys.argv[2] is file to remove
        remove_file(sys.argv[2])
    else:
        assert False


if __name__ == '__main__':
    sys.exit(main())
