from hestia_earth.models.log import debugRequirements, logger
from hestia_earth.models.utils.cycle import valid_site_type
from hestia_earth.models.utils.measurement import most_relevant_measurement_value
from . import MODEL

MODEL_KEY = 'cycleDuration'
DEFAULT_DURATION = 365


def _run(croppingIntensity: float):
    value = croppingIntensity * DEFAULT_DURATION
    logger.info('model=%s, key=%s, value=%s', MODEL, MODEL_KEY, value)
    return value


def _should_run(cycle: dict):
    site = cycle.get('site', {})
    end_date = cycle.get('endDate')
    croppingIntensity = most_relevant_measurement_value(site.get('measurements', []), 'croppingIntensity', end_date)
    cycleDuration = cycle.get('cycleDuration')

    debugRequirements(model=MODEL, key=MODEL_KEY,
                      cycleDuration=cycleDuration,
                      croppingIntensity=croppingIntensity)

    should_run = all([valid_site_type(cycle), cycleDuration == 365, croppingIntensity])
    logger.info('model=%s, key=%s, should_run=%s', MODEL, MODEL_KEY, should_run)
    return should_run, croppingIntensity


def run(cycle: dict):
    should_run, croppingIntensity = _should_run(cycle)
    return _run(croppingIntensity) if should_run else None
