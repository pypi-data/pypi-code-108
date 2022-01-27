"""
Main interface for opensearch service.

Usage::

    ```python
    import boto3
    from mypy_boto3_opensearch import (
        Client,
        OpenSearchServiceClient,
    )

    session = boto3.Session()

    client: OpenSearchServiceClient = boto3.client("opensearch")
    session_client: OpenSearchServiceClient = session.client("opensearch")
    ```
"""
from .client import OpenSearchServiceClient

Client = OpenSearchServiceClient


__all__ = ("Client", "OpenSearchServiceClient")
