from typing import Any, Callable, Dict, List, Optional


class LunarModel:
    def __init__(self, name: str, version: str, predict_fn: Callable, models: Optional[List[Any]] = []):
        self.name = name
        self.version = version
        self.predict_fn = predict_fn
        self.models = models
        self.attrs = {}

    def add_attr(self, key: str, value: Any) -> None:
        self.attrs[key] = value

    def remove_attr(self, key: str) -> None:
        self.attrs.pop(key, None)

    def clear_attrs(self) -> None:
        self.attrs = {}

    async def predict(self, id: str, channel_id: str, **kwargs) -> List[Dict[str, Any]]:
        return await self.predict_fn(models=self.models, id=id, channel_id=channel_id, **kwargs)
