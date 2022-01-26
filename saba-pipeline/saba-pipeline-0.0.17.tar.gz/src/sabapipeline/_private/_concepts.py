from ._utilities import *


class Event(ABC):
    def _repr(self) ->str:
        try:
            return self.__str__()
        except Exception as e:
            return f'Invalid string representation: {e.__str__()}'


class EventHandler(ABC):
    @abstractmethod
    def handle_event(self, event_to_handle: Event):
        raise NotImplementedError()
