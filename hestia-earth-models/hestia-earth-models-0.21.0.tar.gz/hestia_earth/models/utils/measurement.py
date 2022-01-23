from dateutil import parser
from statistics import mode, mean
from hestia_earth.schema import SchemaType
from hestia_earth.utils.api import download_hestia
from hestia_earth.utils.model import linked_node

from . import _term_id, _include_methodModel, _include_source
from .term import get_lookup_value

# TODO verify those values
MAX_DEPTH = 1000
OLDEST_DATE = '1800'

MEASUREMENT_REDUCE = {
    'mean': lambda value: mean(value),
    'mode': lambda value: mode(value),
    'sum': lambda value: sum(value)
}


def _new_measurement(term, model=None, biblio_title=None):
    node = {'@type': SchemaType.MEASUREMENT.value}
    node['term'] = linked_node(term if isinstance(term, dict) else download_hestia(_term_id(term)))
    return _include_methodModel(_include_source(node, biblio_title), model)


def measurement_value(measurement: dict) -> float:
    term = measurement.get('term', {})
    reducer = get_lookup_value(term, 'arrayTreatment') or 'mean'
    value = measurement.get('value', [])
    is_value_valid = value is not None and isinstance(value, list) and len(value) > 0
    return MEASUREMENT_REDUCE.get(reducer, lambda v: v[0])(value) if is_value_valid else 0


def _measurement_date(measurement: dict): return parser.isoparse(measurement.get('endDate', OLDEST_DATE))


def _distance(measurement: dict, date): return abs((_measurement_date(measurement) - date).days)


def _most_recent_measurements(measurements: list, date: str) -> list:
    closest_date = parser.isoparse(date)
    min_distance = min([_distance(m, closest_date) for m in measurements])
    return list(filter(lambda m: _distance(m, closest_date) == min_distance, measurements))


def _shallowest_measurement(measurements: list) -> dict:
    min_depth = min([m.get('depthUpper', MAX_DEPTH) for m in measurements])
    return next((m for m in measurements if m.get('depthUpper', MAX_DEPTH) == min_depth), {})


def most_relevant_measurement(measurements: list, term_id: str, date: str):
    filtered_measurements = [m for m in measurements if m.get('term', {}).get('@id') == term_id]
    return {} if len(filtered_measurements) == 0 \
        else _shallowest_measurement(_most_recent_measurements(filtered_measurements, date)) \
        if date and len(filtered_measurements) > 1 else filtered_measurements[0]


def most_relevant_measurement_value(measurements: list, term_id: str, date: str, default=None):
    measurement = most_relevant_measurement(measurements, term_id, date)
    return measurement_value(measurement) if measurement else default
