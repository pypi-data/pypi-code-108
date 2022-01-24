# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Thesis ID provider."""

from __future__ import absolute_import, print_function

from invenio_pidstore.providers.recordid_v2 import RecordIdProviderV2

from nr_datasets.constants import PUBLISHED_DATASET_PID_TYPE


class NRDatasetsIdProvider(RecordIdProviderV2):
    pid_type = PUBLISHED_DATASET_PID_TYPE
