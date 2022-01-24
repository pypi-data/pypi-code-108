# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains functionality for running reinforcement learning experiments on Azure Machine Learning
and associated configuration.
"""

from ._rl_estimator import ReinforcementLearningEstimator
from ._rl_run import ReinforcementLearningRun
from ._rl_runconfig import ReinforcementLearningConfiguration, WorkerConfiguration
from ._rl_framework import Ray, RLFramework
from azureml._base_sdk_common import __version__ as VERSION
import azureml._base_sdk_common.user_agent as user_agent

__version__ = VERSION

user_agent.append("azureml-contrib-reinforcementlearning", __version__)

__all__ = [
    "ReinforcementLearningEstimator",
    "ReinforcementLearningRun",
    "ReinforcementLearningConfiguration",
    "WorkerConfiguration",
    "Ray",
    "RLFramework"
]
