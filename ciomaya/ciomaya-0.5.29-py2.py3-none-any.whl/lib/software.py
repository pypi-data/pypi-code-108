"""
Software data as a singleton.

Software is converted to a PackageTree containing only maya packages and
supported plugins.

Also has the ability to use fixtures for dev purposes.
"""
import re

import pymel.core as pm

def detect_host():
    version_parts = pm.about(iv=True).replace(
        "Autodesk Maya", "").strip().split(".")
    if len(version_parts) < 2:
        version_parts.append("0")
    version_parts[1] = "SP{}".format(version_parts[1])
    return "maya-io {}".format(".".join(version_parts))


def get_plugin_version(plugin):
    try:
        return pm.pluginInfo(plugin, q=True, version=True)
    except RuntimeError:
        return

def detect_mtoa():
    version = get_plugin_version("mtoa")
    if version:
        parts = version.split(".")
        version = ".".join(parts + ["0"] * (4 - len(parts)))
        return "arnold-maya {}".format(version)


def detect_rfm():
    version = get_plugin_version("RenderMan_for_Maya")
    if version:

        parts = list(filter(None, re.split(r" |\.|@", version)))
        version = ".".join(parts + ["0"] * (4 - len(parts)))
        return "renderman-maya {}".format(version)


def detect_vray():
    version = get_plugin_version("vrayformaya")
    if version:  # something loaded
        if version.lower() != "next":
            return version
        try:
            version = pm.fileInfo('vrayBuild', q=True)
        except KeyError:
            return "v-ray-maya 99.99.99.99"

        parts = version.split(" ")[0].split(".")
        version = ".".join(parts + ["0"] * (4 - len(parts)))
        return "v-ray-maya {}".format(version)


def detect_redshift():
    version = get_plugin_version("redshift4maya")
    if version:
        parts = version.split(".")
        version = ".".join(parts + ["0"] * (4 - len(parts)))
        return "redshift-maya {}".format(version)

def detect_yeti():
    version = get_plugin_version("pgYetiMaya")
    if version:
        parts = version.split(".")
        version = ".".join(parts + ["0"] * (4 - len(parts)))
        return "yeti {}".format(version)
