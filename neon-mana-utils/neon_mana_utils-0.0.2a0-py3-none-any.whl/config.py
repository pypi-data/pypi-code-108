# NEON AI (TM) SOFTWARE, Software Development Kit & Application Framework
# All trademark and other rights reserved by their respective owners
# Copyright 2008-2022 Neongecko.com Inc.
# Contributors: Daniel McKnight, Guy Daniels, Elon Gasper, Richard Leeds,
# Regina Bloomstine, Casimiro Ferreira, Andrii Pernatii, Kirill Hrymailo
# BSD-3 License
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from this
#    software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS  BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS;  OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE,  EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from os import makedirs
from os.path import join, isdir, isfile
from pprint import pformat
from typing import Optional

from ruamel.yaml import YAML
from xdg.BaseDirectory import xdg_config_home


_DEFAULT_CONFIG = {
    "host": "0.0.0.0",
    "port": 8181,
    "route": "/core",
    "ssl": False
}


def get_config_dir() -> str:
    """
    Get the configuration directory for this package
    :returns: path to config directory
    """
    config_dir = join(xdg_config_home, "mana")
    if not isdir(config_dir):
        makedirs(config_dir)
    return config_dir


def set_messagebus_config(host: str, port: int, route: str, ssl: bool):
    """
    Set the default messagebus config
    :param host: IP or hostname of MessageBus
    :param port: port used by MessageBus
    :param route: route used for core communications
    :param ssl: Connect via SSL if true
    """
    config = {"host": host,
              "port": port,
              "route": route,
              "ssl": ssl}
    config_file = join(get_config_dir(), "messagebus.yml")
    with open(config_file, 'w+') as f:
        YAML().dump(config, f)


def print_config() -> str:
    """
    Get a formatted representation of the configuration
    :returns: Formatted string representation of configuration files
    """
    bus_config = f"messagebus.yml\n{pformat(get_messagebus_config())}\n"
    filter_config = f"filters.yml\n{pformat(get_event_filters())}\n"
    return "\n".join((bus_config, filter_config))


def get_messagebus_config(config_dir: Optional[str] = None) -> dict:
    """
    Get the configured messagebus config
    :param config_dir: Optional path to configuration files (else default)
    :returns: Messagebus config from file or default
    """
    global _DEFAULT_CONFIG
    config_dir = config_dir or get_config_dir()
    config_file = join(config_dir, "messagebus.yml")
    if isfile(config_file):
        with open(config_file) as f:
            config = YAML().load(f)
        return config
    return _DEFAULT_CONFIG


def get_event_filters(config_dir: Optional[str] = None) -> dict:
    """
    Get configured event filters
    :param config_dir: Optional path to configuration files (else default)
    :returns: dict of 'include' and 'exclude' event lists
    """
    config_dir = config_dir or get_config_dir()
    filters_file = join(config_dir, "filters.yml")
    if isfile(filters_file):
        with open(filters_file) as f:
            config = YAML().load(f)
        return config
    return {"include": [],
            "exclude": []}
