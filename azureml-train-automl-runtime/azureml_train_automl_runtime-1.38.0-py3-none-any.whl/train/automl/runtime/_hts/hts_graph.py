# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Any, Dict, List, Optional, Tuple, Union, cast
import json
import numpy as np
import os
import pandas as pd

from pandas.core.groupby import DataFrameGroupBy
from queue import Queue
from sklearn.feature_extraction.text import CountVectorizer

from azureml.core import Run
from azureml.automl.core.forecasting_parameters import ForecastingParameters
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.train.automl.constants import HTSConstants
from azureml.train.automl.runtime._hts.hts_node import Node
from azureml.train.automl.runtime._hts.content_hash_vocabulary import ContentHashVocabulary
import azureml.train.automl.runtime._hts.hts_runtime_utilities as hru
import azureml.train.automl._hts.hts_client_utilities as cu


class Graph(object):
    def __init__(
            self,
            hierarchy: List[str],
            training_level: str,
            forecasting_parameters: ForecastingParameters,
            label_column_name: str
    ):
        """
        Init a hts graph object.

        :param hierarchy: The hierarchy defined for the graph.
        :param training_level: The training level for the HTS trainings.
        :param forecasting_parameters: The other forecasting related paramters.
        :param label_column_name: The label column name for the forecasting tasks.
        """
        cu.validate_hierarchy_settings(hierarchy, training_level, forecasting_parameters, label_column_name)
        self._hierarchy = hierarchy
        self._training_level = training_level
        self._root = None  # type: Optional[Node]
        self._time_column_name = forecasting_parameters.time_column_name
        self._label_column_name = label_column_name
        self._time_series_id_column_names = forecasting_parameters.formatted_time_series_id_column_names
        self._node_id_lookup_table = {}  # type: Dict[str, Node]

        self.drop_column_names = forecasting_parameters.formatted_drop_column_names

    @property
    def hierarchy(self) -> List[str]:
        """A list of strings represents the hierarchy column names."""
        return self._hierarchy

    @property
    def training_level(self) -> str:
        """Hierarchy training level column names."""
        return self._training_level

    @property
    def hierarchy_to_training_level(self) -> List[str]:
        """All the hierarchy columns from the first one until training level column names(inclusive)."""
        if self._training_level == HTSConstants.HTS_ROOT_NODE_LEVEL:
            return []
        return self._hierarchy[:self._hierarchy.index(self.training_level) + 1]

    @property
    def group_by_columns(self) -> List[str]:
        """The columns that for the group by in the aggregate data method."""
        group_by_columns = self.hierarchy_to_training_level
        group_by_columns.append(self._time_column_name)
        if self._time_series_id_column_names is not None:
            group_by_columns.extend(self._time_series_id_column_names)
        return group_by_columns

    @property
    def agg_exclude_columns(self) -> List[str]:
        """All the columns that won't need to be aggregated."""
        agg_exclude_columns = self.group_by_columns
        if self.drop_column_names is not None:
            agg_exclude_columns.extend(self.drop_column_names)
        agg_exclude_columns.append(self._label_column_name)
        return agg_exclude_columns

    @property
    def label_column_name(self) -> str:
        """The label column name."""
        return self._label_column_name

    @property
    def time_column_name(self) -> str:
        """Return the time column name."""
        return self._time_column_name

    @property
    def root(self) -> Optional[Node]:
        """The root node of the graph."""
        return self._root

    @root.setter
    def root(self, root: Optional[Node]) -> None:
        """Set the root node."""
        self._root = root

    def make_or_update_hierarchy(self, df: pd.DataFrame) -> None:
        """
        Make or update the hierarchy graph based on the input dataframe.

        :param df: The input DataFrame
        """
        if self.root is not None:
            name_lists = [n for n in df.groupby(self.hierarchy).size().index.tolist()]
            for name_list in name_lists:
                self.update_leaf_node_by_name_list(name_list)
        else:
            self._make_hierarchy(df)

    def aggregate_data_single_group(
            self,
            df: pd.DataFrame,
            column_vocabulary_dict: Optional[Dict[str, ContentHashVocabulary]] = None
    ) -> Tuple[pd.DataFrame, Dict[str, str]]:
        """
        Columns aggregation for single hierarchy group.

        :param df: The input dataframe.
        :param column_vocabulary_dict: The column-str vocabulary mapping dict used for transformation.
        :return: The tuple, containing data frame with transformed data and dictionary mapping
                 engineered to original column names.
        """
        all_exclude_columns = self.agg_exclude_columns

        if column_vocabulary_dict is None:
            cat_agg_cols = [col for col in df.select_dtypes(['object']).columns if col not in all_exclude_columns]
        else:
            cat_agg_cols = list(column_vocabulary_dict.keys())
            for col in cat_agg_cols:
                Contract.assert_true(
                    col not in all_exclude_columns,
                    "Column vocabulary should not contain excluded columns.",
                    reference_code=ReferenceCodes._HTS_CAT_COL_EXCLUDED
                )

        mode_columns = []
        # substitute nan with space before group by.
        for col in cat_agg_cols:
            df[col] = hru.fill_na_with_space(df[col])

        dfg = df.groupby(self.group_by_columns)
        node = self.get_training_level_node_by_df_first_row(df)
        if node is not None and node.ignored_columns_types_dict is not None:
            all_exclude_columns.extend(node.ignored_columns_types_dict.keys())

        aggregation_methods = {}

        def sum_with_nan(x):
            # A custom way to sum a numric column that may contain nan.
            # If the entire column is nan return nan, otherwise treat nan as 0
            # and some numeric values.
            if x.isnull().all():
                return pd.Series(np.nan)
            return pd.to_numeric(x).sum(skipna=True)

        # Only include label column if it is present in dataframe.
        # In the case of inference data it may not be present.
        if self._label_column_name in df.columns:
            aggregation_methods[self._label_column_name] = [sum_with_nan]

        for col in df.select_dtypes([np.number]).columns:
            if col in all_exclude_columns:
                continue
            else:
                aggregation_methods[col] = ['min', 'max', 'mean']  # type: ignore
        for col in df.select_dtypes([np.datetime64]).columns:
            if col in all_exclude_columns:
                continue
            else:
                aggregation_methods[col] = ['min', 'max']  # type: ignore
                mode_columns.append(col)

        text_transformed_cols = None
        # Save the transformation summary in the dictionary column -> new_column_names.
        dt_trasform_summary = {}  # type: Dict[str, str]
        if cat_agg_cols:
            text_transformed_cols, dt_trasform_summary = Graph.cat_column_agg_transform_for_single_group(
                dfg, cat_agg_cols, column_vocabulary_dict)

        # If we have aggregation_methods, aggregate those columns
        # otherwise just take the groupby columns to be used for merge with text columns
        # and drop duplicates.
        if aggregation_methods:
            agg_data = dfg.agg(aggregation_methods).reset_index()
            new_columns = []
            for col, method in agg_data.columns:
                new_col_name = Graph.get_combined_column_names(col, method)
                new_columns.append(new_col_name)
                if new_col_name != col:
                    dt_trasform_summary[new_col_name] = col
            agg_data.columns = new_columns
            for col in mode_columns:
                new_col_name = Graph.get_combined_column_names(col, 'mode')
                dt_trasform_summary[new_col_name] = col
                agg_data[new_col_name] = dfg[col].agg(lambda x: x.value_counts().index[0]).reset_index()[col]
        else:
            agg_data = df[self.group_by_columns].drop_duplicates()

        if text_transformed_cols is not None:
            agg_data = pd.merge(agg_data, text_transformed_cols, on=self.group_by_columns)
        return agg_data, dt_trasform_summary

    def forecasting_group_by_levels(self, forecasting_level: str) -> List[str]:
        """
        Get the forecasting group by columns until the forecasting level.

        :param forecasting_level: The forecasting level.
        """
        Contract.assert_true(
            forecasting_level in self.hierarchy or forecasting_level == HTSConstants.HTS_ROOT_NODE_LEVEL,
            message="Forecasting level is not found in hierarchy.",
            target="forecasting_level", reference_code=ReferenceCodes._HTS_GRAPH_FORECASTING_LEVEL_NOT_IN_HIERARCHY)
        if forecasting_level != HTSConstants.HTS_ROOT_NODE_LEVEL:
            group_by_columns = self._hierarchy[:self._hierarchy.index(forecasting_level) + 1]
        else:
            group_by_columns = []
        group_by_columns.append(self._time_column_name)
        if self._time_series_id_column_names is not None:
            group_by_columns.extend(self._time_series_id_column_names)
        return group_by_columns

    def serialize(self) -> Dict[str, Any]:
        """
        Serialize the graph into a json dict.

        :return: Dict[str, Any]
        """
        Contract.assert_non_empty(
            self.root, "graph.root", reference_code=ReferenceCodes._HTS_GRAPH_SERIALIZE_EMPTY_ROOT
        )
        node = cast(Node, self.root)
        node_list = node.serialize()
        return {
            'root': node.node_id,
            'hierarchy': self.hierarchy,
            'training_level': self.training_level,
            'time_column_name': self._time_column_name,
            'time_series_id_column_names': self._time_series_id_column_names,
            'label_column_name': self._label_column_name,
            'drop_column_names': self.drop_column_names,
            'node_list': node_list
        }

    def has_node_by_id(self, node_id: str) -> bool:
        """
        Check whether a graph has a node with node_id.

        :param node_id: The node_id.
        :return: bool
        """
        return node_id in self._node_id_lookup_table

    def get_node_by_id(self, node_id: str) -> Optional[Node]:
        """
        Get the node by id.

        :param node_id: The node id.
        :return: Optional[Node]
        """
        return self._node_id_lookup_table.get(node_id)

    def get_training_level_node_by_df_first_row(self, df: pd.DataFrame) -> Optional[Node]:
        """
        Get the training level node by the first row of the input dataframe.

        :param df: The input dataframe.
        :return: Node
        """
        if self.training_level == HTSConstants.HTS_ROOT_NODE_LEVEL:
            node = self.root
        else:
            node = self._get_node_by_df_first_row(df, self.hierarchy_to_training_level)
        return node

    def get_training_level_node_by_df_first_row_raise_none(self, df: pd.DataFrame) -> Node:
        """
        Get the training level node by the first row of the input dataframe. If None, raise exceptions.

        :param df: The input dataframe.
        :return: Node
        """
        node = self.get_training_level_node_by_df_first_row(df)
        Contract.assert_non_empty(node, "node found from df", ReferenceCodes._HTS_GRAPH_GET_NODE_DF_NOT_NONE)
        return cast(Node, node)

    def get_node_by_name_list_raise_none(self, name_list: List[Any]) -> Node:
        """
        Get node by the name list. If node does not exists, raise exception.

        :param name_list: A list of hierarchy names to the node.
        :return: Node
        """
        node = self._get_node_by_name_list(name_list)
        Contract.assert_non_empty(node, "node", ReferenceCodes._HTS_GRAPH_GET_NODE_NAME_LIST_NOT_NONE)
        return cast(Node, node)

    def get_leaf_node_name_list(self, df_row: pd.Series) -> List[Any]:
        """Get the name list of a leaf node."""
        return [df_row[level] for level in self.hierarchy]

    def get_leaf_nodes_by_node(self, node: Optional[Node]) -> List[Node]:
        """
        Get all the leaf nodes of a node.

        :param node: The target node.
        :return: List[Node]
        """
        Contract.assert_non_empty(node, "node", ReferenceCodes._HTS_GRAPH_GET_LEAF_NODES_BY_NODE)
        node = cast(Node, node)
        nodes_to_search = [node]
        res = []

        if not node.children:
            return [node]

        while nodes_to_search:
            cur_node = nodes_to_search[0]
            nodes_to_search = nodes_to_search[1:] if len(nodes_to_search) > 1 else []
            if cur_node.children:
                for c_node in cur_node.children:
                    nodes_to_search.append(c_node)

            if cur_node.level == self._hierarchy[-1]:
                res.append(cur_node)

        return res

    def update_leaf_node_by_name_list(self, name_list: Union[List[Any], Tuple[Any]]) -> None:
        """
        Add a new leaf node by the node name list.

        :param name_list: The name list down from first level to the leaf level.
        """
        Contract.assert_non_empty(
            self.root, "graph.root", reference_code=ReferenceCodes._HTS_GRAPH_UPDATE_LEAF_EMPTY_ROOT
        )
        Contract.assert_true(
            len(name_list) == len(self._hierarchy), target="name_list", message="Only adding leaf node is supported.",
            reference_code=ReferenceCodes._HTS_GRAPH_ADDING_NOT_LEAF_NODE
        )
        node = cast(Node, self.root)
        for name, level in zip(name_list, self._hierarchy):
            if not node.has_child(name):
                child_node = Node(name, level=level)
                node.add_child(child_node)
                self._node_id_lookup_table[child_node.node_id] = child_node
            node = cast(Node, node.get_child_by_name(name))

    def get_bottom_nodes(self) -> List[Node]:
        """Get all the bottom nodes of the graph."""
        return self.get_nodes_by_level(self.hierarchy[-1])

    def get_all_nodes(self) -> List[Node]:
        """Get all the nodes of the graph."""
        return [node for node in self._node_id_lookup_table.values()]

    def preserve_hts_col_for_df(
            self, input_data: pd.DataFrame, additional_cols: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Preserve the hts relevant cols (time column, time series identifier columns, hierarchy columns to
        training level and additional cols) for df and remove add the aggregation generated columns.

        :param input_data: The input dataframe.
        :param additional_cols: Additional cols.
        :return: pd.DataFrame
        """
        return input_data[self._get_preserved_columns(additional_cols)]

    def get_empty_df(self, additional_cols: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Get a dataframe with only the columns needed for hts graph.

        :param additional_cols: The columns to safely add to group columns.
        :return: The empty data frame consisting from grouping and
                 additional columns.
        """
        return pd.DataFrame(columns=self._get_preserved_columns(additional_cols))

    @staticmethod
    def deserialize(graph_info: Dict[str, Any]) -> 'Graph':
        """
        Deserialize the graph info dict into a graph.

        :param graph_info: The graph info dict.
        """
        # To avoid warning about dropped column names, set drop_column_names
        # parameter only if it is not None or empty.
        forecasting_parameters = ForecastingParameters(
            time_column_name=graph_info['time_column_name'],
            time_series_id_column_names=graph_info.get('time_series_id_column_names'),
        )
        drop_columns = graph_info.get('drop_column_names')
        if drop_columns:
            forecasting_parameters.drop_column_names = drop_columns
        graph = Graph(
            graph_info['hierarchy'], graph_info['training_level'], forecasting_parameters,
            cast(str, graph_info.get('label_column_name'))
        )
        root = Node.deserialize(graph_info['node_list'])
        graph.root = root

        graph._build_node_id_lookup_table(graph.root)
        graph._validate_graph()
        return graph

    @staticmethod
    def cat_column_agg_transform_for_single_group(
            dfg: DataFrameGroupBy,
            str_columns: List[str],
            column_vocabulary_dict: Optional[Dict[str, ContentHashVocabulary]] = None
    ) -> Tuple[pd.DataFrame, Dict[str, str]]:
        """
        Categorical columns aggregation and transformation for single hierarchy group.

        :param dfg: The DataFrameGroupBy.
        :param str_columns: A list of the string columns that needs to be aggregated and transformed.
        :param column_vocabulary_dict: The column-str vocabulary mapping dict used for transformation.
        :return: The tuple, containing data frame with transformed data and dictionary mapping
                 engineered to original column names.
        """
        groupby_df_dict = {}
        for col in str_columns:
            groupby_df_dict[col] = dfg[col].apply(lambda x: " ".join(x)).reset_index()[col]

        # This step is to obtain the columns that doesn't need to do the transformation.
        transformed_df = dfg[str_columns[0]].apply(lambda x: " ".join(x)).reset_index()
        transformed_df.drop(str_columns[0], axis=1, inplace=True)
        transform_summary = {}
        for col, df in groupby_df_dict.items():
            if column_vocabulary_dict and col in column_vocabulary_dict:
                vocabulary = column_vocabulary_dict[col].hash_vocabulary_dict  # type: Optional[Dict[str, int]]
                hash_content_mapping = column_vocabulary_dict[col].hash_content_dict
            else:
                vocabulary = None
                hash_content_mapping = {}
            count_vectorizer = CountVectorizer(
                max_features=HTSConstants.HTS_COUNT_VECTORIZER_MAX_FEATURES, vocabulary=vocabulary, lowercase=False)
            transformed_matrix = count_vectorizer.fit_transform(df).todense()
            for v, i in count_vectorizer.vocabulary_.items():
                content = hash_content_mapping[v] if v in hash_content_mapping else v
                new_column_name = "_{}_{}".format(col, content)
                transform_summary[new_column_name] = col
                transformed_df[new_column_name] = transformed_matrix[:, i]

        return transformed_df, transform_summary

    @staticmethod
    def get_graph_from_artifacts(run: Run, output_dir: str) -> 'Graph':
        """
        Get the graph from run artifacts.

        :param run: The pipeline run.
        :param output_dir: The output dir to hold the download files.
        :return: A hierarchy graph for HTS runs.
        """
        graph_file = os.path.join(output_dir, HTSConstants.GRAPH_JSON_FILE)
        run.download_file(HTSConstants.GRAPH_JSON_FILE, output_dir)
        graph = Graph.get_graph_from_file(graph_file)
        os.remove(graph_file)
        return graph

    @staticmethod
    def get_graph_from_file(graph_file: str) -> 'Graph':
        """
        Get the graph from local json file.

        :param graph_file: The graph json file path.
        :return: A hierarchy graph for HTS runs.
        """
        with open(graph_file) as f:
            graph_json_str = json.load(f)
            graph = Graph.deserialize(graph_json_str)
        return graph

    @staticmethod
    def get_combined_column_names(col: str, method: str) -> str:
        """
        Get the column names with the aggregation method.

        :param col: The column name.
        :param method: The aggregation method.
        :return: str
        """
        if method == "" or method is None or method == 'sum' or method == 'sum_with_nan':
            return col
        else:
            return "{}_{}".format(col, method)

    def _build_node_id_lookup_table(self, root: Optional[Node]) -> None:
        """
        Recursively build the node_id-node look up table.

        :param root: The root node.
        """
        if root is None:
            return
        Contract.assert_true(
            root.node_id not in self._node_id_lookup_table, target='node',
            message="There are duplicated node ids in the graph. "
                    "Please ensure that your graph file is not corrupted and generated by AutoML HTS pipeline.",
            reference_code=ReferenceCodes._HTS_GRAPH_DUPLICATED_NODES
        )
        self._node_id_lookup_table[root.node_id] = root
        for child in root.children:
            self._build_node_id_lookup_table(child)

    def _get_preserved_columns(self, additional_cols: Optional[List[str]] = None) -> List[str]:
        """
        Get the columns needed for graph only.

        :param additional_cols: The columns to safely add to group columns.
        :return: The list of preserved columns
        """
        preserved_columns = [col for col in self.group_by_columns]
        if additional_cols:
            for col in additional_cols:
                if col not in self.group_by_columns:
                    preserved_columns.append(col)
        return preserved_columns

    def _build_graph(self, df: pd.DataFrame, new_levels: List[str]) -> List[Node]:
        """
        Recursively build the graph on each level.

        :param df: The input datafram.
        :param new_levels: The new levels remaining.
        :return: List[Node]
        """
        if len(new_levels) == 0:
            return []

        level = new_levels[0]
        res = []
        for val, grp in df.groupby(level):
            node = Node(val, level=level)
            sub_tree = new_levels[1:] if len(new_levels) > 1 else []
            node.children = self._build_graph(grp, sub_tree)
            res.append(node)
        return res

    def _get_node_by_df_first_row(self, df: pd.DataFrame, groupby_cols: List[str]) -> Optional[Node]:
        """
        Get node by the first row of a dataframe.

        :param df: The input dataframe.
        :param groupby_cols: The columns needs to be extract name list.
        :return: Node
        """
        return self._get_node_by_name_list(df.head(1)[groupby_cols].values.tolist()[0])

    def get_nodes_by_level(self, level: str) -> List[Node]:
        """
        Get the nodes by certain level.

        :param level: The target level.
        :return: List[Node]
        """
        return [
            node for node in self._node_id_lookup_table.values() if node.level == level
        ]

    def _get_node_depth(self, node: Node) -> int:
        """
        Get the node depth.

        :param node: The node.
        :return: int
        """
        if node.parent is None:
            return 0
        else:
            return self._get_node_depth(node.parent) + 1

    def _get_node_by_name_list(self, name_list: List[Any]) -> Optional[Node]:
        """
        Get node by the name list.

        :param name_list: A list of hierarchy names to the node.
        :return: Node
        """
        node = self.root
        for name in name_list:
            if node is None:
                return None
            node = node.get_child_by_name(name)
        return node

    def get_children_of_level(self,
                              node: Node,
                              level: str) -> List[Node]:
        """
        Get the node's children on the given level.

        :param node: the node to search the children for.
        :param level: The level of children.
        :return: the list of (grand)children on the given level.
        """
        if node == self.root:
            # Return all, the nodes on the given level.
            return self.get_nodes_by_level(level)
        if node.level not in self.hierarchy or level not in self.hierarchy:
            return []
        # If we are trying to get the children of higher level then the
        # level of the node, return the empty list.
        if self.hierarchy.index(node.level) >= self.hierarchy.index(level):
            return []
        # Go node by node, while we will not get to the given level.
        child_level = []
        children = Queue()  # type: Queue[Node]
        children.put(node)
        while not children.empty():
            childlist = children.get().children
            for chld in childlist:
                if chld.level == level:
                    child_level.append(chld)
                else:
                    children.put(chld)
        return child_level

    def _make_hierarchy(self, df: pd.DataFrame) -> None:
        """
        Make the hierarchy graph based on the input dataframe.

        :param df: The input dataframe.
        :return:
        """
        root = Node(HTSConstants.HTS_ROOT_NODE_NAME, HTSConstants.HTS_ROOT_NODE_LEVEL)
        root.children = self._build_graph(df, self.hierarchy)

        self._root = root
        self._build_node_id_lookup_table(root)

    def _validate_graph(self):
        """Validate the graph."""
        for node in self._node_id_lookup_table.values():
            if not node.children:
                Contract.assert_true(
                    self._get_node_depth(node) == len(self.hierarchy), target='graph',
                    message="All the leaf node should have same depth the hierarchy.",
                    reference_code=ReferenceCodes._HTS_GRAPH_VALIDATE_GRAPH_DEPTH_ERROR
                )
