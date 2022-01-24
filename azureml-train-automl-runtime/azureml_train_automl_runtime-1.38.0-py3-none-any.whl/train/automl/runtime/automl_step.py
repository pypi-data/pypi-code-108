# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""DEPRECATED. Use the functionality in the :mod:`azureml.pipeline.steps.automl_step` module."""


class AutoMLStep:
    """DEPRECATED. Use the :class:`azureml.pipeline.steps.automl_step.AutoMLStep` class.

    .. remarks::

        This class is deprecated. Use the :class:`azureml.pipeline.steps.automl_step.AutoMLStep` class in the
        Azure Machine Learning pipeline :mod:`azureml.pipeline.steps` package.
    """

    def __init__(self, name, automl_config, inputs=None, outputs=None, script_repl_params=None,
                 allow_reuse=True, version=None, hash_paths=None, passthru_automl_config=True):
        """DEPRECATED."""
        raise DeprecationWarning(
            "The AutoMLStep in this package is deprecated. Please use the AutoMLStep in azureml-pipeline-steps.")


class AutoMLStepRun:
    """DEPRECATED. Use the :class:`azureml.pipeline.steps.automl_step.AutoMLStepRun` class.

    .. remarks::

        This class is deprecated. Use the :class:`azureml.pipeline.steps.automl_step.AutoMLStepRun` class in the
        Azure Machine Learning pipeline :mod:`azureml.pipeline.steps` package.
    """

    def __init__(self, step_run):
        """DEPRECATED."""
        raise DeprecationWarning(
            "The AutoMLStepRun in this package is deprecated. Please use the AutoMLStepRun in azureml-pipeline-steps.")
