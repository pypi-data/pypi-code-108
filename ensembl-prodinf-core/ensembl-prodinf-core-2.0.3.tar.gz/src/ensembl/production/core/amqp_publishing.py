#    See the NOTICE file distributed with this work for additional information
#    regarding copyright ownership.
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#        http://www.apache.org/licenses/LICENSE-2.0
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

from contextlib import contextmanager
import logging
from kombu import Connection, Exchange
from kombu.pools import producers


OPTIONS = {
    'serializer': 'json',
    'delivery_mode': 2,
    'retry': True,
    # 'compression': 'zlib',
    'retry_policy': {
        'interval_start': 0,
        'interval_step': 2,
        'interval_max': 30,
        'max_retries': 5
    }
}


logger = logging.getLogger(__name__)


class AMQPPublisher:
    """Simple publisher for connecting and publishing messages to a AMQP broker exchange.
    An optional formatter instance can be passed in order to format the message before sending it,
    (it must implement a method named `format`).
    Connections are lazy and stored in a global pool so that AMQPPublisher instances with the same uri
    in the same process will use the same connection object.
    The additional kwargs `options` are passed as additional parameters to kombu.Producer.publish
    please refer to: https://kombu.readthedocs.io/en/latest/userguide/producers.html#reference
    """
    def __init__(self, uri, exchange_name, exchange_type='topic', routing_key=None, formatter=None, **options):
        self.routing_key = routing_key
        self.formatter = formatter
        self.options = {**OPTIONS, **options}
        self.connection = Connection(uri, transport_options=self.options.get('retry_policy'))
        self.exchange = Exchange(exchange_name, type=exchange_type)


    class AMQPProducer:
        def __init__(self, producer, exchange, routing_key, formatter, options):
            self.producer = producer
            self.exchange = exchange
            self.routing_key = routing_key
            self.formatter = formatter
            self.options = options

        def publish(self, msg, routing_key=None):
            body = self.formatter.format(msg) if self.formatter is not None else msg
            key = routing_key if routing_key else self.routing_key
            if not key:
                raise ValueError('Invalid routing_key: {} (Producer routing_key is: {})'.format(
                    routing_key, self.routing_key
                    ))
            logger.debug(
                "Publishing message: %s, %s, Routing Key: %s, options: %s", body, self.exchange, key, self.options
            )
            self.producer.publish(body,
                                  exchange=self.exchange,
                                  routing_key=key,
                                  declare=(self.exchange,),
                                  **self.options)
            logger.debug(
                'Published AMQP message: %s, %s, Routing Key: %s', body, self.exchange, key
            )


    @contextmanager
    def acquire_producer(self, block=True):
        """Acquire a producer from the global pool for holding a connection/channel while publishing.
        Useful for removing the overhead of acquiring a producer from the global pool when
        publishing several messages in a row.
        """
        with producers[self.connection].acquire(block=block) as producer:
            logger.debug('Acquired producer for connection %s', self.connection.as_uri())
            yield self.AMQPProducer(producer,
                                    self.exchange,
                                    self.routing_key,
                                    self.formatter,
                                    self.options)
        logger.debug('Released producer for connection %s', self.connection.as_uri())

    def publish(self, msg, routing_key=None):
        """Acquire a producer from the global pool and publish a single message.
        An optional `routing_key` can be passed. If no `routing_key` is passed
        the instance one is used (in that case, if no `routing_key` has been set in the instance)
        a ValueError is raised. Also raises kombu.exceptions.OperationalError if the message
        cannot be delivered accordig to policy specified in this instance (i.e in self.options)
        """
        with self.acquire_producer() as producer:
            producer.publish(msg, routing_key)

