"""
Main interface for fis service.

Usage::

    ```python
    import boto3
    from mypy_boto3_fis import (
        Client,
        FISClient,
    )

    session = boto3.Session()

    client: FISClient = boto3.client("fis")
    session_client: FISClient = session.client("fis")
    ```
"""
from .client import FISClient

Client = FISClient


__all__ = ("Client", "FISClient")
