from celery import Celery

import os

from .config import BROKER_DIR, get_schedule
from .watchdog import WatchDog


app = Celery(__name__)
app.conf.update(
    {
        "broker_url": "filesystem://",
        "broker_transport_options": {
            "data_folder_in": os.path.join(BROKER_DIR, "out"),
            "data_folder_out": os.path.join(BROKER_DIR, "out"),
            "data_folder_processed": os.path.join(BROKER_DIR, "processed"),
        },
        "result_persistent": False,
        "task_serializer": "json",
        "result_serializer": "json",
        "accept_content": ["json"],
    }
)
app.conf.beat_schedule, app.conf.timezone = get_schedule()


@app.task
def tick():  # pragma: no cover - wrapper for function which is tested
    """Is triggered once every minute and performs the checks."""
    watchdog = WatchDog()
    watchdog.tick()


@app.task
def heartbeat():  # pragma: no cover - wrapper for function which is tested
    """Is triggered once every day and lets the user know it's still alive."""
    watchdog = WatchDog()
    watchdog.heartbeat()
