#!/usr/bin/env python3
# coding: utf-8

import sys


def hexify(path: str):
    with open(path, 'rb') as fin, open(path + '.hex', 'w') as fout:
        chunk = fin.read(32)
        while chunk:
            print(chunk.hex())
            print(chunk.hex(), file=fout)
            chunk = fin.read(32)


def _run():
    for path in sys.argv[1:]:
        hexify(path)


if __name__ == '__main__':
    _run()
