from functools import reduce
from hestia_earth.schema import InputStatsDefinition, TermTermType
from hestia_earth.utils.model import filter_list_term_type
from hestia_earth.utils.tools import flatten, list_sum, non_empty_list

from hestia_earth.models.log import logger
from hestia_earth.models.utils.term import get_lookup_value
from hestia_earth.models.utils.input import _new_input
from . import MODEL


def _input(term_id: str, value: float, operation: dict):
    logger.info('model=%s, term=%s, value=%s', MODEL, term_id, value)
    input = _new_input(term_id, MODEL)
    input['value'] = [value]
    input['statsDefinition'] = InputStatsDefinition.MODELLED.value
    input['operation'] = operation
    return input


def _run_operation(practice: dict):
    operation = practice.get('term', {})
    value = list_sum(practice.get('value'))
    coeffs = get_lookup_value(operation, 'fuelUse')
    values = non_empty_list(coeffs.split(';')) if coeffs else []
    return [(operation, c.split(':')[0], float(c.split(':')[1]) * value) for c in values]


def _group_inputs(values: list):
    def group_by(prev: dict, curr: tuple):
        term, id, value = curr
        group = prev.get(id, {})
        group['operation'] = term
        group['value'] = group.get('value', 0) + value
        return {**prev, id: group}

    return reduce(group_by, values, {})


def _run(operations: list):
    inputs = flatten(map(_run_operation, operations))
    inputs = _group_inputs(inputs)
    return [_input(key, value.get('value'), value.get('operation')) for key, value in inputs.items()]


def _should_run(cycle: dict):
    operations = filter_list_term_type(cycle.get('practices', []), TermTermType.OPERATION)
    operations = [p for p in operations if list_sum(p.get('value', [])) > 0]

    should_run = len(operations) > 0
    logger.info('model=%s, term=fuelElectricity, should_run=%s', MODEL, should_run)
    return should_run, operations


def run(cycle: dict):
    should_run, operations = _should_run(cycle)
    return _run(operations) if should_run else []
