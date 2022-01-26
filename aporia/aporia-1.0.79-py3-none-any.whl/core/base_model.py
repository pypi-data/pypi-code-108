from contextlib import contextmanager
from functools import wraps
import logging
from typing import Callable, Optional

from .context import get_context
from .errors import AporiaError, handle_error
from .logging_utils import LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)


def validate_model_ready(func: Callable) -> Callable:
    """Decorator that checks if the model is ready before calling the wrapped function.

    Args:
        func: Function to wrap

    Returns:
        Wrapped function
    """

    @wraps(func)
    def wrapper(self, *args, **kwargs):  # noqa: ANN001, ANN201
        if not getattr(self, "_model_ready", False):
            return

        return func(self, *args, **kwargs)

    return wrapper


class BaseModel:
    """Base class for model objects."""

    def __init__(self, model_id: str, model_version: str, set_ready_when_done: bool = True):
        """Initializes a BaseModel object.

        Args:
            model_id: Model identifier, as received from the Aporia dashboard.
            model_version: Model version - this can be any string that represents the model
                version, such as "v1" or a git commit hash.
            set_ready_when_done: True if self._model_ready should be set to
                True when initialization is finished. False if the subclass wants to
                handle this.
        """
        self._model_ready = False

        logger.debug(
            "Initializing model object for model {} version {}".format(model_id, model_version)
        )
        context = get_context()

        self.model_id = model_id
        self.model_version = model_version
        self._event_loop = context.event_loop
        self._http_client = context.http_client
        self._config = context.config

        if len(model_id) == 0 or len(model_version) == 0:
            raise AporiaError("model_id and model_version must be non-empty strings")

        if set_ready_when_done:
            self._model_ready = True

    @contextmanager
    def handle_error(self, message_format: str, throw_errors: Optional[bool] = None):
        """Context manager for error handling.

        Yields:
            None

        Args:
            message_format: Error message format string
            throw_errors: True if exceptions should be raised. Defaults to global config value.
        """
        try:
            yield
        except Exception as err:
            handle_error(
                message_format=message_format,
                verbose=self._config.verbose,
                throw_errors=self._config.throw_errors if throw_errors is None else throw_errors,
                debug=self._config.debug,
                original_exception=err,
                log_level=logging.ERROR,
            )
