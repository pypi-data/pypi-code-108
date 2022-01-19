from contextlib import contextmanager
import pika


class Connection:
    """Connection Manager for Rabbit MQ using pika library."""

    exchange: str = 'propzen.direct'

    def __init__(self, bus_url: str) -> None:
        """
        Parameters
        ----------
        bus_url : str
            RabbitMQ URL parameters for pika.URLParameters
        """

        self.connection_params = pika.URLParameters(bus_url)
        self.connection = None
        self.channel = None

    @contextmanager
    def connect(self):
        """Contextually establishes a connection and opens a channel which disposes on exit

        Returns
        -------
        pika.channel.Channel
            yields a connected pika Channel
        """

        self.open_channel()
        yield self.channel
        self.close()

    def open_channel(self):
        """Establishes a connection and returns an open channel.

        Returns
        -------
        pika.channel.Channel
            a connected pika Channel
        """

        if self.connection is None or not self.connection.is_open:
            self.connection = pika.BlockingConnection(self.connection_params)
        self.channel = self.connection.channel()
        return self.channel

    def close(self):
        """Close and disposes current channel and connection."""

        if self.channel is not None:
            if self.channel.is_open:
                self.channel.close()
            self.channel = None

        if self.connection is not None:
            if self.connection.is_open:
                self.connection.close()
            self.connection = None
