"""
Type annotations for ec2 service ServiceResource

[Open documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html)

Usage::

    ```python
    import boto3

    from mypy_boto3_ec2 import EC2ServiceResource
    import mypy_boto3_ec2.service_resource as ec2_resources

    resource: EC2ServiceResource = boto3.resource("ec2")

    my_classic_address: ec2_resources.ClassicAddress = resource.ClassicAddress(...)
    my_dhcp_options: ec2_resources.DhcpOptions = resource.DhcpOptions(...)
    my_image: ec2_resources.Image = resource.Image(...)
    my_instance: ec2_resources.Instance = resource.Instance(...)
    my_internet_gateway: ec2_resources.InternetGateway = resource.InternetGateway(...)
    my_key_pair: ec2_resources.KeyPair = resource.KeyPair(...)
    my_key_pair_info: ec2_resources.KeyPairInfo = resource.KeyPairInfo(...)
    my_network_acl: ec2_resources.NetworkAcl = resource.NetworkAcl(...)
    my_network_interface: ec2_resources.NetworkInterface = resource.NetworkInterface(...)
    my_network_interface_association: ec2_resources.NetworkInterfaceAssociation = resource.NetworkInterfaceAssociation(...)
    my_placement_group: ec2_resources.PlacementGroup = resource.PlacementGroup(...)
    my_route: ec2_resources.Route = resource.Route(...)
    my_route_table: ec2_resources.RouteTable = resource.RouteTable(...)
    my_route_table_association: ec2_resources.RouteTableAssociation = resource.RouteTableAssociation(...)
    my_security_group: ec2_resources.SecurityGroup = resource.SecurityGroup(...)
    my_snapshot: ec2_resources.Snapshot = resource.Snapshot(...)
    my_subnet: ec2_resources.Subnet = resource.Subnet(...)
    my_tag: ec2_resources.Tag = resource.Tag(...)
    my_volume: ec2_resources.Volume = resource.Volume(...)
    my_vpc: ec2_resources.Vpc = resource.Vpc(...)
    my_vpc_peering_connection: ec2_resources.VpcPeeringConnection = resource.VpcPeeringConnection(...)
    my_vpc_address: ec2_resources.VpcAddress = resource.VpcAddress(...)
```
"""
import sys
from datetime import datetime
from typing import IO, Any, Dict, Iterator, List, Optional, Sequence, Union

from boto3.resources.base import ResourceMeta
from boto3.resources.base import ServiceResource as Boto3ServiceResource
from boto3.resources.collection import ResourceCollection
from botocore.response import StreamingBody

from .client import EC2Client
from .literals import (
    ArchitectureValuesType,
    BootModeValuesType,
    ImageAttributeNameType,
    InstanceAttributeNameType,
    InstanceTypeType,
    KeyTypeType,
    NetworkInterfaceAttributeType,
    NetworkInterfaceCreationTypeType,
    OperationTypeType,
    PlacementStrategyType,
    ReportInstanceReasonCodesType,
    ReportStatusTypeType,
    RuleActionType,
    ShutdownBehaviorType,
    SnapshotAttributeNameType,
    TenancyType,
    VolumeAttributeNameType,
    VolumeTypeType,
    VpcAttributeNameType,
)
from .type_defs import (
    AcceptVpcPeeringConnectionResultTypeDef,
    AssignPrivateIpAddressesResultTypeDef,
    AssociateAddressResultTypeDef,
    AttachClassicLinkVpcResultTypeDef,
    AttachNetworkInterfaceResultTypeDef,
    AttributeBooleanValueTypeDef,
    AttributeValueTypeDef,
    AuthorizeSecurityGroupEgressResultTypeDef,
    AuthorizeSecurityGroupIngressResultTypeDef,
    BlobAttributeValueTypeDef,
    BlockDeviceMappingTypeDef,
    CapacityReservationSpecificationTypeDef,
    CopySnapshotResultTypeDef,
    CpuOptionsRequestTypeDef,
    CreateVolumePermissionModificationsTypeDef,
    CreditSpecificationRequestTypeDef,
    DeleteVpcPeeringConnectionResultTypeDef,
    DescribeNetworkInterfaceAttributeResultTypeDef,
    DescribeSnapshotAttributeResultTypeDef,
    DescribeVolumeAttributeResultTypeDef,
    DescribeVolumeStatusResultTypeDef,
    DescribeVpcAttributeResultTypeDef,
    DetachClassicLinkVpcResultTypeDef,
    DisableVpcClassicLinkResultTypeDef,
    ElasticGpuSpecificationTypeDef,
    ElasticInferenceAcceleratorTypeDef,
    EnableVpcClassicLinkResultTypeDef,
    EnclaveOptionsRequestTypeDef,
    FilterTypeDef,
    GetConsoleOutputResultTypeDef,
    GetPasswordDataResultTypeDef,
    HibernationOptionsRequestTypeDef,
    IamInstanceProfileSpecificationTypeDef,
    IcmpTypeCodeTypeDef,
    ImageAttributeTypeDef,
    InstanceAttributeTypeDef,
    InstanceBlockDeviceMappingSpecificationTypeDef,
    InstanceIpv6AddressTypeDef,
    InstanceMarketOptionsRequestTypeDef,
    InstanceMetadataOptionsRequestTypeDef,
    InstanceNetworkInterfaceSpecificationTypeDef,
    IpPermissionTypeDef,
    Ipv4PrefixSpecificationRequestTypeDef,
    Ipv6PrefixSpecificationRequestTypeDef,
    LaunchPermissionModificationsTypeDef,
    LaunchTemplateSpecificationTypeDef,
    LicenseConfigurationRequestTypeDef,
    MonitorInstancesResultTypeDef,
    NetworkInterfaceAttachmentChangesTypeDef,
    NewDhcpConfigurationTypeDef,
    PlacementTypeDef,
    PortRangeTypeDef,
    PrivateDnsNameOptionsRequestTypeDef,
    PrivateIpAddressSpecificationTypeDef,
    RejectVpcPeeringConnectionResultTypeDef,
    ReplaceNetworkAclAssociationResultTypeDef,
    RevokeSecurityGroupEgressResultTypeDef,
    RevokeSecurityGroupIngressResultTypeDef,
    RunInstancesMonitoringEnabledTypeDef,
    StartInstancesResultTypeDef,
    StopInstancesResultTypeDef,
    TagSpecificationTypeDef,
    TagTypeDef,
    TerminateInstancesResultTypeDef,
    UnmonitorInstancesResultTypeDef,
    VolumeAttachmentResponseMetadataTypeDef,
)

if sys.version_info >= (3, 9):
    from typing import Literal
else:
    from typing_extensions import Literal


__all__ = (
    "EC2ServiceResource",
    "ClassicAddress",
    "DhcpOptions",
    "Image",
    "Instance",
    "InternetGateway",
    "KeyPair",
    "KeyPairInfo",
    "NetworkAcl",
    "NetworkInterface",
    "NetworkInterfaceAssociation",
    "PlacementGroup",
    "Route",
    "RouteTable",
    "RouteTableAssociation",
    "SecurityGroup",
    "Snapshot",
    "Subnet",
    "Tag",
    "Volume",
    "Vpc",
    "VpcPeeringConnection",
    "VpcAddress",
    "ServiceResourceClassicAddressesCollection",
    "ServiceResourceDhcpOptionsSetsCollection",
    "ServiceResourceImagesCollection",
    "ServiceResourceInstancesCollection",
    "ServiceResourceInternetGatewaysCollection",
    "ServiceResourceKeyPairsCollection",
    "ServiceResourceNetworkAclsCollection",
    "ServiceResourceNetworkInterfacesCollection",
    "ServiceResourcePlacementGroupsCollection",
    "ServiceResourceRouteTablesCollection",
    "ServiceResourceSecurityGroupsCollection",
    "ServiceResourceSnapshotsCollection",
    "ServiceResourceSubnetsCollection",
    "ServiceResourceVolumesCollection",
    "ServiceResourceVpcAddressesCollection",
    "ServiceResourceVpcPeeringConnectionsCollection",
    "ServiceResourceVpcsCollection",
    "InstanceVolumesCollection",
    "InstanceVpcAddressesCollection",
    "PlacementGroupInstancesCollection",
    "SubnetInstancesCollection",
    "SubnetNetworkInterfacesCollection",
    "VolumeSnapshotsCollection",
    "VpcAcceptedVpcPeeringConnectionsCollection",
    "VpcInstancesCollection",
    "VpcInternetGatewaysCollection",
    "VpcNetworkAclsCollection",
    "VpcNetworkInterfacesCollection",
    "VpcRequestedVpcPeeringConnectionsCollection",
    "VpcRouteTablesCollection",
    "VpcSecurityGroupsCollection",
    "VpcSubnetsCollection",
)


class ServiceResourceClassicAddressesCollection(ResourceCollection):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.classic_addresses)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#serviceresourceclassicaddressescollection)
    """

    def all(self) -> "ServiceResourceClassicAddressesCollection":
        """
        Get all items from the collection, optionally with a custom page size and item count limit.
        """

    def filter(  # type: ignore
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        PublicIps: Sequence[str] = ...,
        AllocationIds: Sequence[str] = ...,
        DryRun: bool = ...
    ) -> "ServiceResourceClassicAddressesCollection":
        """
        Get items from the collection, passing keyword arguments along as parameters to the underlying service operation, which are typically used to filter the results.
        """

    def limit(self, count: int) -> "ServiceResourceClassicAddressesCollection":
        """
        Return at most this many ClassicAddresss.
        """

    def page_size(self, count: int) -> "ServiceResourceClassicAddressesCollection":
        """
        Fetch at most this many ClassicAddresss per service request.
        """

    def pages(self) -> Iterator[List["ClassicAddress"]]:
        """
        A generator which yields pages of ClassicAddresss.
        """

    def __iter__(self) -> Iterator["ClassicAddress"]:
        """
        A generator which yields ClassicAddresss.
        """


class ServiceResourceDhcpOptionsSetsCollection(ResourceCollection):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.dhcp_options_sets)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#serviceresourcedhcpoptionssetscollection)
    """

    def all(self) -> "ServiceResourceDhcpOptionsSetsCollection":
        """
        Get all items from the collection, optionally with a custom page size and item count limit.
        """

    def filter(  # type: ignore
        self,
        *,
        DhcpOptionsIds: Sequence[str] = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        DryRun: bool = ...,
        NextToken: str = ...,
        MaxResults: int = ...
    ) -> "ServiceResourceDhcpOptionsSetsCollection":
        """
        Get items from the collection, passing keyword arguments along as parameters to the underlying service operation, which are typically used to filter the results.
        """

    def limit(self, count: int) -> "ServiceResourceDhcpOptionsSetsCollection":
        """
        Return at most this many DhcpOptionss.
        """

    def page_size(self, count: int) -> "ServiceResourceDhcpOptionsSetsCollection":
        """
        Fetch at most this many DhcpOptionss per service request.
        """

    def pages(self) -> Iterator[List["DhcpOptions"]]:
        """
        A generator which yields pages of DhcpOptionss.
        """

    def __iter__(self) -> Iterator["DhcpOptions"]:
        """
        A generator which yields DhcpOptionss.
        """


class ServiceResourceImagesCollection(ResourceCollection):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.images)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#serviceresourceimagescollection)
    """

    def all(self) -> "ServiceResourceImagesCollection":
        """
        Get all items from the collection, optionally with a custom page size and item count limit.
        """

    def filter(  # type: ignore
        self,
        *,
        ExecutableUsers: Sequence[str] = ...,
        Filters: Sequence["FilterTypeDef"] = ...,
        ImageIds: Sequence[str] = ...,
        Owners: Sequence[str] = ...,
        IncludeDeprecated: bool = ...,
        DryRun: bool = ...
    ) -> "ServiceResourceImagesCollection":
        """
        Get items from the collection, passing keyword arguments along as parameters to the underlying service operation, which are typically used to filter the results.
        """

    def limit(self, count: int) -> "ServiceResourceImagesCollection":
        """
        Return at most this many Images.
        """

    def page_size(self, count: int) -> "ServiceResourceImagesCollection":
        """
        Fetch at most this many Images per service request.
        """

    def pages(self) -> Iterator[List["Image"]]:
        """
        A generator which yields pages of Images.
        """

    def __iter__(self) -> Iterator["Image"]:
        """
        A generator which yields Images.
        """


class ServiceResourceInstancesCollection(ResourceCollection):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.instances)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#serviceresourceinstancescollection)
    """

    def all(self) -> "ServiceResourceInstancesCollection":
        """
        Get all items from the collection, optionally with a custom page size and item count limit.
        """

    def filter(  # type: ignore
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        InstanceIds: Sequence[str] = ...,
        DryRun: bool = ...,
        MaxResults: int = ...,
        NextToken: str = ...
    ) -> "ServiceResourceInstancesCollection":
        """
        Get items from the collection, passing keyword arguments along as parameters to the underlying service operation, which are typically used to filter the results.
        """

    def create_tags(self, *, DryRun: bool = ...) -> None:
        """
        Batch method.
        """

    def monitor(self, *, DryRun: bool = ...) -> MonitorInstancesResultTypeDef:
        """
        Batch method.
        """

    def reboot(self, *, DryRun: bool = ...) -> None:
        """
        Batch method.
        """

    def start(
        self, *, AdditionalInfo: str = ..., DryRun: bool = ...
    ) -> StartInstancesResultTypeDef:
        """
        Batch method.
        """

    def stop(
        self, *, Hibernate: bool = ..., DryRun: bool = ..., Force: bool = ...
    ) -> StopInstancesResultTypeDef:
        """
        Batch method.
        """

    def terminate(self, *, DryRun: bool = ...) -> TerminateInstancesResultTypeDef:
        """
        Batch method.
        """

    def unmonitor(self, *, DryRun: bool = ...) -> UnmonitorInstancesResultTypeDef:
        """
        Batch method.
        """

    def limit(self, count: int) -> "ServiceResourceInstancesCollection":
        """
        Return at most this many Instances.
        """

    def page_size(self, count: int) -> "ServiceResourceInstancesCollection":
        """
        Fetch at most this many Instances per service request.
        """

    def pages(self) -> Iterator[List["Instance"]]:
        """
        A generator which yields pages of Instances.
        """

    def __iter__(self) -> Iterator["Instance"]:
        """
        A generator which yields Instances.
        """


class ServiceResourceInternetGatewaysCollection(ResourceCollection):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.internet_gateways)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#serviceresourceinternetgatewayscollection)
    """

    def all(self) -> "ServiceResourceInternetGatewaysCollection":
        """
        Get all items from the collection, optionally with a custom page size and item count limit.
        """

    def filter(  # type: ignore
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        DryRun: bool = ...,
        InternetGatewayIds: Sequence[str] = ...,
        NextToken: str = ...,
        MaxResults: int = ...
    ) -> "ServiceResourceInternetGatewaysCollection":
        """
        Get items from the collection, passing keyword arguments along as parameters to the underlying service operation, which are typically used to filter the results.
        """

    def limit(self, count: int) -> "ServiceResourceInternetGatewaysCollection":
        """
        Return at most this many InternetGateways.
        """

    def page_size(self, count: int) -> "ServiceResourceInternetGatewaysCollection":
        """
        Fetch at most this many InternetGateways per service request.
        """

    def pages(self) -> Iterator[List["InternetGateway"]]:
        """
        A generator which yields pages of InternetGateways.
        """

    def __iter__(self) -> Iterator["InternetGateway"]:
        """
        A generator which yields InternetGateways.
        """


class ServiceResourceKeyPairsCollection(ResourceCollection):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.key_pairs)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#serviceresourcekeypairscollection)
    """

    def all(self) -> "ServiceResourceKeyPairsCollection":
        """
        Get all items from the collection, optionally with a custom page size and item count limit.
        """

    def filter(  # type: ignore
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        KeyNames: Sequence[str] = ...,
        KeyPairIds: Sequence[str] = ...,
        DryRun: bool = ...
    ) -> "ServiceResourceKeyPairsCollection":
        """
        Get items from the collection, passing keyword arguments along as parameters to the underlying service operation, which are typically used to filter the results.
        """

    def limit(self, count: int) -> "ServiceResourceKeyPairsCollection":
        """
        Return at most this many KeyPairInfos.
        """

    def page_size(self, count: int) -> "ServiceResourceKeyPairsCollection":
        """
        Fetch at most this many KeyPairInfos per service request.
        """

    def pages(self) -> Iterator[List["KeyPairInfo"]]:
        """
        A generator which yields pages of KeyPairInfos.
        """

    def __iter__(self) -> Iterator["KeyPairInfo"]:
        """
        A generator which yields KeyPairInfos.
        """


