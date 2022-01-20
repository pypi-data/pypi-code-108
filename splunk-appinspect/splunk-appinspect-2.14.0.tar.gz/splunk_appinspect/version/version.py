# Copyright 2019 Splunk Inc. All rights reserved.

"""This file is used to track the version of Splunk AppInspect."""
import os


# https://packaging.python.org/guides/single-sourcing-package-version/
def get_version(current_dir=None):
    """
    Helper function to get Splunk AppInspect version info
    """
    if current_dir is None:
        current_dir = os.path.dirname(os.path.realpath(__file__))
    version_file = os.path.join(current_dir, "VERSION.txt")

    with open(version_file, "r") as version_text:
        return version_text.read().strip()
