# Copyright (c) AppDynamics, Inc., and its affiliates
# 2015
# All Rights Reserved

"""Interceptor for memcached.

"""

from __future__ import unicode_literals

from appdynamics.agent.interceptor.cache import CacheInterceptor
from appdynamics.lib import parse_args


class MemcacheClientInterceptor(CacheInterceptor):
    def __init__(self, agent, cls):
        super(MemcacheClientInterceptor, self).__init__(agent, cls, 'MEMCACHED')

    def run_command(self, command_func, client, *args, **kwargs):
        exit_call = None
        with self.log_exceptions():
            bt = self.bt
            if bt:
                backend = self.get_backend(['%s:%s' % server.address for server in client.servers])
                if backend:
                    operation = '%s(%s)' % (command_func.__name__, parse_args(args, kwargs))
                    exit_call = self.start_exit_call(bt, backend, operation=operation)
        result = command_func(client, appd_exit_call=exit_call, *args, **kwargs)
        self.end_exit_call(exit_call)
        return result


def intercept_memcache(agent, mod):
    interceptor = MemcacheClientInterceptor(agent, mod.Client)
    interceptor.attach([
        'set',
        'set_multi',
        'add',
        'replace',
        'append',
        'prepend',
        'cas',
        'get',
        'get_multi',
        'gets',
        'delete',
        'delete_multi',
        'incr',
        'decr',
        'flush_all',
    ], patched_method_name='run_command')
