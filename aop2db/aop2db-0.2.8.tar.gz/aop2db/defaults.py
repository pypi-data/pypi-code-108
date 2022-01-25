"""Default paths and variables."""

import logging
import os
from pathlib import Path

from aop2db.constants import AOP_XML_DOWNLOAD

logger = logging.getLogger(__name__)

# Paths
HOME = str(Path.home())
PROJECT_NAME = "aop2db"
BASE_DIR = Path.home().joinpath(f".{PROJECT_NAME}")

AOP_DIR = BASE_DIR.joinpath("aop")
LOG_DIR = BASE_DIR.joinpath("logs")
DB_PATH = BASE_DIR.joinpath(f"{PROJECT_NAME}.db")

AOP_XML_FILE = AOP_DIR.joinpath(Path(AOP_XML_DOWNLOAD).name)
TAXONOMY_CACHE = AOP_DIR.joinpath("taxonomy_ids.json")

# Make the folders
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(AOP_DIR, exist_ok=True)

# Config file
CONFIG = BASE_DIR.joinpath("config.ini")

# Logging Configuration
LOG_FILE_PATH = LOG_DIR.joinpath("aop2db.log")
logging.basicConfig(
    filename=LOG_FILE_PATH,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG,
)

# SQL Connection
CONN_STRING = f"sqlite:///{DB_PATH}"
