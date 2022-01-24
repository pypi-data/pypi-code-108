# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging

from abc import ABC, abstractmethod
from azureml.exceptions import TrainingException
from azureml.core.runconfig import MpiConfiguration, TensorflowConfiguration

_GENERIC_ESTIMATOR_NAME = "Estimator".lower()
_PYTORCH_ESTIMATOR_NAME = "PyTorch".lower()
_TENSORFLOW_ESTIMATOR_NAME = "TensorFlow".lower()
_CHAINER_ESTIMATOR_NAME = "Chainer".lower()
_LIGHTGBM_ESTIMATOR_NAME = "LightGBM".lower()

module_logger = logging.getLogger(__name__)


class _DistributedTraining(ABC):
    def validate(self, estimator_name):
        if estimator_name.lower() not in self._supported_frameworks:
            raise TrainingException("Unsupported framework for {} distributed training type. Supported frameworks "
                                    "are: {}".format(self.__class__.__name__, self._supported_frameworks))

    def _get_communicator(self):
        return self.__class__.__name__

    @abstractmethod
    def _get_framework(self):
        pass

    @abstractmethod
    def __str__(self):
        pass


class Mpi(_DistributedTraining):
    """Manages Message Passing Interface (MPI) settings for distributed training jobs.

    DEPRECATED. Use the :class:`azureml.core.runconfig.MpiConfiguration` class.

    MPI can be specified for a job with the ``distributed_training`` parameter of preconfigured estimators
    :class:`azureml.train.dnn.Chainer`, :class:`azureml.train.dnn.PyTorch`, and
    :class:`azureml.train.dnn.TensorFlow`, or with a generic
    :class:`azureml.train.estimator.Estimator`.

    :param process_count_per_node: The number of processes (or "workers") to run on each node.
    :type process_count_per_node: int
    """
    _supported_frameworks = [_PYTORCH_ESTIMATOR_NAME, _TENSORFLOW_ESTIMATOR_NAME,
                             _CHAINER_ESTIMATOR_NAME.lower(), _GENERIC_ESTIMATOR_NAME, _LIGHTGBM_ESTIMATOR_NAME]

    def __init__(self, process_count_per_node=1):
        """A class for managing MPI settings for jobs.

        :param process_count_per_node: When using MPI, number of processes per node.
        :type process_count_per_node: int
        """
        module_logger.warning("'Mpi' is deprecated. Please use "
                              "'azureml.core.runconfig.MpiConfiguration' with 'ScriptRunConfig' "
                              "from 'azureml.core.runconfig'.")
        self.process_count_per_node = process_count_per_node

    def _get_framework(self):
        return "python"

    def _get_configuration(self):
        mpi_config = MpiConfiguration()
        mpi_config.process_count_per_node = self.process_count_per_node
        return mpi_config

    def __str__(self):
        return "mpi"


class ParameterServer(_DistributedTraining):
    """Manages Parameter Server settings for training jobs.

    DEPRECATED. Use the :class:`azureml.core.runconfig.TensorflowConfiguration` class.

    :param worker_count: The number of work tasks.
    :type worker_count: int
    :param parameter_server_count: The number of parameter server tasks.
    :type parameter_server_count: int
    """

    _supported_frameworks = [_TENSORFLOW_ESTIMATOR_NAME, _GENERIC_ESTIMATOR_NAME]

    def __init__(self, worker_count=1, parameter_server_count=1):
        """A class for managing parameter server settings for jobs.

        DEPRECATED. Use the :class:`azureml.core.runconfig.TensorflowConfiguration` class.

        :param worker_count: The number of work tasks.
        :type worker_count: int
        :param parameter_server_count: The number of parameter server tasks.
        :type parameter_server_count: int
        """
        self.worker_count = worker_count
        self.parameter_server_count = parameter_server_count
        module_logger.warning("'ParameterServer' is deprecated. Use the "
                              ":class:`azureml.core.runconfig.TensorflowConfiguration` class.")

    def _get_framework(self):
        return _TENSORFLOW_ESTIMATOR_NAME

    def _get_configuration(self):
        ps_config = TensorflowConfiguration()
        ps_config.worker_count = self.worker_count
        ps_config.parameter_server_count = self.parameter_server_count
        return ps_config

    def __str__(self):
        return "ps"


class Gloo(_DistributedTraining):
    """Manages Gloo settings for distributed training jobs.

    DEPRECATED. Use the :class:`azureml.core.runconfig.PyTorchConfiguration` class.

    Gloo can be specified for a training job with the ``distributed_training`` parameter of the
    preconfigured :class:`azureml.train.dnn.PyTorch` estimator or any generic
    :class:`azureml.train.estimator.Estimator` supporting Gloo.
    """
    _supported_frameworks = [_PYTORCH_ESTIMATOR_NAME, _GENERIC_ESTIMATOR_NAME]

    def __init__(self):
        """A class for managing Gloo settings for jobs."""
        module_logger.warning("'Gloo' is deprecated. Please use "
                              "'azureml.core.runconfig.PyTorchConfiguration' with 'ScriptRunConfig' "
                              "from 'azureml.core.runconfig, and set the 'PyTorchConfiguration' "
                              "'communication_backend' parameter to 'Gloo'.")
        pass

    def _get_framework(self):
        return _PYTORCH_ESTIMATOR_NAME

    def __str__(self):
        return "gloo"


class Nccl(_DistributedTraining):
    """Manages Nccl settings for distributed training jobs.

    DEPRECATED. Use the :class:`azureml.core.runconfig.PyTorchConfiguration` class.

    Nccl can be specified for a training job with the ``distributed_training`` parameter of the
    preconfigured :class:`azureml.train.dnn.PyTorch` estimator or any generic
    :class:`azureml.train.estimator.Estimator` supporting Nccl.
    """
    _supported_frameworks = [_PYTORCH_ESTIMATOR_NAME, _GENERIC_ESTIMATOR_NAME]

    def __init__(self):
        """A class for managing Nccl settings for jobs."""
        module_logger.warning("'Nccl' is deprecated. Please use "
                              "'azureml.core.runconfig.PyTorchConfiguration' with 'ScriptRunConfig' "
                              "from 'azureml.core.runconfig, and set the 'PyTorchConfiguration' "
                              "'communication_backend' parameter to 'Nccl'.")
        pass

    def _get_framework(self):
        return _PYTORCH_ESTIMATOR_NAME

    def __str__(self):
        return "nccl"
