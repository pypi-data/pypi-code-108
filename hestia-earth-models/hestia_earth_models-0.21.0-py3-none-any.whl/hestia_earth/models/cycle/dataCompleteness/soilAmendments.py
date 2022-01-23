from hestia_earth.models.log import logger
from hestia_earth.models.utils import is_from_model
from hestia_earth.models.utils.measurement import most_relevant_measurement, measurement_value
from . import MODEL

MODEL_KEY = 'soilAmendments'


def run(cycle: dict):
    end_date = cycle.get('endDate')
    measurements = cycle.get('site', {}).get('measurements', [])
    soilPh_measurement = most_relevant_measurement(measurements, 'soilPh', end_date)
    soilPh = measurement_value(soilPh_measurement)
    is_complete = is_from_model(soilPh_measurement) and soilPh > 6.5
    logger.info('model=%s, key=%s, is_complete=%s', MODEL, MODEL_KEY, is_complete)
    return is_complete
