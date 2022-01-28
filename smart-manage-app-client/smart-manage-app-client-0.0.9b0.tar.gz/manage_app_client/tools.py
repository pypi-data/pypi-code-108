import os
import traceback
from typing import Callable, Any, Optional

from .client import ManageClient


def log_exception(
    definition: dict,
    description: str,
    trb: Optional[str] = None,
    function_name: str = '',
    is_auth: bool = False,
) -> bool:
    """Log error helper

    Args:
        definition (dict): dict definiton
        description (str): exception str
        trb (Optional[str], optional): full traceback. Defaults to None.
        function_name (Optional[str], optional): function. Defaults to ''.

    Returns:
        bool: status
    """
    init_kwargs = {
        "system_id": os.environ.get("MANAGE_SYSTEM_ID", ""),
        "system_url": os.environ.get("MANAGE_SYSTEM_URL", ""),
        "token": os.environ.get("MANAGE_SYSTEM_TOKEN", ""),
        "debug": os.environ.get("MANAGE_SYSTEM_DEBUG", '0'),
    }
    client = ManageClient(**init_kwargs)
    if not trb:
        trb = str(traceback.format_exc()).replace(
            'func_result = function', function_name
        )
    return client.log_exception(definition, description, trb=trb, is_auth=is_auth)


def run(function: Callable[..., Any], **kwargs) -> Any:
    """
    function must be a top level function, not class method, and not decorated function
    """
    try:
        from zappa.asynchronous import run as zappa_run
    except ImportError:
        raise ImportError('u need to install zappa==0.50.0')
    if "kwargs" in kwargs:
        kwargs = kwargs["kwargs"]
    if not os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
        return function(**kwargs)
    zappa_run(function, kwargs=kwargs)
    return True