class ServiceResourceNetworkAclsCollection(ResourceCollection):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.network_acls)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#serviceresourcenetworkaclscollection)
    """

    def all(self) -> "ServiceResourceNetworkAclsCollection":
        """
        Get all items from the collection, optionally with a custom page size and item count limit.
        """

    def filter(  # type: ignore
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        DryRun: bool = ...,
        NetworkAclIds: Sequence[str] = ...,
        NextToken: str = ...,
        MaxResults: int = ...
    ) -> "ServiceResourceNetworkAclsCollection":
        """
        Get items from the collection, passing keyword arguments along as parameters to the underlying service operation, which are typically used to filter the results.
        """

    def limit(self, count: int) -> "ServiceResourceNetworkAclsCollection":
        """
        Return at most this many NetworkAcls.
        """

    def page_size(self, count: int) -> "ServiceResourceNetworkAclsCollection":
        """
        Fetch at most this many NetworkAcls per service request.
        """

    def pages(self) -> Iterator[List["NetworkAcl"]]:
        """
        A generator which yields pages of NetworkAcls.
        """

    def __iter__(self) -> Iterator["NetworkAcl"]:
        """
        A generator which yields NetworkAcls.
        """


class ServiceResourceNetworkInterfacesCollection(ResourceCollection):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.network_interfaces)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#serviceresourcenetworkinterfacescollection)
    """

    def all(self) -> "ServiceResourceNetworkInterfacesCollection":
        """
        Get all items from the collection, optionally with a custom page size and item count limit.
        """

    def filter(  # type: ignore
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        DryRun: bool = ...,
        NetworkInterfaceIds: Sequence[str] = ...,
        NextToken: str = ...,
        MaxResults: int = ...
    ) -> "ServiceResourceNetworkInterfacesCollection":
        """
        Get items from the collection, passing keyword arguments along as parameters to the underlying service operation, which are typically used to filter the results.
        """

    def limit(self, count: int) -> "ServiceResourceNetworkInterfacesCollection":
        """
        Return at most this many NetworkInterfaces.
        """

    def page_size(self, count: int) -> "ServiceResourceNetworkInterfacesCollection":
        """
        Fetch at most this many NetworkInterfaces per service request.
        """

    def pages(self) -> Iterator[List["NetworkInterface"]]:
        """
        A generator which yields pages of NetworkInterfaces.
        """

    def __iter__(self) -> Iterator["NetworkInterface"]:
        """
        A generator which yields NetworkInterfaces.
        """


class ServiceResourcePlacementGroupsCollection(ResourceCollection):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.placement_groups)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#serviceresourceplacementgroupscollection)
    """

    def all(self) -> "ServiceResourcePlacementGroupsCollection":
        """
        Get all items from the collection, optionally with a custom page size and item count limit.
        """

    def filter(  # type: ignore
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        DryRun: bool = ...,
        GroupNames: Sequence[str] = ...,
        GroupIds: Sequence[str] = ...
    ) -> "ServiceResourcePlacementGroupsCollection":
        """
        Get items from the collection, passing keyword arguments along as parameters to the underlying service operation, which are typically used to filter the results.
        """

    def limit(self, count: int) -> "ServiceResourcePlacementGroupsCollection":
        """
        Return at most this many PlacementGroups.
        """

    def page_size(self, count: int) -> "ServiceResourcePlacementGroupsCollection":
        """
        Fetch at most this many PlacementGroups per service request.
        """

    def pages(self) -> Iterator[List["PlacementGroup"]]:
        """
        A generator which yields pages of PlacementGroups.
        """

    def __iter__(self) -> Iterator["PlacementGroup"]:
        """
        A generator which yields PlacementGroups.
        """


class ServiceResourceRouteTablesCollection(ResourceCollection):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.route_tables)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#serviceresourceroutetablescollection)
    """

    def all(self) -> "ServiceResourceRouteTablesCollection":
        """
        Get all items from the collection, optionally with a custom page size and item count limit.
        """

    def filter(  # type: ignore
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        DryRun: bool = ...,
        RouteTableIds: Sequence[str] = ...,
        NextToken: str = ...,
        MaxResults: int = ...
    ) -> "ServiceResourceRouteTablesCollection":
        """
        Get items from the collection, passing keyword arguments along as parameters to the underlying service operation, which are typically used to filter the results.
        """

    def limit(self, count: int) -> "ServiceResourceRouteTablesCollection":
        """
        Return at most this many RouteTables.
        """

    def page_size(self, count: int) -> "ServiceResourceRouteTablesCollection":
        """
        Fetch at most this many RouteTables per service request.
        """

    def pages(self) -> Iterator[List["RouteTable"]]:
        """
        A generator which yields pages of RouteTables.
        """

    def __iter__(self) -> Iterator["RouteTable"]:
        """
        A generator which yields RouteTables.
        """


class ServiceResourceSecurityGroupsCollection(ResourceCollection):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.security_groups)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#serviceresourcesecuritygroupscollection)
    """

    def all(self) -> "ServiceResourceSecurityGroupsCollection":
        """
        Get all items from the collection, optionally with a custom page size and item count limit.
        """

    def filter(  # type: ignore
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        GroupIds: Sequence[str] = ...,
        GroupNames: Sequence[str] = ...,
        DryRun: bool = ...,
        NextToken: str = ...,
        MaxResults: int = ...
    ) -> "ServiceResourceSecurityGroupsCollection":
        """
        Get items from the collection, passing keyword arguments along as parameters to the underlying service operation, which are typically used to filter the results.
        """

    def limit(self, count: int) -> "ServiceResourceSecurityGroupsCollection":
        """
        Return at most this many SecurityGroups.
        """

    def page_size(self, count: int) -> "ServiceResourceSecurityGroupsCollection":
        """
        Fetch at most this many SecurityGroups per service request.
        """

    def pages(self) -> Iterator[List["SecurityGroup"]]:
        """
        A generator which yields pages of SecurityGroups.
        """

    def __iter__(self) -> Iterator["SecurityGroup"]:
        """
        A generator which yields SecurityGroups.
        """


class ServiceResourceSnapshotsCollection(ResourceCollection):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.snapshots)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#serviceresourcesnapshotscollection)
    """

    def all(self) -> "ServiceResourceSnapshotsCollection":
        """
        Get all items from the collection, optionally with a custom page size and item count limit.
        """

    def filter(  # type: ignore
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        MaxResults: int = ...,
        NextToken: str = ...,
        OwnerIds: Sequence[str] = ...,
        RestorableByUserIds: Sequence[str] = ...,
        SnapshotIds: Sequence[str] = ...,
        DryRun: bool = ...
    ) -> "ServiceResourceSnapshotsCollection":
        """
        Get items from the collection, passing keyword arguments along as parameters to the underlying service operation, which are typically used to filter the results.
        """

    def limit(self, count: int) -> "ServiceResourceSnapshotsCollection":
        """
        Return at most this many Snapshots.
        """

    def page_size(self, count: int) -> "ServiceResourceSnapshotsCollection":
        """
        Fetch at most this many Snapshots per service request.
        """

    def pages(self) -> Iterator[List["Snapshot"]]:
        """
        A generator which yields pages of Snapshots.
        """

    def __iter__(self) -> Iterator["Snapshot"]:
        """
        A generator which yields Snapshots.
        """


class ServiceResourceSubnetsCollection(ResourceCollection):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.subnets)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#serviceresourcesubnetscollection)
    """

    def all(self) -> "ServiceResourceSubnetsCollection":
        """
        Get all items from the collection, optionally with a custom page size and item count limit.
        """

    def filter(  # type: ignore
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        SubnetIds: Sequence[str] = ...,
        DryRun: bool = ...,
        NextToken: str = ...,
        MaxResults: int = ...
    ) -> "ServiceResourceSubnetsCollection":
        """
        Get items from the collection, passing keyword arguments along as parameters to the underlying service operation, which are typically used to filter the results.
        """

    def limit(self, count: int) -> "ServiceResourceSubnetsCollection":
        """
        Return at most this many Subnets.
        """

    def page_size(self, count: int) -> "ServiceResourceSubnetsCollection":
        """
        Fetch at most this many Subnets per service request.
        """

    def pages(self) -> Iterator[List["Subnet"]]:
        """
        A generator which yields pages of Subnets.
        """

    def __iter__(self) -> Iterator["Subnet"]:
        """
        A generator which yields Subnets.
        """


class ServiceResourceVolumesCollection(ResourceCollection):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.volumes)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#serviceresourcevolumescollection)
    """

    def all(self) -> "ServiceResourceVolumesCollection":
        """
        Get all items from the collection, optionally with a custom page size and item count limit.
        """

    def filter(  # type: ignore
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        VolumeIds: Sequence[str] = ...,
        DryRun: bool = ...,
        MaxResults: int = ...,
        NextToken: str = ...
    ) -> "ServiceResourceVolumesCollection":
        """
        Get items from the collection, passing keyword arguments along as parameters to the underlying service operation, which are typically used to filter the results.
        """

    def limit(self, count: int) -> "ServiceResourceVolumesCollection":
        """
        Return at most this many Volumes.
        """

    def page_size(self, count: int) -> "ServiceResourceVolumesCollection":
        """
        Fetch at most this many Volumes per service request.
        """

    def pages(self) -> Iterator[List["Volume"]]:
        """
        A generator which yields pages of Volumes.
        """

    def __iter__(self) -> Iterator["Volume"]:
        """
        A generator which yields Volumes.
        """


class ServiceResourceVpcAddressesCollection(ResourceCollection):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.vpc_addresses)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#serviceresourcevpcaddressescollection)
    """

    def all(self) -> "ServiceResourceVpcAddressesCollection":
        """
        Get all items from the collection, optionally with a custom page size and item count limit.
        """

    def filter(  # type: ignore
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        PublicIps: Sequence[str] = ...,
        AllocationIds: Sequence[str] = ...,
        DryRun: bool = ...
    ) -> "ServiceResourceVpcAddressesCollection":
        """
        Get items from the collection, passing keyword arguments along as parameters to the underlying service operation, which are typically used to filter the results.
        """

    def limit(self, count: int) -> "ServiceResourceVpcAddressesCollection":
        """
        Return at most this many VpcAddresss.
        """

    def page_size(self, count: int) -> "ServiceResourceVpcAddressesCollection":
        """
        Fetch at most this many VpcAddresss per service request.
        """

    def pages(self) -> Iterator[List["VpcAddress"]]:
        """
        A generator which yields pages of VpcAddresss.
        """

    def __iter__(self) -> Iterator["VpcAddress"]:
        """
        A generator which yields VpcAddresss.
        """


class ServiceResourceVpcPeeringConnectionsCollection(ResourceCollection):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.vpc_peering_connections)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#serviceresourcevpcpeeringconnectionscollection)
    """

    def all(self) -> "ServiceResourceVpcPeeringConnectionsCollection":
        """
        Get all items from the collection, optionally with a custom page size and item count limit.
        """

    def filter(  # type: ignore
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        DryRun: bool = ...,
        VpcPeeringConnectionIds: Sequence[str] = ...,
        NextToken: str = ...,
        MaxResults: int = ...
    ) -> "ServiceResourceVpcPeeringConnectionsCollection":
        """
        Get items from the collection, passing keyword arguments along as parameters to the underlying service operation, which are typically used to filter the results.
        """

    def limit(self, count: int) -> "ServiceResourceVpcPeeringConnectionsCollection":
        """
        Return at most this many VpcPeeringConnections.
        """

    def page_size(self, count: int) -> "ServiceResourceVpcPeeringConnectionsCollection":
        """
        Fetch at most this many VpcPeeringConnections per service request.
        """

    def pages(self) -> Iterator[List["VpcPeeringConnection"]]:
        """
        A generator which yields pages of VpcPeeringConnections.
        """

    def __iter__(self) -> Iterator["VpcPeeringConnection"]:
        """
        A generator which yields VpcPeeringConnections.
        """


class ServiceResourceVpcsCollection(ResourceCollection):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.vpcs)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#serviceresourcevpcscollection)
    """

    def all(self) -> "ServiceResourceVpcsCollection":
        """
        Get all items from the collection, optionally with a custom page size and item count limit.
        """

    def filter(  # type: ignore
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        VpcIds: Sequence[str] = ...,
        DryRun: bool = ...,
        NextToken: str = ...,
        MaxResults: int = ...
    ) -> "ServiceResourceVpcsCollection":
        """
        Get items from the collection, passing keyword arguments along as parameters to the underlying service operation, which are typically used to filter the results.
        """

    def limit(self, count: int) -> "ServiceResourceVpcsCollection":
        """
        Return at most this many Vpcs.
        """

    def page_size(self, count: int) -> "ServiceResourceVpcsCollection":
        """
        Fetch at most this many Vpcs per service request.
        """

    def pages(self) -> Iterator[List["Vpc"]]:
        """
        A generator which yields pages of Vpcs.
        """

    def __iter__(self) -> Iterator["Vpc"]:
        """
        A generator which yields Vpcs.
        """


class InstanceVolumesCollection(ResourceCollection):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Instance.volumes)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#instancevolumescollection)
    """

    def all(self) -> "InstanceVolumesCollection":
        """
        Get all items from the collection, optionally with a custom page size and item count limit.
        """

    def filter(  # type: ignore
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        VolumeIds: Sequence[str] = ...,
        DryRun: bool = ...,
        MaxResults: int = ...,
        NextToken: str = ...
    ) -> "InstanceVolumesCollection":
        """
        Get items from the collection, passing keyword arguments along as parameters to the underlying service operation, which are typically used to filter the results.
        """

    def limit(self, count: int) -> "InstanceVolumesCollection":
        """
        Return at most this many Volumes.
        """

    def page_size(self, count: int) -> "InstanceVolumesCollection":
        """
        Fetch at most this many Volumes per service request.
        """

    def pages(self) -> Iterator[List["Volume"]]:
        """
        A generator which yields pages of Volumes.
        """

    def __iter__(self) -> Iterator["Volume"]:
        """
        A generator which yields Volumes.
        """


class InstanceVpcAddressesCollection(ResourceCollection):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Instance.vpc_addresses)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#instancevpcaddressescollection)
    """

    def all(self) -> "InstanceVpcAddressesCollection":
        """
        Get all items from the collection, optionally with a custom page size and item count limit.
        """

    def filter(  # type: ignore
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        PublicIps: Sequence[str] = ...,
        AllocationIds: Sequence[str] = ...,
        DryRun: bool = ...
    ) -> "InstanceVpcAddressesCollection":
        """
        Get items from the collection, passing keyword arguments along as parameters to the underlying service operation, which are typically used to filter the results.
        """

    def limit(self, count: int) -> "InstanceVpcAddressesCollection":
        """
        Return at most this many VpcAddresss.
        """

    def page_size(self, count: int) -> "InstanceVpcAddressesCollection":
        """
        Fetch at most this many VpcAddresss per service request.
        """

    def pages(self) -> Iterator[List["VpcAddress"]]:
        """
        A generator which yields pages of VpcAddresss.
        """

    def __iter__(self) -> Iterator["VpcAddress"]:
        """
        A generator which yields VpcAddresss.
        """


class PlacementGroupInstancesCollection(ResourceCollection):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.PlacementGroup.instances)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#placementgroupinstancescollection)
    """

    def all(self) -> "PlacementGroupInstancesCollection":
        """
        Get all items from the collection, optionally with a custom page size and item count limit.
        """

    def filter(  # type: ignore
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        InstanceIds: Sequence[str] = ...,
        DryRun: bool = ...,
        MaxResults: int = ...,
        NextToken: str = ...
    ) -> "PlacementGroupInstancesCollection":
        """
        Get items from the collection, passing keyword arguments along as parameters to the underlying service operation, which are typically used to filter the results.
        """

    def create_tags(self, *, DryRun: bool = ...) -> None:
        """
        Batch method.
        """

    def monitor(self, *, DryRun: bool = ...) -> MonitorInstancesResultTypeDef:
        """
        Batch method.
        """

    def reboot(self, *, DryRun: bool = ...) -> None:
        """
        Batch method.
        """

    def start(
        self, *, AdditionalInfo: str = ..., DryRun: bool = ...
    ) -> StartInstancesResultTypeDef:
        """
        Batch method.
        """

    def stop(
        self, *, Hibernate: bool = ..., DryRun: bool = ..., Force: bool = ...
    ) -> StopInstancesResultTypeDef:
        """
        Batch method.
        """

    def terminate(self, *, DryRun: bool = ...) -> TerminateInstancesResultTypeDef:
        """
        Batch method.
        """

    def unmonitor(self, *, DryRun: bool = ...) -> UnmonitorInstancesResultTypeDef:
        """
        Batch method.
        """

    def limit(self, count: int) -> "PlacementGroupInstancesCollection":
        """
        Return at most this many Instances.
        """

    def page_size(self, count: int) -> "PlacementGroupInstancesCollection":
        """
        Fetch at most this many Instances per service request.
        """

    def pages(self) -> Iterator[List["Instance"]]:
        """
        A generator which yields pages of Instances.
        """

    def __iter__(self) -> Iterator["Instance"]:
        """
        A generator which yields Instances.
        """


