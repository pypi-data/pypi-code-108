# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Contains functionality for creating stack ensembles from previous Automated Machine Learning iterations."""
from typing import Any, cast, Dict, Optional, Union

from azureml.automl.runtime import stack_ensemble_base
from azureml.automl.runtime._run_history.offline_automl_run import OfflineAutoMLRun
from azureml.train.automl._azureautomlsettings import AzureAutoMLSettings
from . import _ensemble_helper


class StackEnsemble(stack_ensemble_base.StackEnsembleBase):
    """
    Represents a stack ensembling of previous automate ML iterations.

    The ensemble pipeline is initialized from a collection of already fitted pipelines.
    You do not use the StackEnsemble class directly. Rather, specify using StackEnsemble with
    the :class:`azureml.train.automl.automlconfig.AutoMLConfig` object ``enable_stack_ensemble``
    parameter. For more information, see `Ensemble
    configuration <https://docs.microsoft.com/azure/machine-learning/how-to-configure-auto-train#ensemble>`_.

    :param automl_settings: The settings for this current experiment.
    :type automl_settings: str or dict or AzureAutoMLSettings
    :param ensemble_run_id: The ID of the current ensembling run.
    :type ensemble_run_id: str
    :param experiment_name: The name of the current automated ML experiment.
    :type experiment_name: str
    :param workspace_name: The name of the current Azure Machine Learning workspace where the experiment is run.
    :type workspace_name: type
    :param subscription_id: The ID of the current Azure subscription where the experiment is run.
    :type subscription_id: str
    :param resource_group_name: The name of the current Azure resource group.
    :type resource_group_name: str
    """

    def __init__(self,
                 automl_settings: Union[str, Dict[str, Any], AzureAutoMLSettings],
                 ensemble_run_id: str,
                 experiment_name: str,
                 workspace_name: str,
                 subscription_id: str,
                 resource_group_name: str,
                 **kwargs: str):
        """Create a StackEnsemble pipeline out of a collection of already fitted pipelines.

        :param automl_settings: The settings for this current experiment.
        :type automl_settings: str or dict or AzureAutoMLSettings
        :param ensemble_run_id: The ID of the current ensembling run.
        :type ensemble_run_id: str
        :param experiment_name: The name of the current automated ML experiment.
        :type experiment_name: str
        :param workspace_name: The name of the current Azure Machine Learning workspace where the experiment is run.
        :type workspace_name: type
        :param subscription_id: The ID of the current Azure subscription where the experiment is run.
        :type subscription_id: str
        :param resource_group_name: The name of the current Azure resource group.
        :type resource_group_name: str
        """
        super(StackEnsemble, self).__init__(automl_settings, AzureAutoMLSettings)
        self.helper = _ensemble_helper.EnsembleHelper(
            cast(AzureAutoMLSettings, self._automl_settings),
            ensemble_run_id,
            experiment_name,
            workspace_name,
            subscription_id,
            resource_group_name)

    def _download_fitted_models_for_child_runs(self, child_runs, model_remote_path):
        """Override the base implementation for downloading the fitted pipelines in an async manner.

        :param child_runs: collection of child runs for which we need to download the pipelines
        :param model_remote_path: the remote path where we're downloading the pipelines from
        """
        return self.helper.download_fitted_models_for_child_runs(child_runs, model_remote_path)

    def _get_ensemble_and_parent_run(self):
        return self.helper.get_ensemble_and_parent_run()
