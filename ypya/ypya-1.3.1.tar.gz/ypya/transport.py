'''
ypya.transport
'''
try:
    from amqplib.client_0_8 import Connection, Message
    BACKEND_NAME = 'amqplib'
except ImportError:
    from amqp import Connection, Message
    BACKEND_NAME = 'amqp'


class AMQPTransport(object):
    '''
    A socket-like interface
    '''

    DEFAULT_CREDENTIAL = ('guest', 'guest')
    DEFAULT_HOSTNAME = 'localhost'
    DEFAULT_PORT = 5672
    DEFAULT_VHOST = '/'
    DEFAULT_EXCHANGE_NAME = 'gelf.exchange'
    DEFAULT_EXCHANGE_TYPE = 'fanout'
    DEFAULT_ROUTING_KEY = ''

    DEFAULT_CONNECTION_TIMEOUT = 1

    DELIVERY_MODE_TRANSIENT  = 1
    DELIVERY_MODE_PERSISTENT = 2

    def __init__(self):
        super(AMQPTransport, self).__init__()
        self.timeout = self.DEFAULT_CONNECTION_TIMEOUT
        self.delivery_mode = self.DELIVERY_MODE_PERSISTENT
        self.backend_name = BACKEND_NAME

    def getSocket(self, parent, conn_args):
        '''
        :param parent: (object)
        :param conn_args: (dict)
        '''
        self.exchange_name = parent.exchange_name
        self.routing_key = parent.routing_key
        is_durable_exchange = getattr(
            parent,
            'exchange_durable',
            True
        )
        allow_auto_deletion = getattr(
            parent,
            'exchange_auto_delete',
            not(is_durable_exchange)
        )

        self._conn = Connection(
            connection_timeout=self.timeout,
            **conn_args
        )
        try:
            self._conn.connect()
        except AttributeError:
            # ignore this due to API differences between backends.
            pass
        self._channel = self._conn.channel()
        self._channel.exchange_declare(
            exchange=self.exchange_name,
            type=parent.exchange_type,
            durable=is_durable_exchange,
            auto_delete=allow_auto_deletion,
        )
        return self

    def sendall(self, data):
        '''
        public method

        :param data: (obj)
        '''
        pack = Message(
            data,
            delivery_mode=self.delivery_mode,
        )
        self._channel.basic_publish(
            pack,
            exchange=self.exchange_name,
            routing_key=self.routing_key,
        )
        return None

    def close(self):
        '''
        public method
        '''
        try:
            self._conn.close()
        except Exception:
            pass
