"""
Main interface for codeguru-reviewer service.

Usage::

    ```python
    import boto3
    from mypy_boto3_codeguru_reviewer import (
        Client,
        CodeGuruReviewerClient,
        CodeReviewCompletedWaiter,
        ListRepositoryAssociationsPaginator,
        RepositoryAssociationSucceededWaiter,
    )

    session = boto3.Session()

    client: CodeGuruReviewerClient = boto3.client("codeguru-reviewer")
    session_client: CodeGuruReviewerClient = session.client("codeguru-reviewer")

    code_review_completed_waiter: CodeReviewCompletedWaiter = client.get_waiter("code_review_completed")
    repository_association_succeeded_waiter: RepositoryAssociationSucceededWaiter = client.get_waiter("repository_association_succeeded")

    list_repository_associations_paginator: ListRepositoryAssociationsPaginator = client.get_paginator("list_repository_associations")
    ```
"""
from .client import CodeGuruReviewerClient
from .paginator import ListRepositoryAssociationsPaginator
from .waiter import CodeReviewCompletedWaiter, RepositoryAssociationSucceededWaiter

Client = CodeGuruReviewerClient


__all__ = (
    "Client",
    "CodeGuruReviewerClient",
    "CodeReviewCompletedWaiter",
    "ListRepositoryAssociationsPaginator",
    "RepositoryAssociationSucceededWaiter",
)