class SubnetInstancesCollection(ResourceCollection):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Subnet.instances)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#subnetinstancescollection)
    """

    def all(self) -> "SubnetInstancesCollection":
        """
        Get all items from the collection, optionally with a custom page size and item count limit.
        """

    def filter(  # type: ignore
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        InstanceIds: Sequence[str] = ...,
        DryRun: bool = ...,
        MaxResults: int = ...,
        NextToken: str = ...
    ) -> "SubnetInstancesCollection":
        """
        Get items from the collection, passing keyword arguments along as parameters to the underlying service operation, which are typically used to filter the results.
        """

    def create_tags(self, *, DryRun: bool = ...) -> None:
        """
        Batch method.
        """

    def monitor(self, *, DryRun: bool = ...) -> MonitorInstancesResultTypeDef:
        """
        Batch method.
        """

    def reboot(self, *, DryRun: bool = ...) -> None:
        """
        Batch method.
        """

    def start(
        self, *, AdditionalInfo: str = ..., DryRun: bool = ...
    ) -> StartInstancesResultTypeDef:
        """
        Batch method.
        """

    def stop(
        self, *, Hibernate: bool = ..., DryRun: bool = ..., Force: bool = ...
    ) -> StopInstancesResultTypeDef:
        """
        Batch method.
        """

    def terminate(self, *, DryRun: bool = ...) -> TerminateInstancesResultTypeDef:
        """
        Batch method.
        """

    def unmonitor(self, *, DryRun: bool = ...) -> UnmonitorInstancesResultTypeDef:
        """
        Batch method.
        """

    def limit(self, count: int) -> "SubnetInstancesCollection":
        """
        Return at most this many Instances.
        """

    def page_size(self, count: int) -> "SubnetInstancesCollection":
        """
        Fetch at most this many Instances per service request.
        """

    def pages(self) -> Iterator[List["Instance"]]:
        """
        A generator which yields pages of Instances.
        """

    def __iter__(self) -> Iterator["Instance"]:
        """
        A generator which yields Instances.
        """


class SubnetNetworkInterfacesCollection(ResourceCollection):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Subnet.network_interfaces)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#subnetnetworkinterfacescollection)
    """

    def all(self) -> "SubnetNetworkInterfacesCollection":
        """
        Get all items from the collection, optionally with a custom page size and item count limit.
        """

    def filter(  # type: ignore
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        DryRun: bool = ...,
        NetworkInterfaceIds: Sequence[str] = ...,
        NextToken: str = ...,
        MaxResults: int = ...
    ) -> "SubnetNetworkInterfacesCollection":
        """
        Get items from the collection, passing keyword arguments along as parameters to the underlying service operation, which are typically used to filter the results.
        """

    def limit(self, count: int) -> "SubnetNetworkInterfacesCollection":
        """
        Return at most this many NetworkInterfaces.
        """

    def page_size(self, count: int) -> "SubnetNetworkInterfacesCollection":
        """
        Fetch at most this many NetworkInterfaces per service request.
        """

    def pages(self) -> Iterator[List["NetworkInterface"]]:
        """
        A generator which yields pages of NetworkInterfaces.
        """

    def __iter__(self) -> Iterator["NetworkInterface"]:
        """
        A generator which yields NetworkInterfaces.
        """


class VolumeSnapshotsCollection(ResourceCollection):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Volume.snapshots)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#volumesnapshotscollection)
    """

    def all(self) -> "VolumeSnapshotsCollection":
        """
        Get all items from the collection, optionally with a custom page size and item count limit.
        """

    def filter(  # type: ignore
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        MaxResults: int = ...,
        NextToken: str = ...,
        OwnerIds: Sequence[str] = ...,
        RestorableByUserIds: Sequence[str] = ...,
        SnapshotIds: Sequence[str] = ...,
        DryRun: bool = ...
    ) -> "VolumeSnapshotsCollection":
        """
        Get items from the collection, passing keyword arguments along as parameters to the underlying service operation, which are typically used to filter the results.
        """

    def limit(self, count: int) -> "VolumeSnapshotsCollection":
        """
        Return at most this many Snapshots.
        """

    def page_size(self, count: int) -> "VolumeSnapshotsCollection":
        """
        Fetch at most this many Snapshots per service request.
        """

    def pages(self) -> Iterator[List["Snapshot"]]:
        """
        A generator which yields pages of Snapshots.
        """

    def __iter__(self) -> Iterator["Snapshot"]:
        """
        A generator which yields Snapshots.
        """


class VpcAcceptedVpcPeeringConnectionsCollection(ResourceCollection):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Vpc.accepted_vpc_peering_connections)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#vpcacceptedvpcpeeringconnectionscollection)
    """

    def all(self) -> "VpcAcceptedVpcPeeringConnectionsCollection":
        """
        Get all items from the collection, optionally with a custom page size and item count limit.
        """

    def filter(  # type: ignore
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        DryRun: bool = ...,
        VpcPeeringConnectionIds: Sequence[str] = ...,
        NextToken: str = ...,
        MaxResults: int = ...
    ) -> "VpcAcceptedVpcPeeringConnectionsCollection":
        """
        Get items from the collection, passing keyword arguments along as parameters to the underlying service operation, which are typically used to filter the results.
        """

    def limit(self, count: int) -> "VpcAcceptedVpcPeeringConnectionsCollection":
        """
        Return at most this many VpcPeeringConnections.
        """

    def page_size(self, count: int) -> "VpcAcceptedVpcPeeringConnectionsCollection":
        """
        Fetch at most this many VpcPeeringConnections per service request.
        """

    def pages(self) -> Iterator[List["VpcPeeringConnection"]]:
        """
        A generator which yields pages of VpcPeeringConnections.
        """

    def __iter__(self) -> Iterator["VpcPeeringConnection"]:
        """
        A generator which yields VpcPeeringConnections.
        """


class VpcInstancesCollection(ResourceCollection):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Vpc.instances)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#vpcinstancescollection)
    """

    def all(self) -> "VpcInstancesCollection":
        """
        Get all items from the collection, optionally with a custom page size and item count limit.
        """

    def filter(  # type: ignore
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        InstanceIds: Sequence[str] = ...,
        DryRun: bool = ...,
        MaxResults: int = ...,
        NextToken: str = ...
    ) -> "VpcInstancesCollection":
        """
        Get items from the collection, passing keyword arguments along as parameters to the underlying service operation, which are typically used to filter the results.
        """

    def create_tags(self, *, DryRun: bool = ...) -> None:
        """
        Batch method.
        """

    def monitor(self, *, DryRun: bool = ...) -> MonitorInstancesResultTypeDef:
        """
        Batch method.
        """

    def reboot(self, *, DryRun: bool = ...) -> None:
        """
        Batch method.
        """

    def start(
        self, *, AdditionalInfo: str = ..., DryRun: bool = ...
    ) -> StartInstancesResultTypeDef:
        """
        Batch method.
        """

    def stop(
        self, *, Hibernate: bool = ..., DryRun: bool = ..., Force: bool = ...
    ) -> StopInstancesResultTypeDef:
        """
        Batch method.
        """

    def terminate(self, *, DryRun: bool = ...) -> TerminateInstancesResultTypeDef:
        """
        Batch method.
        """

    def unmonitor(self, *, DryRun: bool = ...) -> UnmonitorInstancesResultTypeDef:
        """
        Batch method.
        """

    def limit(self, count: int) -> "VpcInstancesCollection":
        """
        Return at most this many Instances.
        """

    def page_size(self, count: int) -> "VpcInstancesCollection":
        """
        Fetch at most this many Instances per service request.
        """

    def pages(self) -> Iterator[List["Instance"]]:
        """
        A generator which yields pages of Instances.
        """

    def __iter__(self) -> Iterator["Instance"]:
        """
        A generator which yields Instances.
        """


class VpcInternetGatewaysCollection(ResourceCollection):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Vpc.internet_gateways)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#vpcinternetgatewayscollection)
    """

    def all(self) -> "VpcInternetGatewaysCollection":
        """
        Get all items from the collection, optionally with a custom page size and item count limit.
        """

    def filter(  # type: ignore
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        DryRun: bool = ...,
        InternetGatewayIds: Sequence[str] = ...,
        NextToken: str = ...,
        MaxResults: int = ...
    ) -> "VpcInternetGatewaysCollection":
        """
        Get items from the collection, passing keyword arguments along as parameters to the underlying service operation, which are typically used to filter the results.
        """

    def limit(self, count: int) -> "VpcInternetGatewaysCollection":
        """
        Return at most this many InternetGateways.
        """

    def page_size(self, count: int) -> "VpcInternetGatewaysCollection":
        """
        Fetch at most this many InternetGateways per service request.
        """

    def pages(self) -> Iterator[List["InternetGateway"]]:
        """
        A generator which yields pages of InternetGateways.
        """

    def __iter__(self) -> Iterator["InternetGateway"]:
        """
        A generator which yields InternetGateways.
        """


class VpcNetworkAclsCollection(ResourceCollection):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Vpc.network_acls)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#vpcnetworkaclscollection)
    """

    def all(self) -> "VpcNetworkAclsCollection":
        """
        Get all items from the collection, optionally with a custom page size and item count limit.
        """

    def filter(  # type: ignore
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        DryRun: bool = ...,
        NetworkAclIds: Sequence[str] = ...,
        NextToken: str = ...,
        MaxResults: int = ...
    ) -> "VpcNetworkAclsCollection":
        """
        Get items from the collection, passing keyword arguments along as parameters to the underlying service operation, which are typically used to filter the results.
        """

    def limit(self, count: int) -> "VpcNetworkAclsCollection":
        """
        Return at most this many NetworkAcls.
        """

    def page_size(self, count: int) -> "VpcNetworkAclsCollection":
        """
        Fetch at most this many NetworkAcls per service request.
        """

    def pages(self) -> Iterator[List["NetworkAcl"]]:
        """
        A generator which yields pages of NetworkAcls.
        """

    def __iter__(self) -> Iterator["NetworkAcl"]:
        """
        A generator which yields NetworkAcls.
        """


class VpcNetworkInterfacesCollection(ResourceCollection):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Vpc.network_interfaces)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#vpcnetworkinterfacescollection)
    """

    def all(self) -> "VpcNetworkInterfacesCollection":
        """
        Get all items from the collection, optionally with a custom page size and item count limit.
        """

    def filter(  # type: ignore
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        DryRun: bool = ...,
        NetworkInterfaceIds: Sequence[str] = ...,
        NextToken: str = ...,
        MaxResults: int = ...
    ) -> "VpcNetworkInterfacesCollection":
        """
        Get items from the collection, passing keyword arguments along as parameters to the underlying service operation, which are typically used to filter the results.
        """

    def limit(self, count: int) -> "VpcNetworkInterfacesCollection":
        """
        Return at most this many NetworkInterfaces.
        """

    def page_size(self, count: int) -> "VpcNetworkInterfacesCollection":
        """
        Fetch at most this many NetworkInterfaces per service request.
        """

    def pages(self) -> Iterator[List["NetworkInterface"]]:
        """
        A generator which yields pages of NetworkInterfaces.
        """

    def __iter__(self) -> Iterator["NetworkInterface"]:
        """
        A generator which yields NetworkInterfaces.
        """


class VpcRequestedVpcPeeringConnectionsCollection(ResourceCollection):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Vpc.requested_vpc_peering_connections)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#vpcrequestedvpcpeeringconnectionscollection)
    """

    def all(self) -> "VpcRequestedVpcPeeringConnectionsCollection":
        """
        Get all items from the collection, optionally with a custom page size and item count limit.
        """

    def filter(  # type: ignore
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        DryRun: bool = ...,
        VpcPeeringConnectionIds: Sequence[str] = ...,
        NextToken: str = ...,
        MaxResults: int = ...
    ) -> "VpcRequestedVpcPeeringConnectionsCollection":
        """
        Get items from the collection, passing keyword arguments along as parameters to the underlying service operation, which are typically used to filter the results.
        """

    def limit(self, count: int) -> "VpcRequestedVpcPeeringConnectionsCollection":
        """
        Return at most this many VpcPeeringConnections.
        """

    def page_size(self, count: int) -> "VpcRequestedVpcPeeringConnectionsCollection":
        """
        Fetch at most this many VpcPeeringConnections per service request.
        """

    def pages(self) -> Iterator[List["VpcPeeringConnection"]]:
        """
        A generator which yields pages of VpcPeeringConnections.
        """

    def __iter__(self) -> Iterator["VpcPeeringConnection"]:
        """
        A generator which yields VpcPeeringConnections.
        """


class VpcRouteTablesCollection(ResourceCollection):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Vpc.route_tables)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#vpcroutetablescollection)
    """

    def all(self) -> "VpcRouteTablesCollection":
        """
        Get all items from the collection, optionally with a custom page size and item count limit.
        """

    def filter(  # type: ignore
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        DryRun: bool = ...,
        RouteTableIds: Sequence[str] = ...,
        NextToken: str = ...,
        MaxResults: int = ...
    ) -> "VpcRouteTablesCollection":
        """
        Get items from the collection, passing keyword arguments along as parameters to the underlying service operation, which are typically used to filter the results.
        """

    def limit(self, count: int) -> "VpcRouteTablesCollection":
        """
        Return at most this many RouteTables.
        """

    def page_size(self, count: int) -> "VpcRouteTablesCollection":
        """
        Fetch at most this many RouteTables per service request.
        """

    def pages(self) -> Iterator[List["RouteTable"]]:
        """
        A generator which yields pages of RouteTables.
        """

    def __iter__(self) -> Iterator["RouteTable"]:
        """
        A generator which yields RouteTables.
        """


class VpcSecurityGroupsCollection(ResourceCollection):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Vpc.security_groups)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#vpcsecuritygroupscollection)
    """

    def all(self) -> "VpcSecurityGroupsCollection":
        """
        Get all items from the collection, optionally with a custom page size and item count limit.
        """

    def filter(  # type: ignore
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        GroupIds: Sequence[str] = ...,
        GroupNames: Sequence[str] = ...,
        DryRun: bool = ...,
        NextToken: str = ...,
        MaxResults: int = ...
    ) -> "VpcSecurityGroupsCollection":
        """
        Get items from the collection, passing keyword arguments along as parameters to the underlying service operation, which are typically used to filter the results.
        """

    def limit(self, count: int) -> "VpcSecurityGroupsCollection":
        """
        Return at most this many SecurityGroups.
        """

    def page_size(self, count: int) -> "VpcSecurityGroupsCollection":
        """
        Fetch at most this many SecurityGroups per service request.
        """

    def pages(self) -> Iterator[List["SecurityGroup"]]:
        """
        A generator which yields pages of SecurityGroups.
        """

    def __iter__(self) -> Iterator["SecurityGroup"]:
        """
        A generator which yields SecurityGroups.
        """


class VpcSubnetsCollection(ResourceCollection):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Vpc.subnets)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#vpcsubnetscollection)
    """

    def all(self) -> "VpcSubnetsCollection":
        """
        Get all items from the collection, optionally with a custom page size and item count limit.
        """

    def filter(  # type: ignore
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        SubnetIds: Sequence[str] = ...,
        DryRun: bool = ...,
        NextToken: str = ...,
        MaxResults: int = ...
    ) -> "VpcSubnetsCollection":
        """
        Get items from the collection, passing keyword arguments along as parameters to the underlying service operation, which are typically used to filter the results.
        """

    def limit(self, count: int) -> "VpcSubnetsCollection":
        """
        Return at most this many Subnets.
        """

    def page_size(self, count: int) -> "VpcSubnetsCollection":
        """
        Fetch at most this many Subnets per service request.
        """

    def pages(self) -> Iterator[List["Subnet"]]:
        """
        A generator which yields pages of Subnets.
        """

    def __iter__(self) -> Iterator["Subnet"]:
        """
        A generator which yields Subnets.
        """


