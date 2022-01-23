from hestia_earth.schema import ProductStatsDefinition
from hestia_earth.utils.tools import non_empty_list, safe_parse_float

from hestia_earth.models.log import logger
from hestia_earth.models.utils.property import get_node_property
from hestia_earth.models.utils.dataCompleteness import _is_term_type_incomplete
from hestia_earth.models.utils.product import _new_product
from hestia_earth.models.utils.crop import get_crop_lookup_value
from . import MODEL

TERM_ID = 'aboveGroundCropResidueRemoved'
PROPERTY_KEY = 'dryMatter'


def _product(value: float):
    logger.info('model=%s, term=%s, value=%s', MODEL, TERM_ID, value)
    product = _new_product(TERM_ID, MODEL)
    product['value'] = [value]
    product['statsDefinition'] = ProductStatsDefinition.MODELLED.value
    return product


def _get_value(product: dict, product_dm_property: dict):
    value = product.get('value', [0])[0]
    dm_percent = safe_parse_float(product_dm_property.get('value'))
    logger.debug('model=%s, term=%s, value=%s, dm_percent=%s',
                 MODEL, product.get('term', {}).get('@id'), value, dm_percent)
    return value * dm_percent / 100


def _run(products: list):
    value = sum([_get_value(product, dm_prop) for product, dm_prop in products])
    return [_product(value)] if value is not None else []


def _should_run_product(product: dict):
    term_id = product.get('term', {}).get('@id')
    product_match = get_crop_lookup_value(term_id, 'isAboveGroundCropResidueRemoved')
    property = get_node_property(product, PROPERTY_KEY) if product_match else None
    logger.debug('model=%s, term=%s, match=%s', MODEL, term_id, product_match)
    return [product, property] if property else []


def _should_run(cycle: dict):
    products = non_empty_list(map(_should_run_product, cycle.get('products', [])))
    should_run = len(products) > 0 and _is_term_type_incomplete(cycle, TERM_ID)
    logger.info('model=%s, term=%s, should_run=%s', MODEL, TERM_ID, should_run)
    return should_run, products


def run(cycle: dict):
    should_run, products = _should_run(cycle)
    return _run(products) if should_run else []
