# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Elasticsearch dumpers for the is_expired state of requests."""


from invenio_records.dumpers import ElasticsearchDumperExt


class CalculatedFieldDumperExt(ElasticsearchDumperExt):
    """Elasticsearch dumper extension for calculated fields."""

    def __init__(self, field, prop=None):
        """Constructor.

        :param field: Field into which to dump the property value.
        :param prop: Property whose value to dump.
        """
        super().__init__()
        self.field = field
        self.property = prop or field

    def dump(self, record, data):
        """Dump the data."""
        data[self.field] = getattr(record, self.property)

    def load(self, data, record_cls):
        """Load the data."""
        data.pop(self.field)
