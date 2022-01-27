from spell.serving.config import Config

from spell.constants import (
    MODEL_SERVER_MAX_BATCH_SIZE_DEFAULT,
    MODEL_SERVER_BATCH_REQUEST_TIMEOUT_DEFAULT,
)


config = Config("/config/.env")


# Host and port the model server is running on
MODEL_SERVER_HOST = config("MODEL_SERVER_HOST", default="localhost")
MODEL_SERVER_PORT = config("MODEL_SERVER_PORT", cast=int, default=5000)
MODEL_SERVER_SOCKET = config("MODEL_SERVER_SOCKET", default=None)
# Maximum size a batch is allowed to be
MAX_BATCH_SIZE = config("MAX_BATCH_SIZE", cast=int, default=MODEL_SERVER_MAX_BATCH_SIZE_DEFAULT)
# Maximum time to wait before processing a request
REQUEST_TIMEOUT_MS = config("REQUEST_TIMEOUT_MS", cast=int, default=MODEL_SERVER_BATCH_REQUEST_TIMEOUT_DEFAULT)
# Run the proxy server in debug mode
DEBUG = config("DEBUG", cast=bool, default=False)
