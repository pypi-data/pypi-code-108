from dateutil.relativedelta import relativedelta
from hestia_earth.utils.date import is_in_days
from hestia_earth.utils.tools import safe_parse_date

from hestia_earth.models.log import logger
from .. import MODEL

MODEL_KEY = 'startDate'


def _run(cycle: dict):
    days = -float(cycle.get('cycleDuration'))
    value = (safe_parse_date(cycle.get('endDate')) + relativedelta(days=days)).strftime('%Y-%m-%d')
    logger.info('model=%s, key=%s, value=%s', MODEL, MODEL_KEY, value)
    return value


def _should_run(cycle: dict):
    should_run = is_in_days(cycle.get('endDate')) \
        and cycle.get('cycleDuration') is not None \
        and cycle.get(MODEL_KEY) is None
    logger.info('model=%s, key=%s, should_run=%s', MODEL, MODEL_KEY, should_run)
    return should_run


def run(cycle: dict): return {**cycle, MODEL_KEY: _run(cycle)} if _should_run(cycle) else cycle
