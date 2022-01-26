from ... import Server


class SocketConfig:
    def __init__(self,
                 server: Server,
                 max_reconnect_timeout: float = 5,
                 initial_reconnect_timeout: float = 0.1,
                 **kwargs):
        """
        :kwargs args for https://websockets.readthedocs.io/en/7.0/api.html#websockets.client.connect
        """
        self.server = server
        self.max_reconnect_timeout = max_reconnect_timeout
        self.initial_reconnect_timeout = initial_reconnect_timeout
        self.connection_kwargs = kwargs
