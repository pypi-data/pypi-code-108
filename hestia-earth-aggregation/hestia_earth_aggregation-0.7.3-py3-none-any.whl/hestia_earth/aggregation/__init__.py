from pkgutil import extend_path
from hestia_earth.utils.tools import current_time_ms
from hestia_earth.schema import NodeType

from .log import logger
from .utils.queries import find_nodes
from .utils.source import get_source
from .utils.term import _is_global
from . import cycle
from . import impact_assessment

__path__ = extend_path(__path__, __name__)


AGGREGATE = {
    NodeType.CYCLE.value: cycle,
    NodeType.IMPACTASSESSMENT.value: impact_assessment
}


def _call_aggregate_by_type(node_type: str, country: dict, *args):
    aggregation = AGGREGATE[node_type]
    is_global = _is_global(country.get('name'))
    return aggregation.aggregate_global(country, *args) if is_global else aggregation.aggregate_country(country, *args)


def aggregate(type: NodeType, country: dict, product: dict, start_year: int, end_year: int, source: dict):
    """
    Aggregates data from Hestia.
    Produced data will be aggregated by product, country and year.

    Parameters
    ----------
    type: NodeType
        The type of Node to aggregate. Can be either: `NodeType.IMPACTASSESSMENT`, `NodeType.CYCLE`.
    country: dict
        The country to group the data.
    product: dict
        The product to group the data.
    start_year: int
        The start year of the data.
    end_year: int
        The end year of the data.
    source: dict
        Optional - the source of the generate data. Will be set to Hestia if not provided.

    Returns
    -------
    list
        A list of aggregations.
        Example: `[<impact_assesment1>, <impact_assesment2>, <cycle1>, <cycle2>]`
    """
    now = current_time_ms()

    node_type = type if isinstance(type, str) else type.value

    nodes = find_nodes(node_type, product.get('name'), start_year, end_year, country.get('name'))
    aggregations = _call_aggregate_by_type(
        node_type, country, product, nodes, source or get_source(), start_year, end_year
    ) if len(nodes) > 0 else []

    logger.info('time=%s, unit=ms', current_time_ms() - now)

    return aggregations
