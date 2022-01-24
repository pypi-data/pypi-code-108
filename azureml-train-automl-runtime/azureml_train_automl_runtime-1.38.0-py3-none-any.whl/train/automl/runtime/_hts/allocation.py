# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Any, cast, Dict, List, Optional, Tuple

import json
import logging
import os
import pandas as pd
import sys

from azureml.core import Run
from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared._diagnostics.automl_error_definitions import HierarchyPredictionsNotFound
from azureml.automl.core.shared.exceptions import ClientException
from azureml.automl.core.console_writer import ConsoleWriter
from azureml.train.automl.constants import HTSConstants
from azureml.train.automl.runtime._hts import allocation_utilities
from azureml.automl.core._logging.event_logger import EventLogger
import azureml.train.automl.runtime._hts.hts_events as hts_events
from azureml.train.automl.runtime._hts.hts_graph import Graph
from azureml.train.automl.runtime._hts.hts_node import Node
from azureml.train.automl._hts import hts_client_utilities as hcu
import azureml.train.automl.runtime._hts.hts_runtime_utilities as hru
from azureml.train.automl._hts.status_record import StatusRecord
from azureml.train.automl._hts import hts_json_serializer
from azureml.train.automl.runtime._many_models.automl_pipeline_step_wrapper import AutoMLPythonStepWrapper


logger = logging.getLogger(__name__)
console_writer = ConsoleWriter(sys.stdout)


class AllocationWrapper(AutoMLPythonStepWrapper):
    """The wrapper code for allocation runs."""
    def __init__(self, current_step_run: Optional[Run] = None):
        """
        The wrapper code for allocation runs.

        :param current_step_run: The current step run.
        """
        super(AllocationWrapper, self).__init__(
            HTSConstants.STEP_ALLOCATION, current_step_run
        )

    def _run(self) -> None:
        """Run code for the allocation driver."""
        allocation_driver(self.step_run, self.arguments_dict, self.event_logger)


def allocation_driver(current_step_run: Run, arguments_dict: Dict[str, Any], event_logger: EventLogger) -> None:
    """
    Allocation driver for python script steps.

    This method should be called from a python script step, used in conjunction with forecast_parallel.
    This method will take predictions at the training level produced by calling forecast_parallel,
    and allocate the predictions ensuring predictions are always coherent, no matter the forecast level.

    Rather than returning the allocated predictions, this method writes them to the output directory,
    as specified in the arguments_dict.

    :param current_step_run: The step run executing this method.
    :param arguments_dict: The arguments used for this script.
    :param event_logger: The event logger.
    :returns: None.
    """
    custom_dim = hru.get_additional_logging_custom_dim(HTSConstants.STEP_ALLOCATION)
    hru.update_log_custom_dimension(custom_dim)
    event_logger_additional_fields = hru.get_event_logger_additional_fields(custom_dim, current_step_run.parent.id)
    event_logger.log_event(hts_events.HTSAllocationStart(event_logger_additional_fields))
    parent_run = hru.get_pipeline_run(current_step_run)
    parent_run.add_properties({HTSConstants.HTS_PROPERTIES_RUN_TYPE: HTSConstants.HTS_PROPERTIES_INFERENCE})

    forecasting_level = arguments_dict[HTSConstants.FORECAST_LEVEL]
    allocation_method = arguments_dict[HTSConstants.ALLOCATION_METHOD]
    forecast_path = arguments_dict[HTSConstants.RAW_FORECASTS]
    training_run_id = arguments_dict[HTSConstants.TRAINING_RUN_ID]
    output = arguments_dict[HTSConstants.OUTPUT_PATH]

    training_run = hcu.get_training_run(training_run_id, current_step_run.experiment, parent_run)
    graph = Graph.get_graph_from_artifacts(training_run, ".")

    event_logger.log_event(hts_events.HTSAllocationProcess(event_logger_additional_fields))
    os.makedirs(output, exist_ok=True)
    preds_df, pred_results = process_input_data(forecast_path)
    parse_store_results(current_step_run, pred_results, output)
    logger.info("Successfully retrieved raw forecasts.")

    parsed_metadata = hru.get_parsed_metadata_from_artifacts(training_run, ".")
    logger.info("Successfully retrieved leaf node metadata.")

    event_logger.log_event(hts_events.HTSAllocationPredict(event_logger_additional_fields))

    # Skip disaggregation if forecast level is above training level and not the root level
    disaggregation_needed = (
        forecasting_level not in graph.hierarchy_to_training_level and
        forecasting_level != HTSConstants.HTS_ROOT_NODE_LEVEL
    )

    if disaggregation_needed:
        logger.info("Forecast level below training level, disaggregating to leaf nodes.")
        preds_df = allocation_utilities.disaggregate_predictions(
            preds_df, graph, allocation_method,
            parsed_metadata, add_children_to_df)
    else:
        logger.info("Forecast level above current allocation level, no disaggregation required.")

    # If the forecast level is equal to the training level, or the forecast level is the leaf node level,
    # no aggregation is required.
    aggregation_needed = forecasting_level != graph.training_level and forecasting_level != graph.hierarchy[-1]
    desired_columns = graph.forecasting_group_by_levels(forecasting_level)
    if aggregation_needed:
        logger.info("Forecast level is above current allocated forecast level, beginning aggregation.")
        res = preds_df.groupby(desired_columns).sum().reset_index()
    else:
        logger.info("Forecast level is at current allocated forecast level.")
        res = preds_df

    res = res[desired_columns + [HTSConstants.PREDICTION_COLUMN]]
    results_file = os.path.join(output, HTSConstants.HTS_FILE_PREDICTIONS)
    res.to_csv(results_file, index=False)
    event_logger.log_event(hts_events.HTSAllocationEnd(event_logger_additional_fields))


