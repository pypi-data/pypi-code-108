# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import cast, Dict, List, Optional, Union
import joblib
import logging
import numpy as np
import os
import pandas as pd
import uuid

from azureml._common._error_definition import AzureMLError
from azureml.core import Model, Run, Workspace, Datastore
from azureml.automl.core.shared import logging_utilities
from azureml.automl.core.shared.exceptions import ClientException, DataErrorException
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (
    ModelNotFound, ModelNotPickleable, InconsistentColumnTypeInTrainValid
)
from azureml.train.automl.runtime._many_models.automl_prs_driver_base import AutoMLPRSDriverBase
from azureml.train.automl.runtime._many_models.train_helper import Arguments
from azureml.automl.runtime.shared import utilities as runtime_utilities
from azureml.train.automl.constants import HTSConstants
from azureml.automl.core.shared.exceptions import DataException
import azureml.train.automl.runtime._hts.hts_events as hts_events
from azureml.automl.core._logging.event_logger import EventLogger
from azureml.train.automl.runtime._hts.hts_graph import Graph
from azureml.train.automl.runtime._hts.hts_node import Node
import azureml.train.automl.runtime._hts.hts_runtime_utilities as hru
from azureml.train.automl._hts.status_record import StatusRecord
from azureml.train.automl.runtime._hts.node_columns_info import NodeColumnsInfo


logger = logging.getLogger(__name__)


class _VocabNotFoundException(Exception):
    """
    An Exception internal to vocabulary not found.

    Note: This should not be used outside of this module.
    """
    pass


