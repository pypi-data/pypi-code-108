# Copyright (c) AppDynamics, Inc., and its affiliates
# 2015
# All Rights Reserved

"""Entry-point interceptors for various web/application frameworks.

"""

from __future__ import unicode_literals

from .bottle import intercept_bottle
from .flask import intercept_flask
from .django import intercept_django_wsgi_handler, intercept_django_base_handler
from .cherrypy import intercept_cherrypy
from .pyramid import intercept_pyramid
from .tornado_web import intercept_tornado_web
from .fastapi import intercept_fastapi

__all__ = [
    'intercept_bottle',
    'intercept_flask',
    'intercept_django_wsgi_handler',
    'intercept_django_base_handler',
    'intercept_cherrypy',
    'intercept_pyramid',
    'intercept_tornado_web',
    'intercept_fastapi',
]
