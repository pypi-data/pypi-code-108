from flask import url_for
from invenio_records_files.api import Record
from oarepo_fsm.mixins import FSMMixin
from oarepo_communities.constants import STATE_EDITING
from oarepo_communities.converters import CommunityPIDValue
from oarepo_communities.proxies import current_oarepo_communities
from oarepo_communities.record import CommunityRecordMixin
from oarepo_invenio_model import InheritedSchemaRecordMixin
from oarepo_records_draft.record import InvalidRecordAllowedMixin, DraftRecordMixin
from oarepo_validate import SchemaKeepingRecordMixin, MarshmallowValidatedRecordMixin, FilesKeepingRecordMixin
from oarepo_tokens.views import TokenEnabledDraftRecordMixin
from oarepo_communities.permissions import update_object_permission_impl

from .constants import published_index_name, draft_index_name, \
    all_datasets_index_name, DATASETS_PREFERRED_SCHEMA, DATASETS_ALLOWED_SCHEMAS
from .marshmallow import NRDatasetMetadataSchemaV3


class DatasetBaseRecord(SchemaKeepingRecordMixin,
                        FilesKeepingRecordMixin,
                        MarshmallowValidatedRecordMixin,
                        InheritedSchemaRecordMixin,
                        CommunityRecordMixin,
                        FSMMixin,
                        Record):
    ALLOWED_SCHEMAS = DATASETS_ALLOWED_SCHEMAS
    PREFERRED_SCHEMA = DATASETS_PREFERRED_SCHEMA
    MARSHMALLOW_SCHEMA = NRDatasetMetadataSchemaV3
    INITIAL_STATE = STATE_EDITING


class PublishedDatasetRecord(InvalidRecordAllowedMixin, DatasetBaseRecord):
    index_name = published_index_name

    @property
    def canonical_url(self):
        return url_for('invenio_records_rest.datasets-community_item',
                       pid_value=CommunityPIDValue(
                           self['InvenioID'],
                           current_oarepo_communities.get_primary_community_field(self)),
                       _external=True)


class DraftDatasetRecord(DraftRecordMixin, TokenEnabledDraftRecordMixin, DatasetBaseRecord):
    index_name = draft_index_name
    CREATE_TOKEN_PERMISSION = update_object_permission_impl

    @property
    def canonical_url(self):
        return url_for('invenio_records_rest.draft-datasets-community_item',
                       pid_value=CommunityPIDValue(
                           self['InvenioID'],
                           current_oarepo_communities.get_primary_community_field(self)),
                       _external=True)


class AllDatasetRecord(SchemaKeepingRecordMixin, CommunityRecordMixin, Record):
    ALLOWED_SCHEMAS = DATASETS_ALLOWED_SCHEMAS
    PREFERRED_SCHEMA = DATASETS_PREFERRED_SCHEMA
    index_name = all_datasets_index_name
    # TODO: better canonical url based on if the class is published or not
