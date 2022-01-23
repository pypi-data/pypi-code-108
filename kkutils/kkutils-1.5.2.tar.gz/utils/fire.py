#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Author: zhangkai
Email: kai.zhang1@nio.com
Last modified: 2019-09-04 13:32:01
'''
import asyncio
import inspect
import sys

from .base_utils import pprint
from .config_utils import Config


def Fire(component=None, stdout=True):
    kwargs = Config()
    params = []
    for x in sys.argv[1:]:
        if x.startswith('--'):
            break
        params.append(x)

    if component is None:
        modules = inspect.stack()[1].frame.f_globals
        component = modules[params[0]]
        params = params[1:]

    if inspect.isclass(component):
        sig = inspect.signature(component)
        cls_kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}
        for k in sig.parameters:
            kwargs.pop(k, None)
        module = component(**cls_kwargs)
        func = getattr(module, params[0])
        args = params[1:]
    elif inspect.isfunction(component):
        func = component
        args = params
    else:
        func = getattr(component, params[0])
        args = params[1:]

    ret = func(*args, **kwargs)
    if inspect.isawaitable(ret):
        loop = asyncio.get_event_loop()
        ret = loop.run_until_complete(ret)

    if stdout and ret is not None:
        pprint(ret)
