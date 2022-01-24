# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module holding the node to column info mapping."""
from typing import Dict, List, cast, Optional
import inspect

import numpy as np

from azureml.automl.core.constants import FeatureType
from azureml.train.automl.runtime._hts.content_hash_vocabulary import ContentHashVocabulary
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.core.shared.reference_codes import ReferenceCodes


class NodeColumnsInfo:
    """Class holding the columns information between node id and columns in the data."""

    def __init__(
            self,
            node_id: str,
            columns_vocabulary: Dict[str, ContentHashVocabulary],
            columns_types_str: Optional[Dict[str, str]] = None,
            columns_purposes: Optional[Dict[str, str]] = None
    ):
        """
        :param node_id: The node id.
        :param columns_vocabulary: The vocabulary of each column.
        :param columns_types_str: The type of each column.
        :param columns_purposes: The dict of column names and their detected purposes.
        """
        self.node_id = node_id
        self.columns_vocabulary = columns_vocabulary
        self.columns_types_str = columns_types_str
        self.columns_purposes = columns_purposes

    def get_ignored_columns_dict(self, exclude_columns: List[str]) -> Dict[str, str]:
        """
        Get the ignored columns based on the column purpose.

        :param exclude_columns: The training exclude columns list
        :return: A dict of columns with their detected purpose that both excluded by the settings and AutoML SDK.
        """
        ignored_columns_types_dict = {}  # type: Dict[str, str]
        if self.columns_purposes is None:
            return ignored_columns_types_dict
        for col, purpose in self.columns_purposes.items():
            if col not in exclude_columns:
                if purpose in FeatureType.DROP_SET:
                    ignored_columns_types_dict[col] = purpose
        return ignored_columns_types_dict

    @staticmethod
    def get_args_list() -> List[str]:
        """Return the list of arguments for this class."""
        return inspect.getfullargspec(NodeColumnsInfo).args[1:]

    @property
    def columns_types(self) -> Dict[str, np.dtype]:
        """Get the converted dtype string."""
        if not self.columns_types_str:
            return {}
        return {col: np.dtype(type_str) for col, type_str in self.columns_types_str.items()}

    def __eq__(self, other: object) -> bool:
        Contract.assert_type(other, "other", NodeColumnsInfo, ReferenceCodes._HTS_NODE_COLUMNS_INFO_TYPE_ERROR)
        other = cast(NodeColumnsInfo, other)
        return self.node_id == other.node_id and \
            self.columns_vocabulary == other.columns_vocabulary and \
            self.columns_types == self.columns_types
