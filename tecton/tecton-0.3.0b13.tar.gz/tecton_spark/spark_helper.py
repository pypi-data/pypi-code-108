from dataclasses import dataclass
from typing import List

import py4j.protocol
from pyspark.sql import DataFrame

from tecton_spark.logger import get_logger


logger = get_logger("SparkHelper")


def _get_table_names_recursively(node):
    """Return the list of table names extracted from the Spark's logical plan (tree rooted at node)."""
    try:
        if node.nodeName() == "UnresolvedRelation":
            return [node.tableName()]
        else:
            children = node.children()
            child_nodes = []
            # node and children are Java objects and working with them in Python is really weird.
            # This is the only hacky way I found to traverse the tree.
            for idx in range(children.size()):
                child_nodes.append(children.slice(idx, idx + 1).last())
            tables = []
            for child in child_nodes:
                tables.extend(_get_table_names_recursively(child))
            return tables
    except py4j.protocol.Py4JError as e:
        # Log the error, since this shouldn't happen. However, if for some weird queries the parsing fails,
        # we should try our best to return as many parsed tables as possible.
        logger.error(f"Failed to get table names recursively for node:\n{node}With exception:\n{e}")
        return []


@dataclass
class QueryPlanInfo:
    has_joins: bool
    has_aggregations: bool
    table_names: List[str]


def _has_node(node, name: str):
    if node.nodeName() == name:
        return True
    else:
        children = node.children()
        for idx in range(children.size()):
            if _has_node(children.slice(idx, idx + 1).last(), name):
                return True
    return False


def get_query_plan_info_for_df(df: DataFrame) -> QueryPlanInfo:
    plan = df._jdf.queryExecution().logical()
    table_names = _get_table_names_recursively(plan)
    return QueryPlanInfo(
        table_names=table_names, has_joins=_has_node(plan, "Join"), has_aggregations=_has_node(plan, "Aggregate")
    )
