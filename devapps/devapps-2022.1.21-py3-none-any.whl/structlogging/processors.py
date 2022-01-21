import time
from threading import current_thread

import structlog

from .common import transient_data_key


def positional_args_into_msg(logger, level, ev_dict):
    '.. but only if wanted...'
    pa = ev_dict.get('positional_args', None)
    if not pa:
        return ev_dict
    ev = ev_dict.get('event')
    if ev == '%s':
        ev_dict['event'] = ' '.join(str(s) for s in pa)
        del ev_dict['positional_args']
    else:
        try:
            if len(pa) == 1 and isinstance(pa[0], dict) and pa[0]:
                pa = pa[0]
            ev_dict['event'] = ev % pa
            del ev_dict['positional_args']
        except:
            pass
    return ev_dict


def censor_values(L, l, ev_dict, cfg):

    keys = cfg.get('keys')
    if not keys:
        return ev_dict

    for k in ev_dict:
        if k in keys:
            show_chars = cfg.get('hint_chars')
            v = cfg.get('repl_with', '*CENSORED*')
            if show_chars:
                v += ' hint: ' + str(unicode(ev_dict[k])[:show_chars]) + '...'
            ev_dict[k] = v
    return ev_dict


def selected_processors(L, l, ev_dict, cfg):
    """The processor function run as partial possibly a few times in the
    main proc chain. See config.py.
    """
    selector = cfg['selector']
    position = cfg['position']  # e.g. 'after_TimeStamper', just an index
    if selector == 'name':
        procs = L.ax_structlog_selected_processors.get(position)
        if procs:
            # maybe the proc wants to know its state.
            # we cannot change the sig, we have sl internal procs as well:
            ev_dict['_processor_state'] = cfg

            for p in procs:
                ev_dict = p(L, l, ev_dict)

            ev_dict.pop('_processor_state', 0)
    return ev_dict


def add_transient_data_holder(L, l, ev_dict):
    ev_dict[transient_data_key] = {}
    return ev_dict


def remove_transient_data(L, l, ev_dict):
    ev_dict.pop(transient_data_key, 0)
    return ev_dict


now = lambda: int(time.time() * 1000)
t0 = now()


def add_dt(_, __, ev):
    ev['timestamp'] = now() - t0
    return ev


def TimeStamper(**kw):
    timefmt = kw.get('fmt', 'ISO')
    if timefmt == 'dt':
        return add_dt
    utc = kw.get('utc', True)
    return structlog.processors.TimeStamper(timefmt, utc=utc)


def add_thread_name(L, l, ev_dict):
    t = current_thread()
    try:
        tn = int(t.getName().rsplit('-', 1)[1])
    except:
        if t.getName() == 'MainThread':
            tn = 0
        else:
            tn = t.ident  # int guaranteed
    tn = tn % 100000
    ev_dict['thread'] = tn
    # ev_dict['thread'] = 0
    return ev_dict
