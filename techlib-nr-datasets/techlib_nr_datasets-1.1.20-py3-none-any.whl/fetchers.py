# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Persistent identifier fetchers.

A proper fetcher is defined as a function that return a
:data:`invenio_pidstore.fetchers.FetchedPID` instance.

E.g.

.. code-block:: python

    def my_fetcher(record_uuid, data):
        return FetchedPID(
            provider=MyRecordIdProvider,
            pid_type=MyRecordIdProvider.pid_type,
            pid_value=extract_pid_value(data),
        )

To see more about providers see :mod:`invenio_pidstore.providers`.
"""

from __future__ import absolute_import, print_function

from invenio_pidstore.fetchers import FetchedPID
from oarepo_communities.converters import CommunityPIDValue
from oarepo_communities.proxies import current_oarepo_communities

from .providers import NRDatasetsIdProvider


def nr_datasets_id_fetcher(record_uuid, data):
    """Fetch a record's identifiers.

    :param record_uuid: The record UUID.
    :param data: The record metadata.
    :returns: A :data:`invenio_pidstore.fetchers.FetchedPID` instance.
    """
    id_field = 'InvenioID'
    return FetchedPID(  # FetchedPID je obyčejný namedtuple
        provider=NRDatasetsIdProvider,
        pid_type=NRDatasetsIdProvider.pid_type,
        pid_value=CommunityPIDValue(
            str(data[id_field]),
            current_oarepo_communities.get_primary_community_field(data))
    )
