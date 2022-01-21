import json
import logging
import os
from enum import Enum
from typing import Optional

from tecton_spark import errors

logging.getLogger("boto3").setLevel(logging.ERROR)
logging.getLogger("botocore").setLevel(logging.ERROR)

_CONFIG_OVERRIDES = {}


class _Debugger(object):
    class ConfSource(Enum):
        SESSION_OVERRIDE = 1
        OS_ENV = 2
        LOCAL_TECTON_CONFIG = 3
        REMOTE_MDS_CONFIG = 4
        RUNTIME_CONFIG = 5
        DATABRICKS_SECRET = 6
        AWS_SECRET_MANAGER = 7
        DEFAULT = 8
        NOT_FOUND = 9

    @classmethod
    def _debug_enabled(cls) -> bool:
        key = "TECTON_DEBUG"
        if key in os.environ:
            return os.environ[key] == "1"
        elif key in _CONFIG_OVERRIDES:
            return _CONFIG_OVERRIDES[key] == "1"
        return False

    @classmethod
    def print(cls, src: ConfSource, key: str, val=None):
        if not cls._debug_enabled():
            return

        print("🔍", f"Looking up {key}")
        indent = ""
        for s in cls.ConfSource:
            if src == s:
                print(indent, "✅", f"{s.name} -> {val}")
                break
            print(indent, "👎", s.name)
            indent += " "


def set(key, value):
    _CONFIG_OVERRIDES[key] = value


def _does_key_have_valid_prefix(key) -> bool:
    for prefix in _VALID_KEY_PREFIXES:
        if key.startswith(prefix):
            return True
    return False


def _get(key) -> Optional[str]:
    """Get the config value for the given key, or return None if not found."""
    if key not in _VALID_KEYS and not _does_key_have_valid_prefix(key):
        raise errors.TectonInternalError(f"Tried accessing invalid configuration key '{key}'")

    # Session-scoped override.
    if key in _CONFIG_OVERRIDES:
        val = _CONFIG_OVERRIDES[key]
        _Debugger.print(_Debugger.ConfSource.SESSION_OVERRIDE, key, val)
        return val

    # Environment variable.
    if key in os.environ:
        val = os.environ[key]
        _Debugger.print(_Debugger.ConfSource.OS_ENV, key, val)
        return val

    # ~/.tecton/config
    if key in _LOCAL_TECTON_CONFIG:
        val = _LOCAL_TECTON_CONFIG[key]
        _Debugger.print(_Debugger.ConfSource.LOCAL_TECTON_CONFIG, key, val)
        return val

    # Config from MDS
    if key in _REMOTE_MDS_CONFIGS:
        val = _REMOTE_MDS_CONFIGS[key]
        _Debugger.print(_Debugger.ConfSource.REMOTE_MDS_CONFIG, key, val)
        return val

    # Compute runtime configs.
    if key in _RUNTIME_CONFIGS:
        val = _RUNTIME_CONFIGS[key]
        _Debugger.print(_Debugger.ConfSource.RUNTIME_CONFIG, key, val)
        return val

    if _get_runtime_env() == TectonEnv.UNKNOWN:
        # Fallback attempt to set env if user has not set it.
        _set_tecton_runtime_env()

    if _should_lookup_db_secrets(key):
        # Databricks secrets
        for scope in _get_secret_scopes():
            value = _get_from_db_secrets(key, scope)
            if value:
                _Debugger.print(_Debugger.ConfSource.DATABRICKS_SECRET, key, value)
                return value

    if _should_lookup_aws_secretsmanager(key):
        # AWS secret manager
        for scope in _get_secret_scopes():
            value = _get_from_secretsmanager(key, scope)
            if value:
                _Debugger.print(_Debugger.ConfSource.AWS_SECRET_MANAGER, key, value)
                return value

    if key in _DEFAULTS:
        value = _DEFAULTS[key]()
        _Debugger.print(_Debugger.ConfSource.DEFAULT, key, value)
        return value

    _Debugger.print(_Debugger.ConfSource.NOT_FOUND, key)
    return None


def get_or_none(key) -> Optional[str]:
    return _get(key)


def get_or_raise(key) -> str:
    val = _get(key)
    if val == None:
        raise errors.TectonInternalError(f"{key} not set")
    return val


# Internal

