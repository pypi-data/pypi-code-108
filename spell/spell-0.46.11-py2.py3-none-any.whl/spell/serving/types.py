from typing import Any, Awaitable, Callable, Dict, List, Optional, Tuple, TypeVar, Union

from starlette.background import BackgroundTasks
from starlette.responses import Response

__all__ = [
    "APIResponse",
    "PredictorClass",
    "PredictorMethod",
    "PredictorResponse",
    "ProxyPredictCallbackResponse",
    "ProxyPredictCallback",
]

_JSON = Union[Dict, List]  # This isn't precise, but it's not inaccurate
PrepareResponse = Tuple[Optional[Union[_JSON, Response]], Optional[BackgroundTasks]]
PredictorResponse = Union[str, bytes, Response, _JSON]
APIResponse = Tuple[PredictorResponse, Optional[BackgroundTasks]]
PredictorClass = TypeVar("PredictorClass")
PredictorMethod = Callable[[Tuple[Any, ...]], Union[PredictorResponse, Awaitable[PredictorResponse]]]

ProxyPredictCallbackResponse = Awaitable[Tuple[Union[List[Any], Response], bool]]
ProxyPredictCallback = Callable[[List[Any]], ProxyPredictCallbackResponse]
