# Copyright (c) AppDynamics, Inc., and its affiliates
# 2016
# All Rights Reserved

from __future__ import unicode_literals
import appdynamics.agent

from appdynamics.agent.interceptor.frameworks.wsgi import WSGIMiddleware


def composite_factory(loader, global_conf, target, **local_conf):
    target = loader.get_app(target, global_conf=global_conf)

    try:
        if not appdynamics.agent.configure(local_conf):
            return target

        return WSGIMiddleware(application=target)
    except:
        return target
