from hestia_earth.models.log import logger
from hestia_earth.models.utils.cycle import is_organic
from . import MODEL

MODEL_KEY = 'organic'


def run(impact: dict):
    value = is_organic(impact.get('cycle', {}))
    logger.info('model=%s, key=%s, value=%s', MODEL, MODEL_KEY, value)
    return value
