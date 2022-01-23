from hestia_earth.utils.tools import non_empty_list, list_average

from hestia_earth.models.log import logger
from .. import MODEL

MODEL_KEY = 'value'


def _run(input: dict):
    value = list_average(input.get('min') + input.get('max'))
    logger.info('model=%s, key=%s, value=%s, term=%s', MODEL, MODEL_KEY, value, input.get('term', {}).get('@id'))
    return {**input, MODEL_KEY: [value]}


def _should_run(input: dict):
    term_id = input.get('term', {}).get('@id')
    should_run = len(input.get(MODEL_KEY, [])) == 0 \
        and len(input.get('min', [])) > 0 and len(input.get('max', [])) > 0
    logger.info('model=%s, key=%s, should_run=%s, term=%s', MODEL, MODEL_KEY, should_run, term_id)
    return should_run


def run(cycle: dict):
    inputs = list(filter(_should_run, cycle.get('inputs', [])))
    return non_empty_list(map(_run, inputs))
