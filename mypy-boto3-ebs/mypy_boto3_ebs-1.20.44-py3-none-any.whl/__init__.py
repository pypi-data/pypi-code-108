"""
Main interface for ebs service.

Usage::

    ```python
    import boto3
    from mypy_boto3_ebs import (
        Client,
        EBSClient,
    )

    session = boto3.Session()

    client: EBSClient = boto3.client("ebs")
    session_client: EBSClient = session.client("ebs")
    ```
"""
from .client import EBSClient

Client = EBSClient


__all__ = ("Client", "EBSClient")
