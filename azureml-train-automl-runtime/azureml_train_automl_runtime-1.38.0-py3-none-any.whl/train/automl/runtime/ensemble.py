# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Contains functionality for creating ensembles from previous automated machine learning iterations.

Creating ensembles can improve machine learning results by combining multiple iterations that may provide
better predictions compared to a single iteration. Configure an experiment to use ensembles with the
:class:`azureml.train.automl.automlconfig.AutoMLConfig` object.
"""
from typing import Any, cast, Dict, Optional, Union
import logging


from azureml.automl.runtime import voting_ensemble_base
from azureml.automl.runtime._run_history.offline_automl_run import OfflineAutoMLRun
from azureml.train.automl._azureautomlsettings import AzureAutoMLSettings
from . import _ensemble_helper


logger = logging.getLogger(__name__)


class Ensemble(voting_ensemble_base.VotingEnsembleBase):
    """
    Represents a collection of previous AutoML iterations brought together into an ensemble.

    The ensemble pipeline is initialized from a collection of already fitted pipelines.

    :param automl_settings: The settings for this current experiment.
    :type automl_settings: typing.Union[str, dict, AzureAutoMLSettings]
    :param ensemble_run_id: The ID of the current ensemble run.
    :type ensemble_run_id: str
    :param experiment_name: The name of the current Azure automated ML experiment.
    :type experiment_name: str
    :param workspace_name: The name of the current Azure Machine Learning workspace where the experiment is run.
    :type workspace_name: str
    :param subscription_id: The ID of the current Azure Machine Learning subscription where the experiment is run.
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
                 resource_group_name: str):
        """Create an Ensemble pipeline out of a collection of already fitted pipelines.

        :param automl_settings: The settings for this current experiment.
        :type automl_settings: typing.Union[str, dict, AzureAutoMLSettings]
        :param ensemble_run_id: The ID of the current ensemble run.
        :type ensemble_run_id: str
        :param experiment_name: The name of the current Azure automated ML experiment.
        :type experiment_name: str
        :param workspace_name: The name of the current Azure Machine Learning workspace where the experiment is run.
        :type workspace_name: str
        :param subscription_id: The ID of the current Azure Machine Learning subscription where the experiment is run.
        :type subscription_id: str
        :param resource_group_name: The name of the current Azure resource group.
        :type resource_group_name: str
        """
        super(Ensemble, self).__init__(automl_settings, AzureAutoMLSettings)
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


class VotingEnsemble(Ensemble):
    """Defines an ensemble created from previous AutoML iterations that implements soft voting.

    You do not use the VotingEnsemble class directly. Rather, specify using VotingEnsemble with
    the :class:`azureml.train.automl.automlconfig.AutoMLConfig` object.
    """

    pass