_LOCAL_TECTON_CONFIG_FILE = os.path.expanduser(
    "~/.tecton/config" if "TECTON_CONFIG_PATH" not in os.environ else os.environ["TECTON_CONFIG_PATH"]
)
_LOCAL_TECTON_TOKENS_FILE = os.path.expanduser(
    "~/.tecton/config.tokens"
    if "TECTON_CONFIG_PATH" not in os.environ
    else f'{os.environ["TECTON_CONFIG_PATH"]}.tokens'
)

_VALID_KEYS = [
    # Alpha features
    "ALPHA_SNOWFLAKE_COMPUTE_ENABLED",
    "API_SERVICE",
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
    "FEATURE_SERVICE",
    "HIVE_METASTORE_HOST",
    "HIVE_METASTORE_PORT",
    "HIVE_METASTORE_USERNAME",
    "HIVE_METASTORE_DATABASE",
    "HIVE_METASTORE_PASSWORD",
    "SPARK_DRIVER_LOCAL_IP",
    "METADATA_SERVICE",
    "TECTON_CLUSTER_NAME",
    "TECTON_API_KEY",
    "OAUTH_ACCESS_TOKEN",
    "OAUTH_ACCESS_TOKEN_EXPIRATION",
    "OAUTH_REFRESH_TOKEN",
    "CLI_CLIENT_ID",
    "USE_DIRECT_GRPC",
    "TECTON_WORKSPACE",
    "SATELLITE_REGIONS",
    "CLUSTER_REGION",
    "REDSHIFT_USER",
    "REDSHIFT_PASSWORD",
    "SNOWFLAKE_USER",
    "SNOWFLAKE_PASSWORD",
    "INTERMEDIATE_DATA_S3_BASE_PATH",
    "TECTON_DEBUG",
    "TECTON_RUNTIME_ENV",
    "TECTON_RUNTIME_MODE",
]

_VALID_KEY_PREFIXES = ["SECRET_"]

# Required for CLI or other local usage
_TECTON_CLI_CONFIG_KEYS = ["API_SERVICE", "FEATURE_SERVICE", "TECTON_WORKSPACE", "CLI_CLIENT_ID"]

_DEFAULTS = {"TECTON_WORKSPACE": (lambda: "prod"), "FEATURE_SERVICE": (lambda: _get("API_SERVICE"))}

_REMOTE_MDS_CONFIGS = {}

_RUNTIME_CONFIGS = {"": ""}

_RUNTIME_CONFIGS_VALID_KEYS = [
    "TECTON_RUNTIME_ENV",
    "TECTON_RUNTIME_MODE",
]

_is_running_on_databricks_cache = None
_is_running_on_emr_cache = None
TectonEnv = Enum("TectonEnv", "DATABRICKS EMR UNKNOWN")


def _is_running_on_databricks():
    """Whether we're running in Databricks notebook or not."""
    global _is_running_on_databricks_cache
    if _is_running_on_databricks_cache is None:
        main = __import__("__main__")
        filename = os.path.basename(getattr(main, "__file__", ""))
        is_python_shell = filename == "PythonShell.py"
        is_databricks_env = "DBUtils" in main.__dict__
        _is_running_on_databricks_cache = is_python_shell and is_databricks_env
    return _is_running_on_databricks_cache


def _is_running_on_emr():
    """Whether we're running in EMR notebook or not."""
    global _is_running_on_emr_cache
    if _is_running_on_emr_cache is None:
        _is_running_on_emr_cache = "EMR_CLUSTER_ID" in os.environ
    return _is_running_on_emr_cache


def _set_tecton_runtime_env():
    key = "TECTON_RUNTIME_ENV"
    if _is_running_on_databricks():
        set_runtime_config(key, "DATABRICKS")
    elif _is_running_on_emr():
        set_runtime_config(key, "EMR")
    else:
        set_runtime_config(key, "UNKNOWN")


def _is_mode_materialization():
    key = "TECTON_RUNTIME_MODE"
    if key in _RUNTIME_CONFIGS and _RUNTIME_CONFIGS[key] == "MATERIALIZATION":
        return True
    if key in os.environ and os.environ[key] == "MATERIALIZATION":
        return True
    return False


def _get_runtime_env():
    key = "TECTON_RUNTIME_ENV"
    if key in _RUNTIME_CONFIGS and _RUNTIME_CONFIGS[key] == "DATABRICKS":
        return TectonEnv.DATABRICKS
    if key in os.environ and os.environ[key] == "DATABRICKS":
        return TectonEnv.DATABRICKS
    if key in _RUNTIME_CONFIGS and _RUNTIME_CONFIGS[key] == "EMR":
        return TectonEnv.EMR
    if key in os.environ and os.environ[key] == "EMR":
        return TectonEnv.EMR
    return TectonEnv.UNKNOWN