class ClassicAddress(Boto3ServiceResource):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.ClassicAddress)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#classicaddress)
    """

    instance_id: str
    allocation_id: str
    association_id: str
    domain: str
    network_interface_id: str
    network_interface_owner_id: str
    private_ip_address: str
    tags: List[Any]
    public_ipv4_pool: str
    network_border_group: str
    customer_owned_ip: str
    customer_owned_ipv4_pool: str
    carrier_ip: str
    public_ip: str

    def associate(
        self,
        *,
        AllocationId: str = ...,
        InstanceId: str = ...,
        AllowReassociation: bool = ...,
        DryRun: bool = ...,
        NetworkInterfaceId: str = ...,
        PrivateIpAddress: str = ...
    ) -> AssociateAddressResultTypeDef:
        """
        Associates an Elastic IP address, or carrier IP address (for instances that are
        in subnets in Wavelength Zones) with an instance or a network interface.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ClassicAddress.associate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#classicaddressassociate-method)
        """

    def disassociate(
        self, *, AssociationId: str = ..., PublicIp: str = ..., DryRun: bool = ...
    ) -> None:
        """
        Disassociates an Elastic IP address from the instance or network interface it's
        associated with.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ClassicAddress.disassociate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#classicaddressdisassociate-method)
        """

    def get_available_subresources(self) -> Sequence[str]:
        """
        Returns a list of all the available sub-resources for this Resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ClassicAddress.get_available_subresources)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#classicaddressget_available_subresources-method)
        """

    def load(self) -> None:
        """
        Calls :py:meth:`EC2.Client.describe_addresses` to update the attributes of the
        ClassicAddress resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ClassicAddress.load)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#classicaddressload-method)
        """

    def release(
        self,
        *,
        AllocationId: str = ...,
        PublicIp: str = ...,
        NetworkBorderGroup: str = ...,
        DryRun: bool = ...
    ) -> None:
        """
        Releases the specified Elastic IP address.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ClassicAddress.release)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#classicaddressrelease-method)
        """

    def reload(self) -> None:
        """
        Calls :py:meth:`EC2.Client.describe_addresses` to update the attributes of the
        ClassicAddress resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ClassicAddress.reload)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#classicaddressreload-method)
        """


_ClassicAddress = ClassicAddress


class KeyPair(Boto3ServiceResource):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.KeyPair)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#keypair)
    """

    key_fingerprint: str
    key_material: str
    key_name: str
    key_pair_id: str
    tags: List[Any]
    name: str

    def delete(self, *, KeyPairId: str = ..., DryRun: bool = ...) -> None:
        """
        Deletes the specified key pair, by removing the public key from Amazon EC2.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.KeyPair.delete)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#keypairdelete-method)
        """

    def get_available_subresources(self) -> Sequence[str]:
        """
        Returns a list of all the available sub-resources for this Resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.KeyPair.get_available_subresources)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#keypairget_available_subresources-method)
        """


_KeyPair = KeyPair


class KeyPairInfo(Boto3ServiceResource):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.KeyPairInfo)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#keypairinfo)
    """

    key_pair_id: str
    key_fingerprint: str
    key_name: str
    key_type: str
    tags: List[Any]
    name: str

    def delete(self, *, KeyPairId: str = ..., DryRun: bool = ...) -> None:
        """
        Deletes the specified key pair, by removing the public key from Amazon EC2.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.KeyPairInfo.delete)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#keypairinfodelete-method)
        """

    def get_available_subresources(self) -> Sequence[str]:
        """
        Returns a list of all the available sub-resources for this Resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.KeyPairInfo.get_available_subresources)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#keypairinfoget_available_subresources-method)
        """

    def load(self) -> None:
        """
        Calls :py:meth:`EC2.Client.describe_key_pairs` to update the attributes of the
        KeyPairInfo resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.KeyPairInfo.load)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#keypairinfoload-method)
        """

    def reload(self) -> None:
        """
        Calls :py:meth:`EC2.Client.describe_key_pairs` to update the attributes of the
        KeyPairInfo resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.KeyPairInfo.reload)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#keypairinforeload-method)
        """


_KeyPairInfo = KeyPairInfo


class NetworkInterfaceAssociation(Boto3ServiceResource):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.NetworkInterfaceAssociation)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#networkinterfaceassociation)
    """

    carrier_ip: str
    customer_owned_ip: str
    ip_owner_id: str
    public_dns_name: str
    public_ip: str
    id: str
    address: "VpcAddress"

    def delete(self, *, PublicIp: str = ..., DryRun: bool = ...) -> None:
        """
        Disassociates an Elastic IP address from the instance or network interface it's
        associated with.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.NetworkInterfaceAssociation.delete)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#networkinterfaceassociationdelete-method)
        """

    def get_available_subresources(self) -> Sequence[str]:
        """
        Returns a list of all the available sub-resources for this Resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.NetworkInterfaceAssociation.get_available_subresources)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#networkinterfaceassociationget_available_subresources-method)
        """

    def load(self) -> None:
        """
        Calls :py:meth:`EC2.Client.describe_network_interfaces` to update the attributes
        of the NetworkInterfaceAssociation resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.NetworkInterfaceAssociation.load)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#networkinterfaceassociationload-method)
        """

    def reload(self) -> None:
        """
        Calls :py:meth:`EC2.Client.describe_network_interfaces` to update the attributes
        of the NetworkInterfaceAssociation resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.NetworkInterfaceAssociation.reload)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#networkinterfaceassociationreload-method)
        """


_NetworkInterfaceAssociation = NetworkInterfaceAssociation


class PlacementGroup(Boto3ServiceResource):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.PlacementGroup)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#placementgroup)
    """

    group_name: str
    state: str
    strategy: str
    partition_count: int
    group_id: str
    tags: List[Any]
    group_arn: str
    name: str
    instances: PlacementGroupInstancesCollection

    def delete(self, *, DryRun: bool = ...) -> None:
        """
        Deletes the specified placement group.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.PlacementGroup.delete)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#placementgroupdelete-method)
        """

    def get_available_subresources(self) -> Sequence[str]:
        """
        Returns a list of all the available sub-resources for this Resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.PlacementGroup.get_available_subresources)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#placementgroupget_available_subresources-method)
        """

    def load(self) -> None:
        """
        Calls :py:meth:`EC2.Client.describe_placement_groups` to update the attributes
        of the PlacementGroup resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.PlacementGroup.load)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#placementgroupload-method)
        """

    def reload(self) -> None:
        """
        Calls :py:meth:`EC2.Client.describe_placement_groups` to update the attributes
        of the PlacementGroup resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.PlacementGroup.reload)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#placementgroupreload-method)
        """


_PlacementGroup = PlacementGroup


class Tag(Boto3ServiceResource):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.Tag)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#tag)
    """

    resource_type: str
    resource_id: str
    key: str
    value: str

    def delete(self, *, DryRun: bool = ...) -> None:
        """
        Deletes the specified set of tags from the specified set of resources.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Tag.delete)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#tagdelete-method)
        """

    def get_available_subresources(self) -> Sequence[str]:
        """
        Returns a list of all the available sub-resources for this Resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Tag.get_available_subresources)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#tagget_available_subresources-method)
        """

    def load(self) -> None:
        """
        Calls :py:meth:`EC2.Client.describe_tags` to update the attributes of the Tag
        resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Tag.load)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#tagload-method)
        """

    def reload(self) -> None:
        """
        Calls :py:meth:`EC2.Client.describe_tags` to update the attributes of the Tag
        resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Tag.reload)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#tagreload-method)
        """


_Tag = Tag


class VpcPeeringConnection(Boto3ServiceResource):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.VpcPeeringConnection)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#vpcpeeringconnection)
    """

    accepter_vpc_info: Dict[str, Any]
    expiration_time: datetime
    requester_vpc_info: Dict[str, Any]
    status: Dict[str, Any]
    tags: List[Any]
    vpc_peering_connection_id: str
    id: str
    accepter_vpc: "Vpc"
    requester_vpc: "Vpc"

    def accept(self, *, DryRun: bool = ...) -> AcceptVpcPeeringConnectionResultTypeDef:
        """
        Accept a VPC peering connection request.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.VpcPeeringConnection.accept)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#vpcpeeringconnectionaccept-method)
        """

    def delete(self, *, DryRun: bool = ...) -> DeleteVpcPeeringConnectionResultTypeDef:
        """
        Deletes a VPC peering connection.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.VpcPeeringConnection.delete)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#vpcpeeringconnectiondelete-method)
        """

    def get_available_subresources(self) -> Sequence[str]:
        """
        Returns a list of all the available sub-resources for this Resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.VpcPeeringConnection.get_available_subresources)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#vpcpeeringconnectionget_available_subresources-method)
        """

    def load(self) -> None:
        """
        Calls :py:meth:`EC2.Client.describe_vpc_peering_connections` to update the
        attributes of the VpcPeeringConnection resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.VpcPeeringConnection.load)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#vpcpeeringconnectionload-method)
        """

    def reject(self, *, DryRun: bool = ...) -> RejectVpcPeeringConnectionResultTypeDef:
        """
        Rejects a VPC peering connection request.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.VpcPeeringConnection.reject)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#vpcpeeringconnectionreject-method)
        """

    def reload(self) -> None:
        """
        Calls :py:meth:`EC2.Client.describe_vpc_peering_connections` to update the
        attributes of the VpcPeeringConnection resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.VpcPeeringConnection.reload)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#vpcpeeringconnectionreload-method)
        """

    def wait_until_exists(self) -> None:
        """
        Waits until this VpcPeeringConnection is exists.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.VpcPeeringConnection.wait_until_exists)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#vpcpeeringconnectionwait_until_exists-method)
        """


_VpcPeeringConnection = VpcPeeringConnection


class VpcAddress(Boto3ServiceResource):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.VpcAddress)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#vpcaddress)
    """

    instance_id: str
    public_ip: str
    association_id: str
    domain: str
    network_interface_id: str
    network_interface_owner_id: str
    private_ip_address: str
    tags: List[Any]
    public_ipv4_pool: str
    network_border_group: str
    customer_owned_ip: str
    customer_owned_ipv4_pool: str
    carrier_ip: str
    allocation_id: str
    association: "NetworkInterfaceAssociation"

    def associate(
        self,
        *,
        InstanceId: str = ...,
        PublicIp: str = ...,
        AllowReassociation: bool = ...,
        DryRun: bool = ...,
        NetworkInterfaceId: str = ...,
        PrivateIpAddress: str = ...
    ) -> AssociateAddressResultTypeDef:
        """
        Associates an Elastic IP address, or carrier IP address (for instances that are
        in subnets in Wavelength Zones) with an instance or a network interface.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.VpcAddress.associate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#vpcaddressassociate-method)
        """

    def get_available_subresources(self) -> Sequence[str]:
        """
        Returns a list of all the available sub-resources for this Resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.VpcAddress.get_available_subresources)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#vpcaddressget_available_subresources-method)
        """

    def load(self) -> None:
        """
        Calls :py:meth:`EC2.Client.describe_addresses` to update the attributes of the
        VpcAddress resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.VpcAddress.load)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#vpcaddressload-method)
        """

    def release(
        self,
        *,
        AllocationId: str = ...,
        PublicIp: str = ...,
        NetworkBorderGroup: str = ...,
        DryRun: bool = ...
    ) -> None:
        """
        Releases the specified Elastic IP address.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.VpcAddress.release)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#vpcaddressrelease-method)
        """

    def reload(self) -> None:
        """
        Calls :py:meth:`EC2.Client.describe_addresses` to update the attributes of the
        VpcAddress resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.VpcAddress.reload)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#vpcaddressreload-method)
        """


_VpcAddress = VpcAddress


class DhcpOptions(Boto3ServiceResource):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.DhcpOptions)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#dhcpoptions)
    """

    dhcp_configurations: List[Any]
    dhcp_options_id: str
    owner_id: str
    tags: List[Any]
    id: str

    def associate_with_vpc(self, *, VpcId: str, DryRun: bool = ...) -> None:
        """
        Associates a set of DHCP options (that you've previously created) with the
        specified VPC, or associates no DHCP options with the VPC.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.DhcpOptions.associate_with_vpc)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#dhcpoptionsassociate_with_vpc-method)
        """

    def create_tags(self, *, Tags: Optional[Sequence["TagTypeDef"]], DryRun: bool = ...) -> _Tag:
        """
        Adds or overwrites only the specified tags for the specified Amazon EC2 resource
        or resources.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.DhcpOptions.create_tags)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#dhcpoptionscreate_tags-method)
        """

    def delete(self, *, DryRun: bool = ...) -> None:
        """
        Deletes the specified set of DHCP options.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.DhcpOptions.delete)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#dhcpoptionsdelete-method)
        """

    def get_available_subresources(self) -> Sequence[str]:
        """
        Returns a list of all the available sub-resources for this Resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.DhcpOptions.get_available_subresources)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#dhcpoptionsget_available_subresources-method)
        """

    def load(self) -> None:
        """
        Calls :py:meth:`EC2.Client.describe_dhcp_options` to update the attributes of
        the DhcpOptions resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.DhcpOptions.load)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#dhcpoptionsload-method)
        """

    def reload(self) -> None:
        """
        Calls :py:meth:`EC2.Client.describe_dhcp_options` to update the attributes of
        the DhcpOptions resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.DhcpOptions.reload)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#dhcpoptionsreload-method)
        """


_DhcpOptions = DhcpOptions


class Image(Boto3ServiceResource):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.Image)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#image)
    """

    architecture: str
    creation_date: str
    image_id: str
    image_location: str
    image_type: str
    public: bool
    kernel_id: str
    owner_id: str
    platform: str
    platform_details: str
    usage_operation: str
    product_codes: List[Any]
    ramdisk_id: str
    state: str
    block_device_mappings: List[Any]
    description: str
    ena_support: bool
    hypervisor: str
    image_owner_alias: str
    name: str
    root_device_name: str
    root_device_type: str
    sriov_net_support: str
    state_reason: Dict[str, Any]
    tags: List[Any]
    virtualization_type: str
    boot_mode: str
    deprecation_time: str
    id: str

    def create_tags(self, *, Tags: Optional[Sequence["TagTypeDef"]], DryRun: bool = ...) -> _Tag:
        """
        Adds or overwrites only the specified tags for the specified Amazon EC2 resource
        or resources.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Image.create_tags)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#imagecreate_tags-method)
        """

    def deregister(self, *, DryRun: bool = ...) -> None:
        """
        Deregisters the specified AMI.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Image.deregister)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#imagederegister-method)
        """

    def describe_attribute(
        self, *, Attribute: ImageAttributeNameType, DryRun: bool = ...
    ) -> ImageAttributeTypeDef:
        """
        Describes the specified attribute of the specified AMI.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Image.describe_attribute)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#imagedescribe_attribute-method)
        """

    def get_available_subresources(self) -> Sequence[str]:
        """
        Returns a list of all the available sub-resources for this Resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Image.get_available_subresources)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#imageget_available_subresources-method)
        """

    def load(self) -> None:
        """
        Calls :py:meth:`EC2.Client.describe_images` to update the attributes of the
        Image resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Image.load)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#imageload-method)
        """

    def modify_attribute(
        self,
        *,
        Attribute: str = ...,
        Description: "AttributeValueTypeDef" = ...,
        LaunchPermission: "LaunchPermissionModificationsTypeDef" = ...,
        OperationType: OperationTypeType = ...,
        ProductCodes: Sequence[str] = ...,
        UserGroups: Sequence[str] = ...,
        UserIds: Sequence[str] = ...,
        Value: str = ...,
        DryRun: bool = ...,
        OrganizationArns: Sequence[str] = ...,
        OrganizationalUnitArns: Sequence[str] = ...
    ) -> None:
        """
        Modifies the specified attribute of the specified AMI.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Image.modify_attribute)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#imagemodify_attribute-method)
        """

    def reload(self) -> None:
        """
        Calls :py:meth:`EC2.Client.describe_images` to update the attributes of the
        Image resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Image.reload)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#imagereload-method)
        """

    def reset_attribute(
        self, *, Attribute: Literal["launchPermission"], DryRun: bool = ...
    ) -> None:
        """
        Resets an attribute of an AMI to its default value.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Image.reset_attribute)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#imagereset_attribute-method)
        """

    def wait_until_exists(self) -> None:
        """
        Waits until this Image is exists.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Image.wait_until_exists)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#imagewait_until_exists-method)
        """


_Image = Image


