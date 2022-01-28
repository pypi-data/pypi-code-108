"""Module for customMy Logger class - wrapper that is internally used. You can also use it, even if 90% of
users will not.

Mylogging is designed in a way that logger should not be configured or used and log functions should be called
from mylogging directly.
"""

from mylogging.my_logging.logger_module import my_logger

__all__ = ["my_logger"]
