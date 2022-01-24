# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Contains packages, modules and classes for AutoML forecasting package."""

import os
import sys

deep4cast_pkg = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..", "Deep4Cast"))
forecast_pkg = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..", "forecast"))
sys.path.append(deep4cast_pkg)
sys.path.insert(0, forecast_pkg)

from .forecasters.deepar import ForecasterDeepAr  # noqa E402
from .models.deepar import DeepAr  # noqa E402

__all__ = ['DeepAr', 'ForecasterDeepAr']
