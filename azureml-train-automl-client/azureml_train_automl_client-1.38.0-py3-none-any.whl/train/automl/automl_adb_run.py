# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Contains functionality for running automated ML experiments with Azure Databricks (ADB).

The :class:`azureml.train.automl.automl_adb_run.AutoMLADBRun` class is a wrapper around the
:class:`azureml.train.automl.run.AutoMLRun` class and provides Azure Databricks-specific implementation of
some methods.
"""
from azureml._common._error_definition import AzureMLError
from azureml._common._error_definition.user_error import ArgumentBlankOrEmpty
from azureml._restclient.constants import AUTOML_RUN_USER_AGENT
from azureml.automl.core.shared.logging_utilities import log_traceback
from .exceptions import ClientException, ConfigException
from .run import AutoMLRun


class AutoMLADBRun(AutoMLRun):
    """
    Represents an automated ML experiment run, executed on Azure Databricks.

    The AutoMLADBRun class inherits from the :class:`azureml.train.automl.run.AutoMLRun` class and holds properties
    related to an Azure Databricks (ADB) experiment run. For more information on working with experiment runs, see
    the :class:`azureml.core.Run` class.

    :param experiment: The experiment associated with the run.
    :type experiment: azureml.core.Experiment
    :param run_id: The ID associated with the run.
    :type run_id: str
    :param adb_thread: The thread executing the experiment on ADB.
    :type adb_thread: azureml.train.automl._experiment_drivers.spark_experiment_driver.AdbDriverThread
    """

    def __init__(self, experiment, run_id, adb_thread, **kwargs):
        """
        Initialize AutoMLADBRun.

        :param experiment: The experiment associated with the run.
        :type experiment: azureml.core.Experiment
        :param run_id: The ID associated with the run.
        :type run_id: str
        :param adb_thread: The thread executing the experiment on ADB.
        :type adb_thread: azureml.train.automl._experiment_drivers.spark_experiment_driver.AdbDriverThread
        """
        user_agent = kwargs.pop('_user_agent', AUTOML_RUN_USER_AGENT)
        super(AutoMLADBRun, self).__init__(experiment=experiment,
                                           run_id=run_id, _user_agent=user_agent, **kwargs)
        if adb_thread is None:
            raise ConfigException._with_error(
                AzureMLError.create(ArgumentBlankOrEmpty, target="adb_thread", argument_name="adb_thread")
            )
        self.adb_thread = adb_thread

    def cancel(self):
        """
        Cancel an AutoML run.

        Returns True if the AutoML run is canceled successfully.

        :return: None
        """
        super(AutoMLADBRun, self).cancel()

        try:
            self.adb_thread.cancel()
        except Exception as e:
            log_traceback(e, self._get_logger(None))
            raise ClientException.create_without_pii("Failed while cancelling spark job with id: {}".format(
                self._run_id)) from None
        return True
