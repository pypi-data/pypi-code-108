from hestia_earth.schema import EmissionMethodTier, EmissionStatsDefinition

from hestia_earth.models.log import debugRequirements, logger
from hestia_earth.models.utils.constant import Units, get_atomic_conversion
from hestia_earth.models.utils.dataCompleteness import _is_term_type_complete
from hestia_earth.models.utils.input import get_inorganic_fertilizer_N_total
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.cycle import valid_site_type
from .utils import get_nh3_no3_nox_to_n, COEFF_NH3NOX_N2O, COEFF_NO3_N2O
from . import MODEL

TERM_ID = 'n2OToAirInorganicFertilizerIndirect'
NO3_TERM_ID = 'no3ToGroundwaterInorganicFertilizer'
NH3_TERM_ID = 'nh3ToAirInorganicFertilizer'
NOX_TERM_ID = 'noxToAirInorganicFertilizer'


def _emission(value: float):
    logger.info('model=%s, term=%s, value=%s', MODEL, TERM_ID, value)
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['methodTier'] = EmissionMethodTier.TIER_1.value
    emission['statsDefinition'] = EmissionStatsDefinition.MODELLED.value
    return emission


def _run(cycle: dict, N_total: float):
    nh3_n, no3_n, nox_n = get_nh3_no3_nox_to_n(cycle, NH3_TERM_ID, NO3_TERM_ID, NOX_TERM_ID)
    debugRequirements(model=MODEL, term=TERM_ID,
                      no3_n=no3_n,
                      nh3_n=nh3_n,
                      nox_n=nox_n)
    value = COEFF_NH3NOX_N2O * (
        N_total * 0.1 if nox_n == 0 or nh3_n == 0 else nh3_n + nox_n
    ) + COEFF_NO3_N2O * (
        N_total * 0.3 if no3_n == 0 else no3_n
    )
    return [_emission(value * get_atomic_conversion(Units.KG_N2O, Units.TO_N))]


def _should_run(cycle: dict):
    N_total = get_inorganic_fertilizer_N_total(cycle)

    debugRequirements(model=MODEL, term=TERM_ID,
                      N_total=N_total)

    should_run = valid_site_type(cycle, True) and (
        all([N_total]) or _is_term_type_complete(cycle, {'termType': 'fertilizer'})
    )
    logger.info('model=%s, term=%s, should_run=%s', MODEL, TERM_ID, should_run)
    return should_run, N_total


def run(cycle: dict):
    should_run, N_total = _should_run(cycle)
    return _run(cycle, N_total) if should_run else []
