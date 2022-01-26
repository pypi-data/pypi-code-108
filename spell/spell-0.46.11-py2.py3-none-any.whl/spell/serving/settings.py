from pathlib import Path

from spell.serving.config import Config


config = Config("/config/.env")


# Path to the config file"
CONFIG_FILE = config("CONFIG_FILE", cast=Path, default=None)
# Path to the module containing the predictor
ENTRYPOINT = config("ENTRYPOINT", cast=Path, default=None)
# Name of the predictor class"
CLASSNAME = config("CLASSNAME", default=None)
# Should the /predict endpoint expect batch requests?
USE_BATCH_PREDICT = config("USE_BATCH_PREDICT", cast=bool, default=False)
# Run the server in debug mode
DEBUG = config("DEBUG", cast=bool, default=False)
# Flag to flip when debugging locally
LOCAL = config("LOCAL", cast=bool, default=False)
