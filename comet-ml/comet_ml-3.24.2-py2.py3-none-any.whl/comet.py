# -*- coding: utf-8 -*-
# *******************************************************
#   ____                     _               _
#  / ___|___  _ __ ___   ___| |_   _ __ ___ | |
# | |   / _ \| '_ ` _ \ / _ \ __| | '_ ` _ \| |
# | |__| (_) | | | | | |  __/ |_ _| | | | | | |
#  \____\___/|_| |_| |_|\___|\__(_)_| |_| |_|_|
#
#  Sign up for free at http://www.comet.ml
#  Copyright (C) 2015-2021 Comet ML INC
#  This file can not be copied and/or distributed without the express
#  permission of Comet ML Inc.
# *******************************************************

"""
Author: Gideon Mendels

This module contains the main components of comet.ml client side

"""
import abc
import logging
import os
import shutil
import sys
import tempfile
import threading
import time
from os.path import basename, splitext

from six.moves.queue import Empty, Queue
from six.moves.urllib.parse import urlencode, urlsplit, urlunsplit

from ._reporting import ON_EXIT_DIDNT_FINISH_UPLOAD_SDK
from ._typing import Any, Dict, List, Optional, Tuple, Union
from .batch_utils import ParametersBatch
from .compat_utils import json_dump
from .config import (
    ADDITIONAL_STREAMER_UPLOAD_TIMEOUT,
    DEFAULT_FILE_UPLOAD_READ_TIMEOUT,
    DEFAULT_PARAMETERS_UPDATE_INTERVAL_SECONDS,
    DEFAULT_STREAMER_MSG_TIMEOUT,
)
from .connection import (
    FileUploadManager,
    FileUploadManagerMonitor,
    format_messages_for_ws,
)
from .exceptions import CometRestApiException
from .file_uploader import is_user_text
from .json_encoder import NestedEncoder
from .logging_messages import (
    CLOUD_DETAILS_MSG_SENDING_ERROR,
    FILE_UPLOADS_PROMPT,
    MODEL_GRAPH_MSG_SENDING_ERROR,
    OS_PACKAGE_MSG_SENDING_ERROR,
    STREAMER_CLOSED_PUT_MESSAGE_FAILED,
    STREAMER_FAILED_TO_PROCESS_ALL_MESSAGES,
    STREAMER_WAIT_FOR_FINISH_FAILED,
    WAITING_DATA_UPLOADED,
)
from .messages import (
    BaseMessage,
    CloseMessage,
    CloudDetailsMessage,
    Message,
    ModelGraphMessage,
    OsPackagesMessage,
    ParameterMessage,
    RemoteAssetMessage,
    SystemDetailsMessage,
    UploadFileMessage,
    UploadInMemoryMessage,
)
from .utils import (
    data_to_fp,
    log_once_at_level,
    wait_for_done,
    write_file_like_to_tmp_file,
)

DEBUG = False
LOGGER = logging.getLogger(__name__)


