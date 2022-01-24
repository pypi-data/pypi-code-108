import logging
import os
import yaml


__all__ = ["BASE_DIR", "CONFIG_FILE", "BROKER_DIR", "CONFIG", "DB_FILENAME"]

BASE_DIR = os.getenv("FIKKIE_BASE_DIR", os.path.expanduser("~/.fikkie"))
CONFIG_FILE = os.getenv("FIKKIE_CONFIG", os.path.join(BASE_DIR, "config.yaml"))
BROKER_DIR = os.getenv("FIKKIE_BROKER_DIR", os.path.join(BASE_DIR, "broker"))
DB_FILENAME = os.getenv("FIKKIE_DB_FILENAME", os.path.join(BASE_DIR, "db.json"))
LOG_FILE = os.getenv("FIKKIE_LOG_FILE", os.path.join(BASE_DIR, "fikkie.log"))
PID_FILE = os.getenv("FIKKIE_PID_FILE", os.path.join(BASE_DIR, "fikkie.pid"))


def load_config() -> dict:  # pragma: no cover - no complexity here
    """Parse the config from a given file."""
    try:
        with open(CONFIG_FILE, "r") as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError as e:
        logging.warning("Please run `fikkie init`.")
        exit(1)
    except yaml.YAMLError as e:
        logging.error(f"Could not parse config: {e}")
        exit(1)
