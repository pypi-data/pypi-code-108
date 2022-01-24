import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from .._jsii import *

import cdktf
import constructs


class DatasyncAgent(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.datasync.DatasyncAgent",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/datasync_agent aws_datasync_agent}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        activation_key: typing.Optional[builtins.str] = None,
        ip_address: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        private_link_endpoint: typing.Optional[builtins.str] = None,
        security_group_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        subnet_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["DatasyncAgentTimeouts"] = None,
        vpc_endpoint_id: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/datasync_agent aws_datasync_agent} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param activation_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_agent#activation_key DatasyncAgent#activation_key}.
        :param ip_address: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_agent#ip_address DatasyncAgent#ip_address}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_agent#name DatasyncAgent#name}.
        :param private_link_endpoint: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_agent#private_link_endpoint DatasyncAgent#private_link_endpoint}.
        :param security_group_arns: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_agent#security_group_arns DatasyncAgent#security_group_arns}.
        :param subnet_arns: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_agent#subnet_arns DatasyncAgent#subnet_arns}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_agent#tags DatasyncAgent#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_agent#tags_all DatasyncAgent#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_agent#timeouts DatasyncAgent#timeouts}
        :param vpc_endpoint_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_agent#vpc_endpoint_id DatasyncAgent#vpc_endpoint_id}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DatasyncAgentConfig(
            activation_key=activation_key,
            ip_address=ip_address,
            name=name,
            private_link_endpoint=private_link_endpoint,
            security_group_arns=security_group_arns,
            subnet_arns=subnet_arns,
            tags=tags,
            tags_all=tags_all,
            timeouts=timeouts,
            vpc_endpoint_id=vpc_endpoint_id,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(self, *, create: typing.Optional[builtins.str] = None) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_agent#create DatasyncAgent#create}.
        '''
        value = DatasyncAgentTimeouts(create=create)

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetActivationKey")
    def reset_activation_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetActivationKey", []))

    @jsii.member(jsii_name="resetIpAddress")
    def reset_ip_address(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIpAddress", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetPrivateLinkEndpoint")
    def reset_private_link_endpoint(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrivateLinkEndpoint", []))

    @jsii.member(jsii_name="resetSecurityGroupArns")
    def reset_security_group_arns(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecurityGroupArns", []))

    @jsii.member(jsii_name="resetSubnetArns")
    def reset_subnet_arns(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSubnetArns", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetTimeouts")
    def reset_timeouts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeouts", []))

    @jsii.member(jsii_name="resetVpcEndpointId")
    def reset_vpc_endpoint_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVpcEndpointId", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "DatasyncAgentTimeoutsOutputReference":
        return typing.cast("DatasyncAgentTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="activationKeyInput")
    def activation_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "activationKeyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipAddressInput")
    def ip_address_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ipAddressInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="privateLinkEndpointInput")
    def private_link_endpoint_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "privateLinkEndpointInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroupArnsInput")
    def security_group_arns_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "securityGroupArnsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnetArnsInput")
    def subnet_arns_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "subnetArnsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAllInput")
    def tags_all_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsAllInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(self) -> typing.Optional["DatasyncAgentTimeouts"]:
        return typing.cast(typing.Optional["DatasyncAgentTimeouts"], jsii.get(self, "timeoutsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcEndpointIdInput")
    def vpc_endpoint_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "vpcEndpointIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="activationKey")
    def activation_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "activationKey"))

    @activation_key.setter
    def activation_key(self, value: builtins.str) -> None:
        jsii.set(self, "activationKey", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipAddress")
    def ip_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ipAddress"))

    @ip_address.setter
    def ip_address(self, value: builtins.str) -> None:
        jsii.set(self, "ipAddress", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="privateLinkEndpoint")
    def private_link_endpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "privateLinkEndpoint"))

    @private_link_endpoint.setter
    def private_link_endpoint(self, value: builtins.str) -> None:
        jsii.set(self, "privateLinkEndpoint", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroupArns")
    def security_group_arns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "securityGroupArns"))

    @security_group_arns.setter
    def security_group_arns(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "securityGroupArns", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnetArns")
    def subnet_arns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "subnetArns"))

    @subnet_arns.setter
    def subnet_arns(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "subnetArns", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tags"))

    @tags.setter
    def tags(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "tags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAll")
    def tags_all(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsAll"))

    @tags_all.setter
    def tags_all(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "tagsAll", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcEndpointId")
    def vpc_endpoint_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "vpcEndpointId"))

    @vpc_endpoint_id.setter
    def vpc_endpoint_id(self, value: builtins.str) -> None:
        jsii.set(self, "vpcEndpointId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.datasync.DatasyncAgentConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "activation_key": "activationKey",
        "ip_address": "ipAddress",
        "name": "name",
        "private_link_endpoint": "privateLinkEndpoint",
        "security_group_arns": "securityGroupArns",
        "subnet_arns": "subnetArns",
        "tags": "tags",
        "tags_all": "tagsAll",
        "timeouts": "timeouts",
        "vpc_endpoint_id": "vpcEndpointId",
    },
)
class DatasyncAgentConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        activation_key: typing.Optional[builtins.str] = None,
        ip_address: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        private_link_endpoint: typing.Optional[builtins.str] = None,
        security_group_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        subnet_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["DatasyncAgentTimeouts"] = None,
        vpc_endpoint_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS DataSync.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param activation_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_agent#activation_key DatasyncAgent#activation_key}.
        :param ip_address: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_agent#ip_address DatasyncAgent#ip_address}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_agent#name DatasyncAgent#name}.
        :param private_link_endpoint: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_agent#private_link_endpoint DatasyncAgent#private_link_endpoint}.
        :param security_group_arns: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_agent#security_group_arns DatasyncAgent#security_group_arns}.
        :param subnet_arns: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_agent#subnet_arns DatasyncAgent#subnet_arns}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_agent#tags DatasyncAgent#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_agent#tags_all DatasyncAgent#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_agent#timeouts DatasyncAgent#timeouts}
        :param vpc_endpoint_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_agent#vpc_endpoint_id DatasyncAgent#vpc_endpoint_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(timeouts, dict):
            timeouts = DatasyncAgentTimeouts(**timeouts)
        self._values: typing.Dict[str, typing.Any] = {}
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if activation_key is not None:
            self._values["activation_key"] = activation_key
        if ip_address is not None:
            self._values["ip_address"] = ip_address
        if name is not None:
            self._values["name"] = name
        if private_link_endpoint is not None:
            self._values["private_link_endpoint"] = private_link_endpoint
        if security_group_arns is not None:
            self._values["security_group_arns"] = security_group_arns
        if subnet_arns is not None:
            self._values["subnet_arns"] = subnet_arns
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if timeouts is not None:
            self._values["timeouts"] = timeouts
        if vpc_endpoint_id is not None:
            self._values["vpc_endpoint_id"] = vpc_endpoint_id

    @builtins.property
    def count(self) -> typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def activation_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_agent#activation_key DatasyncAgent#activation_key}.'''
        result = self._values.get("activation_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ip_address(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_agent#ip_address DatasyncAgent#ip_address}.'''
        result = self._values.get("ip_address")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_agent#name DatasyncAgent#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def private_link_endpoint(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_agent#private_link_endpoint DatasyncAgent#private_link_endpoint}.'''
        result = self._values.get("private_link_endpoint")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def security_group_arns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_agent#security_group_arns DatasyncAgent#security_group_arns}.'''
        result = self._values.get("security_group_arns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def subnet_arns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_agent#subnet_arns DatasyncAgent#subnet_arns}.'''
        result = self._values.get("subnet_arns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_agent#tags DatasyncAgent#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_agent#tags_all DatasyncAgent#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["DatasyncAgentTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_agent#timeouts DatasyncAgent#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["DatasyncAgentTimeouts"], result)

    @builtins.property
    def vpc_endpoint_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_agent#vpc_endpoint_id DatasyncAgent#vpc_endpoint_id}.'''
        result = self._values.get("vpc_endpoint_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatasyncAgentConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.datasync.DatasyncAgentTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create"},
)
class DatasyncAgentTimeouts:
    def __init__(self, *, create: typing.Optional[builtins.str] = None) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_agent#create DatasyncAgent#create}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if create is not None:
            self._values["create"] = create

    @builtins.property
    def create(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_agent#create DatasyncAgent#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatasyncAgentTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DatasyncAgentTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.datasync.DatasyncAgentTimeoutsOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetCreate")
    def reset_create(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreate", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createInput")
    def create_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="create")
    def create(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "create"))

    @create.setter
    def create(self, value: builtins.str) -> None:
        jsii.set(self, "create", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DatasyncAgentTimeouts]:
        return typing.cast(typing.Optional[DatasyncAgentTimeouts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[DatasyncAgentTimeouts]) -> None:
        jsii.set(self, "internalValue", value)


class DatasyncLocationEfs(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.datasync.DatasyncLocationEfs",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_efs aws_datasync_location_efs}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        ec2_config: "DatasyncLocationEfsEc2Config",
        efs_file_system_arn: builtins.str,
        subdirectory: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_efs aws_datasync_location_efs} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param ec2_config: ec2_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_efs#ec2_config DatasyncLocationEfs#ec2_config}
        :param efs_file_system_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_efs#efs_file_system_arn DatasyncLocationEfs#efs_file_system_arn}.
        :param subdirectory: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_efs#subdirectory DatasyncLocationEfs#subdirectory}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_efs#tags DatasyncLocationEfs#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_efs#tags_all DatasyncLocationEfs#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DatasyncLocationEfsConfig(
            ec2_config=ec2_config,
            efs_file_system_arn=efs_file_system_arn,
            subdirectory=subdirectory,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putEc2Config")
    def put_ec2_config(
        self,
        *,
        security_group_arns: typing.Sequence[builtins.str],
        subnet_arn: builtins.str,
    ) -> None:
        '''
        :param security_group_arns: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_efs#security_group_arns DatasyncLocationEfs#security_group_arns}.
        :param subnet_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_efs#subnet_arn DatasyncLocationEfs#subnet_arn}.
        '''
        value = DatasyncLocationEfsEc2Config(
            security_group_arns=security_group_arns, subnet_arn=subnet_arn
        )

        return typing.cast(None, jsii.invoke(self, "putEc2Config", [value]))

    @jsii.member(jsii_name="resetSubdirectory")
    def reset_subdirectory(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSubdirectory", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ec2Config")
    def ec2_config(self) -> "DatasyncLocationEfsEc2ConfigOutputReference":
        return typing.cast("DatasyncLocationEfsEc2ConfigOutputReference", jsii.get(self, "ec2Config"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="uri")
    def uri(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uri"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ec2ConfigInput")
    def ec2_config_input(self) -> typing.Optional["DatasyncLocationEfsEc2Config"]:
        return typing.cast(typing.Optional["DatasyncLocationEfsEc2Config"], jsii.get(self, "ec2ConfigInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="efsFileSystemArnInput")
    def efs_file_system_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "efsFileSystemArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subdirectoryInput")
    def subdirectory_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "subdirectoryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAllInput")
    def tags_all_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsAllInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="efsFileSystemArn")
    def efs_file_system_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "efsFileSystemArn"))

    @efs_file_system_arn.setter
    def efs_file_system_arn(self, value: builtins.str) -> None:
        jsii.set(self, "efsFileSystemArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subdirectory")
    def subdirectory(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "subdirectory"))

    @subdirectory.setter
    def subdirectory(self, value: builtins.str) -> None:
        jsii.set(self, "subdirectory", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tags"))

    @tags.setter
    def tags(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "tags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAll")
    def tags_all(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsAll"))

    @tags_all.setter
    def tags_all(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "tagsAll", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.datasync.DatasyncLocationEfsConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "ec2_config": "ec2Config",
        "efs_file_system_arn": "efsFileSystemArn",
        "subdirectory": "subdirectory",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class DatasyncLocationEfsConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        ec2_config: "DatasyncLocationEfsEc2Config",
        efs_file_system_arn: builtins.str,
        subdirectory: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS DataSync.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param ec2_config: ec2_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_efs#ec2_config DatasyncLocationEfs#ec2_config}
        :param efs_file_system_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_efs#efs_file_system_arn DatasyncLocationEfs#efs_file_system_arn}.
        :param subdirectory: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_efs#subdirectory DatasyncLocationEfs#subdirectory}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_efs#tags DatasyncLocationEfs#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_efs#tags_all DatasyncLocationEfs#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(ec2_config, dict):
            ec2_config = DatasyncLocationEfsEc2Config(**ec2_config)
        self._values: typing.Dict[str, typing.Any] = {
            "ec2_config": ec2_config,
            "efs_file_system_arn": efs_file_system_arn,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if subdirectory is not None:
            self._values["subdirectory"] = subdirectory
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all

    @builtins.property
    def count(self) -> typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def ec2_config(self) -> "DatasyncLocationEfsEc2Config":
        '''ec2_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_efs#ec2_config DatasyncLocationEfs#ec2_config}
        '''
        result = self._values.get("ec2_config")
        assert result is not None, "Required property 'ec2_config' is missing"
        return typing.cast("DatasyncLocationEfsEc2Config", result)

    @builtins.property
    def efs_file_system_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_efs#efs_file_system_arn DatasyncLocationEfs#efs_file_system_arn}.'''
        result = self._values.get("efs_file_system_arn")
        assert result is not None, "Required property 'efs_file_system_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def subdirectory(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_efs#subdirectory DatasyncLocationEfs#subdirectory}.'''
        result = self._values.get("subdirectory")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_efs#tags DatasyncLocationEfs#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_efs#tags_all DatasyncLocationEfs#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatasyncLocationEfsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.datasync.DatasyncLocationEfsEc2Config",
    jsii_struct_bases=[],
    name_mapping={
        "security_group_arns": "securityGroupArns",
        "subnet_arn": "subnetArn",
    },
)
class DatasyncLocationEfsEc2Config:
    def __init__(
        self,
        *,
        security_group_arns: typing.Sequence[builtins.str],
        subnet_arn: builtins.str,
    ) -> None:
        '''
        :param security_group_arns: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_efs#security_group_arns DatasyncLocationEfs#security_group_arns}.
        :param subnet_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_efs#subnet_arn DatasyncLocationEfs#subnet_arn}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "security_group_arns": security_group_arns,
            "subnet_arn": subnet_arn,
        }

    @builtins.property
    def security_group_arns(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_efs#security_group_arns DatasyncLocationEfs#security_group_arns}.'''
        result = self._values.get("security_group_arns")
        assert result is not None, "Required property 'security_group_arns' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def subnet_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_efs#subnet_arn DatasyncLocationEfs#subnet_arn}.'''
        result = self._values.get("subnet_arn")
        assert result is not None, "Required property 'subnet_arn' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatasyncLocationEfsEc2Config(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DatasyncLocationEfsEc2ConfigOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.datasync.DatasyncLocationEfsEc2ConfigOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroupArnsInput")
    def security_group_arns_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "securityGroupArnsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnetArnInput")
    def subnet_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "subnetArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroupArns")
    def security_group_arns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "securityGroupArns"))

    @security_group_arns.setter
    def security_group_arns(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "securityGroupArns", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnetArn")
    def subnet_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "subnetArn"))

    @subnet_arn.setter
    def subnet_arn(self, value: builtins.str) -> None:
        jsii.set(self, "subnetArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DatasyncLocationEfsEc2Config]:
        return typing.cast(typing.Optional[DatasyncLocationEfsEc2Config], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DatasyncLocationEfsEc2Config],
    ) -> None:
        jsii.set(self, "internalValue", value)


