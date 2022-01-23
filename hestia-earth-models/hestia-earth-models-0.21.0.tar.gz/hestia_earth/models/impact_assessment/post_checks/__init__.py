from os.path import dirname, abspath
import sys

from hestia_earth.models.utils import _run_in_serie
from hestia_earth.models.impact_assessment.post_checks import cycle

CURRENT_DIR = dirname(abspath(__file__)) + '/'
sys.path.append(CURRENT_DIR)

MODELS = [
    cycle.run
]


def run(data: dict): return _run_in_serie(data, MODELS)
