"""
Main interface for ec2-instance-connect service.

Usage::

    ```python
    import boto3
    from mypy_boto3_ec2_instance_connect import (
        Client,
        EC2InstanceConnectClient,
    )

    session = boto3.Session()

    client: EC2InstanceConnectClient = boto3.client("ec2-instance-connect")
    session_client: EC2InstanceConnectClient = session.client("ec2-instance-connect")
    ```
"""
from .client import EC2InstanceConnectClient

Client = EC2InstanceConnectClient


__all__ = ("Client", "EC2InstanceConnectClient")
