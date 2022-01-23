from functools import reduce
from hestia_earth.schema import InputStatsDefinition
from hestia_earth.utils.model import find_term_match
from hestia_earth.utils.tools import safe_parse_float
from hestia_earth.utils.api import node_exists

from hestia_earth.models.log import logger
from hestia_earth.models.utils.input import _new_input
from hestia_earth.models.utils.property import find_term_property
from . import MODEL


def _as_kg_mass(percent: int, value: int): return (1 / (percent/100)) * value


def _kg_N(percent: int, value: int): return (percent/100) * value


SUFFIX_VALUE = 'KgMass'
SUFFIXES = ['KgMass', 'KgN']
SUFFIX_MAP = {
    'KgMass': {
        'opposite': 'KgN',
        'value_fn': _as_kg_mass
    },
    'KgN': {
        'opposite': 'KgMass',
        'value_fn': _kg_N
    }
}


def _opposite_id(id: str, suffix: str): return f"{id}{SUFFIX_MAP[suffix]['opposite']}"


def _term_no_suffix_id(id: str): return reduce(lambda prev, curr: prev.replace(curr, ''), SUFFIXES, id)


def _term_no_suffix_exists(id: str): return all([node_exists(f"{id}{suffix}") for suffix in SUFFIXES])


def _term_no_suffix_should_run(inputs: list):
    def _should_run(id: str):
        return any([find_term_match(inputs, f"{id}{suffix}", None) is not None for suffix in SUFFIXES])

    return _should_run


def _run_suffix(term_id: str, suffix: str):
    full_term_id = f"{term_id}{SUFFIX_VALUE}"
    property = find_term_property(full_term_id, 'nitrogenContent', {'value': None})
    percent = safe_parse_float(property.get('value'))
    logger.debug('model=%s, term=%s, percent=%s', MODEL, full_term_id, percent)
    return {'suffix': suffix, 'percent': percent} if percent else None


def _run_input(inputs: list):
    def _run(term_id: str):
        model = next((_run_suffix(term_id, suffix) for suffix in SUFFIXES
                      if find_term_match(inputs, f"{term_id}{suffix}", None) is None), None)
        if model is not None:
            suffix = model.get('suffix')
            suffix_term_id = f"{term_id}{suffix}"
            opposite_term_id = _opposite_id(term_id, suffix)
            opposite_value = find_term_match(inputs, opposite_term_id).get('value', [0])[0]
            value = SUFFIX_MAP[suffix]['value_fn'](model.get('percent'), opposite_value)

            logger.info('model=%s, term=%s, value=%s', MODEL, suffix_term_id, value)
            input = _new_input(suffix_term_id, MODEL)
            input['value'] = [value]
            input['statsDefinition'] = InputStatsDefinition.MODELLED.value
            return input
    return _run


def _run_inputs(inputs: list, term_ids: list): return list(map(_run_input(inputs), term_ids))


def _should_run(inputs: list):
    term_ids = [element.get('term', {}).get('@id') for element in inputs]
    term_ids = list(set(map(_term_no_suffix_id, term_ids)))
    term_ids = list(filter(_term_no_suffix_exists, term_ids))
    term_ids = list(filter(_term_no_suffix_should_run(inputs), term_ids))
    should_run = len(term_ids) > 0
    logger.info('model=%s, term=%s, should_run=%s', MODEL, term_ids, should_run)
    return should_run, term_ids


def run(cycle: dict):
    inputs = cycle.get('inputs', [])
    should_run, term_ids = _should_run(inputs)
    return _run_inputs(inputs, term_ids) if should_run else []
