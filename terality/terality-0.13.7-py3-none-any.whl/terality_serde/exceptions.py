from typing import Optional


class TeralitySerdeError(Exception):
    pass


class TeralitySerializationError(TeralitySerdeError):
    def __init__(self, message: str, unserializable_type: Optional[str] = None) -> None:
        super().__init__(message)
        self.unserializable_type = unserializable_type


class TeralityDeserializationError(TeralitySerdeError):
    pass
