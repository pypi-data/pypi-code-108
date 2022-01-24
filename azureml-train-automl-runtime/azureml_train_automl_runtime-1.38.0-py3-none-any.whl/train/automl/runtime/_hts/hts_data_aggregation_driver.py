# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Any, cast, Dict, List
import json
import os
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer

from azureml.core import Run, Datastore
from azureml.automl.runtime.featurization import data_transformer_utils
from azureml.train.automl.runtime._many_models.automl_prs_driver_base import AutoMLPRSDriverBase
from azureml.train.automl.runtime._many_models.train_helper import Arguments
from azureml.train.automl.constants import HTSConstants
import azureml.train.automl._hts.hts_client_utilities as cu
import azureml.train.automl.runtime._hts.hts_events as hts_events
from azureml.automl.core._logging.event_logger import EventLogger
from azureml.train.automl.runtime._hts.content_hash_vocabulary import ContentHashVocabulary
from azureml.train.automl.runtime._hts.node_columns_info import NodeColumnsInfo
import azureml.train.automl.runtime._hts.hts_runtime_utilities as hru
from azureml.automl.core.constants import FeatureType
from azureml.automl.runtime.column_purpose_detection import ColumnPurposeDetector
from azureml.train.automl.runtime._hts.hts_graph import Graph


