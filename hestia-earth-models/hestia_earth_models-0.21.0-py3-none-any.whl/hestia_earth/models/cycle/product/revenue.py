from hestia_earth.utils.tools import list_sum, non_empty_list

from hestia_earth.models.log import logger
from hestia_earth.models.utils.cycle import default_currency
from .. import MODEL

MODEL_KEY = 'revenue'


def _run(currency: str):
    def run(product: dict):
        value = list_sum(product.get('value', [0])) * product.get('price', 0)
        logger.info('model=%s, key=%s, value=%s, term=%s', MODEL, MODEL_KEY, value, product.get('term', {}).get('@id'))
        return {'currency': currency, **product, MODEL_KEY: value}
    return run


def _should_run(product: dict):
    should_run = all([
        MODEL_KEY not in product.keys(),
        any([
            len(product.get('value', [])) > 0 and product.get('price', 0) > 0,
            list_sum(product.get('value', []), -1) == 0
        ])
    ])
    term_id = product.get('term', {}).get('@id')
    logger.info('model=%s, key=%s, should_run=%s, term=%s', MODEL, MODEL_KEY, should_run, term_id)
    return should_run


def run(cycle: dict):
    products = list(filter(_should_run, cycle.get('products', [])))
    return non_empty_list(map(_run(default_currency(cycle)), products))
