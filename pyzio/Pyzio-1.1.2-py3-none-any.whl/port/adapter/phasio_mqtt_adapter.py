import json
import threading

from ...port.adapter.mqtt.message_factory import MessageFactory
from ...port.adapter.mqtt.message_handler_factory import MessageHandlerFactory
from ...port.adapter.mqtt.phasio_mqtt_client import PhasioMQTTClient
from ...config.mqtt_topics_config import MQTTTopicsConfig
from ...enums.job_status import JobStatus
from ...enums.sensor_type import SensorType
from ...port.phasio_mqtt_port import PhasioMQTTPort
from ...pyzio_listener import PyzioListener
from ...pyzio_logger import PyzioLogger
from ...service.i_printer_service import IPrinterService


class PhasioMQTTAdapter(PhasioMQTTPort):

    def __init__(self, logger: PyzioLogger, message_handler_factory: MessageHandlerFactory, client: PhasioMQTTClient,
                 message_factory: MessageFactory, mqtt_config: MQTTTopicsConfig, printer_service: IPrinterService):
        self._client = client
        self._mqtt_config = mqtt_config
        self._printer_service = printer_service
        self._message_factory = message_factory
        self._handler_factory = message_handler_factory
        self._logger = logger

    def connect_as_candidate(self, candidate_id: str, secret: str, listener: PyzioListener) -> None:
        username = f'candidate-{candidate_id}'
        self._client.connect(username, secret)
        for handler_type, handler in self._handler_factory.build(listener).items():
            self._client.add_handler(handler_type, handler)
        self._listen_for_printer_id()
        self._client.subscribe()

    def connect_as_printer(self, printer_id: str, secret: str, listener: PyzioListener) -> None:
        username = str(printer_id)
        self._client.connect(username, secret)
        for handler_type, handler in self._handler_factory.build(listener).items():
            self._client.add_handler(handler_type, handler)
        self._listen_for_sensor_ids()
        self._listen_for_commands()
        self._client.subscribe()

    def disconnect(self) -> None:
        self._client.disconnect()

    def is_connected(self) -> bool:
        return self._client.is_connected()

    def register_sensor(self, sensor_name: str, sensor_type: SensorType) -> str:
        base_topic = self._mqtt_config.sensor_registration_topic()
        printer_id = self._printer_service.get_printer_id()
        msg, request_id = self._message_factory.create_sensor_registration_message(sensor_name, printer_id, sensor_type)
        msg_string = json.dumps(msg)
        self._client.publish(f'{base_topic}/{printer_id}', msg_string)
        return request_id

    def stream_sensor_data(self, sensor_id: str, sensor_type: SensorType, value: float) -> None:
        base_topic = self._mqtt_config.sensor_readings_topic()
        printer_id = self._printer_service.get_printer_id()
        msg = self._message_factory.create_reading_message(sensor_id, sensor_type, value)
        msg_string = json.dumps(msg)
        self._client.publish(f'{base_topic}/{printer_id}', msg_string)

    def send_job_updates(self, job_id: str, status: JobStatus) -> None:
        base_topic = self._mqtt_config.job_updates_topic()
        printer_id = self._printer_service.get_printer_id()
        msg = self._message_factory.create_job_update_message(job_id, printer_id, status)
        msg_string = json.dumps(msg)
        self._client.publish(f'{base_topic}/{printer_id}', msg_string)

    def send_heartbeat(self) -> None:
        base_topic = self._mqtt_config.printer_heartbeat_topic()
        printer_id = self._printer_service.get_printer_id()
        msg = self._message_factory.create_heartbeat_message(printer_id)
        msg_string = json.dumps(msg)
        self._client.publish(f'{base_topic}/{printer_id}', msg_string)

    def _listen_for_printer_id(self) -> None:
        base_topic = self._mqtt_config.printer_registration_ack_topic()
        candidate_id = self._printer_service.get_candidate_id()
        self._client.add_subscription(f'{base_topic}/{candidate_id}')

    def _listen_for_sensor_ids(self) -> None:
        base_topic = self._mqtt_config.sensor_registration_ack_topic()
        printer_id = self._printer_service.get_printer_id()
        self._client.add_subscription(f'{base_topic}/{printer_id}')

    def _listen_for_commands(self) -> None:
        base_topic = self._mqtt_config.command_topic()
        printer_id = self._printer_service.get_printer_id()
        self._client.add_subscription(f'{base_topic}/{printer_id}')
