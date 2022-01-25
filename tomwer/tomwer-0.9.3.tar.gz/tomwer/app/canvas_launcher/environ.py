"""
environ
=======

This module contains some basic configuration options for Orange
(for now mostly changing directories where settings and data are saved).

How it works
------------

The configuration is read from '{sys.prefix}/etc/orangerc.cfg'
which is a standard `configparser` file.

orangerc.cfg
------------

.. code-block:: cfg

    # An exemple orangerc.cfg file
    # ----------------------------
    #
    # A number of variables are predefined:
    # - prefix: `sys.prefix`
    # - name: The application/library name ('Orange')
    # - version: The application/library name ('Orange.__version__')
    # - version.major, version.minor, version.micro: The version components

    [paths]
    # The base path where persistent application data can be stored
    # (here we define a prefix relative path)
    data_dir_base = %(prefix)s/share
    # the base path where application data can be stored
    cache_dir = %(prefix)s/cache/%(name)s/%(version)s

    # The following is only applicable for a running orange canvas application.

    # The base dir where widgets store their settings
    widget_settings_dir = %(prefix)s/config/%(name)s/widgets
    # The base dir where canvas stores its settings
    canvas_settings_dir = %(prefix)s/config/%(name)s/canvas

"""
import os
import sys
import sysconfig
import configparser

from typing import Optional

import tomwer


def _get_parsed_config():
    version = tomwer.__version__.split(".")
    data = sysconfig.get_path("data")
    vars = {
        "home": os.path.expanduser("~/"),
        "prefix": sys.prefix,
        "data": sysconfig.get_path("data"),
        "name": "Orange",
        "version": tomwer.__version__,
        "version.major": version[0],
        "version.minor": version[1],
        "version.micro": version[2],
    }
    conf = configparser.ConfigParser(vars)
    conf.read(
        [
            os.path.join(data, "etc/tomwerrc.conf"),
        ],
        encoding="utf-8",
    )
    if not conf.has_section("paths"):
        conf.add_section("paths")
    return conf


def get_path(name: str, default: Optional[str] = None) -> Optional[str]:
    """
    Get configured path

    Parameters
    ----------
    name: str
        The named config path value
    default: Optional[str]
        The default to return if `name` is not defined
    """
    cfg = _get_parsed_config()
    try:
        return cfg.get("paths", name)
    except (configparser.NoOptionError, configparser.NoSectionError):
        return default
