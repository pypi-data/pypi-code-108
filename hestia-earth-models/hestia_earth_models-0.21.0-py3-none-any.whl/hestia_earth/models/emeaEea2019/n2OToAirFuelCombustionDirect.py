from hestia_earth.schema import EmissionMethodTier, EmissionStatsDefinition
from hestia_earth.utils.tools import list_sum

from hestia_earth.models.log import debugRequirements, logger
from hestia_earth.models.utils.emission import _new_emission
from .utils import _get_fuel_values
from . import MODEL

TERM_ID = 'n2OToAirFuelCombustionDirect'
DIESEL_COMB_N2O = 0.000136
GASOLINE_COMB_N2O = 0.000059


def _emission(value: float):
    logger.info('model=%s, term=%s, value=%s', MODEL, TERM_ID, value)
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['methodTier'] = EmissionMethodTier.TIER_1.value
    emission['statsDefinition'] = EmissionStatsDefinition.MODELLED.value
    return emission


def _run(diesel_values: list, gasoline_values: list):
    diesel_value = list_sum(diesel_values) * DIESEL_COMB_N2O
    gasoline_value = list_sum(gasoline_values) * GASOLINE_COMB_N2O
    return [_emission(diesel_value + gasoline_value)]


def _should_run(cycle: dict):
    diesel_values, gasoline_values = _get_fuel_values(cycle)

    debugRequirements(model=MODEL, term=TERM_ID,
                      diesel_values=list_sum(diesel_values),
                      gasoline_values=list_sum(gasoline_values))

    should_run = len(diesel_values) > 0 or len(gasoline_values) > 0
    logger.info('model=%s, term=%s, should_run=%s', MODEL, TERM_ID, should_run)
    return should_run, diesel_values, gasoline_values


def run(cycle: dict):
    should_run, diesel_values, gasoline_values = _should_run(cycle)
    return _run(diesel_values, gasoline_values) if should_run else []
