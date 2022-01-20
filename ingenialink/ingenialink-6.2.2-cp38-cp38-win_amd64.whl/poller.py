from abc import ABC, abstractmethod


class Poller(ABC):
    """Register poller.

    Args:
        servo (Servo): Servo.
        num_channels (int): Number of channels.

    Raises:
        ILCreationError: If the poller could not be created.

    """
    def __init__(self, servo, num_channels):
        self.__servo = servo
        self.__num_channels = num_channels

    @abstractmethod
    def start(self):
        raise NotImplementedError

    @abstractmethod
    def stop(self):
        raise NotImplementedError

    @abstractmethod
    def configure(self, t_s, sz):
        raise NotImplementedError

    @abstractmethod
    def ch_configure(self, ch, reg):
        raise NotImplementedError

    @abstractmethod
    def ch_disable(self, ch):
        raise NotImplementedError

    @abstractmethod
    def ch_disable_all(self):
        raise NotImplementedError

    @property
    def data(self):
        raise NotImplementedError

    @property
    def servo(self):
        """Servo: Servo instance to be used."""
        return self.__servo

    @servo.setter
    def servo(self, value):
        self.__servo = value

    @property
    def num_channels(self):
        """int: Number of channels in the poller."""
        return self.__num_channels

    @num_channels.setter
    def num_channels(self, value):
        self.__num_channels = value
