from hestia_earth.schema import InputJSONLD, InputStatsDefinition
from hestia_earth.utils.model import linked_node

from hestia_earth.aggregation.utils import _aggregated_version


def _new_input(term: dict, value: float = None):
    node = InputJSONLD().to_dict()
    node['term'] = linked_node(term)
    if value is not None:
        node['value'] = [value]
        node['statsDefinition'] = InputStatsDefinition.CYCLES.value
    return _aggregated_version(node, 'term', 'statsDefinition', 'value')