class HTSForecastParallelDriver(AutoMLPRSDriverBase):
    def __init__(
            self,
            current_step_run: Run,
            args: Arguments
    ) -> None:
        """
        Init the HTSForecastParallelDriver.

        :param current_step_run: The current run.
        :param args: The pipeline argunments used for Parallel Run Step.
        """
        super(HTSForecastParallelDriver, self).__init__(current_step_run)

        self.graph = cast(Graph, args.hts_graph)
        self.output_path = cast(str, args.output_path)
        self.node_columns_info = cast(Dict[str, NodeColumnsInfo], args.node_columns_info)
        self.event_dim = cast(Dict[str, str], args.event_logger_dim)
        self.event_logger = EventLogger(run=self.current_step_run)

    def try_convert_inference_data(
            self,
            df: pd.DataFrame,
            columns_types:
            Dict[str, np.dtype]
    ) -> pd.DataFrame:
        """
        Try to check the type and convert the type of the inference data with trying data. It will raise BadData if
        the input is inconsistent.

        :param df: The input df.
        :param columns_types: The dict contains columns to types mapping.
        :return: pd.DataFrame
        """
        if not columns_types:
            logger.warn("Receive empty columns types dict. Skipping type conversion now.")
            return df

        for col in df:
            if col not in columns_types:
                self._console_writer.println("{} cannot be found in training data, skipping now...".format(col))
                logger.warn("column not found in training data, skipping now...")
            else:
                old_col_type = df[col].dtype
                if old_col_type != columns_types[col]:
                    try:
                        df[col] = df[col].astype(columns_types[col])
                        self._console_writer.println(
                            "Column {} successfully converted from type {} to {}.".format(
                                col, old_col_type, columns_types[col]))
                    except Exception as e:
                        input_dtype = runtime_utilities._get_column_data_type_as_str(df[col])
                        self._console_writer.println(
                            "Exception when trying to convert a column with inconsistent types: {}".format(e))
                        raise DataException._with_error(
                            AzureMLError.create(
                                InconsistentColumnTypeInTrainValid,
                                target="X",
                                reference_code=ReferenceCodes._HTS_FORECAST_PARALLEL_INCONSISTENT_DATA,
                                column_name=col,
                                train_dtype=columns_types[col],
                                validation_dtype=input_dtype
                            )
                        )
        return df

    def get_model(self, workspace: Workspace, model_name: str) -> Model:
        """
        Get model from workspace given a model name.

        :param workspace: The workspace from which to retrieve the model.
        :param model_name: The name of the model to retrieve.
        :returns: The deserialized model.
        """
        try:
            model_list = Model.list(workspace, name=model_name, latest=True)
            model_path = model_list[0].download(exist_ok=True)
            model = joblib.load(model_path)
            return model
        except IndexError:
            raise DataErrorException._with_error(
                AzureMLError.create(
                    ModelNotFound, model_name=model_name,
                    reference_code=ReferenceCodes._HTS_FORECAST_PARALLEL_GET_MODEL_INDEX_ERROR
                )
            ) from None
        except ImportError as e:
            raise ClientException._with_error(
                AzureMLError.create(
                    ModelNotPickleable, model_name=model_name,
                    reference_code=ReferenceCodes._HTS_FORECAST_PARALLEL_GET_MODEL_IMPORT_ERROR
                )
            ) from e

    def _get_input_source(
            self,
            node: Union[Node, None],
            raw_file_name: Optional[str] = None
    ) -> Union[str, None]:
        """Get the input source. If the raw file name is provided, using it. Else use the node_id."""
        if raw_file_name is not None:
            return raw_file_name
        elif node is not None:
            return node.node_id
        return None

    def forecast_parallel(
            self,
            input_df: pd.DataFrame,
            raw_file_name: Optional[str] = None
    ) -> List[pd.DataFrame]:
        """
        Run driver for ParallelRunStep based forecasts.
        """
        custom_dim = hru.get_additional_logging_custom_dim(HTSConstants.STEP_FORECAST)
        hru.update_log_custom_dimension(custom_dim)
        self.event_logger.log_event(hts_events.HTSForecastStart(self.event_dim))

        workspace = self.current_step_run.experiment.workspace

        status_records = []
        results_dfs = []
        # This groupby is needed if multiple nodes are represented by a single partition.
        # If the input dataset is a partitioned file/tabular dataset, it will be a no-op.
        self.event_logger.log_event(hts_events.HTSForecastGroupBy(self.event_dim))
        if self.graph.training_level == HTSConstants.HTS_ROOT_NODE_LEVEL:
            try:
                results_dfs.append(
                    self.forecast_single_node(
                        input_df, cast(Node, self.graph.root), self.graph, self.node_columns_info, workspace)
                )
                input_source = self._get_input_source(self.graph.root, raw_file_name)
                status_records.append(
                    StatusRecord(
                        [HTSConstants.HTS_ROOT_NODE_NAME],
                        StatusRecord.SUCCEEDED,
                        input_source,
                        HTSConstants.HTS_FILE_RAW_PREDICTIONS
                    )
                )
            except Exception as e:
                logging_utilities.log_traceback(e, logger, is_critical=False)
                status_records.append(
                    StatusRecord(
                        [HTSConstants.HTS_ROOT_NODE_NAME],
                        StatusRecord.FAILED,
                        raw_file_name,
                        None,
                        StatusRecord.get_error_type(e),
                        error_message=str(e)
                    )
                )

        else:
            for _, single_group in input_df.groupby(self.graph.hierarchy_to_training_level):
                node = self.graph.get_training_level_node_by_df_first_row(single_group)

                if node is None:
                    logger.warn("Node not found in graph.")
                    status_records.append(StatusRecord(
                        single_group.values[0].tolist(),
                        StatusRecord.FAILED,
                        raw_file_name,
                        None,
                        error_type=StatusRecord.USER_ERROR,
                        error_message="Node not found in graph. Data was not seen at training time."
                    ))
                    continue
                try:
                    results_dfs.append(
                        self.forecast_single_node(
                            single_group, node, self.graph, self.node_columns_info, workspace)
                    )
                    input_source = self._get_input_source(self.graph.root, raw_file_name)
                    status_records.append(
                        StatusRecord(
                            node.node_parent_name_list,
                            StatusRecord.SUCCEEDED,
                            input_source,
                            HTSConstants.HTS_FILE_RAW_PREDICTIONS
                        )
                    )
                except Exception as e:
                    status_records.append(
                        StatusRecord(
                            node.node_parent_name_list,
                            StatusRecord.FAILED,
                            raw_file_name,
                            None,
                            StatusRecord.get_error_type(e),
                            error_message=str(e)
                        )
                    )

        partial_status_file_name = str(uuid.uuid4()) + HTSConstants.HTS_FILE_PRED_RESULTS_POSTFIX
        hru.dump_object_to_json(status_records, os.path.join(self.output_path, partial_status_file_name))

        self.event_logger.log_event(hts_events.HTSForecastEnd(self.event_dim))

        return results_dfs

    def forecast_single_node(
            self,
            df: pd.DataFrame,
            node: Node,
            graph: Graph,
            node_columns_info: Dict[str, NodeColumnsInfo],
            workspace: Workspace,
    ) -> pd.DataFrame:
        """
        Forecast a single node.

        This method takes a node and dataframe which contains data for a given node and it's children.
        It aggregates the data up to the level of node, retrieves the corresponding model, and forecasts.
        If the forecast is successful, a StatusRecord indicating success is returned. If the forecast
        fails, a StatusRecord indicating failure is returned. A side effect of success is the prediction
        results being written to the output_dir.

        :param df: The dataframe to be used for forecasting.
        :param node: The desired node to forecast on. The data frame should contain data related to children of Node.
        :param graph: The graph related to this run.
        :param node_columns_info: The column info related to this run.
        :param workspace: The workspace containing the registered models associated to this run.
        """
        vocab_dict = node_columns_info[node.node_id].columns_vocabulary if node.node_id in node_columns_info else None
        if vocab_dict is None:
            logger.warn("Failed to find vocabulary for node {}".format(node.node_id))
            raise _VocabNotFoundException("Vocabulary not found.")

        df = self.try_convert_inference_data(df, node_columns_info[node.node_id].columns_types)

        agg_data, _ = graph.aggregate_data_single_group(
            df,
            vocab_dict
        )

        sha_hash = hru.get_model_hash(node.node_parent_name_list)
        model_name = "automl_" + sha_hash
        self._console_writer.println("Retrieving model: {}".format(model_name))
        try:
            model = self.get_model(workspace, model_name)
        except (DataErrorException, ClientException) as e:
            logger.warn("Model not found or failed to deserialize.")
            logging_utilities.log_traceback(e, logger, is_critical=False)
            raise

        try:
            y = None
            if graph.label_column_name in agg_data.columns:
                y = agg_data.pop(graph.label_column_name).values
            pred, x_trans = model.forecast(agg_data, y, ignore_data_errors=True)
            agg_data[HTSConstants.PREDICTION_COLUMN] = pred
            self._console_writer.println("completed model {}".format(model_name))
        except Exception as e:
            logger.warn("Model failed to predict with given data.")
            logging_utilities.log_traceback(e, logger, is_critical=False)
            raise

        return graph.preserve_hts_col_for_df(agg_data, [HTSConstants.PREDICTION_COLUMN, ])

    def run(self, input_data_file: str, output_data_file: str) -> pd.DataFrame:
        """Run method."""
        input_df = self.read_input_data(input_data_file)
        result_list = self.forecast_parallel(input_df, input_data_file)
        if not result_list:
            result_df = self.graph.get_empty_df()
        else:
            result_df = pd.concat(result_list)
        result_df.to_parquet(output_data_file)
        return result_df
