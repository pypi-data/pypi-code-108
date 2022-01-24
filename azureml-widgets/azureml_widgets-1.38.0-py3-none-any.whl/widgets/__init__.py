# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains functionality to view the progress of machine learning training runs in Jupyter Notebooks.

Supported run types include :class:`azureml.pipeline.core.StepRun`, :class:`azureml.pipeline.core.run.PipelineRun`,
:class:`azureml.train.hyperdrive.HyperDriveRun`, and :class:`azureml.train.automl.run.AutoMLRun`. For more
information on supported run types and environments, see :class:`azureml.widgets.RunDetails`.
"""
from .run_details import RunDetails
from .parallel_run_step_details import ParallelRunStepDetails

__all__ = ["RunDetails", "ParallelRunStepDetails"]


def _jupyter_nbextension_paths():
    return [{
        'section': 'notebook',
        'src': 'static',
        'dest': 'azureml_widgets',
        'require': 'azureml_widgets/extension'
    }]
