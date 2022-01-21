"""
SuperLight Structured Logging
-----------------------------

Stdlib Free Fast Logging, Using Structlog Only

Usage:
    axlog.setup_logging()  once per app
    axlog.get_logger('axwifi').info('foo', bar=baz)

    The app may use flags: --log_level=20
"""


import os
import sys
import traceback

import structlog
from devapp.tools import FLG, define_flags
from pygments.styles import get_all_styles
from structlog import BoundLoggerBase, PrintLogger, wrap_logger
from structlog.exceptions import DropEvent

# -- Setup for a stdlib logging free, getattr free use:
from structlog.processors import JSONRenderer
from structlogging import processors as ax_log_processors
from structlogging import renderers

pygm_styles = list(get_all_styles())
pygm_styles.extend(['light', 'dark'])


class flags:
    autoshort = ''

    class log_level:
        n = 'Log level (10: debug, 20: info, ...). You may also say log_level=error'
        d = '20'

    class log_time_fmt:
        n = 'Log time format. Shortcuts: "ISO", "dt"'
        d = '%m-%d %H:%M:%S'

    class log_fmt:
        n = 'Force a log format. 0: off, 1: auto, 2: plain, 3: plain_no_colors, 4: json. '
        n += 'Note: This value can be set away from auto via export log_fmt as well.'
        d = 'auto'

    class log_add_thread_name:
        n = 'Add name of thread'
        d = False

    class log_dev_fmt_coljson:
        n = 'List of keys to log as json.'
        d = 'json,payload'
        t = list

    class log_dev_coljson_style:
        n = 'Pygments style for colorized json. To use the 16 base colors and leave it '
        n += 'to the terminal palette how to render choose light or dark'
        t = sorted(pygm_styles)
        d = 'dark'


define_flags(flags)

# fmt:off
log_levels = {
    'fatal'     : 70,
    'critical'  : 60,
    'error'     : 50,
    'exception' : 50,
    'err'       : 50,
    'warn'      : 40,
    'warning'   : 40,
    'info'      : 20,
    'debug'     : 10,
}
# fmt:on
def storing_testlogger(dub_to=None, store=None):
    """for tests - stores into array, optionally dubs to existing logger"""
    store = [] if store is None else store

    def add_log_to_store(logger, _meth_, ev, store=store, log=dub_to):
        d = dict(ev)
        d['_meth_'] = _meth_
        store.append(d)
        if log:
            getattr(log, _meth_)(ev.pop('event'), **ev)
        raise structlog.DropEvent

    gl = structlog.get_logger
    l, m = ('dub', gl) if dub_to is None else (dub_to, structlog.wrap_logger)
    r = m(l, processors=[add_log_to_store])
    r.reset = r.clear = lambda s=store: s.clear()
    r.store = store
    return r


def log_flags():
    flog = get_logger('flag')
    m = FLG.flag_values_dict()
    for k in sorted(m.keys()):
        flog.debug('', **{k: m[k]})


class AXLogger(BoundLoggerBase):
    """A Bound Logger is a concrete one, e.g. stdlib logger"""

    def log(self, event, kw, _meth_od):
        # the frame will allow *pretty* powerful parametrization options
        # todo: allow that for the user
        # the lambda below is also a frame:
        kw['_frame_'] = sys._getframe().f_back.f_back
        try:
            args, kw = self._process_event(_meth_od, event, kw)
        except DropEvent:
            return
        return self._logger.msg(*args, **kw)


class AppLogLevel:
    """Intermediate resets of devapp app loglevel

    with AppLogLevel(30):
        do_lots_of_stuff()

    """

    def __init__(self, level):
        from devapp.app import app

        self.app = app
        self.level = level
        self.was_level = app.log._logger.level

    def __enter__(self):
        self.app.log._logger.level = self.level

    def __exit__(self, *a, **kw):
        self.app.log._logger.level = self.was_level


# setting all level methods, like log.warn into the logger:
for l, nr in log_levels.items():
    setattr(AXLogger, l, lambda self, ev, _meth_=l, **kw: self.log(ev, kw, _meth_))


def get_logger(name, level=None, **ctx):
    """supports name and level conventions - matches the processor chain"""
    if not structlog.is_configured():
        setup_logging()

    FLG.log_level = int(log_levels.get(FLG.log_level, FLG.log_level))
    level = level or FLG.log_level
    log = wrap_logger(PrintLogger(file=sys.stderr), wrapper_class=AXLogger)
    log._logger.name = name
    log._logger.level = level
    return log.bind(**ctx)


def filter_by_level(logger, _meth_, ev):
    if log_levels[_meth_] < logger.level:
        raise DropEvent
    return ev


censored = ['password', 'access_token']


def censor_passwords(_, __, ev, _censored=censored):
    """
    Supports to deliver the censor structure in ev or at setup:
    log.info('MyMsg', data={'foo': {'pw': ..}}, censor=('token', ('data', 'pw')))
    """
    censored = ev.pop('censor', _censored)
    for pkw in censored:
        # nested censored value?
        if isinstance(pkw, (list, tuple)):
            pw = ev
            for part in pkw:
                try:
                    pw = pw.get(part)
                except Exception as ex:
                    pw = None
                if not pw:
                    break
        else:
            pw = ev.get(pkw)
        if pw:
            # TODO: does only work with ONE censored field
            k = min(len(pw) - 1, 3)
            v = pw[:k] + '*' * min((len(pw) - k), 10)
            if isinstance(pkw, (list, tuple)):
                cur = ev
                for part in pkw[:-1]:
                    cur = ev[part]
                cur[pkw[-1]] = v

            else:
                ev[pkw] = v
    return ev


