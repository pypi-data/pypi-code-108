#!/usr/bin/env python3
# coding: utf-8

import argparse
import shlex
import sys
from joker.superuser.environ import GlobalInterface

import pyperclip
from joker.textmanip.url import url_simplify

gi = GlobalInterface()


def smart_url_simplify(url, queries):
    config = gi.conf['urls']
    for pattern, _queries in config.items():
        if pattern in url:
            queries = _queries
            break
    return str(url_simplify(url, queries))


def _copy_and_print(url: str):
    print(url)
    print(shlex.quote(url))
    pyperclip.copy(url)


def run(prog, args):
    desc = 'simplify a url'
    parser = argparse.ArgumentParser(prog=prog, description=desc)
    parser.add_argument('url')
    parser.add_argument('query', nargs='*')
    ns = parser.parse_args(args)
    url = str(smart_url_simplify(ns.url, ns.query))
    _copy_and_print(url)


def runloop(prog, args):
    while True:
        userinput = input('URL> ')
        parts = shlex.split(userinput)
        if not parts:
            continue
        url = parts[0]
        queries = parts[1:]
        try:
            url = smart_url_simplify(url, queries)
        except Exception as e:
            print(e.__class__.__name__, e, file=sys.stderr)
            continue
        _copy_and_print(url)
