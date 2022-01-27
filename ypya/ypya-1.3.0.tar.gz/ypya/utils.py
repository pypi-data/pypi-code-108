'''
ypya.utils
'''
from logging import Filter
from logging.handlers import SocketHandler
import socket


from .base import YBase
from .transport import AMQPTransport


class YExclusion(Filter):
    '''
    A simple exclusion filter based on the name of log message sending facility
    '''
    NS_SEP = '.'

    def __init__(self, name):
        assert (name is not None) and (len(name) > 0 ), 'invalid value'
        self.name = name

    def _get_ns_path_root(self, val):
        '''
        :param val: (string)
        :return: (string)
        '''
        tokens = val.split(self.NS_SEP, 1)
        return tokens[0]

    def filter(self, record):
        '''
        public method

        :param record: (obj)
        :return: (boolean)
        '''
        match = (self._get_ns_path_root(record.name) == self.name)
        return not(match)


class YLogHandler(YBase, SocketHandler):
    '''
    A simple logging handler
    '''

    def __init__(
            self,
            broker_host=AMQPTransport.DEFAULT_HOSTNAME,
            broker_port=AMQPTransport.DEFAULT_PORT,
            broker_auth=AMQPTransport.DEFAULT_CREDENTIAL,
            vhost=AMQPTransport.DEFAULT_VHOST,
            exchange_name=AMQPTransport.DEFAULT_EXCHANGE_NAME,
            exchange_type=AMQPTransport.DEFAULT_EXCHANGE_TYPE,
            routing_key=AMQPTransport.DEFAULT_ROUTING_KEY,
            facility=None,
            localname=None,
            fqdn=YBase.INCLUDE_FULLY_QUALIFIED_NAME,
            add_level_name=YBase.INCLUDE_LEVEL_SYMBOLIC_NAME,
            debugging_fields=YBase.INCLUDE_DEBUG_FIELD,
            extra_fields=YBase.INCLUDE_EXTRA_FIELD,
            deep_sanitize=False
    ):

        self.credentials = broker_auth
        self.hostname = broker_host
        self.port = broker_port

        self.vhost = vhost
        self.exchange_name = exchange_name
        self.exchange_type = exchange_type
        self.routing_key = routing_key

        self.transport = AMQPTransport()

        self.sender_host = localname
        self.sender_name = facility
        self.use_fully_qualified_name = fqdn
        self.use_level_name = add_level_name
        self.add_debug_field = debugging_fields
        self.add_extra_field = extra_fields
        self.safe_but_slow = deep_sanitize

        SocketHandler.__init__(
            self,
            host=self.hostname,
            port=self.port
        )
        self.addFilter(
            YExclusion(self.transport.backend_name)
        )

    def setFormatter(self, fmt):
        '''
        public method

        :param fmt: (`logging.Formatter`)
        '''
        self.formatter = fmt

    def makeSocket(self):
        '''
        public method
        '''
        conn_args = {
            'host': '{h}:{p}'.format(
                h=self.hostname,
                p=self.port
            ),
            'userid': self.credentials[0],
            'password': self.credentials[1],
            'vhost': self.vhost,
            'insist': False,
        }

        local_name_unset = (
            (self.sender_host is None)
            or
            (len(self.sender_host) == 0)
        )
        if local_name_unset:
            if self.use_fully_qualified_name:
                refresh_host = socket.getfqdn()
            else:
                refresh_host = socket.gethostname()
            self.sender_host = refresh_host

        return self.transport.getSocket(self, conn_args)
