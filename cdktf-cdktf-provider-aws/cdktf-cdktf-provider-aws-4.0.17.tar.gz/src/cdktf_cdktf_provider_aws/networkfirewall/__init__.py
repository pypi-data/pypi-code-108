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


class NetworkfirewallFirewall(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallFirewall",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall aws_networkfirewall_firewall}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        firewall_policy_arn: builtins.str,
        name: builtins.str,
        subnet_mapping: typing.Sequence["NetworkfirewallFirewallSubnetMapping"],
        vpc_id: builtins.str,
        delete_protection: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        description: typing.Optional[builtins.str] = None,
        firewall_policy_change_protection: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        subnet_change_protection: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall aws_networkfirewall_firewall} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param firewall_policy_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall#firewall_policy_arn NetworkfirewallFirewall#firewall_policy_arn}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall#name NetworkfirewallFirewall#name}.
        :param subnet_mapping: subnet_mapping block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall#subnet_mapping NetworkfirewallFirewall#subnet_mapping}
        :param vpc_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall#vpc_id NetworkfirewallFirewall#vpc_id}.
        :param delete_protection: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall#delete_protection NetworkfirewallFirewall#delete_protection}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall#description NetworkfirewallFirewall#description}.
        :param firewall_policy_change_protection: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall#firewall_policy_change_protection NetworkfirewallFirewall#firewall_policy_change_protection}.
        :param subnet_change_protection: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall#subnet_change_protection NetworkfirewallFirewall#subnet_change_protection}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall#tags NetworkfirewallFirewall#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall#tags_all NetworkfirewallFirewall#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = NetworkfirewallFirewallConfig(
            firewall_policy_arn=firewall_policy_arn,
            name=name,
            subnet_mapping=subnet_mapping,
            vpc_id=vpc_id,
            delete_protection=delete_protection,
            description=description,
            firewall_policy_change_protection=firewall_policy_change_protection,
            subnet_change_protection=subnet_change_protection,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="firewallStatus")
    def firewall_status(
        self,
        index: builtins.str,
    ) -> "NetworkfirewallFirewallFirewallStatus":
        '''
        :param index: -
        '''
        return typing.cast("NetworkfirewallFirewallFirewallStatus", jsii.invoke(self, "firewallStatus", [index]))

    @jsii.member(jsii_name="resetDeleteProtection")
    def reset_delete_protection(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeleteProtection", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetFirewallPolicyChangeProtection")
    def reset_firewall_policy_change_protection(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFirewallPolicyChangeProtection", []))

    @jsii.member(jsii_name="resetSubnetChangeProtection")
    def reset_subnet_change_protection(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSubnetChangeProtection", []))

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
    @jsii.member(jsii_name="updateToken")
    def update_token(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updateToken"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deleteProtectionInput")
    def delete_protection_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "deleteProtectionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firewallPolicyArnInput")
    def firewall_policy_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "firewallPolicyArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firewallPolicyChangeProtectionInput")
    def firewall_policy_change_protection_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "firewallPolicyChangeProtectionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnetChangeProtectionInput")
    def subnet_change_protection_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "subnetChangeProtectionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnetMappingInput")
    def subnet_mapping_input(
        self,
    ) -> typing.Optional[typing.List["NetworkfirewallFirewallSubnetMapping"]]:
        return typing.cast(typing.Optional[typing.List["NetworkfirewallFirewallSubnetMapping"]], jsii.get(self, "subnetMappingInput"))

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
    @jsii.member(jsii_name="vpcIdInput")
    def vpc_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "vpcIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deleteProtection")
    def delete_protection(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "deleteProtection"))

    @delete_protection.setter
    def delete_protection(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "deleteProtection", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firewallPolicyArn")
    def firewall_policy_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "firewallPolicyArn"))

    @firewall_policy_arn.setter
    def firewall_policy_arn(self, value: builtins.str) -> None:
        jsii.set(self, "firewallPolicyArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firewallPolicyChangeProtection")
    def firewall_policy_change_protection(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "firewallPolicyChangeProtection"))

    @firewall_policy_change_protection.setter
    def firewall_policy_change_protection(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "firewallPolicyChangeProtection", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnetChangeProtection")
    def subnet_change_protection(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "subnetChangeProtection"))

    @subnet_change_protection.setter
    def subnet_change_protection(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "subnetChangeProtection", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnetMapping")
    def subnet_mapping(self) -> typing.List["NetworkfirewallFirewallSubnetMapping"]:
        return typing.cast(typing.List["NetworkfirewallFirewallSubnetMapping"], jsii.get(self, "subnetMapping"))

    @subnet_mapping.setter
    def subnet_mapping(
        self,
        value: typing.List["NetworkfirewallFirewallSubnetMapping"],
    ) -> None:
        jsii.set(self, "subnetMapping", value)

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
    @jsii.member(jsii_name="vpcId")
    def vpc_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "vpcId"))

    @vpc_id.setter
    def vpc_id(self, value: builtins.str) -> None:
        jsii.set(self, "vpcId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallFirewallConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "firewall_policy_arn": "firewallPolicyArn",
        "name": "name",
        "subnet_mapping": "subnetMapping",
        "vpc_id": "vpcId",
        "delete_protection": "deleteProtection",
        "description": "description",
        "firewall_policy_change_protection": "firewallPolicyChangeProtection",
        "subnet_change_protection": "subnetChangeProtection",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class NetworkfirewallFirewallConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        firewall_policy_arn: builtins.str,
        name: builtins.str,
        subnet_mapping: typing.Sequence["NetworkfirewallFirewallSubnetMapping"],
        vpc_id: builtins.str,
        delete_protection: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        description: typing.Optional[builtins.str] = None,
        firewall_policy_change_protection: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        subnet_change_protection: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS Network Firewall.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param firewall_policy_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall#firewall_policy_arn NetworkfirewallFirewall#firewall_policy_arn}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall#name NetworkfirewallFirewall#name}.
        :param subnet_mapping: subnet_mapping block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall#subnet_mapping NetworkfirewallFirewall#subnet_mapping}
        :param vpc_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall#vpc_id NetworkfirewallFirewall#vpc_id}.
        :param delete_protection: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall#delete_protection NetworkfirewallFirewall#delete_protection}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall#description NetworkfirewallFirewall#description}.
        :param firewall_policy_change_protection: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall#firewall_policy_change_protection NetworkfirewallFirewall#firewall_policy_change_protection}.
        :param subnet_change_protection: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall#subnet_change_protection NetworkfirewallFirewall#subnet_change_protection}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall#tags NetworkfirewallFirewall#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall#tags_all NetworkfirewallFirewall#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "firewall_policy_arn": firewall_policy_arn,
            "name": name,
            "subnet_mapping": subnet_mapping,
            "vpc_id": vpc_id,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if delete_protection is not None:
            self._values["delete_protection"] = delete_protection
        if description is not None:
            self._values["description"] = description
        if firewall_policy_change_protection is not None:
            self._values["firewall_policy_change_protection"] = firewall_policy_change_protection
        if subnet_change_protection is not None:
            self._values["subnet_change_protection"] = subnet_change_protection
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
    def firewall_policy_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall#firewall_policy_arn NetworkfirewallFirewall#firewall_policy_arn}.'''
        result = self._values.get("firewall_policy_arn")
        assert result is not None, "Required property 'firewall_policy_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall#name NetworkfirewallFirewall#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def subnet_mapping(self) -> typing.List["NetworkfirewallFirewallSubnetMapping"]:
        '''subnet_mapping block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall#subnet_mapping NetworkfirewallFirewall#subnet_mapping}
        '''
        result = self._values.get("subnet_mapping")
        assert result is not None, "Required property 'subnet_mapping' is missing"
        return typing.cast(typing.List["NetworkfirewallFirewallSubnetMapping"], result)

    @builtins.property
    def vpc_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall#vpc_id NetworkfirewallFirewall#vpc_id}.'''
        result = self._values.get("vpc_id")
        assert result is not None, "Required property 'vpc_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def delete_protection(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall#delete_protection NetworkfirewallFirewall#delete_protection}.'''
        result = self._values.get("delete_protection")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall#description NetworkfirewallFirewall#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def firewall_policy_change_protection(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall#firewall_policy_change_protection NetworkfirewallFirewall#firewall_policy_change_protection}.'''
        result = self._values.get("firewall_policy_change_protection")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def subnet_change_protection(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall#subnet_change_protection NetworkfirewallFirewall#subnet_change_protection}.'''
        result = self._values.get("subnet_change_protection")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall#tags NetworkfirewallFirewall#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall#tags_all NetworkfirewallFirewall#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallFirewallConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NetworkfirewallFirewallFirewallStatus(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallFirewallFirewallStatus",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        complex_computed_list_index: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: -
        :param terraform_attribute: -
        :param complex_computed_list_index: -

        :stability: experimental
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_computed_list_index])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="syncStates")
    def sync_states(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "syncStates"))


class NetworkfirewallFirewallFirewallStatusSyncStates(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallFirewallFirewallStatusSyncStates",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        complex_computed_list_index: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: -
        :param terraform_attribute: -
        :param complex_computed_list_index: -

        :stability: experimental
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_computed_list_index])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attachment")
    def attachment(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "attachment"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="availabilityZone")
    def availability_zone(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "availabilityZone"))


class NetworkfirewallFirewallFirewallStatusSyncStatesAttachment(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallFirewallFirewallStatusSyncStatesAttachment",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        complex_computed_list_index: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: -
        :param terraform_attribute: -
        :param complex_computed_list_index: -

        :stability: experimental
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_computed_list_index])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpointId")
    def endpoint_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endpointId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnetId")
    def subnet_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "subnetId"))


