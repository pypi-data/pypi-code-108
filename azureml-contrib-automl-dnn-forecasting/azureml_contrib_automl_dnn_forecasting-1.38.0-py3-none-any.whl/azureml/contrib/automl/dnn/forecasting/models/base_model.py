# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""The base class for all DNN forecasting models."""

import numpy as np
import torch


class BaseModel(torch.nn.Module):
    """Base class for all models."""

    def __init__(self):
        """Init."""
        super().__init__()

    @property
    def n_parameters(self):
        """Return the number of model parameters."""
        par = list(self.parameters())
        s = sum([np.prod(list(d.size())) for d in par])
        return s