class BaseStreamer(threading.Thread):

    __metaclass__ = abc.ABCMeta

    def __init__(self, initial_offset, queue_timeout):
        threading.Thread.__init__(self)

        self.counter = initial_offset
        self.messages = Queue()  # type: Queue
        self.queue_timeout = queue_timeout
        self.closed = False
        self.__lock__ = threading.RLock()

        LOGGER.debug("%r instantiated with duration %s", self, self.queue_timeout)

    def put_message_in_q(self, message):
        """
        Puts a message in the queue
        :param message: Some kind of payload, type agnostic
        """
        with self.__lock__:
            if message is not None:
                if not self.closed:
                    LOGGER.debug("Putting 1 %r in queue", message.__class__)
                    self.messages.put(message)
                else:
                    LOGGER.debug(STREAMER_CLOSED_PUT_MESSAGE_FAILED)
                    LOGGER.debug("Ignored message (streamer closed): %s", message)

    def close(self):
        """
        Puts a None in the queue which leads to closing it.
        """
        with self.__lock__:
            if self.closed is True:
                LOGGER.debug("Streamer tried to be closed more than once")
                return

            # Send a message to close
            self.put_message_in_q(CloseMessage())

            self.closed = True

    def _before_run(self):
        pass

    def run(self):
        """
        Continuously pulls messages from the queue and process them.
        """
        self._before_run()

        while True:
            out = self._loop()

            # Exit the infinite loop
            if isinstance(out, CloseMessage):
                break

        self._after_run()

        LOGGER.debug("%s has finished", self.__class__)

        return

    @abc.abstractmethod
    def _loop(self):
        pass

    def _after_run(self):
        pass

    def getn(self, n):
        # type: (int) -> Optional[List[Tuple[BaseMessage, int]]]
        """
        Pops n messages from the queue.
        Args:
            n: Number of messages to pull from queue

        Returns: n messages

        """
        try:
            msg = self.messages.get(
                timeout=self.queue_timeout
            )  # block until at least 1
        except Empty:
            LOGGER.debug("No message in queue, timeout")
            return None

        if isinstance(msg, CloseMessage):
            return [(msg, self.counter + 1)]

        self.counter += 1
        result = [(msg, self.counter)]
        try:
            while len(result) < n:
                another_msg = self.messages.get(
                    block=False
                )  # don't block if no more messages
                self.counter += 1
                result.append((another_msg, self.counter))
        except Exception:
            LOGGER.debug("Exception while getting more than 1 message", exc_info=True)
        return result


