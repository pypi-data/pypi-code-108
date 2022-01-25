"""Top-level package for aop2db."""

import pandas as pd


def __get_latest_xml_file() -> str:
    """Get latest XML file version from AOP wiki site."""
    df = pd.read_html("https://aopwiki.org/downloads")  # Returns list
    latest_version = df[0].iloc[0]["Date"]
    return latest_version


__author__ = """Bruce Schultz"""
__email__ = "bruce.schultz@scai.fraunhofer.de"
__version__ = "0.2.6"

LATEST_XML_VERSION = __get_latest_xml_file()
