import os
import sys
import appdirs

from bcanalyzer.common.const import *


def config_file_path():
    return os.path.join(appdirs.user_config_dir(APP_NAME, False), "settings.json")


if __name__ == "__main__":
    sys.path.append(os.path.abspath(os.path.join(
        os.path.dirname(__file__), '..', '..')))

    print(config_file_path())
