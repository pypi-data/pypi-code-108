from typing import Any, Dict, Set


class bidict(dict):
    def __init__(self, mapping: Dict[Any, Any]) -> None:
        self._dict: Dict[Any, Any] = {}
        self.inverse: Dict[Any, Set[Any]] = {}
        for key, value in mapping.items():
            self[key] = value
        return

    def __setitem__(self, key: Any, value: Any) -> None:
        self._dict[key] = value
        self.inverse.setdefault(value, set()).add(key)
        return

    def __getitem__(self, key: Any) -> Any:
        return self._dict[key]

    def __delitem__(self, key: Any) -> None:
        self.inverse[self._dict[key]].remove(key)
        del self._dict[key]
        return

    def __repr__(self) -> str:
        return repr(self._dict)
