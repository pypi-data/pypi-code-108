from abc import ABC, abstractmethod
from time import time

import pomace


class Script(ABC):

    URL = ""
    SKIP = False

    attempted = completed = failed = 0

    @property
    def name(self) -> str:
        return self.__class__.__name__.lower()

    def loop(self, duration: int = 0, *, max_failed: int = 10, dev: bool = False):
        start = time()
        elapsed = 0.0
        while (elapsed < duration or not duration) and self.failed < max_failed:
            self._iterate(dev)
            elapsed = round(time() - start, 1)
        pomace.log.info(f"Stopping {self.name} after {elapsed} seconds")

    def _iterate(self, dev: bool):
        self.attempted += 1
        pomace.log.info(f"Starting {self.name} iteration {self.attempted}")

        page = self.init()

        page = self.run(page)

        if self.check(page):
            self.completed += 1
            self.failed = 0
        else:
            self.failed += 1
            if dev:
                breakpoint()

        iterations = "iteration" if self.completed == 1 else "iterations"
        pomace.log.info(f"Completed {self.completed} {self.name} {iterations}")
        if self.failed:
            failures = "failure" if self.failed == 1 else "failures"
            pomace.log.warn(f"{self.failed} successive {failures}")

    def init(self) -> pomace.Page:
        if pomace.shared.browser and pomace.shared.browser.url == self.URL:
            return pomace.auto()

        pomace.log.info(f"Visiting {self.URL}")
        page = pomace.visit(self.URL)
        return page

    @abstractmethod
    def run(self, page: pomace.Page) -> pomace.Page:
        return None

    @abstractmethod
    def check(self, page: pomace.Page) -> bool:
        return False
