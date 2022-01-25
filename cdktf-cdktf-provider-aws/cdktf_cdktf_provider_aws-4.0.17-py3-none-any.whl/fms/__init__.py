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


class FmsAdminAccount(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.fms.FmsAdminAccount",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/fms_admin_account aws_fms_admin_account}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        account_id: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/fms_admin_account aws_fms_admin_account} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param account_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fms_admin_account#account_id FmsAdminAccount#account_id}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = FmsAdminAccountConfig(
            account_id=account_id,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetAccountId")
    def reset_account_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccountId", []))

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
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: builtins.str) -> None:
        jsii.set(self, "accountId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.fms.FmsAdminAccountConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "account_id": "accountId",
    },
)
class FmsAdminAccountConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        account_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Firewall Management Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param account_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fms_admin_account#account_id FmsAdminAccount#account_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {}
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if account_id is not None:
            self._values["account_id"] = account_id

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
    def account_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fms_admin_account#account_id FmsAdminAccount#account_id}.'''
        result = self._values.get("account_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FmsAdminAccountConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class FmsPolicy(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.fms.FmsPolicy",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/fms_policy aws_fms_policy}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        exclude_resource_tags: typing.Union[builtins.bool, cdktf.IResolvable],
        name: builtins.str,
        security_service_policy_data: "FmsPolicySecurityServicePolicyData",
        delete_all_policy_resources: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        exclude_map: typing.Optional["FmsPolicyExcludeMap"] = None,
        include_map: typing.Optional["FmsPolicyIncludeMap"] = None,
        remediation_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        resource_tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        resource_type: typing.Optional[builtins.str] = None,
        resource_type_list: typing.Optional[typing.Sequence[builtins.str]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/fms_policy aws_fms_policy} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param exclude_resource_tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fms_policy#exclude_resource_tags FmsPolicy#exclude_resource_tags}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fms_policy#name FmsPolicy#name}.
        :param security_service_policy_data: security_service_policy_data block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fms_policy#security_service_policy_data FmsPolicy#security_service_policy_data}
        :param delete_all_policy_resources: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fms_policy#delete_all_policy_resources FmsPolicy#delete_all_policy_resources}.
        :param exclude_map: exclude_map block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fms_policy#exclude_map FmsPolicy#exclude_map}
        :param include_map: include_map block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fms_policy#include_map FmsPolicy#include_map}
        :param remediation_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fms_policy#remediation_enabled FmsPolicy#remediation_enabled}.
        :param resource_tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fms_policy#resource_tags FmsPolicy#resource_tags}.
        :param resource_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fms_policy#resource_type FmsPolicy#resource_type}.
        :param resource_type_list: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fms_policy#resource_type_list FmsPolicy#resource_type_list}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = FmsPolicyConfig(
            exclude_resource_tags=exclude_resource_tags,
            name=name,
            security_service_policy_data=security_service_policy_data,
            delete_all_policy_resources=delete_all_policy_resources,
            exclude_map=exclude_map,
            include_map=include_map,
            remediation_enabled=remediation_enabled,
            resource_tags=resource_tags,
            resource_type=resource_type,
            resource_type_list=resource_type_list,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putExcludeMap")
    def put_exclude_map(
        self,
        *,
        account: typing.Optional[typing.Sequence[builtins.str]] = None,
        orgunit: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param account: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fms_policy#account FmsPolicy#account}.
        :param orgunit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fms_policy#orgunit FmsPolicy#orgunit}.
        '''
        value = FmsPolicyExcludeMap(account=account, orgunit=orgunit)

        return typing.cast(None, jsii.invoke(self, "putExcludeMap", [value]))

    @jsii.member(jsii_name="putIncludeMap")
    def put_include_map(
        self,
        *,
        account: typing.Optional[typing.Sequence[builtins.str]] = None,
        orgunit: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param account: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fms_policy#account FmsPolicy#account}.
        :param orgunit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fms_policy#orgunit FmsPolicy#orgunit}.
        '''
        value = FmsPolicyIncludeMap(account=account, orgunit=orgunit)

        return typing.cast(None, jsii.invoke(self, "putIncludeMap", [value]))

    @jsii.member(jsii_name="putSecurityServicePolicyData")
    def put_security_service_policy_data(
        self,
        *,
        type: builtins.str,
        managed_service_data: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fms_policy#type FmsPolicy#type}.
        :param managed_service_data: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fms_policy#managed_service_data FmsPolicy#managed_service_data}.
        '''
        value = FmsPolicySecurityServicePolicyData(
            type=type, managed_service_data=managed_service_data
        )

        return typing.cast(None, jsii.invoke(self, "putSecurityServicePolicyData", [value]))

    @jsii.member(jsii_name="resetDeleteAllPolicyResources")
    def reset_delete_all_policy_resources(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeleteAllPolicyResources", []))

    @jsii.member(jsii_name="resetExcludeMap")
    def reset_exclude_map(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExcludeMap", []))

    @jsii.member(jsii_name="resetIncludeMap")
    def reset_include_map(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIncludeMap", []))

    @jsii.member(jsii_name="resetRemediationEnabled")
    def reset_remediation_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRemediationEnabled", []))

    @jsii.member(jsii_name="resetResourceTags")
    def reset_resource_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResourceTags", []))

    @jsii.member(jsii_name="resetResourceType")
    def reset_resource_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResourceType", []))

    @jsii.member(jsii_name="resetResourceTypeList")
    def reset_resource_type_list(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResourceTypeList", []))

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
    @jsii.member(jsii_name="excludeMap")
    def exclude_map(self) -> "FmsPolicyExcludeMapOutputReference":
        return typing.cast("FmsPolicyExcludeMapOutputReference", jsii.get(self, "excludeMap"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="includeMap")
    def include_map(self) -> "FmsPolicyIncludeMapOutputReference":
        return typing.cast("FmsPolicyIncludeMapOutputReference", jsii.get(self, "includeMap"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyUpdateToken")
    def policy_update_token(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policyUpdateToken"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityServicePolicyData")
    def security_service_policy_data(
        self,
    ) -> "FmsPolicySecurityServicePolicyDataOutputReference":
        return typing.cast("FmsPolicySecurityServicePolicyDataOutputReference", jsii.get(self, "securityServicePolicyData"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deleteAllPolicyResourcesInput")
    def delete_all_policy_resources_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "deleteAllPolicyResourcesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="excludeMapInput")
    def exclude_map_input(self) -> typing.Optional["FmsPolicyExcludeMap"]:
        return typing.cast(typing.Optional["FmsPolicyExcludeMap"], jsii.get(self, "excludeMapInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="excludeResourceTagsInput")
    def exclude_resource_tags_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "excludeResourceTagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="includeMapInput")
    def include_map_input(self) -> typing.Optional["FmsPolicyIncludeMap"]:
        return typing.cast(typing.Optional["FmsPolicyIncludeMap"], jsii.get(self, "includeMapInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="remediationEnabledInput")
    def remediation_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "remediationEnabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceTagsInput")
    def resource_tags_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "resourceTagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceTypeInput")
    def resource_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "resourceTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceTypeListInput")
    def resource_type_list_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "resourceTypeListInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityServicePolicyDataInput")
    def security_service_policy_data_input(
        self,
    ) -> typing.Optional["FmsPolicySecurityServicePolicyData"]:
        return typing.cast(typing.Optional["FmsPolicySecurityServicePolicyData"], jsii.get(self, "securityServicePolicyDataInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deleteAllPolicyResources")
    def delete_all_policy_resources(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "deleteAllPolicyResources"))

    @delete_all_policy_resources.setter
    def delete_all_policy_resources(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "deleteAllPolicyResources", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="excludeResourceTags")
    def exclude_resource_tags(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "excludeResourceTags"))

    @exclude_resource_tags.setter
    def exclude_resource_tags(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "excludeResourceTags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="remediationEnabled")
    def remediation_enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "remediationEnabled"))

    @remediation_enabled.setter
    def remediation_enabled(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "remediationEnabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceTags")
    def resource_tags(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "resourceTags"))

    @resource_tags.setter
    def resource_tags(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "resourceTags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceType")
    def resource_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "resourceType"))

    @resource_type.setter
    def resource_type(self, value: builtins.str) -> None:
        jsii.set(self, "resourceType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceTypeList")
    def resource_type_list(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "resourceTypeList"))

    @resource_type_list.setter
    def resource_type_list(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "resourceTypeList", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.fms.FmsPolicyConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "exclude_resource_tags": "excludeResourceTags",
        "name": "name",
        "security_service_policy_data": "securityServicePolicyData",
        "delete_all_policy_resources": "deleteAllPolicyResources",
        "exclude_map": "excludeMap",
        "include_map": "includeMap",
        "remediation_enabled": "remediationEnabled",
        "resource_tags": "resourceTags",
        "resource_type": "resourceType",
        "resource_type_list": "resourceTypeList",
    },
)
class FmsPolicyConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        exclude_resource_tags: typing.Union[builtins.bool, cdktf.IResolvable],
        name: builtins.str,
        security_service_policy_data: "FmsPolicySecurityServicePolicyData",
        delete_all_policy_resources: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        exclude_map: typing.Optional["FmsPolicyExcludeMap"] = None,
        include_map: typing.Optional["FmsPolicyIncludeMap"] = None,
        remediation_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        resource_tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        resource_type: typing.Optional[builtins.str] = None,
        resource_type_list: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''AWS Firewall Management Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param exclude_resource_tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fms_policy#exclude_resource_tags FmsPolicy#exclude_resource_tags}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fms_policy#name FmsPolicy#name}.
        :param security_service_policy_data: security_service_policy_data block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fms_policy#security_service_policy_data FmsPolicy#security_service_policy_data}
        :param delete_all_policy_resources: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fms_policy#delete_all_policy_resources FmsPolicy#delete_all_policy_resources}.
        :param exclude_map: exclude_map block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fms_policy#exclude_map FmsPolicy#exclude_map}
        :param include_map: include_map block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fms_policy#include_map FmsPolicy#include_map}
        :param remediation_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fms_policy#remediation_enabled FmsPolicy#remediation_enabled}.
        :param resource_tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fms_policy#resource_tags FmsPolicy#resource_tags}.
        :param resource_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fms_policy#resource_type FmsPolicy#resource_type}.
        :param resource_type_list: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fms_policy#resource_type_list FmsPolicy#resource_type_list}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(security_service_policy_data, dict):
            security_service_policy_data = FmsPolicySecurityServicePolicyData(**security_service_policy_data)
        if isinstance(exclude_map, dict):
            exclude_map = FmsPolicyExcludeMap(**exclude_map)
        if isinstance(include_map, dict):
            include_map = FmsPolicyIncludeMap(**include_map)
        self._values: typing.Dict[str, typing.Any] = {
            "exclude_resource_tags": exclude_resource_tags,
            "name": name,
            "security_service_policy_data": security_service_policy_data,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if delete_all_policy_resources is not None:
            self._values["delete_all_policy_resources"] = delete_all_policy_resources
        if exclude_map is not None:
            self._values["exclude_map"] = exclude_map
        if include_map is not None:
            self._values["include_map"] = include_map
        if remediation_enabled is not None:
            self._values["remediation_enabled"] = remediation_enabled
        if resource_tags is not None:
            self._values["resource_tags"] = resource_tags
        if resource_type is not None:
            self._values["resource_type"] = resource_type
        if resource_type_list is not None:
            self._values["resource_type_list"] = resource_type_list

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
    def exclude_resource_tags(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fms_policy#exclude_resource_tags FmsPolicy#exclude_resource_tags}.'''
        result = self._values.get("exclude_resource_tags")
        assert result is not None, "Required property 'exclude_resource_tags' is missing"
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fms_policy#name FmsPolicy#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def security_service_policy_data(self) -> "FmsPolicySecurityServicePolicyData":
        '''security_service_policy_data block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fms_policy#security_service_policy_data FmsPolicy#security_service_policy_data}
        '''
        result = self._values.get("security_service_policy_data")
        assert result is not None, "Required property 'security_service_policy_data' is missing"
        return typing.cast("FmsPolicySecurityServicePolicyData", result)

    @builtins.property
    def delete_all_policy_resources(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fms_policy#delete_all_policy_resources FmsPolicy#delete_all_policy_resources}.'''
        result = self._values.get("delete_all_policy_resources")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def exclude_map(self) -> typing.Optional["FmsPolicyExcludeMap"]:
        '''exclude_map block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fms_policy#exclude_map FmsPolicy#exclude_map}
        '''
        result = self._values.get("exclude_map")
        return typing.cast(typing.Optional["FmsPolicyExcludeMap"], result)

    @builtins.property
    def include_map(self) -> typing.Optional["FmsPolicyIncludeMap"]:
        '''include_map block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fms_policy#include_map FmsPolicy#include_map}
        '''
        result = self._values.get("include_map")
        return typing.cast(typing.Optional["FmsPolicyIncludeMap"], result)

    @builtins.property
    def remediation_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fms_policy#remediation_enabled FmsPolicy#remediation_enabled}.'''
        result = self._values.get("remediation_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def resource_tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fms_policy#resource_tags FmsPolicy#resource_tags}.'''
        result = self._values.get("resource_tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def resource_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fms_policy#resource_type FmsPolicy#resource_type}.'''
        result = self._values.get("resource_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def resource_type_list(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fms_policy#resource_type_list FmsPolicy#resource_type_list}.'''
        result = self._values.get("resource_type_list")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FmsPolicyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.fms.FmsPolicyExcludeMap",
    jsii_struct_bases=[],
    name_mapping={"account": "account", "orgunit": "orgunit"},
)
class FmsPolicyExcludeMap:
    def __init__(
        self,
        *,
        account: typing.Optional[typing.Sequence[builtins.str]] = None,
        orgunit: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param account: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fms_policy#account FmsPolicy#account}.
        :param orgunit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fms_policy#orgunit FmsPolicy#orgunit}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if account is not None:
            self._values["account"] = account
        if orgunit is not None:
            self._values["orgunit"] = orgunit

    @builtins.property
    def account(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fms_policy#account FmsPolicy#account}.'''
        result = self._values.get("account")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def orgunit(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fms_policy#orgunit FmsPolicy#orgunit}.'''
        result = self._values.get("orgunit")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FmsPolicyExcludeMap(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class FmsPolicyExcludeMapOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.fms.FmsPolicyExcludeMapOutputReference",
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

    @jsii.member(jsii_name="resetAccount")
    def reset_account(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccount", []))

    @jsii.member(jsii_name="resetOrgunit")
    def reset_orgunit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOrgunit", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountInput")
    def account_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "accountInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="orgunitInput")
    def orgunit_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "orgunitInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="account")
    def account(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "account"))

    @account.setter
    def account(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "account", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="orgunit")
    def orgunit(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "orgunit"))

    @orgunit.setter
    def orgunit(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "orgunit", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[FmsPolicyExcludeMap]:
        return typing.cast(typing.Optional[FmsPolicyExcludeMap], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[FmsPolicyExcludeMap]) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.fms.FmsPolicyIncludeMap",
    jsii_struct_bases=[],
    name_mapping={"account": "account", "orgunit": "orgunit"},
)
class FmsPolicyIncludeMap:
    def __init__(
        self,
        *,
        account: typing.Optional[typing.Sequence[builtins.str]] = None,
        orgunit: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param account: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fms_policy#account FmsPolicy#account}.
        :param orgunit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fms_policy#orgunit FmsPolicy#orgunit}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if account is not None:
            self._values["account"] = account
        if orgunit is not None:
            self._values["orgunit"] = orgunit

    @builtins.property
    def account(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fms_policy#account FmsPolicy#account}.'''
        result = self._values.get("account")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def orgunit(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fms_policy#orgunit FmsPolicy#orgunit}.'''
        result = self._values.get("orgunit")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FmsPolicyIncludeMap(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class FmsPolicyIncludeMapOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.fms.FmsPolicyIncludeMapOutputReference",
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

    @jsii.member(jsii_name="resetAccount")
    def reset_account(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccount", []))

    @jsii.member(jsii_name="resetOrgunit")
    def reset_orgunit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOrgunit", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountInput")
    def account_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "accountInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="orgunitInput")
    def orgunit_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "orgunitInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="account")
    def account(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "account"))

    @account.setter
    def account(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "account", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="orgunit")
    def orgunit(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "orgunit"))

    @orgunit.setter
    def orgunit(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "orgunit", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[FmsPolicyIncludeMap]:
        return typing.cast(typing.Optional[FmsPolicyIncludeMap], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[FmsPolicyIncludeMap]) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.fms.FmsPolicySecurityServicePolicyData",
    jsii_struct_bases=[],
    name_mapping={"type": "type", "managed_service_data": "managedServiceData"},
)
class FmsPolicySecurityServicePolicyData:
    def __init__(
        self,
        *,
        type: builtins.str,
        managed_service_data: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fms_policy#type FmsPolicy#type}.
        :param managed_service_data: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fms_policy#managed_service_data FmsPolicy#managed_service_data}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "type": type,
        }
        if managed_service_data is not None:
            self._values["managed_service_data"] = managed_service_data

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fms_policy#type FmsPolicy#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def managed_service_data(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fms_policy#managed_service_data FmsPolicy#managed_service_data}.'''
        result = self._values.get("managed_service_data")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FmsPolicySecurityServicePolicyData(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class FmsPolicySecurityServicePolicyDataOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.fms.FmsPolicySecurityServicePolicyDataOutputReference",
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

    @jsii.member(jsii_name="resetManagedServiceData")
    def reset_managed_service_data(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetManagedServiceData", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="managedServiceDataInput")
    def managed_service_data_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "managedServiceDataInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="managedServiceData")
    def managed_service_data(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "managedServiceData"))

    @managed_service_data.setter
    def managed_service_data(self, value: builtins.str) -> None:
        jsii.set(self, "managedServiceData", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        jsii.set(self, "type", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[FmsPolicySecurityServicePolicyData]:
        return typing.cast(typing.Optional[FmsPolicySecurityServicePolicyData], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[FmsPolicySecurityServicePolicyData],
    ) -> None:
        jsii.set(self, "internalValue", value)


__all__ = [
    "FmsAdminAccount",
    "FmsAdminAccountConfig",
    "FmsPolicy",
    "FmsPolicyConfig",
    "FmsPolicyExcludeMap",
    "FmsPolicyExcludeMapOutputReference",
    "FmsPolicyIncludeMap",
    "FmsPolicyIncludeMapOutputReference",
    "FmsPolicySecurityServicePolicyData",
    "FmsPolicySecurityServicePolicyDataOutputReference",
]

publication.publish()
