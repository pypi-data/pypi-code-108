import json
import logging
import threading
from datetime import datetime
from typing import List, Dict

from apscheduler.schedulers.background import BackgroundScheduler
from websocket import WebSocketApp, WebSocketException

from hiro_graph_client.clientlib import AbstractTokenApiHandler
from hiro_graph_client.websocketlib import AbstractAuthenticatedWebSocketHandler, ErrorMessage, ReaderStatus

logger = logging.getLogger(__name__)
""" The logger for this module """


class EventMessage:
    """
    The structure of an incoming events message
    """
    id: str
    timestamp: int
    nanotime: int
    body: dict
    type: str
    metadata: dict

    def __init__(self,
                 event_id: str,
                 event_timestamp: int,
                 event_body: dict,
                 event_type: str,
                 event_metadata: dict,
                 event_nanotime: int):
        """
        Constructor

        :param event_id: ID
        :param event_timestamp: Timestamp in milliseconds
        :param event_body: Body dict
        :param event_type: Type of event. CREATE, UPDATE or DELETE.
        :param event_metadata: Additional metadata.
        :param event_nanotime: Nanotime for the event
        """
        self.id = event_id
        self.timestamp = event_timestamp
        self.body = event_body
        self.type = event_type.upper()
        self.metadata = event_metadata
        self.nanotime = event_nanotime

    @classmethod
    def parse(cls, message: str):
        """
        :param message: The message received from the websocket. Will be decoded here.
        :return: The EventMessage or None if this is not an EventMessage (type or id are missing).
        """
        json_message: dict = json.loads(message)
        if not isinstance(json_message, dict):
            return None

        event_type = json_message.get('type')
        event_id = json_message.get('id')
        if not event_type or not event_id:
            return None

        return cls(event_id,
                   json_message.get('timestamp'),
                   json_message.get('body'),
                   event_type,
                   json_message.get('metadata'),
                   json_message.get('nanotime'))

    def __str__(self):
        return json.dumps(vars(self))


class EventsFilter:
    """
    The event filter structure
    """
    id: str
    type: str
    content: str

    def __init__(self, filter_id: str, filter_content: str, filter_type: str = None):
        """
        Constructor

        :param filter_id: Unique name/id of the filter
        :param filter_content: jfilter specification for the filter.
        :param filter_type: Type of filter. Only 'jfilter' (the default when this is None) is possible here atm.
        """
        self.id = filter_id
        self.content = filter_content
        self.type = filter_type or 'jfilter'

    def __str__(self):
        return json.dumps(vars(self))

    def to_dict(self) -> dict:
        return {
            "filter-id": self.id,
            "filter-type": self.type,
            "filter-content": self.content
        }


