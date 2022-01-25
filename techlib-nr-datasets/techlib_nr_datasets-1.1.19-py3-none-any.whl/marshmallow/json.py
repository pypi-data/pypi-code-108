# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
#
# My site is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""JSON Schemas."""
from marshmallow import Schema, fields, INCLUDE
from marshmallow.fields import Nested, Bool
from marshmallow_utils.fields import EDTFDateString, SanitizedUnicode
from nr_datasets_metadata.marshmallow import DataSetMetadataSchemaV3
from oarepo_communities.marshmallow import OARepoCommunitiesMixin
from oarepo_fsm.marshmallow import FSMRecordSchemaMixin
from oarepo_invenio_model.marshmallow import InvenioRecordMetadataFilesMixin, InvenioRecordMetadataSchemaV1Mixin


class DOIRequested(Schema):
    publisher = SanitizedUnicode(required=True, many=False)
    requestedBy = fields.Integer(required=True)
    requestedDate = EDTFDateString(required=True)


class ValiditySchema(Schema):
    class Meta:
        unknown = INCLUDE


class NRDatasetMetadataSchemaV3(OARepoCommunitiesMixin,
                                FSMRecordSchemaMixin,
                                InvenioRecordMetadataSchemaV1Mixin,
                                InvenioRecordMetadataFilesMixin,
                                DataSetMetadataSchemaV3):
    """Schema for NR dataset record metadata."""
    _validity = Nested(ValiditySchema(), data_key='oarepo:validity', attribute='oarepo:validity')
    _draft = Bool(data_key='oarepo:draft', attribute='oarepo:draft')
    _doi_requested = Nested(DOIRequested(),
                            data_key='oarepo:doirequest',
                            attribute='oarepo:doirequest')