class InternetGateway(Boto3ServiceResource):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.InternetGateway)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#internetgateway)
    """

    attachments: List[Any]
    internet_gateway_id: str
    owner_id: str
    tags: List[Any]
    id: str

    def attach_to_vpc(self, *, VpcId: str, DryRun: bool = ...) -> None:
        """
        Attaches an internet gateway or a virtual private gateway to a VPC, enabling
        connectivity between the internet and the VPC.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.InternetGateway.attach_to_vpc)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#internetgatewayattach_to_vpc-method)
        """

    def create_tags(self, *, Tags: Optional[Sequence["TagTypeDef"]], DryRun: bool = ...) -> _Tag:
        """
        Adds or overwrites only the specified tags for the specified Amazon EC2 resource
        or resources.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.InternetGateway.create_tags)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#internetgatewaycreate_tags-method)
        """

    def delete(self, *, DryRun: bool = ...) -> None:
        """
        Deletes the specified internet gateway.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.InternetGateway.delete)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#internetgatewaydelete-method)
        """

    def detach_from_vpc(self, *, VpcId: str, DryRun: bool = ...) -> None:
        """
        Detaches an internet gateway from a VPC, disabling connectivity between the
        internet and the VPC.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.InternetGateway.detach_from_vpc)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#internetgatewaydetach_from_vpc-method)
        """

    def get_available_subresources(self) -> Sequence[str]:
        """
        Returns a list of all the available sub-resources for this Resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.InternetGateway.get_available_subresources)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#internetgatewayget_available_subresources-method)
        """

    def load(self) -> None:
        """
        Calls :py:meth:`EC2.Client.describe_internet_gateways` to update the attributes
        of the InternetGateway resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.InternetGateway.load)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#internetgatewayload-method)
        """

    def reload(self) -> None:
        """
        Calls :py:meth:`EC2.Client.describe_internet_gateways` to update the attributes
        of the InternetGateway resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.InternetGateway.reload)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#internetgatewayreload-method)
        """


_InternetGateway = InternetGateway


class NetworkAcl(Boto3ServiceResource):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.NetworkAcl)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#networkacl)
    """

    associations: List[Any]
    entries: List[Any]
    is_default: bool
    network_acl_id: str
    tags: List[Any]
    vpc_id: str
    owner_id: str
    id: str
    vpc: "Vpc"

    def create_entry(
        self,
        *,
        Egress: bool,
        Protocol: str,
        RuleAction: RuleActionType,
        RuleNumber: int,
        CidrBlock: str = ...,
        DryRun: bool = ...,
        IcmpTypeCode: "IcmpTypeCodeTypeDef" = ...,
        Ipv6CidrBlock: str = ...,
        PortRange: "PortRangeTypeDef" = ...
    ) -> None:
        """
        Creates an entry (a rule) in a network ACL with the specified rule number.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.NetworkAcl.create_entry)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#networkaclcreate_entry-method)
        """

    def create_tags(self, *, Tags: Optional[Sequence["TagTypeDef"]], DryRun: bool = ...) -> _Tag:
        """
        Adds or overwrites only the specified tags for the specified Amazon EC2 resource
        or resources.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.NetworkAcl.create_tags)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#networkaclcreate_tags-method)
        """

    def delete(self, *, DryRun: bool = ...) -> None:
        """
        Deletes the specified network ACL.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.NetworkAcl.delete)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#networkacldelete-method)
        """

    def delete_entry(self, *, Egress: bool, RuleNumber: int, DryRun: bool = ...) -> None:
        """
        Deletes the specified ingress or egress entry (rule) from the specified network
        ACL.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.NetworkAcl.delete_entry)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#networkacldelete_entry-method)
        """

    def get_available_subresources(self) -> Sequence[str]:
        """
        Returns a list of all the available sub-resources for this Resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.NetworkAcl.get_available_subresources)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#networkaclget_available_subresources-method)
        """

    def load(self) -> None:
        """
        Calls :py:meth:`EC2.Client.describe_network_acls` to update the attributes of
        the NetworkAcl resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.NetworkAcl.load)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#networkaclload-method)
        """

    def reload(self) -> None:
        """
        Calls :py:meth:`EC2.Client.describe_network_acls` to update the attributes of
        the NetworkAcl resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.NetworkAcl.reload)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#networkaclreload-method)
        """

    def replace_association(
        self, *, AssociationId: str, DryRun: bool = ...
    ) -> ReplaceNetworkAclAssociationResultTypeDef:
        """
        Changes which network ACL a subnet is associated with.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.NetworkAcl.replace_association)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#networkaclreplace_association-method)
        """

    def replace_entry(
        self,
        *,
        Egress: bool,
        Protocol: str,
        RuleAction: RuleActionType,
        RuleNumber: int,
        CidrBlock: str = ...,
        DryRun: bool = ...,
        IcmpTypeCode: "IcmpTypeCodeTypeDef" = ...,
        Ipv6CidrBlock: str = ...,
        PortRange: "PortRangeTypeDef" = ...
    ) -> None:
        """
        Replaces an entry (rule) in a network ACL.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.NetworkAcl.replace_entry)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#networkaclreplace_entry-method)
        """


_NetworkAcl = NetworkAcl


class NetworkInterface(Boto3ServiceResource):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.NetworkInterface)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#networkinterface)
    """

    association_attribute: Dict[str, Any]
    attachment: Dict[str, Any]
    availability_zone: str
    description: str
    groups: List[Any]
    interface_type: str
    ipv6_addresses: List[Any]
    mac_address: str
    network_interface_id: str
    outpost_arn: str
    owner_id: str
    private_dns_name: str
    private_ip_address: str
    private_ip_addresses: List[Any]
    ipv4_prefixes: List[Any]
    ipv6_prefixes: List[Any]
    requester_id: str
    requester_managed: bool
    source_dest_check: bool
    status: str
    subnet_id: str
    tag_set: List[Any]
    vpc_id: str
    deny_all_igw_traffic: bool
    ipv6_native: bool
    ipv6_address: str
    id: str
    association: "NetworkInterfaceAssociation"
    subnet: "Subnet"
    vpc: "Vpc"

    def assign_private_ip_addresses(
        self,
        *,
        AllowReassignment: bool = ...,
        PrivateIpAddresses: Sequence[str] = ...,
        SecondaryPrivateIpAddressCount: int = ...,
        Ipv4Prefixes: Sequence[str] = ...,
        Ipv4PrefixCount: int = ...
    ) -> AssignPrivateIpAddressesResultTypeDef:
        """
        Assigns one or more secondary private IP addresses to the specified network
        interface.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.NetworkInterface.assign_private_ip_addresses)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#networkinterfaceassign_private_ip_addresses-method)
        """

    def attach(
        self, *, DeviceIndex: int, InstanceId: str, DryRun: bool = ..., NetworkCardIndex: int = ...
    ) -> AttachNetworkInterfaceResultTypeDef:
        """
        Attaches a network interface to an instance.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.NetworkInterface.attach)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#networkinterfaceattach-method)
        """

    def create_tags(self, *, Tags: Optional[Sequence["TagTypeDef"]], DryRun: bool = ...) -> _Tag:
        """
        Adds or overwrites only the specified tags for the specified Amazon EC2 resource
        or resources.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.NetworkInterface.create_tags)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#networkinterfacecreate_tags-method)
        """

    def delete(self, *, DryRun: bool = ...) -> None:
        """
        Deletes the specified network interface.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.NetworkInterface.delete)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#networkinterfacedelete-method)
        """

    def describe_attribute(
        self, *, Attribute: NetworkInterfaceAttributeType = ..., DryRun: bool = ...
    ) -> DescribeNetworkInterfaceAttributeResultTypeDef:
        """
        Describes a network interface attribute.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.NetworkInterface.describe_attribute)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#networkinterfacedescribe_attribute-method)
        """

    def detach(self, *, AttachmentId: str, DryRun: bool = ..., Force: bool = ...) -> None:
        """
        Detaches a network interface from an instance.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.NetworkInterface.detach)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#networkinterfacedetach-method)
        """

    def get_available_subresources(self) -> Sequence[str]:
        """
        Returns a list of all the available sub-resources for this Resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.NetworkInterface.get_available_subresources)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#networkinterfaceget_available_subresources-method)
        """

    def load(self) -> None:
        """
        Calls :py:meth:`EC2.Client.describe_network_interfaces` to update the attributes
        of the NetworkInterface resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.NetworkInterface.load)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#networkinterfaceload-method)
        """

    def modify_attribute(
        self,
        *,
        Attachment: "NetworkInterfaceAttachmentChangesTypeDef" = ...,
        Description: "AttributeValueTypeDef" = ...,
        DryRun: bool = ...,
        Groups: Sequence[str] = ...,
        SourceDestCheck: "AttributeBooleanValueTypeDef" = ...
    ) -> None:
        """
        Modifies the specified network interface attribute.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.NetworkInterface.modify_attribute)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#networkinterfacemodify_attribute-method)
        """

    def reload(self) -> None:
        """
        Calls :py:meth:`EC2.Client.describe_network_interfaces` to update the attributes
        of the NetworkInterface resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.NetworkInterface.reload)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#networkinterfacereload-method)
        """

    def reset_attribute(self, *, DryRun: bool = ..., SourceDestCheck: str = ...) -> None:
        """
        Resets a network interface attribute.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.NetworkInterface.reset_attribute)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#networkinterfacereset_attribute-method)
        """

    def unassign_private_ip_addresses(
        self, *, PrivateIpAddresses: Sequence[str] = ..., Ipv4Prefixes: Sequence[str] = ...
    ) -> None:
        """
        Unassigns one or more secondary private IP addresses, or IPv4 Prefix Delegation
        prefixes from a network interface.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.NetworkInterface.unassign_private_ip_addresses)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#networkinterfaceunassign_private_ip_addresses-method)
        """


_NetworkInterface = NetworkInterface


class Route(Boto3ServiceResource):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.Route)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#route)
    """

    destination_ipv6_cidr_block: str
    destination_prefix_list_id: str
    egress_only_internet_gateway_id: str
    gateway_id: str
    instance_id: str
    instance_owner_id: str
    nat_gateway_id: str
    transit_gateway_id: str
    local_gateway_id: str
    carrier_gateway_id: str
    network_interface_id: str
    origin: str
    state: str
    vpc_peering_connection_id: str
    core_network_arn: str
    route_table_id: str
    destination_cidr_block: str

    def RouteTable(self) -> "_RouteTable":
        """
        Creates a RouteTable resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Route.RouteTable)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#routeroutetable-method)
        """

    def delete(
        self,
        *,
        DestinationIpv6CidrBlock: str = ...,
        DestinationPrefixListId: str = ...,
        DryRun: bool = ...
    ) -> None:
        """
        Deletes the specified route from the specified route table.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Route.delete)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#routedelete-method)
        """

    def get_available_subresources(self) -> Sequence[str]:
        """
        Returns a list of all the available sub-resources for this Resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Route.get_available_subresources)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#routeget_available_subresources-method)
        """

    def replace(
        self,
        *,
        DestinationIpv6CidrBlock: str = ...,
        DestinationPrefixListId: str = ...,
        DryRun: bool = ...,
        VpcEndpointId: str = ...,
        EgressOnlyInternetGatewayId: str = ...,
        GatewayId: str = ...,
        InstanceId: str = ...,
        LocalTarget: bool = ...,
        NatGatewayId: str = ...,
        TransitGatewayId: str = ...,
        LocalGatewayId: str = ...,
        CarrierGatewayId: str = ...,
        NetworkInterfaceId: str = ...,
        VpcPeeringConnectionId: str = ...,
        CoreNetworkArn: str = ...
    ) -> None:
        """
        Replaces an existing route within a route table in a VPC.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Route.replace)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#routereplace-method)
        """


_Route = Route


class RouteTableAssociation(Boto3ServiceResource):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.RouteTableAssociation)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#routetableassociation)
    """

    main: bool
    route_table_association_id: str
    route_table_id: str
    subnet_id: str
    gateway_id: str
    association_state: Dict[str, Any]
    id: str
    route_table: "RouteTable"
    subnet: "Subnet"

    def delete(self, *, DryRun: bool = ...) -> None:
        """
        Disassociates a subnet or gateway from a route table.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.RouteTableAssociation.delete)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#routetableassociationdelete-method)
        """

    def get_available_subresources(self) -> Sequence[str]:
        """
        Returns a list of all the available sub-resources for this Resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.RouteTableAssociation.get_available_subresources)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#routetableassociationget_available_subresources-method)
        """

    def replace_subnet(self, *, RouteTableId: str, DryRun: bool = ...) -> "_RouteTableAssociation":
        """
        Changes the route table associated with a given subnet, internet gateway, or
        virtual private gateway in a VPC.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.RouteTableAssociation.replace_subnet)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#routetableassociationreplace_subnet-method)
        """


_RouteTableAssociation = RouteTableAssociation


class SecurityGroup(Boto3ServiceResource):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.SecurityGroup)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#securitygroup)
    """

    description: str
    group_name: str
    ip_permissions: List[Any]
    owner_id: str
    group_id: str
    ip_permissions_egress: List[Any]
    tags: List[Any]
    vpc_id: str
    id: str

    def authorize_egress(
        self,
        *,
        DryRun: bool = ...,
        IpPermissions: Sequence["IpPermissionTypeDef"] = ...,
        TagSpecifications: Sequence["TagSpecificationTypeDef"] = ...,
        CidrIp: str = ...,
        FromPort: int = ...,
        IpProtocol: str = ...,
        ToPort: int = ...,
        SourceSecurityGroupName: str = ...,
        SourceSecurityGroupOwnerId: str = ...
    ) -> AuthorizeSecurityGroupEgressResultTypeDef:
        """
        [VPC only] Adds the specified outbound (egress) rules to a security group for
        use with a VPC.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.SecurityGroup.authorize_egress)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#securitygroupauthorize_egress-method)
        """

    def authorize_ingress(
        self,
        *,
        CidrIp: str = ...,
        FromPort: int = ...,
        GroupName: str = ...,
        IpPermissions: Sequence["IpPermissionTypeDef"] = ...,
        IpProtocol: str = ...,
        SourceSecurityGroupName: str = ...,
        SourceSecurityGroupOwnerId: str = ...,
        ToPort: int = ...,
        DryRun: bool = ...,
        TagSpecifications: Sequence["TagSpecificationTypeDef"] = ...
    ) -> AuthorizeSecurityGroupIngressResultTypeDef:
        """
        Adds the specified inbound (ingress) rules to a security group.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.SecurityGroup.authorize_ingress)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#securitygroupauthorize_ingress-method)
        """

    def create_tags(self, *, Tags: Optional[Sequence["TagTypeDef"]], DryRun: bool = ...) -> _Tag:
        """
        Adds or overwrites only the specified tags for the specified Amazon EC2 resource
        or resources.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.SecurityGroup.create_tags)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#securitygroupcreate_tags-method)
        """

    def delete(self, *, GroupName: str = ..., DryRun: bool = ...) -> None:
        """
        Deletes a security group.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.SecurityGroup.delete)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#securitygroupdelete-method)
        """

    def get_available_subresources(self) -> Sequence[str]:
        """
        Returns a list of all the available sub-resources for this Resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.SecurityGroup.get_available_subresources)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#securitygroupget_available_subresources-method)
        """

    def load(self) -> None:
        """
        Calls :py:meth:`EC2.Client.describe_security_groups` to update the attributes of
        the SecurityGroup resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.SecurityGroup.load)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#securitygroupload-method)
        """

    def reload(self) -> None:
        """
        Calls :py:meth:`EC2.Client.describe_security_groups` to update the attributes of
        the SecurityGroup resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.SecurityGroup.reload)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#securitygroupreload-method)
        """

    def revoke_egress(
        self,
        *,
        DryRun: bool = ...,
        IpPermissions: Sequence["IpPermissionTypeDef"] = ...,
        SecurityGroupRuleIds: Sequence[str] = ...,
        CidrIp: str = ...,
        FromPort: int = ...,
        IpProtocol: str = ...,
        ToPort: int = ...,
        SourceSecurityGroupName: str = ...,
        SourceSecurityGroupOwnerId: str = ...
    ) -> RevokeSecurityGroupEgressResultTypeDef:
        """
        [VPC only] Removes the specified outbound (egress) rules from a security group
        for EC2-VPC.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.SecurityGroup.revoke_egress)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#securitygrouprevoke_egress-method)
        """

    def revoke_ingress(
        self,
        *,
        CidrIp: str = ...,
        FromPort: int = ...,
        GroupName: str = ...,
        IpPermissions: Sequence["IpPermissionTypeDef"] = ...,
        IpProtocol: str = ...,
        SourceSecurityGroupName: str = ...,
        SourceSecurityGroupOwnerId: str = ...,
        ToPort: int = ...,
        DryRun: bool = ...,
        SecurityGroupRuleIds: Sequence[str] = ...
    ) -> RevokeSecurityGroupIngressResultTypeDef:
        """
        Removes the specified inbound (ingress) rules from a security group.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.SecurityGroup.revoke_ingress)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#securitygrouprevoke_ingress-method)
        """


