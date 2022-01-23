from functools import reduce
from hestia_earth.schema import EmissionMethodTier, EmissionStatsDefinition, TermTermType
from hestia_earth.utils.lookup import download_lookup
from hestia_earth.utils.model import find_term_match, filter_list_term_type
from hestia_earth.utils.tools import list_sum

from hestia_earth.models.log import debugRequirements, logger
from hestia_earth.models.utils import _filter_list_term_unit
from hestia_earth.models.utils.dataCompleteness import _is_term_type_incomplete
from hestia_earth.models.utils.inorganicFertilizer import (
    get_NH3_emission_factor, get_terms, get_term_lookup, BREAKDOWN_LOOKUP, get_country_breakdown
)
from hestia_earth.models.utils.constant import Units
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.measurement import most_relevant_measurement_value
from hestia_earth.models.utils.cycle import valid_site_type
from . import MODEL

TERM_ID = 'nh3ToAirInorganicFertilizer'


def _emission(value: float):
    logger.info('model=%s, term=%s, value=%s', MODEL, TERM_ID, value)
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['methodTier'] = EmissionMethodTier.TIER_1.value
    emission['statsDefinition'] = EmissionStatsDefinition.MODELLED.value
    return emission


def _get_input_value(soilPh: float, temperature: float):
    def get_value(input: dict):
        term_id = input.get('term', {}).get('@id')
        factor = get_NH3_emission_factor(term_id, soilPh, temperature)
        value = list_sum(input.get('value'))
        logger.debug('model=%s, term=%s, factor=%s, value=%s', MODEL, term_id, factor, value)
        return value * factor
    return get_value


def _run(temperature: float, soilPh: float, inputs: float):
    value = list_sum(list(map(_get_input_value(soilPh, temperature), inputs)))
    return [_emission(value)]


def _get_groupings():
    term_ids = get_terms()

    def get_grouping(groupings: dict, term_id: str):
        grouping = get_term_lookup(term_id, 'fertGroupingNitrogen')
        return {**groupings, **({grouping: term_id} if len(grouping) > 0 else {})}

    return reduce(get_grouping, term_ids, {})


def _get_term_value(soilPh: float, temperature: float, country_id: str, grouping: str, term_id: str):
    factor = get_NH3_emission_factor(term_id, soilPh, temperature)
    value = get_country_breakdown(country_id, grouping)
    logger.debug('model=%s, term=%s, grouping=%s, NH3_factor=%s, country breakdown=%s',
                 MODEL, TERM_ID, grouping, factor, value)
    return value * factor


def _run_with_unspecified(temperature: float, soilPh: float, unspecifiedKgN_value: float, country_id: str):
    # creates a dictionary grouping => term_id with only a single key per group (avoid counting twice)
    groupings = _get_groupings()
    value = list_sum([
        _get_term_value(soilPh, temperature, country_id, grouping, term_id) for grouping, term_id in groupings.items()
    ]) * unspecifiedKgN_value
    return [_emission(value)]


def _get_unspecifiedKgN_value(cycle: dict):
    values = find_term_match(
        cycle.get('inputs', []), 'inorganicNitrogenFertilizerUnspecifiedKgN').get('value', [])
    return [0] if len(values) == 0 and _is_term_type_incomplete(cycle, {'termType': 'fertilizer'}) else values


def _should_run(cycle: dict):
    end_date = cycle.get('endDate')
    site = cycle.get('site', {})
    measurements = site.get('measurements', [])
    soilPh = most_relevant_measurement_value(measurements, 'soilPh', end_date)
    temperature = most_relevant_measurement_value(
        measurements, 'temperatureAnnual', end_date) or most_relevant_measurement_value(
        measurements, 'temperatureLongTermAnnualMean', end_date)

    inputs = filter_list_term_type(cycle.get('inputs', []), TermTermType.INORGANICFERTILIZER)
    N_inputs = _filter_list_term_unit(inputs, Units.KG_N)

    unspecifiedKgN = _get_unspecifiedKgN_value(cycle)
    country_id = site.get('country', {}).get('@id')
    lookup = download_lookup(BREAKDOWN_LOOKUP)
    has_country_data = country_id in list(lookup.termid)

    debugRequirements(model=MODEL, term=TERM_ID,
                      temperature=temperature,
                      soilPh=soilPh,
                      unspecifiedKgN=unspecifiedKgN,
                      has_country_data=has_country_data,
                      N_inputs=len(N_inputs))

    should_run = all([
        valid_site_type(cycle, True),
        temperature,
        soilPh,
        (len(unspecifiedKgN) > 0 and has_country_data) or
        (len(unspecifiedKgN) == 0 and len(N_inputs) > 0)
    ])
    logger.info('model=%s, term=%s, should_run=%s', MODEL, TERM_ID, should_run)

    return should_run, temperature, soilPh, N_inputs, unspecifiedKgN, country_id


def run(cycle: dict):
    should_run, temperature, soilPh, N_inputs, unspecifiedKgN, country_id = _should_run(cycle)
    return (
        _run_with_unspecified(temperature, soilPh, list_sum(unspecifiedKgN), country_id) if len(unspecifiedKgN) > 0
        else _run(temperature, soilPh, N_inputs)
    ) if should_run else []
