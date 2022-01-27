# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# OARepo Micro API is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""OArepo Micro API alias prefix replacer."""
from flask import current_app
from invenio_base.signals import app_loaded
from invenio_search import current_search
from wrapt import ObjectProxy


class IndicesProxy(ObjectProxy):
    """Proxy that helps create mapping with replaced {PREFIX} placeholder."""

    def create(self, index=None, body=None, **kwargs):
        """Replace {PREFIX} placeholder in alias section in mapping."""
        if 'aliases' in body:
            prefix = current_app.config.get('SEARCH_INDEX_PREFIX', '')
            body['aliases'] = {
                k.replace('{PREFIX}', prefix): v for k, v in body['aliases'].items()
            }
        return self.__wrapped__.create(index=index, body=body, **kwargs)


class ElasticsearchProxy(ObjectProxy):
    """Proxy that helps create mapping with replaced {PREFIX} placeholder."""

    def __init__(self, wrapped):
        """Init method."""
        super().__init__(wrapped)
        self.__wrapped_indices__ = None

    @property
    def indices(self):
        """Property that return indices."""
        if not self.__wrapped_indices__:
            self.__wrapped_indices__ = IndicesProxy(self.__wrapped__.indices)
        return self.__wrapped_indices__


@app_loaded.connect
def patch_invenio(sender, *args, app=None, **kwargs):
    """Insert custom search client into invenio-search."""
    with app.app_context():
        client = current_search.client
        if not isinstance(client, ElasticsearchProxy):
            current_search._client = ElasticsearchProxy(client)
