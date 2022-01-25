"""Utility methods for AOP submodule."""
import pandas as pd


def __get_latest_xml_file() -> str:
    """Get latest XML file version from AOP wiki site."""
    df = pd.read_html("https://aopwiki.org/downloads")  # Returns list
    latest_version = df[0].iloc[0]["Date"]
    return latest_version


LATEST_XML_VERSION = __get_latest_xml_file()
