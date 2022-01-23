from hestia_earth.schema import EmissionMethodTier, TermTermType, EmissionStatsDefinition
from hestia_earth.utils.lookup import column_name, download_lookup, get_table_value
from hestia_earth.utils.model import find_primary_product, filter_list_term_type
from hestia_earth.utils.tools import safe_parse_float

from hestia_earth.models.log import debugRequirements, debugMissingLookup, logger
from hestia_earth.models.utils.dataCompleteness import _is_term_type_complete
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.constant import Units, get_atomic_conversion
from hestia_earth.models.utils.input import total_excreta_tan
from . import MODEL

TERM_ID = 'nh3ToAirExcreta'


def _emission(value: float):
    logger.info('model=%s, term=%s, value=%s', MODEL, TERM_ID, value)
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['methodTier'] = EmissionMethodTier.TIER_2.value
    emission['statsDefinition'] = EmissionStatsDefinition.MODELLED.value
    return emission


def get_nh3_factor(termType: str, practices: list, lookup_col: str):
    practices = filter_list_term_type(practices, TermTermType.EXCRETAMANAGEMENT)
    practice_id = practices[0].get('term', {}).get('@id') if len(practices) > 0 else None
    lookup_name = f"excretaManagement-{termType}-NH3_EF_2019.csv"
    lookup = download_lookup(lookup_name)
    value = get_table_value(lookup, 'termid', practice_id, column_name(lookup_col))
    debugMissingLookup(lookup_name, 'termid', practice_id, lookup_col, value)
    return safe_parse_float(value, None)


def _run(excretaKgTAN: float, NH3_N_EF: float):
    value = (NH3_N_EF or 0) * excretaKgTAN
    value = value * get_atomic_conversion(Units.KG_NH3, Units.TO_N)
    return [_emission(value)]


def _should_run(cycle: dict):
    primary_product = find_primary_product(cycle) or {}
    product_id = primary_product.get('term', {}).get('@id')
    termType = primary_product.get('term', {}).get('termType')

    excretaKgTAN = total_excreta_tan(cycle.get('inputs', []))

    NH3_N_EF = get_nh3_factor(termType, cycle.get('practices', []), product_id) if product_id else None

    debugRequirements(model=MODEL, term=TERM_ID,
                      excretaKgTAN=excretaKgTAN,
                      NH3_N_EF=NH3_N_EF)

    should_run = all([
        excretaKgTAN, NH3_N_EF is not None
    ]) or _is_term_type_complete(cycle, {'termType': TermTermType.EXCRETAMANAGEMENT.value})
    logger.info('model=%s, term=%s, should_run=%s', MODEL, TERM_ID, should_run)
    return should_run, excretaKgTAN, NH3_N_EF


def run(cycle: dict):
    should_run, excretaKgTAN, NH3_N_EF = _should_run(cycle)
    return _run(excretaKgTAN, NH3_N_EF) if should_run else []