def set_runtime_config(key: str, value: str):
    if key not in _RUNTIME_CONFIGS_VALID_KEYS:
        raise errors.TectonInternalError(f"Tried accessing invalid configuration key '{key}'")
    _RUNTIME_CONFIGS[key] = value


def _should_lookup_aws_secretsmanager(key: str) -> bool:
    # Keys used for secret manager lookups that cause infinite loops.
    return key not in ("CLUSTER_REGION", "TECTON_CLUSTER_NAME", "USE_DIRECT_GRPC")


def _should_lookup_db_secrets(key: str) -> bool:
    return _get_runtime_env() != TectonEnv.EMR and key not in ("TECTON_CLUSTER_NAME")


def _get_dbutils():
    # Returns dbutils import. Only works in Databricks notebook environment
    import IPython

    return IPython.get_ipython().user_ns["dbutils"]


def _save_tecton_config():
    _init_configs()
    tecton_config = {}
    for key in _TECTON_CLI_CONFIG_KEYS:
        tecton_config[key] = get_or_none(key)
    os.makedirs(os.path.dirname(_LOCAL_TECTON_CONFIG_FILE), exist_ok=True)
    with open(_LOCAL_TECTON_CONFIG_FILE, "w") as f:
        json.dump(tecton_config, f)


# Get key by looking in TECTON_CLUSTER_NAME'd scope and falling back to "tecton"
def _get_secret_scopes():
    cluster_name = get_or_none("TECTON_CLUSTER_NAME")
    secret_scopes = []
    if cluster_name:
        secret_prefix = cluster_name if cluster_name.startswith("tecton-") else f"tecton-{cluster_name}"
        secret_scopes.append(secret_prefix)
    secret_scopes.append("tecton")
    return secret_scopes


def _get_from_secretsmanager(key: str, scope: str):
    try:
        # Try to Grab secret from AWS secrets manager
        from boto3 import client

        if _is_mode_materialization():
            aws_secret_client = client("secretsmanager")
        else:
            aws_secret_client = client("secretsmanager", region_name=get_or_none("CLUSTER_REGION"))
        secret = aws_secret_client.get_secret_value(SecretId=f"{scope}/{key}")
        return secret["SecretString"]
    except Exception:
        # Do not fail if secret is not found
        return None


def _get_from_db_secrets(key: str, scope: str):
    try:
        dbutils = _get_dbutils()
        return dbutils.secrets.get(scope, key)
    except Exception:
        return None


def _save_token(access_token, access_token_expiration, refresh_token=None):
    os.makedirs(os.path.dirname(_LOCAL_TECTON_TOKENS_FILE), exist_ok=True)
    config = {}
    if os.path.exists(_LOCAL_TECTON_TOKENS_FILE):
        with open(_LOCAL_TECTON_TOKENS_FILE, "r") as f:
            config = json.load(f)
    config["OAUTH_ACCESS_TOKEN"] = access_token
    config["OAUTH_ACCESS_TOKEN_EXPIRATION"] = access_token_expiration
    if refresh_token:
        config["OAUTH_REFRESH_TOKEN"] = refresh_token
    with open(_LOCAL_TECTON_TOKENS_FILE, "w") as f:
        json.dump(config, f)


def _read_json_config(file_path):
    """If the file exists, reads it and returns parsed JSON. Otherwise returns empty dictionary."""
    if file_path and os.path.exists(file_path):
        with open(file_path) as f:
            content = f.read()
            if not content:
                return {}
            try:
                return json.loads(content)
            except json.decoder.JSONDecodeError as e:
                raise ValueError(
                    f"Unable to decode JSON configuration file {file_path} ({str(e)}). "
                    + "To regenerate configuration, delete this file and run `tecton login`."
                )
    else:
        return {}


_LOCAL_TECTON_CONFIG = None


def _init_configs():
    if not _is_mode_materialization():
        global _LOCAL_TECTON_CONFIG
        _LOCAL_TECTON_CONFIG = _read_json_config(_LOCAL_TECTON_CONFIG_FILE)
        for key, val in _read_json_config(_LOCAL_TECTON_TOKENS_FILE).items():
            _LOCAL_TECTON_CONFIG[key] = val


def _init_metadata_server_config(mds_response):
    global _REMOTE_MDS_CONFIGS
    _REMOTE_MDS_CONFIGS = dict(mds_response.key_values)


_init_configs()
