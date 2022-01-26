from typing import List

from confluent_kafka import TIMESTAMP_NOT_AVAILABLE

from ..service import Service
from ..logger import init_logger
from ..adapter.PetraAdapter import PetraAdapter
from ..machine_topics import MACHINE_EVENTS, MACHINE_INPUT_TOPIC
from ..message import Headers
from ..config import KAFKA_SERVER_URL
from ..simulation.update_message_types import SetMachineMessage, UpdateMessage
from ..event_utls.consumer_decorator import consume

_logger = init_logger(__name__)


class MachineService(Service):
    def __init__(self, name, adapter: PetraAdapter):
        super().__init__(name)
        self.category = 'Simulation'
        self.machine_adapter = adapter

    def _are_keys_in_dict(self, keys: List[str], dict):
        for key in keys:
            if key not in dict:
                return False
        return True

    def process(self, message: SetMachineMessage) -> List[str]:
        raise NotImplemented()

    @consume([MACHINE_INPUT_TOPIC], KAFKA_SERVER_URL)
    def machine_input_handler(self, msg, **kwargs):
        timestamp_type, timestamp = msg.timestamp()
        if timestamp_type == TIMESTAMP_NOT_AVAILABLE:
            _logger.debug(f"[{self.name}] receive a message without a timestamp")
            return
        headers = Headers.from_kafka_headers(msg.headers())
        received_package_id = headers.package_id
        _logger.debug(f'[{self.name}] call machine_input_handler receive headers: {str(headers)} group_id: {",".join([t.group_id for t in self.thread_pool])}')
        # if headers.is_message_for(self.type) or headers.is_message_for(self.name):

        message = SetMachineMessage.deserialize([msg])
        updated_tables = self.process(message)

        # updated event
        self.updated_event(package_id=received_package_id,
                           msg=UpdateMessage(source=headers.msg_type, updated=updated_tables))
        _logger.debug(f"[{self.name}] end machine_input_handler")

    def updated_event(self, package_id, msg):
        self.producer.sync_produce(MACHINE_EVENTS, msg.serialize(), Headers(package_id=package_id, source=self.type))
