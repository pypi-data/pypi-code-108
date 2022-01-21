from __future__ import unicode_literals
import logging
import os

log = logging


if os.environ.get('MAMMOTH_API_URL', None):
    API = os.environ['MAMMOTH_API_URL']
else:
    API = 'https://app.mammoth.io/api/v1'

log.warning('{0} is the api server URL'.format(API))


class USER_PERMISSIONS:
    OWNER = "owner"
    ADMIN = "admin"
    ANALYST = "analyst"

class RESERVED_COLUMN_DISPLAY_NAMES:
    BATCH_ID = 'batch_ID'
    BATCH_ROW_COUNT = 'batch_RowCount'
    BATCH_DATE = 'batch_Date'
    BATCH_SOURCE = 'batch_Source'
    BATCH_NAME = 'batch_Name'

class RESERVED_COLUMN_INTERNAL_NAMES:
    BATCH_ID = 'batch_table_col_id'
    BATCH_ROW_COUNT = 'batch_table_col_row_count'
    BATCH_DATE = 'batch_table_col_date'
    BATCH_SOURCE = 'batch_table_col_source'
    BATCH_NAME = 'batch_table_col_name'


class BATCH_TABLE_CONSTANTS:
    BATCH_TABLE_COLUMNS_LIST = [
        {
            'display_name': RESERVED_COLUMN_DISPLAY_NAMES.BATCH_ID,
            'internal_name': RESERVED_COLUMN_INTERNAL_NAMES.BATCH_ID,
            'type': 'NUMERIC',
            'key': 'id'
        },
        {
            'display_name': RESERVED_COLUMN_DISPLAY_NAMES.BATCH_ROW_COUNT,
            'internal_name': RESERVED_COLUMN_INTERNAL_NAMES.BATCH_ROW_COUNT,
            'type': 'NUMERIC',
            'key': 'count'
        },
        {
            'display_name': RESERVED_COLUMN_DISPLAY_NAMES.BATCH_DATE,
            'internal_name': RESERVED_COLUMN_INTERNAL_NAMES.BATCH_DATE,
            'type': 'DATE',
            'key': 'created_at'
        },
        {
            'display_name': RESERVED_COLUMN_DISPLAY_NAMES.BATCH_SOURCE,
            'internal_name': RESERVED_COLUMN_INTERNAL_NAMES.BATCH_SOURCE,
            'type': 'TEXT',
            'key': 'source'
        },
        {
            'display_name': RESERVED_COLUMN_DISPLAY_NAMES.BATCH_NAME,
            'internal_name': RESERVED_COLUMN_INTERNAL_NAMES.BATCH_NAME,
            'type': 'TEXT',
            'key': 'name'
        }
    ]

RESERVED_BATCH_COLUMN_INTERNAL_NAMES_AND_KEYS = {col['internal_name']:col['key'] for col in BATCH_TABLE_CONSTANTS.BATCH_TABLE_COLUMNS_LIST}
