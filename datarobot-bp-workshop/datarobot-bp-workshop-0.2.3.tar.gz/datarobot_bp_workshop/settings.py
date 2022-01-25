"""
Copyright 2021 DataRobot, Inc. and its affiliates.

All rights reserved.

DataRobot, Inc. Confidential.

This is unpublished proprietary source code of DataRobot, Inc. and its affiliates.

The copyright notice above does not evidence any actual or intended publication of such source code.

Released under the terms of DataRobot Tool and Utility Agreement.
"""

import json
import os
from typing import Optional
from urllib import request

from ._version import __version__

# Global Session Information
SESSION_INFO = {"VERSION_CHECK_ATTEMPTED": False}


class Settings(object):
    """ Introduce concept of settings """

    force_no_color = False
    force_dev_mode = False
    force_no_version_check = False

    defaults = {
        "BLUEPRINT_WORKSHOP_DEV_MODE": False,
        "BLUEPRINT_WORKSHOP_ALLOW_COLOR": True,
        "BLUEPRINT_WORKSHOP_VERSION_CHECK": True,
    }

    @property
    def is_dev_mode(self) -> bool:
        return self.force_dev_mode or self.get_env_value("BLUEPRINT_WORKSHOP_DEV_MODE")

    @property
    def allow_color(self) -> bool:
        if self.force_no_color:
            return False
        return self.get_env_value("BLUEPRINT_WORKSHOP_ALLOW_COLOR")

    @property
    def should_check_version(self) -> bool:
        if SESSION_INFO["VERSION_CHECK_ATTEMPTED"]:
            return False
        if self.force_no_version_check:
            return False
        return self.get_env_value("BLUEPRINT_WORKSHOP_VERSION_CHECK")

    @classmethod
    def get_env_value(cls, setting):
        return os.environ.get(setting, cls.defaults[setting])

    @staticmethod
    def get_latest_version() -> Optional[str]:
        """ Parse the version info JSON from PyPI """
        version_info = {}
        try:
            with request.urlopen(
                "https://pypi.org/pypi/datarobot-bp-workshop/json"
            ) as f:
                version_info = json.loads(f.read().decode("utf-8"))
        except Exception:
            # Silently fail if unable to perform version check
            # This failure is likely due to no network connection.
            pass

        return (
            version_info.get("info", {}).get("version")
            if version_info is not None
            else None
        )

    def is_latest_version_or_none(self) -> bool:
        """ Easily testable version comparison check """
        version = self.get_latest_version()
        # If version cannot be obtained, resolve as if latest
        return True if version is None else version == __version__

    def check_if_should_upgrade(self) -> bool:
        """ Check PyPI for the latest version and recommend update. """
        should_upgrade = False
        if self.should_check_version:
            # Check to see if latest version is being used
            if not self.is_latest_version_or_none():
                should_upgrade = True
                print(
                    "Please upgrade to the latest version: "
                    "pip install --upgrade datarobot_bp_workshop"
                )
            # We attempted to check - wait until next session to try again
            self.set_version_check_attempted(True)
        return should_upgrade

    @staticmethod
    def set_version_check_attempted(attempted: bool):
        """
        Set whether the version check has been attempted

        Parameters
        ----------
        attempted: bool
            Whether the version check has been attempted
        """
        SESSION_INFO["VERSION_CHECK_ATTEMPTED"] = attempted
