import logging

from typing import Any, Dict

DEFAULT_LOGGING_FORMAT = "[%(asctime)s] [%(levelname)s] : %(message)s"


def setupLoggingSystem(**kwargs):
    params: Dict[str, Any] = kwargs
    
    logging.basicConfig(
        level = params["level"],
        format = params["format"],
        datefmt = params["datefmt"]
    )
