import os
import sys
import json

_config_vars = {
    'DEBUG': False,
    'CONFIG_PATH': os.path.expanduser('~/.config/carbondeploy/client.json'),
    'ADMIN_SERVER': 'https://admin.carbondeploy.com/',
    'MODEL_SERVER': 'https://models.carbondeploy.com/',
    'APP_SERVER_BACKEND': 'https://app.carbondeploy.com/',
    'APP_SERVER': 'https://www.carbondeploy.com/',
    'ORG': None,
    'USERNAME': '',
    'PASSWORD': None,
    'API_KEY': None,
}

for v, val in _config_vars.items():
    globals()[v] = val

def env_name(var):
    return 'DMN_'+var.upper()
_source = {}

for v in _config_vars.keys():
    if env_name(v) in os.environ:
        globals()[v] = os.environ[env_name(v)]
        _source[v] = 'env'

if os.path.exists(CONFIG_PATH):
    try:
        with open(CONFIG_PATH, 'r') as f:
            CONFIG = json.load(f)
        for v, val in CONFIG.items():
            v = v.upper()
            if v not in _config_vars:
                raise RuntimeError('Unrecognized config option `%s`.  Options are: %s.' %
                                   (v, list(CONFIG.keys())))
            if v not in _source:
                globals()[v] = val
                _source[v] = 'config_file'
    except Exception as e:
        raise RuntimeError('Unable to load config file `%s`: %s' % (CONFIG_PATH, e))

def get_default(_v, default_val, classname):
    if default_val is not None:
        return default_val
    v = _v.upper()
    val = globals().get(v)
    if val is None:
        raise RuntimeError(f'No {_v} specified.  Either pass it as an argument to `{classname}`, ' +
                           f'in the environment variable `{env_name(_v)}`, ' +
                           f'or add `{_v}` to the config file at `{CONFIG_PATH}`.')
    return val
