# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains modules and classes for exporting run history to TensorBoard logs and launching a TensorBoard instance.

A Tensorboard instance enables you to visualize experiment performance and structure. For machine learning
experiments that natively output TensorBoard logs, create a Tensorboard instance referencing your experiment's run
history. For Azure Machine Learning experiments and other machine learning frameworks that don't natively output
TensorBoard logs, export your run history to Tensorboard log format before visualization. For more
information about using TensorBoard, see [Visualize experiment runs and metrics with TensorBoard and Azure
Machine Learning](https://docs.microsoft.com/azure/machine-learning/how-to-monitor-tensorboard).
"""
from .tensorboard import Tensorboard

__all__ = ["Tensorboard"]
