import json
import os
from distutils.util import strtobool

SETTINGS_PREFIX = "__SERVICE_"


def environment_type_converter(s):
    if s == 'True' or s == 'False':
        return strtobool(s)
    elif s.isnumeric():
        return int(s)
    elif s[0] == "[" or s[0] == "{":
        return json.loads(s)
    else:
        return s


def apply_settings(app):
    app.config.from_pyfile("config.py")
    for key in os.environ:
        if key.startswith(SETTINGS_PREFIX):
            app.config[key.replace(SETTINGS_PREFIX, '')] = environment_type_converter(os.environ.get(key))