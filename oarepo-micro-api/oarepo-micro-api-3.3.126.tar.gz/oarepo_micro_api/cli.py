# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# OARepo Micro API is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Default configuration for OARepo Micro API.

You overwrite and set instance-specific configuration by either:

- Configuration file: ``<virtualenv prefix>/var/instance/invenio.cfg``
- Environment variables: ``APP_<variable name>``
"""

from __future__ import absolute_import, print_function

from functools import wraps

from invenio_app.factory import create_api
from invenio_base import create_cli


def with_api(f):
    """Decorator to wrap function with current api application context."""
    @wraps(f)
    def inner(*args, **kwargs):
        with create_api().app_context():
            return f(*args, **kwargs)

    return inner


#: Invenio CLI application.
cli = create_cli(create_app=create_api)
