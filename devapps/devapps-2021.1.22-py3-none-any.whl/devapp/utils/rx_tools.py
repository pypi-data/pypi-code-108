#!/usr/bin/env python
import time
from copy import deepcopy
from functools import partial
from threading import current_thread
from typing import Callable, Iterable

import pycond
import rx
from devapp.app import app
from devapp.tools import funcname, in_gevent, jdiff, now
from rx import operators as op
from rx.scheduler import NewThreadScheduler, ThreadPoolScheduler
from theming.colorhilite import coljhighlight as pretty

# Custom ones also return an rx one, they wrap inner items:
is_operator = lambda o: getattr(o, '__module__', '').startswith('rx')

threaded = lambda t=10: op.observe_on(ThreadPoolScheduler(t))

pass_ = lambda *ev, **kw: 0


class Ops:
    """Allowing apps to set the default operator in chains"""

    default = op.map


def do_if(*actions: Callable, if_=None, which=None, default_op=None):
    """
    # Conditional Running of Operators
    Run the actions stream only when (alternatively):
    - the if_ condition is met
    - actions is a *dict* of actions, where the key is evaled by 'which' selector

    ## Params
    - actions: An operator chain, to be run when if_ evals to truthy
               OR
               A dict of operator chains, to be run when the which selector
               evals to dict key

    - if_, which: selector functions
    - default_ops: operator to wrap plain functions into (default rx's map
                   operator)
    Examples:

        We want to map to mult, then divide only on odd numbers:

        rx.from_([2,3,4]).pipe(
            do_some_stuff,
            do_if(mult, divide, if_=lambda i: i % 2)
        )

        We want to map to mult, then divide only on 3:

        rx.from_([2,3,4]).pipe(
               do_some_stuff,
               do_if(
                    {3: (mult, divide)},
                    which=lambda i: i
                 ))
    I.e. on the given stream 2,3,4 those produce the same results.
    The latter example demonstrates that we simply do nothing when the selector
    doese not match

    """

    def dict_actions(key, actions_by_key):
        if callable(actions_by_key):
            acts = actions_by_key(key)
        else:
            acts = actions_by_key.get(key)
        if not acts:
            return ()
        return acts if isinstance(acts, (list, tuple)) else (acts,)

    if if_:
        actions_by_key = {True: actions}
        # convenience for the user: we just have 2 cases, and group_by should not
        # see (and have to cache) anything not falsy:
        if not callable(if_):
            pc = pycond.pycond(if_)
            selector = lambda x: pc(state=x)
        else:
            selector = lambda x: bool(if_(x))
    else:
        if not isinstance(actions[0], dict) and not callable(actions[0]):
            raise Exception(
                (
                    'First argument must be a dict of operators,'
                    'based on the "which" selector result'
                )
            )
        actions_by_key = actions[0]
        selector = which

    return rx.pipe(
        op.group_by(selector),
        op.flat_map(
            lambda s, dop=default_op: chain(
                s, *dict_actions(s.key, actions_by_key), default_op=dop
            )
        ),
    )


def only(if_, pipe: Iterable[Callable]):
    return do_if(*pipe, if_=if_)


def chain(observe, *obs, default_op=None):
    return stream(observe=observe, pipe=list(obs), default_op=default_op)


def stream(observe, pipe, default_op=None):
    p = p1 = observe
    d = Ops.default if default_op is None else default_op
    ops = []

    for o in pipe:
        if is_operator(o):
            ops.append(o)
        else:
            ops.append(d(o))

        # p = p.pipe(o if is_operator(o) else d(o))
        # p = p.pipe(o if is_operator(o) else d(o))
    p = p.pipe(*ops)
    return p


def log(ev):
    app.info('Event', json=ev)
    return ev


def show(ev, add_dt=False):
    m = {'event': ev, 'thread': current_thread().name, 'ts': time.ctime()}
    if add_dt:
        ev['meta']['dt'] = now() - ev['meta']['t0']
    print(pretty(m))
    return ev


def pdb(ev):
    show(ev)
    print('''Breakpoint inserted''')
    breakpoint()
    return ev


def map_diff_log(f, wrap=op.map):
    """a map showing diff before and after
    Requires app set up
    """
    fn = funcname(f)

    def diff_log_map(r, f=f, fn=fn):
        try:
            ro = deepcopy(r)
            res = f(r)
        except Exception as ex:
            app.log.error(fn, r=r, diff=jdiff(ro, r))
            raise
        app.log.info(fn, rdiff=jdiff(ro, r))
        return res

    return wrap(diff_log_map)


