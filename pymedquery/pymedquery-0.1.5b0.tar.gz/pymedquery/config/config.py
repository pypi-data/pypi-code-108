import os
from collections import defaultdict
try:
    import importlib.resources as pkg_resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as pkg_resources

from pymedquery.src.helpers import nested_dict

# Paths
ROOT = os.getcwd()
SQL_PATH = os.path.join(ROOT, "pymedquery", "sql", "tables")
# Get the package path 
data_path = pkg_resources.path('pymedquery.sql.default', 'image_default_query.sql')
with data_path as sql:
    SERIES_MASK_QUERY_DEFAULT = str(sql)

# postgres and storage params
DATABASE_TMP = 'medquery_template'

STORAGE_NAME = "medical_imaging_storage"
BUCKET_NAME = "multimodal-images"
bucket_dict = defaultdict(list)
blob_dict = defaultdict(list)
nested_blob_dict = nested_dict()
BUCKET_KEYS = ["bucket_name", "creation_date"]

TEST_TABLE = 'junction_img_table'
PRIMARY_KEY = ['study_uid']
NEW_COL_VALS = 'patient_333'
COL_TO_CHANGE = 'patient_uid'
COLS = ['study_uid', 'patient_uid', 'exam_uid']
RECORDS = [('project_king', 'patient_666', 'study_666')]
SQL_FILE_PATH = os.path.join(ROOT, 'pymedquery/data/sql/test.sql')
UPDATE_PRIMARY_KEY = 'project_king'

# Extensions
EXT_READTYPE_DICT = {"pkl": "rb", "pickle": "r", "json": "r", "csv": "r", "gz": "rb"}

# Create tables config
create_dependencies = {}
create_sql_command_dict = {}
