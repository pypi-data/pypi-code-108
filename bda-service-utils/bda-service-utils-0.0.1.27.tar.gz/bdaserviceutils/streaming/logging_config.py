from os import environ
import logging
from .utils import running_on_edge
import sys

# Config variables
validMessageFormats = ["string", "json"]



##############################
# LOGGING SETTINGS
# Get log level from env variable
logLevel = logging.INFO
if environ.get('logLevel') is not None:
    if environ.get('logLevel')=="ERROR":
        logLevel = logging.ERROR
    elif environ.get('logLevel')=="DEBUG":
        logLevel = logging.DEBUG
    elif environ.get('logLevel')=="INFO":
        logLevel = logging.INFO
    else:
        raise ValueError("Logging configuration " + str(environ.get('logLevel')) + " not supported!")


if not running_on_edge():
    # Set logging configuration for Cluster executing
    logging.basicConfig(
        level=logLevel,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler()
        ]
    )
else:
   # Set logging configuration for Edge executing
    logging.basicConfig(
        filename=environ.get('logs_location'), #"/shared/logs.log",
        filemode='a',
        level=logLevel,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    
    # Redirect std out and err to file
    sys.stdout = open(environ.get('logs_location'), 'a')
    sys.stderr = sys.stdout



##############################