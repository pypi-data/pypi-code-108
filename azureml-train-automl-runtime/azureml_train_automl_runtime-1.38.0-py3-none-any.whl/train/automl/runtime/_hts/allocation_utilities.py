# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Any, Callable, Dict, Optional, cast

import pandas as pd

from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.train.automl.constants import HTSConstants
from azureml.train.automl.runtime._hts.hts_graph import Graph
from azureml.train.automl.runtime._hts.hts_node import Node


def disaggregate_predictions(
    preds_df: pd.DataFrame,
    graph: Graph,
    allocation_method: str,
    parsed_metadata: Dict[str, Any],
    disagg_one_node_fun: Callable[..., pd.DataFrame],
    target_level: Optional[str] = None,
) -> pd.DataFrame:
    """
    Disaggregate the model predictions.

    This method takes the model predictions from the training level and disaggregates
    to the leaf nodes. It uses the allocaiton_method and parsed_metadata to determine
    what proportion of predictions to allocate towards each leaf node.

    :param preds_df: Dataframe containing predictions from the training_level.
    :param graph: Graph from the data used for training models used to create preds_df.
    :param allocation_method: Method to use for forecast allocations. Should be present in parsed_metadata.
    :param parsed_metadata: Dictionary containing disaggregation proportions. The schema is assumed to be
        node_id: {allocation_method: allocation_proportion}
    :param target_level: The level, which will be used for disaggregation.
    :param disagg_one_node_fun: The function to be used for disaggregation of a given node.
    :returns: The predictions allocated to the leaf node level.
    """
    partial_res = []
    if graph.training_level == HTSConstants.HTS_ROOT_NODE_LEVEL:
        node = cast(Node, graph.root)
        Contract.assert_non_empty(
            node, "node", reference_code=ReferenceCodes._HTS_ALLOCATION_NOT_FOUND_NODE_TOP_LEVEL
        )
        res = disagg_one_node_fun(preds_df, node, graph, parsed_metadata, allocation_method, target_level)
        partial_res.append(res)
    else:
        for k, grp in preds_df.groupby(graph.hierarchy_to_training_level):
            if not isinstance(k, tuple):
                # if k is a single value this condition is hit.
                k = [k]
            else:
                k = list(k)
            node = graph.get_node_by_name_list_raise_none(k)
            Contract.assert_non_empty(
                node, "node", reference_code=ReferenceCodes._HTS_ALLOCATION_NOT_FOUND_NODE
            )
            res = disagg_one_node_fun(grp, node, graph, parsed_metadata, allocation_method, target_level)
            partial_res.append(res)
    return pd.concat(partial_res, sort=False, ignore_index=True)