def frame(f):
    m = {}
    m['pos'] = [f.lineno, f.filename]
    m['line'] = f.line
    # if not f.name == '<lambda>':
    m['name'] = f.name
    return m


def add_exception_stack(_, __, ev):
    """This filters out huge rx stacks, which are not useful at all normally.
    """
    if 'exc' in ev:
        E = ev['exc']
        if isinstance(E, Exception):
            r = traceback.extract_tb(sys.exc_info()[2])
            ev['stack'] = [
                'Traceback',
                [frame(l) for l in r if not '/rx/' in l.filename],
                [E.__class__.__name__, E.args],
            ]
    return ev


def add_stack_info(_, __, ev):
    # from structlog._frames import _find_first_app_frame_and_name as ffafan

    si = ev.pop('stack_info', 0)
    if si and not 'stack' in ev:
        # TODO make the non raise stack_info tbs also better, like the exc ones
        ev['stack'] = traceback.format_stack(ev['_frame_'][0])
    return ev


def add_logger_name_and_frame_infos(logger, _, ev):
    # TODO parametrizeable frame info extraction.
    ev.pop('_frame_')
    ev['logger'] = '%s' % (logger.name)
    return ev


std_processors = [
    filter_by_level,
    # structlog.stdlib.add_logger_name,
    structlog.stdlib.add_log_level,
    censor_passwords,
    add_exception_stack,
    add_stack_info,  # allows to say stack_info=1 w/o exceptions
    add_logger_name_and_frame_infos,
]


def fmt_to_int(fmt):
    if str(fmt) in ('auto', '1'):
        fmt = os.environ.get('log_fmt', fmt)
    if fmt.isdigit():
        return int(fmt)
    m = {'off': 0, 'auto': 1, 'plain': 2, 'plain_no_colors': 3, 'json': 4}
    return m.get(fmt, 1)


def log_dropper(*a):
    raise structlog.DropEvent


# class F:
#     log_fmt = 'plain'
#     log_level = 10
#     log_time_fmt = '%m-%d %H:%M:%S'
#     log_add_thread_name = True
#     log_dev_fmt_coljson = []
#     log_dev_coljson_style = ('paraiso-dark',)
import ujson, json, time


def to_str(obj):
    try:
        return obj.decode('utf-8')
    except:
        return str(obj)


def safe_dumps(obj, to_str=to_str, default=None):
    try:
        # fails when objects are in, e.g. connection sockets:
        # can dump tuple keys
        return ujson.dumps(obj, ensure_ascii=False, reject_bytes=False)
    except:
        try:
            return json.dumps(obj, default=default)
        except Exception as ex:
            return json.dumps(
                {
                    'event': 'cannot log-serialize: %s' % str(obj),
                    'level': 'error',
                    'logger': 'sl',
                    'timestamp': time.time(),
                }
            )


def setup_logging(
    name=None,
    level=None,
    processors=None,
    censor=(),
    # these come from the app. should not overwrite flags except if not given
    log_dev_fmt_coljson=None,
    log_time_fmt=None,
    get_renderer=False,
):
    """
    pygmentize: Those keys, if present, will be rendered as colored json
    This requires app.run done.
    If not: Say FLG(sys.argv)
    """
    # try:
    #     log_fmt = FLG.log_fmt
    # except:
    #     breakpoint()  # FIXME BREAKPOINT
    #     FLG = F

    # are we a real app, or just a test program:
    # fmt:off
    log_fmt               = FLG.log_fmt
    log_time_fmt          = FLG.log_time_fmt
    log_add_thread_name   = FLG.log_add_thread_name
    log_dev_coljson_style = FLG.log_dev_coljson_style
    log_dev_fmt_coljson_flg  = FLG.log_dev_fmt_coljson
    # fmt:on

    if censor:
        censor = [censor] if isinstance(censor, str) else censor
        [censored.append(c) for c in censor if not c in censored]
    fmt_vals, val_formatters = {}, {}
    # log.info('Response', json=... ) auto formats:
    lc = log_dev_fmt_coljson_flg
    if log_dev_fmt_coljson:
        lc.extend(log_dev_fmt_coljson)
    for k in lc:
        fmt_vals[k] = 'f_coljson'
    fmt_vals['stack'] = 'f_coljson'  # stack tracebacks always

    val_formatters['f_coljson'] = {
        'formatter': 'coljson',
        'style': log_dev_coljson_style,
    }

    fmt = fmt_to_int(log_fmt)
    tty = sys.stdout.isatty()
    if fmt == 4 or (fmt == 1 and not tty):
        rend = JSONRenderer(serializer=safe_dumps)
    else:
        # console renderer. colors?
        colors = fmt != 3
        rend = renderers.ThemeableConsoleRenderer(
            colors=colors, fmt_vals=fmt_vals, val_formatters=val_formatters
        )

    if get_renderer:
        return rend

    p = processors or std_processors
    if log_add_thread_name:
        p.insert(1, ax_log_processors.add_thread_name)
    if log_time_fmt:
        p.insert(1, ax_log_processors.TimeStamper(fmt=log_time_fmt))
    p.append(rend)
    if fmt == 0:
        p.insert(0, log_dropper)

    structlog.configure(
        processors=p,
        context_class=dict,
        wrapper_class=AXLogger,
        cache_logger_on_first_use=True,
    )
    # all in one:
    if name is not None:
        return get_logger(name, level=level)


# .
