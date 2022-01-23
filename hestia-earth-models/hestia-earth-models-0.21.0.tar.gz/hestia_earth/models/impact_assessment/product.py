from hestia_earth.utils.model import find_primary_product

from hestia_earth.models.log import logger
from . import MODEL

MODEL_KEY = 'product'


def _run(primary_product: dict):
    term = primary_product.get('term', {})
    term_id = term.get('@id')
    logger.info('model=%s, key=%s, value=%s', MODEL, MODEL_KEY, term_id)
    return term


def _should_run(impact: dict):
    primary_product = find_primary_product(impact.get('cycle', {}))
    should_run = primary_product is not None
    logger.info('model=%s, key=%s, should_run=%s', MODEL, MODEL_KEY, should_run)
    return should_run, primary_product


def run(impact: dict):
    should_run, primary_product = _should_run(impact)
    return _run(primary_product) if should_run else None
