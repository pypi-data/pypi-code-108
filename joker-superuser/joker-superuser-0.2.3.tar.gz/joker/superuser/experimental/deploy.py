#!/usr/bin/env python3
# coding: utf-8

import glob
import os
import re

import json5
from joker.interfaces.repos import Repository


def _fmt_error_line(colno: int, errmsg: str):
    leading_whitespaces = ' ' * (colno - 3)
    underline = '^' * 6
    return f'{leading_whitespaces}{underline} <- {errmsg}'


def _parse_error_msg(errmsg: str, filename: str):
    mat = re.search(r':(?P<lineno>\d+).* column (?P<colno>\d+)', errmsg)
    return (
        int(mat.groupdict()['lineno']),
        int(mat.groupdict()['colno']),
        errmsg.replace('<string>', filename),
    )


def _check_json5(path: str):
    lines = open(path)
    lines = [s.rstrip() for s in lines]
    try:
        _ = json5.loads(os.linesep.join(lines))
        print('OK', path, sep='\t')
    except ValueError as err:
        lineno, colno, errmsg = _parse_error_msg(str(err), path)
        lines.insert(lineno, _fmt_error_line(colno, errmsg))
        for line in lines:
            print(line)
        print('ERR', path, sep='\t')


def check_json5(path: str):
    try:
        _ = json5.load(open(path))
        print('OK', path, sep='\t')
    except ValueError:
        print('ERR', path, sep='\t')


def _glob_multiple(*patterns):
    paths = []
    for pat in patterns:
        paths.extend(glob.glob(pat))
    return paths


def check_json5_files():
    paths = _glob_multiple('*.json', '*.json5', '*/*.json', '*/*.json5')
    for path in paths:
        check_json5(path)


def pull_all():
    repos = Repository.find('.')
    for repo in repos:
        repo.pull()
