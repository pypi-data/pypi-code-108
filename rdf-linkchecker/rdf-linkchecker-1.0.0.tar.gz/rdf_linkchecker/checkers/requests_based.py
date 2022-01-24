from typing import List, Optional, Set

import configparser
from pathlib import Path

import requests

from rdf_linkchecker.checkers import CONFIG_DEFAULTS


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

    def _accept_url(self, url):
        for skip in self.skip_domains:
            if skip in url:
                return False
        return True

    def add_urls(self, urls: List[str]) -> None:
        upd = {u for u in urls if self._accept_url(u)}
        self.urls.update(upd)

    def _check_single(self, url) -> bool:
        """Return True if resource request succeeded, else False

        Uses the streaming version to cut down on dl size/time
        """
        con = self.config["connection"]

        def _check():
            try:
                with requests.get(
                    url, timeout=int(con["timeout"]), stream=True
                ) as response:
                    try:
                        response.raise_for_status()
                        return True
                    except requests.exceptions.HTTPError:
                        return False
            except requests.exceptions.ConnectionError:
                return False

        for try_no in range(int(con["retries"]) + 1):
            if not _check():
                continue
            return True
        return False

    def check(self, print_results=True) -> bool:
        results = [self._check_single(u) for u in self.urls]
        if print_results:
            self.print_results(results)
        return all(results)

    def print_results(self, results):
        from rich.console import Console
        from rich.table import Table

        table = Table("URL", "Ok?", title="Checked URLs")
        for url, reachable in zip(self.urls, results):
            marker = "[green]✓[/green]" if reachable else "[red]x[/red]"
            table.add_row(url, marker)
        console = Console()
        console.print(table)
