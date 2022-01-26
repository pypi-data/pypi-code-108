import itertools
import json
import threading
from typing import Tuple, List, Set, Dict
from paho.mqtt.client import MQTTv311
import paho.mqtt.client as mqtt

from .mqtt_operation_cache import OperationQueue, Operation, OperationType
from ....config.mqtt_topics_config import MQTTTopicsConfig
from ....enums.message_type import MessageType
from ....handlers.mqtt import MessageHandler
from ....pyzio_logger import PyzioLogger


class PhasioMQTTClient:

    def __init__(self, logger: PyzioLogger, mqtt_config: MQTTTopicsConfig, operation_queue: OperationQueue):
        self._mqtt_config = mqtt_config
        self._client = None
        self._logger = logger
        self._client = mqtt.Client()
        self._topics: Set[str] = set()
        self._handlers: Dict[str, MessageHandler] = dict()
        self._message_queue = operation_queue
        self._lock = threading.Lock()

    def connect(self, username: str, password: str) -> None:
        self._client_loop_start(username, password)

    def add_subscription(self, topic: str):
        self._topics.add(topic)

    def add_handler(self, message_type: MessageType, handler: MessageHandler):
        self._handlers[message_type.name] = handler

    def subscribe(self):
        for topic in self._topics:
            self._subscribe_to_topic(topic)

    def publish(self, topic: str, message: str, qos: int = 1, retain: bool = False):
        with self._lock:
            if not self._client.is_connected():
                self._logger.info("Queuing pub on topic " + str(topic) + ":  " + str(message))
                operation = Operation(OperationType.PUB, topic=topic, message=message, qos=qos, retain=retain)
                self._message_queue.push(operation)
                return
            encoded_message = message.encode()
            self._logger.info("Publishing message on topic " + str(topic) + ": " + str(encoded_message))
            self._client.publish(topic, payload=encoded_message, qos=qos, retain=retain)

    def is_connected(self) -> bool:
        return self._client.is_connected()

    def disconnect(self) -> None:
        self._client_loop_stop()
        self._client.disconnect()

    def shutdown(self) -> None:
        self._client_loop_stop()
        self.disconnect()

    def _thread_main(self, username: str, password: str):
        ports = self._get_mqtt_endpoints()
        for port, transport in ports:
            try:
                self._logger.info(f'Connecting to broker on port {port} with {transport}')
                with self._lock:
                    self._client = mqtt.Client(client_id=username, clean_session=False, protocol=MQTTv311, transport=transport)
                    self._assign_mqtt_events()
                self._client.tls_set()
                self._client.username_pw_set(username, password)
                self._client.connect_async(self._mqtt_config.host(), port, keepalive=5)
                self._client.loop_forever(retry_first_connection=False)
                break
            except Exception as e:
                self._logger.error(e)
                self._logger.info(f'Error connecting to broker on port {port} with {transport}')
                continue

    def _get_mqtt_endpoints(self) -> List[Tuple[int, str]]:
        return list(zip(self._mqtt_config.ports(), itertools.repeat('tcp'))) \
               + list(zip(self._mqtt_config.websocket_ports(), itertools.repeat('websockets')))

    def _client_loop_start(self, username: str, password: str):
        self._thread = threading.Thread(target=self._thread_main, args=(username, password), daemon=True)
        self._thread.start()

    def _client_loop_stop(self):
        self._thread = None

    def _assign_mqtt_events(self):
        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message
        self._client.on_subscribe = self._on_subscribe
        self._client.on_disconnect = self._on_disconnect

    def _on_subscribe(self, client, userdata, mid, granted_qos) -> None:
        self._logger.info("Subscribed")

    def _on_connect(self, client, userdata, flags, rc) -> None:
        self._execute_queued_operations()
        if not rc == 0:
            self._logger.info("Connection to mqtt broker refused, code " + str(rc))
        else:
            self._logger.info("Connected with result  code " + str(rc))

    def _execute_queued_operations(self):
        self._logger.info("Executing queued operations")
        while not self._message_queue.isempty():
            op = self._message_queue.pop()
            if op.type == OperationType.PUB:
                self.publish(op.topic, op.message, op.qos, op.retain)
            elif op.type == OperationType.SUB:
                self._subscribe_to_topic(op.topic)

    def _on_disconnect(self, client, userdata, rc: int):
        if not rc == 0:
            self._logger.info("Disconnected from mqtt broker for unknown reasons (network error?), rc = {}".format(rc))
        else:
            self._logger.info("Disconnected from mqtt broker")

    def _on_message(self, client, userdata, msg: mqtt.MQTTMessage) -> None:
        self._logger.info("Received message on topic " + str(msg.topic) + ": " + str(msg.payload))
        payload = json.loads(msg.payload)
        message_type = payload['type']
        handler = self._handlers[message_type]
        handler.handle(payload)

    def _subscribe_to_topic(self, topic: str) -> None:
        with self._lock:
            if not self._client.is_connected():
                self._logger.info("Queuing sub" + topic)
                operation = Operation(OperationType.SUB, topic=topic)
                self._message_queue.push(operation)
                return
            self._logger.info("Subscribing " + topic)
            self._client.subscribe(topic, qos=0)
