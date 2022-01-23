from hestia_earth.schema import CycleFunctionalUnit, PropertyStatsDefinition
from hestia_earth.utils.api import download_hestia
from hestia_earth.utils.model import find_term_match
from hestia_earth.utils.tools import list_sum, non_empty_list, safe_parse_float

from hestia_earth.models.log import logger
from hestia_earth.models.utils.property import _new_property
from hestia_earth.models.utils.term import get_irrigation_terms
from hestia_earth.models.utils.cycle import valid_site_type
from hestia_earth.models.utils.crop import get_crop_lookup_value
from . import MODEL

TERM_ID = 'rootingDepth'


def _property(value: float, term: dict):
    logger.info('model=%s, term=%s, value=%s', MODEL, TERM_ID, value)
    prop = _new_property(term, MODEL)
    prop['value'] = value
    prop['statsDefinition'] = PropertyStatsDefinition.MODELLED.value
    return prop


def _get_input_value_from_term(inputs: list, term_id: str):
    return list_sum(find_term_match(inputs, term_id).get('value'))


def _get_value(cycle: dict, term: dict, irrigation_ids: list):
    term_id = term.get('@id', '')

    if cycle.get('dataCompleteness', {}).get('water', False):
        value = sum([_get_input_value_from_term(cycle.get('inputs', []), term_id) for term_id in irrigation_ids])

        # Assumes that if water data is complete and there are no data on irrigation then there was no irrigation.
        column = 'rooting_depth_irrigated_m' if value >= 250 else 'rooting_depth_rainfed_m'
    else:
        column = 'rooting_depth_average_m'

    return safe_parse_float(get_crop_lookup_value(term_id, column), None)


def _should_run_product(product: dict):
    product_id = product.get('term', {}).get('@id')
    should_run = find_term_match(product.get('properties', []), TERM_ID, None) is None
    logger.info('model=%s, term=%s, product=%s, should_run=%s', MODEL, TERM_ID, product_id, should_run)
    return should_run


def _run_cycle(cycle: dict, products: list):
    term = download_hestia(TERM_ID)
    irrigation_ids = get_irrigation_terms()

    def run_product(product):
        value = _get_value(cycle, product.get('term'), irrigation_ids)
        prop = _property(value, term) if value is not None and term is not None else None
        return {**product, 'properties': product.get('properties', []) + [prop]} if prop else product

    return non_empty_list(map(run_product, products))


def _should_run(cycle: dict):
    should_run = valid_site_type(cycle) and cycle.get('functionalUnit') == CycleFunctionalUnit._1_HA.value
    logger.info('model=%s, term=%s, should_run=%s', MODEL, TERM_ID, should_run)
    return should_run


def run(cycle: dict):
    should_run = _should_run(cycle)
    products = list(filter(_should_run_product, cycle.get('products', []))) if should_run else []
    return _run_cycle(cycle, products) if len(products) > 0 else []
