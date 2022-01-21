import re
from collections import OrderedDict as OD
from functools import partial

import structlog
from structlogging import processors as ax_procs

from .common import proc_modules, selected_by_name_processors

try:
    from ax.utils.dynamic_objects import make_staticmethods
    from ax.utils.dynamic_objects import get_mod
except:
    get_mod = None
    make_staticmethods = None


def not_found_processor(logger, level, ev_dict, **kw):
    ev_dict['NOT_FOUND_PROCESSOR'] = kw.pop('proc_str')
    return ev_dict


def build_chain_from_list(processors):
    """get a list of processor names and return a list of processor callables,
    parametrized, if the processor "name" is a dict"""

    # to build the unique name for selective processors:
    # e.g. 'after_add_logger_name_2'
    ctx = {'last': 'beginning', 'nr': 0}

    def processor(p, ctx=ctx):
        if not isinstance(p, (basestring, dict)):
            # already done:
            return p

        cfg = None
        if isinstance(p, dict):
            sub_procs = p.get('selected_by_name')
            # A list of processors run only for some loggers, when the name
            # matches.
            # We build the subchain, indexed by match at global dict
            # 'selected_by_name_processors', so that at logger instantiation
            # we attach the procs to the logger
            # so that the 'selected_processors' processor has an easy time
            # calling them on log events:
            if sub_procs:
                cfg = {
                    'position': 'after_%(last)s_%(nr)s' % ctx,
                    'selector': 'name',
                }
                m = selected_by_name_processors[cfg['position']] = OD()
                for sp in sub_procs:
                    match = sp['match']
                    m[match] = build_chain_from_list(sp['processors'])

                return partial(ax_procs.selected_processors, cfg=cfg)

            # normal processor with some config:
            cfg = p
            p = p.pop('processor')  # crash here, required.

        # todo: custom ones:
        pp = None
        for m in proc_modules:
            pp = getattr(m, p, None)
            if pp:
                break
        if not pp:
            return partial(not_found_processor, proc_str=p)

        # structlog convention: Upper case are classes which can be configured
        if p[0] == p[0].upper():
            return pp(**cfg) if cfg else pp()

        ctx['nr'] += 1
        ctx['last'] = p
        return partial(pp, cfg=cfg) if cfg else pp

    return [processor(p) for p in processors]


class LoggerFactory(structlog.stdlib.LoggerFactory):
    """Wrapper, to attach selective processors"""

    def __init__(self, custom_config, *a, **kw):
        self.custom_config = custom_config
        structlog.stdlib.LoggerFactory.__init__(self, *a, **kw)

    def __call__(self, *args):
        logger = l = structlog.stdlib.LoggerFactory.__call__(self, *args)
        assp = l.ax_structlog_selected_processors = {}
        for pos, chains_by_match in selected_by_name_processors.items():
            assp[pos] = []
            for match in chains_by_match:
                if re.match(match, logger.name):
                    assp[pos].extend(chains_by_match[match])
        return logger


def dict_config(config):
    assert get_mod, 'ax.utils required for structlogging.config'
    d = config.get('structlog')

    # get the list of custom processor modules, where we look for processors:
    while proc_modules:
        proc_modules.pop()
    [proc_modules.append(get_mod(m)) for m in d.get('processor_modules', ())]
    proc_modules.extend([ax_procs, structlog.stdlib, structlog.processors])

    procs = d.get('processors')
    if not procs:
        return

    procs = build_chain_from_list(procs)
    procs.insert(0, structlog.stdlib.filter_by_level)
    procs.append(structlog.stdlib.ProcessorFormatter.wrap_for_formatter)

    structlog.configure(
        processors=procs,
        context_class=dict,
        logger_factory=LoggerFactory(custom_config=d),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def preprocess_dict_config(C):
    """Mutates the Config (C) via batch ops on the dict
    to simplify (re-)config measures
    """
    assert make_staticmethods, 'ax.utils required for preprocess_dict_config'

    def pre_process_dict(C, feat):
        """C the config dict which are mutating"""
        pp = C.get('pre_process_config', {})
        cfg = pp.get(feat)
        if not cfg:
            return
        func = getattr(Features, feat, None)
        if func:
            func(C, cfg)

    class Features:
        def add_handler(C, cfg):
            """add a handler to all matching logs"""

            def add_handler(loggers, match, h):
                [
                    loggers[l]['handlers'].append(h)
                    for l in loggers
                    if re.match(match, l) and not h in loggers[l]['handlers']
                ]

            [add_handler(C['loggers'], match, hdl) for match, hdl in cfg.items()]

        def set_log_dir(C, dir_):
            """prefix all filenames with that dir if """
            for h in C['handlers'].values():
                fn = h.get('filename')
                if fn and not fn.startswith('/'):
                    h['filename'] = '%s/%s' % (dir_, fn)

    make_staticmethods(Features)

    [pre_process_dict(C, f) for f in ['add_handler', 'set_log_dir']]
