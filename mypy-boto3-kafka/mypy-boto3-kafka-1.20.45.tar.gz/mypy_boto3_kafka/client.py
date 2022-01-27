"""
Type annotations for kafka service client.

[Open documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafka/client.html)

Usage::

    ```python
    import boto3
    from mypy_boto3_kafka import KafkaClient

    client: KafkaClient = boto3.client("kafka")
    ```
"""
import sys
from typing import IO, Any, Dict, Mapping, Sequence, Type, Union, overload

from botocore.client import BaseClient, ClientMeta
from botocore.response import StreamingBody

from .literals import EnhancedMonitoringType
from .paginator import (
    ListClusterOperationsPaginator,
    ListClustersPaginator,
    ListClustersV2Paginator,
    ListConfigurationRevisionsPaginator,
    ListConfigurationsPaginator,
    ListKafkaVersionsPaginator,
    ListNodesPaginator,
    ListScramSecretsPaginator,
)
from .type_defs import (
    BatchAssociateScramSecretResponseTypeDef,
    BatchDisassociateScramSecretResponseTypeDef,
    BrokerEBSVolumeInfoTypeDef,
    BrokerNodeGroupInfoTypeDef,
    ClientAuthenticationTypeDef,
    ConfigurationInfoTypeDef,
    ConnectivityInfoTypeDef,
    CreateClusterResponseTypeDef,
    CreateClusterV2ResponseTypeDef,
    CreateConfigurationResponseTypeDef,
    DeleteClusterResponseTypeDef,
    DeleteConfigurationResponseTypeDef,
    DescribeClusterOperationResponseTypeDef,
    DescribeClusterResponseTypeDef,
    DescribeClusterV2ResponseTypeDef,
    DescribeConfigurationResponseTypeDef,
    DescribeConfigurationRevisionResponseTypeDef,
    EncryptionInfoTypeDef,
    GetBootstrapBrokersResponseTypeDef,
    GetCompatibleKafkaVersionsResponseTypeDef,
    ListClusterOperationsResponseTypeDef,
    ListClustersResponseTypeDef,
    ListClustersV2ResponseTypeDef,
    ListConfigurationRevisionsResponseTypeDef,
    ListConfigurationsResponseTypeDef,
    ListKafkaVersionsResponseTypeDef,
    ListNodesResponseTypeDef,
    ListScramSecretsResponseTypeDef,
    ListTagsForResourceResponseTypeDef,
    LoggingInfoTypeDef,
    OpenMonitoringInfoTypeDef,
    ProvisionedRequestTypeDef,
    RebootBrokerResponseTypeDef,
    ServerlessRequestTypeDef,
    UpdateBrokerCountResponseTypeDef,
    UpdateBrokerStorageResponseTypeDef,
    UpdateBrokerTypeResponseTypeDef,
    UpdateClusterConfigurationResponseTypeDef,
    UpdateClusterKafkaVersionResponseTypeDef,
    UpdateConfigurationResponseTypeDef,
    UpdateConnectivityResponseTypeDef,
    UpdateMonitoringResponseTypeDef,
    UpdateSecurityResponseTypeDef,
)

if sys.version_info >= (3, 9):
    from typing import Literal
else:
    from typing_extensions import Literal


__all__ = ("KafkaClient",)


class BotocoreClientError(BaseException):
    MSG_TEMPLATE: str

    def __init__(self, error_response: Mapping[str, Any], operation_name: str) -> None:
        self.response: Dict[str, Any]
        self.operation_name: str


class Exceptions:
    BadRequestException: Type[BotocoreClientError]
    ClientError: Type[BotocoreClientError]
    ConflictException: Type[BotocoreClientError]
    ForbiddenException: Type[BotocoreClientError]
    InternalServerErrorException: Type[BotocoreClientError]
    NotFoundException: Type[BotocoreClientError]
    ServiceUnavailableException: Type[BotocoreClientError]
    TooManyRequestsException: Type[BotocoreClientError]
    UnauthorizedException: Type[BotocoreClientError]


