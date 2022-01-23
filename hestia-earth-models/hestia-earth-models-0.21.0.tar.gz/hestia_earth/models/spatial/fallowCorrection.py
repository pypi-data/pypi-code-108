from hestia_earth.schema import MeasurementStatsDefinition

from hestia_earth.models.log import logger
from hestia_earth.models.utils.measurement import _new_measurement
from hestia_earth.models.utils.site import valid_site_type
from .utils import download, find_existing_measurement, has_geospatial_data, _site_gadm_id
from . import MODEL

TERM_ID = 'fallowCorrection'
EE_PARAMS = {
    'type': 'raster',
    'reducer': 'mean'
}


def _measurement(value: float):
    logger.info('model=%s, term=%s, value=%s', MODEL, TERM_ID, value)
    measurement = _new_measurement(TERM_ID, MODEL)
    measurement['value'] = [round(value, 7)]
    measurement['statsDefinition'] = MeasurementStatsDefinition.SPATIAL.value
    return measurement


def _download(site: dict):
    # 1) extract maximum monthly growing area (MMGA)
    MMGA_value = download(
        collection='MMGA',
        ee_type=EE_PARAMS['type'],
        reducer=EE_PARAMS['reducer'],
        fields=EE_PARAMS['reducer'],
        latitude=site.get('latitude'),
        longitude=site.get('longitude'),
        gadm_id=_site_gadm_id(site),
        boundary=site.get('boundary')
    )
    MMGA_value = MMGA_value.get(EE_PARAMS['reducer'], 0)

    # 2) extract cropping extent (CE)
    CE_value = download(
        collection='CE',
        ee_type=EE_PARAMS['type'],
        reducer=EE_PARAMS['reducer'],
        fields=EE_PARAMS['reducer'],
        latitude=site.get('latitude'),
        longitude=site.get('longitude'),
        gadm_id=_site_gadm_id(site),
        boundary=site.get('boundary')
    )
    CE_value = CE_value.get(EE_PARAMS['reducer'])

    # 3) estimate fallowCorrection from MMGA and CE.
    return None if MMGA_value == 0 or CE_value is None else min(6, max(CE_value / MMGA_value, 1))


def _run(site: dict):
    value = find_existing_measurement(TERM_ID, site) or _download(site)
    return [_measurement(value)] if value else []


def _should_run(site: dict):
    should_run = has_geospatial_data(site) and valid_site_type(site)
    logger.info('model=%s, term=%s, should_run=%s', MODEL, TERM_ID, should_run)
    return should_run


def run(site: dict): return _run(site) if _should_run(site) else []
