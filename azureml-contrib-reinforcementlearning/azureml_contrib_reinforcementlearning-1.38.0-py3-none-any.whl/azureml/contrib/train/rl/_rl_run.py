# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Class for handling and monitoring Reinforcement Learning runs associated with an
   Experiment object and individual run id."""

from __future__ import print_function

from azureml.core.run import Run
from azureml.contrib.train.rl._rl_runconfig import ReinforcementLearningConfiguration


class ReinforcementLearningRun(Run):

    """A run class to handle and monitor Reinforcement Learning Runs associated with an
        experiment and an individual run ID.

    .. remarks::

        The Azure Machine Learning SDK provides you with a series of interconnected classes, that are
        designed to help you train and compare machine learning models that are related by the shared
        problem that they are solving.

        An :class:`azureml.core.Experiment` acts as a logical container for these training runs. A
        :class:`azureml.contrib.train.rl.ReinforcementLearningConfiguration` object is used to codify
        the information necessary to submit a training run in a Reinforcement Learning experiment. Which
        can then be submitted through the experiment. Please refer to the documentation in
        :class:`azureml.contrib.train.rl.ReinforcementLearningConfiguration` to see an example of this
        process.

        Once the :class:`azureml.contrib.train.rl.ReinforcementLearningConfiguration` is submitted, a
        ReinforcementLearningRun object is returned.

        A ReinforcementLearningRun object gives you programmatic access to information about
        the associated Reinforcement Learning run. Some examples include retrieving the logs
        corresponding to a run, canceling or completing a run if it's still in progress,
        cleaning up the artifacts of a completed run, and waiting for completion of a run
        currently in progress.


    :param experiment: The experiment object.
    :type experiment: azureml.core.experiment.Experiment
    :param run_id: The run id.
    :type run_id: str
    :param directory: The source directory.
    :type directory: str
    :param _run_config: The reinforcement learning configuration.
    :type _run_config: azureml.contrib.train.rl.ReinforcementLearningConfiguration
    :param kwargs:
    :type kwargs: dict
    """

    RUN_TYPE = "reinforcementlearning"

    def __init__(self, experiment, run_id, directory=None, _run_config=None, **kwargs):
        """Class ReinforcementLearningRun constructor."""
        from azureml._project.project import Project
        super(ReinforcementLearningRun, self).__init__(experiment, run_id, **kwargs)
        project_object = Project(experiment=experiment, directory=directory, _disable_service_check=True)
        if _run_config is not None:
            self._run_config_object = ReinforcementLearningConfiguration._get_run_config_object(_run_config, directory)
        else:
            self._run_config_object = None
        self._project_object = project_object
        self._output_logs_pattern = "azureml-logs/reinforcementlearning.txt"

    @property
    def _run_config(self):
        if self._run_config_object is None:
            # Get it from experiment in the cloud.
            # run_details = self.get_details()
            # TODO uncomment this once _get_runconfig_using_run_details is implemented
            # on ReinforcementLearningConfiguration
            # self._run_config_object =
            # ReinforcementLearningConfiguration._get_runconfig_using_run_details(run_details)
            # return self._run_config_object
            pass

    def complete(self):
        """Complete the ongoing run

        .. remarks::

            An example to complete run is as follows:

            .. code-block:: python

                run = experiment.submit(config=ReinforcementLearningRunConfig)
                run.complete()

        """
        uri = self._run_dto.get('complete_uri', None)
        self._client.cancel(uri=uri)

    @staticmethod
    def _from_run_dto(experiment, run_dto):
        """Creates run from run_dto object, which comes from RunClient
        .. code-block:: python

            client = RunClient(SERVICE_CONTEXT, EXPERIMENT_NAME, RUN_ID)
            run_dto = client.get_run()
            run = ReinforcementLearningRun._from_run_dto(EXPERIMENT, run_dto)

        :param experiment:
        :type experiment: azureml.core.experiment.Experiment
        :param run_dto:
        :type run_dto: object
        :return: Returns the run
        :rtype: ReinforcementLearningRun
        """
        return ReinforcementLearningRun(experiment, run_dto.run_id, _run_dto=run_dto)
