# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Persistent identifier minters."""

from __future__ import absolute_import, print_function

from nr_datasets.providers import NRDatasetsIdProvider


def nr_datasets_id_minter(record_uuid, data):
    assert 'InvenioID' not in data
    provider = NRDatasetsIdProvider.create(
        object_type='rec',
        object_uuid=record_uuid,
    )
    data['InvenioID'] = provider.pid.pid_value
    return provider.pid
