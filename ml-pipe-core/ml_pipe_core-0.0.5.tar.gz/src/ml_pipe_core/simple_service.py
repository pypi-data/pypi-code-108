import json
from abc import abstractmethod
from typing import Optional, Tuple

from confluent_kafka import TIMESTAMP_NOT_AVAILABLE

from .logger import init_logger
from .config import KAFKA_SERVER_URL
from .machine_topics import MACHINE_INPUT_TOPIC
from .service import Service
from .event_utls.consumer_decorator import consume
from .message import Headers, Message
from .simple_service_message import SimpleServiceMessage
from .topics import AGENT_EVENTS, RECONFIG_TOPIC, SERVICE_INPUT_TOPIC
from .adapter.PetraAdapter import PetraAdapter
from .simulation.update_message_types import *
from .agent_result_message import AgentResultMessage

_logger = init_logger(__name__)


class SimpleService(Service):
    def __init__(self, name, machine_adapter: PetraAdapter):
        super().__init__(name)
        self.machine_adapter = machine_adapter
        self.current_package_id = None

    @abstractmethod
    def proposal(self, params: Optional[dict]) -> Optional[Tuple[dict, int, str]]:
        """[summary]
        Function that will be called when the Agent is triggered.
        :param params: Optional parameter for configuration or setting internal parameter 
        :type params: Optional[dict]
        :return: A tuple consisting of a dictionary which is containing the result of the Agent that will be stored, 
        an error code and and error message. All parameter are optional and can be set to None if not needed.
        :rtype: Optional[Tuple[dict, int, str]]
        """
        pass

    def machine_events(self, msg_type, msg):
        _logger.warning("observe is not implemented by servie")

    def set_machine(self, data: SetMachineMessage):
        if self.current_package_id is not None:
            self.producer.sync_produce(MACHINE_INPUT_TOPIC, data.serialize(), Headers(package_id=self.current_package_id, source=self.type, msg_type=self.type))
        else:
            _logger.error("Try to set machine with a message without package_id.")

    def reconfig_event(self, msg):
        """[summary]
        Function that can be overloaded by the concret service to reconfig without restarting
        :param msg: [description]
        :type msg: [type]
        """
        pass

    def _does_local_storage_exists(self):
        # ToDo: Not implemented yet
        return False

    @consume([SERVICE_INPUT_TOPIC, RECONFIG_TOPIC], KAFKA_SERVER_URL)
    def service_input_handler(self, msg, **kwargs):
        timestamp_type, timestamp = msg.timestamp()
        if timestamp_type == TIMESTAMP_NOT_AVAILABLE:
            _logger.debug(f"[{self.name}] receive a message without a timestamp")
            return
        headers = Headers.from_kafka_headers(msg.headers())
        self.current_package_id = headers.package_id
        #self.machine_adapter.active_package_id = headers.package_id
        _logger.debug(f'[{self.name}] call service_input_handler receive headers: {str(headers)} group_id: {",".join([t.group_id for t in self.thread_pool])}')
        _logger.debug(f"Received message from topic '{msg.topic()}'")
        if headers.is_message_for(self.type) or headers.is_message_for(self.name):

            if msg.topic() == SERVICE_INPUT_TOPIC:
                data = SimpleServiceMessage.deserialize([msg])
                result = self.proposal(data.params)
                # store message
                if result != None:
                    agent_result, error_code, error_message = result
                    if self._does_local_storage_exists():
                        # TODO: store the agent_result in local db and set agent_result to db url
                        pass
                    self.producer.async_produce(AGENT_EVENTS, AgentResultMessage(agent_result, error_message, error_code).serialize(),
                                                Headers(package_id=self.current_package_id, source=self.type, msg_type=self.type))
                    _logger.debug(f"send result message to topic '{AGENT_EVENTS}'")

            elif msg.topic() == RECONFIG_TOPIC:
                _logger.debug(f"reconfig message received")
                self.reconfig_event(json.loads(msg.value().decode('utf-8')))

        _logger.debug(f'[{self.name}] end service_input_handler')
