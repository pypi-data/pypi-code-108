# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module containing Datatypes."""

from typing import Union

import azureml.dataprep as dprep
import numpy as np
import pandas as pd

DataInputType = Union[pd.DataFrame, dprep.Dataflow]
TargetInputType = Union[DataInputType, np.ndarray, pd.Series]
