import json
import logging
import random
import ssl
import threading
import time
from abc import abstractmethod
from enum import Enum
from typing import List, Dict, Optional
from urllib.parse import urlencode

from websocket import WebSocketApp, ABNF, WebSocketException, setdefaulttimeout, WebSocketConnectionClosedException, \
    STATUS_NORMAL, STATUS_UNEXPECTED_CONDITION

from hiro_graph_client.clientlib import AbstractTokenApiHandler

logger = logging.getLogger(__name__)
""" The logger for this module """


class ErrorMessage:
    """
    The structure of an incoming error message
    """
    code: int
    message: str

    def __init__(self,
                 code,
                 message):
        """
        Constructor

        :param code: Numerical error code of the error
        :param message: Error message
        """
        self.code = int(code)
        self.message = str(message)

    @classmethod
    def parse(cls, message: str):
        """
        :param message: The message received from the websocket. Will be decoded here.
        :return: The new error message or None if this is not an error message.
        """
        json_message: dict = json.loads(message)
        error_message = json_message.get('error')
        if isinstance(error_message, dict):
            return cls(error_message.get('code'),
                       error_message.get('message'))
        else:
            return None

    def __str__(self):
        return json.dumps(vars(self))

    def to_dict(self) -> dict:
        return {
            "error": {
                "code": self.code,
                "message": self.message
            }
        }


class ReaderStatus(str, Enum):
    """
    The states the reader thread can be in.
    """
    NONE = 'Not started',
    STARTING = 'Starting',
    RUNNING_PRELIMINARY = 'Running preliminary (status of token unknown)',
    RUNNING = 'Running'
    RESTARTING = 'Restarting',
    DONE = 'Finished normally',
    FAILED = 'Finished because of error'


