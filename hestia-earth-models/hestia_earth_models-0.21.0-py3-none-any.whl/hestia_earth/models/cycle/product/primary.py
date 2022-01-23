from hestia_earth.models.log import logger
from .. import MODEL

MODEL_KEY = 'primary'


def _product(product: dict):
    logger.info('model=%s, key=%s, value=%s', MODEL, MODEL_KEY, product.get('term', {}).get('@id'))
    return {**product, MODEL_KEY: True}


def _find_primary_product(products: list):
    # If only one product, primary = True
    if len(products) == 1:
        return products[0]

    # else primary product = the product with the largest economic value share
    else:
        max_products = sorted(
            list(filter(lambda p: 'economicValueShare' in p.keys(), products)),  # take only products with value
            key=lambda k: k.get('economicValueShare'),  # sort by value
            reverse=True  # take the first as top value
        )
        if len(max_products) > 0:
            return max_products[0]

    return None


def _run(products: list):
    primary = _find_primary_product(products)
    return [] if primary is None else [_product(primary)]


def _should_run(products: list):
    primary = next((p for p in products if p.get(MODEL_KEY, False) is True), None)
    should_run = len(products) > 0 and primary is None
    logger.info('model=%s, key=%s, should_run=%s', MODEL, MODEL_KEY, should_run)
    return should_run


def run(cycle: dict):
    products = cycle.get('products', [])
    return _run(products) if _should_run(products) else []
