import json
import logging
import threading
import time
from abc import abstractmethod
from datetime import datetime
from enum import Enum
from typing import Optional, Union, Dict

from apscheduler.job import Job
from apscheduler.jobstores.base import JobLookupError
from apscheduler.schedulers.background import BackgroundScheduler
from websocket import WebSocketApp

from hiro_graph_client.clientlib import AbstractTokenApiHandler
from hiro_graph_client.websocketlib import AbstractAuthenticatedWebSocketHandler

logger = logging.getLogger(__name__)
""" The logger for this module """


###############################################################################################################
# Message models
###############################################################################################################

class ActionMessageType(str, Enum):
    ACKNOWLEDGED = 'acknowledged'
    NEGATIVE_ACKNOWLEDGED = 'negativeAcknowledged'
    SEND_ACTION_RESULT = 'sendActionResult'
    SUBMIT_ACTION = 'submitAction'
    ERROR = 'error'
    CONFIG_CHANGED = 'configChanged'


class AbstractActionHandlerMessage:
    """
    The structure of an incoming action message
    """
    type: ActionMessageType
    """ static type name of field 'type' in the json message """

    def __init__(self, **kwargs):
        pass

    def __str__(self) -> str:
        """ Create a JSON string representation of the message """
        result = {"type": self.type}
        result.update(vars(self))
        return json.dumps(result)

    @classmethod
    def parse(cls, dict_message: dict):
        pass


class AbstractActionHandlerIdMessage(AbstractActionHandlerMessage):
    """
    The structure of an incoming action message with id
    """
    id: str

    def __init__(self,
                 action_id: str,
                 **kwargs):
        """
        Constructor

        :param action_id: ID. Might be None for messages without an ID.
        """
        super().__init__(**kwargs)
        if not action_id:
            raise ValueError("{}: parameter 'action_id' required.".format(self.__class__.__name__))
        self.id = action_id


class AbstractActionHandlerCodeMessage(AbstractActionHandlerMessage):
    """
    The structure of an incoming action message with code and message
    """
    code: int
    message: str

    def __init__(self,
                 code: int,
                 message: str,
                 **kwargs):
        """
        Constructor

        :param code: Code number
        :param message: Message string
        """
        super().__init__(**kwargs)
        self.code = code
        self.message = message


class ActionHandlerSubmit(AbstractActionHandlerIdMessage):
    handler: str
    capability: str
    parameters: dict
    timeout: int
    """Milliseconds"""

    _expires_at: int
    """Milliseconds"""

    type = ActionMessageType.SUBMIT_ACTION

    def __init__(self,
                 action_id: str,
                 handler: str,
                 capability: str,
                 parameters: dict,
                 timeout: int):
        """
        Constructor

        :param action_id: ID
        :param handler: Handler name
        :param capability: Capability name
        :param parameters: Parameter dict
        :param timeout: Timeout in milliseconds
        """
        super().__init__(action_id=action_id)
        self.handler = handler
        self.capability = capability
        self.parameters = parameters
        self.timeout = timeout

        self._expires_at = int(time.time_ns() / 1000000 + self.timeout)

    @classmethod
    def parse(cls, dict_message: dict):
        return cls(
            action_id=dict_message.get('id'),
            handler=dict_message.get('handler'),
            capability=dict_message.get('capability'),
            parameters=dict_message.get('parameters'),
            timeout=dict_message.get('timeout')
        )

    @property
    def expires_at(self):
        return self._expires_at


class ActionHandlerResult(AbstractActionHandlerIdMessage):
    result: dict

    type = ActionMessageType.SEND_ACTION_RESULT

    def __init__(self,
                 action_id: str,
                 result: Union[dict, str]):
        """
        Constructor

        :param action_id: ID
        :param result: Result data
        """
        super().__init__(action_id=action_id)
        self.result = result

    @classmethod
    def parse(cls, dict_message: dict):
        return cls(
            action_id=dict_message.get('id'),
            result=dict_message.get('result')
        )

    def stringify_result(self) -> str:
        return json.dumps({
            "type": self.type,
            "id": self.id,
            "result": json.dumps(self.result)
        })


