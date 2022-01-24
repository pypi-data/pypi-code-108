import json
import logging
import requests
import functools
from datetime import datetime
from time import time

from pyrasgo.config import get_session_api_key
from pyrasgo.api.connection import Connection


def track_experiment(func):
    @functools.wraps(func)
    def decorated(self, *args, **kwargs):
        try:
            api = self.api
            unique_id = self._experiment_id
        except AttributeError:
            try:
                api = Connection(api_key=get_session_api_key())
                unique_id = self._experiment_id
            except:
                logging.debug(f"Cannot create events for functions called from {self.__class__.__name__} class.")
                return func(self, *args, **kwargs)
        except KeyError:
            logging.debug(f"To create events for functions called from " \
                            f"{self.__class__.__name__} class, a dataframe must be tagged by ID.")
            return func(self, *args, **kwargs)

        if unique_id:
            event_timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S-%f")
            event_name = func.__name__
            event_type = self.__class__.__name__
            event_dict = {
                "event_timestamp": event_timestamp,
                "unique_id": unique_id,
                "event_type": event_type,
                "event_name": event_name,
                "event_details": {},
            }

        try:
            api._post(f"/event-logging", event_dict, api_version=1).json()
        except Exception as e:
            logging.info(f"Unable to log event with exception: {e}")
        return func(self, *args, **kwargs)
    return decorated