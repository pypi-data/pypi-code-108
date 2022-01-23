from functools import reduce
from hestia_earth.schema import EmissionMethodTier, EmissionStatsDefinition
from hestia_earth.utils.tools import flatten, list_sum, non_empty_list

from hestia_earth.models.log import debugRequirements, logger
from hestia_earth.models.utils.term import get_lookup_value
from hestia_earth.models.data.impact_assessment import ecoinventV3_impacts
from hestia_earth.models.utils.emission import _new_emission

MODEL = 'ecoinventV3'


def _emission(term_id: str, value: float, input: dict):
    logger.info('model=%s, term=%s, value=%s', MODEL, term_id, value)
    emission = _new_emission(term_id, MODEL)
    emission['value'] = [value]
    emission['methodTier'] = EmissionMethodTier.BACKGROUND.value
    emission['statsDefinition'] = EmissionStatsDefinition.MODELLED.value
    emission['inputs'] = [input.get('term')]
    return emission


def _add_emission(prev: dict, mapping: tuple):
    ecoinventName, coeff = mapping
    emissions = ecoinventV3_impacts(ecoinventName)
    for id, value in emissions:
        prev[id] = prev.get(id, 0) + (value * coeff)
    return prev


def _get_input_mappings(input: dict):
    term = input.get('term', {})
    value = get_lookup_value(term, 'ecoinventMapping')
    mappings = non_empty_list(value.split(';')) if value else []
    debugRequirements(model=MODEL, term=term.get('@id'),
                      mappings=';'.join(mappings))
    return [(m.split(':')[0], float(m.split(':')[1])) for m in mappings]


def _run_input(input: dict):
    term_id = input.get('term', {}).get('@id')
    input_value = list_sum(input.get('value', []))
    mappings = _get_input_mappings(input)
    should_run = len(mappings) > 0
    logger.info('model=%s, term=%s, should_run=%s', MODEL, term_id, should_run)
    grouped_emissions = reduce(_add_emission, mappings, {}) if should_run else {}
    return [_emission(term_id, value * input_value, input) for term_id, value in grouped_emissions.items()]


def run(cycle: dict):
    inputs = [i for i in cycle.get('inputs', []) if list_sum(i.get('value', [])) > 0]
    return flatten(map(_run_input, inputs))
