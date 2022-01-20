from datetime import datetime
from typing import Dict, List, Optional

from grid.cli.core.artifact import Artifact
from grid.cli.core.base import GridObject
from grid.cli.exceptions import ResourceNotFound


class Experiment(GridObject):
    """
    Grid experiment object. This object contains all the properties that a
    given artifact should have. This also encapsulates special methods
    for interactive with experiment properties.

    Parameters
    ----------
    name: str
        Experiment name
    """
    terminal_statuses = ("failed", "succeeded", "cancelled")

    def __init__(self, name: Optional[str] = None, identifier: Optional[str] = None):
        self._data: Optional[Dict[str, str]] = {}
        if identifier:
            self.identifier = identifier
        elif not name:
            raise RuntimeError("Either name or identifier is required")
        self.name = name
        super().__init__()

        # get experiment ID upon instantiation if class doesn't have one
        if not hasattr(self, "identifier"):
            self.identifier = self._experiment_id_from_name(self.name)

        # log handling attributes
        self._archive_log_current_page: int
        self._archive_log_total_pages: int

    def _experiment_id_from_name(self, name: str) -> str:
        """Retrieves experiment ID from an experiment name."""

        # User can pass experiments as username:experiment_name to fetch other users experiments
        username = None
        split = name.split(":")
        if len(split) > 2:
            raise ValueError(f"Error while parsing {name}. Use the format <username>:<experiment-name>")
        elif len(split) == 2:
            username = split[0]
            name = split[1]

        query = """
        query ($experimentName: String!, $username: String) {
            getExperimentId(experimentName: $experimentName, username: $username) {
                success
                message
                experimentId
            }
        }
        """
        params = {"experimentName": name, "username": username}
        result = self.client.query(query, **params)

        if not result["getExperimentId"]["success"]:
            if "Cannot find experiment" in result["getExperimentId"]["message"]:
                raise ResourceNotFound(
                    f"Experiment {name} does not exist\nIf you wish to fetch an experiment for somebody in your team, use <username>:<experiment-name> format"
                )
            raise ValueError(f"{result['getExperimentId']['message']}")

        return result["getExperimentId"]["experimentId"]

    def refresh(self) -> None:
        """
        Updates object metadata. This makes a query to Grid to fetch the
        object"s latest data.
        """
        query = """
        query GetExperimentDetails ($experimentId: ID!) {
            getExperimentDetails(experimentId: $experimentId) {
                name
                githubId
                desiredState
                commitSha
                entrypoint
                invocationCommands
                createdAt
                startedRunningAt
                finishedAt
                run {
                    runId
                    name
                }
                parameters {
                    name
                    value
                }
            }
        }
        """
        result = self.client.query(query, experimentId=self.identifier)
        self._data = result["getExperimentDetails"]
        self._update_meta()

    def _archive_logs(self,
                      start: Optional[datetime] = None,
                      stop: Optional[datetime] = None,
                      limit: int = 100) -> List[Dict[str, str]]:
        """
        Retrieves logs from the archives. Logs from the archives can only
        be retrieved using a time window.

        Parameters
        ----------
        start: datetime
            Start period

        stop: datetime
            Stop period

        limit: int, default 100
            Number of lines to return. This only filters lines in memory.

        Returns
        -------
        List[Dict[str, str]]
            List of log records
        """
        query = """
        query ($experimentId: ID!, $start: DateTime, $stop: DateTime) {
            getExperimentLogs(experimentId: $experimentId, start: $start, stop: $stop) {
                success
                message

                lines {
                    message
                    timestamp
                }
            }
        }
        """
        params = {"experimentId": self.identifier, "start": start, "stop": stop}
        result = self.client.query(query, **params)

        data = result["getExperimentLogs"]

        # check if request was successful
        if not data["success"]:
            raise ValueError(f"Failed to fetch logs. Error: {data['message']}")

        # set metadata for pagination
        if not data['lines']:
            return []
        self._archive_logs_latest_timestamp = max({l["timestamp"] for l in data["lines"]})

        # return just log lines; filter based on limit
        # TODO: this operation is better placed in the backend. This will reduce
        # data transfer and be faster overall.
        output = data["lines"]
        if limit is not None and limit > 0:
            output = output[-limit:]

        # add type identifier
        for log in output:
            log["type"] = "experiment"

        return output

    def _live_logs(self, limit: int) -> Dict[str, str]:
        """
        Streams real-time experiment logs.

        Yields
        ------
        Dict[str, str]
            Log lines
        """
        subscription = """
        subscription ($experimentId: ID!, $limit:Int) {
            getLiveExperimentLogs(
                experimentId: $experimentId,
                limit: $limit) {
                    message
                    timestamp
            }
        }
        """
        params = {"experimentId": self.identifier, "limit": limit}
        stream = self.client.subscribe(query=subscription, **params)
        for element in stream:
            for entry in element["getLiveExperimentLogs"]:
                yield {"type": "experiment", **entry}

    def _live_build_logs(self, limit: int) -> Dict[str, str]:
        """
        Streams build logs from subscription API.

        Yields
        ------
        Dict[str, str]
            Log lines
        """
        subscription = """
        subscription ($experimentId: ID!, $tailLines:Int) {
            getLiveBuildLogs(
                experimentId: $experimentId,
                tailLines: $tailLines) {
                    message
                    timestamp
            }
        }
        """
        params = {"experimentId": self.identifier, "tailLines": limit}
        stream = self.client.subscribe(query=subscription, **params)
        for element in stream:
            yield {"type": "build", **element["getLiveBuildLogs"]}

    def _archive_build_logs(self,
                            start: Optional[datetime] = None,
                            stop: Optional[datetime] = None,
                            limit: int = 100) -> List[Dict[str, str]]:
        """
        Retrievies build logs from the archive.

        Yields
        ------
        Dict[str, str]
            Log lines
        """
        subscription = """
        query ($experimentId: ID!, $start: DateTime, $stop: DateTime) {
            getBuildLogs(
                experimentId: $experimentId,
                start: $start,
                stop: $stop) {
                    message
                    timestamp
            }
        }
        """
        params = {"experimentId": self.identifier, "start": start, "stop": stop}
        result = self.client.query(query=subscription, **params)

        data = result["getBuildLogs"]

        # add type identifier
        for log in data:
            log["type"] = "build"
        if limit is not None and limit > 0:
            data = data[-limit:]
        return data

    def logs(self, build_logs: Optional[bool] = None, tail_lines: Optional[int] = None) -> Dict[str, str]:
        """
        Experiment logs generator; combines both stdout and stderr logs.

        Parameters
        ----------
        build_logs: bool, default None
            If result should include build logs. When left to `None`, this will automatically
            include build logs in output when `Experiment.is_queued` evaluates to `True`.
            If `build_logs=True` is passed, then this includes build logs in the output
            by default.
        tail_lines: int, default None
            Number of lines to fetch from end. If subscribing for logs on a running
            experiment, this will fetch up to this number of lines.

        Yields
        ------
        Dict[str, str]
            Log entry
        """
        if build_logs is not False:
            # TODO (luiscape): pagination summary API is required for pagination
            if self.is_queued:
                for entry in self._live_build_logs(limit=tail_lines):
                    yield entry
            else:
                for entry in self._archive_build_logs(limit=tail_lines):
                    yield entry
        if self.is_terminal:
            # adds limit for a better user experience; this is done to
            # prevent overwheming clients with all logs all the time
            if tail_lines is None:
                tail_lines = 100

            for entry in self._archive_logs(limit=tail_lines):
                yield entry
        elif self.is_running:
            for entry in self._live_logs(limit=tail_lines):
                yield entry

    @property
    def is_terminal(self):
        """Determines if an experiment is in terminal status."""
        return self.status in self.terminal_statuses

    @property
    def is_running(self):
        """Determines if an experiment is in a running status."""
        return self.status == "running"

    @property
    def is_queued(self):
        """Determines if an experiment is in a queued status."""
        return self.status == "queued"

    @property
    def is_preparing(self):
        """Represents states prior to an experiment running"""
        return self.status in ("queued", "pending")

    @property
    def status(self) -> str:
        query = """
        query ($experimentId: ID!) {
            getExperimentDetails(experimentId: $experimentId) {
                status
            }
        }
        """
        result = self.client.query(query, experimentId=self.identifier)
        return result["getExperimentDetails"]["status"]

    @property
    def artifacts(self) -> List[Artifact]:
        """Fetches artifacts from a given experiments. Artifacts are"""
        query = """
        query ($experimentId: ID!) {
            getArtifacts(experimentId: $experimentId) {
                signedUrl
                downloadToPath
                downloadToFilename
            }
        }
        """
        result = self.client.query(query, experimentId=self.identifier)
        return [Artifact(*a.values()) for a in result.get("getArtifacts")]
