import json
import logging
import threading
import typing as t

import websocket

from meili_sdk.exceptions import MeiliException, WebsocketException
from meili_sdk.resources.base import BaseResource
from meili_sdk.site import get_host
from meili_sdk.version import VERSION
from meili_sdk.websockets import constants
from meili_sdk.websockets.models.message import Message
from meili_sdk.websockets.models.move_message import MoveMessage
from meili_sdk.websockets.models.slow_down_message import SlowDownMessage
from meili_sdk.websockets.models.task import Task
from meili_sdk.websockets.models.topic import RosTopic

logger = logging.getLogger("meili_sdk")

__all__ = ("MeiliWebsocketClient",)


class MeiliWebsocketClient:
    """
    Client for all communication related with FMS through websockets

    :Parameters:
    token (str) - authentication token with the WS
    fleet (bool) - use fleet websocket if set to true (default: true)
    open_handler() (callable) - a callable object that will be called with no parameters when websocket is opened
    close_handler() (callable) - a callable objects that will be called with no parameters when websocket is closed
    error_handler(err) (callable) - a callable with a single parameter that will receive the exception as a parameter
    task_handler(task: Task, data: dict, vehicle: str) - a callable that will be called when a new task is received
    move_action_handler(message: MoveMessage, data: dict, vehicle: str) - a callable for moving vehicle according to FMS
    slow_down_handler(message: SlowDownMessage, data: dict, vehicle: str) - a callable for altering movement of robots
    topic_list_handler(data: dict, vehicle: str) - a callable for handling topic list request
    topic_list_initializer_handler(topics: List[RosTopic], data: dict, vehicle: str) - a callable to initialize topics
    """

    __vehicles = []
    __connection: t.Optional[websocket.WebSocketApp]
    thread: threading.Thread

    def __init__(
        self,
        token: str,
        override_host: t.Optional[str] = None,
        fleet: t.Optional[bool] = True,
        open_handler: t.Optional[t.Callable] = None,
        close_handler: t.Optional[t.Callable] = None,
        error_handler: t.Optional[t.Callable] = None,
        task_handler: t.Optional[t.Callable] = None,
        move_action_handler: t.Optional[t.Callable] = None,
        slow_down_handler: t.Optional[t.Callable] = None,
        topic_list_handler: t.Optional[t.Callable] = None,
        topic_list_initializer_handler: t.Optional[t.Callable] = None,
        fake_opened_connection: t.Optional[bool] = False,
        message_error_handler: t.Optional[t.Callable] = None,
    ) -> None:
        self.token = token
        self.__connection_is_open = fake_opened_connection
        self.__fleet = fleet

        host = override_host or get_host()
        self.url = BaseResource.build_url(
            host, f"ws/{'fleets/' if fleet else 'vehicle/'}"
        )

        self.__open_handler = open_handler
        self.__close_handler = close_handler
        self.__error_handler = error_handler

        self.__task_handler = task_handler
        self.__move_handler = move_action_handler
        self.__slow_down_handler = slow_down_handler
        self.__topic_list_handler = topic_list_handler
        self.__topic_list_initializer_handler = topic_list_initializer_handler
        self.__message_error_handler = message_error_handler
        self.__connection = None

    def get_headers(self) -> dict:
        return {
            "x-meili-app-name": "sdk",
            "x-meili-app-version": VERSION,
            "x-meili-fleet-token": self.token,
        }

    def run_in_thread(self, wait_to_connect=True):
        try:
            self.thread = threading.Thread(target=self.run, args=())
            self.thread.start()

            if wait_to_connect:
                while not self.__connection_is_open:
                    continue
        except RuntimeError as exc:
            raise MeiliException(f"Cannot start websocket thread: {exc}")

    def run(self):
        self.__connection = websocket.WebSocketApp(
            self.url,
            on_close=self.__on_close,
            on_open=self.__on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            header=self.get_headers(),
        )

        self.__connection.run_forever()

    def __on_open(self, _):
        self.__connection_is_open = True
        self.on_open()

    def on_open(self):
        """
        When websocket is opened it should send a registration message to backend in order
        to set the vehicles that will be connected via this websocket
        """
        registration_message = self._get_registration_message()
        self.send(registration_message)

        if self.__open_handler and callable(self.__open_handler):
            self.__open_handler()

    def __on_close(self, *_):
        self.__connection_is_open = False
        self.on_close()

    def on_close(self):
        if self.__close_handler:
            self.__close_handler()

    def on_message(self, _, message):
        """
        Capture message, try loading JSON and pass it to message handler
        """
        try:
            message = json.loads(message)
            action = message["type"]
        except (ValueError, json.JSONDecodeError) as e:
            raise WebsocketException(f"Cannot decode JSON from response message: {e}")
        except KeyError:
            raise WebsocketException(f"Cannot retrieve message type")
        else:
            vehicle = message.get("vehicle", None)

            if action in constants.IGNORED_TYPES:
                return

            if action == constants.ACTION_ERROR:
                self.process_message_error(message)
                return

            if not vehicle and self.__fleet and action in constants.ALL_ACTIONS:
                raise WebsocketException(
                    f"Malformed message received. No vehicle in a fleet connection: {message}"
                )
            self.process_message(action, message, vehicle)

    def on_error(self, connection, error):
        logger.warning(f"An error has occurred inside the websocket client: {error}")
        if self.__error_handler:
            self.__error_handler(connection, error)

    def send(self, message: t.Union[dict, list, Message, str]):
        """
        Send message to the backend server

        Will automatically resolve message into required data type
        """
        if not self.__connection_is_open:
            raise WebsocketException("Connection is closed")
        if isinstance(message, Message):
            message = dict(message)
        if not isinstance(message, str):
            message = json.dumps(message)
        self.send_raw(message)

    def send_raw(self, message):
        self.__connection.send(message)

    def process_message(
        self, action: str, message: dict, vehicle: t.Optional[str] = None
    ):
        processors = {
            constants.ACTION_TASK: self.process_task,
            constants.ACTION_MOVE: self.process_move,
            constants.ACTION_MOVE_TO_CHARGING_POINT: self.process_move,
            constants.ACTION_SLOW_DOWN: self.process_slow_down,
            constants.ACTION_TOPIC_LIST: self.process_request_for_topics,
            constants.ACTION_TOPIC_INITIALIZATION: self.process_topic_list,
        }
        try:
            processor = processors[action]
        except KeyError:
            logger.warning(
                f"Cannot handle action {action}. Maybe you are using an outdated library?"
            )
            return

        if processor and callable(processor):
            processor(message, vehicle)

    def process_task(self, message: dict, vehicle: t.Optional[str] = None):
        """
        Load task to a Python object and pass it to task handler provided in the __init__
        method by implementers if applicable
        """
        task_data = message["data"]
        task = Task(**task_data)

        if self.__task_handler and callable(self.__task_handler):
            self.__task_handler(task, task_data, vehicle)

    def process_move(self, message: dict, vehicle: t.Optional[str] = None):
        move_message = MoveMessage(**message)
        if self.__move_handler and callable(self.__move_handler):
            self.__move_handler(move_message, message, vehicle)

    def process_slow_down(self, message: dict, vehicle: t.Optional[str] = None):
        slow_down = SlowDownMessage(**message["data"])
        if self.__slow_down_handler and callable(self.__slow_down_handler):
            self.__slow_down_handler(slow_down, message, vehicle)

    def process_request_for_topics(
        self, message: dict, vehicle: t.Optional[str] = None
    ):
        if self.__topic_list_handler and callable(self.__topic_list_handler):
            self.__topic_list_handler(message, vehicle)

    def process_topic_list(self, message: dict, vehicle: t.Optional[str] = None):
        topics = []

        for topic in message.get("data", []):
            topics.append(RosTopic(**topic))

        if self.__topic_list_initializer_handler and callable(
            self.__topic_list_initializer_handler
        ):
            self.__topic_list_initializer_handler(topics, message, vehicle)

    def process_message_error(self, message: dict):
        logger.warning(
            f"Validation failed for message with the following errors: {message}"
        )
        if self.__message_error_handler:
            self.__message_error_handler(message["errors"])

    def _get_registration_message(self):
        return Message(
            event=constants.EVENT_REGISTER,
            vehicles=self._get_registration_vehicles(),
        )

    def _get_registration_vehicles(self):
        return self.vehicles

    @property
    def vehicles(self):
        return self.__vehicles

    def add_vehicle(self, vehicle):
        if vehicle in self.__vehicles:
            raise ValueError("Vehicle already exists")
        self.__vehicles.append(vehicle)

    @vehicles.setter
    def vehicles(self, vehicles):
        if len(vehicles) != len(set(vehicles)):
            raise ValueError("There are duplicate vehicles")
        self.__vehicles = vehicles

    def remove_vehicle(self, vehicle):
        self.__vehicles.remove(vehicle)