def new_thread(c=[]):
    if c:
        return c[0]
    if in_gevent():
        # in compex nested blocking arrangements with high load we spotted
        # rx heap errors when using NewThreadSched. when monkey patched
        # => really use this one, no errs here:
        from rx.scheduler.eventloop import GEventScheduler

        s = GEventScheduler()
    else:
        s = NewThreadScheduler()
    c.append(s)
    return s


def concurrent(pipe):
    """Puts a function call, including a subsequent processing chain onto a
    new thread/greenlet
    The function is the first item of the pipe.
    There is no control over concurrency, this is isolated runs, flat-mapped
    back into the main stream

    # without the func = 0 element of pipe it would be:
    return stream(rx.just(r), [op.observe_on(new_thread()), *pipe])
    """

    def block(r, func, ops):
        s = rx.from_callable(lambda r=r: func(r), scheduler=new_thread())
        return s.pipe(*ops)

    return op.flat_map(partial(block, func=pipe[0], ops=pipe[1:]))


# ----------- StreamRunner (streams from serializable dicts) ------------------
def op_by_dict_cfg(opdict, stream_runner):
    """
    Configure operators with dicts, e.g.:
        def foo(i:int)
    configured like:
        {"foo": {"i": 10}}

    Higher order function operators like
        def foo(i, pipe)
    configured like:
        {"foo": {"pipe": ["bar"], "i": 10}}
    and bar is resolved into the function

    -> The resolution into funcs requires the 'pipe' keyword.
    """
    cls = stream_runner
    op_name, v = func_name_args_from_dict(opdict)

    f = find_operator_by_name(op_name, cls)
    if 'pipe' in v:
        # we don't want to ditch the serializable config,
        # want to keep as sent from the config machinery
        v = dict(v)
        # recursion here:
        v['pipe'] = pipe_from_cfg(stream_runner, v['pipe'])
        return f(**v)
    else:
        return partial(f, **v)


def find_operator_by_name(oprtr, stream_runner):
    cls = stream_runner
    for f in cls.functions:
        if isinstance(oprtr, list):
            return op_by_dict_cfg({'concurrent': {'pipe': oprtr}}, cls)
        if isinstance(oprtr, dict):
            return op_by_dict_cfg(oprtr, cls)

        # We do allow nested functionality classes with a namespace:
        parts = oprtr.split('.')
        op = getattr(f, parts.pop(0), None)
        while parts and op:
            part = parts.pop(0)
            op = getattr(op, part, None)
        if op:
            return op
    raise Exception('operator not found', {'operator': oprtr, 'checked': cls.functions})


def pipe_from_cfg(stream_runner, cfg_pipe):
    """Turns a list of operator names into their functions
    looking them up int the stream_runner._functions
    """
    cfg_pipe = [cfg_pipe] if not isinstance(cfg_pipe, list) else cfg_pipe
    return [find_operator_by_name(op, stream_runner) for op in cfg_pipe]


def func_name_args_from_dict(single_item_dict):
    # {'some_func_in_namespace': {'args': 'foo'}}
    for k, v in single_item_dict.items():
        return k, v


class StreamRunner:
    _subscriptions = {}
    _configs = {}

    @classmethod
    def run_cfg(cls, name, cfg):
        """We store the subscriptions in order to get rid of them when streams
        are redefined"""
        if name in cls._subscriptions:
            app.warning('Stopping', name=name)
            cls._subscriptions[name]['subs'].dispose()
        cls._configs[name] = cfg
        return cls.run(name)

    @classmethod
    def run(cls, name, observe=None, pipe=None, **kw):
        cfg = cls._configs.get(name, {})
        if cfg:
            obs = cfg['observe']
            if isinstance(obs, str):
                observe = getattr(cls, cfg['observe'])
            else:
                # func -> args, e.g. {'from_route': {'path': '/inform', 'type': 'blocking', 'verbs': ['post']},
                func_name, args = func_name_args_from_dict(obs)
                observe = args['subject'] = rx.subjects.Subject()
                # Reference the stream in the Streams class:
                setattr(cls, name, observe)
                # use the same function finding machinery as for the pipe ops:
                op_by_dict_cfg({func_name: args}, cls)()

            pipe = pipe_from_cfg(cls, cfg['pipe'])

        app.warning('Starting stream', name=name, json=cfg)

        stream_def = lambda observe=observe, pipe=pipe: stream(observe, pipe)
        stream_ = stream_def()
        d = stream_.subscribe(pass_)
        cls._subscriptions[name] = {
            'stream': stream_,
            'def': stream_def,
            'subs': d,
            'observe': observe,
            'pipe': pipe,
        }
