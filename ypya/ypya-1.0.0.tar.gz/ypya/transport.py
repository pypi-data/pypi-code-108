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

    def __init__(self):
        super(AMQPTransport, self).__init__()
        self.backend_name = BACKEND_NAME
