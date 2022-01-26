import os
from os.path import dirname, join
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path, verbose=True)

# Environment
ENV = os.environ.get("ENV", "dev")
SENTRY_DSN = os.environ.get("SENTRY_DSN")
SLACK_URL = os.environ.get("SLACK_URL", None)
APP_VERSION = os.environ.get("IMAGE_VERSION")
NAME = os.environ.get("SERVICE_NAME", "dbt-py")
LOG_LEVEL = os.environ.get("LOG_LEVEL", "debug")
DATADOG_HOST = os.environ.get("DD_HOST", None)
DATADOG_PORT = os.environ.get("DD_STATSD_PORT", None)
SUCCESS_ALERTS = bool(int(os.environ.get("SUCCESS_ALERTS", 0)))
PUSHGATEWAY_HOST = os.environ.get("PUSHGATEWAY_HOST", None)
PUSHGATEWAY_PORT = os.environ.get("PUSHGATEWAY_PORT", None)
