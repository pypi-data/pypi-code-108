import math
from hestia_earth.schema import EmissionMethodTier, EmissionStatsDefinition
from hestia_earth.utils.tools import list_sum

from hestia_earth.models.log import debugRequirements, logger
from hestia_earth.models.utils.constant import Units, get_atomic_conversion
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.input import get_total_nitrogen
from hestia_earth.models.utils.product import residue_nitrogen
from hestia_earth.models.utils.measurement import most_relevant_measurement_value
from hestia_earth.models.utils.ecoClimateZone import get_ecoClimateZone_lookup_value
from hestia_earth.models.utils.cycle import valid_site_type
from . import MODEL

TERM_ID = 'noxToAirSoilFlux'


def _should_run(cycle: dict):
    end_date = cycle.get('endDate')
    site = cycle.get('site', {})
    measurements = site.get('measurements', [])
    ecoClimateZone = most_relevant_measurement_value(measurements, 'ecoClimateZone', end_date)
    totalNitrogenPerKgSoil = most_relevant_measurement_value(measurements, 'totalNitrogenPerKgSoil', end_date)
    nitrogen_residue = residue_nitrogen(cycle.get('products', []))
    nitrogen_content = list_sum(get_total_nitrogen(cycle.get('inputs', [])))
    N_total = nitrogen_content + nitrogen_residue

    debugRequirements(model=MODEL, term=TERM_ID,
                      ecoClimateZone=ecoClimateZone,
                      totalNitrogenPerKgSoil=totalNitrogenPerKgSoil,
                      residue=nitrogen_residue,
                      nitrogen_content=nitrogen_content,
                      N_total=N_total)

    should_run = all([
        valid_site_type(cycle),
        ecoClimateZone,
        totalNitrogenPerKgSoil,
        N_total > 0
    ])
    return should_run, ecoClimateZone, totalNitrogenPerKgSoil, N_total, nitrogen_residue


def _get_value(ecoClimateZone: str, nitrogenContent: float, N_total: float):
    eco_factor = get_ecoClimateZone_lookup_value(ecoClimateZone, 'STEHFEST_BOUWMAN_2006_NOX-N_FACTOR')
    nitrogen_factor = 0 if nitrogenContent < 0.5 else -1.0211 if nitrogenContent <= 2 else 0.7892
    conversion_unit = get_atomic_conversion(Units.KG_NOX, Units.TO_N)

    value = min(
        0.025 * N_total,
        math.exp(-0.451 + 0.0061 * N_total + nitrogen_factor + eco_factor) -
        math.exp(-0.451 + nitrogen_factor + eco_factor)
    ) * conversion_unit

    debugRequirements(model=MODEL, term=TERM_ID,
                      N_total=N_total,
                      eco_factor=eco_factor,
                      nitrogen_factor=nitrogen_factor,
                      conversion_unit=conversion_unit)

    return value


def _emission(value: float):
    logger.info('model=%s, term=%s, value=%s', MODEL, TERM_ID, value)
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['methodTier'] = EmissionMethodTier.TIER_2.value
    emission['statsDefinition'] = EmissionStatsDefinition.MODELLED.value
    return emission


def _run(eecoClimateZone: str, nitrogenContent: float, N_total: float):
    value = _get_value(eecoClimateZone, nitrogenContent, N_total)
    return [_emission(value)]


def run(cycle: dict):
    should_run, ecoClimateZone, nitrogenContent, N_total, *args = _should_run(cycle)
    logger.info('model=%s, term=%s, should_run=%s', MODEL, TERM_ID, should_run)
    return _run(ecoClimateZone, nitrogenContent, N_total) if should_run else []
