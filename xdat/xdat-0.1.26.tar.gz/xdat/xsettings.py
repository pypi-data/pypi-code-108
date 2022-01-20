import os
import tempfile

import matplotlib.colors as mcolors
from scriptine import path

PROJECT_NAME = ''
IGNORE_INDEX = True                 # useful when dataframes don't have a meaningful index
SANITY_CHECKS = False               # False, "warn", "error"
NAN_TEXTS = ['', '-', '.', '--', 'X', 'x', '#DIV/0!', '#VALUE!', 'NA', 'NAN', '0R', 'NR', 'NULL', 'None']
ACCU_METHOD = 'fsum'                # method to perform accurate math

FIGSIZE = (10, 10)

COL_DESC = dict()                   # column name --> column description
DEFAULT_COLORS = mcolors.TABLEAU_COLORS.keys()
HARD_CODED_COLORS = {
    '0': 'xkcd:sea blue',
    '0.0': 'xkcd:sea blue',
    '1': 'xkcd:crimson',
    '1.0': 'xkcd:crimson',
    'NaN': 'xkcd:gray',
    'None': 'xkcd:gray',
}

DEFAULT_MARKERS = 'o^sP*DXp<>v'
HARD_CODED_MARKERS = {
    '0': 'o',
    '0.0': 'o',
    '1': 'X',
    '1.0': 'X',
    'NaN': '^',
    'None': '^',
}

OUTPUT_PATH = None
CACHE_PATH = None


def x_add_desc(from_name, to_name):
    if from_name == to_name:
        return

    COL_DESC[from_name] = to_name


def x_get_desc(key):
    for _ in range(100):
        if key not in COL_DESC:
            return key

        assert COL_DESC[key] != key
        key = COL_DESC[key]

    raise ValueError(f"Looks like some sort of endless loop for '{key}'")


def updated_config():
    global OUTPUT_PATH, CACHE_PATH
    assert PROJECT_NAME, "need to set PROJECT_NAME"
    base_path = os.environ.get('DSXP_OUTPUT_PATH', tempfile.gettempdir())

    OUTPUT_PATH = path(base_path).joinpath(PROJECT_NAME)
    CACHE_PATH = OUTPUT_PATH.joinpath('cache')
    OUTPUT_PATH.ensure_dir()

    print(f"OUTPUT_PATH set to '{OUTPUT_PATH}'")


def get_default(default, override, possible_values=None):
    if override is None:
        if possible_values:
            assert default in possible_values, default

        return default

    if possible_values:
        assert override in possible_values, override

    return override
