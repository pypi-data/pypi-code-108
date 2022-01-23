#!/usr/bin/env python3
# coding: utf-8

import os
import re
import shlex

import requests
from joker.cast.collective import CircularReferenceDetector
from joker.stream import Stream
from joker.stream.shell import RecursiveInclusionStream, ShellStream

regex_http = re.compile(r'https?://')


def _abspath(path):
    return os.path.abspath(os.path.expanduser(path))


def http_get(url):
    return requests.get(url).text


class UnsourceStream(RecursiveInclusionStream, ShellStream):
    def __init__(self, file, *filters):
        super(UnsourceStream, self).__init__(file, *filters)
        self.crd = None

    def include(self, locator):
        return self.openloc(locator, self.crd)

    @classmethod
    def openloc(cls, locator, crd=None):
        if isinstance(locator, str) and regex_http.match(locator):
            stm = cls.wrap(http_get(locator))
            crd_ident = locator
        else:
            stm = super(UnsourceStream, cls).open(locator, mode='r')
            crd_ident = _abspath(locator)
        if crd is None:
            stm.crd = CircularReferenceDetector(crd_ident)
        else:
            stm.crd = crd.branch(crd_ident)
        stm.name = locator
        return stm


def get_rc_path(name, userdir=True):
    if userdir:
        return _abspath('~/.' + name)
    from joker.superuser import utils
    utils.make_joker_superuser_dir()
    return utils.under_joker_superuser_dir(name)


def has_sourced(loc, t_loc):
    t_loc = t_loc if regex_http.match(t_loc) else _abspath(t_loc)
    ustm = UnsourceStream.openloc(loc)
    for line in ustm:
        s_loc = ustm.check_for_inclusion(line)
        if not s_loc:
            continue
        s_loc = s_loc if regex_http.match(s_loc) else _abspath(s_loc)
        if s_loc == t_loc:
            return True
    return False


def add_source(path, target):
    if has_sourced(path, target):
        return
    with open(path, 'a') as fout:
        line = '\nsource ' + shlex.quote(target) + '\n'
        fout.write(line)


def unsource(outpath, *locators):
    with Stream.open(outpath, 'w') as fout:
        for loc in locators:
            with UnsourceStream.openloc(loc) as ustm:
                for line in ustm.setup().dense():
                    fout.write(line + os.linesep)


def run(prog, args):
    import argparse
    desc = 'expand shell scripts with sourced files replaced by contents'
    pr = argparse.ArgumentParser(prog=prog, description=desc)
    pr.add_argument('-a', '--apply', choices=['zshrc', 'bashrc'])
    pr.add_argument('files', nargs='+', help='shell scripts')
    ns = pr.parse_args(args)
    if not ns.apply:
        return unsource('-', *ns.files)
    outpath = get_rc_path(ns.apply, userdir=False)
    unsource(outpath, *ns.files)
    add_source(get_rc_path(ns.apply, userdir=True), outpath)
