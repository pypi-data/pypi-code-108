import warnings
from typing import Any, Dict, Optional


def deprecation(message):
    warnings.warn(message, DeprecationWarning, stacklevel=2)


# Enable deprecation warnings.
warnings.simplefilter("default")


def _clean_params(params: Dict[str, Optional[Any]]) -> Dict[str, Any]:
    """Remove params without value"""
    return {param: value for param, value in params.items() if value is not None}
