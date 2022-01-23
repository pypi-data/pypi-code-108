from hestia_earth.schema import IndicatorStatsDefinition

from hestia_earth.models.log import debugRequirements, logger
from hestia_earth.models.utils.indicator import _new_indicator
from hestia_earth.models.utils.impact_assessment import get_product, get_site, convert_value_from_cycle
from hestia_earth.models.utils.cycle import land_occupation_per_kg
from hestia_earth.models.utils.input import sum_input_impacts
from . import MODEL

TERM_ID_CYCLE = 'landOccupationDuringCycle'
TERM_ID_INPUTS = 'landOccupationInputsProduction'
TERM_ID = 'landOccupationDuringCycle,landOccupationInputsProduction'


def _indicator(term_id: str, value: float):
    logger.info('model=%s, term=%s, value=%s', MODEL, term_id, value)
    indicator = _new_indicator(term_id, MODEL)
    indicator['value'] = value
    indicator['statsDefinition'] = IndicatorStatsDefinition.MODELLED.value
    return indicator


def _run_inputs(impact_assessment: dict, product: dict):
    cycle = impact_assessment.get('cycle', {})
    value = convert_value_from_cycle(product, sum_input_impacts(cycle.get('inputs', []), TERM_ID_CYCLE))
    logger.debug('model=%s, term=%s, value=%s', MODEL, TERM_ID_INPUTS, value)
    return [_indicator(TERM_ID_INPUTS, value)]


def _run(impact_assessment: dict, product: dict):
    cycle = impact_assessment.get('cycle', {})
    site = get_site(impact_assessment)
    cycle['site'] = site
    # value might be None if functionalUnit != '1 ha'
    value = land_occupation_per_kg(cycle, product)
    logger.debug('model=%s, term=%s, value=%s', MODEL, TERM_ID_CYCLE, value)
    return _indicator(TERM_ID_CYCLE, value)


def _should_run(impact_assessment: dict):
    product = get_product(impact_assessment)
    product_id = product.get('term', {}).get('@id')

    debugRequirements(model=MODEL, term=TERM_ID_CYCLE,
                      product=product_id)

    should_run = product_id is not None
    logger.info('model=%s, term=%s, should_run=%s', MODEL, TERM_ID_CYCLE, should_run)
    return should_run, product


def run(impact_assessment: dict):
    should_run, product = _should_run(impact_assessment)
    return (
        [_run(impact_assessment, product)] if should_run else []
    ) + (
        _run_inputs(impact_assessment, product) if product else []
    )
