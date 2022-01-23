import os

from elasticsearch import Elasticsearch


def get_elastic_client(
    url: str, api_id: str = os.environ.get("ELASTIC_API_ID"), api_key: str = os.environ.get("ELASTIC_API_KEY"), **kwargs
):
    """
    Returns an Elasticsearch client using api credentials.

    If api id and the api key are not provided, it looks for `ELASTIC_API_ID` and `ELASTIC_API_KEY` environment variables.

    Parameters
    ----------
    url : str
        Host of the Elasticsearch instance.
    api_id : str, optional
        Elastic API ID, by default os.environ.get("ELASTIC_API_ID")
    api_key : str, optional
        Elastic API Key, by default os.environ.get("ELASTIC_API_KEY")

    Returns
    -------
    Elasticsearch
        Elasticsearch client.

    Examples
    --------
    >>> from sidhulabs.elastic.client import get_elastic_client
    >>> es_client = get_elastic_client("http://localhost:9200")
    """

    assert api_id is not None, "Pass in Elastic API ID to function or set env var ELASTIC_API_ID"
    assert api_key is not None, "Pass in Elastic API KEY to function or set env var ELASTIC_API_KEY"

    return Elasticsearch(hosts=[url], api_key=(api_id, api_key), **kwargs)
