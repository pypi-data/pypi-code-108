from functools import reduce
from typing import List
from hestia_earth.schema import MeasurementStatsDefinition
from hestia_earth.utils.model import find_term_match

from hestia_earth.models.log import logger
from hestia_earth.models.utils.measurement import _new_measurement, measurement_value
from .utils import download, find_existing_measurement, has_geospatial_data, _site_gadm_id
from . import MODEL

TERM_ID = 'clayContent,sandContent,siltContent'
TERM_IDS = {
    'clayContent': 'T_CLAY',
    'sandContent': 'T_SAND',
    'siltContent': None
}
EE_PARAMS = {
    'type': 'raster',
    'reducer': 'mean'
}
BIBLIO_TITLE = 'The harmonized world soil database. verson 1.0'


def _measurement(term_id: str, value: int):
    logger.info('model=%s, term=%s, value=%s', MODEL, term_id, value)
    measurement = _new_measurement(term_id, MODEL, BIBLIO_TITLE)
    measurement['value'] = [value]
    measurement['depthUpper'] = 0
    measurement['depthLower'] = 30
    measurement['statsDefinition'] = MeasurementStatsDefinition.SPATIAL.value
    return measurement


def _download(site: dict, collection: str):
    value = download(
        collection=collection,
        ee_type=EE_PARAMS['type'],
        reducer=EE_PARAMS['reducer'],
        fields=EE_PARAMS['reducer'],
        latitude=site.get('latitude'),
        longitude=site.get('longitude'),
        gadm_id=_site_gadm_id(site),
        boundary=site.get('boundary')
    ).get(EE_PARAMS['reducer'])
    return None if value is None else round(value)


def _run_content(site: dict, term_id: str, collection: str):
    value = find_existing_measurement(TERM_ID, site) or _download(site, collection)
    return [_measurement(term_id, value)] if value else []


def _run_all(site: dict, models: List[str]):
    other_models = list(filter(lambda model: TERM_IDS[model] is not None, models))
    measurements = reduce(
        lambda prev, term_id: prev + _run_content(site, term_id, TERM_IDS[term_id]),
        other_models,
        []
    )
    # if we calculated all but 1 model, it can be calculated without querying GEE
    model_keys = _missing_terms(measurements)
    return measurements + (_run_single(measurements, model_keys[0]) if len(model_keys) == 1 else [])


def _run_single(measurements: list, model: str):
    other_models = list(TERM_IDS.keys())
    other_models.remove(model)
    value = reduce(
        lambda prev, curr: prev - measurement_value(find_term_match(measurements, curr, {})),
        other_models,
        100
    )
    return [_measurement(model, value)]


def _missing_terms(measurements: list):
    return list(filter(
        lambda term_id: find_term_match(measurements, term_id, None) is None,
        list(TERM_IDS.keys())
    ))


def _run(site: dict, terms: list):
    measurements = site.get('measurements', [])
    return _run_single(measurements, terms[0]) if len(terms) == 1 else _run_all(site, terms)


def _should_run(site: dict):
    has_coordinates = has_geospatial_data(site)
    missing_terms = _missing_terms(site.get('measurements', []))
    should_run = has_coordinates and len(missing_terms) > 0
    logger.info('model=%s, terms=%s, should_run=%s', MODEL, missing_terms, should_run)
    return should_run, missing_terms


def run(site: dict):
    should_run, missing_terms = _should_run(site)
    return _run(site, missing_terms) if should_run else []
