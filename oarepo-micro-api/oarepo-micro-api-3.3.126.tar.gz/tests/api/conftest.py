# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# OARepo Micro API is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Pytest fixtures and plugins for the API application."""

from __future__ import absolute_import, print_function

import pytest
from invenio_app.factory import create_api
from webtest import TestApp

from oarepo_micro_api.wsgi import application


@pytest.fixture(scope='module')
def app_config(app_config):
    """Get app config."""
    app_config['SERVER_NAME'] = 'localhost'
    app_config['PREFERRED_URL_SCHEME'] = 'http'
    app_config['FLASK_ENV'] = 'development'
    return app_config


@pytest.fixture(scope='module')
def wsgi(app):
    """Create test app."""
    app = TestApp(application)
    return app


@pytest.fixture(scope='module')
def create_app():
    """Create test app."""
    return create_api
