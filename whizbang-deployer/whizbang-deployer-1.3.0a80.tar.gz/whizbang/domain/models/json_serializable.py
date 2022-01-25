import json
from abc import ABC, abstractmethod


class JsonSerializable(ABC):
    @abstractmethod
    def __init__(self):
        pass

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)