_SecurityGroup = SecurityGroup


class Snapshot(Boto3ServiceResource):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.Snapshot)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#snapshot)
    """

    data_encryption_key_id: str
    description: str
    encrypted: bool
    kms_key_id: str
    owner_id: str
    progress: str
    snapshot_id: str
    start_time: datetime
    state: str
    state_message: str
    volume_id: str
    volume_size: int
    owner_alias: str
    outpost_arn: str
    tags: List[Any]
    storage_tier: str
    restore_expiry_time: datetime
    id: str
    volume: "Volume"

    def copy(
        self,
        *,
        SourceRegion: str,
        Description: str = ...,
        DestinationOutpostArn: str = ...,
        DestinationRegion: str = ...,
        Encrypted: bool = ...,
        KmsKeyId: str = ...,
        PresignedUrl: str = ...,
        TagSpecifications: Sequence["TagSpecificationTypeDef"] = ...,
        DryRun: bool = ...
    ) -> CopySnapshotResultTypeDef:
        """
        Copies a point-in-time snapshot of an EBS volume and stores it in Amazon S3.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Snapshot.copy)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#snapshotcopy-method)
        """

    def create_tags(self, *, Tags: Optional[Sequence["TagTypeDef"]], DryRun: bool = ...) -> _Tag:
        """
        Adds or overwrites only the specified tags for the specified Amazon EC2 resource
        or resources.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Snapshot.create_tags)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#snapshotcreate_tags-method)
        """

    def delete(self, *, DryRun: bool = ...) -> None:
        """
        Deletes the specified snapshot.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Snapshot.delete)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#snapshotdelete-method)
        """

    def describe_attribute(
        self, *, Attribute: SnapshotAttributeNameType, DryRun: bool = ...
    ) -> DescribeSnapshotAttributeResultTypeDef:
        """
        Describes the specified attribute of the specified snapshot.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Snapshot.describe_attribute)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#snapshotdescribe_attribute-method)
        """

    def get_available_subresources(self) -> Sequence[str]:
        """
        Returns a list of all the available sub-resources for this Resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Snapshot.get_available_subresources)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#snapshotget_available_subresources-method)
        """

    def load(self) -> None:
        """
        Calls :py:meth:`EC2.Client.describe_snapshots` to update the attributes of the
        Snapshot resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Snapshot.load)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#snapshotload-method)
        """

    def modify_attribute(
        self,
        *,
        Attribute: SnapshotAttributeNameType = ...,
        CreateVolumePermission: "CreateVolumePermissionModificationsTypeDef" = ...,
        GroupNames: Sequence[str] = ...,
        OperationType: OperationTypeType = ...,
        UserIds: Sequence[str] = ...,
        DryRun: bool = ...
    ) -> None:
        """
        Adds or removes permission settings for the specified snapshot.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Snapshot.modify_attribute)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#snapshotmodify_attribute-method)
        """

    def reload(self) -> None:
        """
        Calls :py:meth:`EC2.Client.describe_snapshots` to update the attributes of the
        Snapshot resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Snapshot.reload)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#snapshotreload-method)
        """

    def reset_attribute(self, *, Attribute: SnapshotAttributeNameType, DryRun: bool = ...) -> None:
        """
        Resets permission settings for the specified snapshot.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Snapshot.reset_attribute)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#snapshotreset_attribute-method)
        """

    def wait_until_completed(self) -> None:
        """
        Waits until this Snapshot is completed.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Snapshot.wait_until_completed)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#snapshotwait_until_completed-method)
        """


_Snapshot = Snapshot


class Instance(Boto3ServiceResource):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.Instance)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#instance)
    """

    ami_launch_index: int
    image_id: str
    instance_id: str
    instance_type: str
    kernel_id: str
    key_name: str
    launch_time: datetime
    monitoring: Dict[str, Any]
    placement: Dict[str, Any]
    platform: str
    private_dns_name: str
    private_ip_address: str
    product_codes: List[Any]
    public_dns_name: str
    public_ip_address: str
    ramdisk_id: str
    state: Dict[str, Any]
    state_transition_reason: str
    subnet_id: str
    vpc_id: str
    architecture: str
    block_device_mappings: List[Any]
    client_token: str
    ebs_optimized: bool
    ena_support: bool
    hypervisor: str
    iam_instance_profile: Dict[str, Any]
    instance_lifecycle: str
    elastic_gpu_associations: List[Any]
    elastic_inference_accelerator_associations: List[Any]
    network_interfaces_attribute: List[Any]
    outpost_arn: str
    root_device_name: str
    root_device_type: str
    security_groups: List[Any]
    source_dest_check: bool
    spot_instance_request_id: str
    sriov_net_support: str
    state_reason: Dict[str, Any]
    tags: List[Any]
    virtualization_type: str
    cpu_options: Dict[str, Any]
    capacity_reservation_id: str
    capacity_reservation_specification: Dict[str, Any]
    hibernation_options: Dict[str, Any]
    licenses: List[Any]
    metadata_options: Dict[str, Any]
    enclave_options: Dict[str, Any]
    boot_mode: str
    platform_details: str
    usage_operation: str
    usage_operation_update_time: datetime
    private_dns_name_options: Dict[str, Any]
    ipv6_address: str
    id: str
    classic_address: "ClassicAddress"
    image: "Image"
    key_pair: "KeyPairInfo"
    network_interfaces: "NetworkInterface"
    placement_group: "PlacementGroup"
    subnet: "Subnet"
    vpc: "Vpc"
    volumes: InstanceVolumesCollection
    vpc_addresses: InstanceVpcAddressesCollection

    def attach_classic_link_vpc(
        self, *, Groups: Sequence[str], VpcId: str, DryRun: bool = ...
    ) -> AttachClassicLinkVpcResultTypeDef:
        """
        Links an EC2-Classic instance to a ClassicLink-enabled VPC through one or more
        of the VPC's security groups.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Instance.attach_classic_link_vpc)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#instanceattach_classic_link_vpc-method)
        """

    def attach_volume(
        self, *, Device: str, VolumeId: str, DryRun: bool = ...
    ) -> VolumeAttachmentResponseMetadataTypeDef:
        """
        Attaches an EBS volume to a running or stopped instance and exposes it to the
        instance with the specified device name.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Instance.attach_volume)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#instanceattach_volume-method)
        """

    def console_output(
        self, *, DryRun: bool = ..., Latest: bool = ...
    ) -> GetConsoleOutputResultTypeDef:
        """
        Gets the console output for the specified instance.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Instance.console_output)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#instanceconsole_output-method)
        """

    def create_image(
        self,
        *,
        Name: str,
        BlockDeviceMappings: Sequence["BlockDeviceMappingTypeDef"] = ...,
        Description: str = ...,
        DryRun: bool = ...,
        NoReboot: bool = ...,
        TagSpecifications: Sequence["TagSpecificationTypeDef"] = ...
    ) -> _Image:
        """
        Creates an Amazon EBS-backed AMI from an Amazon EBS-backed instance that is
        either running or stopped.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Instance.create_image)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#instancecreate_image-method)
        """

    def create_tags(self, *, Tags: Optional[Sequence["TagTypeDef"]], DryRun: bool = ...) -> _Tag:
        """
        Adds or overwrites only the specified tags for the specified Amazon EC2 resource
        or resources.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Instance.create_tags)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#instancecreate_tags-method)
        """

    def delete_tags(self, Tags: Sequence["TagTypeDef"] = ..., DryRun: bool = ...) -> None:
        """
        Deletes the specified set of tags from the specified set of resources.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Instance.delete_tags)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#instancedelete_tags-method)
        """

    def describe_attribute(
        self, *, Attribute: InstanceAttributeNameType, DryRun: bool = ...
    ) -> InstanceAttributeTypeDef:
        """
        Describes the specified attribute of the specified instance.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Instance.describe_attribute)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#instancedescribe_attribute-method)
        """

    def detach_classic_link_vpc(
        self, *, VpcId: str, DryRun: bool = ...
    ) -> DetachClassicLinkVpcResultTypeDef:
        """
        Unlinks (detaches) a linked EC2-Classic instance from a VPC.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Instance.detach_classic_link_vpc)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#instancedetach_classic_link_vpc-method)
        """

    def detach_volume(
        self, *, VolumeId: str, Device: str = ..., Force: bool = ..., DryRun: bool = ...
    ) -> VolumeAttachmentResponseMetadataTypeDef:
        """
        Detaches an EBS volume from an instance.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Instance.detach_volume)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#instancedetach_volume-method)
        """

    def get_available_subresources(self) -> Sequence[str]:
        """
        Returns a list of all the available sub-resources for this Resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Instance.get_available_subresources)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#instanceget_available_subresources-method)
        """

    def load(self) -> None:
        """
        Calls :py:meth:`EC2.Client.describe_instances` to update the attributes of the
        Instance resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Instance.load)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#instanceload-method)
        """

    def modify_attribute(
        self,
        *,
        SourceDestCheck: "AttributeBooleanValueTypeDef" = ...,
        Attribute: InstanceAttributeNameType = ...,
        BlockDeviceMappings: Sequence["InstanceBlockDeviceMappingSpecificationTypeDef"] = ...,
        DisableApiTermination: "AttributeBooleanValueTypeDef" = ...,
        DryRun: bool = ...,
        EbsOptimized: "AttributeBooleanValueTypeDef" = ...,
        EnaSupport: "AttributeBooleanValueTypeDef" = ...,
        Groups: Sequence[str] = ...,
        InstanceInitiatedShutdownBehavior: "AttributeValueTypeDef" = ...,
        InstanceType: "AttributeValueTypeDef" = ...,
        Kernel: "AttributeValueTypeDef" = ...,
        Ramdisk: "AttributeValueTypeDef" = ...,
        SriovNetSupport: "AttributeValueTypeDef" = ...,
        UserData: "BlobAttributeValueTypeDef" = ...,
        Value: str = ...
    ) -> None:
        """
        Modifies the specified attribute of the specified instance.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Instance.modify_attribute)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#instancemodify_attribute-method)
        """

    def monitor(self, *, DryRun: bool = ...) -> MonitorInstancesResultTypeDef:
        """
        Enables detailed monitoring for a running instance.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Instance.monitor)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#instancemonitor-method)
        """

    def password_data(self, *, DryRun: bool = ...) -> GetPasswordDataResultTypeDef:
        """
        Retrieves the encrypted administrator password for a running Windows instance.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Instance.password_data)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#instancepassword_data-method)
        """

    def reboot(self, *, DryRun: bool = ...) -> None:
        """
        Requests a reboot of the specified instances.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Instance.reboot)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#instancereboot-method)
        """

    def reload(self) -> None:
        """
        Calls :py:meth:`EC2.Client.describe_instances` to update the attributes of the
        Instance resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Instance.reload)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#instancereload-method)
        """

    def report_status(
        self,
        *,
        ReasonCodes: Sequence[ReportInstanceReasonCodesType],
        Status: ReportStatusTypeType,
        Description: str = ...,
        DryRun: bool = ...,
        EndTime: Union[datetime, str] = ...,
        StartTime: Union[datetime, str] = ...
    ) -> None:
        """
        Submits feedback about the status of an instance.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Instance.report_status)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#instancereport_status-method)
        """

    def reset_attribute(self, *, Attribute: InstanceAttributeNameType, DryRun: bool = ...) -> None:
        """
        Resets an attribute of an instance to its default value.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Instance.reset_attribute)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#instancereset_attribute-method)
        """

    def reset_kernel(self, *, Attribute: InstanceAttributeNameType, DryRun: bool = ...) -> None:
        """
        Resets an attribute of an instance to its default value.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Instance.reset_kernel)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#instancereset_kernel-method)
        """

    def reset_ramdisk(self, *, Attribute: InstanceAttributeNameType, DryRun: bool = ...) -> None:
        """
        Resets an attribute of an instance to its default value.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Instance.reset_ramdisk)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#instancereset_ramdisk-method)
        """

    def reset_source_dest_check(
        self, *, Attribute: InstanceAttributeNameType, DryRun: bool = ...
    ) -> None:
        """
        Resets an attribute of an instance to its default value.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Instance.reset_source_dest_check)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#instancereset_source_dest_check-method)
        """

    def start(
        self, *, AdditionalInfo: str = ..., DryRun: bool = ...
    ) -> StartInstancesResultTypeDef:
        """
        Starts an Amazon EBS-backed instance that you've previously stopped.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Instance.start)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#instancestart-method)
        """

    def stop(
        self, *, Hibernate: bool = ..., DryRun: bool = ..., Force: bool = ...
    ) -> StopInstancesResultTypeDef:
        """
        Stops an Amazon EBS-backed instance.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Instance.stop)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#instancestop-method)
        """

    def terminate(self, *, DryRun: bool = ...) -> TerminateInstancesResultTypeDef:
        """
        Shuts down the specified instances.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Instance.terminate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#instanceterminate-method)
        """

    def unmonitor(self, *, DryRun: bool = ...) -> UnmonitorInstancesResultTypeDef:
        """
        Disables detailed monitoring for a running instance.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Instance.unmonitor)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#instanceunmonitor-method)
        """

    def wait_until_exists(self) -> None:
        """
        Waits until this Instance is exists.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Instance.wait_until_exists)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#instancewait_until_exists-method)
        """

    def wait_until_running(self) -> None:
        """
        Waits until this Instance is running.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Instance.wait_until_running)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#instancewait_until_running-method)
        """

    def wait_until_stopped(self) -> None:
        """
        Waits until this Instance is stopped.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Instance.wait_until_stopped)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#instancewait_until_stopped-method)
        """

    def wait_until_terminated(self) -> None:
        """
        Waits until this Instance is terminated.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Instance.wait_until_terminated)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#instancewait_until_terminated-method)
        """


_Instance = Instance


