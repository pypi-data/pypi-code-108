from hestia_earth.schema import EmissionMethodTier, EmissionStatsDefinition

from hestia_earth.models.log import logger
from hestia_earth.models.utils.emission import _new_emission
from . import MODEL
from .noxToAirSoilFlux import _should_run, _get_value

TERM_ID = 'noxToAirCropResidueDecomposition'


def _emission(value: float):
    logger.info('model=%s, term=%s, value=%s', MODEL, TERM_ID, value)
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['methodTier'] = EmissionMethodTier.TIER_1.value
    emission['statsDefinition'] = EmissionStatsDefinition.MODELLED.value
    return emission


def _run(country_id: str, N_total: float, residue: float):
    noxToAirSoilFlux = _get_value(country_id, N_total)
    return [_emission(residue * noxToAirSoilFlux / N_total)]


def run(cycle: dict):
    should_run, country_id, N_total, residue = _should_run(cycle)
    logger.info('model=%s, term=%s, should_run=%s', MODEL, TERM_ID, should_run)
    return _run(country_id, N_total, residue) if should_run else []
