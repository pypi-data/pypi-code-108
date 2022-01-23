from hestia_earth.schema import MeasurementJSONLD, MeasurementStatsDefinition
from hestia_earth.utils.model import linked_node

from . import _aggregated_version


def _new_measurement(term: dict, value: float = None):
    node = MeasurementJSONLD().to_dict()
    node['term'] = linked_node(term)
    if value is not None:
        node['value'] = [value]
        node['statsDefinition'] = MeasurementStatsDefinition.SITES.value
    return _aggregated_version(node, 'term', 'statsDefinition', 'value')
