"""
Type annotations for kafka service client paginators.

[Open documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafka/paginators.html)

Usage::

    ```python
    import boto3

    from mypy_boto3_kafka import KafkaClient
    from mypy_boto3_kafka.paginator import (
        ListClusterOperationsPaginator,
        ListClustersPaginator,
        ListClustersV2Paginator,
        ListConfigurationRevisionsPaginator,
        ListConfigurationsPaginator,
        ListKafkaVersionsPaginator,
        ListNodesPaginator,
        ListScramSecretsPaginator,
    )

    client: KafkaClient = boto3.client("kafka")

    list_cluster_operations_paginator: ListClusterOperationsPaginator = client.get_paginator("list_cluster_operations")
    list_clusters_paginator: ListClustersPaginator = client.get_paginator("list_clusters")
    list_clusters_v2_paginator: ListClustersV2Paginator = client.get_paginator("list_clusters_v2")
    list_configuration_revisions_paginator: ListConfigurationRevisionsPaginator = client.get_paginator("list_configuration_revisions")
    list_configurations_paginator: ListConfigurationsPaginator = client.get_paginator("list_configurations")
    list_kafka_versions_paginator: ListKafkaVersionsPaginator = client.get_paginator("list_kafka_versions")
    list_nodes_paginator: ListNodesPaginator = client.get_paginator("list_nodes")
    list_scram_secrets_paginator: ListScramSecretsPaginator = client.get_paginator("list_scram_secrets")
    ```
"""
from typing import Generic, Iterator, TypeVar

from botocore.paginate import PageIterator
from botocore.paginate import Paginator as Boto3Paginator

from .type_defs import (
    ListClusterOperationsResponseTypeDef,
    ListClustersResponseTypeDef,
    ListClustersV2ResponseTypeDef,
    ListConfigurationRevisionsResponseTypeDef,
    ListConfigurationsResponseTypeDef,
    ListKafkaVersionsResponseTypeDef,
    ListNodesResponseTypeDef,
    ListScramSecretsResponseTypeDef,
    PaginatorConfigTypeDef,
)

__all__ = (
    "ListClusterOperationsPaginator",
    "ListClustersPaginator",
    "ListClustersV2Paginator",
    "ListConfigurationRevisionsPaginator",
    "ListConfigurationsPaginator",
    "ListKafkaVersionsPaginator",
    "ListNodesPaginator",
    "ListScramSecretsPaginator",
)


_ItemTypeDef = TypeVar("_ItemTypeDef")


class _PageIterator(Generic[_ItemTypeDef], PageIterator):
    def __iter__(self) -> Iterator[_ItemTypeDef]:
        """
        Proxy method to specify iterator item type.
        """


class ListClusterOperationsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/kafka.html#Kafka.Paginator.ListClusterOperations)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafka/paginators.html#listclusteroperationspaginator)
    """

    def paginate(
        self, *, ClusterArn: str, PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListClusterOperationsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/kafka.html#Kafka.Paginator.ListClusterOperations.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafka/paginators.html#listclusteroperationspaginator)
        """


class ListClustersPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/kafka.html#Kafka.Paginator.ListClusters)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafka/paginators.html#listclusterspaginator)
    """

    def paginate(
        self, *, ClusterNameFilter: str = ..., PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListClustersResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/kafka.html#Kafka.Paginator.ListClusters.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafka/paginators.html#listclusterspaginator)
        """


class ListClustersV2Paginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/kafka.html#Kafka.Paginator.ListClustersV2)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafka/paginators.html#listclustersv2paginator)
    """

    def paginate(
        self,
        *,
        ClusterNameFilter: str = ...,
        ClusterTypeFilter: str = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListClustersV2ResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/kafka.html#Kafka.Paginator.ListClustersV2.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafka/paginators.html#listclustersv2paginator)
        """


class ListConfigurationRevisionsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/kafka.html#Kafka.Paginator.ListConfigurationRevisions)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafka/paginators.html#listconfigurationrevisionspaginator)
    """

    def paginate(
        self, *, Arn: str, PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListConfigurationRevisionsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/kafka.html#Kafka.Paginator.ListConfigurationRevisions.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafka/paginators.html#listconfigurationrevisionspaginator)
        """


class ListConfigurationsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/kafka.html#Kafka.Paginator.ListConfigurations)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafka/paginators.html#listconfigurationspaginator)
    """

    def paginate(
        self, *, PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListConfigurationsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/kafka.html#Kafka.Paginator.ListConfigurations.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafka/paginators.html#listconfigurationspaginator)
        """


class ListKafkaVersionsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/kafka.html#Kafka.Paginator.ListKafkaVersions)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafka/paginators.html#listkafkaversionspaginator)
    """

    def paginate(
        self, *, PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListKafkaVersionsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/kafka.html#Kafka.Paginator.ListKafkaVersions.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafka/paginators.html#listkafkaversionspaginator)
        """


class ListNodesPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/kafka.html#Kafka.Paginator.ListNodes)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafka/paginators.html#listnodespaginator)
    """

    def paginate(
        self, *, ClusterArn: str, PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListNodesResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/kafka.html#Kafka.Paginator.ListNodes.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafka/paginators.html#listnodespaginator)
        """


class ListScramSecretsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/kafka.html#Kafka.Paginator.ListScramSecrets)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafka/paginators.html#listscramsecretspaginator)
    """

    def paginate(
        self, *, ClusterArn: str, PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListScramSecretsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/kafka.html#Kafka.Paginator.ListScramSecrets.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafka/paginators.html#listscramsecretspaginator)
        """
