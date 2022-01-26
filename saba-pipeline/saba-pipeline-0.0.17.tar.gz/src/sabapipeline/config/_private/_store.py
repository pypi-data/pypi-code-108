from ..._private._utilities import *
from ... import Event
from copy import deepcopy


SIMPLE_CHANGE_INDICATOR = lambda x, y: x != y


class DataStore(ABC):
    @abstractmethod
    def get_value(self, key: str) -> Optional[Any]:
        raise NotImplementedError()

    @abstractmethod
    def set_value(self, key: str, value: Any, cause: Event = None) -> None:
        raise NotImplementedError()

    @abstractmethod
    def contains(self, key: str) -> bool:
        raise NotImplementedError()

    def __getitem__(self, item: str) -> Optional[Any]:
        return self.get_value(item)

    def __setitem__(self, key: str, value: Any) -> None:
        self.set_value(key, value)

    def __contains__(self, item: str) -> bool:
        return self.contains(item)

    @synchronized
    def get_branch(self, prefix: str,
                   value_generator: Callable[[str], Any] = None,
                   change_event_handlers: List[Callable[[str, Optional[Any], Any, Optional[Event]], None]] = None,
                   change_indicator: Callable[[Any, Any], bool] = SIMPLE_CHANGE_INDICATOR
                   ):
        if not hasattr(self, '_branches'):
            self._branches: Dict[str, DataStoreBranch] = dict()
        if prefix in self._branches:
            result: DataStoreBranch = self._branches[prefix]
            if result._value_generator is not None and value_generator is not None:
                raise ValueError(f'Branch with prefix "{prefix}" already has a value generator')
            if result._change_indicator != SIMPLE_CHANGE_INDICATOR and change_indicator != SIMPLE_CHANGE_INDICATOR:
                raise ValueError(f'Branch with prefix "{prefix}" already has a change indicator')
            if change_event_handlers is not None and len(change_event_handlers) > 0:
                if result._change_event_handlers is None:
                    result._change_event_handlers = change_event_handlers
                else:
                    result._change_event_handlers += change_event_handlers
        else:
            result = DataStoreBranch(self, prefix, value_generator, change_event_handlers, change_indicator)
            self._branches[prefix] = result
        return result


class DataStoreBranch(DataStore):
    def __init__(self,
                 parent_data_store: DataStore,
                 prefix: str,
                 value_generator: Callable[[str], Any],
                 change_event_handlers: List[Callable[[str, Optional[Any], Any, Optional[Event]], None]],
                 change_indicator: Callable[[Any, Any], bool]
                 ):
        super().__init__()
        self._parent_data_store = parent_data_store
        self._prefix = prefix
        self._value_generator = value_generator
        self._change_event_handlers = change_event_handlers
        self._change_indicator = change_indicator

    def get_value(self, key: str) -> Optional[Any]:
        result = self._parent_data_store.get_value(self._prefix + key)
        if result is None and self._value_generator is not None:
            result = self._value_generator(key)
            self._parent_data_store.set_value(self._prefix + key, result, None)
            if (self._change_event_handlers is not None
                    and len(self._change_event_handlers) > 0
                    and self._change_indicator(None, result)):
                for handler in self._change_event_handlers:
                    handler(key, None, result, None)
        return result

    def set_value(self, key: str, value: Any, cause: Event = None) -> None:
        should_call_handlers = False
        if self._change_event_handlers is not None and len(self._change_event_handlers) > 0:
            previous_value = self.get_value(key)
            should_call_handlers = True
            if not self._change_indicator(previous_value, value):
                return
        self._parent_data_store.set_value(self._prefix + key, value, cause)
        if should_call_handlers:
            for handler in self._change_event_handlers:
                # noinspection PyUnboundLocalVariable
                handler(key, previous_value, value, cause)

    def contains(self, key: str) -> bool:
        return self._parent_data_store.contains(self._prefix + key)


class SimpleRAMDataStore(DataStore):
    def __init__(self):
        super().__init__()
        self._storage: Dict[str, Any] = dict()

    def get_value(self, key: str) -> Optional[Any]:
        return deepcopy(self._storage.get(key, None))

    def set_value(self, key: str, value: Any, cause: Event = None) -> None:
        self._storage[key] = deepcopy(value)

    def contains(self, key: str) -> bool:
        return key in self._storage
