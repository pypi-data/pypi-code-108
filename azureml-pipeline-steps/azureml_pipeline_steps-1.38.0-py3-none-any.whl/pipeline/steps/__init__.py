# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains pre-built steps that can be executed in an Azure Machine Learning Pipeline.

Azure ML Pipeline steps can be configured together to construct a Pipeline, which represents a shareable
and reusable Azure Machine Learning workflow. Each step of a pipeline can be configured to allow reuse of
its previous run results if the step contents (scripts and dependencies) as well as inputs and parameters
remain unchanged.

The classes in this package are typically used together with the classes in the
:mod:`azureml.pipeline.core` package. The core package contains classes for configuring data
(:class:`azureml.pipeline.core.PipelineData`), scheduling (:class:`azureml.pipeline.core.Schedule`), and
managing the output of steps (:class:`azureml.pipeline.core.StepRun`).

The pre-built steps in this package cover many common scenarios encountered in machine
learning workflows. To get started with pre-built pipeline steps, see:

* https://aka.ms/pl-first-pipeline

* [Jupyter notebooks on
  GitHub](https://github.com/Azure/MachineLearningNotebooks/tree/master/how-to-use-azureml/machine-learning-pipelines)
"""
from .adla_step import AdlaStep
from .automl_step import AutoMLStep, AutoMLStepRun
from .databricks_step import DatabricksStep
from .data_transfer_step import DataTransferStep
from .python_script_step import PythonScriptStep
from ._hdinsight_step import _HDInsightStep
from .r_script_step import RScriptStep
from .command_step import CommandStep
from .estimator_step import EstimatorStep
from .mpi_step import MpiStep
from .hyper_drive_step import HyperDriveStep, HyperDriveStepRun
from .azurebatch_step import AzureBatchStep
from .module_step import ModuleStep
from .parallel_run_config import ParallelRunConfig
from .parallel_run_step import ParallelRunStep
from .kusto_step import KustoStep
from .synapse_spark_step import SynapseSparkStep

__all__ = ["AdlaStep",
           "AutoMLStep",
           "AutoMLStepRun",
           "AzureBatchStep",
           "DatabricksStep",
           "DataTransferStep",
           "EstimatorStep",
           "_HDInsightStep",
           "HyperDriveStep",
           "HyperDriveStepRun",
           "ModuleStep",
           "MpiStep",
           "ParallelRunConfig",
           "ParallelRunStep",
           "PythonScriptStep",
           "RScriptStep",
           "SynapseSparkStep",
           "CommandStep",
           "KustoStep"
           ]