class Streamer(BaseStreamer):
    """
    This class extends threading.Thread and provides a simple concurrent queue
    and an async service that pulls data from the queue and sends it to the server.
    """

    def __init__(
        self,
        ws_connection,
        beat_duration,
        connection,
        initial_offset,
        experiment_key,
        api_key,
        run_id,
        project_id,
        rest_api_client,
        worker_cpu_ratio,
        verify_tls,  # type: bool
        pending_rpcs_callback=None,
        msg_waiting_timeout=DEFAULT_STREAMER_MSG_TIMEOUT,
        file_upload_waiting_timeout=ADDITIONAL_STREAMER_UPLOAD_TIMEOUT,
        file_upload_read_timeout=DEFAULT_FILE_UPLOAD_READ_TIMEOUT,
        wait_for_finish_sleep_interval=15,
        parameters_batch_base_interval=DEFAULT_PARAMETERS_UPDATE_INTERVAL_SECONDS,
    ):
        # type: (...) -> None
        super(Streamer, self).__init__(initial_offset, beat_duration / 1000.0)
        self.daemon = True
        self.name = "Streamer(%r)" % (ws_connection)
        self.ws_connection = ws_connection
        self.connection = connection
        self.rest_api_client = rest_api_client

        self.stop_processing = False
        self.on_gpu_monitor_interval = None
        self.on_cpu_monitor_interval = None

        self.on_pending_rpcs_callback = pending_rpcs_callback

        self.last_beat = time.time()
        self.msg_waiting_timeout = msg_waiting_timeout
        self.wait_for_finish_sleep_interval = wait_for_finish_sleep_interval
        self.file_upload_waiting_timeout = file_upload_waiting_timeout
        self.file_upload_read_timeout = file_upload_read_timeout

        self.file_upload_manager = FileUploadManager(worker_cpu_ratio)

        self.experiment_key = experiment_key
        self.api_key = api_key
        self.run_id = run_id
        self.project_id = project_id

        self.verify_tls = verify_tls

        self.parameters_batch = ParametersBatch(parameters_batch_base_interval)

        LOGGER.debug("Streamer instantiated with ws url %s", self.ws_connection)

    def _before_run(self):
        self.ws_connection.wait_for_connection()

    def _loop(self):
        """
        A single loop of running
        """
        try:
            # If we should stop processing the queue, abort early
            if self.stop_processing is True:
                return CloseMessage()

            if self.ws_connection is not None and self.ws_connection.is_connected():
                messages = self.getn(1)

                if messages is not None:
                    LOGGER.debug(
                        "Got %d messages, %d still in queue",
                        len(messages),
                        self.messages.qsize(),
                    )
                    # TODO better group multiple WS messages
                    for (message, offset) in messages:
                        if isinstance(message, CloseMessage):
                            return message
                        elif isinstance(message, UploadFileMessage):
                            self._process_upload_message(message)
                        elif isinstance(message, UploadInMemoryMessage):
                            self._process_upload_in_memory_message(message)
                        elif isinstance(message, RemoteAssetMessage):
                            self._process_upload_remote_asset_message(message)
                        elif isinstance(message, Message):
                            self._process_ws_message(message, offset)
                        elif isinstance(message, ParameterMessage):
                            self._process_parameter_message(message, offset)
                        elif isinstance(message, OsPackagesMessage):
                            self._process_os_package_message(message)
                        elif isinstance(message, ModelGraphMessage):
                            self._process_model_graph_message(message)
                        elif isinstance(message, SystemDetailsMessage):
                            self._process_system_details_message(message)
                        elif isinstance(message, CloudDetailsMessage):
                            self._process_cloud_details_message(message)
                        else:
                            raise ValueError("Unknown message type %r", message)

                # attempt to send collected parameters
                if self.parameters_batch.accept(self._send_ws_message):
                    LOGGER.debug("Parameters batch was sent")

            else:
                LOGGER.debug("WS connection not ready")
                # Basic backoff
                time.sleep(0.5)
        except Exception:
            LOGGER.debug("Unknown streaming error", exc_info=True)

    def _process_upload_message(self, message):
        # type: (UploadFileMessage) -> None
        # Compute the url from the upload type
        url = self.connection.get_upload_url(message.upload_type)

        self.file_upload_manager.upload_file_thread(
            additional_params=message.additional_params,
            api_key=self.api_key,
            clean=message.clean,
            critical=message._critical,
            experiment_id=self.experiment_key,
            file_path=message.file_path,
            metadata=message.metadata,
            project_id=self.project_id,
            timeout=self.file_upload_read_timeout,
            verify_tls=self.verify_tls,
            upload_endpoint=url,
            on_asset_upload=message._on_asset_upload,
            on_failed_asset_upload=message._on_failed_asset_upload,
            estimated_size=message._size,
        )
        LOGGER.debug("Processing uploading message done")

    def _process_upload_in_memory_message(self, message):
        # type: (UploadInMemoryMessage) -> None
        # Compute the url from the upload type
        url = self.connection.get_upload_url(message.upload_type)

        self.file_upload_manager.upload_file_like_thread(
            additional_params=message.additional_params,
            api_key=self.api_key,
            critical=message._critical,
            experiment_id=self.experiment_key,
            file_like=message.file_like,
            metadata=message.metadata,
            project_id=self.project_id,
            timeout=self.file_upload_read_timeout,
            verify_tls=self.verify_tls,
            upload_endpoint=url,
            on_asset_upload=message._on_asset_upload,
            on_failed_asset_upload=message._on_failed_asset_upload,
            estimated_size=message._size,
        )
        LOGGER.debug("Processing in-memory uploading message done")

    def _process_upload_remote_asset_message(self, message):
        # type: (RemoteAssetMessage) -> None
        # Compute the url from the upload type
        url = self.connection.get_upload_url(message.upload_type)

        self.file_upload_manager.upload_remote_asset_thread(
            additional_params=message.additional_params,
            api_key=self.api_key,
            critical=message._critical,
            experiment_id=self.experiment_key,
            metadata=message.metadata,
            project_id=self.project_id,
            remote_uri=message.remote_uri,
            timeout=self.file_upload_read_timeout,
            verify_tls=self.verify_tls,
            upload_endpoint=url,
            on_asset_upload=message._on_asset_upload,
            on_failed_asset_upload=message._on_failed_asset_upload,
            estimated_size=message._size,
        )
        LOGGER.debug("Processing remote uploading message done")

    def _send_ws_message(self, message, offset):
        # type: (Union[Message, ParameterMessage], int) -> None
        """The method to be used as callback for parameters batch processing or to send WS messages immediately"""
        try:
            data = self._serialise_message_for_ws(message=message, offset=offset)
            self.ws_connection.send(data)
        except Exception:
            LOGGER.debug("WS sending error", exc_info=True)

    def _process_parameter_message(self, message, offset):
        # type: (ParameterMessage, int) -> None
        # add message to the parameters batch
        if not self.parameters_batch.append(message=message, offset=offset):
            LOGGER.debug("Failed to add message to the parameters batch: %r" % message)

    def _process_ws_message(self, message, offset):
        # type: (Message, int) -> None
        self._send_ws_message(message, offset)

    def _serialise_message_for_ws(self, message, offset):
        # type: (BaseMessage, int) -> str
        """Enhance provided message with relevant meta-data and serialize it to JSON compatible with WS format"""
        message_dict = message._non_null_dict()

        # Inject online specific values
        message_dict["apiKey"] = self.api_key
        message_dict["runId"] = self.run_id
        message_dict["projectId"] = self.project_id
        message_dict["experimentKey"] = self.experiment_key
        message_dict["offset"] = offset

        return format_messages_for_ws([message_dict])

    def _process_os_package_message(self, message):
        # type: (OsPackagesMessage) -> None
        try:
            self.rest_api_client.set_experiment_os_packages(
                self.experiment_key, message.os_packages
            )
        except CometRestApiException as exc:
            LOGGER.debug(
                OS_PACKAGE_MSG_SENDING_ERROR,
                exc.response.status_code,
                exc.response.content,
            )
        except Exception:
            LOGGER.debug("Error sending os_packages message", exc_info=True)

    def _process_model_graph_message(self, message):
        # type: (ModelGraphMessage) -> None
        try:
            self.rest_api_client.set_experiment_model_graph(
                self.experiment_key, message.graph
            )
        except CometRestApiException as exc:
            LOGGER.debug(
                MODEL_GRAPH_MSG_SENDING_ERROR,
                exc.response.status_code,
                exc.response.content,
            )
        except Exception:
            LOGGER.debug("Error sending model_graph message", exc_info=True)

    def _process_system_details_message(self, message):
        # type: (SystemDetailsMessage) -> None
        try:
            self.rest_api_client.set_experiment_system_details(
                _os=message.os,
                command=message.command,
                env=message.env,
                experiment_key=self.experiment_key,
                hostname=message.hostname,
                ip=message.ip,
                machine=message.machine,
                os_release=message.os_release,
                os_type=message.os_type,
                pid=message.pid,
                processor=message.processor,
                python_exe=message.python_exe,
                python_version_verbose=message.python_version_verbose,
                python_version=message.python_version,
                user=message.user,
            )
        except CometRestApiException as exc:
            LOGGER.debug(
                MODEL_GRAPH_MSG_SENDING_ERROR,
                exc.response.status_code,
                exc.response.content,
            )
        except Exception:
            LOGGER.debug("Error sending model_graph message", exc_info=True)

    def _process_cloud_details_message(self, message):
        # type: (CloudDetailsMessage) -> None
        try:
            self.rest_api_client.set_experiment_cloud_details(
                experiment_key=self.experiment_key,
                provider=message.provider,
                cloud_metadata=message.cloud_metadata,
            )
        except CometRestApiException as exc:
            LOGGER.debug(
                CLOUD_DETAILS_MSG_SENDING_ERROR,
                exc.response.status_code,
                exc.response.content,
            )
        except Exception:
            LOGGER.debug("Error sending cloud details message", exc_info=True)

    def wait_for_finish(self):
        """Blocks the experiment from exiting until all data was sent to server
        OR the configured timeouts has expired."""

        if not self._is_msg_queue_empty():
            log_once_at_level(logging.INFO, WAITING_DATA_UPLOADED)
            log_once_at_level(
                logging.INFO,
                "The Python SDK has %d seconds to finish before aborting...",
                self.msg_waiting_timeout,
            )

            wait_for_done(
                self._is_msg_queue_empty,
                self.msg_waiting_timeout,
                progress_callback=self._show_remaining_messages,
                sleep_time=self.wait_for_finish_sleep_interval,
            )

        if not self._is_msg_queue_empty():
            LOGGER.warning(STREAMER_FAILED_TO_PROCESS_ALL_MESSAGES)

        # From now on, stop processing the message queue as it might contains file upload messages
        # TODO: Find a correct way of testing it
        self.stop_processing = True
        self.file_upload_manager.close()

        # Send all remained parameters from the batch if any
        self.parameters_batch.accept(self._send_ws_message, unconditional=True)

        if not self.file_upload_manager.all_done():
            monitor = FileUploadManagerMonitor(self.file_upload_manager)

            LOGGER.info(FILE_UPLOADS_PROMPT)
            LOGGER.info(
                "The Python SDK has %d seconds to finish before aborting...",
                self.file_upload_waiting_timeout,
            )
            wait_for_done(
                monitor.all_done,
                self.file_upload_waiting_timeout,
                progress_callback=monitor.log_remaining_uploads,
                sleep_time=self.wait_for_finish_sleep_interval,
            )

        if not self._is_msg_queue_empty() or not self.file_upload_manager.all_done():
            remaining = self.messages.qsize()
            remaining_upload = self.file_upload_manager.remaining_uploads()
            LOGGER.error(STREAMER_WAIT_FOR_FINISH_FAILED, remaining, remaining_upload)

            self.connection.report(
                event_name=ON_EXIT_DIDNT_FINISH_UPLOAD_SDK,
                err_msg=(
                    STREAMER_WAIT_FOR_FINISH_FAILED % (remaining, remaining_upload)
                ),
            )

            return False

        self.file_upload_manager.join()

        return True

    def _is_msg_queue_empty(self):
        finished = self.messages.empty()

        if finished is False:
            LOGGER.debug(
                "Message queue not empty, %d messages, closed %s",
                self.messages.qsize(),
                self.closed,
            )
            LOGGER.debug(
                "WS Connection connected? %s %s",
                self.ws_connection.is_connected(),
                self.ws_connection.address,
            )

        return finished

    def _show_remaining_messages(self):
        remaining = self.messages.qsize()
        LOGGER.info("Uploading %d metrics, params and output messages", remaining)

    def has_failed(self):
        # type: (...) -> bool
        return self.file_upload_manager.has_failed()


