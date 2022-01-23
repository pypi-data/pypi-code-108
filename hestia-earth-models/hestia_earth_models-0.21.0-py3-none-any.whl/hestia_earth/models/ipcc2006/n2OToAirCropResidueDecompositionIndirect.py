from hestia_earth.schema import EmissionMethodTier, EmissionStatsDefinition, TermTermType

from hestia_earth.models.log import debugRequirements, logger
from hestia_earth.models.utils.constant import Units, get_atomic_conversion
from hestia_earth.models.utils.dataCompleteness import _is_term_type_complete
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.cycle import valid_site_type
from .utils import get_nh3_no3_nox_to_n, COEFF_NH3NOX_N2O, COEFF_NO3_N2O
from . import MODEL

TERM_ID = 'n2OToAirCropResidueDecompositionIndirect'
NO3_TERM_ID = 'no3ToGroundwaterCropResidueDecomposition'
NH3_TERM_ID = 'nh3ToAirCropResidueDecomposition'
NOX_TERM_ID = 'noxToAirCropResidueDecomposition'


def _emission(value: float):
    logger.info('model=%s, term=%s, value=%s', MODEL, TERM_ID, value)
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['methodTier'] = EmissionMethodTier.TIER_1.value
    emission['statsDefinition'] = EmissionStatsDefinition.MODELLED.value
    return emission


def _run(no3: float, nh3: float, nox: float):
    value = COEFF_NH3NOX_N2O * (nh3 + nox) + COEFF_NO3_N2O * no3
    return [_emission(value * get_atomic_conversion(Units.KG_N2O, Units.TO_N))]


def _should_run(cycle: dict):
    nh3_n, no3_n, nox_n = get_nh3_no3_nox_to_n(cycle, NH3_TERM_ID, NO3_TERM_ID, NOX_TERM_ID)

    debugRequirements(model=MODEL, term=TERM_ID,
                      no3_n=no3_n,
                      nh3_n=nh3_n,
                      nox_n=nox_n)

    should_run = valid_site_type(cycle) and (
        all([no3_n, nh3_n, nox_n]) or _is_term_type_complete(cycle, {'termType': TermTermType.CROPRESIDUE.value})
    )
    logger.info('model=%s, term=%s, should_run=%s', MODEL, TERM_ID, should_run)
    return should_run, no3_n, nh3_n, nox_n


def run(cycle: dict):
    should_run, no3, nh3, nox = _should_run(cycle)
    return _run(no3, nh3, nox) if should_run else []
