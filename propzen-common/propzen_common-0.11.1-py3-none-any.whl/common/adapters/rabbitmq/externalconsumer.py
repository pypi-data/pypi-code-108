import os
from typing import Any
from pika.exchange_type import ExchangeType
from pika.exceptions import ConnectionClosedByBroker, AMQPChannelError, AMQPConnectionError
from tenacity import retry_if_exception_type, wait_fixed, Retrying, RetryCallState

from propzen.common.service_layer.externalbus import ExternalEventHandler
from propzen.common.adapters.rabbitmq.connection import Connection


class RabbitConsumer:
    exchange: str = 'propzen.direct'

    def __init__(self, queue_name: str, bus: Connection, logger: Any):
        self.queue_name = queue_name
        self.bus = bus
        self.handlers = {}
        self.types = {}
        self.logger = logger
        self.is_running = False

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.dispose()

    def run_consume_with_retry(self):
        def reconnect_before(retry_state: RetryCallState):
            self.logger.info('Reconnecting...')
            self.dispose()

        retry_consume = Retrying(
            retry=(
                retry_if_exception_type(ConnectionClosedByBroker) |
                retry_if_exception_type(AMQPChannelError) |
                retry_if_exception_type(AMQPConnectionError)),
            wait=wait_fixed(5),
            before=reconnect_before,
        )

        retry_consume(self.run_consume)

    def run_consume(self):
        try:
            self.logger.info('Starting consumer...')

            self.bus.open_channel()
            self.logger.info('Channel opened...')

            self.bus.channel.exchange_declare(
                exchange=RabbitConsumer.exchange,
                exchange_type=ExchangeType.direct,
                durable=True)
            self.logger.info('Exchange declared...')

            self.bus.channel.queue_declare(
                queue=self.queue_name,
                durable=True)
            self.logger.info(f'Queue {self.queue_name} declared...')

            self._bindhandlers()

            self.bus.channel.basic_consume(
                queue=self.queue_name,
                on_message_callback=self._process_event)

            self.bus.channel.start_consuming()
            self.is_running = True
            self.logger.info('Consumer started...')
        except KeyboardInterrupt:
            self.dispose()
            self.logger.info('Closing rabbitmq consumer...')
            os._exit(0)

    def dispose(self):
        if self.is_running:
            self._unbindhandlers()
            self.bus.channel.stop_consuming()
        self.bus.close()
        self.is_running = False

    def add_handlers(self, handlers: ExternalEventHandler):
        for eventtype, handler in handlers.mapping.items():
            eventname = eventtype.routingkey()
            self.types[eventname] = eventtype
            self.handlers[eventname] = handler

    def _process_event(self, channel, method, properties, body):
        eventname = method.routing_key
        eventjson = body.decode('utf-8')
        event = self.types[eventname].from_json(eventjson)
        self.logger.info(
            'external event received',
            externalevent=method.routing_key,
            **event.to_dict())
        try:
            self.handlers[eventname](event)
            channel.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as exc:
            self.logger.exception(exc, externalevent=method.routing_key)

    def _bindhandlers(self):
        for eventname in self.handlers:
            self.bus.channel.queue_bind(
                exchange=RabbitConsumer.exchange,
                queue=self.queue_name,
                routing_key=eventname
            )
            self.logger.info(
                f'{eventname} event bound to {self.queue_name}.')

    def _unbindhandlers(self):
        for eventname in self.handlers:
            self.bus.channel.queue_unbind(
                queue=self.queue_name,
                exchange=RabbitConsumer.exchange,
                routing_key=eventname)
