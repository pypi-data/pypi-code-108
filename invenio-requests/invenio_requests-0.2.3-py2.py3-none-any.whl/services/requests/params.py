# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 TU Wien.
#
# Invenio-Requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Search parameter interpreters for requests."""

from invenio_records_resources.services.records.params import FilterParam

from ...resolvers.registry import ResolverRegistry


class ReferenceFilterParam(FilterParam):
    """Filter for reference dictionaries."""

    def __init__(self, param_name, field_name, config):
        """Constructor."""
        super().__init__(param_name, field_name, config)
        self._match_cache = {}

    def _is_valid(self, ref_type, ref_id):
        """Check if the reference dict is potentially resolvable."""
        if ref_type in self._match_cache:
            return self._match_cache[ref_type]

        # check if there's any resolver registered for the dict
        is_valid = any(
            (
                res.matches_reference_dict({ref_type: ref_id})
                for res in ResolverRegistry().get_registered_resolvers()
            )
        )
        self._match_cache[ref_type] = is_valid
        return is_valid

    def apply(self, identity, search, params):
        """Apply filter for a potentially resolvable reference dict."""
        if self.param_name not in params:
            return search

        ref_dict = params.pop(self.param_name, None)
        ref_type, ref_id = list(ref_dict.items())[0]

        # only apply the filter if it is potentially resolvable
        if self._is_valid(ref_type, ref_id):
            field_name = f"{self.field_name}.{ref_type}"
            if isinstance(ref_id, str):
                search = search.filter("term", **{field_name: ref_id})
            else:
                search = search.filter("terms", **{field_name: ref_id})

        return search
