"""
A scraper to collect paths from Yeti nodes.
"""

import os
import sys

import pymel.core as pm
from ciopath.gpath import Path

RESOURCES_TOKEN = "<MAYA_RESOURCES>"
MAYA_LOCATION = os.environ.get("MAYA_LOCATION")


def run(_):
    """
    Find the ocio config file and set the OCIO variable

    If the config file is under MAYA_LOCATION then we assume it's available on the render node and
    ignore it. Since MAYA_RESOURCES token is in MAYA_LOCATION, we can also ignore it.

    TODO: This is a bare bones implementation, and does not yet scrape the config file itself for nested
    dependencies. 

    Returns: Dict: paths and environment overrides
    """
    if not pm.colorManagementPrefs(q=True, cmEnabled=True):
        return 
    if not pm.colorManagementPrefs(q=True, cmConfigFileEnabled=True):
        return 
    config_file = pm.colorManagementPrefs(q=True, configFilePath=True)
    if RESOURCES_TOKEN in config_file:
        return 
    if not config_file: 
        return
    if config_file.startswith(MAYA_LOCATION):
        return

    return {
        "paths": [{"path": config_file}],
        "env": [
            {
                "name": "OCIO",
                "value": Path(config_file).fslash(with_drive=False),
                "merge_policy": "exclusive",
            }
        ],
    }
