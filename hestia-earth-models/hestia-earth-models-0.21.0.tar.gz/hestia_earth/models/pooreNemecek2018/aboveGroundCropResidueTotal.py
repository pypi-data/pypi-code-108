from hestia_earth.schema import ProductStatsDefinition, TermTermType
from hestia_earth.utils.model import filter_list_term_type
from hestia_earth.utils.tools import list_sum, safe_parse_float

from hestia_earth.models.log import debugRequirements, logger
from hestia_earth.models.utils.dataCompleteness import _is_term_type_incomplete
from hestia_earth.models.utils.product import _new_product
from hestia_earth.models.utils.crop import get_crop_lookup_value
from . import MODEL

TERM_ID = 'aboveGroundCropResidueTotal'
COLUMN_NAME = 'Default_ag_dm_crop_residue'


def _product(value: float):
    logger.info('model=%s, term=%s, value=%s', MODEL, TERM_ID, value)
    product = _new_product(TERM_ID, MODEL)
    product['value'] = [value]
    product['statsDefinition'] = ProductStatsDefinition.MODELLED.value
    return product


def _get_lookup_value(product: dict):
    term_id = product.get('term', {}).get('@id', '')
    return safe_parse_float(get_crop_lookup_value(term_id, COLUMN_NAME), None)


def _run(product: dict):
    value = _get_lookup_value(product)
    return [_product(value)]


def _should_run_product(product: dict):
    value = list_sum(product.get('value', [0]))
    lookup_value = _get_lookup_value(product)
    return value > 0 and lookup_value is not None


def _should_run(cycle: dict):
    # filter crop products with matching data in the lookup
    products = filter_list_term_type(cycle.get('products', []), TermTermType.CROP)
    products = list(filter(_should_run_product, products))
    single_crop_product = len(products) == 1

    debugRequirements(model=MODEL, term=TERM_ID,
                      single_crop_product=single_crop_product)

    should_run = all([_is_term_type_incomplete(cycle, TERM_ID), single_crop_product])
    logger.info('model=%s, term=%s, should_run=%s', MODEL, TERM_ID, should_run)
    return should_run, products


def run(cycle: dict):
    should_run, products = _should_run(cycle)
    return _run(products[0]) if should_run else []