class KafkaClient(BaseClient):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/kafka.html#Kafka.Client)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafka/client.html)
    """

    meta: ClientMeta

    @property
    def exceptions(self) -> Exceptions:
        """
        KafkaClient exceptions.
        """

    def batch_associate_scram_secret(
        self, *, ClusterArn: str, SecretArnList: Sequence[str]
    ) -> BatchAssociateScramSecretResponseTypeDef:
        """
        Associates one or more Scram Secrets with an Amazon MSK cluster.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/kafka.html#Kafka.Client.batch_associate_scram_secret)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafka/client.html#batch_associate_scram_secret)
        """

    def batch_disassociate_scram_secret(
        self, *, ClusterArn: str, SecretArnList: Sequence[str]
    ) -> BatchDisassociateScramSecretResponseTypeDef:
        """
        Disassociates one or more Scram Secrets from an Amazon MSK cluster.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/kafka.html#Kafka.Client.batch_disassociate_scram_secret)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafka/client.html#batch_disassociate_scram_secret)
        """

    def can_paginate(self, operation_name: str) -> bool:
        """
        Check if an operation can be paginated.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/kafka.html#Kafka.Client.can_paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafka/client.html#can_paginate)
        """

    def create_cluster(
        self,
        *,
        BrokerNodeGroupInfo: "BrokerNodeGroupInfoTypeDef",
        ClusterName: str,
        KafkaVersion: str,
        NumberOfBrokerNodes: int,
        ClientAuthentication: "ClientAuthenticationTypeDef" = ...,
        ConfigurationInfo: "ConfigurationInfoTypeDef" = ...,
        EncryptionInfo: "EncryptionInfoTypeDef" = ...,
        EnhancedMonitoring: EnhancedMonitoringType = ...,
        OpenMonitoring: "OpenMonitoringInfoTypeDef" = ...,
        LoggingInfo: "LoggingInfoTypeDef" = ...,
        Tags: Mapping[str, str] = ...
    ) -> CreateClusterResponseTypeDef:
        """
        Creates a new MSK cluster.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/kafka.html#Kafka.Client.create_cluster)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafka/client.html#create_cluster)
        """

    def create_cluster_v2(
        self,
        *,
        ClusterName: str,
        Tags: Mapping[str, str] = ...,
        Provisioned: "ProvisionedRequestTypeDef" = ...,
        Serverless: "ServerlessRequestTypeDef" = ...
    ) -> CreateClusterV2ResponseTypeDef:
        """
        Creates a new MSK cluster.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/kafka.html#Kafka.Client.create_cluster_v2)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafka/client.html#create_cluster_v2)
        """

    def create_configuration(
        self,
        *,
        Name: str,
        ServerProperties: Union[bytes, IO[bytes], StreamingBody],
        Description: str = ...,
        KafkaVersions: Sequence[str] = ...
    ) -> CreateConfigurationResponseTypeDef:
        """
        Creates a new MSK configuration.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/kafka.html#Kafka.Client.create_configuration)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafka/client.html#create_configuration)
        """

    def delete_cluster(
        self, *, ClusterArn: str, CurrentVersion: str = ...
    ) -> DeleteClusterResponseTypeDef:
        """
        Deletes the MSK cluster specified by the Amazon Resource Name (ARN) in the
        request.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/kafka.html#Kafka.Client.delete_cluster)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafka/client.html#delete_cluster)
        """

    def delete_configuration(self, *, Arn: str) -> DeleteConfigurationResponseTypeDef:
        """
        Deletes an MSK Configuration.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/kafka.html#Kafka.Client.delete_configuration)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafka/client.html#delete_configuration)
        """

    def describe_cluster(self, *, ClusterArn: str) -> DescribeClusterResponseTypeDef:
        """
        Returns a description of the MSK cluster whose Amazon Resource Name (ARN) is
        specified in the request.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/kafka.html#Kafka.Client.describe_cluster)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafka/client.html#describe_cluster)
        """

    def describe_cluster_operation(
        self, *, ClusterOperationArn: str
    ) -> DescribeClusterOperationResponseTypeDef:
        """
        Returns a description of the cluster operation specified by the ARN.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/kafka.html#Kafka.Client.describe_cluster_operation)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafka/client.html#describe_cluster_operation)
        """

    def describe_cluster_v2(self, *, ClusterArn: str) -> DescribeClusterV2ResponseTypeDef:
        """
        Returns a description of the MSK cluster whose Amazon Resource Name (ARN) is
        specified in the request.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/kafka.html#Kafka.Client.describe_cluster_v2)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafka/client.html#describe_cluster_v2)
        """

    def describe_configuration(self, *, Arn: str) -> DescribeConfigurationResponseTypeDef:
        """
        Returns a description of this MSK configuration.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/kafka.html#Kafka.Client.describe_configuration)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafka/client.html#describe_configuration)
        """

    def describe_configuration_revision(
        self, *, Arn: str, Revision: int
    ) -> DescribeConfigurationRevisionResponseTypeDef:
        """
        Returns a description of this revision of the configuration.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/kafka.html#Kafka.Client.describe_configuration_revision)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafka/client.html#describe_configuration_revision)
        """

    def generate_presigned_url(
        self,
        ClientMethod: str,
        Params: Mapping[str, Any] = ...,
        ExpiresIn: int = 3600,
        HttpMethod: str = ...,
    ) -> str:
        """
        Generate a presigned url given a client, its method, and arguments.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/kafka.html#Kafka.Client.generate_presigned_url)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafka/client.html#generate_presigned_url)
        """

    def get_bootstrap_brokers(self, *, ClusterArn: str) -> GetBootstrapBrokersResponseTypeDef:
        """
        A list of brokers that a client application can use to bootstrap.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/kafka.html#Kafka.Client.get_bootstrap_brokers)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafka/client.html#get_bootstrap_brokers)
        """

    def get_compatible_kafka_versions(
        self, *, ClusterArn: str = ...
    ) -> GetCompatibleKafkaVersionsResponseTypeDef:
        """
        Gets the Apache Kafka versions to which you can update the MSK cluster.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/kafka.html#Kafka.Client.get_compatible_kafka_versions)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafka/client.html#get_compatible_kafka_versions)
        """

    def list_cluster_operations(
        self, *, ClusterArn: str, MaxResults: int = ..., NextToken: str = ...
    ) -> ListClusterOperationsResponseTypeDef:
        """
        Returns a list of all the operations that have been performed on the specified
        MSK cluster.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/kafka.html#Kafka.Client.list_cluster_operations)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafka/client.html#list_cluster_operations)
        """

    def list_clusters(
        self, *, ClusterNameFilter: str = ..., MaxResults: int = ..., NextToken: str = ...
    ) -> ListClustersResponseTypeDef:
        """
        Returns a list of all the MSK clusters in the current Region.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/kafka.html#Kafka.Client.list_clusters)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafka/client.html#list_clusters)
        """

    def list_clusters_v2(
        self,
        *,
        ClusterNameFilter: str = ...,
        ClusterTypeFilter: str = ...,
        MaxResults: int = ...,
        NextToken: str = ...
    ) -> ListClustersV2ResponseTypeDef:
        """
        Returns a list of all the MSK clusters in the current Region.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/kafka.html#Kafka.Client.list_clusters_v2)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafka/client.html#list_clusters_v2)
        """

    def list_configuration_revisions(
        self, *, Arn: str, MaxResults: int = ..., NextToken: str = ...
    ) -> ListConfigurationRevisionsResponseTypeDef:
        """
        Returns a list of all the MSK configurations in this Region.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/kafka.html#Kafka.Client.list_configuration_revisions)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafka/client.html#list_configuration_revisions)
        """

    def list_configurations(
        self, *, MaxResults: int = ..., NextToken: str = ...
    ) -> ListConfigurationsResponseTypeDef:
        """
        Returns a list of all the MSK configurations in this Region.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/kafka.html#Kafka.Client.list_configurations)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafka/client.html#list_configurations)
        """

    def list_kafka_versions(
        self, *, MaxResults: int = ..., NextToken: str = ...
    ) -> ListKafkaVersionsResponseTypeDef:
        """
        Returns a list of Apache Kafka versions.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/kafka.html#Kafka.Client.list_kafka_versions)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafka/client.html#list_kafka_versions)
        """

    def list_nodes(
        self, *, ClusterArn: str, MaxResults: int = ..., NextToken: str = ...
    ) -> ListNodesResponseTypeDef:
        """
        Returns a list of the broker nodes in the cluster.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/kafka.html#Kafka.Client.list_nodes)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafka/client.html#list_nodes)
        """

    def list_scram_secrets(
        self, *, ClusterArn: str, MaxResults: int = ..., NextToken: str = ...
    ) -> ListScramSecretsResponseTypeDef:
        """
        Returns a list of the Scram Secrets associated with an Amazon MSK cluster.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/kafka.html#Kafka.Client.list_scram_secrets)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafka/client.html#list_scram_secrets)
        """

    def list_tags_for_resource(self, *, ResourceArn: str) -> ListTagsForResourceResponseTypeDef:
        """
        Returns a list of the tags associated with the specified resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/kafka.html#Kafka.Client.list_tags_for_resource)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafka/client.html#list_tags_for_resource)
        """

    def reboot_broker(
        self, *, BrokerIds: Sequence[str], ClusterArn: str
    ) -> RebootBrokerResponseTypeDef:
        """
        Reboots brokers.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/kafka.html#Kafka.Client.reboot_broker)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafka/client.html#reboot_broker)
        """

    def tag_resource(self, *, ResourceArn: str, Tags: Mapping[str, str]) -> None:
        """
        Adds tags to the specified MSK resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/kafka.html#Kafka.Client.tag_resource)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafka/client.html#tag_resource)
        """

    def untag_resource(self, *, ResourceArn: str, TagKeys: Sequence[str]) -> None:
        """
        Removes the tags associated with the keys that are provided in the query.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/kafka.html#Kafka.Client.untag_resource)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafka/client.html#untag_resource)
        """

    def update_broker_count(
        self, *, ClusterArn: str, CurrentVersion: str, TargetNumberOfBrokerNodes: int
    ) -> UpdateBrokerCountResponseTypeDef:
        """
        Updates the number of broker nodes in the cluster.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/kafka.html#Kafka.Client.update_broker_count)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafka/client.html#update_broker_count)
        """

    def update_broker_storage(
        self,
        *,
        ClusterArn: str,
        CurrentVersion: str,
        TargetBrokerEBSVolumeInfo: Sequence["BrokerEBSVolumeInfoTypeDef"]
    ) -> UpdateBrokerStorageResponseTypeDef:
        """
        Updates the EBS storage associated with MSK brokers.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/kafka.html#Kafka.Client.update_broker_storage)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafka/client.html#update_broker_storage)
        """

    def update_broker_type(
        self, *, ClusterArn: str, CurrentVersion: str, TargetInstanceType: str
    ) -> UpdateBrokerTypeResponseTypeDef:
        """
        Updates EC2 instance type.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/kafka.html#Kafka.Client.update_broker_type)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafka/client.html#update_broker_type)
        """

    def update_cluster_configuration(
        self, *, ClusterArn: str, ConfigurationInfo: "ConfigurationInfoTypeDef", CurrentVersion: str
    ) -> UpdateClusterConfigurationResponseTypeDef:
        """
        Updates the cluster with the configuration that is specified in the request
        body.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/kafka.html#Kafka.Client.update_cluster_configuration)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafka/client.html#update_cluster_configuration)
        """

    def update_cluster_kafka_version(
        self,
        *,
        ClusterArn: str,
        CurrentVersion: str,
        TargetKafkaVersion: str,
        ConfigurationInfo: "ConfigurationInfoTypeDef" = ...
    ) -> UpdateClusterKafkaVersionResponseTypeDef:
        """
        Updates the Apache Kafka version for the cluster.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/kafka.html#Kafka.Client.update_cluster_kafka_version)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafka/client.html#update_cluster_kafka_version)
        """

    def update_configuration(
        self,
        *,
        Arn: str,
        ServerProperties: Union[bytes, IO[bytes], StreamingBody],
        Description: str = ...
    ) -> UpdateConfigurationResponseTypeDef:
        """
        Updates an MSK configuration.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/kafka.html#Kafka.Client.update_configuration)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafka/client.html#update_configuration)
        """

    def update_connectivity(
        self, *, ClusterArn: str, ConnectivityInfo: "ConnectivityInfoTypeDef", CurrentVersion: str
    ) -> UpdateConnectivityResponseTypeDef:
        """
        Updates the cluster's connectivity configuration.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/kafka.html#Kafka.Client.update_connectivity)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafka/client.html#update_connectivity)
        """

    def update_monitoring(
        self,
        *,
        ClusterArn: str,
        CurrentVersion: str,
        EnhancedMonitoring: EnhancedMonitoringType = ...,
        OpenMonitoring: "OpenMonitoringInfoTypeDef" = ...,
        LoggingInfo: "LoggingInfoTypeDef" = ...
    ) -> UpdateMonitoringResponseTypeDef:
        """
        Updates the monitoring settings for the cluster.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/kafka.html#Kafka.Client.update_monitoring)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafka/client.html#update_monitoring)
        """

    def update_security(
        self,
        *,
        ClusterArn: str,
        CurrentVersion: str,
        ClientAuthentication: "ClientAuthenticationTypeDef" = ...,
        EncryptionInfo: "EncryptionInfoTypeDef" = ...
    ) -> UpdateSecurityResponseTypeDef:
        """
        Updates the security settings for the cluster.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/kafka.html#Kafka.Client.update_security)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafka/client.html#update_security)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_cluster_operations"]
    ) -> ListClusterOperationsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/kafka.html#Kafka.Paginator.ListClusterOperations)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafka/paginators.html#listclusteroperationspaginator)
        """

    @overload
    def get_paginator(self, operation_name: Literal["list_clusters"]) -> ListClustersPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/kafka.html#Kafka.Paginator.ListClusters)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafka/paginators.html#listclusterspaginator)
        """

    @overload
    def get_paginator(self, operation_name: Literal["list_clusters_v2"]) -> ListClustersV2Paginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/kafka.html#Kafka.Paginator.ListClustersV2)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafka/paginators.html#listclustersv2paginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_configuration_revisions"]
    ) -> ListConfigurationRevisionsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/kafka.html#Kafka.Paginator.ListConfigurationRevisions)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafka/paginators.html#listconfigurationrevisionspaginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_configurations"]
    ) -> ListConfigurationsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/kafka.html#Kafka.Paginator.ListConfigurations)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafka/paginators.html#listconfigurationspaginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_kafka_versions"]
    ) -> ListKafkaVersionsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/kafka.html#Kafka.Paginator.ListKafkaVersions)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafka/paginators.html#listkafkaversionspaginator)
        """

    @overload
    def get_paginator(self, operation_name: Literal["list_nodes"]) -> ListNodesPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/kafka.html#Kafka.Paginator.ListNodes)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafka/paginators.html#listnodespaginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_scram_secrets"]
    ) -> ListScramSecretsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/kafka.html#Kafka.Paginator.ListScramSecrets)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_kafka/paginators.html#listscramsecretspaginator)
        """
