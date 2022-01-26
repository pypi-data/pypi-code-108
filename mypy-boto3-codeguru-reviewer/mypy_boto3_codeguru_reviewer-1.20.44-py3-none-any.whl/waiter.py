"""
Type annotations for codeguru-reviewer service client waiters.

[Open documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_codeguru_reviewer/waiters.html)

Usage::

    ```python
    import boto3

    from mypy_boto3_codeguru_reviewer import CodeGuruReviewerClient
    from mypy_boto3_codeguru_reviewer.waiter import (
        CodeReviewCompletedWaiter,
        RepositoryAssociationSucceededWaiter,
    )

    client: CodeGuruReviewerClient = boto3.client("codeguru-reviewer")

    code_review_completed_waiter: CodeReviewCompletedWaiter = client.get_waiter("code_review_completed")
    repository_association_succeeded_waiter: RepositoryAssociationSucceededWaiter = client.get_waiter("repository_association_succeeded")
    ```
"""
from botocore.waiter import Waiter as Boto3Waiter

from .type_defs import WaiterConfigTypeDef

__all__ = ("CodeReviewCompletedWaiter", "RepositoryAssociationSucceededWaiter")


class CodeReviewCompletedWaiter(Boto3Waiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.44/reference/services/codeguru-reviewer.html#CodeGuruReviewer.Waiter.CodeReviewCompleted)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_codeguru_reviewer/waiters.html#codereviewcompletedwaiter)
    """

    def wait(self, *, CodeReviewArn: str, WaiterConfig: WaiterConfigTypeDef = ...) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.44/reference/services/codeguru-reviewer.html#CodeGuruReviewer.Waiter.CodeReviewCompleted.wait)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_codeguru_reviewer/waiters.html#codereviewcompletedwaiter)
        """


class RepositoryAssociationSucceededWaiter(Boto3Waiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.44/reference/services/codeguru-reviewer.html#CodeGuruReviewer.Waiter.RepositoryAssociationSucceeded)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_codeguru_reviewer/waiters.html#repositoryassociationsucceededwaiter)
    """

    def wait(self, *, AssociationArn: str, WaiterConfig: WaiterConfigTypeDef = ...) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.44/reference/services/codeguru-reviewer.html#CodeGuruReviewer.Waiter.RepositoryAssociationSucceeded.wait)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_codeguru_reviewer/waiters.html#repositoryassociationsucceededwaiter)
        """
