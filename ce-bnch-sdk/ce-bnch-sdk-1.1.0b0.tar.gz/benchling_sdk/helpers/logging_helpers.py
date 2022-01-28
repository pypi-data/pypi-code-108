import logging
from typing import Iterable, Optional


def default_logger(name: str = "benchling_sdk") -> logging.Logger:
    """Construct the default logger for the SDK."""
    logger = logging.getLogger(name)
    logger.addHandler(logging.NullHandler())
    return logger


sdk_logger = default_logger()


def log_deprecation(source_name: str, suggestion: str) -> None:
    """Log a standardized message for use of deprecated functionality."""
    sdk_logger.warning(f"{source_name} is deprecated. Please use {suggestion}")


def check_for_csv_bug_fix(variable: str, value: Optional[Iterable[str]]) -> None:
    """Specific error for a fixed bug that might cause breaks. See BNCH-24087."""
    if value is None:
        return
    for v in value:
        if "," in v:
            raise ValueError(f"Items in {variable} must not contain ','")
