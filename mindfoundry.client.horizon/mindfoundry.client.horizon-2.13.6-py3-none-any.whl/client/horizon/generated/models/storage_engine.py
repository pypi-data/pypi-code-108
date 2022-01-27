from enum import Enum


class StorageEngine(str, Enum):
    NONE = "none"
    HTTP = "http"
    APPENDABLE_HTTP = "appendable_http"

    def __str__(self) -> str:
        return str(self.value)
