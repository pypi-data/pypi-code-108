from pathlib import Path
import yaml
import os

# The default location for the MWC configuration file is ~/.mwc.
# This can be specified (e.g. to support parallel installations) using
# the MWC_CONFIG environment variable.
if "MWC_CONFIG" in os.environ:
    settings_path = Path(os.environ["MWC_CONFIG"])
else:
    settings_path = Path.home() / ".mwc"

def read_settings():
    """Reads the settings file and returns a dict. 
    If the settings file does not exist, returns {}
    """
    if settings_path.exists():
        return yaml.safe_load(settings_path.read_text())
    else:
        return {}

def iter_settings(settings, prefix=None):
    """Iterates through the settings dict, yielding (key, value) pairs.
    Nested keys are returned with dots: {'a': {'b': 'c'}} -> ('a.b', 'c')
    """
    for key, value in settings.items():
        keypath = (prefix or []) + [key]
        if isinstance(value, dict):
            for k, v in _iter_settings(value, prefix=keypath):
                yield '.'.join(keypath), v
        else:
            yield '.'.join(keypath), value

def check_settings(settings):
    """Checks that all settings match SETTINGS_FORMAT"""
    errors = []
    
def write_settings(settings):
    """Writes the settings to the settings file."""
    settings_path.write_text(yaml.dump(settings))
    
