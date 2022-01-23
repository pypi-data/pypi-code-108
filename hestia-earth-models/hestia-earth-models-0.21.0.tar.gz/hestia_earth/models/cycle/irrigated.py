from hestia_earth.schema import TermTermType, CycleFunctionalUnit
from hestia_earth.utils.tools import list_average
from hestia_earth.utils.model import filter_list_term_type

from hestia_earth.models.log import logger
from hestia_earth.models.utils.practice import _new_practice
from . import MODEL

TERM_ID = 'irrigated'


def _run():
    logger.info('model=%s, term=%s', MODEL, TERM_ID)
    return [_new_practice(TERM_ID)]


def _has_water_practices(practices: list):
    return not any([p for p in practices if p.get('term', {}).get('termType') == TermTermType.WATERREGIME.value
                    and p.get('term', {}).get('@id') != TERM_ID])


def _should_run_inputs(inputs: list, functionalUnit: str):
    irrigation_inputs = filter_list_term_type(inputs, TermTermType.WATER)
    value = sum([list_average(i.get('value')) for i in irrigation_inputs if len(i.get('value', [])) > 0])
    return len(irrigation_inputs) > 0 and (
        functionalUnit != CycleFunctionalUnit._1_HA.value or value > 250
    )


def _should_run(cycle: dict):
    should_run = _has_water_practices(cycle.get('practices', [])) \
        and _should_run_inputs(cycle.get('inputs', []), cycle.get('functionalUnit'))
    logger.info('model=%s, term=%s, should_run=%s', MODEL, TERM_ID, should_run)
    return should_run


def run(cycle: dict): return _run() if _should_run(cycle) else []
