from os.path import dirname, abspath
import sys

from hestia_earth.models.utils import _run_in_serie

CURRENT_DIR = dirname(abspath(__file__)) + '/'
sys.path.append(CURRENT_DIR)

MODELS = []


def run(data: dict): return _run_in_serie(data, MODELS)
