"""Checker implemented with https://github.com/linkchecker/linkchecker

Too complex to make it do what simple tasks we need.
"""

from typing import List, Optional

from pathlib import Path


class Checker:
    def __init__(self, configfile: Optional[Path] = None):
        from linkcheck import configuration, logconf
        from linkcheck.director import console, get_aggregate

        self.config = configuration.Configuration()
        if configfile:
            self.config.read(files=[configfile])
        logconf.init_log_config()

        self.config["recursionlevel"] = 0

        self.config.sanitize()
        self.config.set_status_logger(console.StatusLogger())

        self.aggregate = get_aggregate(self.config)

    def add_urls(self, urls: List[str]):
        from linkcheck.cmdline import aggregate_url

        for url in urls:
            aggregate_url(aggregate=self.aggregate, url=url)

    def check(self):
        from linkcheck.director import check_urls

        check_urls(self.aggregate)

        stats = self.config["logger"].stats
        # on internal errors, exit with status 2
        if stats.internal_errors:
            return 2
        # on errors or printed warnings, exit with status 1
        if stats.errors or (stats.warnings_printed and self.config["warnings"]):
            return 1
        return 0
