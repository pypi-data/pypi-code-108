from unipipeline.brokers.uni_amqp_py_broker import UniAmqpPyBroker


class RmqBroker(UniAmqpPyBroker):

    @classmethod
    def get_connection_uri(cls) -> str:
        return 'amqp://admin:admin@localhost:25672'
