import functools
from typing import Any, Dict


def skip_warmup_call(func: Any) -> Any:
    @functools.wraps(func)
    def warmup_wrapper(event: Dict[str, Any], context: Any) -> Any:
        if event.get("source") == "serverless-plugin-warmup":
            return "WarmUp - Lambda is warm!"
        return func(event, context)

    return warmup_wrapper
