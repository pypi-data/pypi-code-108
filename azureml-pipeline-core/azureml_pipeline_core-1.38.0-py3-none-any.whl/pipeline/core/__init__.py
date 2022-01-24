# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains core functionality for Azure Machine Learning pipelines, which are configurable machine learning workflows.

Azure Machine Learning pipelines allow you to create resusable machine learning workflows that can be used as a
template for your machine learning scenarios. This package contains the core functionality for working with
Azure ML pipelines and is typically used along with the classes in the :mod:`azureml.pipeline.steps`
package.

A machine learning pipeline is represented by a collection of :class:`azureml.pipeline.core.PipelineStep` objects
that can sequenced and parallelized, or be created with explicit dependencies between steps. Pipeline steps are
used to define a :class:`azureml.pipeline.core.Pipeline` object which represents the workflow to execute.
You can create and work with pipelines in a Jupyter Notebook or any other IDE with the Azure ML SDK installed.

Azure ML pipelines enable you to focus on machine learning rather than infrastructure. To get started building
a pipeline, see https://aka.ms/pl-first-pipeline.

For more information about the benefits of the Machine Learning Pipeline and how it is related to other
pipelines offered by Azure, see [What are ML pipelines in Azure Machine Learning
service?](https://docs.microsoft.com/azure/machine-learning/concept-ml-pipelines)
"""
from .builder import PipelineStep, PipelineData, StepSequence
from .pipeline import Pipeline
from .graph import PublishedPipeline, PortDataReference, OutputPortBinding, InputPortBinding, TrainingOutput
from .graph import PipelineParameter, PipelineDataset
from .schedule import Schedule, ScheduleRecurrence, TimeZone
from .pipeline_endpoint import PipelineEndpoint
from .module import Module, ModuleVersion, ModuleVersionDescriptor
from .run import PipelineRun, StepRun, StepRunOutput
from .pipeline_draft import PipelineDraft

__all__ = ["InputPortBinding",
           "Module",
           "ModuleVersion",
           "ModuleVersionDescriptor",
           "OutputPortBinding",
           "Pipeline",
           "PipelineData",
           "PipelineDataset",
           "PipelineDraft",
           "PipelineEndpoint",
           "PipelineParameter",
           "PipelineRun",
           "PipelineStep",
           "PortDataReference",
           "PublishedPipeline",
           "Schedule",
           "ScheduleRecurrence",
           "StepRun",
           "StepRunOutput",
           "StepSequence",
           "TimeZone",
           "TrainingOutput"
           ]
