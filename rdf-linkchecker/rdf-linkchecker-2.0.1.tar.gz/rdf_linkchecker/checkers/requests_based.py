from typing import List, Optional, Set

import asyncio
import configparser
import operator
from pathlib import Path

import aiohttp
from rich.console import Console
from rich.table import Table
from user_agent import generate_user_agent

from rdf_linkchecker.checkers import CONFIG_DEFAULTS

_SESSION_HEADER = {
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "Referer": "https://www.google.com/",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "User-Agent": generate_user_agent(),
}


class Checker:
    """`requests` based link checker"""

    def __init__(self, configfile: Optional[Path] = None):
        self.config = configparser.ConfigParser()
        self.config.read_dict(CONFIG_DEFAULTS)
        if configfile:
            self.config.read(filenames=[configfile])
        self.urls: Set[str] = set()
        try:
            self.skip_domains = self.config["skip"]["domains"].split(",")
        except AttributeError:
            self.skip_domains = []
        self._session = None

    def _accept_url(self, url):
        for skip in self.skip_domains:
            if skip in url:
                return False
        return True

    def add_urls(self, urls: List[str]) -> None:
        upd = {u for u in urls if self._accept_url(u)}
        self.urls.update(upd)

    async def _check_single(self, url: str, session: aiohttp.ClientSession) -> bool:
        """Return True if resource request succeeded, else False

        Uses the streaming version to cut down on dl size/time
        """
        con = self.config["connection"]

        async def _check():
            try:
                timeout = aiohttp.ClientTimeout(total=int(con["timeout"]))
                async with session.get(url, timeout=timeout) as response:
                    response.raise_for_status()
                    return True
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                return False

        for try_no in range(int(con["retries"]) + 1):
            if not await _check():
                continue
            return True
        return False

    async def _check(self):
        if len(self.urls) == 0:
            # we cannot await an empty tasks list
            tasks = []
        else:
            async with aiohttp.ClientSession(headers=_SESSION_HEADER) as session:
                tasks = [
                    asyncio.ensure_future(self._check_single(u, session=session))
                    for u in self.urls
                ]
                await asyncio.wait(tasks)
        self.results = [t.result() for t in tasks]

    def check(self) -> bool:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._check())
        if self.config["reporting"]["level"] != "none":
            self.report_results(self.results)
        return all(self.results)

    def report_results(self, results):
        rptg = self.config["reporting"]
        only_failed = rptg["level"] == "only-failed"

        title = "Failed URLs" if only_failed else "Checked URLs"
        table = Table("URL", "Ok?", title=title)
        for url, reachable in sorted(
            zip(self.urls, results), key=operator.itemgetter(0)
        ):
            if rptg["level"] == "all" or (only_failed and not reachable):
                marker = "[green]✓[/green]" if reachable else "[red]x[/red]"
                table.add_row(url, marker)

        def _print(console):
            if table.row_count:
                console.print(table)

        if rptg["target"] != "console":
            with open(rptg["target"], "wt") as report_file:
                console = Console(file=report_file)
                _print(console)
        else:
            console = Console()
            _print(console)
