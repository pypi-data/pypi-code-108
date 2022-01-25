"""
This file hosts all the websocket service endpoints (which is only cluster logs now). This should be
a python package with cluster/experiment services inside it in the future. Similar to services, we have
models which are the inputs to these services
"""
import json
from typing import Iterator
import logging

import arrow
from websocket import WebSocketConnectionClosedException

from grid.websocket.client import WebSocketClient
from grid.websocket.model import ClusterLogsRequest, ClusterLogsResponse

logger = logging.getLogger(__name__)


class ClusterService:
    service_url = "v1/core/clusters"

    def __init__(self, ws_client: WebSocketClient):
        self.ws_client = ws_client

    def cluster_logs(self, req: ClusterLogsRequest) -> Iterator[ClusterLogsResponse]:
        subscription_path = f"{self.service_url}/{req.cluster_id}/logs"
        query_params = req.as_dict()
        query_params.pop("cluster_id", None)
        ws = self.ws_client.connect(subscription_path, query_params)
        try:
            for message in ws:
                if not message:
                    continue
                kwargs = json.loads(message)
                kwargs['timestamp'] = arrow.get(kwargs['timestamp']).datetime
                kwargs['level'] = kwargs['labels']['level']
                yield ClusterLogsResponse(**kwargs)
        except WebSocketConnectionClosedException:
            logger.debug("WebSocket connection closed")
