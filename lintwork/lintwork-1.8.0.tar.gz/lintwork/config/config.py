# -*- coding: utf-8 -*-

import os
import yaml

INPUT_TEXT_SEP = ","


class ConfigFile:
    APIVERSION = "apiVersion"
    KIND = "kind"
    METADATA = "metadata"
    SPEC = "spec"


class MetaData:
    NAME = "name"


class ConfigException(Exception):
    def __init__(self, info):
        super().__init__(self)
        self._info = info

    def __str__(self):
        return self._info


class Config(object):
    def __init__(self):
        self._config_file = None
        self._lint_project = ""
        self._listen_url = ""
        self._output_file = ""

    @property
    def config_file(self):
        return self._config_file

    @config_file.setter
    def config_file(self, name):
        if not isinstance(name, str) or len(name.strip()) == 0:
            raise ConfigException("config invalid")
        name = name.strip()
        if not name.endswith(".yml") and not name.endswith(".yaml"):
            raise ConfigException("suffix invalid")
        if not os.path.exists(name):
            raise ConfigException("%s not found" % name)
        with open(name) as file:
            self._config_file = yaml.load(file, Loader=yaml.FullLoader)
        if self._config_file is None:
            raise ConfigException("config invalid")

    @property
    def lint_project(self):
        return self._lint_project

    @lint_project.setter
    def lint_project(self, name):
        if not isinstance(name, str):
            raise ConfigException("project invalid")
        name = name.strip()
        if len(name) != 0 and not os.path.exists(name):
            raise ConfigException("%s not found" % name)
        self._lint_project = name

    @property
    def listen_url(self):
        return self._listen_url

    @listen_url.setter
    def listen_url(self, url):
        if not isinstance(url, str):
            raise ConfigException("url invalid")
        self._listen_url = url.strip()

    @property
    def output_file(self):
        return self._output_file

    @output_file.setter
    def output_file(self, name):
        if not isinstance(name, str):
            raise ConfigException("output invalid")
        name = name.strip()
        if len(name) != 0:
            if (
                not name.endswith(".json")
                and not name.endswith(".txt")
                and not name.endswith(".xlsx")
            ):
                raise ConfigException("suffix invalid")
            if os.path.exists(name):
                raise ConfigException("%s already exist" % name)
        self._output_file = name
