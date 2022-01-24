import logging
import os

from dotenv import load_dotenv
from jinja2 import Environment, PackageLoader, select_autoescape

load_dotenv()

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)
log = logging.getLogger(__name__)

JINJA_ENV = Environment(loader=PackageLoader("fhir_cli"), autoescape=select_autoescape())

# CDMs

FHIR_ID = "fhir"
CDM_LIST = [FHIR_ID]
FHIR_API_URL = os.environ.get("FHIR_API_URL", "http://localhost:8080/fhir")
FHIR_COLUMN_NAME = FHIR_ID

# DBT

DBT_SCHEMA = os.environ.get("DBT_SCHEMA", "dbt")
FHIR_DBT_SCHEMA = f"{DBT_SCHEMA}_{FHIR_ID}"
DBT_INCREMENTAL_MODEL_TEMPLATE = "dbt_incremental_model.sql.j2"
DBT_MODELS_DIR = "models"
DBT_META_TABLE = "_meta"
INIT_DB_TEMPLATE = "init_db.sql.j2"
MAPPING_DIR_NAME = os.environ.get("MAPPING_DIR_NAME", "schemas")

# Postgres

POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.environ.get("POSTGRES_PORT", 5432))
POSTGRES_DB = os.environ.get("POSTGRES_DB", "postgres")
POSTGRES_USER = os.environ.get("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "postgres")
POSTGRES_SERVER_NAME = os.environ.get("POSTGRES_SERVER_NAME", "postgres")

# Functions

FUNCTIONS_DIR_NAME = "functions"

# Connect

CONNECT_URL = os.environ.get("CONNECT_URL", "http://localhost:8083")
POSTGRES_SOURCE_CONNECTOR_TEMPLATE = "postgres_source_connector.json.j2"
