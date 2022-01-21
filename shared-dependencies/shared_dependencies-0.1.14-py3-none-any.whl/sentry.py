import os
import logging
from typing import Callable, List, Union, Dict, Any, Sequence

from sentry_sdk import capture_exception, init
from sentry_sdk.integrations import Integration
from sentry_sdk.integrations.pure_eval import PureEvalIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

logger = logging.getLogger("uvicorn")

sentry_logging = LoggingIntegration(level=logging.INFO, event_level=logging.ERROR)

common_integrations = [
    sentry_logging,
    PureEvalIntegration(),
]


def safe_capture_exception(e: Exception) -> str:
    sentry_id_or_none = capture_exception(e)
    return sentry_id_or_none if sentry_id_or_none is not None else "not sent"


def init_sentry(sentry_integrations: Sequence[Integration]):
    """
    This method has to be called in the app init file (main.py).
    SENTRY_DSN, SENTRY_ENVIRONMENT and SENTRY_RELEASE must be provided in app variables.
    :param sentry_integrations:
    :return: sentry init function
    """
    return init(
        integrations=sentry_integrations,
        traces_sample_rate=float(os.getenv("TRACES_SAMPLE_RATE_SENTRY", 1.0)),
        sample_rate=float(os.getenv("SAMPLE_RATE_SENTRY", 1.0)),
        traces_sampler=sampling_context,
    )  # type: ignore


def sampling_context(context: Dict[str, Any]) -> Union[int, float]:
    try:
        if "/metrics" in context["asgi_scope"].get("path", ""):
            return 0
    except KeyError:
        logger.exception("context->asgi_scope failed")
        return 0
    else:
        logger.info(f'sentry-trace : {context["transaction_context"]["trace_id"]}')
        return float(os.getenv("TRACES_SAMPLE_RATE_SENTRY", 1.0))
