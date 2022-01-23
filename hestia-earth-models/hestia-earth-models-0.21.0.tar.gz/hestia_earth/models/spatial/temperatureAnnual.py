from hestia_earth.schema import MeasurementStatsDefinition
from datetime import datetime
from dateutil.relativedelta import relativedelta
from hestia_earth.utils.tools import non_empty_list, safe_parse_date

from hestia_earth.models.log import logger
from hestia_earth.models.utils.measurement import _new_measurement
from hestia_earth.models.utils.site import related_cycles
from .utils import download, find_existing_measurement, has_geospatial_data, _site_gadm_id
from . import MODEL

TERM_ID = 'temperatureAnnual'
EE_PARAMS = {
    'collection': 'ECMWF/ERA5/MONTHLY',
    'type': 'raster_by_period',
    'reducer': 'mean',
    'band_name': 'mean_2m_air_temperature'
}
BIBLIO_TITLE = 'ERA5: Fifth generation of ECMWF atmospheric reanalyses of the global climate'
KELVIN_0 = 273.15


def _cycle_year(cycle: dict):
    date = safe_parse_date(cycle.get('endDate'))
    return date.year if date else None


def _cycle_valid(year: int):
    # NOTE: Currently uses the climate data for the final year of the study
    # see: https://developers.google.com/earth-engine/datasets/catalog/ECMWF_ERA5_MONTHLY
    # ERA5 data is available from 1979 to three months from real-time
    limit_upper = datetime.now() + relativedelta(months=-3)
    return 1979 <= year and year <= limit_upper.year


def _measurement(value: float, year: int):
    logger.info('model=%s, term=%s, value=%s, year=%s', MODEL, TERM_ID, value, year)
    measurement = _new_measurement(TERM_ID, MODEL, BIBLIO_TITLE)
    measurement['value'] = [value]
    measurement['startDate'] = f"{year}-01-01"
    measurement['endDate'] = f"{year}-12-31"
    measurement['statsDefinition'] = MeasurementStatsDefinition.SPATIAL.value
    return measurement


def _to_celcius(kelvin_value: int): return kelvin_value - KELVIN_0 if kelvin_value else None


def _download(site: dict, year: int):
    return download(
        collection=EE_PARAMS['collection'],
        ee_type=EE_PARAMS['type'],
        band_name=EE_PARAMS['band_name'],
        reducer=EE_PARAMS['reducer'],
        year=str(year),
        latitude=site.get('latitude'),
        longitude=site.get('longitude'),
        gadm_id=_site_gadm_id(site),
        boundary=site.get('boundary')
    ).get(EE_PARAMS['reducer'], 0)


def _run(site: dict, year: int):
    value = find_existing_measurement(TERM_ID, site, year) or _to_celcius(_download(site, year))
    return _measurement(value, year) if value else None


def _should_run(site: dict, year: int):
    should_run = _cycle_valid(year) and has_geospatial_data(site)
    logger.info('model=%s, term=%s, should_run=%s', MODEL, TERM_ID, should_run)
    return should_run


def run(site: dict):
    cycles = related_cycles(site.get('@id'))
    logger.info('model=%s, term=%s, related_cycles=%s', MODEL, TERM_ID, ','.join(map(lambda c: c.get('@id'), cycles)))
    years = non_empty_list(set(map(_cycle_year, cycles)))
    years = list(filter(lambda year: _should_run(site, year), years))
    logger.info('model=%s, term=%s, years=%s', MODEL, TERM_ID, years)
    return non_empty_list(map(lambda year: _run(site, year), years))
