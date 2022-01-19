from __future__ import annotations
from typing import List, Optional
from continual.rpc.management.v1 import management_pb2
from continual.rpc.management.v1 import types
from continual.python.sdk.resource import Resource
from continual.python.sdk.manager import Manager
from continual.python.sdk.iterators import Pager
from continual.python.sdk.events import EventManager


class ExperimentManager(Manager):
    """Manages experiment resources."""

    name_pattern: str = (
        "projects/{project}/models/{model}/versions/{version}/experiments/{experiment}"
    )

    def get(self, id: str) -> Experiment:
        """Get experiment.

        Arguments:
            id: Experiment name or id.

        Returns
            An experiment.
        """
        req = management_pb2.GetExperimentRequest(name=self.name(id))
        resp = self.client._management.GetExperiment(req)
        return Experiment.from_proto(resp, client=self.client)

    def list(
        self,
        page_size: Optional[int] = None,
        filters: List[str] = None,
        all_projects=False,
    ) -> List[Experiment]:
        """List experiments.

        Arguments:
            page_size: Number of items to return.

            filters: List of filters to apply to experiment. Can be:
            - state  (i.e. state:FAILED)


        Returns:
            A list of experiments.
        """
        req = management_pb2.ListExperimentsRequest(
            parent=self.parent,
            page_size=page_size,
            filters=filters,
            all_projects=all_projects,
        )
        resp = self.client._management.ListExperiments(req)
        return [Experiment.from_proto(x, client=self.client) for x in resp.experiments]

    def list_all(self) -> Pager[Experiment]:
        """List all experiments.

        Pages through all experiments using an iterator.

        Returns:
            A iterator of all experiments.
        """

        def next_page(next_page_token):
            req = management_pb2.ListExperimentsRequest(
                parent=self.parent, page_token=next_page_token
            )
            resp = self.client._management.ListExperiments(req)
            return (
                [
                    Experiment.from_proto(x, client=self.client)
                    for x in resp.experiments
                ],
                resp.next_page_token,
            )

        return Pager(next_page)


class Experiment(Resource, types.Experiment):
    """Experiment resource."""

    manager: ExperimentManager
    events: EventManager
    """Event manager."""

    name_pattern: str = (
        "projects/{project}/models/{model}/versions/{version}/experiments/{experiment}"
    )

    def _init(self):
        self.manager = ExperimentManager(parent=self.parent, client=self.client)
        self.events = EventManager(parent=self.name, client=self.client)

    def cancel(self) -> None:
        """Cancel experiment."""
        raise NotImplementedError("Not yet implemented.")

    def wait(self) -> None:
        """Wait for experiment to complete."""
        raise NotImplementedError("Not yet implemented.")
