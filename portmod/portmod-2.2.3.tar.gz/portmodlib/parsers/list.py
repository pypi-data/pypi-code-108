# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

"""Module for reading from list files"""

import os
from typing import List, Optional


class CommentedLine(str):
    """A line in a list file which is preceeded by a comment"""

    comment: List[str]


def read_list(listpath: str, encoding: Optional[str] = None) -> List[str]:
    """
    Reads the given list file and returns its contents

    Comments are supported, and comment blocks get attached to all lines following them
    until a blank line is encountered.
    """
    results: List[str] = []
    comment: Optional[List[str]] = None
    with open(listpath, mode="r", encoding=encoding) as list_file:
        for line in list_file.read().splitlines():
            line = line.strip()
            if line.startswith("#"):
                if comment:
                    comment.append(line)
                else:
                    comment = [line]
            elif line:
                if comment:
                    commented = CommentedLine(line)
                    commented.comment = comment
                    results.append(commented)
                else:
                    results.append(line)
            else:
                comment = None
    return results


def add_list(listpath: str, entry: str):
    """Appends the given value to the list file"""
    os.makedirs(os.path.dirname(listpath), exist_ok=True)
    with open(listpath, mode="a") as list_file:
        print(entry, file=list_file)


def write_list(path: str, contents: List[str]):
    """Writes a list file containing the given list"""
    with open(path, "w") as file:
        for value in contents:
            print(value, file=file)
