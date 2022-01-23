from os.path import dirname, abspath
import sys

from hestia_earth.models.utils import _run_in_serie
from hestia_earth.models.cycle.pre_checks import site
from hestia_earth.models.cycle.pre_checks import startDate

CURRENT_DIR = dirname(abspath(__file__)) + '/'
sys.path.append(CURRENT_DIR)

MODELS = [
    site.run,
    startDate.run
]


def run(data: dict): return _run_in_serie(data, MODELS)
