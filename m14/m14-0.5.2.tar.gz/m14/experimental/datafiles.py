#!/usr/bin/env python3
# coding: utf-8

import csv
import itertools
import sys

from volkanic.utils import load_json5_file


def dicts_to_rows(dicts: list, keys: list):
    return [[d.get(k) for k in keys] for d in dicts]


def rows_to_dicts(rows: list, keys: list):
    return [dict(zip(keys, r)) for r in rows]


def _write_to_csv(rows, path: str = None):
    if path is None:
        wr = csv.writer(sys.stdout)
        wr.writerows(rows)
        return
    with open(path, 'a') as fout:
        wr = csv.writer(fout)
        wr.writerows(rows)


def dicts_to_csv(dicts: list, keys: list, path: str = None):
    if not dicts:
        return
    if not keys:
        keys = list(dicts[0].keys())
    rows = dicts_to_rows(dicts, keys)
    _write_to_csv(itertools.chain([keys], rows), path)


def json_to_csv(path: str, keys: list = None):
    data = load_json5_file(path)
    if not isinstance(data, list):
        raise TypeError(f'a list is required, got {type(data)}')
    if not data:
        return


def jsonl_to_csv(path: str, keys: list = None):
    data = load_json5_file(path)
    if not isinstance(data, list):
        raise TypeError(f'a list is required, got {type(data)}')
    if not data:
        return
    keys = list(data[0].keys())
    rows = dicts_to_rows(data, keys)
    wr = csv.writer(sys.stdout)
    wr.writerow(keys)
    wr.writerows(rows)


if __name__ == '__main__':
    json_to_csv(sys.argv[1])
