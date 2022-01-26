# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CESNET.
#
# NR datasets repository is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Flask extension for nr datasets."""

from __future__ import absolute_import, print_function

import logging

from invenio_indexer.signals import before_record_index
from nr_datasets_metadata.record import date_ranges_to_index
from oarepo_communities.signals import on_request_approval, on_request_changes, on_approve, on_publish, on_unpublish, \
    on_revert_approval, on_delete_draft

from . import config
from .handlers import handle_request_approval, handle_request_changes, handle_approve, handle_revert_approval, \
    handle_publish, handle_unpublish, handle_delete_draft

log = logging.getLogger('nr-datasets')


class NRDatasets(object):
    """Datasets model repository extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        self.connect_signals()

    def init_config(self, app):
        """Initialize configuration.

        Override configuration variables with the values in this package.
        """
        app.config.setdefault('RECORDS_DRAFT_ENDPOINTS', {}).update(config.RECORDS_DRAFT_ENDPOINTS)
        app.config.setdefault('RECORDS_REST_ENDPOINTS', {}).update(config.RECORDS_REST_ENDPOINTS)
        app.config.setdefault('RECORDS_REST_FACETS', {}).update(config.RECORDS_REST_FACETS)
        app.config.setdefault('RECORDS_REST_SORT_OPTIONS', {}).update(
            config.RECORDS_REST_SORT_OPTIONS)

        app.config.setdefault('RECORDS_REST_DEFAULT_SORT', {}).update(
            config.RECORDS_REST_DEFAULT_SORT)

    def connect_signals(self):
        before_record_index.connect(date_ranges_to_index)
        on_request_approval.connect(handle_request_approval)
        on_request_changes.connect(handle_request_changes)
        on_approve.connect(handle_approve)
        on_revert_approval.connect(handle_revert_approval)
        on_publish.connect(handle_publish)
        on_unpublish.connect(handle_unpublish)
        on_delete_draft.connect(handle_delete_draft)
