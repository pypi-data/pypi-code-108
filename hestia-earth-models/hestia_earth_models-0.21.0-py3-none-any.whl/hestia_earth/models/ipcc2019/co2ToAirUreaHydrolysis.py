from hestia_earth.schema import EmissionMethodTier, EmissionStatsDefinition
from hestia_earth.utils.tools import list_sum, safe_parse_float
from hestia_earth.utils.model import find_term_match

from hestia_earth.models.log import debugRequirements, logger
from hestia_earth.models.utils.dataCompleteness import _is_term_type_complete
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.term import get_urea_terms
from hestia_earth.models.utils.cycle import valid_site_type
from hestia_earth.models.utils.inorganicFertilizer import get_country_breakdown, get_term_lookup
from . import MODEL

TERM_ID = 'co2ToAirUreaHydrolysis'


def _emission(value: float):
    logger.info('model=%s, term=%s, value=%s', MODEL, TERM_ID, value)
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['methodTier'] = EmissionMethodTier.TIER_1.value
    emission['statsDefinition'] = EmissionStatsDefinition.MODELLED.value
    return emission


def _urea_input_value(data: dict):
    term_id = data.get('id')
    values = data.get('values')
    coeff = safe_parse_float(get_term_lookup(term_id, 'CO2_urea_emissions_factor'), 1)
    logger.debug('model=%s, term=%s, coefficient=%s', MODEL, term_id, coeff)
    return list_sum(values) * coeff


def _run(urea_values: list):
    value = list_sum(list(map(_urea_input_value, urea_values)))
    return [_emission(value)]


def _get_urea_values(cycle: dict, inputs: list, term_id: str):
    inputs = list(filter(lambda i: i.get('term', {}).get('@id') == term_id, inputs))
    values = [list_sum(i.get('value'), 0) for i in inputs if len(i.get('value', [])) > 0]
    return [0] if len(inputs) == 0 and _is_term_type_complete(cycle, {'termType': 'fertilizer'}) else values


def _should_run(cycle: dict):
    inputs = cycle.get('inputs', [])
    term_ids = get_urea_terms()

    country_id = cycle.get('site', {}).get('country', {}).get('@id')
    unspecified_id = 'inorganicNitrogenFertilizerUnspecifiedKgN'
    urea_share = get_country_breakdown(country_id, 'Urea_UAS_Amm_Bicarb')
    uan_share = get_country_breakdown(country_id, 'UAN_Solu')
    urea_unspecified_as_n = list_sum(find_term_match(inputs, unspecified_id).get('value', []))

    urea_values = [{'id': id, 'values': _get_urea_values(cycle, inputs, id)} for id in term_ids] + ([
        {'id': 'ureaKgN', 'values': [urea_unspecified_as_n * urea_share]},
        {'id': 'ureaAmmoniumNitrateKgN', 'values': [urea_unspecified_as_n * uan_share]}
    ] if urea_unspecified_as_n > 0 else [])
    has_urea_value = any([len(data.get('values')) > 0 for data in urea_values])

    debugRequirements(model=MODEL, term=TERM_ID,
                      has_urea_value=has_urea_value,
                      urea_unspecified_as_n=urea_unspecified_as_n,
                      urea_share=urea_share,
                      uan_share=uan_share)

    should_run = valid_site_type(cycle, True) and has_urea_value
    logger.info('model=%s, term=%s, should_run=%s', MODEL, TERM_ID, should_run)

    return should_run, urea_values


def run(cycle: dict):
    should_run, urea_values = _should_run(cycle)
    return _run(urea_values) if should_run else []
