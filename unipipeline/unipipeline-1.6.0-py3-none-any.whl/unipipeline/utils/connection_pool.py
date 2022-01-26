from typing import Generic, TypeVar, Dict, Any, Set

TConnectionObj = TypeVar('TConnectionObj')


class ConnectionObj(Generic[TConnectionObj]):
    def __hash__(self) -> int:
        raise NotImplementedError(f'method "__hash__" is not implemented for {type(self).__name__}')

    def get(self) -> TConnectionObj:
        raise NotImplementedError(f'method "get" is not implemented for {type(self).__name__}')

    def is_closed(self) -> bool:
        raise NotImplementedError(f'method "is_closed" is not implemented for {type(self).__name__}')

    def connect(self) -> None:
        raise NotImplementedError(f'method "connect" is not implemented for {type(self).__name__}')

    def close(self) -> None:
        raise NotImplementedError(f'method "close" is not implemented for {type(self).__name__}')


class ConnectionRC(Generic[TConnectionObj]):
    def __init__(self, connection_obj: ConnectionObj[TConnectionObj]) -> None:
        self._connection_obj = connection_obj
        self._identifiers: Set[int] = set()

    def count(self) -> int:
        return len(self._identifiers)

    def connect(self, identifier: int) -> TConnectionObj:
        if identifier not in self._identifiers:
            if self.count() == 0:
                self._connection_obj.connect()
            self._identifiers.add(identifier)
        return self._connection_obj.get()

    def disconnect(self, identifier: int) -> None:
        if identifier not in self._identifiers:
            return
        self._identifiers.remove(identifier)
        if self.count() == 0:
            self._connection_obj.close()


class ConnectionManager(Generic[TConnectionObj]):
    def __init__(self, rc: ConnectionRC[TConnectionObj], identifier: int, connection_obj: ConnectionObj[Any]) -> None:
        self._rc = rc
        self._id = identifier
        self._key = hash(connection_obj)
        self._connection_obj = connection_obj

    def connect(self) -> TConnectionObj:
        return self._rc.connect(self._id)

    def disconnect(self) -> None:
        return self._rc.disconnect(self._id)

    def close(self) -> None:
        self.disconnect()

    def __del__(self) -> None:
        self.disconnect()

    def __enter__(self) -> TConnectionObj:
        return self.connect()

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        return self.disconnect()


class ConnectionPool:

    def __init__(self) -> None:
        self._registry: Dict[int, ConnectionRC[Any]] = dict()
        self._id_counter: int = 0

    def new_manager(self, connection_obj: ConnectionObj[TConnectionObj]) -> ConnectionManager[TConnectionObj]:
        identifier = self._id_counter
        self._id_counter += 1

        key = hash(connection_obj)
        if key not in self._registry:
            self._registry[key] = ConnectionRC(connection_obj)
        rc = self._registry[key]

        return ConnectionManager(rc, identifier, connection_obj)


connection_pool = ConnectionPool()
