from hestia_earth.schema import ProductStatsDefinition
from hestia_earth.utils.model import find_term_match
from hestia_earth.utils.tools import list_sum

from hestia_earth.models.log import debugRequirements, logger
from hestia_earth.models.utils.dataCompleteness import _is_term_type_incomplete
from hestia_earth.models.utils.product import _new_product
from . import MODEL

TERM_ID = 'aboveGroundCropResidueTotal'


def _product(value: float):
    logger.info('model=%s, term=%s, value=%s', MODEL, TERM_ID, value)
    product = _new_product(TERM_ID)
    product['value'] = [value]
    product['statsDefinition'] = ProductStatsDefinition.MODELLED.value
    return product


def _run(practice_value: float, value: float):
    value = 0 if value and practice_value == 0 else value / (practice_value / 100)
    return [_product(value)]


def _should_run(cycle: dict):
    removed_practice_value = find_term_match(cycle.get('practices', []), 'residueRemoved').get('value', [])
    removed_value = find_term_match(cycle.get('products', []), 'aboveGroundCropResidueRemoved').get('value', [])

    debugRequirements(model=MODEL, term=TERM_ID,
                      removed_practice_value=list_sum(removed_practice_value),
                      removed_value=list_sum(removed_value))

    should_run = all([
        _is_term_type_incomplete(cycle, TERM_ID), len(removed_practice_value) > 0, len(removed_value) > 0
    ])
    logger.info('model=%s, term=%s, should_run=%s', MODEL, TERM_ID, should_run)
    return should_run, list_sum(removed_practice_value), list_sum(removed_value)


def run(cycle: dict):
    should_run, removed_practice_value, removed_value = _should_run(cycle)
    return _run(removed_practice_value, removed_value) if should_run else []
