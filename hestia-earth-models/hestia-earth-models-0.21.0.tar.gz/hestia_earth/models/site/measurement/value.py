from hestia_earth.utils.tools import non_empty_list, list_average

from hestia_earth.models.log import logger
from hestia_earth.models.utils.measurement import _new_measurement
from .. import MODEL

MODEL_KEY = 'value'


def _run(measurement: dict):
    value = list_average(measurement.get('min') + measurement.get('max'))
    logger.info('model=%s, key=%s, value=%s, term=%s', MODEL, MODEL_KEY, value, measurement.get('term', {}).get('@id'))
    measurement = _new_measurement(measurement.get('term'))
    measurement[MODEL_KEY] = [value]
    return measurement


def _should_run(measurement: dict):
    term_id = measurement.get('term', {}).get('@id')
    should_run = len(measurement.get(MODEL_KEY, [])) == 0 \
        and len(measurement.get('min', [])) > 0 and len(measurement.get('max', [])) > 0
    logger.info('model=%s, key=%s, should_run=%s, term=%s', MODEL, MODEL_KEY, should_run, term_id)
    return should_run


def run(cycle: dict):
    measurements = list(filter(_should_run, cycle.get('measurements', [])))
    return non_empty_list(map(_run, measurements))
