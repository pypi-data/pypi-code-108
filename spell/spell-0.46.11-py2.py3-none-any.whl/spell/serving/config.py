from starlette.config import Config as StarletteConfig


class Config(StarletteConfig):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._values = {}

    def __call__(self, key, *args, **kwargs):
        value = super().__call__(f"SPELL_{key}", *args, **kwargs)
        self._values[key] = value
        return value

    def __str__(self):
        return "\n".join([f"{k.lower().replace('_', ' ')}: {v}" for k, v in self._values.items() if v is not None])
