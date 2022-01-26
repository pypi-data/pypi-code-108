from __future__ import annotations
from typing import List, Optional
from continual.rpc.management.v1 import management_pb2
from continual.rpc.management.v1 import types
from continual.python.sdk.resource import Resource
from continual.python.sdk.manager import Manager
from continual.python.sdk.iterators import Pager
from continual.python.sdk.waiter import wait
from continual.python.sdk.experiments import ExperimentManager, Experiment
from continual.python.sdk.promotions import Promotion
from continual.python.sdk.events import EventManager


class ModelVersionManager(Manager):
    """Manages Model Version resources."""

    name_pattern: str = "projects/{project}/models/{model}/versions/{version}"

    def get(self, id: str) -> ModelVersion:
        """Get model version.

        Arguments:
            id: Model name or id.

        Returns
            An Model Version.
        """
        req = management_pb2.GetModelVersionRequest(name=self.name(id))
        resp = self.client._management.GetModelVersion(req)
        return ModelVersion.from_proto(resp, client=self.client)

    def list(
        self,
        page_size: Optional[int] = None,
        filters: List[str] = None,
        all_projects: bool = False,
    ) -> List[ModelVersion]:
        """List model versions.

        Arguments:
            page_size: Number of items to return.

            filter: List of filters to apply to batch prediction job. Can be:
            - state  (i.e. state:FAILED)

        Returns:
            A list of model versions.
        """
        req = management_pb2.ListModelVersionsRequest(
            parent=self.parent,
            page_size=page_size,
            filters=filters,
            all_projects=all_projects,
        )
        resp = self.client._management.ListModelVersions(req)
        return [
            ModelVersion.from_proto(x, client=self.client) for x in resp.model_versions
        ]

    def list_all(self) -> Pager[ModelVersion]:
        """List all model versions.

        Pages through all model versions using an iterator.

        Returns:
            A iterator of all model versions.
        """

        def next_page(next_page_token):
            req = management_pb2.ListModelVersionsRequest(
                parent=self.parent, page_token=next_page_token
            )
            resp = self.client._management.ListModelVersions(req)
            return (
                [
                    ModelVersion.from_proto(x, client=self.client)
                    for x in resp.model_versions
                ],
                resp.next_page_token,
            )

        return Pager(next_page)

    def promote(self, id: str, force: bool = True) -> Promotion:
        """Promote model version.

        Arguments:
            id: Name or id of model version.
            force: Promote even if model performance is worse.
        Returns:
            A new promotion.
        """
        req = management_pb2.PromoteModelVersionRequest(name=self.name(id))
        resp = self.client._management.PromoteModelVersion(req)
        return Promotion.from_proto(resp, client=self.client)

    def cancel(self, id: str) -> None:
        """Cancel model training run."""
        req = management_pb2.CancelTrainingRequest(name=self.name(id))
        self.client._management.CancelTraining(req)


class ModelVersion(Resource, types.ModelVersion):
    """Model version resource."""

    name_pattern: str = "projects/{project}/models/{model}/versions/{version}"
    manager: ModelVersionManager

    experiments: ExperimentManager
    """Experiment manager."""

    events: EventManager
    """Event manager."""

    def _init(self):
        self.manager = ModelVersionManager(parent=self.parent, client=self.client)
        self.experiments = ExperimentManager(parent=self.name, client=self.client)
        self.events = EventManager(parent=self.name, client=self.client)

    def cancel(self) -> None:
        """Cancel model version trailing."""
        self.manager.cancel(self.id)

    def wait(
        self,
        echo: bool = False,
        timeout: Optional[int] = None,
    ) -> ModelVersion:
        """Wait for model state transition to complete.

        Arguments:
            echo: Display progress.
            timeout: Timeout in second.

        Returns:
            An updated model version.
        """
        return wait(lambda: self.manager.get(self.id), echo=echo, timeout=timeout)

    def promote(self, force: bool = True) -> Promotion:
        """Promote model version.

        Arguments:
            force: Promote even if model performance is worse.

        Returns:
            A new promotion.
        """
        return self.manager.promote(self.id, force)

    @property
    def experiment(self) -> Experiment:
        """Winning experiment (expanded object)."""
        return self.client.experiments.get(super().experiment)

    @experiment.setter
    def experiment(self, value: Experiment) -> None:
        types.ModelVersion.experiment.fset(self, value)
