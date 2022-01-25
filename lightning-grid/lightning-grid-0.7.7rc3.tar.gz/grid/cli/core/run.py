from typing import List

from grid.cli.core import Experiment
from grid.cli.core.base import GridObject


class Run(GridObject):
    """
    Run object in Grid. Runs are collections of Experiment objects.

    Parameters
    ----------
    name: str
        Run name (not Run ID)
    """
    def __init__(self, name: str):
        # TODO this is not the right abstraction - username shouldn't be here. Revert this hack
        # User can pass runs as username:run_name to fetch other users experiments
        username = None
        split = name.split(":")
        if len(split) > 2:
            raise ValueError(f"Error while parsing {name}. Use the format <username>:<experiment-name>")
        elif len(split) == 2:
            username = split[0]
            name = split[1]
        self._username = username
        self.identifier = name
        super().__init__()

    def refresh(self) -> None:
        """
        Updates object metadata. This makes a query to Grid to fetch the
        object's latest data.
        """
        query = """
        query GetRunDetails ($runName: ID!) {
            getRuns(runName: $runName) {
                runId
                name
                description
                entrypoint
                createdAt
                startedRunningAt
                finishedAt
                clusterId
                nExperiments
                nRunning
                nFailed
                nCompleted
                nCancelled
                nQueued
                nPending
                invocationCommand
                projectId
                config {
                    compute
                }
            }
        }
        """
        result = self.client.query(query, runName=self.identifier)
        self._data = result["getRuns"][0]
        self._update_meta()

    @property
    def experiments(self) -> List[Experiment]:
        """
        List of experiments for the Run.

        Returns
        -------
        experiments: List[Experiment]
            List of Experiment instances.
        """
        # TODO This should live in Experiment object
        query = """
        query (
                $runName: ID, $username: String
            ) {
                getExperiments (runName: $runName, username: $username) {
                    experimentId
                    name
                    commitSha
                    entrypoint
                    invocationCommands
                    createdAt
                    finishedAt
                    startedRunningAt
                    desiredState
                }
            }
        """
        result = self.client.query(query, runName=self.identifier, username=self._username)
        # Skips the need for the Experiment object to reload
        # data from the backend API.
        experiments = []
        for experiment_data in result.get("getExperiments"):
            E = Experiment(experiment_data.pop("name"))
            E.identifier = experiment_data.pop("experimentId")
            E.data = experiment_data
            experiments.append(E)

        return experiments
