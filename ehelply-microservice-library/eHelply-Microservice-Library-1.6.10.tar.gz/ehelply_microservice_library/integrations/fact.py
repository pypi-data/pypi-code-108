from ehelply_bootstrapper.integrations.integration import Integration
import threading
from ehelply_logger.Logger import Logger

import requests
import time

from typing import List

from pydantic import BaseModel
from ehelply_bootstrapper.utils.environment import Environment

from ehelply_bootstrapper.utils.state import State


class FactBase(BaseModel):
    name: str
    data: dict


def get_fact(fact_name: str):
    from ehelply_bootstrapper.utils.state import State
    fact: Fact = State.integrations.get("fact")
    return fact.facts[fact_name]


def get_fact_stage(fact_name: str):
    from ehelply_bootstrapper.utils.state import State
    fact: Fact = State.integrations.get("fact")
    try:
        return fact.facts[fact_name][Environment.stage()]
    except:
        raise Exception("Fact `" + fact_name + "` has no stage `" + Environment.stage() + "`")


def get_fact_endpoint(fact_name: str):
    from ehelply_bootstrapper.utils.state import State
    fact: Fact = State.integrations.get("fact")
    try:
        return fact.facts[fact_name][Environment.stage()]['endpoint']
    except:
        raise Exception("Fact `" + fact_name + "` has no endpoint for stage `" + Environment.stage() + "`")


class Fact(Integration):
    def __init__(self, logger: Logger, fact_names: List[str] = None) -> None:
        super().__init__("fact")
        self.fact_names = []
        if fact_names:
            self.fact_names = fact_names
        self.facts = {}
        self.logger = logger.spinoff()
        self.thread: FactThread = None
        self.fact_query_delay_minutes: int = 20

        # self.m2m = State.integrations.get("m2m")

    def init(self):
        # Initial load to prevent race conditions
        self._query()
        self.thread = FactThread(self).start()

    def load(self):
        pass

    def _query(self):
        State.logger.info("  -> Fetching Latest Facts")
        for fact_name in self.fact_names:
            State.logger.debug("     * " + State.config.facts.endpoint + "/facts/" + fact_name)
            response = requests.get(State.config.facts.endpoint + "/facts/" + fact_name)
            try:
                self.facts[fact_name] = response.json()['data']
            except:
                raise Exception(
                    "Communication with ehelply-facts failed. There are several possible reasons for this: incorrect fact name or you're sending the request from an IP address that has not been whitelisted.")

    def refresh(self):
        self._query()

    def run(self):
        while True:
            time.sleep(self.fact_query_delay_minutes * 60)
            self._query()

    def push_fact(self, fact: FactBase):
        response = requests.post(State.config.facts.endpoint + "/facts", json={"fact": fact.dict()})
        return response


class FactThread(threading.Thread):
    def __init__(self, fact: Fact):
        super().__init__()
        self.fact: Fact = fact
        self.daemon = True

    def run(self) -> None:
        self.fact.run()
