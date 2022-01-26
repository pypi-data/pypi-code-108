from importlib.metadata import distribution
from logging import getLogger

_module = __name__.split(".")[0]

logger = getLogger(_module)
dist = distribution(_module)

# Default values
APPLICATION = "Mosaic"
HOST = "0.0.0.0"
LATENCY_COUNT = 2
LATENCY_THRESHOLD = 0.8
PORT_CONNECTOR = 61682
TECOROUTE_HOST = "route.tecomat.com"
TECOROUTE_PORT = 61682