class Volume(Boto3ServiceResource):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.Volume)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#volume)
    """

    attachments: List[Any]
    availability_zone: str
    create_time: datetime
    encrypted: bool
    kms_key_id: str
    outpost_arn: str
    size: int
    snapshot_id: str
    state: str
    volume_id: str
    iops: int
    tags: List[Any]
    volume_type: str
    fast_restored: bool
    multi_attach_enabled: bool
    throughput: int
    id: str
    snapshots: VolumeSnapshotsCollection

    def attach_to_instance(
        self, *, Device: str, InstanceId: str, DryRun: bool = ...
    ) -> VolumeAttachmentResponseMetadataTypeDef:
        """
        Attaches an EBS volume to a running or stopped instance and exposes it to the
        instance with the specified device name.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Volume.attach_to_instance)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#volumeattach_to_instance-method)
        """

    def create_snapshot(
        self,
        *,
        Description: str = ...,
        OutpostArn: str = ...,
        TagSpecifications: Sequence["TagSpecificationTypeDef"] = ...,
        DryRun: bool = ...
    ) -> _Snapshot:
        """
        Creates a snapshot of an EBS volume and stores it in Amazon S3.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Volume.create_snapshot)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#volumecreate_snapshot-method)
        """

    def create_tags(self, *, Tags: Optional[Sequence["TagTypeDef"]], DryRun: bool = ...) -> _Tag:
        """
        Adds or overwrites only the specified tags for the specified Amazon EC2 resource
        or resources.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Volume.create_tags)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#volumecreate_tags-method)
        """

    def delete(self, *, DryRun: bool = ...) -> None:
        """
        Deletes the specified EBS volume.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Volume.delete)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#volumedelete-method)
        """

    def describe_attribute(
        self, *, Attribute: VolumeAttributeNameType, DryRun: bool = ...
    ) -> DescribeVolumeAttributeResultTypeDef:
        """
        Describes the specified attribute of the specified volume.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Volume.describe_attribute)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#volumedescribe_attribute-method)
        """

    def describe_status(
        self,
        *,
        Filters: Sequence["FilterTypeDef"] = ...,
        MaxResults: int = ...,
        NextToken: str = ...,
        DryRun: bool = ...
    ) -> DescribeVolumeStatusResultTypeDef:
        """
        Describes the status of the specified volumes.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Volume.describe_status)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#volumedescribe_status-method)
        """

    def detach_from_instance(
        self, *, Device: str = ..., Force: bool = ..., InstanceId: str = ..., DryRun: bool = ...
    ) -> VolumeAttachmentResponseMetadataTypeDef:
        """
        Detaches an EBS volume from an instance.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Volume.detach_from_instance)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#volumedetach_from_instance-method)
        """

    def enable_io(self, *, DryRun: bool = ...) -> None:
        """
        Enables I/O operations for a volume that had I/O operations disabled because the
        data on the volume was potentially inconsistent.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Volume.enable_io)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#volumeenable_io-method)
        """

    def get_available_subresources(self) -> Sequence[str]:
        """
        Returns a list of all the available sub-resources for this Resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Volume.get_available_subresources)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#volumeget_available_subresources-method)
        """

    def load(self) -> None:
        """
        Calls :py:meth:`EC2.Client.describe_volumes` to update the attributes of the
        Volume resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Volume.load)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#volumeload-method)
        """

    def modify_attribute(
        self, *, AutoEnableIO: "AttributeBooleanValueTypeDef" = ..., DryRun: bool = ...
    ) -> None:
        """
        Modifies a volume attribute.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Volume.modify_attribute)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#volumemodify_attribute-method)
        """

    def reload(self) -> None:
        """
        Calls :py:meth:`EC2.Client.describe_volumes` to update the attributes of the
        Volume resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Volume.reload)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#volumereload-method)
        """


_Volume = Volume


class RouteTable(Boto3ServiceResource):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.RouteTable)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#routetable)
    """

    associations_attribute: List[Any]
    propagating_vgws: List[Any]
    route_table_id: str
    routes_attribute: List[Any]
    tags: List[Any]
    vpc_id: str
    owner_id: str
    id: str
    associations: "RouteTableAssociation"
    routes: "Route"
    vpc: "Vpc"

    def associate_with_subnet(
        self, *, DryRun: bool = ..., SubnetId: str = ..., GatewayId: str = ...
    ) -> _RouteTableAssociation:
        """
        Associates a subnet in your VPC or an internet gateway or virtual private
        gateway attached to your VPC with a route table in your VPC.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.RouteTable.associate_with_subnet)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#routetableassociate_with_subnet-method)
        """

    def create_route(
        self,
        *,
        DestinationCidrBlock: str = ...,
        DestinationIpv6CidrBlock: str = ...,
        DestinationPrefixListId: str = ...,
        DryRun: bool = ...,
        VpcEndpointId: str = ...,
        EgressOnlyInternetGatewayId: str = ...,
        GatewayId: str = ...,
        InstanceId: str = ...,
        NatGatewayId: str = ...,
        TransitGatewayId: str = ...,
        LocalGatewayId: str = ...,
        CarrierGatewayId: str = ...,
        NetworkInterfaceId: str = ...,
        VpcPeeringConnectionId: str = ...,
        CoreNetworkArn: str = ...
    ) -> _Route:
        """
        Creates a route in a route table within a VPC.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.RouteTable.create_route)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#routetablecreate_route-method)
        """

    def create_tags(self, *, Tags: Optional[Sequence["TagTypeDef"]], DryRun: bool = ...) -> _Tag:
        """
        Adds or overwrites only the specified tags for the specified Amazon EC2 resource
        or resources.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.RouteTable.create_tags)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#routetablecreate_tags-method)
        """

    def delete(self, *, DryRun: bool = ...) -> None:
        """
        Deletes the specified route table.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.RouteTable.delete)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#routetabledelete-method)
        """

    def get_available_subresources(self) -> Sequence[str]:
        """
        Returns a list of all the available sub-resources for this Resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.RouteTable.get_available_subresources)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#routetableget_available_subresources-method)
        """

    def load(self) -> None:
        """
        Calls :py:meth:`EC2.Client.describe_route_tables` to update the attributes of
        the RouteTable resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.RouteTable.load)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#routetableload-method)
        """

    def reload(self) -> None:
        """
        Calls :py:meth:`EC2.Client.describe_route_tables` to update the attributes of
        the RouteTable resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.RouteTable.reload)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#routetablereload-method)
        """


_RouteTable = RouteTable


class Subnet(Boto3ServiceResource):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.Subnet)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#subnet)
    """

    availability_zone: str
    availability_zone_id: str
    available_ip_address_count: int
    cidr_block: str
    default_for_az: bool
    enable_lni_at_device_index: int
    map_public_ip_on_launch: bool
    map_customer_owned_ip_on_launch: bool
    customer_owned_ipv4_pool: str
    state: str
    subnet_id: str
    vpc_id: str
    owner_id: str
    assign_ipv6_address_on_creation: bool
    ipv6_cidr_block_association_set: List[Any]
    tags: List[Any]
    subnet_arn: str
    outpost_arn: str
    enable_dns64: bool
    ipv6_native: bool
    private_dns_name_options_on_launch: Dict[str, Any]
    id: str
    vpc: "Vpc"
    instances: SubnetInstancesCollection
    network_interfaces: SubnetNetworkInterfacesCollection

    def create_instances(
        self,
        *,
        MaxCount: int,
        MinCount: int,
        BlockDeviceMappings: Sequence["BlockDeviceMappingTypeDef"] = ...,
        ImageId: str = ...,
        InstanceType: InstanceTypeType = ...,
        Ipv6AddressCount: int = ...,
        Ipv6Addresses: Sequence["InstanceIpv6AddressTypeDef"] = ...,
        KernelId: str = ...,
        KeyName: str = ...,
        Monitoring: "RunInstancesMonitoringEnabledTypeDef" = ...,
        Placement: "PlacementTypeDef" = ...,
        RamdiskId: str = ...,
        SecurityGroupIds: Sequence[str] = ...,
        SecurityGroups: Sequence[str] = ...,
        UserData: str = ...,
        AdditionalInfo: str = ...,
        ClientToken: str = ...,
        DisableApiTermination: bool = ...,
        DryRun: bool = ...,
        EbsOptimized: bool = ...,
        IamInstanceProfile: "IamInstanceProfileSpecificationTypeDef" = ...,
        InstanceInitiatedShutdownBehavior: ShutdownBehaviorType = ...,
        NetworkInterfaces: Sequence["InstanceNetworkInterfaceSpecificationTypeDef"] = ...,
        PrivateIpAddress: str = ...,
        ElasticGpuSpecification: Sequence["ElasticGpuSpecificationTypeDef"] = ...,
        ElasticInferenceAccelerators: Sequence["ElasticInferenceAcceleratorTypeDef"] = ...,
        TagSpecifications: Sequence["TagSpecificationTypeDef"] = ...,
        LaunchTemplate: "LaunchTemplateSpecificationTypeDef" = ...,
        InstanceMarketOptions: "InstanceMarketOptionsRequestTypeDef" = ...,
        CreditSpecification: "CreditSpecificationRequestTypeDef" = ...,
        CpuOptions: "CpuOptionsRequestTypeDef" = ...,
        CapacityReservationSpecification: "CapacityReservationSpecificationTypeDef" = ...,
        HibernationOptions: "HibernationOptionsRequestTypeDef" = ...,
        LicenseSpecifications: Sequence["LicenseConfigurationRequestTypeDef"] = ...,
        MetadataOptions: "InstanceMetadataOptionsRequestTypeDef" = ...,
        EnclaveOptions: "EnclaveOptionsRequestTypeDef" = ...,
        PrivateDnsNameOptions: "PrivateDnsNameOptionsRequestTypeDef" = ...
    ) -> List[_Instance]:
        """
        Launches the specified number of instances using an AMI for which you have
        permissions.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Subnet.create_instances)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#subnetcreate_instances-method)
        """

    def create_network_interface(
        self,
        *,
        Description: str = ...,
        DryRun: bool = ...,
        Groups: Sequence[str] = ...,
        Ipv6AddressCount: int = ...,
        Ipv6Addresses: Sequence["InstanceIpv6AddressTypeDef"] = ...,
        PrivateIpAddress: str = ...,
        PrivateIpAddresses: Sequence["PrivateIpAddressSpecificationTypeDef"] = ...,
        SecondaryPrivateIpAddressCount: int = ...,
        Ipv4Prefixes: Sequence["Ipv4PrefixSpecificationRequestTypeDef"] = ...,
        Ipv4PrefixCount: int = ...,
        Ipv6Prefixes: Sequence["Ipv6PrefixSpecificationRequestTypeDef"] = ...,
        Ipv6PrefixCount: int = ...,
        InterfaceType: NetworkInterfaceCreationTypeType = ...,
        TagSpecifications: Sequence["TagSpecificationTypeDef"] = ...,
        ClientToken: str = ...
    ) -> _NetworkInterface:
        """
        Creates a network interface in the specified subnet.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Subnet.create_network_interface)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#subnetcreate_network_interface-method)
        """

    def create_tags(self, *, Tags: Optional[Sequence["TagTypeDef"]], DryRun: bool = ...) -> _Tag:
        """
        Adds or overwrites only the specified tags for the specified Amazon EC2 resource
        or resources.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Subnet.create_tags)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#subnetcreate_tags-method)
        """

    def delete(self, *, DryRun: bool = ...) -> None:
        """
        Deletes the specified subnet.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Subnet.delete)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#subnetdelete-method)
        """

    def get_available_subresources(self) -> Sequence[str]:
        """
        Returns a list of all the available sub-resources for this Resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Subnet.get_available_subresources)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#subnetget_available_subresources-method)
        """

    def load(self) -> None:
        """
        Calls :py:meth:`EC2.Client.describe_subnets` to update the attributes of the
        Subnet resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Subnet.load)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#subnetload-method)
        """

    def reload(self) -> None:
        """
        Calls :py:meth:`EC2.Client.describe_subnets` to update the attributes of the
        Subnet resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Subnet.reload)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#subnetreload-method)
        """


_Subnet = Subnet


class Vpc(Boto3ServiceResource):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.Vpc)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#vpc)
    """

    cidr_block: str
    dhcp_options_id: str
    state: str
    vpc_id: str
    owner_id: str
    instance_tenancy: str
    ipv6_cidr_block_association_set: List[Any]
    cidr_block_association_set: List[Any]
    is_default: bool
    tags: List[Any]
    id: str
    dhcp_options: "DhcpOptions"
    accepted_vpc_peering_connections: VpcAcceptedVpcPeeringConnectionsCollection
    instances: VpcInstancesCollection
    internet_gateways: VpcInternetGatewaysCollection
    network_acls: VpcNetworkAclsCollection
    network_interfaces: VpcNetworkInterfacesCollection
    requested_vpc_peering_connections: VpcRequestedVpcPeeringConnectionsCollection
    route_tables: VpcRouteTablesCollection
    security_groups: VpcSecurityGroupsCollection
    subnets: VpcSubnetsCollection

    def associate_dhcp_options(self, *, DhcpOptionsId: str, DryRun: bool = ...) -> None:
        """
        Associates a set of DHCP options (that you've previously created) with the
        specified VPC, or associates no DHCP options with the VPC.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Vpc.associate_dhcp_options)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#vpcassociate_dhcp_options-method)
        """

    def attach_classic_link_instance(
        self, *, Groups: Sequence[str], InstanceId: str, DryRun: bool = ...
    ) -> AttachClassicLinkVpcResultTypeDef:
        """
        Links an EC2-Classic instance to a ClassicLink-enabled VPC through one or more
        of the VPC's security groups.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Vpc.attach_classic_link_instance)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#vpcattach_classic_link_instance-method)
        """

    def attach_internet_gateway(self, *, InternetGatewayId: str, DryRun: bool = ...) -> None:
        """
        Attaches an internet gateway or a virtual private gateway to a VPC, enabling
        connectivity between the internet and the VPC.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Vpc.attach_internet_gateway)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#vpcattach_internet_gateway-method)
        """

    def create_network_acl(
        self, *, DryRun: bool = ..., TagSpecifications: Sequence["TagSpecificationTypeDef"] = ...
    ) -> _NetworkAcl:
        """
        Creates a network ACL in a VPC.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Vpc.create_network_acl)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#vpccreate_network_acl-method)
        """

    def create_route_table(
        self, *, DryRun: bool = ..., TagSpecifications: Sequence["TagSpecificationTypeDef"] = ...
    ) -> _RouteTable:
        """
        Creates a route table for the specified VPC.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Vpc.create_route_table)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#vpccreate_route_table-method)
        """

    def create_security_group(
        self,
        *,
        Description: str,
        GroupName: str,
        TagSpecifications: Sequence["TagSpecificationTypeDef"] = ...,
        DryRun: bool = ...
    ) -> _SecurityGroup:
        """
        Creates a security group.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Vpc.create_security_group)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#vpccreate_security_group-method)
        """

    def create_subnet(
        self,
        *,
        TagSpecifications: Sequence["TagSpecificationTypeDef"] = ...,
        AvailabilityZone: str = ...,
        AvailabilityZoneId: str = ...,
        CidrBlock: str = ...,
        Ipv6CidrBlock: str = ...,
        OutpostArn: str = ...,
        DryRun: bool = ...,
        Ipv6Native: bool = ...
    ) -> _Subnet:
        """
        Creates a subnet in a specified VPC.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Vpc.create_subnet)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#vpccreate_subnet-method)
        """

    def create_tags(self, *, Tags: Optional[Sequence["TagTypeDef"]], DryRun: bool = ...) -> _Tag:
        """
        Adds or overwrites only the specified tags for the specified Amazon EC2 resource
        or resources.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Vpc.create_tags)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#vpccreate_tags-method)
        """

    def delete(self, *, DryRun: bool = ...) -> None:
        """
        Deletes the specified VPC.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Vpc.delete)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#vpcdelete-method)
        """

    def describe_attribute(
        self, *, Attribute: VpcAttributeNameType, DryRun: bool = ...
    ) -> DescribeVpcAttributeResultTypeDef:
        """
        Describes the specified attribute of the specified VPC.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Vpc.describe_attribute)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#vpcdescribe_attribute-method)
        """

    def detach_classic_link_instance(
        self, *, InstanceId: str, DryRun: bool = ...
    ) -> DetachClassicLinkVpcResultTypeDef:
        """
        Unlinks (detaches) a linked EC2-Classic instance from a VPC.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Vpc.detach_classic_link_instance)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#vpcdetach_classic_link_instance-method)
        """

    def detach_internet_gateway(self, *, InternetGatewayId: str, DryRun: bool = ...) -> None:
        """
        Detaches an internet gateway from a VPC, disabling connectivity between the
        internet and the VPC.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Vpc.detach_internet_gateway)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#vpcdetach_internet_gateway-method)
        """

    def disable_classic_link(self, *, DryRun: bool = ...) -> DisableVpcClassicLinkResultTypeDef:
        """
        Disables ClassicLink for a VPC.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Vpc.disable_classic_link)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#vpcdisable_classic_link-method)
        """

    def enable_classic_link(self, *, DryRun: bool = ...) -> EnableVpcClassicLinkResultTypeDef:
        """
        Enables a VPC for ClassicLink.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Vpc.enable_classic_link)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#vpcenable_classic_link-method)
        """

    def get_available_subresources(self) -> Sequence[str]:
        """
        Returns a list of all the available sub-resources for this Resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Vpc.get_available_subresources)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#vpcget_available_subresources-method)
        """

    def load(self) -> None:
        """
        Calls :py:meth:`EC2.Client.describe_vpcs` to update the attributes of the Vpc
        resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Vpc.load)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#vpcload-method)
        """

    def modify_attribute(
        self,
        *,
        EnableDnsHostnames: "AttributeBooleanValueTypeDef" = ...,
        EnableDnsSupport: "AttributeBooleanValueTypeDef" = ...
    ) -> None:
        """
        Modifies the specified attribute of the specified VPC.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Vpc.modify_attribute)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#vpcmodify_attribute-method)
        """

    def reload(self) -> None:
        """
        Calls :py:meth:`EC2.Client.describe_vpcs` to update the attributes of the Vpc
        resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Vpc.reload)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#vpcreload-method)
        """

    def request_vpc_peering_connection(
        self,
        *,
        DryRun: bool = ...,
        PeerOwnerId: str = ...,
        PeerVpcId: str = ...,
        PeerRegion: str = ...,
        TagSpecifications: Sequence["TagSpecificationTypeDef"] = ...
    ) -> _VpcPeeringConnection:
        """
        Requests a VPC peering connection between two VPCs: a requester VPC that you own
        and an accepter VPC with which to create the connection.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Vpc.request_vpc_peering_connection)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#vpcrequest_vpc_peering_connection-method)
        """

    def wait_until_available(self) -> None:
        """
        Waits until this Vpc is available.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Vpc.wait_until_available)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#vpcwait_until_available-method)
        """

    def wait_until_exists(self) -> None:
        """
        Waits until this Vpc is exists.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.Vpc.wait_until_exists)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#vpcwait_until_exists-method)
        """


