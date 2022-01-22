import abc


class Serializable(abc.ABC):
    @abc.abstractmethod
    def serialize(self):
        raise NotImplementedError
