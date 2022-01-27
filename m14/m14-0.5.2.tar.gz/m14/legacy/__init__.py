#!/usr/bin/env python3
# coding: utf-8


from __future__ import unicode_literals

import base64
import codecs
import functools
import itertools
import os
import json


# replaced by volkanic.utils.indented_json_print
def indented_json_print_legacy(obj, **kwargs):
    # https://stackoverflow.com/a/12888081/2925169
    decoder = codecs.getdecoder('unicode_escape')
    print_kwargs = {}
    for k in ['sep', 'end', 'file', 'flush']:
        if k in kwargs:
            print_kwargs[k] = kwargs.pop(k)
    kwargs.setdefault('indent', 4)
    s = json.dumps(obj, **kwargs)
    print(decoder(s)[0], **print_kwargs)


def search_with(regexes, text):
    for regex in regexes:
        mat = regex.search(text)
        if mat:
            return mat.groupdict()
    return dict()


def smart_split(text, sep):
    if isinstance(sep, str):
        parts = text.split(sep, 1)
        if len(parts) > 1:
            parts.insert(1, sep)
        return strip_all(*parts)
    # regex split
    return [p.strip() for p in sep.split(text, 1)]


def strip_all(*parts):
    return [p.strip() for p in parts]


def castable(func):
    """
    NOT supported: negative index (castfunc=-1 to get last item)
    >>> @castable
    ... def myfunc(*args):
    ...     for i in range(*args):
    ...         yield i
    ...
    >>> myfunc(12, castfunc=tuple)
    (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)
    >>> myfunc(0, 12, 2, castfunc=2)
    (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)

    Purely syntax sugar,
    to make interactive use of some functions easier.
    Cast a generator function to list, set, or select n-th item, etc.

        myfunc(..., castfunc=list)   <=>  list(myfunc(...))
        myfunc(..., castfunc=1)      <=>  list(myfunc(...))[1]
    """

    @functools.wraps(func)
    def _decorated_func(*args, **kwargs):
        castfunc = None
        if 'castfunc' in kwargs:
            castfunc = kwargs['castfunc']
            del kwargs['castfunc']

        retval = func(*args, **kwargs)
        if castfunc:
            if callable(castfunc):
                return castfunc(retval)
            # shortcut to pick up nth record
            if isinstance(castfunc, int):
                return next(itertools.islice(retval, castfunc, None))
            return TypeError('castfunc must be a callable or integer')
        return retval

    return _decorated_func


# https://docs.python.org/3/library/enum.html#using-automatic-values
class AttrEchoer(object):
    """
    Resembles an enum type
    Reduces typos by using syntax based completion of dev tools

    Example:

        @instanciate_with_foolproof
        class Event(AttrEchoer):
            _prefix = 'event'
            bad_params = ''  # assign whatever
            unauthorized_access = ''
            undefined_fault = ''
            ...

        assert Event.unauthoried  == 'event.bad_params'
    """
    _prefix = '_root.'

    def __init__(self):
        pass

    def __getattribute__(self, key):
        kls = type(self)
        if key in kls.__dict__ and key != '_prefix':
            if not kls._prefix:
                return key
            return '{}{}'.format(kls._prefix, key)
        return object.__getattribute__(self, key)


def locate_standard_conf(package):
    # a string is also acceptable
    name = getattr(package, '__name__', package)
    workdirs = [os.environ.get('{}_WORKDIR'.format(name.upper()))]

    # look for ~/.<package> and /data/<package>
    # ONLY IF <package>_WORKDIR is not set
    if workdirs[0] is None:
        workdirs = [
            os.path.expanduser('~/.{}'.format(name)),
            '/data/{}/'.format(name),
        ]
        workdirs = [d for d in workdirs if os.path.isdir(d)]

    for d in workdirs:
        p = os.path.join(d, 'configs/{}.yml'.format(name))
        if p and os.path.isfile(p):
            return p
    raise ValueError('config file not found')


def gen_random_string(length):
    n = 1 + int(length * 0.625)
    return base64.b32encode(os.urandom(n)).decode()[:length]


def setup_basic_logging(level='INFO'):
    import logging
    params = {
        'level': level,
        'format': '%(asctime)s %(levelname)s %(name)s %(message)s',
        'datefmt': '%Y%m%d~%H:%M:%S',
    }
    logging.basicConfig(**params)


def strip_lines(lines, lstrip=True, rtrip=True):
    stripfuncs = []
    if rtrip:
        stripfuncs.append(str.lstrip)
    if lstrip:
        stripfuncs.append(str.rsplit)
    if not stripfuncs:
        stripfuncs = [lambda s: s.rstrip('\n')]
    elif len(stripfuncs) == 2:
        stripfuncs = [str.strip]
    for line in lines:
        stripfuncs[0](line)