_Vpc = Vpc


class EC2ResourceMeta(ResourceMeta):
    client: EC2Client


class EC2ServiceResource(Boto3ServiceResource):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html)
    """

    meta: "EC2ResourceMeta"
    classic_addresses: ServiceResourceClassicAddressesCollection
    dhcp_options_sets: ServiceResourceDhcpOptionsSetsCollection
    images: ServiceResourceImagesCollection
    instances: ServiceResourceInstancesCollection
    internet_gateways: ServiceResourceInternetGatewaysCollection
    key_pairs: ServiceResourceKeyPairsCollection
    network_acls: ServiceResourceNetworkAclsCollection
    network_interfaces: ServiceResourceNetworkInterfacesCollection
    placement_groups: ServiceResourcePlacementGroupsCollection
    route_tables: ServiceResourceRouteTablesCollection
    security_groups: ServiceResourceSecurityGroupsCollection
    snapshots: ServiceResourceSnapshotsCollection
    subnets: ServiceResourceSubnetsCollection
    volumes: ServiceResourceVolumesCollection
    vpc_addresses: ServiceResourceVpcAddressesCollection
    vpc_peering_connections: ServiceResourceVpcPeeringConnectionsCollection
    vpcs: ServiceResourceVpcsCollection

    def ClassicAddress(self, public_ip: str) -> _ClassicAddress:
        """
        Creates a ClassicAddress resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.ClassicAddress)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#ec2serviceresourceclassicaddress-method)
        """

    def DhcpOptions(self, id: str) -> _DhcpOptions:
        """
        Creates a DhcpOptions resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.DhcpOptions)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#ec2serviceresourcedhcpoptions-method)
        """

    def Image(self, id: str) -> _Image:
        """
        Creates a Image resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.Image)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#ec2serviceresourceimage-method)
        """

    def Instance(self, id: str) -> _Instance:
        """
        Creates a Instance resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.Instance)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#ec2serviceresourceinstance-method)
        """

    def InternetGateway(self, id: str) -> _InternetGateway:
        """
        Creates a InternetGateway resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.InternetGateway)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#ec2serviceresourceinternetgateway-method)
        """

    def KeyPair(self, name: str) -> _KeyPairInfo:
        """
        Creates a KeyPairInfo resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.KeyPair)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#ec2serviceresourcekeypair-method)
        """

    def NetworkAcl(self, id: str) -> _NetworkAcl:
        """
        Creates a NetworkAcl resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.NetworkAcl)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#ec2serviceresourcenetworkacl-method)
        """

    def NetworkInterface(self, id: str) -> _NetworkInterface:
        """
        Creates a NetworkInterface resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.NetworkInterface)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#ec2serviceresourcenetworkinterface-method)
        """

    def NetworkInterfaceAssociation(self, id: str) -> _NetworkInterfaceAssociation:
        """
        Creates a NetworkInterfaceAssociation resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.NetworkInterfaceAssociation)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#ec2serviceresourcenetworkinterfaceassociation-method)
        """

    def PlacementGroup(self, name: str) -> _PlacementGroup:
        """
        Creates a PlacementGroup resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.PlacementGroup)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#ec2serviceresourceplacementgroup-method)
        """

    def Route(self, route_table_id: str, destination_cidr_block: str) -> _Route:
        """
        Creates a Route resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.Route)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#ec2serviceresourceroute-method)
        """

    def RouteTable(self, id: str) -> _RouteTable:
        """
        Creates a RouteTable resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.RouteTable)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#ec2serviceresourceroutetable-method)
        """

    def RouteTableAssociation(self, id: str) -> _RouteTableAssociation:
        """
        Creates a RouteTableAssociation resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.RouteTableAssociation)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#ec2serviceresourceroutetableassociation-method)
        """

    def SecurityGroup(self, id: str) -> _SecurityGroup:
        """
        Creates a SecurityGroup resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.SecurityGroup)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#ec2serviceresourcesecuritygroup-method)
        """

    def Snapshot(self, id: str) -> _Snapshot:
        """
        Creates a Snapshot resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.Snapshot)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#ec2serviceresourcesnapshot-method)
        """

    def Subnet(self, id: str) -> _Subnet:
        """
        Creates a Subnet resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.Subnet)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#ec2serviceresourcesubnet-method)
        """

    def Tag(self, resource_id: str, key: str, value: str) -> _Tag:
        """
        Creates a Tag resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.Tag)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#ec2serviceresourcetag-method)
        """

    def Volume(self, id: str) -> _Volume:
        """
        Creates a Volume resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.Volume)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#ec2serviceresourcevolume-method)
        """

    def Vpc(self, id: str) -> _Vpc:
        """
        Creates a Vpc resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.Vpc)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#ec2serviceresourcevpc-method)
        """

    def VpcAddress(self, allocation_id: str) -> _VpcAddress:
        """
        Creates a VpcAddress resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.VpcAddress)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#ec2serviceresourcevpcaddress-method)
        """

    def VpcPeeringConnection(self, id: str) -> _VpcPeeringConnection:
        """
        Creates a VpcPeeringConnection resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.VpcPeeringConnection)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#ec2serviceresourcevpcpeeringconnection-method)
        """

    def create_dhcp_options(
        self,
        *,
        DhcpConfigurations: Sequence["NewDhcpConfigurationTypeDef"],
        TagSpecifications: Sequence["TagSpecificationTypeDef"] = ...,
        DryRun: bool = ...
    ) -> _DhcpOptions:
        """
        Creates a set of DHCP options for your VPC.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.create_dhcp_options)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#ec2serviceresourcecreate_dhcp_options-method)
        """

    def create_instances(
        self,
        *,
        MaxCount: int,
        MinCount: int,
        BlockDeviceMappings: Sequence["BlockDeviceMappingTypeDef"] = ...,
        ImageId: str = ...,
        InstanceType: InstanceTypeType = ...,
        Ipv6AddressCount: int = ...,
        Ipv6Addresses: Sequence["InstanceIpv6AddressTypeDef"] = ...,
        KernelId: str = ...,
        KeyName: str = ...,
        Monitoring: "RunInstancesMonitoringEnabledTypeDef" = ...,
        Placement: "PlacementTypeDef" = ...,
        RamdiskId: str = ...,
        SecurityGroupIds: Sequence[str] = ...,
        SecurityGroups: Sequence[str] = ...,
        SubnetId: str = ...,
        UserData: str = ...,
        AdditionalInfo: str = ...,
        ClientToken: str = ...,
        DisableApiTermination: bool = ...,
        DryRun: bool = ...,
        EbsOptimized: bool = ...,
        IamInstanceProfile: "IamInstanceProfileSpecificationTypeDef" = ...,
        InstanceInitiatedShutdownBehavior: ShutdownBehaviorType = ...,
        NetworkInterfaces: Sequence["InstanceNetworkInterfaceSpecificationTypeDef"] = ...,
        PrivateIpAddress: str = ...,
        ElasticGpuSpecification: Sequence["ElasticGpuSpecificationTypeDef"] = ...,
        ElasticInferenceAccelerators: Sequence["ElasticInferenceAcceleratorTypeDef"] = ...,
        TagSpecifications: Sequence["TagSpecificationTypeDef"] = ...,
        LaunchTemplate: "LaunchTemplateSpecificationTypeDef" = ...,
        InstanceMarketOptions: "InstanceMarketOptionsRequestTypeDef" = ...,
        CreditSpecification: "CreditSpecificationRequestTypeDef" = ...,
        CpuOptions: "CpuOptionsRequestTypeDef" = ...,
        CapacityReservationSpecification: "CapacityReservationSpecificationTypeDef" = ...,
        HibernationOptions: "HibernationOptionsRequestTypeDef" = ...,
        LicenseSpecifications: Sequence["LicenseConfigurationRequestTypeDef"] = ...,
        MetadataOptions: "InstanceMetadataOptionsRequestTypeDef" = ...,
        EnclaveOptions: "EnclaveOptionsRequestTypeDef" = ...,
        PrivateDnsNameOptions: "PrivateDnsNameOptionsRequestTypeDef" = ...
    ) -> List[_Instance]:
        """
        Launches the specified number of instances using an AMI for which you have
        permissions.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.create_instances)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#ec2serviceresourcecreate_instances-method)
        """

    def create_internet_gateway(
        self, *, TagSpecifications: Sequence["TagSpecificationTypeDef"] = ..., DryRun: bool = ...
    ) -> _InternetGateway:
        """
        Creates an internet gateway for use with a VPC.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.create_internet_gateway)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#ec2serviceresourcecreate_internet_gateway-method)
        """

    def create_key_pair(
        self,
        *,
        KeyName: str,
        DryRun: bool = ...,
        KeyType: KeyTypeType = ...,
        TagSpecifications: Sequence["TagSpecificationTypeDef"] = ...
    ) -> _KeyPair:
        """
        Creates an ED25519 or 2048-bit RSA key pair with the specified name.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.create_key_pair)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#ec2serviceresourcecreate_key_pair-method)
        """

    def create_network_acl(
        self,
        *,
        VpcId: str,
        DryRun: bool = ...,
        TagSpecifications: Sequence["TagSpecificationTypeDef"] = ...
    ) -> _NetworkAcl:
        """
        Creates a network ACL in a VPC.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.create_network_acl)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#ec2serviceresourcecreate_network_acl-method)
        """

    def create_network_interface(
        self,
        *,
        SubnetId: str,
        Description: str = ...,
        DryRun: bool = ...,
        Groups: Sequence[str] = ...,
        Ipv6AddressCount: int = ...,
        Ipv6Addresses: Sequence["InstanceIpv6AddressTypeDef"] = ...,
        PrivateIpAddress: str = ...,
        PrivateIpAddresses: Sequence["PrivateIpAddressSpecificationTypeDef"] = ...,
        SecondaryPrivateIpAddressCount: int = ...,
        Ipv4Prefixes: Sequence["Ipv4PrefixSpecificationRequestTypeDef"] = ...,
        Ipv4PrefixCount: int = ...,
        Ipv6Prefixes: Sequence["Ipv6PrefixSpecificationRequestTypeDef"] = ...,
        Ipv6PrefixCount: int = ...,
        InterfaceType: NetworkInterfaceCreationTypeType = ...,
        TagSpecifications: Sequence["TagSpecificationTypeDef"] = ...,
        ClientToken: str = ...
    ) -> _NetworkInterface:
        """
        Creates a network interface in the specified subnet.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.create_network_interface)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#ec2serviceresourcecreate_network_interface-method)
        """

    def create_placement_group(
        self,
        *,
        DryRun: bool = ...,
        GroupName: str = ...,
        Strategy: PlacementStrategyType = ...,
        PartitionCount: int = ...,
        TagSpecifications: Sequence["TagSpecificationTypeDef"] = ...
    ) -> _PlacementGroup:
        """
        Creates a placement group in which to launch instances.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.create_placement_group)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#ec2serviceresourcecreate_placement_group-method)
        """

    def create_route_table(
        self,
        *,
        VpcId: str,
        DryRun: bool = ...,
        TagSpecifications: Sequence["TagSpecificationTypeDef"] = ...
    ) -> _RouteTable:
        """
        Creates a route table for the specified VPC.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.create_route_table)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#ec2serviceresourcecreate_route_table-method)
        """

    def create_security_group(
        self,
        *,
        Description: str,
        GroupName: str,
        VpcId: str = ...,
        TagSpecifications: Sequence["TagSpecificationTypeDef"] = ...,
        DryRun: bool = ...
    ) -> _SecurityGroup:
        """
        Creates a security group.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.create_security_group)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#ec2serviceresourcecreate_security_group-method)
        """

    def create_snapshot(
        self,
        *,
        VolumeId: str,
        Description: str = ...,
        OutpostArn: str = ...,
        TagSpecifications: Sequence["TagSpecificationTypeDef"] = ...,
        DryRun: bool = ...
    ) -> _Snapshot:
        """
        Creates a snapshot of an EBS volume and stores it in Amazon S3.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.create_snapshot)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#ec2serviceresourcecreate_snapshot-method)
        """

    def create_subnet(
        self,
        *,
        VpcId: str,
        TagSpecifications: Sequence["TagSpecificationTypeDef"] = ...,
        AvailabilityZone: str = ...,
        AvailabilityZoneId: str = ...,
        CidrBlock: str = ...,
        Ipv6CidrBlock: str = ...,
        OutpostArn: str = ...,
        DryRun: bool = ...,
        Ipv6Native: bool = ...
    ) -> _Subnet:
        """
        Creates a subnet in a specified VPC.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.create_subnet)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#ec2serviceresourcecreate_subnet-method)
        """

    def create_tags(
        self, *, Resources: Sequence[str], Tags: Sequence["TagTypeDef"], DryRun: bool = ...
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.create_tags)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#ec2serviceresourcecreate_tags-method)
        """

    def create_volume(
        self,
        *,
        AvailabilityZone: str,
        Encrypted: bool = ...,
        Iops: int = ...,
        KmsKeyId: str = ...,
        OutpostArn: str = ...,
        Size: int = ...,
        SnapshotId: str = ...,
        VolumeType: VolumeTypeType = ...,
        DryRun: bool = ...,
        TagSpecifications: Sequence["TagSpecificationTypeDef"] = ...,
        MultiAttachEnabled: bool = ...,
        Throughput: int = ...,
        ClientToken: str = ...
    ) -> _Volume:
        """
        Creates an EBS volume that can be attached to an instance in the same
        Availability Zone.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.create_volume)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#ec2serviceresourcecreate_volume-method)
        """

    def create_vpc(
        self,
        *,
        CidrBlock: str = ...,
        AmazonProvidedIpv6CidrBlock: bool = ...,
        Ipv6Pool: str = ...,
        Ipv6CidrBlock: str = ...,
        Ipv4IpamPoolId: str = ...,
        Ipv4NetmaskLength: int = ...,
        Ipv6IpamPoolId: str = ...,
        Ipv6NetmaskLength: int = ...,
        DryRun: bool = ...,
        InstanceTenancy: TenancyType = ...,
        Ipv6CidrBlockNetworkBorderGroup: str = ...,
        TagSpecifications: Sequence["TagSpecificationTypeDef"] = ...
    ) -> _Vpc:
        """
        Creates a VPC with the specified IPv4 CIDR block.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.create_vpc)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#ec2serviceresourcecreate_vpc-method)
        """

    def create_vpc_peering_connection(
        self,
        *,
        DryRun: bool = ...,
        PeerOwnerId: str = ...,
        PeerVpcId: str = ...,
        VpcId: str = ...,
        PeerRegion: str = ...,
        TagSpecifications: Sequence["TagSpecificationTypeDef"] = ...
    ) -> _VpcPeeringConnection:
        """
        Requests a VPC peering connection between two VPCs: a requester VPC that you own
        and an accepter VPC with which to create the connection.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.create_vpc_peering_connection)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#ec2serviceresourcecreate_vpc_peering_connection-method)
        """

    def disassociate_route_table(self, *, AssociationId: str, DryRun: bool = ...) -> None:
        """
        Disassociates a subnet or gateway from a route table.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.disassociate_route_table)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#ec2serviceresourcedisassociate_route_table-method)
        """

    def get_available_subresources(self) -> Sequence[str]:
        """
        Returns a list of all the available sub-resources for this Resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.get_available_subresources)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#ec2serviceresourceget_available_subresources-method)
        """

    def import_key_pair(
        self,
        *,
        KeyName: str,
        PublicKeyMaterial: Union[bytes, IO[bytes], StreamingBody],
        DryRun: bool = ...,
        TagSpecifications: Sequence["TagSpecificationTypeDef"] = ...
    ) -> _KeyPairInfo:
        """
        Imports the public key from an RSA or ED25519 key pair that you created with a
        third-party tool.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.import_key_pair)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#ec2serviceresourceimport_key_pair-method)
        """

    def register_image(
        self,
        *,
        Name: str,
        ImageLocation: str = ...,
        Architecture: ArchitectureValuesType = ...,
        BlockDeviceMappings: Sequence["BlockDeviceMappingTypeDef"] = ...,
        Description: str = ...,
        DryRun: bool = ...,
        EnaSupport: bool = ...,
        KernelId: str = ...,
        BillingProducts: Sequence[str] = ...,
        RamdiskId: str = ...,
        RootDeviceName: str = ...,
        SriovNetSupport: str = ...,
        VirtualizationType: str = ...,
        BootMode: BootModeValuesType = ...
    ) -> _Image:
        """
        Registers an AMI.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/ec2.html#EC2.ServiceResource.register_image)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ec2/service_resource.html#ec2serviceresourceregister_image-method)
        """
