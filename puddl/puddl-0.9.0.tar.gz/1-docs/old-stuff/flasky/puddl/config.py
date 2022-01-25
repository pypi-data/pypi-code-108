import json
import logging
import os

from pathlib import Path

log = logging.getLogger(__name__)

path = Path("~/.puddlrc").expanduser()

_config = {"db": {"drivername": "postgresql"}}


def read():
    global _config
    with path.open() as f:
        _config = json.load(f)


DB2ENV = {
    "username": "PGUSER",
    "password": "PGPASSWORD",
    "host": "PGHOST",
    "port": "PGPORT",
    "database": "PGDATABASE",
}


def from_env():
    global _config
    converted = {a: os.environ[b] for a, b in DB2ENV.items()}
    _config["db"] = {**_config["db"], **converted}


def to_env():
    global _config
    db_env_vars = {b: _config["db"][a] for a, b in DB2ENV.items()}
    return {**os.environ.copy(), **db_env_vars}


def write():
    with path.open("w") as f:
        json.dump(_config, f, sort_keys=True, indent=2)
        f.write("\n")


def get(section):
    read()
    return _config[section]
