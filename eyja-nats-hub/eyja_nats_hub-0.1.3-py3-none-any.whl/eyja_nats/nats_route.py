from typing import Callable, Any, Optional

from pydantic import BaseModel


class NATSRoute(BaseModel):
    queue: str
    handler: Callable
    data_cls: Optional[Any] = dict
