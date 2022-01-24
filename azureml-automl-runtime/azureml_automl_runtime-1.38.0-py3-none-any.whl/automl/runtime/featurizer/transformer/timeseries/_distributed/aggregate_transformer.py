# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Any, Dict, Iterable, List, Tuple

import pandas as pd

from azureml._common._error_definition import AzureMLError
from azureml.automl.core import _codegen_utilities
from azureml.automl.core.shared._diagnostics.automl_error_definitions import TimeseriesGrainAbsentNoDataContext
from azureml.automl.core.shared.exceptions import DataException
from azureml.automl.core.shared.reference_codes import ReferenceCodes

from azureml.automl.runtime.featurizer.transformer.timeseries.\
    forecasting_base_estimator import AzureMLForecastTransformerBase, _GrainBasedStatefulTransformer
from azureml.automl.runtime.featurizer.transformer.timeseries._distributed import distributed_timeseries_util


class AutoMLAggregateTransformer(AzureMLForecastTransformerBase):
    """A transformer to map per grain transformers within a featurization pipeline."""
    def __init__(self, groupby_cols: List[str], mapping: Dict[str, _GrainBasedStatefulTransformer]):
        self._groupby_cols = groupby_cols
        self._mapping = mapping

    def fit(self, X, y=None):
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        dfs = []
        for group, X_group in X.groupby(self._groupby_cols):
            group_pairs = {}
            if not isinstance(group, tuple):
                group = [group]
            for k, v in zip(self._groupby_cols, group):
                group_pairs[k] = v
            desired_tr = distributed_timeseries_util.convert_grain_dict_to_str(group_pairs)
            tr = self._mapping.get(desired_tr)
            if tr is None:
                raise DataException._with_error(AzureMLError.create(
                    TimeseriesGrainAbsentNoDataContext, grain=group,
                    reference_code=ReferenceCodes._DIST_FORECASTING_MISSING_GRAIN)
                )
            dfs.append(tr.transform(X_group))
        return pd.concat(dfs)

    def get_params(self, deep=True):
        params = super().get_params(deep)
        params["groupby_cols"] = self._groupby_cols
        params["mapping"] = self._mapping
        return params

    def __repr__(self) -> str:
        return _codegen_utilities.generate_repr_str(self.__class__, self.get_params(deep=False))

    def _get_imports(self) -> List[Tuple[str, str, Any]]:
        params = self.get_params(deep=False)
        return _codegen_utilities.get_recursive_imports(params)
