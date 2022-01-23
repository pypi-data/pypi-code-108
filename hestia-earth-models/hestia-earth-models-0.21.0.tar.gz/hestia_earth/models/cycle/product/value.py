from hestia_earth.utils.tools import non_empty_list, list_average

from hestia_earth.models.log import logger
from .. import MODEL

MODEL_KEY = 'value'


def _run(product: dict):
    value = list_average(product.get('min') + product.get('max'))
    logger.info('model=%s, key=%s, value=%s, term=%s', MODEL, MODEL_KEY, value, product.get('term', {}).get('@id'))
    return {**product, MODEL_KEY: [value]}


def _should_run(product: dict):
    term_id = product.get('term', {}).get('@id')
    should_run = len(product.get(MODEL_KEY, [])) == 0 \
        and len(product.get('min', [])) > 0 and len(product.get('max', [])) > 0
    logger.info('model=%s, key=%s, should_run=%s, term=%s', MODEL, MODEL_KEY, should_run, term_id)
    return should_run


def run(cycle: dict):
    products = list(filter(_should_run, cycle.get('products', [])))
    return non_empty_list(map(_run, products))
