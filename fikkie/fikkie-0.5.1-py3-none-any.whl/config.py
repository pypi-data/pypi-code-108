import logging
import os
import yaml

from celery.schedules import crontab


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
        raise FileNotFoundError("Could not find config file, please run `fikkie init`.")
    except yaml.YAMLError as e:
        logging.error(f"Could not parse config: {e}")
        exit(1)


def get_schedule() -> tuple:
    """Returns the Celery schedule and timezone."""
    try:
        config = load_config()
    except FileNotFoundError:  # pragma: no cover - no complexity here
        config = {}

    heartbeat_config = config.get("heartbeat", {})

    timezone = heartbeat_config.get("timezone", "UTC")
    schedule = {"tick": {"task": "fikkie.main.tick", "schedule": 60}}

    if heartbeat_config.get("enable", True):
        heartbeat_schedule_config = heartbeat_config.get("schedule", {})
        heartbeat_schedule = {
            "minute": heartbeat_schedule_config.get("minute", 0),
            "hour": heartbeat_schedule_config.get("hour", 12),
            "day_of_week": heartbeat_schedule_config.get("day_of_week", "*"),
            "day_of_month": heartbeat_schedule_config.get("day_of_month", "*"),
        }
        schedule["heartbeat"] = {
            "task": "fikkie.main.heartbeat",
            "schedule": crontab(**heartbeat_schedule),
        }

    return schedule, timezone
