#!/usr/bin/env python3
# coding: utf-8

import os
from collections import deque


def iter_path_bisections(path: str):
    names = deque([])
    while path:
        path, name = os.path.split(path)
        if not path or not name:
            break
        names.appendleft(name)
        yield path, os.path.join(*names)


class PathMapper:
    def __init__(self, fs_path: str, user_path: str):
        self._real_prefix = os.path.realpath(fs_path)
        self._user_prefix = user_path

    def userpath(self, *paths):
        return os.path.join(self._user_prefix, *paths)

    def realpath(self, *paths):
        return os.path.join(self._real_prefix, *paths)

    def under(self, *paths, mkdirs=False):
        path = self.realpath(*paths)
        if mkdirs:
            dir_ = os.path.split(path)[0]
            os.makedirs(dir_, exist_ok=True)
        return path

    def exists(self, *paths):
        return os.path.exists(self.realpath(*paths))

    def isfile(self, *paths):
        return os.path.isfile(self.realpath(*paths))

    def isdir(self, *paths):
        return os.path.isdir(self.realpath(*paths))
