"""
Tools which are importable before app runs
"""


import os
import platform
import sys
from getpass import getpass

from devapp.tools import write_config_cls_key

try:
    from devapp.app import app

    app.die
except:
    app = None

env = os.environ
ls = os.listdir


def j(*f):
    return os.path.join(*f)


def die(msg, **kw):
    app and app.die(msg, **kw)
    print(msg, str(kw))
    sys.exit(1)


def confirm(msg, default=True):
    y = 'Y' if default else 'y'
    n = 'n' if default else 'N'
    print('Confirm: %s [%s/%s] ' % (msg, y, n))
    try:
        v = input('> ')
    except KeyboardInterrupt as ex:
        print('Interrupted - bye.')
        sys.exit(1)
    except EOFError as ex:
        print('Interrupted - bye.')
        sys.exit(1)
    if not v:
        v = str(default)
    if v.lower() in ('y', 'yes', '1', 'true'):
        return True
    print('Unconfirmed')
    return False


def env_get_interactive_write(k, validate=None, example=None):
    v = env.get(k)
    if v is not None:
        return v
    msg = 'Required environ missing.'
    if example:
        msg += '\nExample value: %s\n' % example
    ask = getpass if 'assw' in k else input
    try:
        v = ask(msg + '\nEnter value for %s: ' % k)
    except KeyboardInterrupt as ex:
        v = 'q'
    except EOFError as ex:
        v = 'q'
    if v == 'q':
        print('Interrupted - bye.')
        sys.exit(1)
    if validate is not None:
        rv = validate(k, v)
        if rv == True:
            return v
        elif rv == 'write':
            write_config_cls_key(k, v)
            return v
        elif rv:
            print(rv)
        return env_get_interactive_write(k, validate, example)
    return v


def source2(fn=None, src=None, repl_ctx=None):
    m = {}
    if fn:
        if not os.path.exists(fn):
            raise Exception(fn, 'not found')
        with open(fn) as fd:
            s = fd.read()
    else:
        s = src
    if repl_ctx and '%(' in s:
        s = s % repl_ctx
    for l in s.splitlines():
        if l.strip() and '=' in l and not l.startswith('#'):
            k, v = l.split('=', 1)
            if v:
                if v[0] in ('"', "'"):
                    v = v[1:-1]
                m[k] = v
    return m


def get_arch():
    arch = platform.architecture()[0]
    if '64' in arch:
        arch = 'x86_64'
    elif '32' in arch:
        arch = 'x86_32'
    else:
        arch = 'unknown'
    return '%s-%s' % (platform.system(), arch)
