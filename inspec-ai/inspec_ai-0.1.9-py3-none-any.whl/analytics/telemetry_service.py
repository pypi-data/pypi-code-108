import os
from tkinter import EXCEPTION
import uuid
import json
import requests
import threading
import time
import sys
import pathlib

from queue import Queue
from datetime import datetime, timedelta

from inspec_ai.config import TRACKING_DISABLED


ANONYMOUS_TRACKING_IDENTIFIER_KEY = "anonymous_tracking_identifier"

telemetry_queue = Queue()

previously_tracked_events = {}

_anonymous_tracking_identifier = ""


def track_function_executed(function_name, *args, **kwargs):
    def decorate(func):
        def call(*args, **kwargs):
            _track_function_executed_internal(function_name)
            result = func(*args, **kwargs)
            return result

        return call
        
    return decorate

def _track_function_executed_internal(function_name: str) -> None:
    if TRACKING_DISABLED:
        return

    utc_now = datetime.utcnow()

    if function_name in previously_tracked_events:
        last_track = previously_tracked_events[function_name]

        previously_tracked_events[function_name] = utc_now

        if utc_now < last_track + timedelta(minutes=5):
            return
    
    else:
        previously_tracked_events[function_name] = utc_now

    telemetryEvent = { 
        "eventDate": str(utc_now), 
        "functionName": str(function_name), 
    } 

    telemetry_queue.put(telemetryEvent)


def _get_anonymous_tracking_identifier() -> None:
    global _anonymous_tracking_identifier

    if _anonymous_tracking_identifier and _anonymous_tracking_identifier != "":
        return _anonymous_tracking_identifier

    data_dir = _get_datadir()
    directory = os.path.join(data_dir, ".inspec")
    file_name = "config.json"

    full_path = os.path.join(directory, file_name)

    if os.path.isfile(full_path):
        with open(full_path, "r") as file:
            config = json.load(file)

    else:
        if not os.path.exists(directory):
            os.mkdir(directory)

        anonymous_tracking_identifier = uuid.uuid4()

        config = { ANONYMOUS_TRACKING_IDENTIFIER_KEY:  str(anonymous_tracking_identifier) }

        with open(full_path, "w") as file:
            json.dump(config, file)

    _anonymous_tracking_identifier = config[ANONYMOUS_TRACKING_IDENTIFIER_KEY]

    return _anonymous_tracking_identifier


def _get_datadir() -> pathlib.Path:
    home = pathlib.Path.home()

    if sys.platform == "win32":
        return home / "AppData/Roaming"
    elif sys.platform == "linux":
        return home / ".local/share"
    elif sys.platform == "darwin":
        return home / "Library/Application Support"


def _telemetry_daemon():
    main_process_alive = True
    while main_process_alive:
        mt = threading.main_thread()
        main_process_alive = mt.is_alive()

        while not telemetry_queue.empty():
            event = telemetry_queue.get()

            anonymous_tracking_identifier = _get_anonymous_tracking_identifier()
            
            event["anonymousTelemetryIdentifier"] = str(anonymous_tracking_identifier) 

            try:
                requests.post(
                    "https://inspec-dev-api.azurewebsites.net/telemetry/track-function-executed",
                    json=event,
                    headers={'Authorization': 'Bearer NDk5MDYxRjctQjM4Mi00MkRBLTlFNUMtNjdCOTBBMTBDM0VD'},
                )
            except: 
                # ignore errors
                pass

        time.sleep(0.1)


telemetry_thread = threading.Thread(target=_telemetry_daemon, name="Telemetry Thread")
telemetry_thread.start()