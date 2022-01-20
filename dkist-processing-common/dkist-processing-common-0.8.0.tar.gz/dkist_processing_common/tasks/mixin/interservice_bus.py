"""
Mixin for a WorkflowDataTaskBase subclass which implements interservice bus access functionality
"""
import json
from os import environ
from typing import Any
from typing import Dict
from typing import List

from talus import DurableBlockingProducerWrapper

from dkist_processing_common._util.config import get_mesh_config


class InterserviceBusMixin:
    @property
    def _interservice_bus_client_retry_config(self) -> dict:
        retry_configuration = environ.get(
            "RETRY_CONFIG",
            '{"retry_delay":1,"retry_backoff":2,"retry_jitter":[1,10],"retry_max_delay":300}',
        )
        retry_configuration = json.loads(retry_configuration)
        retry_configuration["retry_jitter"] = tuple(retry_configuration["retry_jitter"])
        return retry_configuration

    @property
    def _interservice_bus_client_config(self) -> dict:
        mesh_config = get_mesh_config()
        return {
            "rabbitmq_host": mesh_config["interservice-bus"]["mesh_address"],
            "rabbitmq_port": mesh_config["interservice-bus"]["mesh_port"],
            "rabbitmq_user": environ.get("ISB_USERNAME", "guest"),
            "rabbitmq_pass": environ.get("ISB_PASSWORD", "guest"),
        }

    @staticmethod
    def _interservice_bus_parse_bindings(messages: List[Any]) -> List[Dict[str, str]]:
        # @message_class decorated messages only
        # transform in to a single list
        all_bindings = []
        for m in messages:
            all_bindings += m.binding()
        # dedup
        result = []
        for binding in all_bindings:
            if binding not in result:
                result.append(binding)
        return result

    def interservice_bus_publish(self, messages: List[Any]):
        # @message_class decorated messages only
        bindings = self._interservice_bus_parse_bindings(messages=messages)
        with DurableBlockingProducerWrapper(
            producer_queue_bindings=bindings,
            publish_exchange="master.direct.x",
            **self._interservice_bus_client_config,
            **self._interservice_bus_client_retry_config,
        ) as producer:
            for message in messages:
                producer.publish_message(message)
