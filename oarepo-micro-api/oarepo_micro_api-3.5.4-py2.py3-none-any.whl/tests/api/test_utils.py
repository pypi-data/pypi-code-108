# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# OARepo Micro API is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test utils module."""
from invenio_records import Record

from oarepo_micro_api.utils import record_to_index_from_index_name


class CustomIndexNameRecord(Record):
    index_name = 'custom-test-record-v1.0.0'


def test_record_to_index(app):
    rec = CustomIndexNameRecord({})
    index, doc_type = record_to_index_from_index_name(rec)
    assert index == 'custom-test-record-v1.0.0'
    assert doc_type == '_doc'

    inveniorec = Record({})
    index, doc_type = record_to_index_from_index_name(inveniorec)
    assert index == 'records-record-v1.0.0'
    assert doc_type == '_doc'