class NetworkfirewallFirewallPolicy(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallFirewallPolicy",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy aws_networkfirewall_firewall_policy}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        firewall_policy: "NetworkfirewallFirewallPolicyFirewallPolicy",
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy aws_networkfirewall_firewall_policy} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param firewall_policy: firewall_policy block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#firewall_policy NetworkfirewallFirewallPolicy#firewall_policy}
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#name NetworkfirewallFirewallPolicy#name}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#description NetworkfirewallFirewallPolicy#description}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#tags NetworkfirewallFirewallPolicy#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#tags_all NetworkfirewallFirewallPolicy#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = NetworkfirewallFirewallPolicyConfig(
            firewall_policy=firewall_policy,
            name=name,
            description=description,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putFirewallPolicy")
    def put_firewall_policy(
        self,
        *,
        stateless_default_actions: typing.Sequence[builtins.str],
        stateless_fragment_default_actions: typing.Sequence[builtins.str],
        stateful_default_actions: typing.Optional[typing.Sequence[builtins.str]] = None,
        stateful_engine_options: typing.Optional["NetworkfirewallFirewallPolicyFirewallPolicyStatefulEngineOptions"] = None,
        stateful_rule_group_reference: typing.Optional[typing.Sequence["NetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReference"]] = None,
        stateless_custom_action: typing.Optional[typing.Sequence["NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomAction"]] = None,
        stateless_rule_group_reference: typing.Optional[typing.Sequence["NetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReference"]] = None,
    ) -> None:
        '''
        :param stateless_default_actions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#stateless_default_actions NetworkfirewallFirewallPolicy#stateless_default_actions}.
        :param stateless_fragment_default_actions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#stateless_fragment_default_actions NetworkfirewallFirewallPolicy#stateless_fragment_default_actions}.
        :param stateful_default_actions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#stateful_default_actions NetworkfirewallFirewallPolicy#stateful_default_actions}.
        :param stateful_engine_options: stateful_engine_options block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#stateful_engine_options NetworkfirewallFirewallPolicy#stateful_engine_options}
        :param stateful_rule_group_reference: stateful_rule_group_reference block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#stateful_rule_group_reference NetworkfirewallFirewallPolicy#stateful_rule_group_reference}
        :param stateless_custom_action: stateless_custom_action block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#stateless_custom_action NetworkfirewallFirewallPolicy#stateless_custom_action}
        :param stateless_rule_group_reference: stateless_rule_group_reference block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#stateless_rule_group_reference NetworkfirewallFirewallPolicy#stateless_rule_group_reference}
        '''
        value = NetworkfirewallFirewallPolicyFirewallPolicy(
            stateless_default_actions=stateless_default_actions,
            stateless_fragment_default_actions=stateless_fragment_default_actions,
            stateful_default_actions=stateful_default_actions,
            stateful_engine_options=stateful_engine_options,
            stateful_rule_group_reference=stateful_rule_group_reference,
            stateless_custom_action=stateless_custom_action,
            stateless_rule_group_reference=stateless_rule_group_reference,
        )

        return typing.cast(None, jsii.invoke(self, "putFirewallPolicy", [value]))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

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
    @jsii.member(jsii_name="firewallPolicy")
    def firewall_policy(
        self,
    ) -> "NetworkfirewallFirewallPolicyFirewallPolicyOutputReference":
        return typing.cast("NetworkfirewallFirewallPolicyFirewallPolicyOutputReference", jsii.get(self, "firewallPolicy"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="updateToken")
    def update_token(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updateToken"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firewallPolicyInput")
    def firewall_policy_input(
        self,
    ) -> typing.Optional["NetworkfirewallFirewallPolicyFirewallPolicy"]:
        return typing.cast(typing.Optional["NetworkfirewallFirewallPolicyFirewallPolicy"], jsii.get(self, "firewallPolicyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

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
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

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
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallFirewallPolicyConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "firewall_policy": "firewallPolicy",
        "name": "name",
        "description": "description",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class NetworkfirewallFirewallPolicyConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        firewall_policy: "NetworkfirewallFirewallPolicyFirewallPolicy",
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS Network Firewall.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param firewall_policy: firewall_policy block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#firewall_policy NetworkfirewallFirewallPolicy#firewall_policy}
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#name NetworkfirewallFirewallPolicy#name}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#description NetworkfirewallFirewallPolicy#description}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#tags NetworkfirewallFirewallPolicy#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#tags_all NetworkfirewallFirewallPolicy#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(firewall_policy, dict):
            firewall_policy = NetworkfirewallFirewallPolicyFirewallPolicy(**firewall_policy)
        self._values: typing.Dict[str, typing.Any] = {
            "firewall_policy": firewall_policy,
            "name": name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if description is not None:
            self._values["description"] = description
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
    def firewall_policy(self) -> "NetworkfirewallFirewallPolicyFirewallPolicy":
        '''firewall_policy block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#firewall_policy NetworkfirewallFirewallPolicy#firewall_policy}
        '''
        result = self._values.get("firewall_policy")
        assert result is not None, "Required property 'firewall_policy' is missing"
        return typing.cast("NetworkfirewallFirewallPolicyFirewallPolicy", result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#name NetworkfirewallFirewallPolicy#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#description NetworkfirewallFirewallPolicy#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#tags NetworkfirewallFirewallPolicy#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#tags_all NetworkfirewallFirewallPolicy#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallFirewallPolicyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallFirewallPolicyFirewallPolicy",
    jsii_struct_bases=[],
    name_mapping={
        "stateless_default_actions": "statelessDefaultActions",
        "stateless_fragment_default_actions": "statelessFragmentDefaultActions",
        "stateful_default_actions": "statefulDefaultActions",
        "stateful_engine_options": "statefulEngineOptions",
        "stateful_rule_group_reference": "statefulRuleGroupReference",
        "stateless_custom_action": "statelessCustomAction",
        "stateless_rule_group_reference": "statelessRuleGroupReference",
    },
)
class NetworkfirewallFirewallPolicyFirewallPolicy:
    def __init__(
        self,
        *,
        stateless_default_actions: typing.Sequence[builtins.str],
        stateless_fragment_default_actions: typing.Sequence[builtins.str],
        stateful_default_actions: typing.Optional[typing.Sequence[builtins.str]] = None,
        stateful_engine_options: typing.Optional["NetworkfirewallFirewallPolicyFirewallPolicyStatefulEngineOptions"] = None,
        stateful_rule_group_reference: typing.Optional[typing.Sequence["NetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReference"]] = None,
        stateless_custom_action: typing.Optional[typing.Sequence["NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomAction"]] = None,
        stateless_rule_group_reference: typing.Optional[typing.Sequence["NetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReference"]] = None,
    ) -> None:
        '''
        :param stateless_default_actions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#stateless_default_actions NetworkfirewallFirewallPolicy#stateless_default_actions}.
        :param stateless_fragment_default_actions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#stateless_fragment_default_actions NetworkfirewallFirewallPolicy#stateless_fragment_default_actions}.
        :param stateful_default_actions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#stateful_default_actions NetworkfirewallFirewallPolicy#stateful_default_actions}.
        :param stateful_engine_options: stateful_engine_options block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#stateful_engine_options NetworkfirewallFirewallPolicy#stateful_engine_options}
        :param stateful_rule_group_reference: stateful_rule_group_reference block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#stateful_rule_group_reference NetworkfirewallFirewallPolicy#stateful_rule_group_reference}
        :param stateless_custom_action: stateless_custom_action block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#stateless_custom_action NetworkfirewallFirewallPolicy#stateless_custom_action}
        :param stateless_rule_group_reference: stateless_rule_group_reference block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#stateless_rule_group_reference NetworkfirewallFirewallPolicy#stateless_rule_group_reference}
        '''
        if isinstance(stateful_engine_options, dict):
            stateful_engine_options = NetworkfirewallFirewallPolicyFirewallPolicyStatefulEngineOptions(**stateful_engine_options)
        self._values: typing.Dict[str, typing.Any] = {
            "stateless_default_actions": stateless_default_actions,
            "stateless_fragment_default_actions": stateless_fragment_default_actions,
        }
        if stateful_default_actions is not None:
            self._values["stateful_default_actions"] = stateful_default_actions
        if stateful_engine_options is not None:
            self._values["stateful_engine_options"] = stateful_engine_options
        if stateful_rule_group_reference is not None:
            self._values["stateful_rule_group_reference"] = stateful_rule_group_reference
        if stateless_custom_action is not None:
            self._values["stateless_custom_action"] = stateless_custom_action
        if stateless_rule_group_reference is not None:
            self._values["stateless_rule_group_reference"] = stateless_rule_group_reference

    @builtins.property
    def stateless_default_actions(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#stateless_default_actions NetworkfirewallFirewallPolicy#stateless_default_actions}.'''
        result = self._values.get("stateless_default_actions")
        assert result is not None, "Required property 'stateless_default_actions' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def stateless_fragment_default_actions(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#stateless_fragment_default_actions NetworkfirewallFirewallPolicy#stateless_fragment_default_actions}.'''
        result = self._values.get("stateless_fragment_default_actions")
        assert result is not None, "Required property 'stateless_fragment_default_actions' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def stateful_default_actions(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#stateful_default_actions NetworkfirewallFirewallPolicy#stateful_default_actions}.'''
        result = self._values.get("stateful_default_actions")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def stateful_engine_options(
        self,
    ) -> typing.Optional["NetworkfirewallFirewallPolicyFirewallPolicyStatefulEngineOptions"]:
        '''stateful_engine_options block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#stateful_engine_options NetworkfirewallFirewallPolicy#stateful_engine_options}
        '''
        result = self._values.get("stateful_engine_options")
        return typing.cast(typing.Optional["NetworkfirewallFirewallPolicyFirewallPolicyStatefulEngineOptions"], result)

    @builtins.property
    def stateful_rule_group_reference(
        self,
    ) -> typing.Optional[typing.List["NetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReference"]]:
        '''stateful_rule_group_reference block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#stateful_rule_group_reference NetworkfirewallFirewallPolicy#stateful_rule_group_reference}
        '''
        result = self._values.get("stateful_rule_group_reference")
        return typing.cast(typing.Optional[typing.List["NetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReference"]], result)

    @builtins.property
    def stateless_custom_action(
        self,
    ) -> typing.Optional[typing.List["NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomAction"]]:
        '''stateless_custom_action block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#stateless_custom_action NetworkfirewallFirewallPolicy#stateless_custom_action}
        '''
        result = self._values.get("stateless_custom_action")
        return typing.cast(typing.Optional[typing.List["NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomAction"]], result)

    @builtins.property
    def stateless_rule_group_reference(
        self,
    ) -> typing.Optional[typing.List["NetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReference"]]:
        '''stateless_rule_group_reference block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#stateless_rule_group_reference NetworkfirewallFirewallPolicy#stateless_rule_group_reference}
        '''
        result = self._values.get("stateless_rule_group_reference")
        return typing.cast(typing.Optional[typing.List["NetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReference"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallFirewallPolicyFirewallPolicy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NetworkfirewallFirewallPolicyFirewallPolicyOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallFirewallPolicyFirewallPolicyOutputReference",
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

    @jsii.member(jsii_name="putStatefulEngineOptions")
    def put_stateful_engine_options(self, *, rule_order: builtins.str) -> None:
        '''
        :param rule_order: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#rule_order NetworkfirewallFirewallPolicy#rule_order}.
        '''
        value = NetworkfirewallFirewallPolicyFirewallPolicyStatefulEngineOptions(
            rule_order=rule_order
        )

        return typing.cast(None, jsii.invoke(self, "putStatefulEngineOptions", [value]))

    @jsii.member(jsii_name="resetStatefulDefaultActions")
    def reset_stateful_default_actions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStatefulDefaultActions", []))

    @jsii.member(jsii_name="resetStatefulEngineOptions")
    def reset_stateful_engine_options(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStatefulEngineOptions", []))

    @jsii.member(jsii_name="resetStatefulRuleGroupReference")
    def reset_stateful_rule_group_reference(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStatefulRuleGroupReference", []))

    @jsii.member(jsii_name="resetStatelessCustomAction")
    def reset_stateless_custom_action(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStatelessCustomAction", []))

    @jsii.member(jsii_name="resetStatelessRuleGroupReference")
    def reset_stateless_rule_group_reference(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStatelessRuleGroupReference", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statefulEngineOptions")
    def stateful_engine_options(
        self,
    ) -> "NetworkfirewallFirewallPolicyFirewallPolicyStatefulEngineOptionsOutputReference":
        return typing.cast("NetworkfirewallFirewallPolicyFirewallPolicyStatefulEngineOptionsOutputReference", jsii.get(self, "statefulEngineOptions"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statefulDefaultActionsInput")
    def stateful_default_actions_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "statefulDefaultActionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statefulEngineOptionsInput")
    def stateful_engine_options_input(
        self,
    ) -> typing.Optional["NetworkfirewallFirewallPolicyFirewallPolicyStatefulEngineOptions"]:
        return typing.cast(typing.Optional["NetworkfirewallFirewallPolicyFirewallPolicyStatefulEngineOptions"], jsii.get(self, "statefulEngineOptionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statefulRuleGroupReferenceInput")
    def stateful_rule_group_reference_input(
        self,
    ) -> typing.Optional[typing.List["NetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReference"]]:
        return typing.cast(typing.Optional[typing.List["NetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReference"]], jsii.get(self, "statefulRuleGroupReferenceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statelessCustomActionInput")
    def stateless_custom_action_input(
        self,
    ) -> typing.Optional[typing.List["NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomAction"]]:
        return typing.cast(typing.Optional[typing.List["NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomAction"]], jsii.get(self, "statelessCustomActionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statelessDefaultActionsInput")
    def stateless_default_actions_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "statelessDefaultActionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statelessFragmentDefaultActionsInput")
    def stateless_fragment_default_actions_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "statelessFragmentDefaultActionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statelessRuleGroupReferenceInput")
    def stateless_rule_group_reference_input(
        self,
    ) -> typing.Optional[typing.List["NetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReference"]]:
        return typing.cast(typing.Optional[typing.List["NetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReference"]], jsii.get(self, "statelessRuleGroupReferenceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statefulDefaultActions")
    def stateful_default_actions(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "statefulDefaultActions"))

    @stateful_default_actions.setter
    def stateful_default_actions(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "statefulDefaultActions", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statefulRuleGroupReference")
    def stateful_rule_group_reference(
        self,
    ) -> typing.List["NetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReference"]:
        return typing.cast(typing.List["NetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReference"], jsii.get(self, "statefulRuleGroupReference"))

    @stateful_rule_group_reference.setter
    def stateful_rule_group_reference(
        self,
        value: typing.List["NetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReference"],
    ) -> None:
        jsii.set(self, "statefulRuleGroupReference", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statelessCustomAction")
    def stateless_custom_action(
        self,
    ) -> typing.List["NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomAction"]:
        return typing.cast(typing.List["NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomAction"], jsii.get(self, "statelessCustomAction"))

    @stateless_custom_action.setter
    def stateless_custom_action(
        self,
        value: typing.List["NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomAction"],
    ) -> None:
        jsii.set(self, "statelessCustomAction", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statelessDefaultActions")
    def stateless_default_actions(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "statelessDefaultActions"))

    @stateless_default_actions.setter
    def stateless_default_actions(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "statelessDefaultActions", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statelessFragmentDefaultActions")
    def stateless_fragment_default_actions(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "statelessFragmentDefaultActions"))

    @stateless_fragment_default_actions.setter
    def stateless_fragment_default_actions(
        self,
        value: typing.List[builtins.str],
    ) -> None:
        jsii.set(self, "statelessFragmentDefaultActions", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statelessRuleGroupReference")
    def stateless_rule_group_reference(
        self,
    ) -> typing.List["NetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReference"]:
        return typing.cast(typing.List["NetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReference"], jsii.get(self, "statelessRuleGroupReference"))

    @stateless_rule_group_reference.setter
    def stateless_rule_group_reference(
        self,
        value: typing.List["NetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReference"],
    ) -> None:
        jsii.set(self, "statelessRuleGroupReference", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[NetworkfirewallFirewallPolicyFirewallPolicy]:
        return typing.cast(typing.Optional[NetworkfirewallFirewallPolicyFirewallPolicy], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[NetworkfirewallFirewallPolicyFirewallPolicy],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallFirewallPolicyFirewallPolicyStatefulEngineOptions",
    jsii_struct_bases=[],
    name_mapping={"rule_order": "ruleOrder"},
)
class NetworkfirewallFirewallPolicyFirewallPolicyStatefulEngineOptions:
    def __init__(self, *, rule_order: builtins.str) -> None:
        '''
        :param rule_order: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#rule_order NetworkfirewallFirewallPolicy#rule_order}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "rule_order": rule_order,
        }

    @builtins.property
    def rule_order(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#rule_order NetworkfirewallFirewallPolicy#rule_order}.'''
        result = self._values.get("rule_order")
        assert result is not None, "Required property 'rule_order' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallFirewallPolicyFirewallPolicyStatefulEngineOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NetworkfirewallFirewallPolicyFirewallPolicyStatefulEngineOptionsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallFirewallPolicyFirewallPolicyStatefulEngineOptionsOutputReference",
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
    @jsii.member(jsii_name="ruleOrderInput")
    def rule_order_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ruleOrderInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ruleOrder")
    def rule_order(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ruleOrder"))

    @rule_order.setter
    def rule_order(self, value: builtins.str) -> None:
        jsii.set(self, "ruleOrder", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[NetworkfirewallFirewallPolicyFirewallPolicyStatefulEngineOptions]:
        return typing.cast(typing.Optional[NetworkfirewallFirewallPolicyFirewallPolicyStatefulEngineOptions], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[NetworkfirewallFirewallPolicyFirewallPolicyStatefulEngineOptions],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReference",
    jsii_struct_bases=[],
    name_mapping={"resource_arn": "resourceArn", "priority": "priority"},
)
class NetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReference:
    def __init__(
        self,
        *,
        resource_arn: builtins.str,
        priority: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param resource_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#resource_arn NetworkfirewallFirewallPolicy#resource_arn}.
        :param priority: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#priority NetworkfirewallFirewallPolicy#priority}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "resource_arn": resource_arn,
        }
        if priority is not None:
            self._values["priority"] = priority

    @builtins.property
    def resource_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#resource_arn NetworkfirewallFirewallPolicy#resource_arn}.'''
        result = self._values.get("resource_arn")
        assert result is not None, "Required property 'resource_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def priority(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#priority NetworkfirewallFirewallPolicy#priority}.'''
        result = self._values.get("priority")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReference(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomAction",
    jsii_struct_bases=[],
    name_mapping={
        "action_definition": "actionDefinition",
        "action_name": "actionName",
    },
)
class NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomAction:
    def __init__(
        self,
        *,
        action_definition: "NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinition",
        action_name: builtins.str,
    ) -> None:
        '''
        :param action_definition: action_definition block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#action_definition NetworkfirewallFirewallPolicy#action_definition}
        :param action_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#action_name NetworkfirewallFirewallPolicy#action_name}.
        '''
        if isinstance(action_definition, dict):
            action_definition = NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinition(**action_definition)
        self._values: typing.Dict[str, typing.Any] = {
            "action_definition": action_definition,
            "action_name": action_name,
        }

    @builtins.property
    def action_definition(
        self,
    ) -> "NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinition":
        '''action_definition block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#action_definition NetworkfirewallFirewallPolicy#action_definition}
        '''
        result = self._values.get("action_definition")
        assert result is not None, "Required property 'action_definition' is missing"
        return typing.cast("NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinition", result)

    @builtins.property
    def action_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#action_name NetworkfirewallFirewallPolicy#action_name}.'''
        result = self._values.get("action_name")
        assert result is not None, "Required property 'action_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomAction(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinition",
    jsii_struct_bases=[],
    name_mapping={"publish_metric_action": "publishMetricAction"},
)
class NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinition:
    def __init__(
        self,
        *,
        publish_metric_action: "NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricAction",
    ) -> None:
        '''
        :param publish_metric_action: publish_metric_action block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#publish_metric_action NetworkfirewallFirewallPolicy#publish_metric_action}
        '''
        if isinstance(publish_metric_action, dict):
            publish_metric_action = NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricAction(**publish_metric_action)
        self._values: typing.Dict[str, typing.Any] = {
            "publish_metric_action": publish_metric_action,
        }

    @builtins.property
    def publish_metric_action(
        self,
    ) -> "NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricAction":
        '''publish_metric_action block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#publish_metric_action NetworkfirewallFirewallPolicy#publish_metric_action}
        '''
        result = self._values.get("publish_metric_action")
        assert result is not None, "Required property 'publish_metric_action' is missing"
        return typing.cast("NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricAction", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinition(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionOutputReference",
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

    @jsii.member(jsii_name="putPublishMetricAction")
    def put_publish_metric_action(
        self,
        *,
        dimension: typing.Sequence["NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimension"],
    ) -> None:
        '''
        :param dimension: dimension block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#dimension NetworkfirewallFirewallPolicy#dimension}
        '''
        value = NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricAction(
            dimension=dimension
        )

        return typing.cast(None, jsii.invoke(self, "putPublishMetricAction", [value]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publishMetricAction")
    def publish_metric_action(
        self,
    ) -> "NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionOutputReference":
        return typing.cast("NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionOutputReference", jsii.get(self, "publishMetricAction"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publishMetricActionInput")
    def publish_metric_action_input(
        self,
    ) -> typing.Optional["NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricAction"]:
        return typing.cast(typing.Optional["NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricAction"], jsii.get(self, "publishMetricActionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinition]:
        return typing.cast(typing.Optional[NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinition], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinition],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricAction",
    jsii_struct_bases=[],
    name_mapping={"dimension": "dimension"},
)
class NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricAction:
    def __init__(
        self,
        *,
        dimension: typing.Sequence["NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimension"],
    ) -> None:
        '''
        :param dimension: dimension block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#dimension NetworkfirewallFirewallPolicy#dimension}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "dimension": dimension,
        }

    @builtins.property
    def dimension(
        self,
    ) -> typing.List["NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimension"]:
        '''dimension block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#dimension NetworkfirewallFirewallPolicy#dimension}
        '''
        result = self._values.get("dimension")
        assert result is not None, "Required property 'dimension' is missing"
        return typing.cast(typing.List["NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimension"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricAction(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimension",
    jsii_struct_bases=[],
    name_mapping={"value": "value"},
)
class NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimension:
    def __init__(self, *, value: builtins.str) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#value NetworkfirewallFirewallPolicy#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "value": value,
        }

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#value NetworkfirewallFirewallPolicy#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimension(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionOutputReference",
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
    @jsii.member(jsii_name="dimensionInput")
    def dimension_input(
        self,
    ) -> typing.Optional[typing.List[NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimension]]:
        return typing.cast(typing.Optional[typing.List[NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimension]], jsii.get(self, "dimensionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dimension")
    def dimension(
        self,
    ) -> typing.List[NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimension]:
        return typing.cast(typing.List[NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimension], jsii.get(self, "dimension"))

    @dimension.setter
    def dimension(
        self,
        value: typing.List[NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimension],
    ) -> None:
        jsii.set(self, "dimension", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricAction]:
        return typing.cast(typing.Optional[NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricAction], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricAction],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReference",
    jsii_struct_bases=[],
    name_mapping={"priority": "priority", "resource_arn": "resourceArn"},
)
class NetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReference:
    def __init__(self, *, priority: jsii.Number, resource_arn: builtins.str) -> None:
        '''
        :param priority: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#priority NetworkfirewallFirewallPolicy#priority}.
        :param resource_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#resource_arn NetworkfirewallFirewallPolicy#resource_arn}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "priority": priority,
            "resource_arn": resource_arn,
        }

    @builtins.property
    def priority(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#priority NetworkfirewallFirewallPolicy#priority}.'''
        result = self._values.get("priority")
        assert result is not None, "Required property 'priority' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def resource_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#resource_arn NetworkfirewallFirewallPolicy#resource_arn}.'''
        result = self._values.get("resource_arn")
        assert result is not None, "Required property 'resource_arn' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReference(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallFirewallSubnetMapping",
    jsii_struct_bases=[],
    name_mapping={"subnet_id": "subnetId"},
)
class NetworkfirewallFirewallSubnetMapping:
    def __init__(self, *, subnet_id: builtins.str) -> None:
        '''
        :param subnet_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall#subnet_id NetworkfirewallFirewall#subnet_id}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "subnet_id": subnet_id,
        }

    @builtins.property
    def subnet_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall#subnet_id NetworkfirewallFirewall#subnet_id}.'''
        result = self._values.get("subnet_id")
        assert result is not None, "Required property 'subnet_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallFirewallSubnetMapping(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NetworkfirewallLoggingConfiguration(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallLoggingConfiguration",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_logging_configuration aws_networkfirewall_logging_configuration}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        firewall_arn: builtins.str,
        logging_configuration: "NetworkfirewallLoggingConfigurationLoggingConfiguration",
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_logging_configuration aws_networkfirewall_logging_configuration} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param firewall_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_logging_configuration#firewall_arn NetworkfirewallLoggingConfiguration#firewall_arn}.
        :param logging_configuration: logging_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_logging_configuration#logging_configuration NetworkfirewallLoggingConfiguration#logging_configuration}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = NetworkfirewallLoggingConfigurationConfig(
            firewall_arn=firewall_arn,
            logging_configuration=logging_configuration,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putLoggingConfiguration")
    def put_logging_configuration(
        self,
        *,
        log_destination_config: typing.Sequence["NetworkfirewallLoggingConfigurationLoggingConfigurationLogDestinationConfig"],
    ) -> None:
        '''
        :param log_destination_config: log_destination_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_logging_configuration#log_destination_config NetworkfirewallLoggingConfiguration#log_destination_config}
        '''
        value = NetworkfirewallLoggingConfigurationLoggingConfiguration(
            log_destination_config=log_destination_config
        )

        return typing.cast(None, jsii.invoke(self, "putLoggingConfiguration", [value]))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="loggingConfiguration")
    def logging_configuration(
        self,
    ) -> "NetworkfirewallLoggingConfigurationLoggingConfigurationOutputReference":
        return typing.cast("NetworkfirewallLoggingConfigurationLoggingConfigurationOutputReference", jsii.get(self, "loggingConfiguration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firewallArnInput")
    def firewall_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "firewallArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="loggingConfigurationInput")
    def logging_configuration_input(
        self,
    ) -> typing.Optional["NetworkfirewallLoggingConfigurationLoggingConfiguration"]:
        return typing.cast(typing.Optional["NetworkfirewallLoggingConfigurationLoggingConfiguration"], jsii.get(self, "loggingConfigurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firewallArn")
    def firewall_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "firewallArn"))

    @firewall_arn.setter
    def firewall_arn(self, value: builtins.str) -> None:
        jsii.set(self, "firewallArn", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallLoggingConfigurationConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "firewall_arn": "firewallArn",
        "logging_configuration": "loggingConfiguration",
    },
)
class NetworkfirewallLoggingConfigurationConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        firewall_arn: builtins.str,
        logging_configuration: "NetworkfirewallLoggingConfigurationLoggingConfiguration",
    ) -> None:
        '''AWS Network Firewall.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param firewall_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_logging_configuration#firewall_arn NetworkfirewallLoggingConfiguration#firewall_arn}.
        :param logging_configuration: logging_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_logging_configuration#logging_configuration NetworkfirewallLoggingConfiguration#logging_configuration}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(logging_configuration, dict):
            logging_configuration = NetworkfirewallLoggingConfigurationLoggingConfiguration(**logging_configuration)
        self._values: typing.Dict[str, typing.Any] = {
            "firewall_arn": firewall_arn,
            "logging_configuration": logging_configuration,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider

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
    def firewall_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_logging_configuration#firewall_arn NetworkfirewallLoggingConfiguration#firewall_arn}.'''
        result = self._values.get("firewall_arn")
        assert result is not None, "Required property 'firewall_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def logging_configuration(
        self,
    ) -> "NetworkfirewallLoggingConfigurationLoggingConfiguration":
        '''logging_configuration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_logging_configuration#logging_configuration NetworkfirewallLoggingConfiguration#logging_configuration}
        '''
        result = self._values.get("logging_configuration")
        assert result is not None, "Required property 'logging_configuration' is missing"
        return typing.cast("NetworkfirewallLoggingConfigurationLoggingConfiguration", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallLoggingConfigurationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallLoggingConfigurationLoggingConfiguration",
    jsii_struct_bases=[],
    name_mapping={"log_destination_config": "logDestinationConfig"},
)
class NetworkfirewallLoggingConfigurationLoggingConfiguration:
    def __init__(
        self,
        *,
        log_destination_config: typing.Sequence["NetworkfirewallLoggingConfigurationLoggingConfigurationLogDestinationConfig"],
    ) -> None:
        '''
        :param log_destination_config: log_destination_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_logging_configuration#log_destination_config NetworkfirewallLoggingConfiguration#log_destination_config}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "log_destination_config": log_destination_config,
        }

    @builtins.property
    def log_destination_config(
        self,
    ) -> typing.List["NetworkfirewallLoggingConfigurationLoggingConfigurationLogDestinationConfig"]:
        '''log_destination_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_logging_configuration#log_destination_config NetworkfirewallLoggingConfiguration#log_destination_config}
        '''
        result = self._values.get("log_destination_config")
        assert result is not None, "Required property 'log_destination_config' is missing"
        return typing.cast(typing.List["NetworkfirewallLoggingConfigurationLoggingConfigurationLogDestinationConfig"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallLoggingConfigurationLoggingConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallLoggingConfigurationLoggingConfigurationLogDestinationConfig",
    jsii_struct_bases=[],
    name_mapping={
        "log_destination": "logDestination",
        "log_destination_type": "logDestinationType",
        "log_type": "logType",
    },
)
class NetworkfirewallLoggingConfigurationLoggingConfigurationLogDestinationConfig:
    def __init__(
        self,
        *,
        log_destination: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
        log_destination_type: builtins.str,
        log_type: builtins.str,
    ) -> None:
        '''
        :param log_destination: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_logging_configuration#log_destination NetworkfirewallLoggingConfiguration#log_destination}.
        :param log_destination_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_logging_configuration#log_destination_type NetworkfirewallLoggingConfiguration#log_destination_type}.
        :param log_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_logging_configuration#log_type NetworkfirewallLoggingConfiguration#log_type}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "log_destination": log_destination,
            "log_destination_type": log_destination_type,
            "log_type": log_type,
        }

    @builtins.property
    def log_destination(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_logging_configuration#log_destination NetworkfirewallLoggingConfiguration#log_destination}.'''
        result = self._values.get("log_destination")
        assert result is not None, "Required property 'log_destination' is missing"
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def log_destination_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_logging_configuration#log_destination_type NetworkfirewallLoggingConfiguration#log_destination_type}.'''
        result = self._values.get("log_destination_type")
        assert result is not None, "Required property 'log_destination_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def log_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_logging_configuration#log_type NetworkfirewallLoggingConfiguration#log_type}.'''
        result = self._values.get("log_type")
        assert result is not None, "Required property 'log_type' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallLoggingConfigurationLoggingConfigurationLogDestinationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NetworkfirewallLoggingConfigurationLoggingConfigurationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallLoggingConfigurationLoggingConfigurationOutputReference",
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
    @jsii.member(jsii_name="logDestinationConfigInput")
    def log_destination_config_input(
        self,
    ) -> typing.Optional[typing.List[NetworkfirewallLoggingConfigurationLoggingConfigurationLogDestinationConfig]]:
        return typing.cast(typing.Optional[typing.List[NetworkfirewallLoggingConfigurationLoggingConfigurationLogDestinationConfig]], jsii.get(self, "logDestinationConfigInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logDestinationConfig")
    def log_destination_config(
        self,
    ) -> typing.List[NetworkfirewallLoggingConfigurationLoggingConfigurationLogDestinationConfig]:
        return typing.cast(typing.List[NetworkfirewallLoggingConfigurationLoggingConfigurationLogDestinationConfig], jsii.get(self, "logDestinationConfig"))

    @log_destination_config.setter
    def log_destination_config(
        self,
        value: typing.List[NetworkfirewallLoggingConfigurationLoggingConfigurationLogDestinationConfig],
    ) -> None:
        jsii.set(self, "logDestinationConfig", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[NetworkfirewallLoggingConfigurationLoggingConfiguration]:
        return typing.cast(typing.Optional[NetworkfirewallLoggingConfigurationLoggingConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[NetworkfirewallLoggingConfigurationLoggingConfiguration],
    ) -> None:
        jsii.set(self, "internalValue", value)


class NetworkfirewallResourcePolicy(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallResourcePolicy",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_resource_policy aws_networkfirewall_resource_policy}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        policy: builtins.str,
        resource_arn: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_resource_policy aws_networkfirewall_resource_policy} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_resource_policy#policy NetworkfirewallResourcePolicy#policy}.
        :param resource_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_resource_policy#resource_arn NetworkfirewallResourcePolicy#resource_arn}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = NetworkfirewallResourcePolicyConfig(
            policy=policy,
            resource_arn=resource_arn,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyInput")
    def policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "policyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceArnInput")
    def resource_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "resourceArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policy")
    def policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policy"))

    @policy.setter
    def policy(self, value: builtins.str) -> None:
        jsii.set(self, "policy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceArn")
    def resource_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "resourceArn"))

    @resource_arn.setter
    def resource_arn(self, value: builtins.str) -> None:
        jsii.set(self, "resourceArn", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallResourcePolicyConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "policy": "policy",
        "resource_arn": "resourceArn",
    },
)
class NetworkfirewallResourcePolicyConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        policy: builtins.str,
        resource_arn: builtins.str,
    ) -> None:
        '''AWS Network Firewall.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_resource_policy#policy NetworkfirewallResourcePolicy#policy}.
        :param resource_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_resource_policy#resource_arn NetworkfirewallResourcePolicy#resource_arn}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "policy": policy,
            "resource_arn": resource_arn,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider

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
    def policy(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_resource_policy#policy NetworkfirewallResourcePolicy#policy}.'''
        result = self._values.get("policy")
        assert result is not None, "Required property 'policy' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def resource_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_resource_policy#resource_arn NetworkfirewallResourcePolicy#resource_arn}.'''
        result = self._values.get("resource_arn")
        assert result is not None, "Required property 'resource_arn' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallResourcePolicyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NetworkfirewallRuleGroup(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroup",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group aws_networkfirewall_rule_group}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        capacity: jsii.Number,
        name: builtins.str,
        type: builtins.str,
        description: typing.Optional[builtins.str] = None,
        rule_group: typing.Optional["NetworkfirewallRuleGroupRuleGroup"] = None,
        rules: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group aws_networkfirewall_rule_group} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param capacity: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#capacity NetworkfirewallRuleGroup#capacity}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#name NetworkfirewallRuleGroup#name}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#type NetworkfirewallRuleGroup#type}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#description NetworkfirewallRuleGroup#description}.
        :param rule_group: rule_group block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#rule_group NetworkfirewallRuleGroup#rule_group}
        :param rules: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#rules NetworkfirewallRuleGroup#rules}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#tags NetworkfirewallRuleGroup#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#tags_all NetworkfirewallRuleGroup#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = NetworkfirewallRuleGroupConfig(
            capacity=capacity,
            name=name,
            type=type,
            description=description,
            rule_group=rule_group,
            rules=rules,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putRuleGroup")
    def put_rule_group(
        self,
        *,
        rules_source: "NetworkfirewallRuleGroupRuleGroupRulesSource",
        rule_variables: typing.Optional["NetworkfirewallRuleGroupRuleGroupRuleVariables"] = None,
        stateful_rule_options: typing.Optional["NetworkfirewallRuleGroupRuleGroupStatefulRuleOptions"] = None,
    ) -> None:
        '''
        :param rules_source: rules_source block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#rules_source NetworkfirewallRuleGroup#rules_source}
        :param rule_variables: rule_variables block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#rule_variables NetworkfirewallRuleGroup#rule_variables}
        :param stateful_rule_options: stateful_rule_options block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#stateful_rule_options NetworkfirewallRuleGroup#stateful_rule_options}
        '''
        value = NetworkfirewallRuleGroupRuleGroup(
            rules_source=rules_source,
            rule_variables=rule_variables,
            stateful_rule_options=stateful_rule_options,
        )

        return typing.cast(None, jsii.invoke(self, "putRuleGroup", [value]))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetRuleGroup")
    def reset_rule_group(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRuleGroup", []))

    @jsii.member(jsii_name="resetRules")
    def reset_rules(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRules", []))

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
    @jsii.member(jsii_name="ruleGroup")
    def rule_group(self) -> "NetworkfirewallRuleGroupRuleGroupOutputReference":
        return typing.cast("NetworkfirewallRuleGroupRuleGroupOutputReference", jsii.get(self, "ruleGroup"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="updateToken")
    def update_token(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updateToken"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="capacityInput")
    def capacity_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "capacityInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ruleGroupInput")
    def rule_group_input(self) -> typing.Optional["NetworkfirewallRuleGroupRuleGroup"]:
        return typing.cast(typing.Optional["NetworkfirewallRuleGroupRuleGroup"], jsii.get(self, "ruleGroupInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rulesInput")
    def rules_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rulesInput"))

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
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="capacity")
    def capacity(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "capacity"))

    @capacity.setter
    def capacity(self, value: jsii.Number) -> None:
        jsii.set(self, "capacity", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rules")
    def rules(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rules"))

    @rules.setter
    def rules(self, value: builtins.str) -> None:
        jsii.set(self, "rules", value)

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
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        jsii.set(self, "type", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "capacity": "capacity",
        "name": "name",
        "type": "type",
        "description": "description",
        "rule_group": "ruleGroup",
        "rules": "rules",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class NetworkfirewallRuleGroupConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        capacity: jsii.Number,
        name: builtins.str,
        type: builtins.str,
        description: typing.Optional[builtins.str] = None,
        rule_group: typing.Optional["NetworkfirewallRuleGroupRuleGroup"] = None,
        rules: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS Network Firewall.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param capacity: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#capacity NetworkfirewallRuleGroup#capacity}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#name NetworkfirewallRuleGroup#name}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#type NetworkfirewallRuleGroup#type}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#description NetworkfirewallRuleGroup#description}.
        :param rule_group: rule_group block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#rule_group NetworkfirewallRuleGroup#rule_group}
        :param rules: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#rules NetworkfirewallRuleGroup#rules}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#tags NetworkfirewallRuleGroup#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#tags_all NetworkfirewallRuleGroup#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(rule_group, dict):
            rule_group = NetworkfirewallRuleGroupRuleGroup(**rule_group)
        self._values: typing.Dict[str, typing.Any] = {
            "capacity": capacity,
            "name": name,
            "type": type,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if description is not None:
            self._values["description"] = description
        if rule_group is not None:
            self._values["rule_group"] = rule_group
        if rules is not None:
            self._values["rules"] = rules
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
    def capacity(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#capacity NetworkfirewallRuleGroup#capacity}.'''
        result = self._values.get("capacity")
        assert result is not None, "Required property 'capacity' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#name NetworkfirewallRuleGroup#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#type NetworkfirewallRuleGroup#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#description NetworkfirewallRuleGroup#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rule_group(self) -> typing.Optional["NetworkfirewallRuleGroupRuleGroup"]:
        '''rule_group block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#rule_group NetworkfirewallRuleGroup#rule_group}
        '''
        result = self._values.get("rule_group")
        return typing.cast(typing.Optional["NetworkfirewallRuleGroupRuleGroup"], result)

    @builtins.property
    def rules(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#rules NetworkfirewallRuleGroup#rules}.'''
        result = self._values.get("rules")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#tags NetworkfirewallRuleGroup#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#tags_all NetworkfirewallRuleGroup#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallRuleGroupConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroup",
    jsii_struct_bases=[],
    name_mapping={
        "rules_source": "rulesSource",
        "rule_variables": "ruleVariables",
        "stateful_rule_options": "statefulRuleOptions",
    },
)
class NetworkfirewallRuleGroupRuleGroup:
    def __init__(
        self,
        *,
        rules_source: "NetworkfirewallRuleGroupRuleGroupRulesSource",
        rule_variables: typing.Optional["NetworkfirewallRuleGroupRuleGroupRuleVariables"] = None,
        stateful_rule_options: typing.Optional["NetworkfirewallRuleGroupRuleGroupStatefulRuleOptions"] = None,
    ) -> None:
        '''
        :param rules_source: rules_source block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#rules_source NetworkfirewallRuleGroup#rules_source}
        :param rule_variables: rule_variables block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#rule_variables NetworkfirewallRuleGroup#rule_variables}
        :param stateful_rule_options: stateful_rule_options block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#stateful_rule_options NetworkfirewallRuleGroup#stateful_rule_options}
        '''
        if isinstance(rules_source, dict):
            rules_source = NetworkfirewallRuleGroupRuleGroupRulesSource(**rules_source)
        if isinstance(rule_variables, dict):
            rule_variables = NetworkfirewallRuleGroupRuleGroupRuleVariables(**rule_variables)
        if isinstance(stateful_rule_options, dict):
            stateful_rule_options = NetworkfirewallRuleGroupRuleGroupStatefulRuleOptions(**stateful_rule_options)
        self._values: typing.Dict[str, typing.Any] = {
            "rules_source": rules_source,
        }
        if rule_variables is not None:
            self._values["rule_variables"] = rule_variables
        if stateful_rule_options is not None:
            self._values["stateful_rule_options"] = stateful_rule_options

    @builtins.property
    def rules_source(self) -> "NetworkfirewallRuleGroupRuleGroupRulesSource":
        '''rules_source block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#rules_source NetworkfirewallRuleGroup#rules_source}
        '''
        result = self._values.get("rules_source")
        assert result is not None, "Required property 'rules_source' is missing"
        return typing.cast("NetworkfirewallRuleGroupRuleGroupRulesSource", result)

    @builtins.property
    def rule_variables(
        self,
    ) -> typing.Optional["NetworkfirewallRuleGroupRuleGroupRuleVariables"]:
        '''rule_variables block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#rule_variables NetworkfirewallRuleGroup#rule_variables}
        '''
        result = self._values.get("rule_variables")
        return typing.cast(typing.Optional["NetworkfirewallRuleGroupRuleGroupRuleVariables"], result)

    @builtins.property
    def stateful_rule_options(
        self,
    ) -> typing.Optional["NetworkfirewallRuleGroupRuleGroupStatefulRuleOptions"]:
        '''stateful_rule_options block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#stateful_rule_options NetworkfirewallRuleGroup#stateful_rule_options}
        '''
        result = self._values.get("stateful_rule_options")
        return typing.cast(typing.Optional["NetworkfirewallRuleGroupRuleGroupStatefulRuleOptions"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallRuleGroupRuleGroup(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NetworkfirewallRuleGroupRuleGroupOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupOutputReference",
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

    @jsii.member(jsii_name="putRulesSource")
    def put_rules_source(
        self,
        *,
        rules_source_list: typing.Optional["NetworkfirewallRuleGroupRuleGroupRulesSourceRulesSourceList"] = None,
        rules_string: typing.Optional[builtins.str] = None,
        stateful_rule: typing.Optional[typing.Sequence["NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRule"]] = None,
        stateless_rules_and_custom_actions: typing.Optional["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActions"] = None,
    ) -> None:
        '''
        :param rules_source_list: rules_source_list block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#rules_source_list NetworkfirewallRuleGroup#rules_source_list}
        :param rules_string: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#rules_string NetworkfirewallRuleGroup#rules_string}.
        :param stateful_rule: stateful_rule block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#stateful_rule NetworkfirewallRuleGroup#stateful_rule}
        :param stateless_rules_and_custom_actions: stateless_rules_and_custom_actions block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#stateless_rules_and_custom_actions NetworkfirewallRuleGroup#stateless_rules_and_custom_actions}
        '''
        value = NetworkfirewallRuleGroupRuleGroupRulesSource(
            rules_source_list=rules_source_list,
            rules_string=rules_string,
            stateful_rule=stateful_rule,
            stateless_rules_and_custom_actions=stateless_rules_and_custom_actions,
        )

        return typing.cast(None, jsii.invoke(self, "putRulesSource", [value]))

    @jsii.member(jsii_name="putRuleVariables")
    def put_rule_variables(
        self,
        *,
        ip_sets: typing.Optional[typing.Sequence["NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSets"]] = None,
        port_sets: typing.Optional[typing.Sequence["NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSets"]] = None,
    ) -> None:
        '''
        :param ip_sets: ip_sets block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#ip_sets NetworkfirewallRuleGroup#ip_sets}
        :param port_sets: port_sets block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#port_sets NetworkfirewallRuleGroup#port_sets}
        '''
        value = NetworkfirewallRuleGroupRuleGroupRuleVariables(
            ip_sets=ip_sets, port_sets=port_sets
        )

        return typing.cast(None, jsii.invoke(self, "putRuleVariables", [value]))

    @jsii.member(jsii_name="putStatefulRuleOptions")
    def put_stateful_rule_options(self, *, rule_order: builtins.str) -> None:
        '''
        :param rule_order: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#rule_order NetworkfirewallRuleGroup#rule_order}.
        '''
        value = NetworkfirewallRuleGroupRuleGroupStatefulRuleOptions(
            rule_order=rule_order
        )

        return typing.cast(None, jsii.invoke(self, "putStatefulRuleOptions", [value]))

    @jsii.member(jsii_name="resetRuleVariables")
    def reset_rule_variables(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRuleVariables", []))

    @jsii.member(jsii_name="resetStatefulRuleOptions")
    def reset_stateful_rule_options(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStatefulRuleOptions", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rulesSource")
    def rules_source(
        self,
    ) -> "NetworkfirewallRuleGroupRuleGroupRulesSourceOutputReference":
        return typing.cast("NetworkfirewallRuleGroupRuleGroupRulesSourceOutputReference", jsii.get(self, "rulesSource"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ruleVariables")
    def rule_variables(
        self,
    ) -> "NetworkfirewallRuleGroupRuleGroupRuleVariablesOutputReference":
        return typing.cast("NetworkfirewallRuleGroupRuleGroupRuleVariablesOutputReference", jsii.get(self, "ruleVariables"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statefulRuleOptions")
    def stateful_rule_options(
        self,
    ) -> "NetworkfirewallRuleGroupRuleGroupStatefulRuleOptionsOutputReference":
        return typing.cast("NetworkfirewallRuleGroupRuleGroupStatefulRuleOptionsOutputReference", jsii.get(self, "statefulRuleOptions"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rulesSourceInput")
    def rules_source_input(
        self,
    ) -> typing.Optional["NetworkfirewallRuleGroupRuleGroupRulesSource"]:
        return typing.cast(typing.Optional["NetworkfirewallRuleGroupRuleGroupRulesSource"], jsii.get(self, "rulesSourceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ruleVariablesInput")
    def rule_variables_input(
        self,
    ) -> typing.Optional["NetworkfirewallRuleGroupRuleGroupRuleVariables"]:
        return typing.cast(typing.Optional["NetworkfirewallRuleGroupRuleGroupRuleVariables"], jsii.get(self, "ruleVariablesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statefulRuleOptionsInput")
    def stateful_rule_options_input(
        self,
    ) -> typing.Optional["NetworkfirewallRuleGroupRuleGroupStatefulRuleOptions"]:
        return typing.cast(typing.Optional["NetworkfirewallRuleGroupRuleGroupStatefulRuleOptions"], jsii.get(self, "statefulRuleOptionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[NetworkfirewallRuleGroupRuleGroup]:
        return typing.cast(typing.Optional[NetworkfirewallRuleGroupRuleGroup], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[NetworkfirewallRuleGroupRuleGroup],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRuleVariables",
    jsii_struct_bases=[],
    name_mapping={"ip_sets": "ipSets", "port_sets": "portSets"},
)
class NetworkfirewallRuleGroupRuleGroupRuleVariables:
    def __init__(
        self,
        *,
        ip_sets: typing.Optional[typing.Sequence["NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSets"]] = None,
        port_sets: typing.Optional[typing.Sequence["NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSets"]] = None,
    ) -> None:
        '''
        :param ip_sets: ip_sets block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#ip_sets NetworkfirewallRuleGroup#ip_sets}
        :param port_sets: port_sets block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#port_sets NetworkfirewallRuleGroup#port_sets}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if ip_sets is not None:
            self._values["ip_sets"] = ip_sets
        if port_sets is not None:
            self._values["port_sets"] = port_sets

    @builtins.property
    def ip_sets(
        self,
    ) -> typing.Optional[typing.List["NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSets"]]:
        '''ip_sets block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#ip_sets NetworkfirewallRuleGroup#ip_sets}
        '''
        result = self._values.get("ip_sets")
        return typing.cast(typing.Optional[typing.List["NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSets"]], result)

    @builtins.property
    def port_sets(
        self,
    ) -> typing.Optional[typing.List["NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSets"]]:
        '''port_sets block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#port_sets NetworkfirewallRuleGroup#port_sets}
        '''
        result = self._values.get("port_sets")
        return typing.cast(typing.Optional[typing.List["NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSets"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallRuleGroupRuleGroupRuleVariables(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSets",
    jsii_struct_bases=[],
    name_mapping={"ip_set": "ipSet", "key": "key"},
)
class NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSets:
    def __init__(
        self,
        *,
        ip_set: "NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSetsIpSet",
        key: builtins.str,
    ) -> None:
        '''
        :param ip_set: ip_set block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#ip_set NetworkfirewallRuleGroup#ip_set}
        :param key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#key NetworkfirewallRuleGroup#key}.
        '''
        if isinstance(ip_set, dict):
            ip_set = NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSetsIpSet(**ip_set)
        self._values: typing.Dict[str, typing.Any] = {
            "ip_set": ip_set,
            "key": key,
        }

    @builtins.property
    def ip_set(self) -> "NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSetsIpSet":
        '''ip_set block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#ip_set NetworkfirewallRuleGroup#ip_set}
        '''
        result = self._values.get("ip_set")
        assert result is not None, "Required property 'ip_set' is missing"
        return typing.cast("NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSetsIpSet", result)

    @builtins.property
    def key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#key NetworkfirewallRuleGroup#key}.'''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSets(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSetsIpSet",
    jsii_struct_bases=[],
    name_mapping={"definition": "definition"},
)
class NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSetsIpSet:
    def __init__(self, *, definition: typing.Sequence[builtins.str]) -> None:
        '''
        :param definition: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#definition NetworkfirewallRuleGroup#definition}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "definition": definition,
        }

    @builtins.property
    def definition(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#definition NetworkfirewallRuleGroup#definition}.'''
        result = self._values.get("definition")
        assert result is not None, "Required property 'definition' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSetsIpSet(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSetsIpSetOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSetsIpSetOutputReference",
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
    @jsii.member(jsii_name="definitionInput")
    def definition_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "definitionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="definition")
    def definition(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "definition"))

    @definition.setter
    def definition(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "definition", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSetsIpSet]:
        return typing.cast(typing.Optional[NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSetsIpSet], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSetsIpSet],
    ) -> None:
        jsii.set(self, "internalValue", value)


class NetworkfirewallRuleGroupRuleGroupRuleVariablesOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRuleVariablesOutputReference",
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

    @jsii.member(jsii_name="resetIpSets")
    def reset_ip_sets(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIpSets", []))

    @jsii.member(jsii_name="resetPortSets")
    def reset_port_sets(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPortSets", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipSetsInput")
    def ip_sets_input(
        self,
    ) -> typing.Optional[typing.List[NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSets]]:
        return typing.cast(typing.Optional[typing.List[NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSets]], jsii.get(self, "ipSetsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="portSetsInput")
    def port_sets_input(
        self,
    ) -> typing.Optional[typing.List["NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSets"]]:
        return typing.cast(typing.Optional[typing.List["NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSets"]], jsii.get(self, "portSetsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipSets")
    def ip_sets(
        self,
    ) -> typing.List[NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSets]:
        return typing.cast(typing.List[NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSets], jsii.get(self, "ipSets"))

    @ip_sets.setter
    def ip_sets(
        self,
        value: typing.List[NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSets],
    ) -> None:
        jsii.set(self, "ipSets", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="portSets")
    def port_sets(
        self,
    ) -> typing.List["NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSets"]:
        return typing.cast(typing.List["NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSets"], jsii.get(self, "portSets"))

    @port_sets.setter
    def port_sets(
        self,
        value: typing.List["NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSets"],
    ) -> None:
        jsii.set(self, "portSets", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[NetworkfirewallRuleGroupRuleGroupRuleVariables]:
        return typing.cast(typing.Optional[NetworkfirewallRuleGroupRuleGroupRuleVariables], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[NetworkfirewallRuleGroupRuleGroupRuleVariables],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSets",
    jsii_struct_bases=[],
    name_mapping={"key": "key", "port_set": "portSet"},
)
class NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSets:
    def __init__(
        self,
        *,
        key: builtins.str,
        port_set: "NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSetsPortSet",
    ) -> None:
        '''
        :param key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#key NetworkfirewallRuleGroup#key}.
        :param port_set: port_set block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#port_set NetworkfirewallRuleGroup#port_set}
        '''
        if isinstance(port_set, dict):
            port_set = NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSetsPortSet(**port_set)
        self._values: typing.Dict[str, typing.Any] = {
            "key": key,
            "port_set": port_set,
        }

    @builtins.property
    def key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#key NetworkfirewallRuleGroup#key}.'''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def port_set(
        self,
    ) -> "NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSetsPortSet":
        '''port_set block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#port_set NetworkfirewallRuleGroup#port_set}
        '''
        result = self._values.get("port_set")
        assert result is not None, "Required property 'port_set' is missing"
        return typing.cast("NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSetsPortSet", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSets(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSetsPortSet",
    jsii_struct_bases=[],
    name_mapping={"definition": "definition"},
)
class NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSetsPortSet:
    def __init__(self, *, definition: typing.Sequence[builtins.str]) -> None:
        '''
        :param definition: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#definition NetworkfirewallRuleGroup#definition}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "definition": definition,
        }

    @builtins.property
    def definition(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#definition NetworkfirewallRuleGroup#definition}.'''
        result = self._values.get("definition")
        assert result is not None, "Required property 'definition' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSetsPortSet(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSetsPortSetOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSetsPortSetOutputReference",
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
    @jsii.member(jsii_name="definitionInput")
    def definition_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "definitionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="definition")
    def definition(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "definition"))

    @definition.setter
    def definition(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "definition", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSetsPortSet]:
        return typing.cast(typing.Optional[NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSetsPortSet], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSetsPortSet],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSource",
    jsii_struct_bases=[],
    name_mapping={
        "rules_source_list": "rulesSourceList",
        "rules_string": "rulesString",
        "stateful_rule": "statefulRule",
        "stateless_rules_and_custom_actions": "statelessRulesAndCustomActions",
    },
)
class NetworkfirewallRuleGroupRuleGroupRulesSource:
    def __init__(
        self,
        *,
        rules_source_list: typing.Optional["NetworkfirewallRuleGroupRuleGroupRulesSourceRulesSourceList"] = None,
        rules_string: typing.Optional[builtins.str] = None,
        stateful_rule: typing.Optional[typing.Sequence["NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRule"]] = None,
        stateless_rules_and_custom_actions: typing.Optional["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActions"] = None,
    ) -> None:
        '''
        :param rules_source_list: rules_source_list block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#rules_source_list NetworkfirewallRuleGroup#rules_source_list}
        :param rules_string: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#rules_string NetworkfirewallRuleGroup#rules_string}.
        :param stateful_rule: stateful_rule block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#stateful_rule NetworkfirewallRuleGroup#stateful_rule}
        :param stateless_rules_and_custom_actions: stateless_rules_and_custom_actions block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#stateless_rules_and_custom_actions NetworkfirewallRuleGroup#stateless_rules_and_custom_actions}
        '''
        if isinstance(rules_source_list, dict):
            rules_source_list = NetworkfirewallRuleGroupRuleGroupRulesSourceRulesSourceList(**rules_source_list)
        if isinstance(stateless_rules_and_custom_actions, dict):
            stateless_rules_and_custom_actions = NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActions(**stateless_rules_and_custom_actions)
        self._values: typing.Dict[str, typing.Any] = {}
        if rules_source_list is not None:
            self._values["rules_source_list"] = rules_source_list
        if rules_string is not None:
            self._values["rules_string"] = rules_string
        if stateful_rule is not None:
            self._values["stateful_rule"] = stateful_rule
        if stateless_rules_and_custom_actions is not None:
            self._values["stateless_rules_and_custom_actions"] = stateless_rules_and_custom_actions

    @builtins.property
    def rules_source_list(
        self,
    ) -> typing.Optional["NetworkfirewallRuleGroupRuleGroupRulesSourceRulesSourceList"]:
        '''rules_source_list block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#rules_source_list NetworkfirewallRuleGroup#rules_source_list}
        '''
        result = self._values.get("rules_source_list")
        return typing.cast(typing.Optional["NetworkfirewallRuleGroupRuleGroupRulesSourceRulesSourceList"], result)

    @builtins.property
    def rules_string(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#rules_string NetworkfirewallRuleGroup#rules_string}.'''
        result = self._values.get("rules_string")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def stateful_rule(
        self,
    ) -> typing.Optional[typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRule"]]:
        '''stateful_rule block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#stateful_rule NetworkfirewallRuleGroup#stateful_rule}
        '''
        result = self._values.get("stateful_rule")
        return typing.cast(typing.Optional[typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRule"]], result)

    @builtins.property
    def stateless_rules_and_custom_actions(
        self,
    ) -> typing.Optional["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActions"]:
        '''stateless_rules_and_custom_actions block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#stateless_rules_and_custom_actions NetworkfirewallRuleGroup#stateless_rules_and_custom_actions}
        '''
        result = self._values.get("stateless_rules_and_custom_actions")
        return typing.cast(typing.Optional["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActions"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallRuleGroupRuleGroupRulesSource(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NetworkfirewallRuleGroupRuleGroupRulesSourceOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSourceOutputReference",
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

    @jsii.member(jsii_name="putRulesSourceList")
    def put_rules_source_list(
        self,
        *,
        generated_rules_type: builtins.str,
        targets: typing.Sequence[builtins.str],
        target_types: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param generated_rules_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#generated_rules_type NetworkfirewallRuleGroup#generated_rules_type}.
        :param targets: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#targets NetworkfirewallRuleGroup#targets}.
        :param target_types: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#target_types NetworkfirewallRuleGroup#target_types}.
        '''
        value = NetworkfirewallRuleGroupRuleGroupRulesSourceRulesSourceList(
            generated_rules_type=generated_rules_type,
            targets=targets,
            target_types=target_types,
        )

        return typing.cast(None, jsii.invoke(self, "putRulesSourceList", [value]))

    @jsii.member(jsii_name="putStatelessRulesAndCustomActions")
    def put_stateless_rules_and_custom_actions(
        self,
        *,
        stateless_rule: typing.Sequence["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRule"],
        custom_action: typing.Optional[typing.Sequence["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomAction"]] = None,
    ) -> None:
        '''
        :param stateless_rule: stateless_rule block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#stateless_rule NetworkfirewallRuleGroup#stateless_rule}
        :param custom_action: custom_action block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#custom_action NetworkfirewallRuleGroup#custom_action}
        '''
        value = NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActions(
            stateless_rule=stateless_rule, custom_action=custom_action
        )

        return typing.cast(None, jsii.invoke(self, "putStatelessRulesAndCustomActions", [value]))

    @jsii.member(jsii_name="resetRulesSourceList")
    def reset_rules_source_list(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRulesSourceList", []))

    @jsii.member(jsii_name="resetRulesString")
    def reset_rules_string(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRulesString", []))

    @jsii.member(jsii_name="resetStatefulRule")
    def reset_stateful_rule(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStatefulRule", []))

    @jsii.member(jsii_name="resetStatelessRulesAndCustomActions")
    def reset_stateless_rules_and_custom_actions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStatelessRulesAndCustomActions", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rulesSourceList")
    def rules_source_list(
        self,
    ) -> "NetworkfirewallRuleGroupRuleGroupRulesSourceRulesSourceListOutputReference":
        return typing.cast("NetworkfirewallRuleGroupRuleGroupRulesSourceRulesSourceListOutputReference", jsii.get(self, "rulesSourceList"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statelessRulesAndCustomActions")
    def stateless_rules_and_custom_actions(
        self,
    ) -> "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsOutputReference":
        return typing.cast("NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsOutputReference", jsii.get(self, "statelessRulesAndCustomActions"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rulesSourceListInput")
    def rules_source_list_input(
        self,
    ) -> typing.Optional["NetworkfirewallRuleGroupRuleGroupRulesSourceRulesSourceList"]:
        return typing.cast(typing.Optional["NetworkfirewallRuleGroupRuleGroupRulesSourceRulesSourceList"], jsii.get(self, "rulesSourceListInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rulesStringInput")
    def rules_string_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rulesStringInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statefulRuleInput")
    def stateful_rule_input(
        self,
    ) -> typing.Optional[typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRule"]]:
        return typing.cast(typing.Optional[typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRule"]], jsii.get(self, "statefulRuleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statelessRulesAndCustomActionsInput")
    def stateless_rules_and_custom_actions_input(
        self,
    ) -> typing.Optional["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActions"]:
        return typing.cast(typing.Optional["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActions"], jsii.get(self, "statelessRulesAndCustomActionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rulesString")
    def rules_string(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rulesString"))

    @rules_string.setter
    def rules_string(self, value: builtins.str) -> None:
        jsii.set(self, "rulesString", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statefulRule")
    def stateful_rule(
        self,
    ) -> typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRule"]:
        return typing.cast(typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRule"], jsii.get(self, "statefulRule"))

    @stateful_rule.setter
    def stateful_rule(
        self,
        value: typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRule"],
    ) -> None:
        jsii.set(self, "statefulRule", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[NetworkfirewallRuleGroupRuleGroupRulesSource]:
        return typing.cast(typing.Optional[NetworkfirewallRuleGroupRuleGroupRulesSource], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[NetworkfirewallRuleGroupRuleGroupRulesSource],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSourceRulesSourceList",
    jsii_struct_bases=[],
    name_mapping={
        "generated_rules_type": "generatedRulesType",
        "targets": "targets",
        "target_types": "targetTypes",
    },
)
class NetworkfirewallRuleGroupRuleGroupRulesSourceRulesSourceList:
    def __init__(
        self,
        *,
        generated_rules_type: builtins.str,
        targets: typing.Sequence[builtins.str],
        target_types: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param generated_rules_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#generated_rules_type NetworkfirewallRuleGroup#generated_rules_type}.
        :param targets: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#targets NetworkfirewallRuleGroup#targets}.
        :param target_types: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#target_types NetworkfirewallRuleGroup#target_types}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "generated_rules_type": generated_rules_type,
            "targets": targets,
            "target_types": target_types,
        }

    @builtins.property
    def generated_rules_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#generated_rules_type NetworkfirewallRuleGroup#generated_rules_type}.'''
        result = self._values.get("generated_rules_type")
        assert result is not None, "Required property 'generated_rules_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def targets(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#targets NetworkfirewallRuleGroup#targets}.'''
        result = self._values.get("targets")
        assert result is not None, "Required property 'targets' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def target_types(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#target_types NetworkfirewallRuleGroup#target_types}.'''
        result = self._values.get("target_types")
        assert result is not None, "Required property 'target_types' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallRuleGroupRuleGroupRulesSourceRulesSourceList(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NetworkfirewallRuleGroupRuleGroupRulesSourceRulesSourceListOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSourceRulesSourceListOutputReference",
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
    @jsii.member(jsii_name="generatedRulesTypeInput")
    def generated_rules_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "generatedRulesTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetsInput")
    def targets_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "targetsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetTypesInput")
    def target_types_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "targetTypesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="generatedRulesType")
    def generated_rules_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "generatedRulesType"))

    @generated_rules_type.setter
    def generated_rules_type(self, value: builtins.str) -> None:
        jsii.set(self, "generatedRulesType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targets")
    def targets(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "targets"))

    @targets.setter
    def targets(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "targets", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetTypes")
    def target_types(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "targetTypes"))

    @target_types.setter
    def target_types(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "targetTypes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[NetworkfirewallRuleGroupRuleGroupRulesSourceRulesSourceList]:
        return typing.cast(typing.Optional[NetworkfirewallRuleGroupRuleGroupRulesSourceRulesSourceList], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[NetworkfirewallRuleGroupRuleGroupRulesSourceRulesSourceList],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRule",
    jsii_struct_bases=[],
    name_mapping={"action": "action", "header": "header", "rule_option": "ruleOption"},
)
class NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRule:
    def __init__(
        self,
        *,
        action: builtins.str,
        header: "NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleHeader",
        rule_option: typing.Sequence["NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleRuleOption"],
    ) -> None:
        '''
        :param action: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#action NetworkfirewallRuleGroup#action}.
        :param header: header block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#header NetworkfirewallRuleGroup#header}
        :param rule_option: rule_option block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#rule_option NetworkfirewallRuleGroup#rule_option}
        '''
        if isinstance(header, dict):
            header = NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleHeader(**header)
        self._values: typing.Dict[str, typing.Any] = {
            "action": action,
            "header": header,
            "rule_option": rule_option,
        }

    @builtins.property
    def action(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#action NetworkfirewallRuleGroup#action}.'''
        result = self._values.get("action")
        assert result is not None, "Required property 'action' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def header(
        self,
    ) -> "NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleHeader":
        '''header block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#header NetworkfirewallRuleGroup#header}
        '''
        result = self._values.get("header")
        assert result is not None, "Required property 'header' is missing"
        return typing.cast("NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleHeader", result)

    @builtins.property
    def rule_option(
        self,
    ) -> typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleRuleOption"]:
        '''rule_option block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#rule_option NetworkfirewallRuleGroup#rule_option}
        '''
        result = self._values.get("rule_option")
        assert result is not None, "Required property 'rule_option' is missing"
        return typing.cast(typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleRuleOption"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleHeader",
    jsii_struct_bases=[],
    name_mapping={
        "destination": "destination",
        "destination_port": "destinationPort",
        "direction": "direction",
        "protocol": "protocol",
        "source": "source",
        "source_port": "sourcePort",
    },
)
class NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleHeader:
    def __init__(
        self,
        *,
        destination: builtins.str,
        destination_port: builtins.str,
        direction: builtins.str,
        protocol: builtins.str,
        source: builtins.str,
        source_port: builtins.str,
    ) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#destination NetworkfirewallRuleGroup#destination}.
        :param destination_port: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#destination_port NetworkfirewallRuleGroup#destination_port}.
        :param direction: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#direction NetworkfirewallRuleGroup#direction}.
        :param protocol: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#protocol NetworkfirewallRuleGroup#protocol}.
        :param source: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#source NetworkfirewallRuleGroup#source}.
        :param source_port: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#source_port NetworkfirewallRuleGroup#source_port}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "destination": destination,
            "destination_port": destination_port,
            "direction": direction,
            "protocol": protocol,
            "source": source,
            "source_port": source_port,
        }

    @builtins.property
    def destination(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#destination NetworkfirewallRuleGroup#destination}.'''
        result = self._values.get("destination")
        assert result is not None, "Required property 'destination' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def destination_port(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#destination_port NetworkfirewallRuleGroup#destination_port}.'''
        result = self._values.get("destination_port")
        assert result is not None, "Required property 'destination_port' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def direction(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#direction NetworkfirewallRuleGroup#direction}.'''
        result = self._values.get("direction")
        assert result is not None, "Required property 'direction' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def protocol(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#protocol NetworkfirewallRuleGroup#protocol}.'''
        result = self._values.get("protocol")
        assert result is not None, "Required property 'protocol' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def source(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#source NetworkfirewallRuleGroup#source}.'''
        result = self._values.get("source")
        assert result is not None, "Required property 'source' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def source_port(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#source_port NetworkfirewallRuleGroup#source_port}.'''
        result = self._values.get("source_port")
        assert result is not None, "Required property 'source_port' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleHeader(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleHeaderOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleHeaderOutputReference",
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
    @jsii.member(jsii_name="destinationInput")
    def destination_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "destinationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="destinationPortInput")
    def destination_port_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "destinationPortInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="directionInput")
    def direction_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "directionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="protocolInput")
    def protocol_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "protocolInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceInput")
    def source_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourcePortInput")
    def source_port_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourcePortInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="destination")
    def destination(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destination"))

    @destination.setter
    def destination(self, value: builtins.str) -> None:
        jsii.set(self, "destination", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="destinationPort")
    def destination_port(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destinationPort"))

    @destination_port.setter
    def destination_port(self, value: builtins.str) -> None:
        jsii.set(self, "destinationPort", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="direction")
    def direction(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "direction"))

    @direction.setter
    def direction(self, value: builtins.str) -> None:
        jsii.set(self, "direction", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="protocol")
    def protocol(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "protocol"))

    @protocol.setter
    def protocol(self, value: builtins.str) -> None:
        jsii.set(self, "protocol", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="source")
    def source(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "source"))

    @source.setter
    def source(self, value: builtins.str) -> None:
        jsii.set(self, "source", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourcePort")
    def source_port(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourcePort"))

    @source_port.setter
    def source_port(self, value: builtins.str) -> None:
        jsii.set(self, "sourcePort", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleHeader]:
        return typing.cast(typing.Optional[NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleHeader], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleHeader],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleRuleOption",
    jsii_struct_bases=[],
    name_mapping={"keyword": "keyword", "settings": "settings"},
)
class NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleRuleOption:
    def __init__(
        self,
        *,
        keyword: builtins.str,
        settings: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param keyword: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#keyword NetworkfirewallRuleGroup#keyword}.
        :param settings: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#settings NetworkfirewallRuleGroup#settings}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "keyword": keyword,
        }
        if settings is not None:
            self._values["settings"] = settings

    @builtins.property
    def keyword(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#keyword NetworkfirewallRuleGroup#keyword}.'''
        result = self._values.get("keyword")
        assert result is not None, "Required property 'keyword' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def settings(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#settings NetworkfirewallRuleGroup#settings}.'''
        result = self._values.get("settings")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleRuleOption(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActions",
    jsii_struct_bases=[],
    name_mapping={"stateless_rule": "statelessRule", "custom_action": "customAction"},
)
class NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActions:
    def __init__(
        self,
        *,
        stateless_rule: typing.Sequence["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRule"],
        custom_action: typing.Optional[typing.Sequence["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomAction"]] = None,
    ) -> None:
        '''
        :param stateless_rule: stateless_rule block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#stateless_rule NetworkfirewallRuleGroup#stateless_rule}
        :param custom_action: custom_action block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#custom_action NetworkfirewallRuleGroup#custom_action}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "stateless_rule": stateless_rule,
        }
        if custom_action is not None:
            self._values["custom_action"] = custom_action

    @builtins.property
    def stateless_rule(
        self,
    ) -> typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRule"]:
        '''stateless_rule block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#stateless_rule NetworkfirewallRuleGroup#stateless_rule}
        '''
        result = self._values.get("stateless_rule")
        assert result is not None, "Required property 'stateless_rule' is missing"
        return typing.cast(typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRule"], result)

    @builtins.property
    def custom_action(
        self,
    ) -> typing.Optional[typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomAction"]]:
        '''custom_action block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#custom_action NetworkfirewallRuleGroup#custom_action}
        '''
        result = self._values.get("custom_action")
        return typing.cast(typing.Optional[typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomAction"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomAction",
    jsii_struct_bases=[],
    name_mapping={
        "action_definition": "actionDefinition",
        "action_name": "actionName",
    },
)
class NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomAction:
    def __init__(
        self,
        *,
        action_definition: "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinition",
        action_name: builtins.str,
    ) -> None:
        '''
        :param action_definition: action_definition block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#action_definition NetworkfirewallRuleGroup#action_definition}
        :param action_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#action_name NetworkfirewallRuleGroup#action_name}.
        '''
        if isinstance(action_definition, dict):
            action_definition = NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinition(**action_definition)
        self._values: typing.Dict[str, typing.Any] = {
            "action_definition": action_definition,
            "action_name": action_name,
        }

    @builtins.property
    def action_definition(
        self,
    ) -> "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinition":
        '''action_definition block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#action_definition NetworkfirewallRuleGroup#action_definition}
        '''
        result = self._values.get("action_definition")
        assert result is not None, "Required property 'action_definition' is missing"
        return typing.cast("NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinition", result)

    @builtins.property
    def action_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#action_name NetworkfirewallRuleGroup#action_name}.'''
        result = self._values.get("action_name")
        assert result is not None, "Required property 'action_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomAction(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinition",
    jsii_struct_bases=[],
    name_mapping={"publish_metric_action": "publishMetricAction"},
)
class NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinition:
    def __init__(
        self,
        *,
        publish_metric_action: "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricAction",
    ) -> None:
        '''
        :param publish_metric_action: publish_metric_action block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#publish_metric_action NetworkfirewallRuleGroup#publish_metric_action}
        '''
        if isinstance(publish_metric_action, dict):
            publish_metric_action = NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricAction(**publish_metric_action)
        self._values: typing.Dict[str, typing.Any] = {
            "publish_metric_action": publish_metric_action,
        }

    @builtins.property
    def publish_metric_action(
        self,
    ) -> "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricAction":
        '''publish_metric_action block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#publish_metric_action NetworkfirewallRuleGroup#publish_metric_action}
        '''
        result = self._values.get("publish_metric_action")
        assert result is not None, "Required property 'publish_metric_action' is missing"
        return typing.cast("NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricAction", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinition(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionOutputReference",
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

    @jsii.member(jsii_name="putPublishMetricAction")
    def put_publish_metric_action(
        self,
        *,
        dimension: typing.Sequence["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricActionDimension"],
    ) -> None:
        '''
        :param dimension: dimension block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#dimension NetworkfirewallRuleGroup#dimension}
        '''
        value = NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricAction(
            dimension=dimension
        )

        return typing.cast(None, jsii.invoke(self, "putPublishMetricAction", [value]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publishMetricAction")
    def publish_metric_action(
        self,
    ) -> "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricActionOutputReference":
        return typing.cast("NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricActionOutputReference", jsii.get(self, "publishMetricAction"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publishMetricActionInput")
    def publish_metric_action_input(
        self,
    ) -> typing.Optional["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricAction"]:
        return typing.cast(typing.Optional["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricAction"], jsii.get(self, "publishMetricActionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinition]:
        return typing.cast(typing.Optional[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinition], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinition],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricAction",
    jsii_struct_bases=[],
    name_mapping={"dimension": "dimension"},
)
class NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricAction:
    def __init__(
        self,
        *,
        dimension: typing.Sequence["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricActionDimension"],
    ) -> None:
        '''
        :param dimension: dimension block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#dimension NetworkfirewallRuleGroup#dimension}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "dimension": dimension,
        }

    @builtins.property
    def dimension(
        self,
    ) -> typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricActionDimension"]:
        '''dimension block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#dimension NetworkfirewallRuleGroup#dimension}
        '''
        result = self._values.get("dimension")
        assert result is not None, "Required property 'dimension' is missing"
        return typing.cast(typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricActionDimension"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricAction(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricActionDimension",
    jsii_struct_bases=[],
    name_mapping={"value": "value"},
)
class NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricActionDimension:
    def __init__(self, *, value: builtins.str) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#value NetworkfirewallRuleGroup#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "value": value,
        }

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#value NetworkfirewallRuleGroup#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricActionDimension(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricActionOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricActionOutputReference",
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
    @jsii.member(jsii_name="dimensionInput")
    def dimension_input(
        self,
    ) -> typing.Optional[typing.List[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricActionDimension]]:
        return typing.cast(typing.Optional[typing.List[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricActionDimension]], jsii.get(self, "dimensionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dimension")
    def dimension(
        self,
    ) -> typing.List[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricActionDimension]:
        return typing.cast(typing.List[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricActionDimension], jsii.get(self, "dimension"))

    @dimension.setter
    def dimension(
        self,
        value: typing.List[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricActionDimension],
    ) -> None:
        jsii.set(self, "dimension", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricAction]:
        return typing.cast(typing.Optional[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricAction], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricAction],
    ) -> None:
        jsii.set(self, "internalValue", value)


class NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsOutputReference",
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

    @jsii.member(jsii_name="resetCustomAction")
    def reset_custom_action(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomAction", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customActionInput")
    def custom_action_input(
        self,
    ) -> typing.Optional[typing.List[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomAction]]:
        return typing.cast(typing.Optional[typing.List[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomAction]], jsii.get(self, "customActionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statelessRuleInput")
    def stateless_rule_input(
        self,
    ) -> typing.Optional[typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRule"]]:
        return typing.cast(typing.Optional[typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRule"]], jsii.get(self, "statelessRuleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customAction")
    def custom_action(
        self,
    ) -> typing.List[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomAction]:
        return typing.cast(typing.List[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomAction], jsii.get(self, "customAction"))

    @custom_action.setter
    def custom_action(
        self,
        value: typing.List[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomAction],
    ) -> None:
        jsii.set(self, "customAction", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statelessRule")
    def stateless_rule(
        self,
    ) -> typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRule"]:
        return typing.cast(typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRule"], jsii.get(self, "statelessRule"))

    @stateless_rule.setter
    def stateless_rule(
        self,
        value: typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRule"],
    ) -> None:
        jsii.set(self, "statelessRule", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActions]:
        return typing.cast(typing.Optional[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActions], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActions],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRule",
    jsii_struct_bases=[],
    name_mapping={"priority": "priority", "rule_definition": "ruleDefinition"},
)
class NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRule:
    def __init__(
        self,
        *,
        priority: jsii.Number,
        rule_definition: "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinition",
    ) -> None:
        '''
        :param priority: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#priority NetworkfirewallRuleGroup#priority}.
        :param rule_definition: rule_definition block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#rule_definition NetworkfirewallRuleGroup#rule_definition}
        '''
        if isinstance(rule_definition, dict):
            rule_definition = NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinition(**rule_definition)
        self._values: typing.Dict[str, typing.Any] = {
            "priority": priority,
            "rule_definition": rule_definition,
        }

    @builtins.property
    def priority(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#priority NetworkfirewallRuleGroup#priority}.'''
        result = self._values.get("priority")
        assert result is not None, "Required property 'priority' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def rule_definition(
        self,
    ) -> "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinition":
        '''rule_definition block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#rule_definition NetworkfirewallRuleGroup#rule_definition}
        '''
        result = self._values.get("rule_definition")
        assert result is not None, "Required property 'rule_definition' is missing"
        return typing.cast("NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinition", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinition",
    jsii_struct_bases=[],
    name_mapping={"actions": "actions", "match_attributes": "matchAttributes"},
)
class NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinition:
    def __init__(
        self,
        *,
        actions: typing.Sequence[builtins.str],
        match_attributes: "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributes",
    ) -> None:
        '''
        :param actions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#actions NetworkfirewallRuleGroup#actions}.
        :param match_attributes: match_attributes block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#match_attributes NetworkfirewallRuleGroup#match_attributes}
        '''
        if isinstance(match_attributes, dict):
            match_attributes = NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributes(**match_attributes)
        self._values: typing.Dict[str, typing.Any] = {
            "actions": actions,
            "match_attributes": match_attributes,
        }

    @builtins.property
    def actions(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#actions NetworkfirewallRuleGroup#actions}.'''
        result = self._values.get("actions")
        assert result is not None, "Required property 'actions' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def match_attributes(
        self,
    ) -> "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributes":
        '''match_attributes block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#match_attributes NetworkfirewallRuleGroup#match_attributes}
        '''
        result = self._values.get("match_attributes")
        assert result is not None, "Required property 'match_attributes' is missing"
        return typing.cast("NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributes", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinition(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributes",
    jsii_struct_bases=[],
    name_mapping={
        "destination": "destination",
        "destination_port": "destinationPort",
        "protocols": "protocols",
        "source": "source",
        "source_port": "sourcePort",
        "tcp_flag": "tcpFlag",
    },
)
class NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributes:
    def __init__(
        self,
        *,
        destination: typing.Optional[typing.Sequence["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestination"]] = None,
        destination_port: typing.Optional[typing.Sequence["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestinationPort"]] = None,
        protocols: typing.Optional[typing.Sequence[jsii.Number]] = None,
        source: typing.Optional[typing.Sequence["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSource"]] = None,
        source_port: typing.Optional[typing.Sequence["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSourcePort"]] = None,
        tcp_flag: typing.Optional[typing.Sequence["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesTcpFlag"]] = None,
    ) -> None:
        '''
        :param destination: destination block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#destination NetworkfirewallRuleGroup#destination}
        :param destination_port: destination_port block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#destination_port NetworkfirewallRuleGroup#destination_port}
        :param protocols: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#protocols NetworkfirewallRuleGroup#protocols}.
        :param source: source block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#source NetworkfirewallRuleGroup#source}
        :param source_port: source_port block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#source_port NetworkfirewallRuleGroup#source_port}
        :param tcp_flag: tcp_flag block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#tcp_flag NetworkfirewallRuleGroup#tcp_flag}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if destination is not None:
            self._values["destination"] = destination
        if destination_port is not None:
            self._values["destination_port"] = destination_port
        if protocols is not None:
            self._values["protocols"] = protocols
        if source is not None:
            self._values["source"] = source
        if source_port is not None:
            self._values["source_port"] = source_port
        if tcp_flag is not None:
            self._values["tcp_flag"] = tcp_flag

    @builtins.property
    def destination(
        self,
    ) -> typing.Optional[typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestination"]]:
        '''destination block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#destination NetworkfirewallRuleGroup#destination}
        '''
        result = self._values.get("destination")
        return typing.cast(typing.Optional[typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestination"]], result)

    @builtins.property
    def destination_port(
        self,
    ) -> typing.Optional[typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestinationPort"]]:
        '''destination_port block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#destination_port NetworkfirewallRuleGroup#destination_port}
        '''
        result = self._values.get("destination_port")
        return typing.cast(typing.Optional[typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestinationPort"]], result)

    @builtins.property
    def protocols(self) -> typing.Optional[typing.List[jsii.Number]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#protocols NetworkfirewallRuleGroup#protocols}.'''
        result = self._values.get("protocols")
        return typing.cast(typing.Optional[typing.List[jsii.Number]], result)

    @builtins.property
    def source(
        self,
    ) -> typing.Optional[typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSource"]]:
        '''source block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#source NetworkfirewallRuleGroup#source}
        '''
        result = self._values.get("source")
        return typing.cast(typing.Optional[typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSource"]], result)

    @builtins.property
    def source_port(
        self,
    ) -> typing.Optional[typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSourcePort"]]:
        '''source_port block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#source_port NetworkfirewallRuleGroup#source_port}
        '''
        result = self._values.get("source_port")
        return typing.cast(typing.Optional[typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSourcePort"]], result)

    @builtins.property
    def tcp_flag(
        self,
    ) -> typing.Optional[typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesTcpFlag"]]:
        '''tcp_flag block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#tcp_flag NetworkfirewallRuleGroup#tcp_flag}
        '''
        result = self._values.get("tcp_flag")
        return typing.cast(typing.Optional[typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesTcpFlag"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestination",
    jsii_struct_bases=[],
    name_mapping={"address_definition": "addressDefinition"},
)
class NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestination:
    def __init__(self, *, address_definition: builtins.str) -> None:
        '''
        :param address_definition: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#address_definition NetworkfirewallRuleGroup#address_definition}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "address_definition": address_definition,
        }

    @builtins.property
    def address_definition(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#address_definition NetworkfirewallRuleGroup#address_definition}.'''
        result = self._values.get("address_definition")
        assert result is not None, "Required property 'address_definition' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestination(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestinationPort",
    jsii_struct_bases=[],
    name_mapping={"from_port": "fromPort", "to_port": "toPort"},
)
class NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestinationPort:
    def __init__(
        self,
        *,
        from_port: jsii.Number,
        to_port: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param from_port: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#from_port NetworkfirewallRuleGroup#from_port}.
        :param to_port: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#to_port NetworkfirewallRuleGroup#to_port}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "from_port": from_port,
        }
        if to_port is not None:
            self._values["to_port"] = to_port

    @builtins.property
    def from_port(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#from_port NetworkfirewallRuleGroup#from_port}.'''
        result = self._values.get("from_port")
        assert result is not None, "Required property 'from_port' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def to_port(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#to_port NetworkfirewallRuleGroup#to_port}.'''
        result = self._values.get("to_port")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestinationPort(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesOutputReference",
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

    @jsii.member(jsii_name="resetDestination")
    def reset_destination(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDestination", []))

    @jsii.member(jsii_name="resetDestinationPort")
    def reset_destination_port(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDestinationPort", []))

    @jsii.member(jsii_name="resetProtocols")
    def reset_protocols(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProtocols", []))

    @jsii.member(jsii_name="resetSource")
    def reset_source(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSource", []))

    @jsii.member(jsii_name="resetSourcePort")
    def reset_source_port(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourcePort", []))

    @jsii.member(jsii_name="resetTcpFlag")
    def reset_tcp_flag(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTcpFlag", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="destinationInput")
    def destination_input(
        self,
    ) -> typing.Optional[typing.List[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestination]]:
        return typing.cast(typing.Optional[typing.List[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestination]], jsii.get(self, "destinationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="destinationPortInput")
    def destination_port_input(
        self,
    ) -> typing.Optional[typing.List[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestinationPort]]:
        return typing.cast(typing.Optional[typing.List[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestinationPort]], jsii.get(self, "destinationPortInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="protocolsInput")
    def protocols_input(self) -> typing.Optional[typing.List[jsii.Number]]:
        return typing.cast(typing.Optional[typing.List[jsii.Number]], jsii.get(self, "protocolsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceInput")
    def source_input(
        self,
    ) -> typing.Optional[typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSource"]]:
        return typing.cast(typing.Optional[typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSource"]], jsii.get(self, "sourceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourcePortInput")
    def source_port_input(
        self,
    ) -> typing.Optional[typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSourcePort"]]:
        return typing.cast(typing.Optional[typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSourcePort"]], jsii.get(self, "sourcePortInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tcpFlagInput")
    def tcp_flag_input(
        self,
    ) -> typing.Optional[typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesTcpFlag"]]:
        return typing.cast(typing.Optional[typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesTcpFlag"]], jsii.get(self, "tcpFlagInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="destination")
    def destination(
        self,
    ) -> typing.List[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestination]:
        return typing.cast(typing.List[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestination], jsii.get(self, "destination"))

    @destination.setter
    def destination(
        self,
        value: typing.List[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestination],
    ) -> None:
        jsii.set(self, "destination", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="destinationPort")
    def destination_port(
        self,
    ) -> typing.List[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestinationPort]:
        return typing.cast(typing.List[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestinationPort], jsii.get(self, "destinationPort"))

    @destination_port.setter
    def destination_port(
        self,
        value: typing.List[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestinationPort],
    ) -> None:
        jsii.set(self, "destinationPort", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="protocols")
    def protocols(self) -> typing.List[jsii.Number]:
        return typing.cast(typing.List[jsii.Number], jsii.get(self, "protocols"))

    @protocols.setter
    def protocols(self, value: typing.List[jsii.Number]) -> None:
        jsii.set(self, "protocols", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="source")
    def source(
        self,
    ) -> typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSource"]:
        return typing.cast(typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSource"], jsii.get(self, "source"))

    @source.setter
    def source(
        self,
        value: typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSource"],
    ) -> None:
        jsii.set(self, "source", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourcePort")
    def source_port(
        self,
    ) -> typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSourcePort"]:
        return typing.cast(typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSourcePort"], jsii.get(self, "sourcePort"))

    @source_port.setter
    def source_port(
        self,
        value: typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSourcePort"],
    ) -> None:
        jsii.set(self, "sourcePort", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tcpFlag")
    def tcp_flag(
        self,
    ) -> typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesTcpFlag"]:
        return typing.cast(typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesTcpFlag"], jsii.get(self, "tcpFlag"))

    @tcp_flag.setter
    def tcp_flag(
        self,
        value: typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesTcpFlag"],
    ) -> None:
        jsii.set(self, "tcpFlag", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributes]:
        return typing.cast(typing.Optional[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributes], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributes],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSource",
    jsii_struct_bases=[],
    name_mapping={"address_definition": "addressDefinition"},
)
class NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSource:
    def __init__(self, *, address_definition: builtins.str) -> None:
        '''
        :param address_definition: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#address_definition NetworkfirewallRuleGroup#address_definition}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "address_definition": address_definition,
        }

    @builtins.property
    def address_definition(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#address_definition NetworkfirewallRuleGroup#address_definition}.'''
        result = self._values.get("address_definition")
        assert result is not None, "Required property 'address_definition' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSource(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSourcePort",
    jsii_struct_bases=[],
    name_mapping={"from_port": "fromPort", "to_port": "toPort"},
)
class NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSourcePort:
    def __init__(
        self,
        *,
        from_port: jsii.Number,
        to_port: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param from_port: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#from_port NetworkfirewallRuleGroup#from_port}.
        :param to_port: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#to_port NetworkfirewallRuleGroup#to_port}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "from_port": from_port,
        }
        if to_port is not None:
            self._values["to_port"] = to_port

    @builtins.property
    def from_port(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#from_port NetworkfirewallRuleGroup#from_port}.'''
        result = self._values.get("from_port")
        assert result is not None, "Required property 'from_port' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def to_port(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#to_port NetworkfirewallRuleGroup#to_port}.'''
        result = self._values.get("to_port")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSourcePort(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesTcpFlag",
    jsii_struct_bases=[],
    name_mapping={"flags": "flags", "masks": "masks"},
)
class NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesTcpFlag:
    def __init__(
        self,
        *,
        flags: typing.Sequence[builtins.str],
        masks: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param flags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#flags NetworkfirewallRuleGroup#flags}.
        :param masks: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#masks NetworkfirewallRuleGroup#masks}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "flags": flags,
        }
        if masks is not None:
            self._values["masks"] = masks

    @builtins.property
    def flags(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#flags NetworkfirewallRuleGroup#flags}.'''
        result = self._values.get("flags")
        assert result is not None, "Required property 'flags' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def masks(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#masks NetworkfirewallRuleGroup#masks}.'''
        result = self._values.get("masks")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesTcpFlag(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionOutputReference",
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

    @jsii.member(jsii_name="putMatchAttributes")
    def put_match_attributes(
        self,
        *,
        destination: typing.Optional[typing.Sequence[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestination]] = None,
        destination_port: typing.Optional[typing.Sequence[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestinationPort]] = None,
        protocols: typing.Optional[typing.Sequence[jsii.Number]] = None,
        source: typing.Optional[typing.Sequence[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSource]] = None,
        source_port: typing.Optional[typing.Sequence[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSourcePort]] = None,
        tcp_flag: typing.Optional[typing.Sequence[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesTcpFlag]] = None,
    ) -> None:
        '''
        :param destination: destination block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#destination NetworkfirewallRuleGroup#destination}
        :param destination_port: destination_port block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#destination_port NetworkfirewallRuleGroup#destination_port}
        :param protocols: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#protocols NetworkfirewallRuleGroup#protocols}.
        :param source: source block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#source NetworkfirewallRuleGroup#source}
        :param source_port: source_port block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#source_port NetworkfirewallRuleGroup#source_port}
        :param tcp_flag: tcp_flag block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#tcp_flag NetworkfirewallRuleGroup#tcp_flag}
        '''
        value = NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributes(
            destination=destination,
            destination_port=destination_port,
            protocols=protocols,
            source=source,
            source_port=source_port,
            tcp_flag=tcp_flag,
        )

        return typing.cast(None, jsii.invoke(self, "putMatchAttributes", [value]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="matchAttributes")
    def match_attributes(
        self,
    ) -> NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesOutputReference:
        return typing.cast(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesOutputReference, jsii.get(self, "matchAttributes"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="actionsInput")
    def actions_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "actionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="matchAttributesInput")
    def match_attributes_input(
        self,
    ) -> typing.Optional[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributes]:
        return typing.cast(typing.Optional[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributes], jsii.get(self, "matchAttributesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="actions")
    def actions(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "actions"))

    @actions.setter
    def actions(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "actions", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinition]:
        return typing.cast(typing.Optional[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinition], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinition],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupStatefulRuleOptions",
    jsii_struct_bases=[],
    name_mapping={"rule_order": "ruleOrder"},
)
class NetworkfirewallRuleGroupRuleGroupStatefulRuleOptions:
    def __init__(self, *, rule_order: builtins.str) -> None:
        '''
        :param rule_order: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#rule_order NetworkfirewallRuleGroup#rule_order}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "rule_order": rule_order,
        }

    @builtins.property
    def rule_order(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#rule_order NetworkfirewallRuleGroup#rule_order}.'''
        result = self._values.get("rule_order")
        assert result is not None, "Required property 'rule_order' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallRuleGroupRuleGroupStatefulRuleOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NetworkfirewallRuleGroupRuleGroupStatefulRuleOptionsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupStatefulRuleOptionsOutputReference",
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
    @jsii.member(jsii_name="ruleOrderInput")
    def rule_order_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ruleOrderInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ruleOrder")
    def rule_order(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ruleOrder"))

    @rule_order.setter
    def rule_order(self, value: builtins.str) -> None:
        jsii.set(self, "ruleOrder", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[NetworkfirewallRuleGroupRuleGroupStatefulRuleOptions]:
        return typing.cast(typing.Optional[NetworkfirewallRuleGroupRuleGroupStatefulRuleOptions], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[NetworkfirewallRuleGroupRuleGroupStatefulRuleOptions],
    ) -> None:
        jsii.set(self, "internalValue", value)


__all__ = [
    "NetworkfirewallFirewall",
    "NetworkfirewallFirewallConfig",
    "NetworkfirewallFirewallFirewallStatus",
    "NetworkfirewallFirewallFirewallStatusSyncStates",
    "NetworkfirewallFirewallFirewallStatusSyncStatesAttachment",
    "NetworkfirewallFirewallPolicy",
    "NetworkfirewallFirewallPolicyConfig",
    "NetworkfirewallFirewallPolicyFirewallPolicy",
    "NetworkfirewallFirewallPolicyFirewallPolicyOutputReference",
    "NetworkfirewallFirewallPolicyFirewallPolicyStatefulEngineOptions",
    "NetworkfirewallFirewallPolicyFirewallPolicyStatefulEngineOptionsOutputReference",
    "NetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReference",
    "NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomAction",
    "NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinition",
    "NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionOutputReference",
    "NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricAction",
    "NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimension",
    "NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionOutputReference",
    "NetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReference",
    "NetworkfirewallFirewallSubnetMapping",
    "NetworkfirewallLoggingConfiguration",
    "NetworkfirewallLoggingConfigurationConfig",
    "NetworkfirewallLoggingConfigurationLoggingConfiguration",
    "NetworkfirewallLoggingConfigurationLoggingConfigurationLogDestinationConfig",
    "NetworkfirewallLoggingConfigurationLoggingConfigurationOutputReference",
    "NetworkfirewallResourcePolicy",
    "NetworkfirewallResourcePolicyConfig",
    "NetworkfirewallRuleGroup",
    "NetworkfirewallRuleGroupConfig",
    "NetworkfirewallRuleGroupRuleGroup",
    "NetworkfirewallRuleGroupRuleGroupOutputReference",
    "NetworkfirewallRuleGroupRuleGroupRuleVariables",
    "NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSets",
    "NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSetsIpSet",
    "NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSetsIpSetOutputReference",
    "NetworkfirewallRuleGroupRuleGroupRuleVariablesOutputReference",
    "NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSets",
    "NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSetsPortSet",
    "NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSetsPortSetOutputReference",
    "NetworkfirewallRuleGroupRuleGroupRulesSource",
    "NetworkfirewallRuleGroupRuleGroupRulesSourceOutputReference",
    "NetworkfirewallRuleGroupRuleGroupRulesSourceRulesSourceList",
    "NetworkfirewallRuleGroupRuleGroupRulesSourceRulesSourceListOutputReference",
    "NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRule",
    "NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleHeader",
    "NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleHeaderOutputReference",
    "NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleRuleOption",
    "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActions",
    "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomAction",
    "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinition",
    "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionOutputReference",
    "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricAction",
    "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricActionDimension",
    "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricActionOutputReference",
    "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsOutputReference",
    "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRule",
    "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinition",
    "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributes",
    "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestination",
    "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestinationPort",
    "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesOutputReference",
    "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSource",
    "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSourcePort",
    "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesTcpFlag",
    "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionOutputReference",
    "NetworkfirewallRuleGroupRuleGroupStatefulRuleOptions",
    "NetworkfirewallRuleGroupRuleGroupStatefulRuleOptionsOutputReference",
]

publication.publish()
