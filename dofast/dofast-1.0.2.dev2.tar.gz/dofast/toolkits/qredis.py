import json

from redis import Redis


class QRedis(Redis):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def jsonset(self, key: str, value: dict) -> None:
        str_json = json.dumps(value)
        return self.set(key, str_json)

    def jsonget(self, key: str) -> dict:
        return json.loads(self.get(key).decode())

    def configure(self, *args, **kwargs) -> object:
        return QRedis(*args, **kwargs)
