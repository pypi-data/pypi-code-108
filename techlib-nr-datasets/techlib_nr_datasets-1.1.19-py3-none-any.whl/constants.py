import os

DATASETS_ALLOWED_SCHEMAS = ['nr_datasets/nr-datasets-v1.0.0.json', 'https://narodni-repozitar.cz/schemas/nr_datasets/nr-datasets-v1.0.0.json']
DATASETS_PREFERRED_SCHEMA = 'nr_datasets/nr-datasets-v1.0.0.json'

PUBLISHED_DATASET_PID_TYPE = 'datst'
DRAFT_DATASET_PID_TYPE = 'ddatst'
ALL_DATASET_PID_TYPE = 'adatst'

PUBLISHED_DATASET_RECORD = 'nr_datasets.record.PublishedDatasetRecord'
DRAFT_DATASET_RECORD = 'nr_datasets.record.DraftDatasetRecord'
ALL_DATASET_RECORD = 'nr_datasets.record.AllDatasetRecord'

published_index_name = 'nr_datasets-nr-datasets-v1.0.0'
draft_index_name = 'draft-nr_datasets-nr-datasets-v1.0.0'
all_index_name = 'nr-all'
all_datasets_index_name = 'nr-all-datasets'

prefixed_published_index_name = os.environ.get('INVENIO_SEARCH_INDEX_PREFIX',
                                               '') + published_index_name
prefixed_draft_index_name = os.environ.get('INVENIO_SEARCH_INDEX_PREFIX', '') + draft_index_name
prefixed_all_index_name = os.environ.get('INVENIO_SEARCH_INDEX_PREFIX', '') + all_index_name
prefixed_all_datasets_index_name = os.environ.get('INVENIO_SEARCH_INDEX_PREFIX', '') + all_datasets_index_name

embargoed_slug = 'c-f1cf'
open_access_slug = 'c-abf2'
restricted_slug = 'c-16ec'
