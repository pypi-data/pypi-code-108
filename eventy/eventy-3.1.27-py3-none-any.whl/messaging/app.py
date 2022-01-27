# Copyright (c) Qotto, 2021

from __future__ import annotations

import logging
import threading
import time
from threading import Thread
from typing import Optional, Iterable, Callable

from eventy.messaging.agent import Agent, Handler, Guarantee
from eventy.messaging.service import Service
from eventy.messaging.store import Cursor, RecordStore, RecordWriteStore, RecordStoreWithInitialization
from eventy.record import Record, Response, RecordType
from eventy.trace_id.local import local_trace

__all__ = [
    'EventyApp',
]

logger = logging.getLogger(__name__)


class EventyApp:
    """
    EventyApp is the messaging application.
    """

    def __init__(
        self,
        record_store: RecordStore,
        app_service: Service,
        ext_services: Iterable[Service] = None,
        agents: Iterable[Agent] = None,
        handlers: Iterable[Handler] = None,
        read_batch_size: int = 1,
        read_timeout_ms: Optional[int] = None,
        read_wait_time_ms: Optional[int] = None,
        write_timeout_ms: Optional[int] = None,
        ack_timeout_ms: Optional[int] = None,
        commit_timeout_ms: Optional[int] = None,
    ):
        """
        Create and initialize EventyApp.

        The record store will be initialized if needed.
        """
        self._record_store = record_store
        self._app_service = app_service
        self._ext_services = ext_services or []
        self._all_handlers = list()
        if handlers is not None:
            for handler in handlers:
                self._all_handlers.append(handler)
        if agents is not None:
            for agent in agents:
                for handler in agent.handlers:
                    self._all_handlers.append(handler)

        self._read_batch_size = read_batch_size
        self._read_timeout_ms = read_timeout_ms
        self._write_timeout_ms = write_timeout_ms
        self._ack_timeout_ms = ack_timeout_ms
        self._commit_timeout_ms = commit_timeout_ms
        self._read_wait_time_ms = read_wait_time_ms or 0

        self._write_store = _AppRecordWriteStore(self)

        self._cancelled = False

        self._initialize()

    @property
    def write_store(self) -> RecordWriteStore:
        """
        The write store to write records directly without transaction management.
        """
        return self._write_store

    def _initialize(self) -> None:

        # Initialize: register topics to store
        logger.info(f"Initializing EventyApp {self._app_service.name}.")
        topics_to_register = self._get_topics_to_register()
        logger.info(f"Registering {len(topics_to_register)} topics: {', '.join(topics_to_register)}.")
        for topic in topics_to_register:
            self._record_store.register_topic(topic, Cursor.ACKNOWLEDGED)

        # Initialize: initialize store if needed
        if isinstance(self._record_store, RecordStoreWithInitialization):
            logger.info(f"Initializing RecordStore.")
            self._record_store.initialize()

        # Cancel immediately if no topics to read from
        if not self._record_store.topics:
            logger.info(f"No topics to read from, cancelling app.")
            self.cancel()

    def run_until_cancelled(self) -> None:
        """
        Run EventyApp until it is cancelled.

        This method will block until the app is cancelled.

        :return: None if the app was cancelled.
        :raises: Exception if an exception occurred processing records.
        """
        logger.info(f"EventyApp {self._app_service.name} started.")
        while not self._cancelled:
            self._process_one_batch()
        logger.info(f"EventyApp {self._app_service.name} stopped after being cancelled.")

    def run(
        self,
        done_callback: Callable[[Optional[BaseException]], None] = None,
    ) -> None:
        """
        Run EventyApp in a separate thread.

        The app will be cancelled when the thread calling this method is stopped.

        If an exception is raised processing records, the callback will be called with the exception.
        If the app is otherwise cancelled, the callback will be called with None.

        :param done_callback: Callback to be called when the app is done.
        """
        calling_thread = threading.current_thread()

        def _run_then_callback():
            logger.info(f"Starting EventyApp {self._app_service.name}.")

            try:
                while not self._cancelled:
                    self._process_one_batch()
                    if not calling_thread.is_alive():
                        logger.info(f"Calling thread died. Cancelling EventyApp {self._app_service.name}.")
                        self.cancel()

            except BaseException as e:
                logger.exception(f"Error processing records in EventyApp {self._app_service.name}.")
                if done_callback:
                    done_callback(e)

            else:
                logger.info(f"EventyApp {self._app_service.name} stopped.")
                if done_callback:
                    done_callback(None)

        thread = Thread(target=_run_then_callback)
        thread.start()

    def cancel(self) -> None:
        """
        Cancel EventyApp, current batch will be processed.
        """
        logger.info(f"Cancelling EventyApp {self._app_service.name}.")
        if self._cancelled:
            logger.info(f"App was already cancelled.")
        else:
            self._cancelled = True

    def _process_one_record_one_handler(self, record: Record, handler: Handler) -> None:
        """
        Process a single record and write possible responses.

        :raises Exception: If the handler fails to process the record.
        """
        logger.debug(
            f"Processing record {record.qualified_name} data={record.data} with handler {handler}."
        )
        for output_record in handler.handle_record(record):
            topic = self._get_topic_for_record(output_record)
            logger.debug(
                f"Writing output record {record.qualified_name} on topic {topic} with data={record.data}."
            )
            self._record_store.write(output_record, topic, self._write_timeout_ms, )

    def _process_one_batch(self) -> None:
        """
        Read an process the next batch of records.

        :raises Exception: If some handler failed.
        """
        records = list(
            self._record_store.read(
                max_count=self._read_batch_size,
                timeout_ms=self._read_timeout_ms,
                auto_ack=False,
            )
        )
        if records:
            logger.debug(f"Received {len(records)} new records.")
        else:
            time.sleep(self._read_wait_time_ms / 1000)
            return

        # At Least Once
        for record in records:
            with local_trace(correlation_id=record.correlation_id):
                for handler in self._get_handlers_for_record(record, Guarantee.AT_LEAST_ONCE):
                    self._process_one_record_one_handler(record, handler)

        # Exactly Once
        self._record_store.start_transaction()
        self._record_store.ack(self._ack_timeout_ms)
        for record in records:
            with local_trace(correlation_id=record.correlation_id):
                for handler in self._get_handlers_for_record(record, Guarantee.EXACTLY_ONCE):
                    self._process_one_record_one_handler(record, handler)
        self._record_store.commit(self._commit_timeout_ms)

        # At Most Once
        for record in records:
            with local_trace(correlation_id=record.correlation_id):
                for handler in self._get_handlers_for_record(record, Guarantee.AT_MOST_ONCE):
                    self._process_one_record_one_handler(record, handler)

    def _get_service_for_name(self, service_name: Optional[str]):
        if service_name is None:
            return self._app_service
        for service in self._ext_services:
            if service.name == service_name:
                return service
        raise ValueError(f"Service {service_name} not found.")

    def _get_topics_to_register(self) -> list[str]:
        topics: set[str] = set()
        for handler in self._all_handlers:
            service = self._get_service_for_name(handler.service_name)
            topic = service.topic_for(handler.record_type)
            logger.info(f"Found handler {handler}. Will listen topic {topic}.")
            topics.add(topic)
        return list(sorted(topics))

    def _get_handlers_for_record(self, record: Record, guarantee: Guarantee) -> list[Handler]:
        handlers: list[Handler] = list()
        for handler in self._all_handlers:
            if (
                handler.record_type == record.type
                and handler.record_name == record.name
                and handler.delivery_guarantee == guarantee
                and self._get_service_for_name(handler.service_name).namespace == record.namespace
            ):
                if isinstance(record, Response):
                    if record.destination == self._app_service.namespace:
                        handlers.append(handler)
                else:
                    handlers.append(handler)
        return handlers

    def _get_topic_for_record(self, record: Record) -> str:
        if record.type == RecordType.EVENT or record.type == RecordType.RESPONSE:
            return self._app_service.topic_for(record.type)
        for service in self._ext_services:
            if service.namespace == record.namespace:
                return service.topic_for(record.type)
        raise ValueError(f"No topic for record {record}.")


class _AppRecordWriteStore(RecordWriteStore):
    """
    A RecordWriteStore implementation which delegates routing to correct topic to the EventyApp.
    """

    def __init__(self, app: EventyApp):
        self._app = app

    def write(self, record: Record) -> None:
        with local_trace(correlation_id=record.correlation_id):
            topic = self._app._get_topic_for_record(record)
            logger.debug(f"Writing record {record.qualified_name} data={record.data} to topic: {topic}.")
            self._app._record_store.write_now(
                record,
                topic,
                self._app._write_timeout_ms,
            )
