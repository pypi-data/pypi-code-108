'''
# cdk-library-aws-ipam

IP Address allocation management
'''
import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from ._jsii import *

import aws_cdk
import aws_cdk.aws_ec2
import constructs


class Ipam(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@renovosolutions/cdk-library-aws-ipam.Ipam",
):
    '''Creates an IPAM.

    PAM is a VPC feature that you can use to automate your IP address management workflows including
    assigning, tracking, troubleshooting, and auditing IP addresses across AWS Regions and accounts
    throughout your AWS Organization. For more information, see What is IPAM? in the Amazon VPC IPAM
    User Guide.

    :see: https://docs.aws.amazon.com/vpc/latest/ipam/what-is-it-ipam.html
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        operating_regions: typing.Optional[typing.Sequence[builtins.str]] = None,
        tags: typing.Optional[typing.Sequence[aws_cdk.CfnTag]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param description: The description for the IPAM.
        :param operating_regions: The operating Regions for an IPAM. Operating Regions are AWS Regions where the IPAM is allowed to manage IP address CIDRs. IPAM only discovers and monitors resources in the AWS Regions you select as operating Regions. For more information about operating Regions, see Create an IPAM in the Amazon VPC IPAM User Guide. Default: Stack.of(this).region
        :param tags: The key/value combination of tags to assign to the resource.
        '''
        props = IpamProps(
            description=description, operating_regions=operating_regions, tags=tags
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipam")
    def ipam(self) -> aws_cdk.aws_ec2.CfnIPAM:
        '''The underlying IPAM resource.'''
        return typing.cast(aws_cdk.aws_ec2.CfnIPAM, jsii.get(self, "ipam"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipamId")
    def ipam_id(self) -> builtins.str:
        '''The ID of the resulting IPAM resource.'''
        return typing.cast(builtins.str, jsii.get(self, "ipamId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="privateDefaultScopeId")
    def private_default_scope_id(self) -> builtins.str:
        '''The default private scope ID.'''
        return typing.cast(builtins.str, jsii.get(self, "privateDefaultScopeId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publicDefaultScopeId")
    def public_default_scope_id(self) -> builtins.str:
        '''The default public scope ID.'''
        return typing.cast(builtins.str, jsii.get(self, "publicDefaultScopeId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="scopeCount")
    def scope_count(self) -> jsii.Number:
        '''The number of scopes in this IPAM.'''
        return typing.cast(jsii.Number, jsii.get(self, "scopeCount"))


class IpamAllocation(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@renovosolutions/cdk-library-aws-ipam.IpamAllocation",
):
    '''An IPAM Allocation.

    In IPAM, an allocation is a CIDR assignment from an IPAM pool to another resource or IPAM pool.
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        ipam_pool: "IpamPool",
        cidr: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        netmask_length: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param ipam_pool: The IPAM pool from which you would like to allocate a CIDR.
        :param cidr: The CIDR you would like to allocate from the IPAM pool. Note the following:. If there is no DefaultNetmaskLength allocation rule set on the pool, you must specify either the NetmaskLength or the CIDR. If the DefaultNetmaskLength allocation rule is set on the pool, you can specify either the NetmaskLength or the CIDR and the DefaultNetmaskLength allocation rule will be ignored.
        :param description: A description of the pool allocation.
        :param netmask_length: The netmask length of the CIDR you would like to allocate from the IPAM pool. Note the following:. If there is no DefaultNetmaskLength allocation rule set on the pool, you must specify either the NetmaskLength or the CIDR. If the DefaultNetmaskLength allocation rule is set on the pool, you can specify either the NetmaskLength or the CIDR and the DefaultNetmaskLength allocation rule will be ignored.
        '''
        props = IpamAllocationProps(
            ipam_pool=ipam_pool,
            cidr=cidr,
            description=description,
            netmask_length=netmask_length,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allocation")
    def allocation(self) -> aws_cdk.aws_ec2.CfnIPAMAllocation:
        '''The underlying IPAM Allocation resource.'''
        return typing.cast(aws_cdk.aws_ec2.CfnIPAMAllocation, jsii.get(self, "allocation"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipamPoolAllocationId")
    def ipam_pool_allocation_id(self) -> builtins.str:
        '''The ID of the allocation.'''
        return typing.cast(builtins.str, jsii.get(self, "ipamPoolAllocationId"))


@jsii.data_type(
    jsii_type="@renovosolutions/cdk-library-aws-ipam.IpamAllocationProps",
    jsii_struct_bases=[],
    name_mapping={
        "ipam_pool": "ipamPool",
        "cidr": "cidr",
        "description": "description",
        "netmask_length": "netmaskLength",
    },
)
class IpamAllocationProps:
    def __init__(
        self,
        *,
        ipam_pool: "IpamPool",
        cidr: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        netmask_length: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''Properties of an IPAM Allocation.

        :param ipam_pool: The IPAM pool from which you would like to allocate a CIDR.
        :param cidr: The CIDR you would like to allocate from the IPAM pool. Note the following:. If there is no DefaultNetmaskLength allocation rule set on the pool, you must specify either the NetmaskLength or the CIDR. If the DefaultNetmaskLength allocation rule is set on the pool, you can specify either the NetmaskLength or the CIDR and the DefaultNetmaskLength allocation rule will be ignored.
        :param description: A description of the pool allocation.
        :param netmask_length: The netmask length of the CIDR you would like to allocate from the IPAM pool. Note the following:. If there is no DefaultNetmaskLength allocation rule set on the pool, you must specify either the NetmaskLength or the CIDR. If the DefaultNetmaskLength allocation rule is set on the pool, you can specify either the NetmaskLength or the CIDR and the DefaultNetmaskLength allocation rule will be ignored.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "ipam_pool": ipam_pool,
        }
        if cidr is not None:
            self._values["cidr"] = cidr
        if description is not None:
            self._values["description"] = description
        if netmask_length is not None:
            self._values["netmask_length"] = netmask_length

    @builtins.property
    def ipam_pool(self) -> "IpamPool":
        '''The IPAM pool from which you would like to allocate a CIDR.'''
        result = self._values.get("ipam_pool")
        assert result is not None, "Required property 'ipam_pool' is missing"
        return typing.cast("IpamPool", result)

    @builtins.property
    def cidr(self) -> typing.Optional[builtins.str]:
        '''The CIDR you would like to allocate from the IPAM pool. Note the following:.

        If there is no DefaultNetmaskLength allocation rule set on the pool, you must
        specify either the NetmaskLength or the CIDR.

        If the DefaultNetmaskLength allocation rule is set on the pool, you can specify
        either the NetmaskLength or the CIDR and the DefaultNetmaskLength allocation rule
        will be ignored.
        '''
        result = self._values.get("cidr")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A description of the pool allocation.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def netmask_length(self) -> typing.Optional[jsii.Number]:
        '''The netmask length of the CIDR you would like to allocate from the IPAM pool. Note the following:.

        If there is no DefaultNetmaskLength allocation rule set on the pool, you must specify either the
        NetmaskLength or the CIDR.

        If the DefaultNetmaskLength allocation rule is set on the pool, you can specify either the
        NetmaskLength or the CIDR and the DefaultNetmaskLength allocation rule will be ignored.
        '''
        result = self._values.get("netmask_length")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IpamAllocationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IpamPool(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@renovosolutions/cdk-library-aws-ipam.IpamPool",
):
    '''An IPAM Pool.

    In IPAM, a pool is a collection of contiguous IP addresses CIDRs. Pools enable you to organize your IP addresses
    according to your routing and security needs. For example, if you have separate routing and security needs for
    development and production applications, you can create a pool for each.
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        address_family: "IpamPoolAddressFamily",
        ipam_scope_id: builtins.str,
        allocation_default_netmask_length: typing.Optional[jsii.Number] = None,
        allocation_max_netmask_length: typing.Optional[jsii.Number] = None,
        allocation_min_netmask_length: typing.Optional[jsii.Number] = None,
        allocation_resource_tags: typing.Optional[typing.Sequence[aws_cdk.CfnTag]] = None,
        auto_import: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        locale: typing.Optional[builtins.str] = None,
        provisioned_cidrs: typing.Optional[typing.Sequence[aws_cdk.aws_ec2.CfnIPAMPool.ProvisionedCidrProperty]] = None,
        source_ipam_pool_id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[aws_cdk.CfnTag]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param address_family: The address family of the pool, either IPv4 or IPv6.
        :param ipam_scope_id: The IPAM scope this pool is associated with.
        :param allocation_default_netmask_length: The default netmask length for allocations added to this pool. If, for example, the CIDR assigned to this pool is 10.0.0.0/8 and you enter 16 here, new allocations will default to 10.0.0.0/16.
        :param allocation_max_netmask_length: The maximum netmask length possible for CIDR allocations in this IPAM pool to be compliant. The maximum netmask length must be greater than the minimum netmask length. Possible netmask lengths for IPv4 addresses are 0 - 32. Possible netmask lengths for IPv6 addresses are 0 - 128.
        :param allocation_min_netmask_length: The minimum netmask length required for CIDR allocations in this IPAM pool to be compliant. The minimum netmask length must be less than the maximum netmask length. Possible netmask lengths for IPv4 addresses are 0 - 32. Possible netmask lengths for IPv6 addresses are 0 - 128.
        :param allocation_resource_tags: Tags that are required for resources that use CIDRs from this IPAM pool. Resources that do not have these tags will not be allowed to allocate space from the pool. If the resources have their tags changed after they have allocated space or if the allocation tagging requirements are changed on the pool, the resource may be marked as noncompliant.
        :param auto_import: If selected, IPAM will continuously look for resources within the CIDR range of this pool and automatically import them as allocations into your IPAM. The CIDRs that will be allocated for these resources must not already be allocated to other resources in order for the import to succeed. IPAM will import a CIDR regardless of its compliance with the pool's allocation rules, so a resource might be imported and subsequently marked as noncompliant. If IPAM discovers multiple CIDRs that overlap, IPAM will import the largest CIDR only. If IPAM discovers multiple CIDRs with matching CIDRs, IPAM will randomly import one of them only. A locale must be set on the pool for this feature to work.
        :param description: The description of the pool.
        :param locale: The locale of the IPAM pool. In IPAM, the locale is the AWS Region where you want to make an IPAM pool available for allocations.Only resources in the same Region as the locale of the pool can get IP address allocations from the pool. You can only allocate a CIDR for a VPC, for example, from an IPAM pool that shares a locale with the VPC’s Region. Note that once you choose a Locale for a pool, you cannot modify it. If you choose an AWS Region for locale that has not been configured as an operating Region for the IPAM, you'll get an error.
        :param provisioned_cidrs: The CIDRs provisioned to the IPAM pool. A CIDR is a representation of an IP address and its associated network mask (or netmask) and refers to a range of IP addresses
        :param source_ipam_pool_id: The ID of the source IPAM pool. You can use this option to create an IPAM pool within an existing source pool.
        :param tags: The key/value combination of tags to assign to the resource.
        '''
        props = IpamPoolProps(
            address_family=address_family,
            ipam_scope_id=ipam_scope_id,
            allocation_default_netmask_length=allocation_default_netmask_length,
            allocation_max_netmask_length=allocation_max_netmask_length,
            allocation_min_netmask_length=allocation_min_netmask_length,
            allocation_resource_tags=allocation_resource_tags,
            auto_import=auto_import,
            description=description,
            locale=locale,
            provisioned_cidrs=provisioned_cidrs,
            source_ipam_pool_id=source_ipam_pool_id,
            tags=tags,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="provisionCidr")
    def provision_cidr(self, cidr: builtins.str) -> None:
        '''Adds a CIDR to the pool.

        :param cidr: The CIDR to add to the pool.
        '''
        return typing.cast(None, jsii.invoke(self, "provisionCidr", [cidr]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        '''The ARN of the resulting IPAM Pool resource.'''
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipamArn")
    def ipam_arn(self) -> builtins.str:
        '''The ARN of the IPAM this pool belongs to.'''
        return typing.cast(builtins.str, jsii.get(self, "ipamArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipamPoolId")
    def ipam_pool_id(self) -> builtins.str:
        '''The ID of the resulting IPAM Pool resource.'''
        return typing.cast(builtins.str, jsii.get(self, "ipamPoolId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipamScopeArn")
    def ipam_scope_arn(self) -> builtins.str:
        '''The ARN of the scope of the IPAM Pool.'''
        return typing.cast(builtins.str, jsii.get(self, "ipamScopeArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipamScopeType")
    def ipam_scope_type(self) -> "IpamScopeType":
        '''The IPAM scope type (public ir private) of the scope of the IPAM Pool.'''
        return typing.cast("IpamScopeType", jsii.get(self, "ipamScopeType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pool")
    def pool(self) -> aws_cdk.aws_ec2.CfnIPAMPool:
        '''The underlying IPAM Pool resource.'''
        return typing.cast(aws_cdk.aws_ec2.CfnIPAMPool, jsii.get(self, "pool"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="poolDepth")
    def pool_depth(self) -> jsii.Number:
        '''The depth of pools in your IPAM pool.'''
        return typing.cast(jsii.Number, jsii.get(self, "poolDepth"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="provisionedCidrs")
    def provisioned_cidrs(
        self,
    ) -> typing.List[aws_cdk.aws_ec2.CfnIPAMPool.ProvisionedCidrProperty]:
        '''The provisioned CIDRs for this pool.'''
        return typing.cast(typing.List[aws_cdk.aws_ec2.CfnIPAMPool.ProvisionedCidrProperty], jsii.get(self, "provisionedCidrs"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        '''The state of the IPAM pool.'''
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stateMessage")
    def state_message(self) -> builtins.str:
        '''A message related to the failed creation of an IPAM pool.'''
        return typing.cast(builtins.str, jsii.get(self, "stateMessage"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allocationDefaultNetmaskLength")
    def allocation_default_netmask_length(self) -> typing.Optional[jsii.Number]:
        '''The default netmask length for allocations added to this pool.'''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "allocationDefaultNetmaskLength"))


@jsii.enum(jsii_type="@renovosolutions/cdk-library-aws-ipam.IpamPoolAddressFamily")
class IpamPoolAddressFamily(enum.Enum):
    IPV4 = "IPV4"
    IPV6 = "IPV6"


@jsii.data_type(
    jsii_type="@renovosolutions/cdk-library-aws-ipam.IpamPoolProps",
    jsii_struct_bases=[],
    name_mapping={
        "address_family": "addressFamily",
        "ipam_scope_id": "ipamScopeId",
        "allocation_default_netmask_length": "allocationDefaultNetmaskLength",
        "allocation_max_netmask_length": "allocationMaxNetmaskLength",
        "allocation_min_netmask_length": "allocationMinNetmaskLength",
        "allocation_resource_tags": "allocationResourceTags",
        "auto_import": "autoImport",
        "description": "description",
        "locale": "locale",
        "provisioned_cidrs": "provisionedCidrs",
        "source_ipam_pool_id": "sourceIpamPoolId",
        "tags": "tags",
    },
)
class IpamPoolProps:
    def __init__(
        self,
        *,
        address_family: IpamPoolAddressFamily,
        ipam_scope_id: builtins.str,
        allocation_default_netmask_length: typing.Optional[jsii.Number] = None,
        allocation_max_netmask_length: typing.Optional[jsii.Number] = None,
        allocation_min_netmask_length: typing.Optional[jsii.Number] = None,
        allocation_resource_tags: typing.Optional[typing.Sequence[aws_cdk.CfnTag]] = None,
        auto_import: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        locale: typing.Optional[builtins.str] = None,
        provisioned_cidrs: typing.Optional[typing.Sequence[aws_cdk.aws_ec2.CfnIPAMPool.ProvisionedCidrProperty]] = None,
        source_ipam_pool_id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[aws_cdk.CfnTag]] = None,
    ) -> None:
        '''Properties of an IPAM Pool.

        :param address_family: The address family of the pool, either IPv4 or IPv6.
        :param ipam_scope_id: The IPAM scope this pool is associated with.
        :param allocation_default_netmask_length: The default netmask length for allocations added to this pool. If, for example, the CIDR assigned to this pool is 10.0.0.0/8 and you enter 16 here, new allocations will default to 10.0.0.0/16.
        :param allocation_max_netmask_length: The maximum netmask length possible for CIDR allocations in this IPAM pool to be compliant. The maximum netmask length must be greater than the minimum netmask length. Possible netmask lengths for IPv4 addresses are 0 - 32. Possible netmask lengths for IPv6 addresses are 0 - 128.
        :param allocation_min_netmask_length: The minimum netmask length required for CIDR allocations in this IPAM pool to be compliant. The minimum netmask length must be less than the maximum netmask length. Possible netmask lengths for IPv4 addresses are 0 - 32. Possible netmask lengths for IPv6 addresses are 0 - 128.
        :param allocation_resource_tags: Tags that are required for resources that use CIDRs from this IPAM pool. Resources that do not have these tags will not be allowed to allocate space from the pool. If the resources have their tags changed after they have allocated space or if the allocation tagging requirements are changed on the pool, the resource may be marked as noncompliant.
        :param auto_import: If selected, IPAM will continuously look for resources within the CIDR range of this pool and automatically import them as allocations into your IPAM. The CIDRs that will be allocated for these resources must not already be allocated to other resources in order for the import to succeed. IPAM will import a CIDR regardless of its compliance with the pool's allocation rules, so a resource might be imported and subsequently marked as noncompliant. If IPAM discovers multiple CIDRs that overlap, IPAM will import the largest CIDR only. If IPAM discovers multiple CIDRs with matching CIDRs, IPAM will randomly import one of them only. A locale must be set on the pool for this feature to work.
        :param description: The description of the pool.
        :param locale: The locale of the IPAM pool. In IPAM, the locale is the AWS Region where you want to make an IPAM pool available for allocations.Only resources in the same Region as the locale of the pool can get IP address allocations from the pool. You can only allocate a CIDR for a VPC, for example, from an IPAM pool that shares a locale with the VPC’s Region. Note that once you choose a Locale for a pool, you cannot modify it. If you choose an AWS Region for locale that has not been configured as an operating Region for the IPAM, you'll get an error.
        :param provisioned_cidrs: The CIDRs provisioned to the IPAM pool. A CIDR is a representation of an IP address and its associated network mask (or netmask) and refers to a range of IP addresses
        :param source_ipam_pool_id: The ID of the source IPAM pool. You can use this option to create an IPAM pool within an existing source pool.
        :param tags: The key/value combination of tags to assign to the resource.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "address_family": address_family,
            "ipam_scope_id": ipam_scope_id,
        }
        if allocation_default_netmask_length is not None:
            self._values["allocation_default_netmask_length"] = allocation_default_netmask_length
        if allocation_max_netmask_length is not None:
            self._values["allocation_max_netmask_length"] = allocation_max_netmask_length
        if allocation_min_netmask_length is not None:
            self._values["allocation_min_netmask_length"] = allocation_min_netmask_length
        if allocation_resource_tags is not None:
            self._values["allocation_resource_tags"] = allocation_resource_tags
        if auto_import is not None:
            self._values["auto_import"] = auto_import
        if description is not None:
            self._values["description"] = description
        if locale is not None:
            self._values["locale"] = locale
        if provisioned_cidrs is not None:
            self._values["provisioned_cidrs"] = provisioned_cidrs
        if source_ipam_pool_id is not None:
            self._values["source_ipam_pool_id"] = source_ipam_pool_id
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def address_family(self) -> IpamPoolAddressFamily:
        '''The address family of the pool, either IPv4 or IPv6.'''
        result = self._values.get("address_family")
        assert result is not None, "Required property 'address_family' is missing"
        return typing.cast(IpamPoolAddressFamily, result)

    @builtins.property
    def ipam_scope_id(self) -> builtins.str:
        '''The IPAM scope this pool is associated with.'''
        result = self._values.get("ipam_scope_id")
        assert result is not None, "Required property 'ipam_scope_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def allocation_default_netmask_length(self) -> typing.Optional[jsii.Number]:
        '''The default netmask length for allocations added to this pool.

        If, for example, the CIDR assigned to this pool is 10.0.0.0/8 and you enter 16 here,
        new allocations will default to 10.0.0.0/16.
        '''
        result = self._values.get("allocation_default_netmask_length")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def allocation_max_netmask_length(self) -> typing.Optional[jsii.Number]:
        '''The maximum netmask length possible for CIDR allocations in this IPAM pool to be compliant.

        The maximum netmask length must be greater than the minimum netmask length.
        Possible netmask lengths for IPv4 addresses are 0 - 32. Possible netmask lengths for IPv6 addresses are 0 - 128.
        '''
        result = self._values.get("allocation_max_netmask_length")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def allocation_min_netmask_length(self) -> typing.Optional[jsii.Number]:
        '''The minimum netmask length required for CIDR allocations in this IPAM pool to be compliant.

        The minimum netmask length must be less than the maximum netmask length.
        Possible netmask lengths for IPv4 addresses are 0 - 32. Possible netmask lengths for IPv6 addresses are 0 - 128.
        '''
        result = self._values.get("allocation_min_netmask_length")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def allocation_resource_tags(self) -> typing.Optional[typing.List[aws_cdk.CfnTag]]:
        '''Tags that are required for resources that use CIDRs from this IPAM pool.

        Resources that do not have these tags will not be allowed to allocate space from the pool.
        If the resources have their tags changed after they have allocated space or if the allocation
        tagging requirements are changed on the pool, the resource may be marked as noncompliant.
        '''
        result = self._values.get("allocation_resource_tags")
        return typing.cast(typing.Optional[typing.List[aws_cdk.CfnTag]], result)

    @builtins.property
    def auto_import(self) -> typing.Optional[builtins.bool]:
        '''If selected, IPAM will continuously look for resources within the CIDR range of this pool and automatically import them as allocations into your IPAM.

        The CIDRs that will be allocated for these resources must not already be allocated
        to other resources in order for the import to succeed. IPAM will import a CIDR regardless of its compliance with the
        pool's allocation rules, so a resource might be imported and subsequently marked as noncompliant. If IPAM discovers
        multiple CIDRs that overlap, IPAM will import the largest CIDR only. If IPAM discovers multiple CIDRs with matching
        CIDRs, IPAM will randomly import one of them only.

        A locale must be set on the pool for this feature to work.
        '''
        result = self._values.get("auto_import")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''The description of the pool.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def locale(self) -> typing.Optional[builtins.str]:
        '''The locale of the IPAM pool.

        In IPAM, the locale is the AWS Region where you want to make an IPAM pool available
        for allocations.Only resources in the same Region as the locale of the pool can get IP address allocations from the pool.
        You can only allocate a CIDR for a VPC, for example, from an IPAM pool that shares a locale with the VPC’s Region.
        Note that once you choose a Locale for a pool, you cannot modify it. If you choose an AWS Region for locale that has
        not been configured as an operating Region for the IPAM, you'll get an error.
        '''
        result = self._values.get("locale")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def provisioned_cidrs(
        self,
    ) -> typing.Optional[typing.List[aws_cdk.aws_ec2.CfnIPAMPool.ProvisionedCidrProperty]]:
        '''The CIDRs provisioned to the IPAM pool.

        A CIDR is a representation of an IP address and its associated network mask
        (or netmask) and refers to a range of IP addresses
        '''
        result = self._values.get("provisioned_cidrs")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_ec2.CfnIPAMPool.ProvisionedCidrProperty]], result)

    @builtins.property
    def source_ipam_pool_id(self) -> typing.Optional[builtins.str]:
        '''The ID of the source IPAM pool.

        You can use this option to create an IPAM pool within an existing source pool.
        '''
        result = self._values.get("source_ipam_pool_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[aws_cdk.CfnTag]]:
        '''The key/value combination of tags to assign to the resource.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[aws_cdk.CfnTag]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IpamPoolProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@renovosolutions/cdk-library-aws-ipam.IpamProps",
    jsii_struct_bases=[],
    name_mapping={
        "description": "description",
        "operating_regions": "operatingRegions",
        "tags": "tags",
    },
)
class IpamProps:
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        operating_regions: typing.Optional[typing.Sequence[builtins.str]] = None,
        tags: typing.Optional[typing.Sequence[aws_cdk.CfnTag]] = None,
    ) -> None:
        '''Properties of the IPAM.

        :param description: The description for the IPAM.
        :param operating_regions: The operating Regions for an IPAM. Operating Regions are AWS Regions where the IPAM is allowed to manage IP address CIDRs. IPAM only discovers and monitors resources in the AWS Regions you select as operating Regions. For more information about operating Regions, see Create an IPAM in the Amazon VPC IPAM User Guide. Default: Stack.of(this).region
        :param tags: The key/value combination of tags to assign to the resource.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if description is not None:
            self._values["description"] = description
        if operating_regions is not None:
            self._values["operating_regions"] = operating_regions
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''The description for the IPAM.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def operating_regions(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The operating Regions for an IPAM.

        Operating Regions are AWS Regions where the IPAM is allowed to manage IP address CIDRs. IPAM only
        discovers and monitors resources in the AWS Regions you select as operating Regions.

        For more information about operating Regions, see Create an IPAM in the Amazon VPC IPAM User Guide.

        :default: Stack.of(this).region

        :see: https://vpc/latest/ipam/create-ipam.html
        '''
        result = self._values.get("operating_regions")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[aws_cdk.CfnTag]]:
        '''The key/value combination of tags to assign to the resource.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[aws_cdk.CfnTag]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IpamProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IpamScope(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@renovosolutions/cdk-library-aws-ipam.IpamScope",
):
    '''An IPAM Scope.

    In IPAM, a scope is the highest-level container within IPAM. An IPAM contains two default scopes.
    Each scope represents the IP space for a single network. The private scope is intended for all private
    IP address space. The public scope is intended for all public IP address space. Scopes enable you to
    reuse IP addresses across multiple unconnected networks without causing IP address overlap or conflict.
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        ipam: Ipam,
        description: typing.Optional[builtins.str] = None,
        ipam_scope_type: typing.Optional["IpamScopeType"] = None,
        tags: typing.Optional[typing.Sequence[aws_cdk.CfnTag]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param ipam: The IPAM for which you're creating the scope.
        :param description: The description of the scope.
        :param ipam_scope_type: The type of scope. Default: IpamScopeType.PRIVATE
        :param tags: The key/value combination of tags to assign to the resource.
        '''
        props = IpamScopeProps(
            ipam=ipam,
            description=description,
            ipam_scope_type=ipam_scope_type,
            tags=tags,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        '''The ARN of the resulting IPAM Scope resource.'''
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipamArn")
    def ipam_arn(self) -> builtins.str:
        '''The ARN of the IPAM this scope belongs to.'''
        return typing.cast(builtins.str, jsii.get(self, "ipamArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipamScopeId")
    def ipam_scope_id(self) -> builtins.str:
        '''The ID of the resulting IPAM Scope resource.'''
        return typing.cast(builtins.str, jsii.get(self, "ipamScopeId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="isDefault")
    def is_default(self) -> aws_cdk.IResolvable:
        '''Indicates whether the scope is the default scope for the IPAM.'''
        return typing.cast(aws_cdk.IResolvable, jsii.get(self, "isDefault"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="poolCount")
    def pool_count(self) -> jsii.Number:
        '''The number of pools in the scope.'''
        return typing.cast(jsii.Number, jsii.get(self, "poolCount"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="scope")
    def scope(self) -> aws_cdk.aws_ec2.CfnIPAMScope:
        '''The underlying IPAM Scope resource.'''
        return typing.cast(aws_cdk.aws_ec2.CfnIPAMScope, jsii.get(self, "scope"))


@jsii.data_type(
    jsii_type="@renovosolutions/cdk-library-aws-ipam.IpamScopeProps",
    jsii_struct_bases=[],
    name_mapping={
        "ipam": "ipam",
        "description": "description",
        "ipam_scope_type": "ipamScopeType",
        "tags": "tags",
    },
)
class IpamScopeProps:
    def __init__(
        self,
        *,
        ipam: Ipam,
        description: typing.Optional[builtins.str] = None,
        ipam_scope_type: typing.Optional["IpamScopeType"] = None,
        tags: typing.Optional[typing.Sequence[aws_cdk.CfnTag]] = None,
    ) -> None:
        '''Properties of an IPAM Scope.

        :param ipam: The IPAM for which you're creating the scope.
        :param description: The description of the scope.
        :param ipam_scope_type: The type of scope. Default: IpamScopeType.PRIVATE
        :param tags: The key/value combination of tags to assign to the resource.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "ipam": ipam,
        }
        if description is not None:
            self._values["description"] = description
        if ipam_scope_type is not None:
            self._values["ipam_scope_type"] = ipam_scope_type
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def ipam(self) -> Ipam:
        '''The IPAM for which you're creating the scope.'''
        result = self._values.get("ipam")
        assert result is not None, "Required property 'ipam' is missing"
        return typing.cast(Ipam, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''The description of the scope.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ipam_scope_type(self) -> typing.Optional["IpamScopeType"]:
        '''The type of scope.

        :default: IpamScopeType.PRIVATE
        '''
        result = self._values.get("ipam_scope_type")
        return typing.cast(typing.Optional["IpamScopeType"], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[aws_cdk.CfnTag]]:
        '''The key/value combination of tags to assign to the resource.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[aws_cdk.CfnTag]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IpamScopeProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@renovosolutions/cdk-library-aws-ipam.IpamScopeType")
class IpamScopeType(enum.Enum):
    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"


__all__ = [
    "Ipam",
    "IpamAllocation",
    "IpamAllocationProps",
    "IpamPool",
    "IpamPoolAddressFamily",
    "IpamPoolProps",
    "IpamProps",
    "IpamScope",
    "IpamScopeProps",
    "IpamScopeType",
]

publication.publish()
