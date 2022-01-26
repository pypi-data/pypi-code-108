"""
Type annotations for codeguru-reviewer service client paginators.

[Open documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_codeguru_reviewer/paginators.html)

Usage::

    ```python
    import boto3

    from mypy_boto3_codeguru_reviewer import CodeGuruReviewerClient
    from mypy_boto3_codeguru_reviewer.paginator import (
        ListRepositoryAssociationsPaginator,
    )

    client: CodeGuruReviewerClient = boto3.client("codeguru-reviewer")

    list_repository_associations_paginator: ListRepositoryAssociationsPaginator = client.get_paginator("list_repository_associations")
    ```
"""
from typing import Generic, Iterator, Sequence, TypeVar

from botocore.paginate import PageIterator
from botocore.paginate import Paginator as Boto3Paginator

from .literals import ProviderTypeType, RepositoryAssociationStateType
from .type_defs import ListRepositoryAssociationsResponseTypeDef, PaginatorConfigTypeDef

__all__ = ("ListRepositoryAssociationsPaginator",)


_ItemTypeDef = TypeVar("_ItemTypeDef")


class _PageIterator(Generic[_ItemTypeDef], PageIterator):
    def __iter__(self) -> Iterator[_ItemTypeDef]:
        """
        Proxy method to specify iterator item type.
        """


class ListRepositoryAssociationsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.44/reference/services/codeguru-reviewer.html#CodeGuruReviewer.Paginator.ListRepositoryAssociations)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_codeguru_reviewer/paginators.html#listrepositoryassociationspaginator)
    """

    def paginate(
        self,
        *,
        ProviderTypes: Sequence[ProviderTypeType] = ...,
        States: Sequence[RepositoryAssociationStateType] = ...,
        Names: Sequence[str] = ...,
        Owners: Sequence[str] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListRepositoryAssociationsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.44/reference/services/codeguru-reviewer.html#CodeGuruReviewer.Paginator.ListRepositoryAssociations.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_codeguru_reviewer/paginators.html#listrepositoryassociationspaginator)
        """