class HTSDataAggregationDriver(AutoMLPRSDriverBase):
    def __init__(
            self,
            current_step_run: Run,
            args: Arguments,
            automl_settings: Dict[str, Any]
    ):
        """
        This class is used for doing batch inference.

        :param current_step_run: Current step run object, parent of AutoML run.
        :param args: The arguments for the run.
        :param logger: The logger object.
        """
        super(HTSDataAggregationDriver, self).__init__(current_step_run)

        self.graph = cast(Graph, args.hts_graph)
        self.automl_settings = automl_settings
        self.output_path = cast(str, args.output_path)
        self.target_path = cast(str, args.target_path)
        if self.current_step_run is None:
            self.current_step_run = Run.get_context()
        self.event_dim = cast(Dict[str, str], args.event_logger_dim)
        self.event_logger = EventLogger(run=self.current_step_run)

        workspace = self.current_step_run.experiment.workspace
        self.dstore = workspace.get_default_datastore()

    @staticmethod
    def get_ignored_columns(df: pd.DataFrame, exclude_columns: List[str]) -> Dict[str, str]:
        """
        Get the ingored columns based on the column purpose.

        :param df: The input dataframe
        :param exclude_columns: The e
        :return: The dict mapping the ignored columns and their detected purpose.
        """
        ignored_columns_types_dict = {}  # type: Dict[str, str]
        for col in df.columns:
            if col not in exclude_columns:
                _, feature_type_detected, _ = ColumnPurposeDetector.detect_column_purpose(col, df)
                if feature_type_detected in FeatureType.DROP_SET:
                    ignored_columns_types_dict[col] = feature_type_detected
        return ignored_columns_types_dict

    @staticmethod
    def get_text_column_vocabulary_dict(
            df: pd.DataFrame,
            excluded_group_columns: List[str]
    ) -> Dict[str, ContentHashVocabulary]:
        """
        Get the vocabulary_dict for a text column from count vectorizer.

        :param df: The input dataframe.
        :param excluded_group_columns: The columns that do not need the count vectorizer.
        :return: A dict that mapping column contents to a hashed dictionary.
        """
        excluded_columns_set = set(excluded_group_columns)
        cat_agg_cols = [col for col in df.select_dtypes(['object']).columns if col not in excluded_columns_set]
        column_vocabulary_dict = {}  # Dict[str, Dict[str, int]]
        for col in cat_agg_cols:
            df[col] = hru.fill_na_with_space(df[col])
            hashed_col = df[col].apply(lambda x: ContentHashVocabulary.md5hash(str(x)))
            count_vectorizer = CountVectorizer(
                max_features=HTSConstants.HTS_COUNT_VECTORIZER_MAX_FEATURES, lowercase=False)
            count_vectorizer.fit(hashed_col)
            # The default output is intc object which is not convertible to json
            hash_vocabulary = {k: int(v) for k, v in count_vectorizer.vocabulary_.items()}
            column_vocabulary_dict[col] = ContentHashVocabulary(
                ContentHashVocabulary.get_original_hash_content_dict(
                    hashed_col, df[col], [k for k in hash_vocabulary.keys()]),
                hash_vocabulary
            )
        return column_vocabulary_dict

    def data_aggregation_and_validation(
            self,
            batch_data: pd.DataFrame
    ) -> List[str]:
        """
        Data aggregation and validation driver code.

        :param batch_data: The data needs to be aggregated.
        :param dstore: The datastore to upload the aggregated data.
        :return: A list of data aggregation results.
        """
        custom_dim = hru.get_additional_logging_custom_dim(HTSConstants.STEP_DATA_AGGREGATION_FILEDATASET)
        hru.update_log_custom_dimension(custom_dim)
        self.event_logger.log_event(hts_events.DataAggStart(self.event_dim))
        result_list = []

        forecasting_parameters = cu.get_forecasting_parameters(self.automl_settings)

        self._console_writer.println("Getting RunContext now.")

        self._console_writer.println("Getting the node info now.")
        node = self.graph.get_training_level_node_by_df_first_row_raise_none(batch_data)
        file_extension = ".csv"
        file_name = node.node_id
        agg_file_name = file_name + file_extension
        self._console_writer.println(
            "Working on node id {} and generating input file {}.".format(node.node_id, file_name))

        column_vocabulary_dict = self.get_text_column_vocabulary_dict(
            batch_data, self.graph.agg_exclude_columns)
        columns_types = {
            col: data_type.str for col, data_type in
            data_transformer_utils.get_pandas_columns_types_mapping(batch_data).items()
            if col not in forecasting_parameters.formatted_drop_column_names
        }
        # We only use feature type detected here.
        col_purposes = {
            str(col): ColumnPurposeDetector.detect_column_purpose(col, batch_data)[1]
            for col in batch_data.columns}
        node_column_info = NodeColumnsInfo(node.node_id, column_vocabulary_dict, columns_types, col_purposes)
        # Temporarily add the info the the current node for aggregation purpose.
        node.ignored_columns_types_dict = node_column_info.get_ignored_columns_dict(
            self.graph.agg_exclude_columns)

        self._console_writer.println("Input data with columns {}.".format(batch_data.columns))
        self._console_writer.println(str(batch_data.head(5)))
        self.event_logger.log_event(hts_events.DataAggAggData(self.event_dim))
        aggregate_df, transform_summary = self.graph.aggregate_data_single_group(
            batch_data, column_vocabulary_dict)
        self._console_writer.println("Input data with columns {}.".format(aggregate_df.columns))
        self._console_writer.println(str(aggregate_df.head(5)))
        if self.automl_settings.get('model_explainability', True):
            with open(os.path.join(self.output_path, hru.get_engineered_column_info_name(node.node_id)), 'w') as fp:
                json.dump(transform_summary, fp)
        aggregate_df.to_csv(agg_file_name, index=False)
        self.event_logger.log_event(hts_events.DataAggUpload(self.event_dim))
        self.dstore.upload_files(
            [agg_file_name], target_path=self.target_path + '/', overwrite=True, show_progress=True)

        self._console_writer.println("Deleting temp csv files now.")
        os.remove(agg_file_name)

        self.event_logger.log_event(hts_events.DataAggPropCalc(self.event_dim))
        batch_data_cross_time = hru.abs_sum_target_by_time(
            batch_data, forecasting_parameters.time_column_name, self.graph.label_column_name, self.graph.hierarchy)

        # Same file name as training step can pickup this name
        self._console_writer.println("Output metadata file now.")
        batch_data_cross_time.to_csv(
            os.path.join(self.output_path, hru.get_proportions_csv_filename(file_name)), index=False)

        self._console_writer.println("Output vocabulary json now.")
        hru.dump_object_to_json(
            node_column_info, os.path.join(self.output_path, hru.get_node_columns_info_filename(file_name)))

        result_list.append("{}: done".format(agg_file_name))

        self.event_logger.log_event(hts_events.DataAggEnd(self.event_dim))
        self._console_writer.println("\n\n\n\n")

        return result_list

    def run(self, input_data_file: str, output_data_file: str) -> pd.DataFrame:
        """Run method."""
        input_df = self.read_input_data(input_data_file)
        result_list = self.data_aggregation_and_validation(input_df)
        result_df = pd.DataFrame([result_list])
        result_df.to_csv(output_data_file)
        return result_df
