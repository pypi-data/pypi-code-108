# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Contstants for Tabular Networks."""

FEATURES = "features"
TARGET = "target"

REGRESSION = "regression"
CLASSIFICATION = "classification"


class SharedBlockTypes:
    FC = "fully_connected"
    CONV = "convolutional"
    ALL = {FC, CONV}
