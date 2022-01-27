# Copyright (c) AppDynamics, Inc., and its affiliates
# 2015
# All Rights Reserved

from __future__ import unicode_literals

from appdynamics.agent.interceptor.frameworks.wsgi import WSGIMiddleware
application = WSGIMiddleware(set_interceptor=False)
