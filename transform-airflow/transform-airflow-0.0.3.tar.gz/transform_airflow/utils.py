import logging

from os import environ

from transform import MQLClient


logger = logging.getLogger()


def get_query_server_url() -> str:
    """Retrieve mql url through environment variable"""
    try:
        return environ["MQL_QUERY_URL"]
    except KeyError:
        logger.error("Missing MQL server url")
        raise EnvironmentError("MQL_QUERY_URL env var not set")


def get_api_key() -> str:
    """Retrieve api_key through environment variable"""
    try:
        return environ["TRANSFORM_API_KEY"]
    except KeyError:
        logger.error("Transform API Key is missing")
        raise EnvironmentError("TRANSFORM_API_KEY env var not set")


def initialize_mql_client() -> MQLClient:  # noqa: D
    return MQLClient(get_api_key(), get_query_server_url())
