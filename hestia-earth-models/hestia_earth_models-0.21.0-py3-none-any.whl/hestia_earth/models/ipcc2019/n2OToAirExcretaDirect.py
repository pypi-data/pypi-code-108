from hestia_earth.schema import EmissionMethodTier, EmissionStatsDefinition

from hestia_earth.models.log import debugRequirements, logger
from hestia_earth.models.utils.constant import Units, get_atomic_conversion
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.input import total_excreta_n
from hestia_earth.models.utils.excretaManagement import get_lookup_factor
from . import MODEL

TERM_ID = 'n2OToAirExcretaDirect'


def _emission(value: float):
    logger.info('model=%s, term=%s, value=%s', MODEL, TERM_ID, value)
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['methodTier'] = EmissionMethodTier.TIER_2.value
    emission['statsDefinition'] = EmissionStatsDefinition.MODELLED.value
    return emission


def _run(excretaKgN: float, N2O_N_EF: float):
    value = N2O_N_EF * excretaKgN
    value = value * get_atomic_conversion(Units.KG_N2O, Units.TO_N)
    return [_emission(value)]


def _should_run(cycle: dict):
    excretaKgN = total_excreta_n(cycle.get('inputs', []))
    N2O_N_EF = get_lookup_factor(cycle.get('practices', []), 'EF_N2O-N')

    debugRequirements(model=MODEL, term=TERM_ID,
                      excretaKgN=excretaKgN,
                      N2O_N_EF=N2O_N_EF)

    should_run = all([excretaKgN, N2O_N_EF])
    logger.info('model=%s, term=%s, should_run=%s', MODEL, TERM_ID, should_run)
    return should_run, excretaKgN, N2O_N_EF


def run(cycle: dict):
    should_run, excretaKgN, N2O_N_EF = _should_run(cycle)
    return _run(excretaKgN, N2O_N_EF) if should_run else []
