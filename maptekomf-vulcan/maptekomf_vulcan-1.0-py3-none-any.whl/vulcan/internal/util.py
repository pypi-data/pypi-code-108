"""Utility functions used by Vulcan OMF."""
###############################################################################
#
# (C) Copyright 2021, Maptek Pty Ltd. All rights reserved.
#
###############################################################################

import os
import winreg
import logging

LOG = logging.getLogger("vulcanomf.internal")

class VulcanNotFoundError(Exception):
  """Exception raised if Vulcan cannot be found."""

def find_latest_vulcan_install() -> str:
  """Returns the path to the latest version of Vulcan.

  This uses the registry similar to Workbench to locate vulcan installs.

  Returns
  -------
  str
    Path to newest vulcan install.

  Raises
  ------
  VulcanNotFoundError
    If no vulcan install can be found.

  """
  vulcan_path = None
  current_version = None
  with winreg.OpenKey(
      winreg.HKEY_LOCAL_MACHINE,
      "SOFTWARE\\Maptek\\Workbench\\Client\\PluginSearchPaths") as key:
    i = 0
    while True:
      try:
        app, path, type = winreg.EnumValue(key, i)
        i += 1
        # Registry key is of the form:
        # Maptek Vulcan <user-facing version> <actual version>
        # and user-facing version is of the form:
        # year.release or year.release.minor
        # and actual version is of the form major.minor.patch.build
        if "Vulcan" in app:
          try:
            # The last item in the registry key is the version.
            # Convert it to a tuple for comparisons.
            parts = app.split(" ")
            version = parts[-1]
            version = [int(x) for x in version.split(".")]
            if current_version is None or version > current_version:
              vulcan_path = os.path.abspath(os.path.join(path, "../../../.."))
              current_version = version
          except (ValueError, IndexError) as error:
            LOG.exception(error,
                          "Failed to parse Vulcan registry key. "
                          "Vulcan installation may be corrupt.")
            continue
      except OSError:
        break

  if not vulcan_path:
    raise VulcanNotFoundError("Failed to find a supported Vulcan install.")
  return vulcan_path

def setup_vulcan_environment():
  """Sets up the VULCAN and VULCAN_EXE environment variables.

  This allows for the maptek.vulcan module to be imported from outside of
  Vulcan's native tsch.

  Raises
  ------
  VulcanNotFoundError
    If no Vulcan install can be found.

  """
  if "VULCAN" not in os.environ and "VULCAN_EXE" not in os.environ:
    vulcan_path = find_latest_vulcan_install()
    os.environ["VULCAN"] = vulcan_path
    os.environ["VULCAN_EXE"] = os.path.join(vulcan_path, "bin", "exe")
