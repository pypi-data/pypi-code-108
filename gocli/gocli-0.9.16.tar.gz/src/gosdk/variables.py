import os
from configparser import ConfigParser

# retrieve variables from environment (higher precedence) or .ini (lower)

CONFIG_SECTION = "gocli-options"
CONFIG_FILE_PATH = "~/.gocli.ini"

# ini

config = ConfigParser()
config.read(os.path.expanduser(CONFIG_FILE_PATH))


def get_variable(variable_name: str):
    return os.getenv(
        f"KMS_{variable_name.upper()}",
        config.get(CONFIG_SECTION, variable_name, fallback=None),
    )
