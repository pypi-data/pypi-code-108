import copy
import logging
import signal
import threading
from typing import Dict, Optional, Set

from . import Incident, instantiate_variable

logger = logging.getLogger(__name__)


class Monitor:
    def __init__(self, interval: Optional[float] = None):
        self._interval = interval
        self._constants = set()
        self._variables = set()
        self._incidents = set()
        self._locals = {}
        self._running = None

        if self._interval:
            signal.signal(signal.SIGINT, self.exit)
            signal.signal(signal.SIGTERM, self.exit)
            logger.info(f"Monitoring is set for {interval} seconds.")

    def exit(self, *args):
        logger.info(f"Exiting")
        self._running.set()

    def add_constants(self, json: Dict) -> int:
        return self._parse_variables(json, self._constants)

    def add_variables(self, json: Dict) -> int:
        return self._parse_variables(json, self._variables)

    def add_incidents(self, json: Dict) -> int:
        count = 0
        for key, json in json.items():
            incident = Incident(key, json)
            if incident in self._incidents:
                raise Exception(f"Incident '{key}' already exists")
            self._incidents.add(incident)
            logger.info(f"Incident '{incident.name}' is configured")
            count += 1
        return count

    def start(self) -> None:
        for v in self._constants:
            self._locals[v.name] = v.value
            logger.info(f"Constant '{v.name}' holds {v.value}")

        if self._interval:
            thread: threading.Thread = None
            self._running = threading.Event()
            while not self._running.wait(self._interval):
                if thread:
                    thread.join()
                if not self._running.is_set():
                    thread = threading.Thread(target=self.fetch_and_evalute)
                    thread.start()
        else:
            self.fetch_and_evalute()

    def fetch_and_evalute(self) -> None:
        locals = copy.deepcopy(self._locals)
        for v in self._variables:
            value = v.new_value()
            last_value = v.last_value
            locals[v.name] = value
            logger.info(f"'{v.name}' is loaded and holds {value}")
            locals["last_" + v.name] = last_value
            logger.info(f"'last_{v.name}' is loaded and holds '{last_value}'")
        logger.debug("Reloaded all variables")

        for incident in self._incidents:
            logger.debug(f"Evaluating '{incident.name}' incident")
            incident.escalated(locals)
        logger.debug("Evaludated all incidents")

    def _parse_variables(self, json: Dict, containor: Set) -> int:
        count = 0
        for key, json in json.items():
            variable = instantiate_variable(key, json)
            if variable in self._constants or variable in self._variables:
                raise Exception(f"Variable '{key}' already exists")
            containor.add(variable)
            logger.info(f"Variable '{variable.name}' is configured")
            count += 1
        return count