def parse_store_results(run: Run, pred_results: List[StatusRecord], output_path: str) -> None:
    """
    Check the collected prediction results and store collected results in output.

    This method checks the prediciton results and adds a warning if any predictions
    failed in the previous step. It also stores the results file to the output path.

    :param run: The run to be used if any failures are found. Warnings will be written to the run.
    :param pred_results: A list of StatusRecords.
    :param output_path: Path to store the output.

    """
    fail_count = 0
    for record in pred_results:
        if record.status == StatusRecord.FAILED:
            console_writer.println(
                "Predictions with data: {} failed with exception: {}".format(record.data, record.error_message)
            )
            logger.warning(
                "Failed prediction record found."
            )
            fail_count += 1

    if fail_count:
        run._client.run.post_event_warning(
            "Run",
            "{} group(s) failed during prediction. Forecasts may not be coherent."
            " Check {} for detailed failures.".format(fail_count, HTSConstants.HTS_FILE_PRED_RESULTS)
        )

    # write all prediction results to single file
    output_file = os.path.join(output_path, HTSConstants.HTS_FILE_PRED_RESULTS)
    with open(output_file, "w") as f:
        json.dump(pred_results, f, indent=4, cls=hts_json_serializer.HTSEncoder)
    run.upload_file(HTSConstants.HTS_FILE_RUN_INFO_JSON, output_file)
    hru.check_parallel_runs_status(pred_results, HTSConstants.STEP_FORECAST, HTSConstants.HTS_FILE_RUN_INFO_JSON)


def process_input_data(input_path: str) -> Tuple[pd.DataFrame, List[StatusRecord]]:
    """
    Process files from input file path.

    This method processes the intermediate files from file path and
    reads them into memory. It can handle files ending with known
    postfix [HTS_FILE_PRED_RESULTS_POSTFIX] or prediction file. If the prediction file
    is missing it will raise an exception.

    :param input_path: The path from where the data lives.
    :returns: A tuple consisting of the processed data and status records.
    """
    pred_results = []
    full_df = pd.DataFrame()
    if HTSConstants.HTS_FILE_RAW_PREDICTIONS not in os.listdir(input_path):
        raise ClientException._with_error(
            AzureMLError.create(HierarchyPredictionsNotFound)
        )

    for data_file in os.listdir(input_path):
        logger.info("processing: {}".format(data_file))
        if data_file.endswith(HTSConstants.HTS_FILE_PRED_RESULTS_POSTFIX):
            # collect prediction result files
            with open(os.path.join(input_path, data_file), "r") as f:
                pred_results += json.load(f, cls=hts_json_serializer.HTSDecoder)
        elif data_file == HTSConstants.HTS_FILE_RAW_PREDICTIONS:
            full_df = pd.read_csv(os.path.join(input_path, data_file), sep=" ")

    return full_df, pred_results


def add_children_to_df(
    df: pd.DataFrame,
    node: Node,
    graph: Graph,
    parsed_metadata: Dict[str, Any],
    allocation_method: str,
    target_level: str,
) -> pd.DataFrame:
    """
    Add bottom level nodes to the dataframe.

    This method takes a node and dataframe, and creates duplicate copies of the dataframe with the entire
    hierarchy from node to leaf nodes included.
    """
    results = []
    # If training index is root, well add the entire hierarchy
    # otherwise we only need to update the nodes from training to leaf.
    cols_to_update = len(graph.hierarchy)
    if graph.training_level != HTSConstants.HTS_ROOT_NODE_LEVEL:
        cols_to_update -= graph.hierarchy.index(graph.training_level)

    logger.info("retrieving children for node: {}".format(node.node_id))
    children = graph.get_leaf_nodes_by_node(node)
    parent_allocation = sum([parsed_metadata[child.node_id][allocation_method] for child in children])

    if children:
        for child in children:
            # Update all our predictions so all leaf nodes are represented.
            c_pred = df.copy(deep=True)
            runner = child
            for i in range(cols_to_update):
                # Update the hierarchy with of each leaf node with
                # the child's relative tree path up to training level.
                c_pred[runner.level] = runner.name
                runner = cast(Node, runner.parent)
            allocation_proportion = parsed_metadata[child.node_id][allocation_method] / parent_allocation
            # As we calculate the proportions in the training part by normalized to the root level,
            # renormalization is needed for all the child nodes of the interested nodes to ensure the
            # proportion is correct in the sub tree of the leaf nodes.
            c_pred[HTSConstants.PREDICTION_COLUMN] = c_pred[HTSConstants.PREDICTION_COLUMN] * allocation_proportion

            results.append(
                c_pred[[HTSConstants.PREDICTION_COLUMN] + graph.forecasting_group_by_levels(graph.hierarchy[-1])]
            )
        logger.info("Updated predictions for {} children.".format(len(children)))
    return pd.concat(results)
