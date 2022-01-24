# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Base logger class for all the transformers."""
from typing import List, Tuple
from typing import Any, cast, Dict, Optional

import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin

from azureml.automl.core import _codegen_utilities
from azureml.automl.runtime.shared.types import DataSingleColumnInputType, DataInputType


class AutoMLTransformer(BaseEstimator, TransformerMixin):
    """Base logger class for all the transformers."""
    is_distributable = False
    is_separable = False

    def __repr__(self) -> str:
        return _codegen_utilities.generate_repr_str(self.__class__, self.get_params(deep=False))

    def _get_imports(self) -> List[Tuple[str, str, Any]]:
        params = self.get_params(deep=False)
        return _codegen_utilities.get_recursive_imports(params)

    @property
    def operator_name(self) -> Optional[str]:
        """Operator name for the engineering feature names.

        When featurizers have specific functionalities that depend on attributes such as "Mode", "Mean" in case of
        Imputer, we would like to know such details in the Engineered feature names. Therefore, we expose an attribute
        called '_operator_name'. If this attribute exists, we return it. If not, we return None.
        """
        if hasattr(self, '_operator_name'):
            op_name = cast(str, getattr(self, '_operator_name'))
            if not callable(op_name):
                return op_name

        return None

    @property
    def transformer_name(self) -> str:
        """Transform function name for the engineering feature names."""
        return self._get_transformer_name()

    def _get_transformer_name(self) -> str:
        # TODO Remove this and make it abstract
        return self.__class__.__name__

    def __getstate__(self):
        """
        Overridden to remove logger object when pickling.

        :return: this object's state as a dictionary
        """
        state = super(AutoMLTransformer, self).__getstate__()
        newstate = {**state, **self.__dict__}
        newstate["logger"] = None
        return newstate

    def _to_dict(self):
        """
        Create dict from transformer for serialization usage.

        :return: a dictionary
        """
        dct = {"args": [], "kwargs": {}}  # type: Dict[str, Any]
        return dct

    def get_memory_footprint(self, X: DataInputType, y: DataSingleColumnInputType) -> int:
        """
        Obtain memory footprint by adding this featurizer.

        :param X: Input data.
        :param y: Input label.
        :return: Amount of memory taken in bytes.
        """
        # TODO Make this method abstract once we have all featurizers implementing this method.
        return 0

    def transform(self, X: DataInputType) -> np.ndarray:
        raise NotImplementedError()
