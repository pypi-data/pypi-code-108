from __future__ import annotations
from typing import List, Optional, Iterator

from continual.rpc.management.v1 import management_pb2
from continual.rpc.management.v1 import types
from continual.python.sdk.resource import Resource
from continual.python.sdk.manager import Manager
from continual.python.sdk.iterators import Pager
from continual.python.sdk.waiter import wait
from continual.python.sdk.events import EventManager

import requests


class BatchPredictionManager(Manager):
    """Manages ingestions resources."""

    name_pattern: str = (
        "projects/{project}/models/{model}/batchPredictions/{batch_prediction_job}"
    )

    def get(self, id: str) -> BatchPrediction:
        """Get batch prediction job.

        Arguments:
            id: Batch Prediction  name or id.

        Returns
            A Batch prediction .
        """
        req = management_pb2.BatchPredictionRequest(name=self.name(id))
        resp = self.client._management.GetBatchPrediction(req)
        return BatchPrediction.from_proto(resp, client=self.client)

    def list(
        self,
        page_size: Optional[int] = None,
        filters: List[str] = None,
        all_projects: bool = False,
    ) -> List[BatchPrediction]:
        """List batch prediction jobs.

        Arguments:
            page_size: Number of items to return.

            filter: List of filters to apply to batch prediction job. Can be:
            - state  (i.e. state:FAILED)
            - incremental (i.e. incremental:True)
            - dest type (i.e. dest_type:STORE)

        Returns:
            A list of batch prediction jobs.
        """
        req = management_pb2.ListBatchPredictionsRequest(
            parent=self.parent,
            page_size=page_size,
            filters=filters,
            all_projects=all_projects,
        )
        resp = self.client._management.ListBatchPredictions(req)
        return [
            BatchPrediction.from_proto(u, client=self.client)
            for u in resp.batch_predictions
        ]

    def list_all(self) -> Iterator[BatchPrediction]:
        """List all batch prediction jobs.

        Pages through all batch prediction jobs using an iterator.

        Returns:
            A iterator of all batch prediction jobs.
        """

        def next_page(next_page_token):
            req = management_pb2.ListBatchPredictionsRequest(
                parent=self.parent, page_token=next_page_token
            )
            resp = self.client._management.ListBatchPredictions(req)
            return (
                [
                    BatchPrediction.from_proto(u, client=self.client)
                    for u in resp.batch_predictions
                ],
                resp.next_page_token,
            )

        return Pager(next_page)

    def cancel(self, id: str) -> None:
        """Cancel an ingestion.

        Arugments:
            id: Name or id of ingestion

        """
        req = management_pb2.BatchPredictionRequest(name=self.name(id))
        self.client._management.CancelBatchPrediction(req)

    def download(self, id: str, file: str) -> None:
        """Download csv file created by batch prediction.

        Arguments:
            id: Batch Prediction  name or id.
            file: the path to a file, relative to the current working directory or absolute

        """
        batch_prediction_job = self.get(id)
        with requests.get(
            batch_prediction_job.csv_file_path, allow_redirects=True
        ) as fd:
            open(file, "xb").write(fd.content)
        return


class BatchPrediction(Resource, types.BatchPrediction):
    """BatchPrediction resource."""

    name_pattern: str = (
        "projects/{project}/models/{model}/batchPredictions/{batch_prediction_job}"
    )
    manager: BatchPredictionManager

    events: EventManager
    """Event manager."""

    def _init(self):
        self.manager = BatchPredictionManager(parent=self.parent, client=self.client)
        self.events = EventManager(parent=self.name, client=self.client)

    def cancel(self):
        """Cancel batch prediction job."""
        self.manager.cancel(self.id)

    def wait(self, echo: bool = True, timeout: int = None) -> BatchPrediction:
        """Wait for batch prediction job to complete.

        Arguments:
            echo: Display progress.
            timeout: Timeout in seconds.
        Returns:
            Updated batch prediction job.
        """
        return wait(
            getter=lambda: self.manager.get(self.id),
            echo=echo,
            timeout=timeout,
        )

    def download(self, file: str) -> None:
        """Download csv file created by batch prediction.

        Arguments:
            file: the path to a file, relative to the current working directory or absolute

        """
        self.manager.download(self.id, file)
        return
