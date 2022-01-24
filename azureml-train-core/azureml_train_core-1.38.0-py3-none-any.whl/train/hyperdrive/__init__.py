# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains modules and classes supporting hyperparameter tuning.

Hyperparameters are adjustable parameters you choose for model training that guide the training process.
The HyperDrive package helps you automate choosing these parameters. For example, you can define the parameter
search space as discrete or continuous, and a sampling method over the search space as random, grid, or Bayesian.
Also, you can specify a primary metric to optimize in the hyperparameter tuning experiment, and whether to minimize
or maximize that metric. You can also define early termination policies in which poorly performing experiment runs
are canceled and new ones started. To define a reusable machine learning workflow for HyperDrive, use
:class:`azureml.pipeline.steps.hyper_drive_step` to create a :class:`azureml.pipeline.core.pipeline.Pipeline`.
"""
from .policy import BanditPolicy, MedianStoppingPolicy, NoTerminationPolicy, TruncationSelectionPolicy, \
    EarlyTerminationPolicy
from .runconfig import HyperDriveRunConfig, HyperDriveConfig, PrimaryMetricGoal
from .run import HyperDriveRun
from .sampling import RandomParameterSampling, GridParameterSampling, BayesianParameterSampling, HyperParameterSampling
from .parameter_expressions import choice, randint, uniform, quniform, loguniform, \
    qloguniform, normal, qnormal, lognormal, qlognormal
from ._search import search
from azureml.core._experiment_method import ExperimentSubmitRegistrar

__all__ = ["BanditPolicy", "BayesianParameterSampling", "EarlyTerminationPolicy", "GridParameterSampling",
           "HyperDriveConfig", "HyperDriveRun", "HyperDriveRunConfig", "HyperParameterSampling",
           "MedianStoppingPolicy", "NoTerminationPolicy", "PrimaryMetricGoal",
           "RandomParameterSampling", "TruncationSelectionPolicy",
           "choice", "lognormal", "loguniform", "normal", "randint",
           "qlognormal", "qloguniform", "qnormal", "quniform", "uniform"]

ExperimentSubmitRegistrar.register_submit_function(HyperDriveRunConfig, search)
ExperimentSubmitRegistrar.register_submit_function(HyperDriveConfig, search)
