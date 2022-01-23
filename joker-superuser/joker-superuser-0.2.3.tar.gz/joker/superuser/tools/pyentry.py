#!/usr/bin/env python3
# coding: utf-8

import os
import re

from joker.cast.syntax import printerr

_template = r"""#!/usr/bin/env python3
# coding: utf-8
import re, sys; from {mod} import {call}
if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit({call}())
"""

_regex = re.compile(r'(?P<cmd>\w+)=(?P<mod>\w[\w.]*\w):(?P<call>\w+)$')


def make_entrypoint_script(spec, targetdir=None):
    spec = ''.join(spec.split())
    mat = _regex.match(spec)
    if not mat:
        raise ValueError('bad spec "{}"'.format(spec))
    params = mat.groupdict()
    text = _template.format(**params)
    if not targetdir:
        return print(text)
    path = os.path.join(targetdir, params.get('cmd'))
    if os.path.exists(path):
        raise FileExistsError(path)
    with open(path, 'w') as fout:
        fout.write(text)
    os.chmod(path, int('754', 8))


class Spy(object):
    def __init__(self):
        self.args = None
        self.kwargs = None

    def __call__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def load_setup_file(self, path):
        import setuptools
        path = os.path.abspath(path)
        cwd = os.getcwd()
        setup = setuptools.setup
        try:
            os.chdir(os.path.dirname(path))
            setuptools.setup = self
            code = open(path).read()
            exec(code, {'__file__': path})
        finally:
            os.chdir(cwd)
            setuptools.setup = setup


def inspect_setuppy(path):
    path = os.path.abspath(path)
    if os.path.isdir(path):
        path = os.path.join(path, 'setup.py')
    if not os.path.isfile(path):
        raise FileNotFoundError(path)
    spy = Spy()
    spy.load_setup_file(path)
    return spy.kwargs['entry_points']['console_scripts'][0]


def run(prog, args):
    import argparse
    desc = 'generate entrypoint script from setup.py'
    pr = argparse.ArgumentParser(prog=prog, description=desc)
    aa = pr.add_argument
    aa('-d', '--dir', help='output dir')
    aa('path', help='path to a setup.py or its containing dir')
    ns = pr.parse_args(args)
    try:
        spec = inspect_setuppy(ns.path)
        make_entrypoint_script(spec, ns.dir)
    except Exception as e:
        printerr(e)