class AbstractAuthenticatedWebSocketHandler:
    """
    The basic class for all WebSockets.
    """
    _api_handler: AbstractTokenApiHandler
    _proxy_hostname: str
    _proxy_port: str
    _proxy_auth: dict

    _reconnect_delay: int

    _protocol: str
    _url: str

    _auto_reconnect: bool

    _ws: Optional[WebSocketApp] = None

    _reader_status: ReaderStatus
    """
    Tracks the status of the internal reader thread.  
    """
    _reader_guard: threading.Condition
    """
    Meant to protect the startup sequence. *
    """
    _ws_guard: threading.RLock
    """
    Protects the websocket reference for startup and restart.
    """

    _backoff_condition: threading.Condition

    _remote_exit_codes: List[int] = []
    """ A list of remote exit codes that will cause the websocket to not reconnect."""

    MAX_RETRIES = 3

    def __init__(self,
                 api_handler: AbstractTokenApiHandler,
                 api_name: str,
                 query_params: Dict[str, str] = None,
                 timeout: int = 5,
                 auto_reconnect: bool = True,
                 remote_exit_codes: List[int] = None):
        """
        Create the websocket

        :param api_handler: Required: The api handler for authentication.
        :param api_name: The name of the ws api.
        :param query_params: URL Query parameters for this specific websocket. Use Dict[str,str] only here,
                             i.e. set {"allscopes": "false"} instead of {"allscopes": False}.
        :param timeout: The timeout for websocket messages. Default is 5sec.
        :param auto_reconnect: Try to create a new websocket automatically when *self.send()* fails. If this is set
                               to False, a WebSocketException will be raised instead. The default is True.
        :param remote_exit_codes: A list of close codes that can come in from the remote side. If one of the codes in
                                  this list matches the remote close code, *self.run_forever()* will exit instead of
                                  trying to reconnect. The default is None -> reconnect always.
                                  See https://datatracker.ietf.org/doc/html/rfc6455#section-7.4.1
        """
        if not api_handler:
            raise ValueError('Parameter api_handler= cannot be empty.')

        if not api_name:
            raise ValueError('Parameter api_name= cannot be empty.')

        self._url, self._protocol, self._proxy_hostname, self._proxy_port, self._proxy_auth = \
            api_handler.get_websocket_config(api_name)

        if query_params:
            self._url += '?' + urlencode(query_params, safe="/,")

        self._api_handler = api_handler

        self._auto_reconnect = auto_reconnect

        self._reader_status = ReaderStatus.NONE
        self._reader_guard = threading.Condition()

        self._ws_guard = threading.RLock()
        self._backoff_condition = threading.Condition()

        if remote_exit_codes:
            self._remote_exit_codes = remote_exit_codes

        setdefaulttimeout(timeout)

        random.seed(time.time_ns())

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.stop()

    def _set_error(self, error: Exception) -> None:
        """
        Log the Exception, store it and set the status to FAILED.

        :param error: The Exception to store.
        """
        self._reader_status = ReaderStatus.FAILED
        logger.error("Reader encountered error: %s %s", error.__class__.__name__, str(error))

    def _check_message(self, ws: WebSocketApp, message: str) -> None:
        """
        Look for error 401. Try to reconnect with a new token when this is encountered.
        Set status to *ReaderStatus.RESTARTING* when a token is no longer valid on error code 401.
        Set status to *ReaderStatus.FAILED* when error 401 is received and the token was never valid.

        :param ws: WebSocketApp
        :param message: Incoming message as string
        """
        try:
            with self._reader_guard:
                error_message = ErrorMessage.parse(message)
                if error_message:
                    if error_message.code == 401:
                        if self._reader_status == ReaderStatus.RUNNING_PRELIMINARY:
                            raise WebSocketException(
                                "Received error message while token was never valid: " + str(error_message))
                        else:
                            self._api_handler.refresh_token()

                            # If we get here, the token has been refreshed successfully.
                            self._reconnect_delay = 0
                            self._reader_status = ReaderStatus.RESTARTING

                            logger.info("Refreshing token because of error: %s", str(error_message))
                            self._close(reason=f"{self._api_handler.user_agent} token refresh.")
                            return
                else:
                    if logger.isEnabledFor(logging.DEBUG):
                        logger.debug("Received message: %s", message)
                    else:
                        logger.info("Received message of length %d", len(message))

            self.on_message(ws, message)

            with self._reader_guard:
                # If we get here, the token is valid
                if self._reader_status not in [ReaderStatus.RUNNING, ReaderStatus.FAILED]:
                    self._reader_status = ReaderStatus.RUNNING
                    self._reconnect_delay = 0

        except Exception as err:
            self._set_error(err)
            self._close(status=STATUS_UNEXPECTED_CONDITION,
                        reason="Exception while handling incoming text message.")

    def _check_open(self, ws: WebSocketApp) -> None:
        """
        First signal, that the connection has been opened successfully. Then
        call *self.on_open* and set *self._reader_status* to CHECKING_TOKEN if opening succeeded.

        :param ws: WebSocketApp
        """
        logger.debug("Connection to %s open.", self._url)

        try:
            with self._reader_guard:
                self._reader_status = ReaderStatus.RUNNING_PRELIMINARY

            self.on_open(ws)
        except Exception as err:
            self._set_error(err)
            self._close(status=STATUS_UNEXPECTED_CONDITION,
                        reason="Exception while handling open message.")

    def _check_close(self, ws: WebSocketApp, code: int, reason: str):
        """
        Call *self.on_close*. When *code* and *reason* are None, the stop has been issued locally and not by the
        remote side.

        :param ws: WebSocketApp
        :param code: Code of stop message
        :param reason: Reason str of stop message
        """
        try:
            with self._reader_guard:
                if code or reason:
                    if code in self._remote_exit_codes or self._reader_status in [ReaderStatus.DONE,
                                                                                  ReaderStatus.FAILED]:
                        logger.debug("Received close from remote: %s %s. Closing...", code, reason)
                    else:
                        logger.debug("Received close from remote: %s %s. Restarting...", code, reason)
                        self._reader_status = ReaderStatus.RESTARTING
                else:
                    logger.debug("Received local close. Exiting...")

            self.on_close(ws, code, reason)
        except Exception as err:
            self._set_error(err)

    def _check_error(self, ws: WebSocketApp, error: Exception) -> None:
        """
        Just log the error and propagate it to *self.on_error*.

        :param ws: WebSocketApp
        :param error: Exception
        """
        # logger.error("Received error: %s", str(error))
        # logger.exception(error)

        try:
            # A '[Errno 9] Bad file descriptor' is expected when closing the websocket
            # internally.
            with self._reader_guard:
                if self._reader_status == ReaderStatus.DONE and isinstance(error, OSError) and error.errno == 9:
                    return

            self._set_error(error)
            self.on_error(ws, error)
        except Exception as err:
            self._set_error(err)

    def _backoff(self, reconnect_delay: int) -> int:
        """
        Sleeps for *reconnect_delay* seconds, then returns the delay in seconds for the next try.

        :param reconnect_delay: Delay in seconds to wait.
        :return: Next value for the delay.
        """
        with self._backoff_condition:
            if reconnect_delay:
                self._backoff_condition.wait(timeout=reconnect_delay)

        return (reconnect_delay + 1) if reconnect_delay < 10 \
            else (reconnect_delay + 10) if reconnect_delay < 60 \
            else random.randint(60, 600)

    def _close(self, status: str = STATUS_NORMAL, reason: str = None):
        """
        Close the websocket.

        :param status: Status code for close message.
        :param reason: The close message.
        """
        with self._ws_guard:
            if self._ws:
                self._ws.close(status=status,
                               reason=reason if reason else f"{self._api_handler.user_agent} closing")

    ###############################################################################################################
    # Public API Reader thread
    ###############################################################################################################

    @abstractmethod
    def on_open(self, ws: WebSocketApp):
        pass

    @abstractmethod
    def on_close(self, ws: WebSocketApp, code: int = None, reason: str = None):
        pass

    @abstractmethod
    def on_message(self, ws: WebSocketApp, message: str):
        pass

    @abstractmethod
    def on_error(self, ws: WebSocketApp, error: Exception):
        pass

    ###############################################################################################################
    # Public API Main Writer thread
    ###############################################################################################################

    def start(self) -> None:
        """
        Create the WebSocketApp

        :raise WebSocketException: When the creation of the WebSocketApp fails.
        """

        try:
            with self._ws_guard:
                self._ws = WebSocketApp(self._url,
                                        header={
                                            "Sec-WebSocket-Protocol":
                                                f"{self._protocol}, token-{self._api_handler.token}"
                                        },
                                        on_open=lambda ws: self._check_open(ws),
                                        on_close=lambda ws, code, reason: self._check_close(ws, code, reason),
                                        on_message=lambda ws, msg: self._check_message(ws, msg),
                                        on_error=lambda ws, _err: self._check_error(ws, _err),
                                        on_ping=lambda ws, data: ws.send(data, opcode=ABNF.OPCODE_PONG))

        except Exception as err:
            raise WebSocketException("Cannot create WebSocketApp.") from err

    def _stop(self, wait_for_shutdown: bool = True) -> None:
        """
        Intentionally closes this websocket. When called by the same thread as *self.run_forever()*
        (i.e. by signal handler), *wait_for_shutdown* needs to be set to False or the method will deadlock.

        :param wait_for_shutdown: Wait until *self.run_forever()* has returned. Default is True.
        """
        with self._ws_guard:
            if not self._ws:
                return

        with self._reader_guard:
            self._reader_status = ReaderStatus.DONE
            self._close()
            with self._backoff_condition:
                self._backoff_condition.notify()
            if wait_for_shutdown:
                self._reader_guard.wait()

    def stop(self) -> None:
        """
        Intentionally closes this websocket and waits for *self.run_forever()* to return. Call this from another thread
        than *self.run_forever()*.
        """
        self._stop(wait_for_shutdown=True)

    def signal_stop(self) -> None:
        """
        Intentionally closes this websocket without waiting. This is meant to be used in signal handlers.
        """
        self._stop(wait_for_shutdown=False)

    def restart(self) -> None:
        """
        Closes the websocket and starts a new one. This needs to be called from another thread than
        *self.run_forever()* or it will deadlock.

        :raise RuntimeError: When no *self._ws* exists.
        """
        with self._ws_guard:
            if not self._ws:
                raise RuntimeError('There is no websocket to restart.')

        with self._reader_guard:
            self._reader_status = ReaderStatus.RESTARTING
            self._close()
            with self._backoff_condition:
                self._backoff_condition.notify()
            self._reader_guard.wait()

    def run_forever(self):
        """
        Runs and receives incoming messages.
        """
        with self._reader_guard:
            self._reader_status = ReaderStatus.STARTING
            self._reconnect_delay = 0

            while self._reader_status not in [ReaderStatus.DONE, ReaderStatus.FAILED]:

                try:
                    self._reader_guard.notify_all()
                    self._reader_guard.release()
                    self._ws.run_forever(http_proxy_host=self._proxy_hostname,
                                         http_proxy_port=self._proxy_port,
                                         http_proxy_auth=self._proxy_auth,
                                         sslopt={
                                             "cert_reqs": ssl.CERT_NONE
                                         } if AbstractTokenApiHandler.accept_all_certs else None)

                except Exception as error:
                    self._check_error(self._ws, error)
                finally:
                    self._reader_guard.acquire()

                self._reconnect_delay = self._backoff(self._reconnect_delay)

            self.on_close(self._ws)

            with self._ws_guard:
                self._ws = None

            self._reader_guard.notify_all()

    def is_active(self) -> bool:
        """
        Checks whether the websocket is still active.
        :return: self._reader_status not in [ReaderStatus.NONE, ReaderStatus.DONE, ReaderStatus.FAILED]
        """
        with self._reader_guard:
            return self._reader_status not in [ReaderStatus.NONE, ReaderStatus.DONE, ReaderStatus.FAILED]

    def send(self, message: str) -> None:
        """
        Send message across the websocket.

        :param message: Message as string
        :raise WebSocketException: When *self._auto_reconnect* is False: If a message cannot be sent and all retries
                                   have been exhausted.
        :raise WebSocketConnectionClosedException: When the websocket is not available at all.
        """
        retries = 0
        retry_delay = 0

        while True:
            retry_delay = self._backoff(retry_delay)

            try:
                with self._reader_guard:
                    if self._reader_status in [ReaderStatus.NONE]:
                        raise WebSocketConnectionClosedException('Websocket not started.')
                    elif self._reader_status in [ReaderStatus.DONE, ReaderStatus.FAILED]:
                        raise WebSocketConnectionClosedException('Websocket has exited.')
                    elif self._reader_status not in [ReaderStatus.RUNNING, ReaderStatus.RUNNING_PRELIMINARY]:
                        raise WebSocketException('Websocket not ready.')

                with self._ws_guard:
                    if not self._ws:
                        raise WebSocketConnectionClosedException('Websocket is gone.')

                    if logger.isEnabledFor(logging.DEBUG):
                        logger.debug("Sending message: %s", message)
                    else:
                        logger.info("Sending message of length %d", len(message))

                    self._ws.send(message)

                return

            except WebSocketConnectionClosedException:
                raise

            except Exception as err:
                if retries >= self.MAX_RETRIES:
                    if self._auto_reconnect:
                        retries = 0
                        logger.warning('Restarting because of error: %s', str(err))
                        self.restart()
                    else:
                        raise WebSocketException("Could not send and all retries have been exhausted.")
                else:
                    logger.warning('Retrying to send message because of error: %s', str(err))
                    retries += 1
