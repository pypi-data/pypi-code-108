from hestia_earth.models.log import logger
from . import MODEL

MODEL_KEY = 'siteDuration'


def _run(cycle: dict):
    value = cycle.get('cycleDuration')
    logger.info('model=%s, key=%s, value=%s', MODEL, MODEL_KEY, value)
    return value


def _should_run(cycle: dict):
    cycleDuration = cycle.get('cycleDuration', 0)
    otherSites = cycle.get('otherSites', [])
    should_run = cycleDuration > 0 and len(otherSites) == 0
    logger.info('model=%s, key=%s, should_run=%s', MODEL, MODEL_KEY, should_run)
    return should_run


def run(cycle: dict): return _run(cycle) if _should_run(cycle) else None