class DatasyncLocationFsxLustreFileSystem(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.datasync.DatasyncLocationFsxLustreFileSystem",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_fsx_lustre_file_system aws_datasync_location_fsx_lustre_file_system}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        fsx_filesystem_arn: builtins.str,
        security_group_arns: typing.Sequence[builtins.str],
        subdirectory: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_fsx_lustre_file_system aws_datasync_location_fsx_lustre_file_system} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param fsx_filesystem_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_fsx_lustre_file_system#fsx_filesystem_arn DatasyncLocationFsxLustreFileSystem#fsx_filesystem_arn}.
        :param security_group_arns: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_fsx_lustre_file_system#security_group_arns DatasyncLocationFsxLustreFileSystem#security_group_arns}.
        :param subdirectory: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_fsx_lustre_file_system#subdirectory DatasyncLocationFsxLustreFileSystem#subdirectory}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_fsx_lustre_file_system#tags DatasyncLocationFsxLustreFileSystem#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_fsx_lustre_file_system#tags_all DatasyncLocationFsxLustreFileSystem#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DatasyncLocationFsxLustreFileSystemConfig(
            fsx_filesystem_arn=fsx_filesystem_arn,
            security_group_arns=security_group_arns,
            subdirectory=subdirectory,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetSubdirectory")
    def reset_subdirectory(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSubdirectory", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="creationTime")
    def creation_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "creationTime"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="uri")
    def uri(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uri"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fsxFilesystemArnInput")
    def fsx_filesystem_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fsxFilesystemArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroupArnsInput")
    def security_group_arns_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "securityGroupArnsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subdirectoryInput")
    def subdirectory_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "subdirectoryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAllInput")
    def tags_all_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsAllInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fsxFilesystemArn")
    def fsx_filesystem_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fsxFilesystemArn"))

    @fsx_filesystem_arn.setter
    def fsx_filesystem_arn(self, value: builtins.str) -> None:
        jsii.set(self, "fsxFilesystemArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroupArns")
    def security_group_arns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "securityGroupArns"))

    @security_group_arns.setter
    def security_group_arns(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "securityGroupArns", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subdirectory")
    def subdirectory(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "subdirectory"))

    @subdirectory.setter
    def subdirectory(self, value: builtins.str) -> None:
        jsii.set(self, "subdirectory", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tags"))

    @tags.setter
    def tags(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "tags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAll")
    def tags_all(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsAll"))

    @tags_all.setter
    def tags_all(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "tagsAll", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.datasync.DatasyncLocationFsxLustreFileSystemConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "fsx_filesystem_arn": "fsxFilesystemArn",
        "security_group_arns": "securityGroupArns",
        "subdirectory": "subdirectory",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class DatasyncLocationFsxLustreFileSystemConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        fsx_filesystem_arn: builtins.str,
        security_group_arns: typing.Sequence[builtins.str],
        subdirectory: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS DataSync.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param fsx_filesystem_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_fsx_lustre_file_system#fsx_filesystem_arn DatasyncLocationFsxLustreFileSystem#fsx_filesystem_arn}.
        :param security_group_arns: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_fsx_lustre_file_system#security_group_arns DatasyncLocationFsxLustreFileSystem#security_group_arns}.
        :param subdirectory: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_fsx_lustre_file_system#subdirectory DatasyncLocationFsxLustreFileSystem#subdirectory}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_fsx_lustre_file_system#tags DatasyncLocationFsxLustreFileSystem#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_fsx_lustre_file_system#tags_all DatasyncLocationFsxLustreFileSystem#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "fsx_filesystem_arn": fsx_filesystem_arn,
            "security_group_arns": security_group_arns,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if subdirectory is not None:
            self._values["subdirectory"] = subdirectory
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all

    @builtins.property
    def count(self) -> typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def fsx_filesystem_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_fsx_lustre_file_system#fsx_filesystem_arn DatasyncLocationFsxLustreFileSystem#fsx_filesystem_arn}.'''
        result = self._values.get("fsx_filesystem_arn")
        assert result is not None, "Required property 'fsx_filesystem_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def security_group_arns(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_fsx_lustre_file_system#security_group_arns DatasyncLocationFsxLustreFileSystem#security_group_arns}.'''
        result = self._values.get("security_group_arns")
        assert result is not None, "Required property 'security_group_arns' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def subdirectory(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_fsx_lustre_file_system#subdirectory DatasyncLocationFsxLustreFileSystem#subdirectory}.'''
        result = self._values.get("subdirectory")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_fsx_lustre_file_system#tags DatasyncLocationFsxLustreFileSystem#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_fsx_lustre_file_system#tags_all DatasyncLocationFsxLustreFileSystem#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatasyncLocationFsxLustreFileSystemConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DatasyncLocationFsxWindowsFileSystem(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.datasync.DatasyncLocationFsxWindowsFileSystem",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_fsx_windows_file_system aws_datasync_location_fsx_windows_file_system}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        fsx_filesystem_arn: builtins.str,
        password: builtins.str,
        security_group_arns: typing.Sequence[builtins.str],
        user: builtins.str,
        domain: typing.Optional[builtins.str] = None,
        subdirectory: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_fsx_windows_file_system aws_datasync_location_fsx_windows_file_system} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param fsx_filesystem_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_fsx_windows_file_system#fsx_filesystem_arn DatasyncLocationFsxWindowsFileSystem#fsx_filesystem_arn}.
        :param password: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_fsx_windows_file_system#password DatasyncLocationFsxWindowsFileSystem#password}.
        :param security_group_arns: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_fsx_windows_file_system#security_group_arns DatasyncLocationFsxWindowsFileSystem#security_group_arns}.
        :param user: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_fsx_windows_file_system#user DatasyncLocationFsxWindowsFileSystem#user}.
        :param domain: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_fsx_windows_file_system#domain DatasyncLocationFsxWindowsFileSystem#domain}.
        :param subdirectory: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_fsx_windows_file_system#subdirectory DatasyncLocationFsxWindowsFileSystem#subdirectory}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_fsx_windows_file_system#tags DatasyncLocationFsxWindowsFileSystem#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_fsx_windows_file_system#tags_all DatasyncLocationFsxWindowsFileSystem#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DatasyncLocationFsxWindowsFileSystemConfig(
            fsx_filesystem_arn=fsx_filesystem_arn,
            password=password,
            security_group_arns=security_group_arns,
            user=user,
            domain=domain,
            subdirectory=subdirectory,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetDomain")
    def reset_domain(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDomain", []))

    @jsii.member(jsii_name="resetSubdirectory")
    def reset_subdirectory(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSubdirectory", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="creationTime")
    def creation_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "creationTime"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="uri")
    def uri(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uri"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainInput")
    def domain_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "domainInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fsxFilesystemArnInput")
    def fsx_filesystem_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fsxFilesystemArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="passwordInput")
    def password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroupArnsInput")
    def security_group_arns_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "securityGroupArnsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subdirectoryInput")
    def subdirectory_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "subdirectoryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAllInput")
    def tags_all_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsAllInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userInput")
    def user_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domain")
    def domain(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "domain"))

    @domain.setter
    def domain(self, value: builtins.str) -> None:
        jsii.set(self, "domain", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fsxFilesystemArn")
    def fsx_filesystem_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fsxFilesystemArn"))

    @fsx_filesystem_arn.setter
    def fsx_filesystem_arn(self, value: builtins.str) -> None:
        jsii.set(self, "fsxFilesystemArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="password")
    def password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "password"))

    @password.setter
    def password(self, value: builtins.str) -> None:
        jsii.set(self, "password", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroupArns")
    def security_group_arns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "securityGroupArns"))

    @security_group_arns.setter
    def security_group_arns(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "securityGroupArns", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subdirectory")
    def subdirectory(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "subdirectory"))

    @subdirectory.setter
    def subdirectory(self, value: builtins.str) -> None:
        jsii.set(self, "subdirectory", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tags"))

    @tags.setter
    def tags(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "tags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAll")
    def tags_all(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsAll"))

    @tags_all.setter
    def tags_all(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "tagsAll", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="user")
    def user(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "user"))

    @user.setter
    def user(self, value: builtins.str) -> None:
        jsii.set(self, "user", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.datasync.DatasyncLocationFsxWindowsFileSystemConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "fsx_filesystem_arn": "fsxFilesystemArn",
        "password": "password",
        "security_group_arns": "securityGroupArns",
        "user": "user",
        "domain": "domain",
        "subdirectory": "subdirectory",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class DatasyncLocationFsxWindowsFileSystemConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        fsx_filesystem_arn: builtins.str,
        password: builtins.str,
        security_group_arns: typing.Sequence[builtins.str],
        user: builtins.str,
        domain: typing.Optional[builtins.str] = None,
        subdirectory: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS DataSync.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param fsx_filesystem_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_fsx_windows_file_system#fsx_filesystem_arn DatasyncLocationFsxWindowsFileSystem#fsx_filesystem_arn}.
        :param password: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_fsx_windows_file_system#password DatasyncLocationFsxWindowsFileSystem#password}.
        :param security_group_arns: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_fsx_windows_file_system#security_group_arns DatasyncLocationFsxWindowsFileSystem#security_group_arns}.
        :param user: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_fsx_windows_file_system#user DatasyncLocationFsxWindowsFileSystem#user}.
        :param domain: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_fsx_windows_file_system#domain DatasyncLocationFsxWindowsFileSystem#domain}.
        :param subdirectory: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_fsx_windows_file_system#subdirectory DatasyncLocationFsxWindowsFileSystem#subdirectory}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_fsx_windows_file_system#tags DatasyncLocationFsxWindowsFileSystem#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_fsx_windows_file_system#tags_all DatasyncLocationFsxWindowsFileSystem#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "fsx_filesystem_arn": fsx_filesystem_arn,
            "password": password,
            "security_group_arns": security_group_arns,
            "user": user,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if domain is not None:
            self._values["domain"] = domain
        if subdirectory is not None:
            self._values["subdirectory"] = subdirectory
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all

    @builtins.property
    def count(self) -> typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def fsx_filesystem_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_fsx_windows_file_system#fsx_filesystem_arn DatasyncLocationFsxWindowsFileSystem#fsx_filesystem_arn}.'''
        result = self._values.get("fsx_filesystem_arn")
        assert result is not None, "Required property 'fsx_filesystem_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def password(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_fsx_windows_file_system#password DatasyncLocationFsxWindowsFileSystem#password}.'''
        result = self._values.get("password")
        assert result is not None, "Required property 'password' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def security_group_arns(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_fsx_windows_file_system#security_group_arns DatasyncLocationFsxWindowsFileSystem#security_group_arns}.'''
        result = self._values.get("security_group_arns")
        assert result is not None, "Required property 'security_group_arns' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def user(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_fsx_windows_file_system#user DatasyncLocationFsxWindowsFileSystem#user}.'''
        result = self._values.get("user")
        assert result is not None, "Required property 'user' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def domain(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_fsx_windows_file_system#domain DatasyncLocationFsxWindowsFileSystem#domain}.'''
        result = self._values.get("domain")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def subdirectory(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_fsx_windows_file_system#subdirectory DatasyncLocationFsxWindowsFileSystem#subdirectory}.'''
        result = self._values.get("subdirectory")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_fsx_windows_file_system#tags DatasyncLocationFsxWindowsFileSystem#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_fsx_windows_file_system#tags_all DatasyncLocationFsxWindowsFileSystem#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatasyncLocationFsxWindowsFileSystemConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DatasyncLocationHdfs(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.datasync.DatasyncLocationHdfs",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_hdfs aws_datasync_location_hdfs}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        agent_arns: typing.Sequence[builtins.str],
        name_node: typing.Sequence["DatasyncLocationHdfsNameNode"],
        authentication_type: typing.Optional[builtins.str] = None,
        block_size: typing.Optional[jsii.Number] = None,
        kerberos_keytab: typing.Optional[builtins.str] = None,
        kerberos_krb5_conf: typing.Optional[builtins.str] = None,
        kerberos_principal: typing.Optional[builtins.str] = None,
        kms_key_provider_uri: typing.Optional[builtins.str] = None,
        qop_configuration: typing.Optional["DatasyncLocationHdfsQopConfiguration"] = None,
        replication_factor: typing.Optional[jsii.Number] = None,
        simple_user: typing.Optional[builtins.str] = None,
        subdirectory: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_hdfs aws_datasync_location_hdfs} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param agent_arns: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_hdfs#agent_arns DatasyncLocationHdfs#agent_arns}.
        :param name_node: name_node block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_hdfs#name_node DatasyncLocationHdfs#name_node}
        :param authentication_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_hdfs#authentication_type DatasyncLocationHdfs#authentication_type}.
        :param block_size: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_hdfs#block_size DatasyncLocationHdfs#block_size}.
        :param kerberos_keytab: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_hdfs#kerberos_keytab DatasyncLocationHdfs#kerberos_keytab}.
        :param kerberos_krb5_conf: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_hdfs#kerberos_krb5_conf DatasyncLocationHdfs#kerberos_krb5_conf}.
        :param kerberos_principal: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_hdfs#kerberos_principal DatasyncLocationHdfs#kerberos_principal}.
        :param kms_key_provider_uri: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_hdfs#kms_key_provider_uri DatasyncLocationHdfs#kms_key_provider_uri}.
        :param qop_configuration: qop_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_hdfs#qop_configuration DatasyncLocationHdfs#qop_configuration}
        :param replication_factor: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_hdfs#replication_factor DatasyncLocationHdfs#replication_factor}.
        :param simple_user: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_hdfs#simple_user DatasyncLocationHdfs#simple_user}.
        :param subdirectory: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_hdfs#subdirectory DatasyncLocationHdfs#subdirectory}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_hdfs#tags DatasyncLocationHdfs#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_hdfs#tags_all DatasyncLocationHdfs#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DatasyncLocationHdfsConfig(
            agent_arns=agent_arns,
            name_node=name_node,
            authentication_type=authentication_type,
            block_size=block_size,
            kerberos_keytab=kerberos_keytab,
            kerberos_krb5_conf=kerberos_krb5_conf,
            kerberos_principal=kerberos_principal,
            kms_key_provider_uri=kms_key_provider_uri,
            qop_configuration=qop_configuration,
            replication_factor=replication_factor,
            simple_user=simple_user,
            subdirectory=subdirectory,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putQopConfiguration")
    def put_qop_configuration(
        self,
        *,
        data_transfer_protection: typing.Optional[builtins.str] = None,
        rpc_protection: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param data_transfer_protection: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_hdfs#data_transfer_protection DatasyncLocationHdfs#data_transfer_protection}.
        :param rpc_protection: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_hdfs#rpc_protection DatasyncLocationHdfs#rpc_protection}.
        '''
        value = DatasyncLocationHdfsQopConfiguration(
            data_transfer_protection=data_transfer_protection,
            rpc_protection=rpc_protection,
        )

        return typing.cast(None, jsii.invoke(self, "putQopConfiguration", [value]))

    @jsii.member(jsii_name="resetAuthenticationType")
    def reset_authentication_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthenticationType", []))

    @jsii.member(jsii_name="resetBlockSize")
    def reset_block_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBlockSize", []))

    @jsii.member(jsii_name="resetKerberosKeytab")
    def reset_kerberos_keytab(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKerberosKeytab", []))

    @jsii.member(jsii_name="resetKerberosKrb5Conf")
    def reset_kerberos_krb5_conf(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKerberosKrb5Conf", []))

    @jsii.member(jsii_name="resetKerberosPrincipal")
    def reset_kerberos_principal(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKerberosPrincipal", []))

    @jsii.member(jsii_name="resetKmsKeyProviderUri")
    def reset_kms_key_provider_uri(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKmsKeyProviderUri", []))

    @jsii.member(jsii_name="resetQopConfiguration")
    def reset_qop_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetQopConfiguration", []))

    @jsii.member(jsii_name="resetReplicationFactor")
    def reset_replication_factor(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReplicationFactor", []))

    @jsii.member(jsii_name="resetSimpleUser")
    def reset_simple_user(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSimpleUser", []))

    @jsii.member(jsii_name="resetSubdirectory")
    def reset_subdirectory(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSubdirectory", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="qopConfiguration")
    def qop_configuration(
        self,
    ) -> "DatasyncLocationHdfsQopConfigurationOutputReference":
        return typing.cast("DatasyncLocationHdfsQopConfigurationOutputReference", jsii.get(self, "qopConfiguration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="uri")
    def uri(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uri"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="agentArnsInput")
    def agent_arns_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "agentArnsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authenticationTypeInput")
    def authentication_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "authenticationTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="blockSizeInput")
    def block_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "blockSizeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kerberosKeytabInput")
    def kerberos_keytab_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kerberosKeytabInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kerberosKrb5ConfInput")
    def kerberos_krb5_conf_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kerberosKrb5ConfInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kerberosPrincipalInput")
    def kerberos_principal_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kerberosPrincipalInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyProviderUriInput")
    def kms_key_provider_uri_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kmsKeyProviderUriInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameNodeInput")
    def name_node_input(
        self,
    ) -> typing.Optional[typing.List["DatasyncLocationHdfsNameNode"]]:
        return typing.cast(typing.Optional[typing.List["DatasyncLocationHdfsNameNode"]], jsii.get(self, "nameNodeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="qopConfigurationInput")
    def qop_configuration_input(
        self,
    ) -> typing.Optional["DatasyncLocationHdfsQopConfiguration"]:
        return typing.cast(typing.Optional["DatasyncLocationHdfsQopConfiguration"], jsii.get(self, "qopConfigurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicationFactorInput")
    def replication_factor_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "replicationFactorInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="simpleUserInput")
    def simple_user_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "simpleUserInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subdirectoryInput")
    def subdirectory_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "subdirectoryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAllInput")
    def tags_all_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsAllInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="agentArns")
    def agent_arns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "agentArns"))

    @agent_arns.setter
    def agent_arns(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "agentArns", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authenticationType")
    def authentication_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authenticationType"))

    @authentication_type.setter
    def authentication_type(self, value: builtins.str) -> None:
        jsii.set(self, "authenticationType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="blockSize")
    def block_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "blockSize"))

    @block_size.setter
    def block_size(self, value: jsii.Number) -> None:
        jsii.set(self, "blockSize", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kerberosKeytab")
    def kerberos_keytab(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kerberosKeytab"))

    @kerberos_keytab.setter
    def kerberos_keytab(self, value: builtins.str) -> None:
        jsii.set(self, "kerberosKeytab", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kerberosKrb5Conf")
    def kerberos_krb5_conf(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kerberosKrb5Conf"))

    @kerberos_krb5_conf.setter
    def kerberos_krb5_conf(self, value: builtins.str) -> None:
        jsii.set(self, "kerberosKrb5Conf", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kerberosPrincipal")
    def kerberos_principal(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kerberosPrincipal"))

    @kerberos_principal.setter
    def kerberos_principal(self, value: builtins.str) -> None:
        jsii.set(self, "kerberosPrincipal", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyProviderUri")
    def kms_key_provider_uri(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsKeyProviderUri"))

    @kms_key_provider_uri.setter
    def kms_key_provider_uri(self, value: builtins.str) -> None:
        jsii.set(self, "kmsKeyProviderUri", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameNode")
    def name_node(self) -> typing.List["DatasyncLocationHdfsNameNode"]:
        return typing.cast(typing.List["DatasyncLocationHdfsNameNode"], jsii.get(self, "nameNode"))

    @name_node.setter
    def name_node(self, value: typing.List["DatasyncLocationHdfsNameNode"]) -> None:
        jsii.set(self, "nameNode", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicationFactor")
    def replication_factor(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "replicationFactor"))

    @replication_factor.setter
    def replication_factor(self, value: jsii.Number) -> None:
        jsii.set(self, "replicationFactor", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="simpleUser")
    def simple_user(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "simpleUser"))

    @simple_user.setter
    def simple_user(self, value: builtins.str) -> None:
        jsii.set(self, "simpleUser", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subdirectory")
    def subdirectory(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "subdirectory"))

    @subdirectory.setter
    def subdirectory(self, value: builtins.str) -> None:
        jsii.set(self, "subdirectory", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tags"))

    @tags.setter
    def tags(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "tags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAll")
    def tags_all(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsAll"))

    @tags_all.setter
    def tags_all(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "tagsAll", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.datasync.DatasyncLocationHdfsConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "agent_arns": "agentArns",
        "name_node": "nameNode",
        "authentication_type": "authenticationType",
        "block_size": "blockSize",
        "kerberos_keytab": "kerberosKeytab",
        "kerberos_krb5_conf": "kerberosKrb5Conf",
        "kerberos_principal": "kerberosPrincipal",
        "kms_key_provider_uri": "kmsKeyProviderUri",
        "qop_configuration": "qopConfiguration",
        "replication_factor": "replicationFactor",
        "simple_user": "simpleUser",
        "subdirectory": "subdirectory",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class DatasyncLocationHdfsConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        agent_arns: typing.Sequence[builtins.str],
        name_node: typing.Sequence["DatasyncLocationHdfsNameNode"],
        authentication_type: typing.Optional[builtins.str] = None,
        block_size: typing.Optional[jsii.Number] = None,
        kerberos_keytab: typing.Optional[builtins.str] = None,
        kerberos_krb5_conf: typing.Optional[builtins.str] = None,
        kerberos_principal: typing.Optional[builtins.str] = None,
        kms_key_provider_uri: typing.Optional[builtins.str] = None,
        qop_configuration: typing.Optional["DatasyncLocationHdfsQopConfiguration"] = None,
        replication_factor: typing.Optional[jsii.Number] = None,
        simple_user: typing.Optional[builtins.str] = None,
        subdirectory: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS DataSync.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param agent_arns: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_hdfs#agent_arns DatasyncLocationHdfs#agent_arns}.
        :param name_node: name_node block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_hdfs#name_node DatasyncLocationHdfs#name_node}
        :param authentication_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_hdfs#authentication_type DatasyncLocationHdfs#authentication_type}.
        :param block_size: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_hdfs#block_size DatasyncLocationHdfs#block_size}.
        :param kerberos_keytab: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_hdfs#kerberos_keytab DatasyncLocationHdfs#kerberos_keytab}.
        :param kerberos_krb5_conf: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_hdfs#kerberos_krb5_conf DatasyncLocationHdfs#kerberos_krb5_conf}.
        :param kerberos_principal: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_hdfs#kerberos_principal DatasyncLocationHdfs#kerberos_principal}.
        :param kms_key_provider_uri: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_hdfs#kms_key_provider_uri DatasyncLocationHdfs#kms_key_provider_uri}.
        :param qop_configuration: qop_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_hdfs#qop_configuration DatasyncLocationHdfs#qop_configuration}
        :param replication_factor: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_hdfs#replication_factor DatasyncLocationHdfs#replication_factor}.
        :param simple_user: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_hdfs#simple_user DatasyncLocationHdfs#simple_user}.
        :param subdirectory: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_hdfs#subdirectory DatasyncLocationHdfs#subdirectory}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_hdfs#tags DatasyncLocationHdfs#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_hdfs#tags_all DatasyncLocationHdfs#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(qop_configuration, dict):
            qop_configuration = DatasyncLocationHdfsQopConfiguration(**qop_configuration)
        self._values: typing.Dict[str, typing.Any] = {
            "agent_arns": agent_arns,
            "name_node": name_node,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if authentication_type is not None:
            self._values["authentication_type"] = authentication_type
        if block_size is not None:
            self._values["block_size"] = block_size
        if kerberos_keytab is not None:
            self._values["kerberos_keytab"] = kerberos_keytab
        if kerberos_krb5_conf is not None:
            self._values["kerberos_krb5_conf"] = kerberos_krb5_conf
        if kerberos_principal is not None:
            self._values["kerberos_principal"] = kerberos_principal
        if kms_key_provider_uri is not None:
            self._values["kms_key_provider_uri"] = kms_key_provider_uri
        if qop_configuration is not None:
            self._values["qop_configuration"] = qop_configuration
        if replication_factor is not None:
            self._values["replication_factor"] = replication_factor
        if simple_user is not None:
            self._values["simple_user"] = simple_user
        if subdirectory is not None:
            self._values["subdirectory"] = subdirectory
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all

    @builtins.property
    def count(self) -> typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def agent_arns(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_hdfs#agent_arns DatasyncLocationHdfs#agent_arns}.'''
        result = self._values.get("agent_arns")
        assert result is not None, "Required property 'agent_arns' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def name_node(self) -> typing.List["DatasyncLocationHdfsNameNode"]:
        '''name_node block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_hdfs#name_node DatasyncLocationHdfs#name_node}
        '''
        result = self._values.get("name_node")
        assert result is not None, "Required property 'name_node' is missing"
        return typing.cast(typing.List["DatasyncLocationHdfsNameNode"], result)

    @builtins.property
    def authentication_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_hdfs#authentication_type DatasyncLocationHdfs#authentication_type}.'''
        result = self._values.get("authentication_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def block_size(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_hdfs#block_size DatasyncLocationHdfs#block_size}.'''
        result = self._values.get("block_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def kerberos_keytab(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_hdfs#kerberos_keytab DatasyncLocationHdfs#kerberos_keytab}.'''
        result = self._values.get("kerberos_keytab")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def kerberos_krb5_conf(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_hdfs#kerberos_krb5_conf DatasyncLocationHdfs#kerberos_krb5_conf}.'''
        result = self._values.get("kerberos_krb5_conf")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def kerberos_principal(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_hdfs#kerberos_principal DatasyncLocationHdfs#kerberos_principal}.'''
        result = self._values.get("kerberos_principal")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def kms_key_provider_uri(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_hdfs#kms_key_provider_uri DatasyncLocationHdfs#kms_key_provider_uri}.'''
        result = self._values.get("kms_key_provider_uri")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def qop_configuration(
        self,
    ) -> typing.Optional["DatasyncLocationHdfsQopConfiguration"]:
        '''qop_configuration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_hdfs#qop_configuration DatasyncLocationHdfs#qop_configuration}
        '''
        result = self._values.get("qop_configuration")
        return typing.cast(typing.Optional["DatasyncLocationHdfsQopConfiguration"], result)

    @builtins.property
    def replication_factor(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_hdfs#replication_factor DatasyncLocationHdfs#replication_factor}.'''
        result = self._values.get("replication_factor")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def simple_user(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_hdfs#simple_user DatasyncLocationHdfs#simple_user}.'''
        result = self._values.get("simple_user")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def subdirectory(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_hdfs#subdirectory DatasyncLocationHdfs#subdirectory}.'''
        result = self._values.get("subdirectory")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_hdfs#tags DatasyncLocationHdfs#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_hdfs#tags_all DatasyncLocationHdfs#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatasyncLocationHdfsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.datasync.DatasyncLocationHdfsNameNode",
    jsii_struct_bases=[],
    name_mapping={"hostname": "hostname", "port": "port"},
)
class DatasyncLocationHdfsNameNode:
    def __init__(self, *, hostname: builtins.str, port: jsii.Number) -> None:
        '''
        :param hostname: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_hdfs#hostname DatasyncLocationHdfs#hostname}.
        :param port: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_hdfs#port DatasyncLocationHdfs#port}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "hostname": hostname,
            "port": port,
        }

    @builtins.property
    def hostname(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_hdfs#hostname DatasyncLocationHdfs#hostname}.'''
        result = self._values.get("hostname")
        assert result is not None, "Required property 'hostname' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def port(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_hdfs#port DatasyncLocationHdfs#port}.'''
        result = self._values.get("port")
        assert result is not None, "Required property 'port' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatasyncLocationHdfsNameNode(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.datasync.DatasyncLocationHdfsQopConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "data_transfer_protection": "dataTransferProtection",
        "rpc_protection": "rpcProtection",
    },
)
class DatasyncLocationHdfsQopConfiguration:
    def __init__(
        self,
        *,
        data_transfer_protection: typing.Optional[builtins.str] = None,
        rpc_protection: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param data_transfer_protection: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_hdfs#data_transfer_protection DatasyncLocationHdfs#data_transfer_protection}.
        :param rpc_protection: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_hdfs#rpc_protection DatasyncLocationHdfs#rpc_protection}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if data_transfer_protection is not None:
            self._values["data_transfer_protection"] = data_transfer_protection
        if rpc_protection is not None:
            self._values["rpc_protection"] = rpc_protection

    @builtins.property
    def data_transfer_protection(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_hdfs#data_transfer_protection DatasyncLocationHdfs#data_transfer_protection}.'''
        result = self._values.get("data_transfer_protection")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rpc_protection(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_hdfs#rpc_protection DatasyncLocationHdfs#rpc_protection}.'''
        result = self._values.get("rpc_protection")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatasyncLocationHdfsQopConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DatasyncLocationHdfsQopConfigurationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.datasync.DatasyncLocationHdfsQopConfigurationOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetDataTransferProtection")
    def reset_data_transfer_protection(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDataTransferProtection", []))

    @jsii.member(jsii_name="resetRpcProtection")
    def reset_rpc_protection(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRpcProtection", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dataTransferProtectionInput")
    def data_transfer_protection_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dataTransferProtectionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rpcProtectionInput")
    def rpc_protection_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rpcProtectionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dataTransferProtection")
    def data_transfer_protection(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dataTransferProtection"))

    @data_transfer_protection.setter
    def data_transfer_protection(self, value: builtins.str) -> None:
        jsii.set(self, "dataTransferProtection", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rpcProtection")
    def rpc_protection(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rpcProtection"))

    @rpc_protection.setter
    def rpc_protection(self, value: builtins.str) -> None:
        jsii.set(self, "rpcProtection", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DatasyncLocationHdfsQopConfiguration]:
        return typing.cast(typing.Optional[DatasyncLocationHdfsQopConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DatasyncLocationHdfsQopConfiguration],
    ) -> None:
        jsii.set(self, "internalValue", value)


class DatasyncLocationNfs(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.datasync.DatasyncLocationNfs",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_nfs aws_datasync_location_nfs}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        on_prem_config: "DatasyncLocationNfsOnPremConfig",
        server_hostname: builtins.str,
        subdirectory: builtins.str,
        mount_options: typing.Optional["DatasyncLocationNfsMountOptions"] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_nfs aws_datasync_location_nfs} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param on_prem_config: on_prem_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_nfs#on_prem_config DatasyncLocationNfs#on_prem_config}
        :param server_hostname: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_nfs#server_hostname DatasyncLocationNfs#server_hostname}.
        :param subdirectory: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_nfs#subdirectory DatasyncLocationNfs#subdirectory}.
        :param mount_options: mount_options block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_nfs#mount_options DatasyncLocationNfs#mount_options}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_nfs#tags DatasyncLocationNfs#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_nfs#tags_all DatasyncLocationNfs#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DatasyncLocationNfsConfig(
            on_prem_config=on_prem_config,
            server_hostname=server_hostname,
            subdirectory=subdirectory,
            mount_options=mount_options,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putMountOptions")
    def put_mount_options(
        self,
        *,
        version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_nfs#version DatasyncLocationNfs#version}.
        '''
        value = DatasyncLocationNfsMountOptions(version=version)

        return typing.cast(None, jsii.invoke(self, "putMountOptions", [value]))

    @jsii.member(jsii_name="putOnPremConfig")
    def put_on_prem_config(self, *, agent_arns: typing.Sequence[builtins.str]) -> None:
        '''
        :param agent_arns: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_nfs#agent_arns DatasyncLocationNfs#agent_arns}.
        '''
        value = DatasyncLocationNfsOnPremConfig(agent_arns=agent_arns)

        return typing.cast(None, jsii.invoke(self, "putOnPremConfig", [value]))

    @jsii.member(jsii_name="resetMountOptions")
    def reset_mount_options(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMountOptions", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mountOptions")
    def mount_options(self) -> "DatasyncLocationNfsMountOptionsOutputReference":
        return typing.cast("DatasyncLocationNfsMountOptionsOutputReference", jsii.get(self, "mountOptions"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="onPremConfig")
    def on_prem_config(self) -> "DatasyncLocationNfsOnPremConfigOutputReference":
        return typing.cast("DatasyncLocationNfsOnPremConfigOutputReference", jsii.get(self, "onPremConfig"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="uri")
    def uri(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uri"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mountOptionsInput")
    def mount_options_input(self) -> typing.Optional["DatasyncLocationNfsMountOptions"]:
        return typing.cast(typing.Optional["DatasyncLocationNfsMountOptions"], jsii.get(self, "mountOptionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="onPremConfigInput")
    def on_prem_config_input(
        self,
    ) -> typing.Optional["DatasyncLocationNfsOnPremConfig"]:
        return typing.cast(typing.Optional["DatasyncLocationNfsOnPremConfig"], jsii.get(self, "onPremConfigInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serverHostnameInput")
    def server_hostname_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serverHostnameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subdirectoryInput")
    def subdirectory_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "subdirectoryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAllInput")
    def tags_all_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsAllInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serverHostname")
    def server_hostname(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serverHostname"))

    @server_hostname.setter
    def server_hostname(self, value: builtins.str) -> None:
        jsii.set(self, "serverHostname", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subdirectory")
    def subdirectory(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "subdirectory"))

    @subdirectory.setter
    def subdirectory(self, value: builtins.str) -> None:
        jsii.set(self, "subdirectory", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tags"))

    @tags.setter
    def tags(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "tags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAll")
    def tags_all(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsAll"))

    @tags_all.setter
    def tags_all(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "tagsAll", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.datasync.DatasyncLocationNfsConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "on_prem_config": "onPremConfig",
        "server_hostname": "serverHostname",
        "subdirectory": "subdirectory",
        "mount_options": "mountOptions",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class DatasyncLocationNfsConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        on_prem_config: "DatasyncLocationNfsOnPremConfig",
        server_hostname: builtins.str,
        subdirectory: builtins.str,
        mount_options: typing.Optional["DatasyncLocationNfsMountOptions"] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS DataSync.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param on_prem_config: on_prem_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_nfs#on_prem_config DatasyncLocationNfs#on_prem_config}
        :param server_hostname: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_nfs#server_hostname DatasyncLocationNfs#server_hostname}.
        :param subdirectory: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_nfs#subdirectory DatasyncLocationNfs#subdirectory}.
        :param mount_options: mount_options block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_nfs#mount_options DatasyncLocationNfs#mount_options}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_nfs#tags DatasyncLocationNfs#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_nfs#tags_all DatasyncLocationNfs#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(on_prem_config, dict):
            on_prem_config = DatasyncLocationNfsOnPremConfig(**on_prem_config)
        if isinstance(mount_options, dict):
            mount_options = DatasyncLocationNfsMountOptions(**mount_options)
        self._values: typing.Dict[str, typing.Any] = {
            "on_prem_config": on_prem_config,
            "server_hostname": server_hostname,
            "subdirectory": subdirectory,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if mount_options is not None:
            self._values["mount_options"] = mount_options
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all

    @builtins.property
    def count(self) -> typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def on_prem_config(self) -> "DatasyncLocationNfsOnPremConfig":
        '''on_prem_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_nfs#on_prem_config DatasyncLocationNfs#on_prem_config}
        '''
        result = self._values.get("on_prem_config")
        assert result is not None, "Required property 'on_prem_config' is missing"
        return typing.cast("DatasyncLocationNfsOnPremConfig", result)

    @builtins.property
    def server_hostname(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_nfs#server_hostname DatasyncLocationNfs#server_hostname}.'''
        result = self._values.get("server_hostname")
        assert result is not None, "Required property 'server_hostname' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def subdirectory(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_nfs#subdirectory DatasyncLocationNfs#subdirectory}.'''
        result = self._values.get("subdirectory")
        assert result is not None, "Required property 'subdirectory' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def mount_options(self) -> typing.Optional["DatasyncLocationNfsMountOptions"]:
        '''mount_options block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_nfs#mount_options DatasyncLocationNfs#mount_options}
        '''
        result = self._values.get("mount_options")
        return typing.cast(typing.Optional["DatasyncLocationNfsMountOptions"], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_nfs#tags DatasyncLocationNfs#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_nfs#tags_all DatasyncLocationNfs#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatasyncLocationNfsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.datasync.DatasyncLocationNfsMountOptions",
    jsii_struct_bases=[],
    name_mapping={"version": "version"},
)
class DatasyncLocationNfsMountOptions:
    def __init__(self, *, version: typing.Optional[builtins.str] = None) -> None:
        '''
        :param version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_nfs#version DatasyncLocationNfs#version}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if version is not None:
            self._values["version"] = version

    @builtins.property
    def version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_nfs#version DatasyncLocationNfs#version}.'''
        result = self._values.get("version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatasyncLocationNfsMountOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DatasyncLocationNfsMountOptionsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.datasync.DatasyncLocationNfsMountOptionsOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetVersion")
    def reset_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVersion", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="versionInput")
    def version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "versionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @version.setter
    def version(self, value: builtins.str) -> None:
        jsii.set(self, "version", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DatasyncLocationNfsMountOptions]:
        return typing.cast(typing.Optional[DatasyncLocationNfsMountOptions], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DatasyncLocationNfsMountOptions],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.datasync.DatasyncLocationNfsOnPremConfig",
    jsii_struct_bases=[],
    name_mapping={"agent_arns": "agentArns"},
)
class DatasyncLocationNfsOnPremConfig:
    def __init__(self, *, agent_arns: typing.Sequence[builtins.str]) -> None:
        '''
        :param agent_arns: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_nfs#agent_arns DatasyncLocationNfs#agent_arns}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "agent_arns": agent_arns,
        }

    @builtins.property
    def agent_arns(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_nfs#agent_arns DatasyncLocationNfs#agent_arns}.'''
        result = self._values.get("agent_arns")
        assert result is not None, "Required property 'agent_arns' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatasyncLocationNfsOnPremConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DatasyncLocationNfsOnPremConfigOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.datasync.DatasyncLocationNfsOnPremConfigOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="agentArnsInput")
    def agent_arns_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "agentArnsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="agentArns")
    def agent_arns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "agentArns"))

    @agent_arns.setter
    def agent_arns(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "agentArns", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DatasyncLocationNfsOnPremConfig]:
        return typing.cast(typing.Optional[DatasyncLocationNfsOnPremConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DatasyncLocationNfsOnPremConfig],
    ) -> None:
        jsii.set(self, "internalValue", value)


class DatasyncLocationS3(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.datasync.DatasyncLocationS3",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_s3 aws_datasync_location_s3}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        s3_bucket_arn: builtins.str,
        s3_config: "DatasyncLocationS3S3Config",
        subdirectory: builtins.str,
        agent_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        s3_storage_class: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_s3 aws_datasync_location_s3} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param s3_bucket_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_s3#s3_bucket_arn DatasyncLocationS3#s3_bucket_arn}.
        :param s3_config: s3_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_s3#s3_config DatasyncLocationS3#s3_config}
        :param subdirectory: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_s3#subdirectory DatasyncLocationS3#subdirectory}.
        :param agent_arns: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_s3#agent_arns DatasyncLocationS3#agent_arns}.
        :param s3_storage_class: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_s3#s3_storage_class DatasyncLocationS3#s3_storage_class}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_s3#tags DatasyncLocationS3#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_s3#tags_all DatasyncLocationS3#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DatasyncLocationS3Config(
            s3_bucket_arn=s3_bucket_arn,
            s3_config=s3_config,
            subdirectory=subdirectory,
            agent_arns=agent_arns,
            s3_storage_class=s3_storage_class,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putS3Config")
    def put_s3_config(self, *, bucket_access_role_arn: builtins.str) -> None:
        '''
        :param bucket_access_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_s3#bucket_access_role_arn DatasyncLocationS3#bucket_access_role_arn}.
        '''
        value = DatasyncLocationS3S3Config(
            bucket_access_role_arn=bucket_access_role_arn
        )

        return typing.cast(None, jsii.invoke(self, "putS3Config", [value]))

    @jsii.member(jsii_name="resetAgentArns")
    def reset_agent_arns(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAgentArns", []))

    @jsii.member(jsii_name="resetS3StorageClass")
    def reset_s3_storage_class(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetS3StorageClass", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3Config")
    def s3_config(self) -> "DatasyncLocationS3S3ConfigOutputReference":
        return typing.cast("DatasyncLocationS3S3ConfigOutputReference", jsii.get(self, "s3Config"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="uri")
    def uri(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uri"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="agentArnsInput")
    def agent_arns_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "agentArnsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3BucketArnInput")
    def s3_bucket_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "s3BucketArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3ConfigInput")
    def s3_config_input(self) -> typing.Optional["DatasyncLocationS3S3Config"]:
        return typing.cast(typing.Optional["DatasyncLocationS3S3Config"], jsii.get(self, "s3ConfigInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3StorageClassInput")
    def s3_storage_class_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "s3StorageClassInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subdirectoryInput")
    def subdirectory_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "subdirectoryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAllInput")
    def tags_all_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsAllInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="agentArns")
    def agent_arns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "agentArns"))

    @agent_arns.setter
    def agent_arns(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "agentArns", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3BucketArn")
    def s3_bucket_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "s3BucketArn"))

    @s3_bucket_arn.setter
    def s3_bucket_arn(self, value: builtins.str) -> None:
        jsii.set(self, "s3BucketArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3StorageClass")
    def s3_storage_class(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "s3StorageClass"))

    @s3_storage_class.setter
    def s3_storage_class(self, value: builtins.str) -> None:
        jsii.set(self, "s3StorageClass", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subdirectory")
    def subdirectory(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "subdirectory"))

    @subdirectory.setter
    def subdirectory(self, value: builtins.str) -> None:
        jsii.set(self, "subdirectory", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tags"))

    @tags.setter
    def tags(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "tags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAll")
    def tags_all(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsAll"))

    @tags_all.setter
    def tags_all(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "tagsAll", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.datasync.DatasyncLocationS3Config",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "s3_bucket_arn": "s3BucketArn",
        "s3_config": "s3Config",
        "subdirectory": "subdirectory",
        "agent_arns": "agentArns",
        "s3_storage_class": "s3StorageClass",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class DatasyncLocationS3Config(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        s3_bucket_arn: builtins.str,
        s3_config: "DatasyncLocationS3S3Config",
        subdirectory: builtins.str,
        agent_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        s3_storage_class: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS DataSync.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param s3_bucket_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_s3#s3_bucket_arn DatasyncLocationS3#s3_bucket_arn}.
        :param s3_config: s3_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_s3#s3_config DatasyncLocationS3#s3_config}
        :param subdirectory: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_s3#subdirectory DatasyncLocationS3#subdirectory}.
        :param agent_arns: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_s3#agent_arns DatasyncLocationS3#agent_arns}.
        :param s3_storage_class: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_s3#s3_storage_class DatasyncLocationS3#s3_storage_class}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_s3#tags DatasyncLocationS3#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_s3#tags_all DatasyncLocationS3#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(s3_config, dict):
            s3_config = DatasyncLocationS3S3Config(**s3_config)
        self._values: typing.Dict[str, typing.Any] = {
            "s3_bucket_arn": s3_bucket_arn,
            "s3_config": s3_config,
            "subdirectory": subdirectory,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if agent_arns is not None:
            self._values["agent_arns"] = agent_arns
        if s3_storage_class is not None:
            self._values["s3_storage_class"] = s3_storage_class
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all

    @builtins.property
    def count(self) -> typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def s3_bucket_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_s3#s3_bucket_arn DatasyncLocationS3#s3_bucket_arn}.'''
        result = self._values.get("s3_bucket_arn")
        assert result is not None, "Required property 's3_bucket_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def s3_config(self) -> "DatasyncLocationS3S3Config":
        '''s3_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_s3#s3_config DatasyncLocationS3#s3_config}
        '''
        result = self._values.get("s3_config")
        assert result is not None, "Required property 's3_config' is missing"
        return typing.cast("DatasyncLocationS3S3Config", result)

    @builtins.property
    def subdirectory(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_s3#subdirectory DatasyncLocationS3#subdirectory}.'''
        result = self._values.get("subdirectory")
        assert result is not None, "Required property 'subdirectory' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def agent_arns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_s3#agent_arns DatasyncLocationS3#agent_arns}.'''
        result = self._values.get("agent_arns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def s3_storage_class(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_s3#s3_storage_class DatasyncLocationS3#s3_storage_class}.'''
        result = self._values.get("s3_storage_class")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_s3#tags DatasyncLocationS3#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_s3#tags_all DatasyncLocationS3#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatasyncLocationS3Config(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.datasync.DatasyncLocationS3S3Config",
    jsii_struct_bases=[],
    name_mapping={"bucket_access_role_arn": "bucketAccessRoleArn"},
)
class DatasyncLocationS3S3Config:
    def __init__(self, *, bucket_access_role_arn: builtins.str) -> None:
        '''
        :param bucket_access_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_s3#bucket_access_role_arn DatasyncLocationS3#bucket_access_role_arn}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "bucket_access_role_arn": bucket_access_role_arn,
        }

    @builtins.property
    def bucket_access_role_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_s3#bucket_access_role_arn DatasyncLocationS3#bucket_access_role_arn}.'''
        result = self._values.get("bucket_access_role_arn")
        assert result is not None, "Required property 'bucket_access_role_arn' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatasyncLocationS3S3Config(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DatasyncLocationS3S3ConfigOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.datasync.DatasyncLocationS3S3ConfigOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketAccessRoleArnInput")
    def bucket_access_role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bucketAccessRoleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketAccessRoleArn")
    def bucket_access_role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucketAccessRoleArn"))

    @bucket_access_role_arn.setter
    def bucket_access_role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "bucketAccessRoleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DatasyncLocationS3S3Config]:
        return typing.cast(typing.Optional[DatasyncLocationS3S3Config], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DatasyncLocationS3S3Config],
    ) -> None:
        jsii.set(self, "internalValue", value)


class DatasyncLocationSmb(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.datasync.DatasyncLocationSmb",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_smb aws_datasync_location_smb}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        agent_arns: typing.Sequence[builtins.str],
        password: builtins.str,
        server_hostname: builtins.str,
        subdirectory: builtins.str,
        user: builtins.str,
        domain: typing.Optional[builtins.str] = None,
        mount_options: typing.Optional["DatasyncLocationSmbMountOptions"] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_smb aws_datasync_location_smb} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param agent_arns: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_smb#agent_arns DatasyncLocationSmb#agent_arns}.
        :param password: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_smb#password DatasyncLocationSmb#password}.
        :param server_hostname: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_smb#server_hostname DatasyncLocationSmb#server_hostname}.
        :param subdirectory: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_smb#subdirectory DatasyncLocationSmb#subdirectory}.
        :param user: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_smb#user DatasyncLocationSmb#user}.
        :param domain: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_smb#domain DatasyncLocationSmb#domain}.
        :param mount_options: mount_options block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_smb#mount_options DatasyncLocationSmb#mount_options}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_smb#tags DatasyncLocationSmb#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_smb#tags_all DatasyncLocationSmb#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DatasyncLocationSmbConfig(
            agent_arns=agent_arns,
            password=password,
            server_hostname=server_hostname,
            subdirectory=subdirectory,
            user=user,
            domain=domain,
            mount_options=mount_options,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putMountOptions")
    def put_mount_options(
        self,
        *,
        version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_smb#version DatasyncLocationSmb#version}.
        '''
        value = DatasyncLocationSmbMountOptions(version=version)

        return typing.cast(None, jsii.invoke(self, "putMountOptions", [value]))

    @jsii.member(jsii_name="resetDomain")
    def reset_domain(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDomain", []))

    @jsii.member(jsii_name="resetMountOptions")
    def reset_mount_options(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMountOptions", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mountOptions")
    def mount_options(self) -> "DatasyncLocationSmbMountOptionsOutputReference":
        return typing.cast("DatasyncLocationSmbMountOptionsOutputReference", jsii.get(self, "mountOptions"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="uri")
    def uri(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uri"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="agentArnsInput")
    def agent_arns_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "agentArnsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainInput")
    def domain_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "domainInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mountOptionsInput")
    def mount_options_input(self) -> typing.Optional["DatasyncLocationSmbMountOptions"]:
        return typing.cast(typing.Optional["DatasyncLocationSmbMountOptions"], jsii.get(self, "mountOptionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="passwordInput")
    def password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serverHostnameInput")
    def server_hostname_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serverHostnameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subdirectoryInput")
    def subdirectory_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "subdirectoryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAllInput")
    def tags_all_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsAllInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userInput")
    def user_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="agentArns")
    def agent_arns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "agentArns"))

    @agent_arns.setter
    def agent_arns(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "agentArns", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domain")
    def domain(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "domain"))

    @domain.setter
    def domain(self, value: builtins.str) -> None:
        jsii.set(self, "domain", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="password")
    def password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "password"))

    @password.setter
    def password(self, value: builtins.str) -> None:
        jsii.set(self, "password", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serverHostname")
    def server_hostname(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serverHostname"))

    @server_hostname.setter
    def server_hostname(self, value: builtins.str) -> None:
        jsii.set(self, "serverHostname", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subdirectory")
    def subdirectory(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "subdirectory"))

    @subdirectory.setter
    def subdirectory(self, value: builtins.str) -> None:
        jsii.set(self, "subdirectory", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tags"))

    @tags.setter
    def tags(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "tags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAll")
    def tags_all(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsAll"))

    @tags_all.setter
    def tags_all(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "tagsAll", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="user")
    def user(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "user"))

    @user.setter
    def user(self, value: builtins.str) -> None:
        jsii.set(self, "user", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.datasync.DatasyncLocationSmbConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "agent_arns": "agentArns",
        "password": "password",
        "server_hostname": "serverHostname",
        "subdirectory": "subdirectory",
        "user": "user",
        "domain": "domain",
        "mount_options": "mountOptions",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class DatasyncLocationSmbConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        agent_arns: typing.Sequence[builtins.str],
        password: builtins.str,
        server_hostname: builtins.str,
        subdirectory: builtins.str,
        user: builtins.str,
        domain: typing.Optional[builtins.str] = None,
        mount_options: typing.Optional["DatasyncLocationSmbMountOptions"] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS DataSync.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param agent_arns: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_smb#agent_arns DatasyncLocationSmb#agent_arns}.
        :param password: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_smb#password DatasyncLocationSmb#password}.
        :param server_hostname: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_smb#server_hostname DatasyncLocationSmb#server_hostname}.
        :param subdirectory: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_smb#subdirectory DatasyncLocationSmb#subdirectory}.
        :param user: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_smb#user DatasyncLocationSmb#user}.
        :param domain: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_smb#domain DatasyncLocationSmb#domain}.
        :param mount_options: mount_options block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_smb#mount_options DatasyncLocationSmb#mount_options}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_smb#tags DatasyncLocationSmb#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_smb#tags_all DatasyncLocationSmb#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(mount_options, dict):
            mount_options = DatasyncLocationSmbMountOptions(**mount_options)
        self._values: typing.Dict[str, typing.Any] = {
            "agent_arns": agent_arns,
            "password": password,
            "server_hostname": server_hostname,
            "subdirectory": subdirectory,
            "user": user,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if domain is not None:
            self._values["domain"] = domain
        if mount_options is not None:
            self._values["mount_options"] = mount_options
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all

    @builtins.property
    def count(self) -> typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def agent_arns(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_smb#agent_arns DatasyncLocationSmb#agent_arns}.'''
        result = self._values.get("agent_arns")
        assert result is not None, "Required property 'agent_arns' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def password(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_smb#password DatasyncLocationSmb#password}.'''
        result = self._values.get("password")
        assert result is not None, "Required property 'password' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def server_hostname(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_smb#server_hostname DatasyncLocationSmb#server_hostname}.'''
        result = self._values.get("server_hostname")
        assert result is not None, "Required property 'server_hostname' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def subdirectory(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_smb#subdirectory DatasyncLocationSmb#subdirectory}.'''
        result = self._values.get("subdirectory")
        assert result is not None, "Required property 'subdirectory' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def user(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_smb#user DatasyncLocationSmb#user}.'''
        result = self._values.get("user")
        assert result is not None, "Required property 'user' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def domain(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_smb#domain DatasyncLocationSmb#domain}.'''
        result = self._values.get("domain")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mount_options(self) -> typing.Optional["DatasyncLocationSmbMountOptions"]:
        '''mount_options block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_smb#mount_options DatasyncLocationSmb#mount_options}
        '''
        result = self._values.get("mount_options")
        return typing.cast(typing.Optional["DatasyncLocationSmbMountOptions"], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_smb#tags DatasyncLocationSmb#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_smb#tags_all DatasyncLocationSmb#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatasyncLocationSmbConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.datasync.DatasyncLocationSmbMountOptions",
    jsii_struct_bases=[],
    name_mapping={"version": "version"},
)
class DatasyncLocationSmbMountOptions:
    def __init__(self, *, version: typing.Optional[builtins.str] = None) -> None:
        '''
        :param version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_smb#version DatasyncLocationSmb#version}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if version is not None:
            self._values["version"] = version

    @builtins.property
    def version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_location_smb#version DatasyncLocationSmb#version}.'''
        result = self._values.get("version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatasyncLocationSmbMountOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DatasyncLocationSmbMountOptionsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.datasync.DatasyncLocationSmbMountOptionsOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetVersion")
    def reset_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVersion", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="versionInput")
    def version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "versionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @version.setter
    def version(self, value: builtins.str) -> None:
        jsii.set(self, "version", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DatasyncLocationSmbMountOptions]:
        return typing.cast(typing.Optional[DatasyncLocationSmbMountOptions], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DatasyncLocationSmbMountOptions],
    ) -> None:
        jsii.set(self, "internalValue", value)


class DatasyncTask(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.datasync.DatasyncTask",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/datasync_task aws_datasync_task}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        destination_location_arn: builtins.str,
        source_location_arn: builtins.str,
        cloudwatch_log_group_arn: typing.Optional[builtins.str] = None,
        excludes: typing.Optional["DatasyncTaskExcludes"] = None,
        name: typing.Optional[builtins.str] = None,
        options: typing.Optional["DatasyncTaskOptions"] = None,
        schedule: typing.Optional["DatasyncTaskSchedule"] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["DatasyncTaskTimeouts"] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/datasync_task aws_datasync_task} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param destination_location_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#destination_location_arn DatasyncTask#destination_location_arn}.
        :param source_location_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#source_location_arn DatasyncTask#source_location_arn}.
        :param cloudwatch_log_group_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#cloudwatch_log_group_arn DatasyncTask#cloudwatch_log_group_arn}.
        :param excludes: excludes block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#excludes DatasyncTask#excludes}
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#name DatasyncTask#name}.
        :param options: options block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#options DatasyncTask#options}
        :param schedule: schedule block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#schedule DatasyncTask#schedule}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#tags DatasyncTask#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#tags_all DatasyncTask#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#timeouts DatasyncTask#timeouts}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DatasyncTaskConfig(
            destination_location_arn=destination_location_arn,
            source_location_arn=source_location_arn,
            cloudwatch_log_group_arn=cloudwatch_log_group_arn,
            excludes=excludes,
            name=name,
            options=options,
            schedule=schedule,
            tags=tags,
            tags_all=tags_all,
            timeouts=timeouts,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putExcludes")
    def put_excludes(
        self,
        *,
        filter_type: typing.Optional[builtins.str] = None,
        value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param filter_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#filter_type DatasyncTask#filter_type}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#value DatasyncTask#value}.
        '''
        value_ = DatasyncTaskExcludes(filter_type=filter_type, value=value)

        return typing.cast(None, jsii.invoke(self, "putExcludes", [value_]))

    @jsii.member(jsii_name="putOptions")
    def put_options(
        self,
        *,
        atime: typing.Optional[builtins.str] = None,
        bytes_per_second: typing.Optional[jsii.Number] = None,
        gid: typing.Optional[builtins.str] = None,
        log_level: typing.Optional[builtins.str] = None,
        mtime: typing.Optional[builtins.str] = None,
        overwrite_mode: typing.Optional[builtins.str] = None,
        posix_permissions: typing.Optional[builtins.str] = None,
        preserve_deleted_files: typing.Optional[builtins.str] = None,
        preserve_devices: typing.Optional[builtins.str] = None,
        task_queueing: typing.Optional[builtins.str] = None,
        transfer_mode: typing.Optional[builtins.str] = None,
        uid: typing.Optional[builtins.str] = None,
        verify_mode: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param atime: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#atime DatasyncTask#atime}.
        :param bytes_per_second: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#bytes_per_second DatasyncTask#bytes_per_second}.
        :param gid: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#gid DatasyncTask#gid}.
        :param log_level: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#log_level DatasyncTask#log_level}.
        :param mtime: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#mtime DatasyncTask#mtime}.
        :param overwrite_mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#overwrite_mode DatasyncTask#overwrite_mode}.
        :param posix_permissions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#posix_permissions DatasyncTask#posix_permissions}.
        :param preserve_deleted_files: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#preserve_deleted_files DatasyncTask#preserve_deleted_files}.
        :param preserve_devices: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#preserve_devices DatasyncTask#preserve_devices}.
        :param task_queueing: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#task_queueing DatasyncTask#task_queueing}.
        :param transfer_mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#transfer_mode DatasyncTask#transfer_mode}.
        :param uid: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#uid DatasyncTask#uid}.
        :param verify_mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#verify_mode DatasyncTask#verify_mode}.
        '''
        value = DatasyncTaskOptions(
            atime=atime,
            bytes_per_second=bytes_per_second,
            gid=gid,
            log_level=log_level,
            mtime=mtime,
            overwrite_mode=overwrite_mode,
            posix_permissions=posix_permissions,
            preserve_deleted_files=preserve_deleted_files,
            preserve_devices=preserve_devices,
            task_queueing=task_queueing,
            transfer_mode=transfer_mode,
            uid=uid,
            verify_mode=verify_mode,
        )

        return typing.cast(None, jsii.invoke(self, "putOptions", [value]))

    @jsii.member(jsii_name="putSchedule")
    def put_schedule(self, *, schedule_expression: builtins.str) -> None:
        '''
        :param schedule_expression: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#schedule_expression DatasyncTask#schedule_expression}.
        '''
        value = DatasyncTaskSchedule(schedule_expression=schedule_expression)

        return typing.cast(None, jsii.invoke(self, "putSchedule", [value]))

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(self, *, create: typing.Optional[builtins.str] = None) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#create DatasyncTask#create}.
        '''
        value = DatasyncTaskTimeouts(create=create)

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetCloudwatchLogGroupArn")
    def reset_cloudwatch_log_group_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCloudwatchLogGroupArn", []))

    @jsii.member(jsii_name="resetExcludes")
    def reset_excludes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExcludes", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetOptions")
    def reset_options(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOptions", []))

    @jsii.member(jsii_name="resetSchedule")
    def reset_schedule(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSchedule", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetTimeouts")
    def reset_timeouts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeouts", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="excludes")
    def excludes(self) -> "DatasyncTaskExcludesOutputReference":
        return typing.cast("DatasyncTaskExcludesOutputReference", jsii.get(self, "excludes"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="options")
    def options(self) -> "DatasyncTaskOptionsOutputReference":
        return typing.cast("DatasyncTaskOptionsOutputReference", jsii.get(self, "options"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="schedule")
    def schedule(self) -> "DatasyncTaskScheduleOutputReference":
        return typing.cast("DatasyncTaskScheduleOutputReference", jsii.get(self, "schedule"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "DatasyncTaskTimeoutsOutputReference":
        return typing.cast("DatasyncTaskTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cloudwatchLogGroupArnInput")
    def cloudwatch_log_group_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cloudwatchLogGroupArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="destinationLocationArnInput")
    def destination_location_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "destinationLocationArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="excludesInput")
    def excludes_input(self) -> typing.Optional["DatasyncTaskExcludes"]:
        return typing.cast(typing.Optional["DatasyncTaskExcludes"], jsii.get(self, "excludesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="optionsInput")
    def options_input(self) -> typing.Optional["DatasyncTaskOptions"]:
        return typing.cast(typing.Optional["DatasyncTaskOptions"], jsii.get(self, "optionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="scheduleInput")
    def schedule_input(self) -> typing.Optional["DatasyncTaskSchedule"]:
        return typing.cast(typing.Optional["DatasyncTaskSchedule"], jsii.get(self, "scheduleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceLocationArnInput")
    def source_location_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceLocationArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAllInput")
    def tags_all_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsAllInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(self) -> typing.Optional["DatasyncTaskTimeouts"]:
        return typing.cast(typing.Optional["DatasyncTaskTimeouts"], jsii.get(self, "timeoutsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cloudwatchLogGroupArn")
    def cloudwatch_log_group_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cloudwatchLogGroupArn"))

    @cloudwatch_log_group_arn.setter
    def cloudwatch_log_group_arn(self, value: builtins.str) -> None:
        jsii.set(self, "cloudwatchLogGroupArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="destinationLocationArn")
    def destination_location_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destinationLocationArn"))

    @destination_location_arn.setter
    def destination_location_arn(self, value: builtins.str) -> None:
        jsii.set(self, "destinationLocationArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceLocationArn")
    def source_location_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceLocationArn"))

    @source_location_arn.setter
    def source_location_arn(self, value: builtins.str) -> None:
        jsii.set(self, "sourceLocationArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tags"))

    @tags.setter
    def tags(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "tags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAll")
    def tags_all(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsAll"))

    @tags_all.setter
    def tags_all(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "tagsAll", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.datasync.DatasyncTaskConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "destination_location_arn": "destinationLocationArn",
        "source_location_arn": "sourceLocationArn",
        "cloudwatch_log_group_arn": "cloudwatchLogGroupArn",
        "excludes": "excludes",
        "name": "name",
        "options": "options",
        "schedule": "schedule",
        "tags": "tags",
        "tags_all": "tagsAll",
        "timeouts": "timeouts",
    },
)
class DatasyncTaskConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        destination_location_arn: builtins.str,
        source_location_arn: builtins.str,
        cloudwatch_log_group_arn: typing.Optional[builtins.str] = None,
        excludes: typing.Optional["DatasyncTaskExcludes"] = None,
        name: typing.Optional[builtins.str] = None,
        options: typing.Optional["DatasyncTaskOptions"] = None,
        schedule: typing.Optional["DatasyncTaskSchedule"] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["DatasyncTaskTimeouts"] = None,
    ) -> None:
        '''AWS DataSync.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param destination_location_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#destination_location_arn DatasyncTask#destination_location_arn}.
        :param source_location_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#source_location_arn DatasyncTask#source_location_arn}.
        :param cloudwatch_log_group_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#cloudwatch_log_group_arn DatasyncTask#cloudwatch_log_group_arn}.
        :param excludes: excludes block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#excludes DatasyncTask#excludes}
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#name DatasyncTask#name}.
        :param options: options block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#options DatasyncTask#options}
        :param schedule: schedule block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#schedule DatasyncTask#schedule}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#tags DatasyncTask#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#tags_all DatasyncTask#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#timeouts DatasyncTask#timeouts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(excludes, dict):
            excludes = DatasyncTaskExcludes(**excludes)
        if isinstance(options, dict):
            options = DatasyncTaskOptions(**options)
        if isinstance(schedule, dict):
            schedule = DatasyncTaskSchedule(**schedule)
        if isinstance(timeouts, dict):
            timeouts = DatasyncTaskTimeouts(**timeouts)
        self._values: typing.Dict[str, typing.Any] = {
            "destination_location_arn": destination_location_arn,
            "source_location_arn": source_location_arn,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if cloudwatch_log_group_arn is not None:
            self._values["cloudwatch_log_group_arn"] = cloudwatch_log_group_arn
        if excludes is not None:
            self._values["excludes"] = excludes
        if name is not None:
            self._values["name"] = name
        if options is not None:
            self._values["options"] = options
        if schedule is not None:
            self._values["schedule"] = schedule
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if timeouts is not None:
            self._values["timeouts"] = timeouts

    @builtins.property
    def count(self) -> typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def destination_location_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#destination_location_arn DatasyncTask#destination_location_arn}.'''
        result = self._values.get("destination_location_arn")
        assert result is not None, "Required property 'destination_location_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def source_location_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#source_location_arn DatasyncTask#source_location_arn}.'''
        result = self._values.get("source_location_arn")
        assert result is not None, "Required property 'source_location_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cloudwatch_log_group_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#cloudwatch_log_group_arn DatasyncTask#cloudwatch_log_group_arn}.'''
        result = self._values.get("cloudwatch_log_group_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def excludes(self) -> typing.Optional["DatasyncTaskExcludes"]:
        '''excludes block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#excludes DatasyncTask#excludes}
        '''
        result = self._values.get("excludes")
        return typing.cast(typing.Optional["DatasyncTaskExcludes"], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#name DatasyncTask#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def options(self) -> typing.Optional["DatasyncTaskOptions"]:
        '''options block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#options DatasyncTask#options}
        '''
        result = self._values.get("options")
        return typing.cast(typing.Optional["DatasyncTaskOptions"], result)

    @builtins.property
    def schedule(self) -> typing.Optional["DatasyncTaskSchedule"]:
        '''schedule block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#schedule DatasyncTask#schedule}
        '''
        result = self._values.get("schedule")
        return typing.cast(typing.Optional["DatasyncTaskSchedule"], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#tags DatasyncTask#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#tags_all DatasyncTask#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["DatasyncTaskTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#timeouts DatasyncTask#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["DatasyncTaskTimeouts"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatasyncTaskConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.datasync.DatasyncTaskExcludes",
    jsii_struct_bases=[],
    name_mapping={"filter_type": "filterType", "value": "value"},
)
class DatasyncTaskExcludes:
    def __init__(
        self,
        *,
        filter_type: typing.Optional[builtins.str] = None,
        value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param filter_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#filter_type DatasyncTask#filter_type}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#value DatasyncTask#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if filter_type is not None:
            self._values["filter_type"] = filter_type
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def filter_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#filter_type DatasyncTask#filter_type}.'''
        result = self._values.get("filter_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#value DatasyncTask#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatasyncTaskExcludes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DatasyncTaskExcludesOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.datasync.DatasyncTaskExcludesOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetFilterType")
    def reset_filter_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFilterType", []))

    @jsii.member(jsii_name="resetValue")
    def reset_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValue", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="filterTypeInput")
    def filter_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "filterTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "valueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="filterType")
    def filter_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "filterType"))

    @filter_type.setter
    def filter_type(self, value: builtins.str) -> None:
        jsii.set(self, "filterType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        jsii.set(self, "value", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DatasyncTaskExcludes]:
        return typing.cast(typing.Optional[DatasyncTaskExcludes], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[DatasyncTaskExcludes]) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.datasync.DatasyncTaskOptions",
    jsii_struct_bases=[],
    name_mapping={
        "atime": "atime",
        "bytes_per_second": "bytesPerSecond",
        "gid": "gid",
        "log_level": "logLevel",
        "mtime": "mtime",
        "overwrite_mode": "overwriteMode",
        "posix_permissions": "posixPermissions",
        "preserve_deleted_files": "preserveDeletedFiles",
        "preserve_devices": "preserveDevices",
        "task_queueing": "taskQueueing",
        "transfer_mode": "transferMode",
        "uid": "uid",
        "verify_mode": "verifyMode",
    },
)
class DatasyncTaskOptions:
    def __init__(
        self,
        *,
        atime: typing.Optional[builtins.str] = None,
        bytes_per_second: typing.Optional[jsii.Number] = None,
        gid: typing.Optional[builtins.str] = None,
        log_level: typing.Optional[builtins.str] = None,
        mtime: typing.Optional[builtins.str] = None,
        overwrite_mode: typing.Optional[builtins.str] = None,
        posix_permissions: typing.Optional[builtins.str] = None,
        preserve_deleted_files: typing.Optional[builtins.str] = None,
        preserve_devices: typing.Optional[builtins.str] = None,
        task_queueing: typing.Optional[builtins.str] = None,
        transfer_mode: typing.Optional[builtins.str] = None,
        uid: typing.Optional[builtins.str] = None,
        verify_mode: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param atime: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#atime DatasyncTask#atime}.
        :param bytes_per_second: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#bytes_per_second DatasyncTask#bytes_per_second}.
        :param gid: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#gid DatasyncTask#gid}.
        :param log_level: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#log_level DatasyncTask#log_level}.
        :param mtime: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#mtime DatasyncTask#mtime}.
        :param overwrite_mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#overwrite_mode DatasyncTask#overwrite_mode}.
        :param posix_permissions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#posix_permissions DatasyncTask#posix_permissions}.
        :param preserve_deleted_files: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#preserve_deleted_files DatasyncTask#preserve_deleted_files}.
        :param preserve_devices: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#preserve_devices DatasyncTask#preserve_devices}.
        :param task_queueing: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#task_queueing DatasyncTask#task_queueing}.
        :param transfer_mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#transfer_mode DatasyncTask#transfer_mode}.
        :param uid: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#uid DatasyncTask#uid}.
        :param verify_mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#verify_mode DatasyncTask#verify_mode}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if atime is not None:
            self._values["atime"] = atime
        if bytes_per_second is not None:
            self._values["bytes_per_second"] = bytes_per_second
        if gid is not None:
            self._values["gid"] = gid
        if log_level is not None:
            self._values["log_level"] = log_level
        if mtime is not None:
            self._values["mtime"] = mtime
        if overwrite_mode is not None:
            self._values["overwrite_mode"] = overwrite_mode
        if posix_permissions is not None:
            self._values["posix_permissions"] = posix_permissions
        if preserve_deleted_files is not None:
            self._values["preserve_deleted_files"] = preserve_deleted_files
        if preserve_devices is not None:
            self._values["preserve_devices"] = preserve_devices
        if task_queueing is not None:
            self._values["task_queueing"] = task_queueing
        if transfer_mode is not None:
            self._values["transfer_mode"] = transfer_mode
        if uid is not None:
            self._values["uid"] = uid
        if verify_mode is not None:
            self._values["verify_mode"] = verify_mode

    @builtins.property
    def atime(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#atime DatasyncTask#atime}.'''
        result = self._values.get("atime")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bytes_per_second(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#bytes_per_second DatasyncTask#bytes_per_second}.'''
        result = self._values.get("bytes_per_second")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def gid(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#gid DatasyncTask#gid}.'''
        result = self._values.get("gid")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def log_level(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#log_level DatasyncTask#log_level}.'''
        result = self._values.get("log_level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mtime(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#mtime DatasyncTask#mtime}.'''
        result = self._values.get("mtime")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def overwrite_mode(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#overwrite_mode DatasyncTask#overwrite_mode}.'''
        result = self._values.get("overwrite_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def posix_permissions(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#posix_permissions DatasyncTask#posix_permissions}.'''
        result = self._values.get("posix_permissions")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def preserve_deleted_files(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#preserve_deleted_files DatasyncTask#preserve_deleted_files}.'''
        result = self._values.get("preserve_deleted_files")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def preserve_devices(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#preserve_devices DatasyncTask#preserve_devices}.'''
        result = self._values.get("preserve_devices")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def task_queueing(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#task_queueing DatasyncTask#task_queueing}.'''
        result = self._values.get("task_queueing")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def transfer_mode(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#transfer_mode DatasyncTask#transfer_mode}.'''
        result = self._values.get("transfer_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def uid(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#uid DatasyncTask#uid}.'''
        result = self._values.get("uid")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def verify_mode(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#verify_mode DatasyncTask#verify_mode}.'''
        result = self._values.get("verify_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatasyncTaskOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DatasyncTaskOptionsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.datasync.DatasyncTaskOptionsOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetAtime")
    def reset_atime(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAtime", []))

    @jsii.member(jsii_name="resetBytesPerSecond")
    def reset_bytes_per_second(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBytesPerSecond", []))

    @jsii.member(jsii_name="resetGid")
    def reset_gid(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGid", []))

    @jsii.member(jsii_name="resetLogLevel")
    def reset_log_level(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogLevel", []))

    @jsii.member(jsii_name="resetMtime")
    def reset_mtime(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMtime", []))

    @jsii.member(jsii_name="resetOverwriteMode")
    def reset_overwrite_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOverwriteMode", []))

    @jsii.member(jsii_name="resetPosixPermissions")
    def reset_posix_permissions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPosixPermissions", []))

    @jsii.member(jsii_name="resetPreserveDeletedFiles")
    def reset_preserve_deleted_files(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPreserveDeletedFiles", []))

    @jsii.member(jsii_name="resetPreserveDevices")
    def reset_preserve_devices(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPreserveDevices", []))

    @jsii.member(jsii_name="resetTaskQueueing")
    def reset_task_queueing(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTaskQueueing", []))

    @jsii.member(jsii_name="resetTransferMode")
    def reset_transfer_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTransferMode", []))

    @jsii.member(jsii_name="resetUid")
    def reset_uid(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUid", []))

    @jsii.member(jsii_name="resetVerifyMode")
    def reset_verify_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVerifyMode", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="atimeInput")
    def atime_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "atimeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bytesPerSecondInput")
    def bytes_per_second_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "bytesPerSecondInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="gidInput")
    def gid_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "gidInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logLevelInput")
    def log_level_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "logLevelInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mtimeInput")
    def mtime_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "mtimeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="overwriteModeInput")
    def overwrite_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "overwriteModeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="posixPermissionsInput")
    def posix_permissions_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "posixPermissionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preserveDeletedFilesInput")
    def preserve_deleted_files_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "preserveDeletedFilesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preserveDevicesInput")
    def preserve_devices_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "preserveDevicesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="taskQueueingInput")
    def task_queueing_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "taskQueueingInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="transferModeInput")
    def transfer_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "transferModeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="uidInput")
    def uid_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "uidInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="verifyModeInput")
    def verify_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "verifyModeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="atime")
    def atime(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "atime"))

    @atime.setter
    def atime(self, value: builtins.str) -> None:
        jsii.set(self, "atime", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bytesPerSecond")
    def bytes_per_second(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "bytesPerSecond"))

    @bytes_per_second.setter
    def bytes_per_second(self, value: jsii.Number) -> None:
        jsii.set(self, "bytesPerSecond", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="gid")
    def gid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gid"))

    @gid.setter
    def gid(self, value: builtins.str) -> None:
        jsii.set(self, "gid", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logLevel")
    def log_level(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "logLevel"))

    @log_level.setter
    def log_level(self, value: builtins.str) -> None:
        jsii.set(self, "logLevel", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mtime")
    def mtime(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mtime"))

    @mtime.setter
    def mtime(self, value: builtins.str) -> None:
        jsii.set(self, "mtime", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="overwriteMode")
    def overwrite_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "overwriteMode"))

    @overwrite_mode.setter
    def overwrite_mode(self, value: builtins.str) -> None:
        jsii.set(self, "overwriteMode", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="posixPermissions")
    def posix_permissions(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "posixPermissions"))

    @posix_permissions.setter
    def posix_permissions(self, value: builtins.str) -> None:
        jsii.set(self, "posixPermissions", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preserveDeletedFiles")
    def preserve_deleted_files(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "preserveDeletedFiles"))

    @preserve_deleted_files.setter
    def preserve_deleted_files(self, value: builtins.str) -> None:
        jsii.set(self, "preserveDeletedFiles", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preserveDevices")
    def preserve_devices(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "preserveDevices"))

    @preserve_devices.setter
    def preserve_devices(self, value: builtins.str) -> None:
        jsii.set(self, "preserveDevices", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="taskQueueing")
    def task_queueing(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "taskQueueing"))

    @task_queueing.setter
    def task_queueing(self, value: builtins.str) -> None:
        jsii.set(self, "taskQueueing", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="transferMode")
    def transfer_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "transferMode"))

    @transfer_mode.setter
    def transfer_mode(self, value: builtins.str) -> None:
        jsii.set(self, "transferMode", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="uid")
    def uid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uid"))

    @uid.setter
    def uid(self, value: builtins.str) -> None:
        jsii.set(self, "uid", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="verifyMode")
    def verify_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "verifyMode"))

    @verify_mode.setter
    def verify_mode(self, value: builtins.str) -> None:
        jsii.set(self, "verifyMode", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DatasyncTaskOptions]:
        return typing.cast(typing.Optional[DatasyncTaskOptions], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[DatasyncTaskOptions]) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.datasync.DatasyncTaskSchedule",
    jsii_struct_bases=[],
    name_mapping={"schedule_expression": "scheduleExpression"},
)
class DatasyncTaskSchedule:
    def __init__(self, *, schedule_expression: builtins.str) -> None:
        '''
        :param schedule_expression: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#schedule_expression DatasyncTask#schedule_expression}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "schedule_expression": schedule_expression,
        }

    @builtins.property
    def schedule_expression(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#schedule_expression DatasyncTask#schedule_expression}.'''
        result = self._values.get("schedule_expression")
        assert result is not None, "Required property 'schedule_expression' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatasyncTaskSchedule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DatasyncTaskScheduleOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.datasync.DatasyncTaskScheduleOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="scheduleExpressionInput")
    def schedule_expression_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "scheduleExpressionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="scheduleExpression")
    def schedule_expression(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "scheduleExpression"))

    @schedule_expression.setter
    def schedule_expression(self, value: builtins.str) -> None:
        jsii.set(self, "scheduleExpression", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DatasyncTaskSchedule]:
        return typing.cast(typing.Optional[DatasyncTaskSchedule], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[DatasyncTaskSchedule]) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.datasync.DatasyncTaskTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create"},
)
class DatasyncTaskTimeouts:
    def __init__(self, *, create: typing.Optional[builtins.str] = None) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#create DatasyncTask#create}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if create is not None:
            self._values["create"] = create

    @builtins.property
    def create(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datasync_task#create DatasyncTask#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatasyncTaskTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DatasyncTaskTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.datasync.DatasyncTaskTimeoutsOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetCreate")
    def reset_create(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreate", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createInput")
    def create_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="create")
    def create(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "create"))

    @create.setter
    def create(self, value: builtins.str) -> None:
        jsii.set(self, "create", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DatasyncTaskTimeouts]:
        return typing.cast(typing.Optional[DatasyncTaskTimeouts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[DatasyncTaskTimeouts]) -> None:
        jsii.set(self, "internalValue", value)


__all__ = [
    "DatasyncAgent",
    "DatasyncAgentConfig",
    "DatasyncAgentTimeouts",
    "DatasyncAgentTimeoutsOutputReference",
    "DatasyncLocationEfs",
    "DatasyncLocationEfsConfig",
    "DatasyncLocationEfsEc2Config",
    "DatasyncLocationEfsEc2ConfigOutputReference",
    "DatasyncLocationFsxLustreFileSystem",
    "DatasyncLocationFsxLustreFileSystemConfig",
    "DatasyncLocationFsxWindowsFileSystem",
    "DatasyncLocationFsxWindowsFileSystemConfig",
    "DatasyncLocationHdfs",
    "DatasyncLocationHdfsConfig",
    "DatasyncLocationHdfsNameNode",
    "DatasyncLocationHdfsQopConfiguration",
    "DatasyncLocationHdfsQopConfigurationOutputReference",
    "DatasyncLocationNfs",
    "DatasyncLocationNfsConfig",
    "DatasyncLocationNfsMountOptions",
    "DatasyncLocationNfsMountOptionsOutputReference",
    "DatasyncLocationNfsOnPremConfig",
    "DatasyncLocationNfsOnPremConfigOutputReference",
    "DatasyncLocationS3",
    "DatasyncLocationS3Config",
    "DatasyncLocationS3S3Config",
    "DatasyncLocationS3S3ConfigOutputReference",
    "DatasyncLocationSmb",
    "DatasyncLocationSmbConfig",
    "DatasyncLocationSmbMountOptions",
    "DatasyncLocationSmbMountOptionsOutputReference",
    "DatasyncTask",
    "DatasyncTaskConfig",
    "DatasyncTaskExcludes",
    "DatasyncTaskExcludesOutputReference",
    "DatasyncTaskOptions",
    "DatasyncTaskOptionsOutputReference",
    "DatasyncTaskSchedule",
    "DatasyncTaskScheduleOutputReference",
    "DatasyncTaskTimeouts",
    "DatasyncTaskTimeoutsOutputReference",
]

publication.publish()
