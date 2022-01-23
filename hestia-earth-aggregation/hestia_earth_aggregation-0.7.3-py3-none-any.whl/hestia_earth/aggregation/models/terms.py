from functools import reduce
from hestia_earth.utils.tools import flatten, non_empty_list, list_average

from hestia_earth.aggregation.log import logger
from hestia_earth.aggregation.utils import _min, _max, _sd
from hestia_earth.aggregation.utils.term import _blank_node_completeness


def _debugNodes(nodes: list):
    for node in nodes:
        if node.get('yield'):
            logger.debug(
                'id=%s, yield=%s, weight=%s, ratio=%s/%s, organic=%s, irrigated=%s',
                node.get('@id'),
                round(node.get('yield')),
                100/len(nodes),
                1,
                len(nodes),
                node.get('organic'),
                node.get('irrigated')
            )


def _aggregate(nodes: list, completeness: dict):
    first_node = nodes[0]
    term = first_node.get('term')
    completeness_key = _blank_node_completeness(first_node)
    completeness_count = len([node for node in nodes if node.get('dataCompleteness', False)])
    completeness_count_total = completeness.get(completeness_key, 0)
    completeness_count_missing = (
        completeness_count_total - completeness_count
    ) if completeness_count_total > completeness_count else 0
    values = non_empty_list(flatten([node.get('value') for node in nodes])) + (
        # account for complete nodes but which have no values
        [0] * completeness_count_missing
    )
    return {
        'node': first_node,
        'term': term,
        'value': list_average(values),
        'max': _max(values),
        'min': _min(values),
        'sd': _sd(values),
        'observations': len(nodes) + completeness_count_missing
    } if len(values) > 0 else None


def _aggregate_term(aggregates_map: dict, completeness: dict):
    def aggregate(term_id: str):
        blank_nodes = [node for node in aggregates_map.get(term_id, []) if not node.get('deleted')]
        return _aggregate(blank_nodes, completeness) if len(blank_nodes) > 0 else None
    return aggregate


def _aggregate_nodes(aggregate_key: str, index=0):
    def aggregate(data: dict):
        if index == 0:
            _debugNodes(data.get('nodes', []))
        completeness = data.get('dataCompleteness', {})
        terms = data.get(aggregate_key).keys()
        aggregates = non_empty_list(map(_aggregate_term(data.get(aggregate_key), completeness), terms))
        return (aggregates, data) if len(aggregates) > 0 else ([], {})

    def aggregate_multiple(data: dict):
        return reduce(
            lambda prev, curr: {**prev, curr[1]: _aggregate_nodes(curr[1], curr[0])(data)}, enumerate(aggregate_key), {}
        )

    return aggregate if isinstance(aggregate_key, str) else aggregate_multiple


def aggregate(aggregate_key: str, groups: dict) -> list:
    return non_empty_list(map(_aggregate_nodes(aggregate_key), groups.values()))
