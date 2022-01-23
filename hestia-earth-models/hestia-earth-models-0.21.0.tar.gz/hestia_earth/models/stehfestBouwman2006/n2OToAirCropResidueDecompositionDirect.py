from hestia_earth.schema import EmissionMethodTier, EmissionStatsDefinition

from hestia_earth.models.log import logger
from hestia_earth.models.utils.constant import Units, get_atomic_conversion
from hestia_earth.models.utils.product import residue_nitrogen
from hestia_earth.models.utils.crop import get_N2ON_fertilizer_coeff_from_primary_product
from hestia_earth.models.utils.emission import _new_emission
from .n2OToAirSoilFlux import _should_run
from . import MODEL

TERM_ID = 'n2OToAirCropResidueDecompositionDirect'


def _emission(value: float):
    logger.info('model=%s, term=%s, value=%s', MODEL, TERM_ID, value)
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['methodTier'] = EmissionMethodTier.TIER_2.value
    emission['statsDefinition'] = EmissionStatsDefinition.MODELLED.value
    return emission


def _run(cycle: dict):
    N_total = residue_nitrogen(cycle.get('products', []))
    coefficient = get_N2ON_fertilizer_coeff_from_primary_product(cycle)
    logger.debug('model=%s, term=%s, N_total=%s, coefficient=%s', MODEL, TERM_ID, N_total, coefficient)
    value = N_total * coefficient * get_atomic_conversion(Units.KG_N2O, Units.TO_N)
    return [_emission(value)]


def run(cycle: dict):
    should_run, *args = _should_run(cycle)
    logger.info('model=%s, term=%s, should_run=%s', MODEL, TERM_ID, should_run)
    return _run(cycle) if should_run else []
