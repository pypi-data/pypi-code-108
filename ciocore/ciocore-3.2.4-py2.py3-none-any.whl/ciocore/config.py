"""
Config is an Object containing configuration variables.

Only contains stuff that is not suitable to specify in a submitter.
"""

import logging
import os
import multiprocessing
import base64
import json
from ciocore import loggeria

from ciocore.common import CONDUCTOR_LOGGER_NAME

logger = logging.getLogger(CONDUCTOR_LOGGER_NAME)


__config__ = None


def config(force=False):
    global __config__
    if force or not __config__:
        __config__ = Config()
    return __config__

class Config(object):
    def __init__(self):

        try:
            default_thread_count = min(multiprocessing.cpu_count() * 2, 16)
        except NotImplementedError:
            default_thread_count = 16

        url = os.environ.get("CONDUCTOR_URL", "https://dashboard.conductortech.com")
        api_url = os.environ.get("CONDUCTOR_API_URL", url.replace("dashboard", "api"))

        falsy = ["false", "no", "off", "0"]

        log_level = os.environ.get("CONDUCTOR_LOG_LEVEL", "INFO")
        if log_level not in ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]:
            log_level = "INFO"

        self.config = {
            "thread_count": int(os.environ.get("CONDUCTOR_THREAD_COUNT", default_thread_count)),
            "priority": int(os.environ.get("CONDUCTOR_PRIORITY", 5)),
            "md5_caching": False
            if os.environ.get("CONDUCTOR_MD5_CACHING", "True").lower() in falsy
            else True,
            "log_level": log_level,
            "url": url,
            # Keep "auth_url" for backwwards compatibillity only. 
            # Clients should use "url" moving forward. 
            # Remove "auth_url" on the next major version bump.
            "auth_url": url,
            "api_url": api_url,
            "api_key": self.get_api_key_from_variable() or self.get_api_key_from_file(),
        }

        loggeria.setup_conductor_logging(
            loggeria.LEVEL_MAP.get(log_level), loggeria.FORMATTER_VERBOSE
        )

    @staticmethod
    def get_api_key_from_variable():
        api_key = os.environ.get("CONDUCTOR_API_KEY")
        if not api_key:
            return
        logger.info("Attempting to read API key from CONDUCTOR_API_KEY")
        try:
            return json.loads(api_key.replace("\n", "").replace("\r", ""))
        except ValueError:
            try:
                result = base64.b64decode(api_key)
                return Config._to_json(result)
            except BaseException:
                result = base64.b64decode(api_key.encode()).decode("ascii")
                return Config._to_json(result)
        except BaseException:
            message = "An error occurred reading the API key from the CONDUCTOR_API_KEY variable"
            logger.error(message)
            raise ValueError(message)

    @staticmethod
    def get_api_key_from_file():
        api_key_path = os.environ.get("CONDUCTOR_API_KEY_PATH")
        if not api_key_path:
            return
        logger.info("Attempting to read API key from CONDUCTOR_API_KEY_PATH")
        try:
            with open(api_key_path, "r") as fp:
                return Config._to_json(fp.read())
        except BaseException:
            message = "An error occurred reading the API key from the path described in the CONDUCTOR_API_KEY_PATH variable"
            logger.error(message)
            raise ValueError(message)

    @staticmethod
    def _to_json(content):
        return json.loads(content.replace("\n", "").replace("\r", ""))
