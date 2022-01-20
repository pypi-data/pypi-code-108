"""Config class."""

import configparser
import os
import re
from pathlib import Path
from typing import List


class Config:
    def __init__(self):
        self._coverage_config_template = None
        self._coverage_source = None
        self._coverage_source_env = None
        self._cfname = None
        self._cfroot = None
        self._cf = None
        self._test_dirs = []
        found = self._find_config()
        if found:
            cf = self._load_config()
            self._parse_config(cf)
            self._cf = cf
        else:
            self._cfroot = Path(".")
            self._test_dirs = ["."]

    def _find_config(self) -> bool:
        p = Path.cwd()
        # TODO: change to use parents
        while True:
            cf = Path(p, ".yearc")
            if cf.is_file():
                self._cfname = cf
                self._cfroot = p
                return True
            gd = Path(p, ".git")
            if gd.is_dir():
                return False
            n = p.parent
            if n.samefile(p):
                break
            p = n
        return False

    def _load_config(self) -> configparser.ConfigParser:
        p = self._cfname
        cf = configparser.ConfigParser()
        cf.read(p)
        return cf

    def _parse_config(self, cf: configparser.ConfigParser) -> List[str]:
        ycfg = cf.items("yea")
        ydict = dict(ycfg)
        test_paths = ydict.get("test_paths", "")
        test_list = re.findall(r"[\S]+", test_paths)
        self._test_dirs = test_list
        test_paths = ydict.get("test_paths", "")

        self._coverage_config_template = ydict.get("coverage_config_template", "")
        self._coverage_source = ydict.get("coverage_source")
        # TODO: clean up how this works, user could already have an absolute path
        if self._coverage_source and self.test_root:
            self._coverage_source = os.path.join(self.test_root, self._coverage_source)
        self._coverage_source_env = ydict.get("coverage_source_env")
        self._results_file = ydict.get("results_file")

        return test_list

    @property
    def test_dirs(self):
        return self._test_dirs

    @property
    def test_root(self):
        return self._cfroot
