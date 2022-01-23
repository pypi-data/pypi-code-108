from hestia_earth.schema import EmissionJSONLD, EmissionMethodTier, EmissionStatsDefinition
from hestia_earth.utils.model import linked_node

from hestia_earth.aggregation.utils import _aggregated_version
from hestia_earth.aggregation.utils.term import METHOD_MODEL


def _new_emission(term: dict, value: float = None):
    node = EmissionJSONLD().to_dict()
    node['term'] = linked_node(term)
    if value is not None:
        node['value'] = [value]
        node['statsDefinition'] = EmissionStatsDefinition.CYCLES.value
    node['methodModel'] = METHOD_MODEL
    node['methodTier'] = EmissionMethodTier.TIER_1.value
    return _aggregated_version(node, 'term', 'statsDefinition', 'value', 'methodModel', 'methodTier')