class ActionHandlerAck(AbstractActionHandlerIdMessage, AbstractActionHandlerCodeMessage):
    type = ActionMessageType.ACKNOWLEDGED

    def __init__(self,
                 action_id: str,
                 code: int,
                 message: str):
        """
        Constructor

        :param action_id: ID
        :param code: Ack code
        :param message: Ack message
        """
        super().__init__(action_id=action_id, code=code, message=message)

    @classmethod
    def parse(cls, dict_message: dict):
        return cls(
            action_id=dict_message.get('id'),
            code=dict_message.get('code'),
            message=dict_message.get('message')
        )


class ActionHandlerNack(AbstractActionHandlerIdMessage, AbstractActionHandlerCodeMessage):
    type = ActionMessageType.NEGATIVE_ACKNOWLEDGED

    def __init__(self,
                 action_id: str,
                 code: int,
                 message: str):
        """
        Constructor

        :param action_id: ID
        :param code: Nack code
        :param message: Nack message
        """
        super().__init__(action_id=action_id, code=code, message=message)

    @classmethod
    def parse(cls, dict_message: dict):
        return cls(
            action_id=dict_message.get('id'),
            code=dict_message.get('code'),
            message=dict_message.get('message')
        )


class ActionHandlerError(AbstractActionHandlerCodeMessage):
    type = ActionMessageType.ERROR

    def __init__(self, code: int, message: str):
        """
        Constructor

        :param code: Error code
        :param message: Error message
        """
        super().__init__(code=code, message=message)

    @classmethod
    def parse(cls, dict_message: dict):
        return cls(
            code=dict_message.get('code'),
            message=dict_message.get('message')
        )


class ActionHandlerConfigChanged(AbstractActionHandlerMessage):
    type = ActionMessageType.CONFIG_CHANGED

    def __init__(self):
        super().__init__()

    @classmethod
    def parse(cls, dict_message: dict):
        return cls()


class ActionHandlerMessageParser:
    """
    Create an ActionHandlerMessage from a string message or dict.
    """

    message: dict

    def __init__(self, message: Union[dict, str]):
        """
        Create an ActionHandlerMessage from a string message or dict. Return None if no message can be parsed.

        :param message: Message as str or dict
        """
        self.message = json.loads(message) if isinstance(message, str) else message

    def parse(self) -> Optional[AbstractActionHandlerMessage]:
        """
        Create the ActionHandlerMessage

        :return: Instance of a child of AbstractActionHandlerMessage or None if *self.message* is empty.
        :raise UnknownActionException: If the type of *self.message* is unknown.
        """
        if self.message:
            message_type = self.message.get('type')

            try:
                action_type = ActionMessageType(message_type)
            except ValueError as err:
                raise UnknownActionException(message_type=message_type, error_id=self.message.get('id')) from err

            if action_type == ActionMessageType.SUBMIT_ACTION:
                return ActionHandlerSubmit.parse(self.message)
            if action_type == ActionMessageType.SEND_ACTION_RESULT:
                return ActionHandlerResult.parse(self.message)
            if action_type == ActionMessageType.ACKNOWLEDGED:
                return ActionHandlerAck.parse(self.message)
            if action_type == ActionMessageType.NEGATIVE_ACKNOWLEDGED:
                return ActionHandlerNack.parse(self.message)
            if action_type == ActionMessageType.CONFIG_CHANGED:
                return ActionHandlerConfigChanged.parse(self.message)
            if action_type == ActionMessageType.ERROR:
                return ActionHandlerError.parse(self.message)

        return None


###############################################################################################################
# Special ActionHandlerMessage storage
###############################################################################################################

class ActionItem:
    """
    An item for the *ExpiringStore* which carries its timeout and retries
    """

    message: AbstractActionHandlerIdMessage
    expires_at: int
    """ Epoch time after which this item is invalid """
    retries: int
    """ Amount of retries this item can be get via the ActionStore.retryGet(). Default is 4 """

    _scheduled_job: Job

    def __init__(self, job: Job, message: AbstractActionHandlerIdMessage, expires_at: int, retries: int = 4):
        """
        Constructor

        :param job: Job of the scheduler
        :param message: AbstractActionHandlerMessage
        :param expires_at: Expiry of the message in epoch in ms
        :param retries: Retry counter for *ActionStore.retry_get*. Defaults to 4.
        """
        self._scheduled_job = job
        self.message = message
        self.expires_at = expires_at
        self.retries = retries

    def __del__(self):
        self.remove()

    def remove(self):
        """
        Remove the job from the scheduler on deletion.
        """
        try:
            self._scheduled_job.remove()
        except JobLookupError:
            pass


