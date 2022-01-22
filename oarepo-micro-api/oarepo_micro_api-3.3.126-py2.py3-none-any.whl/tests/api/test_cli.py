# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# OARepo Micro API is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test utils module."""
from flask import current_app

from oarepo_micro_api.cli import with_api


def test_with_api():

    @with_api
    def api_func():
        assert current_app is not None
        assert 'invenio_files_rest.object_api' in current_app.url_map._rules_by_endpoint

    api_func()
