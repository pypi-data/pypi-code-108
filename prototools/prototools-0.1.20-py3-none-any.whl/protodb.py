import os
import json
from typing import Union, Dict, List, Type


JSON = Union[Dict[str, 'JSON'], List['JSON'], int, str, float, bool, Type[None]] 


class ProtoDB:
    """Simple and lightweight json database"""

    __slots__ = ['_db', 'filename']

    def __init__(self, filename: str) -> None:
        self.filename = filename + ".pdb"
        self._load()

    def _load(self) -> None:
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                try:
                    self._db = json.load(f)
                except json.decoder.JSONDecodeError:
                    self._db = {}
        else:
            self._db = {}
    
    def get_data(self):
        with open(self.filename, 'r') as f:
            try:
                return json.load(f)
            except json.decoder.JSONDecodeError:
                return {}

    def _save(self) -> None:
        with open(self.filename, 'w') as f:
            json.dump(self._db, f)
    
    def add(self, obj: object, id: str = None) -> None:
        if id is not None and not isinstance(obj, dict):
            self._db[id] = obj
            self._save()
        else:
            self._db.update(obj)
            self._save()

    def delete(self, key: str) -> None:
        if key in self._db:
            del self._db[key]
            self._save()
    
    def get(self, key: str) -> JSON:
        return self._db.get(key, None)

    def get_all(self) -> List[JSON]:
        return list(self._db.values())
    
    def search(self, key: str) -> List[JSON]:
        for k, v in self._db.items():
            if key in k:
                yield v