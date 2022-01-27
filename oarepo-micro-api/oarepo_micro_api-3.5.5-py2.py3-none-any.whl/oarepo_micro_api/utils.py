# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# OARepo Micro API is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""OArepo Micro API utilities."""
from urllib.parse import urlparse

from flask import request
from invenio_indexer.utils import default_record_to_index

API_ROUTES = [
    '/oauth'
]


def is_api_request():
    """Determines whether a request is to be served by micro API."""
    # TODO: update OARepo Whitenoise to use this
    path = urlparse(request.url).path
    if not any([path.startswith(r) for r in API_ROUTES]):
        accept = request.headers.get('Accept', '')
        if 'html' in accept and 'download' not in request.args:
            return False

    return True


def record_to_index_from_index_name(record):
    """Get index/doc_type given a record.

    It tries to extract from `record['index_name']` the index and doc_type.
    If it fails, return the default values using default Invenio record_to_index.
    :param record: The record object.
    :returns: Tuple (index, doc_type).
    """
    index = getattr(record, 'index_name', None)
    if index:
        return index, '_doc'

    return default_record_to_index(record)
