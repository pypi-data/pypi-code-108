from hestia_earth.schema import EmissionMethodTier, EmissionStatsDefinition

from hestia_earth.models.log import debugRequirements, logger
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.cycle import land_occupation_per_ha
from .utils import get_emission_factor
from . import MODEL

TERM_ID = 'co2ToAirSoilCarbonStockChange'


def _emission(value: float):
    logger.info('model=%s, term=%s, value=%s', MODEL, TERM_ID, value)
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['methodTier'] = EmissionMethodTier.TIER_1.value
    emission['statsDefinition'] = EmissionStatsDefinition.MODELLED.value
    return emission


def _run(land_occupation: float, co2_land_use_change: float):
    value = land_occupation * co2_land_use_change
    return [_emission(value)]


def _should_run(cycle: dict):
    land_occupation = land_occupation_per_ha(cycle)
    co2_land_use_change = get_emission_factor(cycle, 'co2LandUseChange')

    debugRequirements(model=MODEL, term=TERM_ID,
                      land_occupation=land_occupation,
                      co2_land_use_change=co2_land_use_change)

    should_run = all([land_occupation, co2_land_use_change is not None])
    logger.info('model=%s, term=%s, should_run=%s', MODEL, TERM_ID, should_run)
    return should_run, land_occupation, co2_land_use_change


def run(cycle: dict):
    should_run, land_occupation, co2_land_use_change = _should_run(cycle)
    return _run(land_occupation, co2_land_use_change) if should_run else []