class ActionStore:
    """
    A thread-safe storage implementation with expiring entries
    """

    _store: Dict[str, ActionItem]
    _store_lock: threading.RLock

    _expiry_scheduler: BackgroundScheduler

    def __init__(self):
        """
        Constructor. Starts the scheduler.
        """
        self._store = {}
        self._store_lock = threading.RLock()
        self._expiry_scheduler = BackgroundScheduler()

        if logging.root.level == logging.INFO:
            logging.getLogger('apscheduler').setLevel(logging.WARNING)

        # self.__expiry_scheduler.start()

    def __del__(self):
        """ Destructor. Shuts down the scheduler. """
        self.clear()
        self.stop_scheduler()

    def start_scheduler(self):
        if not self._expiry_scheduler.running:
            self._expiry_scheduler.start()

    def stop_scheduler(self):
        if self._expiry_scheduler.running:
            self._expiry_scheduler.shutdown()

    def __expiry_remove(self, message_id: str) -> None:
        """
        Remove a message from the store and log it on *logger.isEnabledFor(logging.INFO)*.

        :param message_id: Id of the message
        """
        with self._store_lock:
            if message_id in self._store:
                item = self._store.pop(message_id)
                logger.info("Discard %s %s because it expired.", item.message.type, item.message.id)
                item.remove()

    def add(self,
            expires_at: int,
            message: AbstractActionHandlerIdMessage,
            retries: int = 4) -> None:
        """
        Add message to the store and start its expiry timer.

        :param expires_at: Epoch in ms when the message expires.
        :param message: The message itself.
        :param retries: Retries allowed when *self.retry_get* is used.
        :raise ActionItemExpired: When the expires_at has expired already.
        :raise ActionItemExists: When the id of the message already exists in the store
        """

        if expires_at - (time.time_ns() / 1000000) < 0:
            raise ActionItemExpired(message.id, message.type)

        with self._store_lock:
            if message.id in self._store:
                raise ActionItemExists(message.id, message.type)

            job: Job = self._expiry_scheduler.add_job(
                func=lambda message_id: self.__expiry_remove(message_id),
                kwargs={"message_id": message.id},
                trigger='date',
                run_date=datetime.fromtimestamp(expires_at / 1000))

            self._store[message.id] = ActionItem(job, message, expires_at, retries)

    def remove(self, message_id: str) -> None:
        """
        Remove a message from the store.

        :param message_id: Id of the message
        """
        with self._store_lock:
            if message_id in self._store:
                self._store.pop(message_id).remove()

    def get(self, message_id: str) -> Optional[AbstractActionHandlerIdMessage]:
        """
        Get a message from the store.

        :param message_id: Id of the message
        :return: The message or None if message_id is not present in the store.
        """
        with self._store_lock:
            item: ActionItem = self._store.get(message_id)
            return item.message if item else None

    def retry_get(self, message_id: str) -> Optional[AbstractActionHandlerIdMessage]:
        """
        Get a message from the store. Each time it is returned, its retries counter is decreased. If it reaches 0,
        the message gets deleted and None gets returned.

        :param message_id: Id of the message
        :return: The message or None if message_id is not present in the store or its retries counter is 0.
        """
        with self._store_lock:
            item: ActionItem = self._store.get(message_id)
            if not item:
                return None

            if item.retries:
                item.retries -= 1
                return item.message
            else:
                logger.info("Discard message %s %s because no retries left.",
                            item.message.type,
                            item.message.id)
                self.remove(message_id)
                return None

    def clear(self) -> None:
        """
        Clear the store. Remove all items from it.
        """
        with self._store_lock:
            for item in self._store.values():
                item.remove()
            self._store.clear()


###############################################################################################################
# Main handler class
###############################################################################################################