def compact_json_dump(data, fp):
    return json_dump(data, fp, sort_keys=True, separators=(",", ":"), cls=NestedEncoder)


class OfflineStreamer(BaseStreamer):
    """
    This class extends threading.Thread and provides a simple concurrent queue
    and an async service that pulls data from the queue and sends it to the server.
    """

    def __init__(self, tmp_dir, initial_offset):
        super(OfflineStreamer, self).__init__(initial_offset, 1)
        self.daemon = True
        self.tmp_dir = tmp_dir

        self.file = open(os.path.join(self.tmp_dir, "messages.json"), "wb")

    def _write(self, json_line_message):
        # type: (Dict[str, Any]) -> None
        compact_json_dump(json_line_message, self.file)
        self.file.write(b"\n")
        self.file.flush()

    def _after_run(self):
        # Close the messages files once we are sure we won't write in it
        # anymore
        self.file.close()

    def _loop(self):
        """
        A single loop of running
        """
        try:
            messages = self.getn(1)

            if messages is not None:
                LOGGER.debug(
                    "Got %d messages, %d still in queue",
                    len(messages),
                    self.messages.qsize(),
                )

                for (message, offset) in messages:
                    if isinstance(message, CloseMessage):
                        return message
                    elif isinstance(message, UploadFileMessage):
                        self._process_upload_message(message)
                    elif isinstance(message, UploadInMemoryMessage):
                        self._process_upload_in_memory_message(message)
                    elif isinstance(message, Message):
                        self._process_ws_message(message)
                    elif isinstance(message, ParameterMessage):
                        self._process_parameter_message(message)
                    elif isinstance(message, OsPackagesMessage):
                        self._process_os_package_message(message)
                    elif isinstance(message, ModelGraphMessage):
                        self._process_model_graph_message(message)
                    elif isinstance(message, SystemDetailsMessage):
                        self._process_system_details_message(message)
                    elif isinstance(message, CloudDetailsMessage):
                        self._process_cloud_details_message(message)
                    elif isinstance(message, RemoteAssetMessage):
                        self._process_remote_asset_message(message)
                    else:
                        raise ValueError("Unkown message type %r", message)

        except Exception:
            LOGGER.debug("Unknown streaming error", exc_info=True)

    def _process_upload_message(self, message):
        # type: (UploadFileMessage) -> None
        # Create the file on disk with the same extension if set
        ext = splitext(message.file_path)[1]

        if ext:
            suffix = ".%s" % ext
        else:
            suffix = ""

        tmpfile = tempfile.NamedTemporaryFile(
            dir=self.tmp_dir, suffix=suffix, delete=False
        )
        tmpfile.close()

        if message.clean:
            # TODO: Avoid un-necessary file copy by checking if the file is
            # already at the top-level of self.tmp_di

            # Then move the original file to the newly create file
            shutil.move(message.file_path, tmpfile.name)
        else:
            shutil.copy(message.file_path, tmpfile.name)
            # Mark the file to be cleaned as we copied it to our tmp dir
            message.clean = True

        message.file_path = basename(tmpfile.name)

        msg_json = message.repr_json()
        data = {"type": "file_upload", "payload": msg_json}
        self._write(data)

    def _process_upload_in_memory_message(self, message):
        # type: (UploadInMemoryMessage) -> None

        # We need to convert the in-memory file to a file one
        if is_user_text(message.file_like):
            file_like = data_to_fp(message.file_like)
        else:
            file_like = message.file_like

        tmpfile = write_file_like_to_tmp_file(file_like, self.tmp_dir)

        new_message = UploadFileMessage(
            tmpfile,
            message.upload_type,
            message.additional_params,
            message.metadata,
            clean=True,
            size=message._size,
        )

        return self._process_upload_message(new_message)

    def _process_parameter_message(self, message):
        # type: (ParameterMessage) -> None
        msg_json = message._non_null_dict()

        data = {"type": ParameterMessage.message_type, "payload": msg_json}
        self._write(data)

    def _process_ws_message(self, message):
        # type: (Message) -> None
        msg_json = message._non_null_dict()

        data = {"type": "ws_msg", "payload": msg_json}
        self._write(data)

    def _process_os_package_message(self, message):
        # type: (OsPackagesMessage) -> None
        msg_json = message._non_null_dict()

        data = {"type": "os_packages", "payload": msg_json}
        self._write(data)

    def _process_model_graph_message(self, message):
        # type: (ModelGraphMessage) -> None
        msg_json = message._non_null_dict()

        data = {"type": "graph", "payload": msg_json}
        self._write(data)

    def _process_system_details_message(self, message):
        # type: (SystemDetailsMessage) -> None
        msg_json = message._non_null_dict()

        data = {"type": "system_details", "payload": msg_json}
        self._write(data)

    def _process_cloud_details_message(self, message):
        # type: (CloudDetailsMessage) -> None
        msg_json = message._non_null_dict()

        data = {"type": "cloud_details", "payload": msg_json}
        self._write(data)

    def _process_remote_asset_message(self, message):
        # type: (RemoteAssetMessage) -> None
        msg_json = message._non_null_dict()

        data = {"type": "remote_file", "payload": msg_json}
        self._write(data)

    def wait_for_finish(self):
        """Blocks the experiment from exiting until all data was sent to server OR 30 seconds passed."""

        msg = "Saving offline stats to disk before program termination (may take several seconds)"
        log_once_at_level(logging.INFO, msg)

        # Wait maximum 2 minutes
        self._wait_for_empty(30)

        if not self.messages.empty():
            msg = "Still saving offline stats to disk before program termination (may take several seconds)"
            LOGGER.info(msg)
            self._wait_for_empty(30)

            if not self.messages.empty():
                self._wait_for_empty(60, verbose=True, sleep_time=5)

        if not self.messages.empty():
            remaining = self.messages.qsize()
            LOGGER.info(
                "Comet failed to send all the data back (%s messages)", remaining
            )

        # Also wait for the thread to finish to be sure that all messages are
        # written to the messages file
        self.join(10)

        if self.is_alive():
            LOGGER.info(
                "OfflineStreamer didn't finished in time, messages files might be incomplete"
            )
            return False
        else:
            LOGGER.debug("OfflineStreamer finished in time")
            return True

    def _wait_for_empty(self, timeout, verbose=False, sleep_time=1):
        """Wait up to TIMEOUT seconds for the messages queue to be empty"""
        end_time = time.time() + timeout

        while not self.messages.empty() and time.time() < end_time:
            if verbose is True:
                LOGGER.info("%d messages remaining to upload", self.messages.qsize())
            # Wait a max of sleep_time, but keep checking to see if
            # messages are empty. Allows wait_for_empty to end
            # before sleep_time has elapsed:
            end_sleep_time = time.time() + sleep_time
            while not self.messages.empty() and time.time() < end_sleep_time:
                time.sleep(sleep_time / 20.0)


