"""
Type annotations for efs service client paginators.

[Open documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_efs/paginators.html)

Usage::

    ```python
    import boto3

    from mypy_boto3_efs import EFSClient
    from mypy_boto3_efs.paginator import (
        DescribeFileSystemsPaginator,
        DescribeMountTargetsPaginator,
        DescribeTagsPaginator,
    )

    client: EFSClient = boto3.client("efs")

    describe_file_systems_paginator: DescribeFileSystemsPaginator = client.get_paginator("describe_file_systems")
    describe_mount_targets_paginator: DescribeMountTargetsPaginator = client.get_paginator("describe_mount_targets")
    describe_tags_paginator: DescribeTagsPaginator = client.get_paginator("describe_tags")
    ```
"""
from typing import Generic, Iterator, TypeVar

from botocore.paginate import PageIterator
from botocore.paginate import Paginator as Boto3Paginator

from .type_defs import (
    DescribeFileSystemsResponseTypeDef,
    DescribeMountTargetsResponseTypeDef,
    DescribeTagsResponseTypeDef,
    PaginatorConfigTypeDef,
)

__all__ = ("DescribeFileSystemsPaginator", "DescribeMountTargetsPaginator", "DescribeTagsPaginator")


_ItemTypeDef = TypeVar("_ItemTypeDef")


class _PageIterator(Generic[_ItemTypeDef], PageIterator):
    def __iter__(self) -> Iterator[_ItemTypeDef]:
        """
        Proxy method to specify iterator item type.
        """


class DescribeFileSystemsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.43/reference/services/efs.html#EFS.Paginator.DescribeFileSystems)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_efs/paginators.html#describefilesystemspaginator)
    """

    def paginate(
        self,
        *,
        CreationToken: str = ...,
        FileSystemId: str = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeFileSystemsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.43/reference/services/efs.html#EFS.Paginator.DescribeFileSystems.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_efs/paginators.html#describefilesystemspaginator)
        """


class DescribeMountTargetsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.43/reference/services/efs.html#EFS.Paginator.DescribeMountTargets)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_efs/paginators.html#describemounttargetspaginator)
    """

    def paginate(
        self,
        *,
        FileSystemId: str = ...,
        MountTargetId: str = ...,
        AccessPointId: str = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeMountTargetsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.43/reference/services/efs.html#EFS.Paginator.DescribeMountTargets.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_efs/paginators.html#describemounttargetspaginator)
        """


class DescribeTagsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.43/reference/services/efs.html#EFS.Paginator.DescribeTags)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_efs/paginators.html#describetagspaginator)
    """

    def paginate(
        self, *, FileSystemId: str, PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeTagsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.43/reference/services/efs.html#EFS.Paginator.DescribeTags.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_efs/paginators.html#describetagspaginator)
        """
