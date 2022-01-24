# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import TypeVar, Union

import pandas as pd

import azureml.dataprep as dprep
from .lazy_tabular_data import LazyTabularData
from .materialized_tabular_data import MaterializedTabularData

DataFrameLike = TypeVar("DataFrameLike", pd.DataFrame, dprep.Dataflow)
TabularData = Union[LazyTabularData, MaterializedTabularData]
