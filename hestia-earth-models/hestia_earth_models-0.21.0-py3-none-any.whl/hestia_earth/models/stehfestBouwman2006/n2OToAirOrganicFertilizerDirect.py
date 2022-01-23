from hestia_earth.schema import EmissionMethodTier, EmissionStatsDefinition

from hestia_earth.models.log import logger
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.input import get_organic_fertilizer_N_total
from .n2OToAirSoilFlux import _get_value, _should_run
from . import MODEL

TERM_ID = 'n2OToAirOrganicFertilizerDirect'


def _emission(value: float):
    logger.info('model=%s, term=%s, value=%s', MODEL, TERM_ID, value)
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['methodTier'] = EmissionMethodTier.TIER_2.value
    emission['statsDefinition'] = EmissionStatsDefinition.MODELLED.value
    return emission


def _run(cycle: dict, content_list_of_items: list, N_total: float):
    n2OToAirSoilFlux = _get_value(content_list_of_items, N_total)
    value = get_organic_fertilizer_N_total(cycle)
    logger.debug('model=%s, term=%s, soil flux=%s, value=%s', MODEL, TERM_ID, n2OToAirSoilFlux, value)
    return [_emission(value * n2OToAirSoilFlux / N_total)]


def run(cycle: dict):
    should_run, N_total, content_list_of_items = _should_run(cycle)
    logger.info('model=%s, term=%s, should_run=%s', MODEL, TERM_ID, should_run)
    return _run(cycle, content_list_of_items, N_total) if should_run else []
