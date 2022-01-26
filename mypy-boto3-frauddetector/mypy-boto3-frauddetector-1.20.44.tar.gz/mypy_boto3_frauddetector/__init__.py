"""
Main interface for frauddetector service.

Usage::

    ```python
    import boto3
    from mypy_boto3_frauddetector import (
        Client,
        FraudDetectorClient,
    )

    session = boto3.Session()

    client: FraudDetectorClient = boto3.client("frauddetector")
    session_client: FraudDetectorClient = session.client("frauddetector")
    ```
"""
from .client import FraudDetectorClient

Client = FraudDetectorClient


__all__ = ("Client", "FraudDetectorClient")
