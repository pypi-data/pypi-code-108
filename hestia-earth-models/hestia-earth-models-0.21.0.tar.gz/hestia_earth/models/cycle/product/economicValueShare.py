from hestia_earth.schema import TermTermType
from hestia_earth.utils.tools import safe_parse_float
from hestia_earth.utils.model import filter_list_term_type, find_primary_product

from hestia_earth.models.log import debugRequirements, logger
from hestia_earth.models.utils.cycle import unique_currencies
from hestia_earth.models.utils.term import get_lookup_value
from .. import MODEL

MODEL_KEY = 'economicValueShare'


def _product(product: dict, value: float):
    logger.info('model=%s, key=%s, value=%s, term=%s', MODEL, MODEL_KEY, value, product.get('term', {}).get('@id'))
    return {**product, MODEL_KEY: value}


def _run_by_revenue(products: list):
    total_revenue = sum([p.get('revenue', 0) for p in products])
    return [_product(p, p.get('revenue', 0) / total_revenue * 100) for p in products if p.get('revenue') > 0]


def _default_value(product: dict):
    return safe_parse_float(get_lookup_value(product.get('term', {}), 'global_economic_value_share'), None)


def _run_by_product(product: dict):
    value = _default_value(product)
    return [] if value is None else [_product(product, value)]


def _should_run_single(cycle: dict):
    values = [(p, _default_value(p)) for p in cycle.get('products', [])]
    products = [p for p, value in values if value is None or value != 0]
    should_run = len(products) == 1
    logger.info('model=%s, key=%s, _should_run_single=%s', MODEL, MODEL_KEY, should_run)
    return should_run, products[0] if should_run else None


def _should_run_by_product(cycle: dict):
    primary_product = find_primary_product(cycle) or {}
    product_is_crop = primary_product.get('term', {}).get('termType') == TermTermType.CROP.value
    single_product_crop = len(filter_list_term_type(cycle.get('products', []), TermTermType.CROP)) == 1

    debugRequirements(model=MODEL, term=MODEL_KEY,
                      product_is_crop=product_is_crop,
                      single_product_crop=single_product_crop)

    should_run = all([product_is_crop, single_product_crop])
    logger.info('model=%s, key=%s, should_run_by_product=%s', MODEL, MODEL_KEY, should_run)
    return should_run


def _should_have_revenue(product: dict):
    term_type = product.get('term', {}).get('termType')
    return term_type not in [
        TermTermType.CROPRESIDUE,
        TermTermType.EXCRETA
    ]


def _should_run_by_revenue(cycle: dict):
    products = cycle.get('products', [])
    total_value = sum([p.get(MODEL_KEY, 0) for p in products])
    currencies = unique_currencies(cycle)
    same_currencies = len(currencies) < 2
    all_with_revenue = all([p.get('revenue', -1) >= 0 for p in products if _should_have_revenue(p)])

    debugRequirements(model=MODEL, term=MODEL_KEY,
                      total_value=total_value,
                      all_with_revenue=all_with_revenue,
                      currencies=';'.join(currencies),
                      same_currencies=same_currencies)

    should_run = all([total_value < 100.5, all_with_revenue, same_currencies])
    logger.info('model=%s, key=%s, should_run_by_revenue=%s', MODEL, MODEL_KEY, should_run)
    return should_run


def run(cycle: dict):
    products = cycle.get('products', [])
    should_run_single, single_product = _should_run_single(cycle)
    return _run_by_revenue(products) if _should_run_by_revenue(cycle) else (
        _run_by_product(find_primary_product(cycle)) if _should_run_by_product(cycle)
        else [_product(single_product, 100)] if should_run_single
        else []
    )
