import hashlib
import uuid
from datetime import datetime
from typing import List, Optional, Any

from more_itertools import lstrip


def hash_string(input_string: str) -> int:
    """
    This function accepts a string and returns an 8 digit integer representation
    Method: generate a sha256 hash of the string and use modulo division to truncate it's integer representation to 8 digits

    WARNING:
    This function WILL return the same integer value for a string each time it is passed in the same session
    This function WILL NOT return a unique value for every unique string combination
    """
    return int(hashlib.sha256(input_string.encode('utf-8')).hexdigest(), 16) % 10**8

def hash_list(input_list: List[Any]) -> int:
    """
    This function accepts a list of objs and returns
    an 8 digit integer representation
    """
    input_list = [str(x) for x in input_list]
    input_string = ''.join(input_list)
    return hash_string(input_string)

def make_timestamp() -> str:
    now = datetime.now()
    return now.strftime("%Y_%m_%d_%H_%M")

def make_fqtn(
        table: str,
        database: Optional[str] = None,
        schema: Optional[str] = None
) -> str:
    """
    Accepts component parts and returns a possible fully qualified table string
    """
    if database is not None and schema is not None:
        return f"{database}.{schema}.{table}"
    if database is not None and schema is None:
        return f"{database}.PUBLIC.{table}"
    if database is None:
        return table

def parse_fqtn(fqtn: str, org_defaults: dict = None) -> tuple:
    """
    Accepts a possible fully qualified table string and returns its component parts
    """
    database = org_defaults.get('database') if org_defaults else None
    schema = org_defaults.get('schema') if org_defaults else None
    table = fqtn
    if fqtn.count('.') == 2:
        database = fqtn.split(".")[0]
        schema = fqtn.split(".")[1]
        table = fqtn.split(".")[-1]
    elif fqtn.count('.') == 1:
        schema = fqtn.split(".")[0]
        table = fqtn.split(".")[-1]
    return database, schema, table

def random_table_name() -> str:
    identifier = str(uuid.uuid4())
    table_name = ''.join(list(lstrip(hashlib.md5(identifier.encode('utf-8')).hexdigest(),
                            lambda x: x.isnumeric()))).upper()
    return table_name

def random_operation_table_name() -> str:
    return "RASGO_OP_" + random_table_name()

def _cleanse_sql_data_type(dtype: str) -> str:
    """
    Converts a string to Snowflake compliant data type
    """
    if dtype.lower() in ["object", "text", "variant"]:
        return "string"
    else:
        return dtype.lower()

def _cleanse_sql_list(list_in: List[str]) -> List[str]:
    """
    Converts a list of strings to Snowflake compliant names
    """
    return [_cleanse_sql_name(n) for n in list_in]

def _cleanse_sql_name(name: str) -> str:
    """
    Converts a string to a snowflake compliant value
    """
    return name.replace(" ", "_").replace("-", "_").replace('"', '').replace(".","_").upper()

def _is_restricted_sql(sql: str) -> bool:
    """
    Checks a SQL string for presence of dangerous keywords
    """
    if any(word in sql.upper() for word in SNOWFLAKE_RESTRICTED_KEYWORDS):
        return True
    return False

def _is_scary_sql(sql: str) -> bool:
    """
    Checks a SQL string for presence of injection keywords
    """
    if any(word in sql.upper() for word in SQL_INJECTION_KEYWORDS):
        return True
    return False

def _is_valid_view_sql(sql: str) -> bool:
    """
    Checks a SQL string for presence of structural keywords
    """
    mandatory_words = ["SELECT", "FROM"]
    if not all(word in sql.upper() for word in mandatory_words):
        return False
    return True

def _quote_restricted_keywords(keyword: str) -> str:
    if keyword in SNOWFLAKE_RESTRICTED_KEYWORDS:
        return f'"{keyword}"'
    return keyword


SQL_RESTRICTED_CHARACTERS = [
    ' ', '-', ';'
]

SQL_INJECTION_KEYWORDS = [
    'DELETE',
    'TRUNCATE',
    'DROP',
    'ALTER',
    'UPDATE',
    'INSERT',
    'MERGE'
]

SNOWFLAKE_RESTRICTED_KEYWORDS = [
    'ACCOUNT','ALL','ALTER','AND','ANY','AS','BETWEEN','BY',
    'CASE','CAST','CHECK','COLUMN','CONNECT','CONNECTION','CONSTRAINT',
    'CREATE','CROSS','CURRENT','CURRENT_DATE','CURRENT_TIME','CURRENT_TIMESTAMP',
    'CURRENT_USER','DATABASE','DELETE','DISTINCT','DROP','ELSE','EXISTS','FALSE',
    'FOLLOWING','FOR','FROM','FULL','GRANT','GROUP','GSCLUSTER','HAVING','ILIKE',
    'IN','INCREMENT','INNER','INSERT','INTERSECT','INTO','IS','ISSUE','JOIN','LATERAL',
    'LEFT','LIKE','LOCALTIME','LOCALTIMESTAMP','MINUS','NATURAL','NOT','NULL','OF','ON',
    'OR','ORDER','ORGANIZATION','QUALIFY','REGEXP','REVOKE','RIGHT','RLIKE','ROW','ROWS',
    'SAMPLE','SCHEMA','SELECT','SET','SOME','START','TABLE','TABLESAMPLE','THEN','TO','TRIGGER',
    'TRUE','TRY_CAST','UNION','UNIQUE','UPDATE','USING','VALUES','VIEW','WHEN','WHENEVER','WHERE','WITH'
]