def get_cmd_args_dict():
    if len(sys.argv) > 1:
        try:
            return parse_cmd_args(sys.argv[1:])

        except ValueError:
            LOGGER.debug("Failed to parse argv values. Falling back to naive parsing.")
            return parse_cmd_args_naive(sys.argv[1:])


def parse_cmd_args_naive(to_parse):
    vals = {}
    if len(to_parse) > 1:
        for i, arg in enumerate(to_parse):
            vals["run_arg_%s" % i] = str(arg)

    return vals


def parse_cmd_args(argv_vals):
    """
    Parses the value of argv[1:] to a dictionary of param,value. Expects params name to start with a - or --
    and value to follow. If no value follows that param is considered to be a boolean param set to true.(e.g --test)
    Args:
        argv_vals: The sys.argv[] list without the first index (script name). Basically sys.argv[1:]

    Returns: Dictionary of param_names, param_values

    """

    def guess_type(s):
        import ast

        try:
            value = ast.literal_eval(s)
            return value

        except (ValueError, SyntaxError):
            return str(s)

    results = {}

    split_argv_vals = []
    for word in argv_vals:
        if word == "--":
            continue  # skip it
        elif "=" in word:
            word_value = word.split("=", 1)
            split_argv_vals.extend(word_value)
        else:
            split_argv_vals.append(word)

    current_key = None
    for word in split_argv_vals:
        word = word.strip()
        prefix = 0

        if word[0] == "-":
            prefix = 1
            if len(word) > 1 and word[1] == "-":
                prefix = 2

            if current_key is not None:
                # if we found a new key but haven't found a value to the previous
                # key it must have been a boolean argument.
                results[current_key] = True

            current_key = word[prefix:]

        else:
            word = word.strip()
            if current_key is None:
                # we failed to parse the string. We think this is a value but we don't know what's the key.
                # fallback to naive parsing.
                raise ValueError("Failed to parse argv arguments")

            else:
                word = guess_type(word)
                results[current_key] = word
                current_key = None

    if current_key is not None:
        # last key was a boolean
        results[current_key] = True

    return results


def is_valid_experiment_key(experiment_key):
    """Validate an experiment_key; returns True or False"""
    return (
        isinstance(experiment_key, str)
        and experiment_key.isalnum()
        and (32 <= len(experiment_key) <= 50)
    )


def format_url(prefix, **query_arguments):
    if prefix is None:
        return None

    splitted = list(urlsplit(prefix))

    splitted[3] = urlencode(query_arguments)

    return urlunsplit(splitted)
