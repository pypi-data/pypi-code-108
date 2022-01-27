# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# OARepo Micro API is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test record and files."""

from flask import url_for


def test_readiness_probes(wsgi):
    url = '/.well-known/heartbeat/liveliness'

    res = wsgi.get(url)
    assert res.status_code != 404


def test_liveliness_probes(wsgi):
    url = '/.well-known/heartbeat/readiness'

    res = wsgi.get(url)
    assert res.status_code != 404


def test_environ(wsgi):
    url = '/.well-known/heartbeat/environ'

    res = wsgi.get(url)
    assert res.status_code != 404


def test_generic_api(wsgi):
    url = url_for('invenio_records_rest.recid_list', _external=True)
    assert url.startswith('http://localhost/api/records')

    res = wsgi.get(url)
    assert res.status_code != 404

    assert 'Cache-Control' in res.headers
    assert res.headers['Cache-Control'] == 'no-cache'