class AbstractEventsWebSocketHandler(AbstractAuthenticatedWebSocketHandler):
    """
    A handler for issue events
    """
    _events_filter_messages: Dict[str, EventsFilter] = {}
    _scopes: List[str] = []

    _initial_messages_lock: threading.RLock
    """Lock for _events_filter_messages and _scopes """

    _token_scheduler: BackgroundScheduler

    def __init__(self,
                 api_handler: AbstractTokenApiHandler,
                 events_filters: List[EventsFilter],
                 scopes: List[str] = None,
                 query_params: Dict[str, str] = None):
        """
        Constructor

        :param api_handler: The TokenApiHandler for this WebSocket.
        :param events_filters: Filters for the events. These have to be set or the flood of incoming events will be too
                               big.
        :param scopes: List of ids of non-default scopes to subscribe. These are ogit/_id of the "ogit/DataScope"s
                       (i.e. the scope of your instance) you want to subscribe to. Default is None, which means:
                       Use default scope.
        :param query_params: URL Query parameters for this specific websocket. Use Dict[str,str] only here,
                             i.e set {"allscopes": "false"} instead of {"allscopes": False}. The default here is to set
                             {'allscopes': 'false'}.
        """
        _query_params = query_params.copy()
        if _query_params is None:
            _query_params = {'allscopes': 'false'}
        elif 'allscopes' not in _query_params:
            _query_params.update({'allscopes': 'false'})

        super().__init__(api_handler,
                         'events-ws',
                         query_params=_query_params)

        self._initial_messages_lock = threading.RLock()

        self._token_scheduler = BackgroundScheduler()

        if logging.root.level == logging.INFO:
            logging.getLogger('apscheduler').setLevel(logging.WARNING)

        if not events_filters:
            raise ValueError('Parameter events_filters= cannot be empty. It needs at least one EventsFilter.')

        for events_filter in events_filters:
            self._events_filter_messages[events_filter.id] = events_filter

        self._scopes = scopes or []

    ###############################################################################################################
    # Websocket Events
    ###############################################################################################################

    def on_open(self, ws: WebSocketApp):
        """
        Register the filters when websocket opens. If this fails, the websocket gets closed again.

        :param ws: The WebSocketApp
        :raise WebSocketFilterException: When setting the filters failed.
        """
        try:
            if not self._token_scheduler.running:
                self._set_next_token_refresh()
                self._token_scheduler.start()

            with self._initial_messages_lock:
                for scope in self._scopes:
                    scope_message = self._get_subscribe_scope_message(scope)
                    self.send(scope_message)

                for events_filter in self._events_filter_messages.values():
                    filter_message = self._get_events_register_message(events_filter)
                    self.send(filter_message)

        except Exception as err:
            raise WebSocketFilterException('Setting events filter failed') from err

    def on_close(self, ws: WebSocketApp, code: int = None, reason: str = None):
        """
        Cancel the self._token_refresh_thread. Registered filters remain as they are.

        :param ws: The WebSocketApp
        :param code:
        :param reason:
        """
        if self._token_scheduler.running:
            self._token_scheduler.shutdown()

    def on_message(self, ws: WebSocketApp, message: str):
        """
        Create an EventMessage from the incoming message and hand it over to *self.on_event*.

        :param ws: The WebSocketApp
        :param message: The raw message as string
        """

        event_message = EventMessage.parse(message)
        if event_message:
            if event_message.type not in ['CREATE', 'UPDATE', 'DELETE']:
                logger.error("Unknown event message of type '%s'", event_message.type)
            else:
                self.on_event(event_message)
        else:
            error_message = ErrorMessage.parse(message)
            if error_message:
                logger.error("Received error: %s", str(error_message))
                if self._reader_status == ReaderStatus.RUNNING_PRELIMINARY:
                    self._reader_status = ReaderStatus.FAILED
            else:
                logger.error("Invalid message: %s", message)

    def on_error(self, ws: WebSocketApp, error: Exception):
        """
        Does nothing here.

        :param ws: The WebSocketApp
        :param error: Exception
        """
        pass

    ###############################################################################################################
    # Public API Reader thread
    ###############################################################################################################

    def on_event(self, message: EventMessage) -> None:
        """
        Catches all event messages. Distributes them between *self.on_create*, *self.on_update* or *self.on_delete*
        by default.
        Overwrite this if you want a catch-all for all event messages.

        :param message: The incoming EventMessage
        """
        if message.type == 'CREATE':
            self.on_create(message)
        elif message.type == 'UPDATE':
            self.on_update(message)
        elif message.type == 'DELETE':
            self.on_delete(message)

    def on_create(self, message: EventMessage) -> None:
        """
        Called by CREATE events. Skeleton function to be overwritten if needed.

        :param message: The incoming EventMessage
        """
        pass

    def on_update(self, message: EventMessage) -> None:
        """
        Called by UPDATE events. Skeleton function to be overwritten if needed.

        :param message: The incoming EventMessage
        """
        pass

    def on_delete(self, message: EventMessage) -> None:
        """
        Called by DELETE events. Skeleton function to be overwritten if needed.

        :param message: The incoming EventMessage
        """
        pass

    ###################################################################################################################
    # Filter handling
    ###################################################################################################################

    @staticmethod
    def _get_events_register_message(events_filter: EventsFilter) -> str:
        message: dict = {
            "type": "register",
            "args": events_filter.to_dict()
        }

        return json.dumps(message)

    @staticmethod
    def _get_subscribe_scope_message(scope_id: str) -> str:
        message: dict = {
            "type": "subscribe",
            "id": scope_id
        }

        return json.dumps(message)

    def add_events_filter(self, events_filter: EventsFilter) -> None:
        message: str = self._get_events_register_message(events_filter)
        self.send(message)
        with self._initial_messages_lock:
            self._events_filter_messages[events_filter.id] = events_filter

    def remove_events_filter(self, events_filter_id: str) -> None:
        message: dict = {
            "type": "unregister",
            "args": {
                "filter-id": events_filter_id
            }
        }

        self.send(json.dumps(message))
        with self._initial_messages_lock:
            del self._events_filter_messages[events_filter_id]

    def clear_events_filters(self) -> None:
        message: dict = {
            "type": "clear",
            "args": {}
        }

        self.send(json.dumps(message))
        with self._initial_messages_lock:
            self._events_filter_messages = {}

    def subscribe_scope(self, scope_id: str):
        message = self._get_subscribe_scope_message(scope_id)
        self.send(json.dumps(message))
        with self._initial_messages_lock:
            self._scopes.append(scope_id)

    def remove_scope(self, scope_id: str):
        """
        This only removes the scope from the internal list since there is no 'unsubscribe'. You need to
        restart the websocket for this change to take effect.
        """
        with self._initial_messages_lock:
            self._scopes.remove(scope_id)

    ###################################################################################################################
    # Token refresh thread
    ###################################################################################################################

    def _set_next_token_refresh(self):
        if self._api_handler.refresh_time() is not None:
            # make seconds
            timestamp = self._api_handler.refresh_time() / 1000

            self._token_scheduler.add_job(
                func=lambda: self._token_refresh_thread(),
                trigger='date',
                run_date=datetime.fromtimestamp(timestamp),
                id='token_refresh_thread',
                replace_existing=True)

    def _token_refresh_thread(self):
        logger.debug("Updating token for session")

        message: dict = {
            "type": "token",
            "args": {
                "_TOKEN": self._api_handler.token
            }
        }

        self.send(json.dumps(message))

        self._set_next_token_refresh()

    ###################################################################################################################
    # Sending messages
    ###################################################################################################################
    #
    # This is not needed, since events are only received, not sent.
    #
    # def send_events_message(self, events_type: str, headers: dict, body: dict) -> str:
    #     uuid: str = uuid4().hex
    #
    #     message: dict = {
    #         "id": uuid,
    #         "type": events_type,
    #         "headers": headers,
    #         "body": body
    #     }
    #
    #     self.send(json.dumps(message))
    #
    #     return uuid


###################################################################################################################
# Exceptions
###################################################################################################################

class WebSocketFilterException(WebSocketException):
    """
    On errors with setting or parsing filter information.
    """
    pass