class AbstractActionWebSocketHandler(AbstractAuthenticatedWebSocketHandler):
    """
    A handler for actions
    """

    submitStore: ActionStore = None
    resultStore: ActionStore = None

    def __init__(self,
                 api_handler: AbstractTokenApiHandler,
                 query_params: Dict[str, str] = None):
        """
        Constructor

        :param api_handler: The TokenApiHandler for this WebSocket.
        :param query_params: URL Query parameters for this specific websocket. Use Dict[str,str] only here - no boolean
                             Values.
        """
        super().__init__(api_handler,
                         'action-ws',
                         query_params=query_params)

        self.submitStore = ActionStore()
        self.resultStore = ActionStore()

    def __del__(self):
        if self.submitStore:
            self.submitStore.stop_scheduler()
        if self.resultStore:
            self.resultStore.stop_scheduler()

    def __finish_submit(self, action_id: str, action_handler_result: Optional[ActionHandlerResult]):
        """
        Sends the action_handler_result if it is not None and makes sure, that the submitAction is removed from the
        self.submitStore.

        :param action_id: ID of the action
        :param action_handler_result: Result for the submitAction. May be None.
        """
        try:
            if action_handler_result:
                logger.info('Sending %s (id: %s)', action_handler_result.type, action_handler_result.id)
                self.send(action_handler_result.stringify_result())
        finally:
            self.submitStore.remove(action_id)

    def start(self) -> None:
        super().start()
        self.submitStore.start_scheduler()
        self.resultStore.start_scheduler()

    def stop(self) -> None:
        self.submitStore.stop_scheduler()
        self.resultStore.stop_scheduler()
        super().stop()

    ###############################################################################################################
    # Websocket Events
    ###############################################################################################################

    def on_open(self, ws: WebSocketApp):
        pass

    def on_close(self, ws: WebSocketApp, code: int = None, reason: str = None):
        pass

    def on_error(self, ws: WebSocketApp, error: Exception):
        pass

    def on_message(self, ws: WebSocketApp, message: str):
        """
        Handle incoming action messages

        :param ws: WebSocketApp
        :param message: The message payload as str
        """
        action_message = None
        try:
            action_message = ActionHandlerMessageParser(message).parse()
            if not action_message:
                return

            if isinstance(action_message, ActionHandlerSubmit):
                logger.info('Handling "%s" (id: %s)', action_message.type, action_message.id)

                self.send(str(ActionHandlerAck(action_message.id, 200, "submitAction acknowledged")))

                try:
                    self.submitStore.add(action_message.expires_at, action_message)
                except (ActionItemExists, ActionItemExpired) as err:
                    logger.info(str(err))
                    return

                action_handler_result = self.resultStore.get(action_message.id)
                if isinstance(action_handler_result, ActionHandlerResult):
                    logger.info('Handling "%s" (id: %s): Already processed', action_message.type, action_message.id)
                    self.__finish_submit(action_message.id, action_handler_result)
                    return

                try:
                    self.on_submit_action(action_message.id, action_message.capability, action_message.parameters)
                except Exception as err:
                    logger.error(str(err))
                    self.send_action_result(action_id=action_message.id, result=None, code=500, message=str(err))

            elif isinstance(action_message, ActionHandlerResult):
                logger.info('Handling "%s" (id: %s)', action_message.type, action_message.id)

                self.send(str(ActionHandlerNack(action_message.id, 400, "sendActionResult rejected")))

            elif isinstance(action_message, ActionHandlerAck):
                logger.info('Handling "%s" (id: %s)', action_message.type, action_message.id)

                self.resultStore.remove(action_message.id)

            elif isinstance(action_message, ActionHandlerNack):
                logger.info('Handling "%s" (id: %s)', action_message.type, action_message.id)

                action_handler_result = self.resultStore.retry_get(action_message.id)
                if isinstance(action_handler_result, ActionHandlerResult):
                    time.sleep(1)
                    self.send(action_handler_result.stringify_result())

            elif isinstance(action_message, ActionHandlerConfigChanged):
                logger.info('Handling "%s"', action_message.type)
                self.on_config_changed()

            elif isinstance(action_message, ActionHandlerError):
                logger.warning('Received error message (code %s): %s',
                               action_message.code,
                               action_message.message)

            else:
                logger.error("Received unknown message: %s", message)

        except UnknownActionException as err:
            logger.error(str(err))
            if err.id:
                self.send(str(ActionHandlerNack(err.id, 400, str(err))))
        except Exception as err:
            logger.error(str(err))
            if isinstance(action_message, AbstractActionHandlerIdMessage):
                self.send(str(ActionHandlerNack(action_message.id, 500, str(err))))

    ###############################################################################################################
    # API methods
    ###############################################################################################################

    @abstractmethod
    def on_submit_action(self, action_id: str, capability: str, parameters: dict):
        """
        Handle incoming submitAction

        :param action_id: Id of the action
        :param capability: Capability of the submitAction
        :param parameters: Additional parameters for the capability
        """
        pass

    def send_action_result(self,
                           action_id: str,
                           result: Union[dict, str] = None,
                           code: int = None,
                           message: str = None,
                           result_params: dict = None) -> None:
        """
        Send the result of a submitAction. Thread-Safe!

        Will create a standard result dict with the parameters *result*, *code* or *message*. See parameter description
        for more.

        ::

            {
                "type": "sendActionResult",
                "id": action_id,
                "result": json.dumps({
                    "message": message,
                    "code": code,
                    "data": result
                })

            }

        If *result_params* is given, this parameter will be used directly while ignoring the other parameters.

        ::

            {
                "type": "sendActionResult",
                "id": action_id,
                "result": json.dumps(result_params)
            }

        :param action_id: Required. Id of the submitAction
        :param result: Result data. Either a dict (which will be serialized into a str), a str or None.
        :param code: Optional result code. If unset, a default will be used (200 if result is not empty, 204 otherwise).
        :param message: Optional result message. If unset, a default message will be used.
        :param result_params: Optional custom data to return as result value in message *sendActionResult*.
                              Overrides all other optional message parameters. Will be serialized to a string.
        """
        result_message = ActionHandlerResult(action_id, result)
        submit_message = self.submitStore.get(action_id)

        if not isinstance(submit_message, ActionHandlerSubmit):
            logger.info('Handling "%s" (id: %s): Submit not stored - maybe it has expired?',
                        result_message.type,
                        result_message.id)
            return

        if not result_params:
            if not result:
                result_params = {
                    "message": message if message else "Action successful (no data)",
                    "code": code if code else 204
                }
            else:
                result_params = {
                    "message": message if message else "Action successful",
                    "code": code if code else 200,
                    "data": json.dumps(result) if isinstance(result, dict) else result
                }

        action_handler_result = ActionHandlerResult(result_message.id, result_params)
        try:
            self.resultStore.add(submit_message.expires_at, action_handler_result)
        except ActionItemExists as err:
            logger.info(str(err))
            action_handler_result = self.resultStore.get(result_message.id)
        except ActionItemExpired as err:
            logger.info(str(err))
            action_handler_result = None

        self.__finish_submit(action_id, action_handler_result)

    @abstractmethod
    def on_config_changed(self):
        pass


###################################################################################################################
# Exceptions
###################################################################################################################

class ActionException(Exception):
    """
    When an unknown action is received
    """
    id: str
    type: str

    def __init__(self, error_id, message_type):
        self.id = error_id
        self.type = message_type


class UnknownActionException(ActionException):
    """
    When an unknown action is received
    """

    def __init__(self, error_id, message_type):
        super().__init__(error_id, message_type)

    def __str__(self):
        return 'Unknown ActionHandlerMessage "{}" (id: {})'.format(self.type, self.id)


class ActionItemExpired(ActionException):
    """
    When an action item for the ActionStore has expired
    """

    def __init__(self, error_id, message_type):
        super().__init__(error_id, message_type)

    def __str__(self):
        return 'Message has expired: "{}" (id: {})'.format(self.type, self.id)


class ActionItemExists(ActionException):
    """
    When an action item for the ActionStore already exists
    """

    def __init__(self, error_id, message_type):
        super().__init__(error_id, message_type)

    def __str__(self):
        return 'Message id already stored: "{}" (id: {})'.format(self.type, self.id)
