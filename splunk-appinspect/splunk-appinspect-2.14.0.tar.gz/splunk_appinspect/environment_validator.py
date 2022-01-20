# Copyright 2019 Splunk Inc. All rights reserved.
"""Helper module to verify runtime environment"""
import sys


def validate_python_version():
    """To validate if the python version meet the requirement of AppInspect CLI"""
    major, _, _, _, _ = sys.version_info
    version_detected = str(major)

    if (major) != (3):
        sys.exit(
            f"Python version {version_detected} was detected."
            " Splunk AppInspect only supports Python 3.7"
        )
