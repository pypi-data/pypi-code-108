from hestia_earth.models.log import logger
from hestia_earth.models.utils.cycle import is_irrigated
from . import MODEL

MODEL_KEY = 'irrigated'


def run(impact: dict):
    value = is_irrigated(impact.get('cycle', {}))
    logger.info('model=%s, key=%s, value=%s', MODEL, MODEL_KEY, value)
    return value
