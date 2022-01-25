"""Collection of methods for getting and setting values in the config file."""
import logging
import os
from configparser import ConfigParser

from aop2db.constants import DATABASE
from aop2db.defaults import CONFIG, CONN_STRING

logger = logging.getLogger(__name__)


def __check_config_file() -> bool:
    if not os.path.isfile(CONFIG):  # then make empty file
        with open(CONFIG, "w"):
            pass
        return False

    return True


def get_conn() -> str:
    """Retrieve CONN in the config file. If no config file, it makes one and sets the CONN to SQLite by default."""
    __check_config_file()
    config = ConfigParser()
    config.read(CONFIG)

    if not config.has_section(DATABASE):
        config.add_section(DATABASE)
        config.set(DATABASE, "CONN", CONN_STRING)
        with open(CONFIG, "w") as cf:
            config.write(cf)

        return CONN_STRING

    else:
        return config.get(DATABASE, "CONN")


def set_conn(conn_string: str) -> None:
    """Set the relational database connection URL."""
    get_conn()  # To make sure config file is there
    config = ConfigParser()
    config.read(CONFIG)
    config.set(DATABASE, "CONN", conn_string)
    with open(CONFIG, "w") as cf:
        config.write(cf)
