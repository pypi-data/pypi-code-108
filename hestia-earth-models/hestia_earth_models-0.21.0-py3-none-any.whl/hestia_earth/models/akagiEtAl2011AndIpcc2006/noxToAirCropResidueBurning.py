from hestia_earth.schema import EmissionMethodTier, EmissionStatsDefinition

from hestia_earth.models.log import debugRequirements, logger
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.cycle import valid_site_type
from .utils import _get_aboveGroundCropResidueBurnt_value
from . import MODEL

TERM_ID = 'noxToAirCropResidueBurning'
DRY_MATTER_FACTOR_TO_NOX = 3.11/1000


def _emission(value: float):
    logger.info('model=%s, term=%s, value=%s', MODEL, TERM_ID, value)
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['methodTier'] = EmissionMethodTier.TIER_1.value
    emission['statsDefinition'] = EmissionStatsDefinition.MODELLED.value
    return emission


def _run(product_value: list):
    value = sum(product_value)
    return [_emission(value * DRY_MATTER_FACTOR_TO_NOX)]


def _should_run(cycle: dict):
    aboveGroundCropResidueBurnt_value = _get_aboveGroundCropResidueBurnt_value(cycle)

    debugRequirements(model=MODEL, term=TERM_ID,
                      aboveGroundCropResidueBurnt=aboveGroundCropResidueBurnt_value)

    should_run = valid_site_type(cycle) and len(aboveGroundCropResidueBurnt_value) > 0
    logger.info('model=%s, term=%s, should_run=%s', MODEL, TERM_ID, should_run)
    return should_run, aboveGroundCropResidueBurnt_value


def run(cycle: dict):
    should_run, aboveGroundCropResidueBurnt_value = _should_run(cycle)
    return _run(aboveGroundCropResidueBurnt_value) if should_run else []
