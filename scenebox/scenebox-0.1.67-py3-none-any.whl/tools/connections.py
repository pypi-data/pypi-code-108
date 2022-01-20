from typing import Optional, Any


class KVStoreTemplate:
    def __init__(self):
        pass

    def put_str(self, key, value):
        pass

    def get_str(self, key, default=None):
        pass

    def put_bytes(self, key, value):
        pass

    def get_bytes(self, key, default=None):
        pass

    def put_json(self, key, json_data):
        pass

    def get_json(self, key: str, default: Optional[Any] = None):
        pass

    def delete(self, key):
        pass

    def clear_all(self, pattern: str):
        pass
