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


class DlmLifecyclePolicy(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.dlm.DlmLifecyclePolicy",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy aws_dlm_lifecycle_policy}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        description: builtins.str,
        execution_role_arn: builtins.str,
        policy_details: "DlmLifecyclePolicyPolicyDetails",
        state: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy aws_dlm_lifecycle_policy} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#description DlmLifecyclePolicy#description}.
        :param execution_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#execution_role_arn DlmLifecyclePolicy#execution_role_arn}.
        :param policy_details: policy_details block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#policy_details DlmLifecyclePolicy#policy_details}
        :param state: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#state DlmLifecyclePolicy#state}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#tags DlmLifecyclePolicy#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#tags_all DlmLifecyclePolicy#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DlmLifecyclePolicyConfig(
            description=description,
            execution_role_arn=execution_role_arn,
            policy_details=policy_details,
            state=state,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putPolicyDetails")
    def put_policy_details(
        self,
        *,
        resource_types: typing.Sequence[builtins.str],
        schedule: typing.Sequence["DlmLifecyclePolicyPolicyDetailsSchedule"],
        target_tags: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        '''
        :param resource_types: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#resource_types DlmLifecyclePolicy#resource_types}.
        :param schedule: schedule block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#schedule DlmLifecyclePolicy#schedule}
        :param target_tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#target_tags DlmLifecyclePolicy#target_tags}.
        '''
        value = DlmLifecyclePolicyPolicyDetails(
            resource_types=resource_types, schedule=schedule, target_tags=target_tags
        )

        return typing.cast(None, jsii.invoke(self, "putPolicyDetails", [value]))

    @jsii.member(jsii_name="resetState")
    def reset_state(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetState", []))

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
    @jsii.member(jsii_name="policyDetails")
    def policy_details(self) -> "DlmLifecyclePolicyPolicyDetailsOutputReference":
        return typing.cast("DlmLifecyclePolicyPolicyDetailsOutputReference", jsii.get(self, "policyDetails"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="executionRoleArnInput")
    def execution_role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "executionRoleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyDetailsInput")
    def policy_details_input(
        self,
    ) -> typing.Optional["DlmLifecyclePolicyPolicyDetails"]:
        return typing.cast(typing.Optional["DlmLifecyclePolicyPolicyDetails"], jsii.get(self, "policyDetailsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stateInput")
    def state_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stateInput"))

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
    @jsii.member(jsii_name="executionRoleArn")
    def execution_role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "executionRoleArn"))

    @execution_role_arn.setter
    def execution_role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "executionRoleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @state.setter
    def state(self, value: builtins.str) -> None:
        jsii.set(self, "state", value)

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
    jsii_type="@cdktf/provider-aws.dlm.DlmLifecyclePolicyConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "description": "description",
        "execution_role_arn": "executionRoleArn",
        "policy_details": "policyDetails",
        "state": "state",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class DlmLifecyclePolicyConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        description: builtins.str,
        execution_role_arn: builtins.str,
        policy_details: "DlmLifecyclePolicyPolicyDetails",
        state: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS Data Lifecycle Manager.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#description DlmLifecyclePolicy#description}.
        :param execution_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#execution_role_arn DlmLifecyclePolicy#execution_role_arn}.
        :param policy_details: policy_details block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#policy_details DlmLifecyclePolicy#policy_details}
        :param state: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#state DlmLifecyclePolicy#state}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#tags DlmLifecyclePolicy#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#tags_all DlmLifecyclePolicy#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(policy_details, dict):
            policy_details = DlmLifecyclePolicyPolicyDetails(**policy_details)
        self._values: typing.Dict[str, typing.Any] = {
            "description": description,
            "execution_role_arn": execution_role_arn,
            "policy_details": policy_details,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if state is not None:
            self._values["state"] = state
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
    def description(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#description DlmLifecyclePolicy#description}.'''
        result = self._values.get("description")
        assert result is not None, "Required property 'description' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def execution_role_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#execution_role_arn DlmLifecyclePolicy#execution_role_arn}.'''
        result = self._values.get("execution_role_arn")
        assert result is not None, "Required property 'execution_role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def policy_details(self) -> "DlmLifecyclePolicyPolicyDetails":
        '''policy_details block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#policy_details DlmLifecyclePolicy#policy_details}
        '''
        result = self._values.get("policy_details")
        assert result is not None, "Required property 'policy_details' is missing"
        return typing.cast("DlmLifecyclePolicyPolicyDetails", result)

    @builtins.property
    def state(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#state DlmLifecyclePolicy#state}.'''
        result = self._values.get("state")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#tags DlmLifecyclePolicy#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#tags_all DlmLifecyclePolicy#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DlmLifecyclePolicyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.dlm.DlmLifecyclePolicyPolicyDetails",
    jsii_struct_bases=[],
    name_mapping={
        "resource_types": "resourceTypes",
        "schedule": "schedule",
        "target_tags": "targetTags",
    },
)
class DlmLifecyclePolicyPolicyDetails:
    def __init__(
        self,
        *,
        resource_types: typing.Sequence[builtins.str],
        schedule: typing.Sequence["DlmLifecyclePolicyPolicyDetailsSchedule"],
        target_tags: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        '''
        :param resource_types: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#resource_types DlmLifecyclePolicy#resource_types}.
        :param schedule: schedule block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#schedule DlmLifecyclePolicy#schedule}
        :param target_tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#target_tags DlmLifecyclePolicy#target_tags}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "resource_types": resource_types,
            "schedule": schedule,
            "target_tags": target_tags,
        }

    @builtins.property
    def resource_types(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#resource_types DlmLifecyclePolicy#resource_types}.'''
        result = self._values.get("resource_types")
        assert result is not None, "Required property 'resource_types' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def schedule(self) -> typing.List["DlmLifecyclePolicyPolicyDetailsSchedule"]:
        '''schedule block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#schedule DlmLifecyclePolicy#schedule}
        '''
        result = self._values.get("schedule")
        assert result is not None, "Required property 'schedule' is missing"
        return typing.cast(typing.List["DlmLifecyclePolicyPolicyDetailsSchedule"], result)

    @builtins.property
    def target_tags(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#target_tags DlmLifecyclePolicy#target_tags}.'''
        result = self._values.get("target_tags")
        assert result is not None, "Required property 'target_tags' is missing"
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DlmLifecyclePolicyPolicyDetails(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DlmLifecyclePolicyPolicyDetailsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.dlm.DlmLifecyclePolicyPolicyDetailsOutputReference",
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
    @jsii.member(jsii_name="resourceTypesInput")
    def resource_types_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "resourceTypesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="scheduleInput")
    def schedule_input(
        self,
    ) -> typing.Optional[typing.List["DlmLifecyclePolicyPolicyDetailsSchedule"]]:
        return typing.cast(typing.Optional[typing.List["DlmLifecyclePolicyPolicyDetailsSchedule"]], jsii.get(self, "scheduleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetTagsInput")
    def target_tags_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "targetTagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceTypes")
    def resource_types(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "resourceTypes"))

    @resource_types.setter
    def resource_types(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "resourceTypes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="schedule")
    def schedule(self) -> typing.List["DlmLifecyclePolicyPolicyDetailsSchedule"]:
        return typing.cast(typing.List["DlmLifecyclePolicyPolicyDetailsSchedule"], jsii.get(self, "schedule"))

    @schedule.setter
    def schedule(
        self,
        value: typing.List["DlmLifecyclePolicyPolicyDetailsSchedule"],
    ) -> None:
        jsii.set(self, "schedule", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetTags")
    def target_tags(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "targetTags"))

    @target_tags.setter
    def target_tags(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "targetTags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DlmLifecyclePolicyPolicyDetails]:
        return typing.cast(typing.Optional[DlmLifecyclePolicyPolicyDetails], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DlmLifecyclePolicyPolicyDetails],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.dlm.DlmLifecyclePolicyPolicyDetailsSchedule",
    jsii_struct_bases=[],
    name_mapping={
        "create_rule": "createRule",
        "name": "name",
        "retain_rule": "retainRule",
        "copy_tags": "copyTags",
        "cross_region_copy_rule": "crossRegionCopyRule",
        "tags_to_add": "tagsToAdd",
    },
)
class DlmLifecyclePolicyPolicyDetailsSchedule:
    def __init__(
        self,
        *,
        create_rule: "DlmLifecyclePolicyPolicyDetailsScheduleCreateRule",
        name: builtins.str,
        retain_rule: "DlmLifecyclePolicyPolicyDetailsScheduleRetainRule",
        copy_tags: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        cross_region_copy_rule: typing.Optional[typing.Sequence["DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRule"]] = None,
        tags_to_add: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''
        :param create_rule: create_rule block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#create_rule DlmLifecyclePolicy#create_rule}
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#name DlmLifecyclePolicy#name}.
        :param retain_rule: retain_rule block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#retain_rule DlmLifecyclePolicy#retain_rule}
        :param copy_tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#copy_tags DlmLifecyclePolicy#copy_tags}.
        :param cross_region_copy_rule: cross_region_copy_rule block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#cross_region_copy_rule DlmLifecyclePolicy#cross_region_copy_rule}
        :param tags_to_add: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#tags_to_add DlmLifecyclePolicy#tags_to_add}.
        '''
        if isinstance(create_rule, dict):
            create_rule = DlmLifecyclePolicyPolicyDetailsScheduleCreateRule(**create_rule)
        if isinstance(retain_rule, dict):
            retain_rule = DlmLifecyclePolicyPolicyDetailsScheduleRetainRule(**retain_rule)
        self._values: typing.Dict[str, typing.Any] = {
            "create_rule": create_rule,
            "name": name,
            "retain_rule": retain_rule,
        }
        if copy_tags is not None:
            self._values["copy_tags"] = copy_tags
        if cross_region_copy_rule is not None:
            self._values["cross_region_copy_rule"] = cross_region_copy_rule
        if tags_to_add is not None:
            self._values["tags_to_add"] = tags_to_add

    @builtins.property
    def create_rule(self) -> "DlmLifecyclePolicyPolicyDetailsScheduleCreateRule":
        '''create_rule block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#create_rule DlmLifecyclePolicy#create_rule}
        '''
        result = self._values.get("create_rule")
        assert result is not None, "Required property 'create_rule' is missing"
        return typing.cast("DlmLifecyclePolicyPolicyDetailsScheduleCreateRule", result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#name DlmLifecyclePolicy#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def retain_rule(self) -> "DlmLifecyclePolicyPolicyDetailsScheduleRetainRule":
        '''retain_rule block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#retain_rule DlmLifecyclePolicy#retain_rule}
        '''
        result = self._values.get("retain_rule")
        assert result is not None, "Required property 'retain_rule' is missing"
        return typing.cast("DlmLifecyclePolicyPolicyDetailsScheduleRetainRule", result)

    @builtins.property
    def copy_tags(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#copy_tags DlmLifecyclePolicy#copy_tags}.'''
        result = self._values.get("copy_tags")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def cross_region_copy_rule(
        self,
    ) -> typing.Optional[typing.List["DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRule"]]:
        '''cross_region_copy_rule block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#cross_region_copy_rule DlmLifecyclePolicy#cross_region_copy_rule}
        '''
        result = self._values.get("cross_region_copy_rule")
        return typing.cast(typing.Optional[typing.List["DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRule"]], result)

    @builtins.property
    def tags_to_add(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#tags_to_add DlmLifecyclePolicy#tags_to_add}.'''
        result = self._values.get("tags_to_add")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DlmLifecyclePolicyPolicyDetailsSchedule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.dlm.DlmLifecyclePolicyPolicyDetailsScheduleCreateRule",
    jsii_struct_bases=[],
    name_mapping={
        "interval": "interval",
        "interval_unit": "intervalUnit",
        "times": "times",
    },
)
class DlmLifecyclePolicyPolicyDetailsScheduleCreateRule:
    def __init__(
        self,
        *,
        interval: jsii.Number,
        interval_unit: typing.Optional[builtins.str] = None,
        times: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param interval: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#interval DlmLifecyclePolicy#interval}.
        :param interval_unit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#interval_unit DlmLifecyclePolicy#interval_unit}.
        :param times: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#times DlmLifecyclePolicy#times}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "interval": interval,
        }
        if interval_unit is not None:
            self._values["interval_unit"] = interval_unit
        if times is not None:
            self._values["times"] = times

    @builtins.property
    def interval(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#interval DlmLifecyclePolicy#interval}.'''
        result = self._values.get("interval")
        assert result is not None, "Required property 'interval' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def interval_unit(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#interval_unit DlmLifecyclePolicy#interval_unit}.'''
        result = self._values.get("interval_unit")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def times(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#times DlmLifecyclePolicy#times}.'''
        result = self._values.get("times")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DlmLifecyclePolicyPolicyDetailsScheduleCreateRule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DlmLifecyclePolicyPolicyDetailsScheduleCreateRuleOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.dlm.DlmLifecyclePolicyPolicyDetailsScheduleCreateRuleOutputReference",
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

    @jsii.member(jsii_name="resetIntervalUnit")
    def reset_interval_unit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIntervalUnit", []))

    @jsii.member(jsii_name="resetTimes")
    def reset_times(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="intervalInput")
    def interval_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "intervalInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="intervalUnitInput")
    def interval_unit_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "intervalUnitInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timesInput")
    def times_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "timesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="interval")
    def interval(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "interval"))

    @interval.setter
    def interval(self, value: jsii.Number) -> None:
        jsii.set(self, "interval", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="intervalUnit")
    def interval_unit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "intervalUnit"))

    @interval_unit.setter
    def interval_unit(self, value: builtins.str) -> None:
        jsii.set(self, "intervalUnit", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="times")
    def times(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "times"))

    @times.setter
    def times(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "times", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DlmLifecyclePolicyPolicyDetailsScheduleCreateRule]:
        return typing.cast(typing.Optional[DlmLifecyclePolicyPolicyDetailsScheduleCreateRule], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DlmLifecyclePolicyPolicyDetailsScheduleCreateRule],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.dlm.DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRule",
    jsii_struct_bases=[],
    name_mapping={
        "encrypted": "encrypted",
        "target": "target",
        "cmk_arn": "cmkArn",
        "copy_tags": "copyTags",
        "deprecate_rule": "deprecateRule",
        "retain_rule": "retainRule",
    },
)
class DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRule:
    def __init__(
        self,
        *,
        encrypted: typing.Union[builtins.bool, cdktf.IResolvable],
        target: builtins.str,
        cmk_arn: typing.Optional[builtins.str] = None,
        copy_tags: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        deprecate_rule: typing.Optional["DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleDeprecateRule"] = None,
        retain_rule: typing.Optional["DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleRetainRule"] = None,
    ) -> None:
        '''
        :param encrypted: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#encrypted DlmLifecyclePolicy#encrypted}.
        :param target: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#target DlmLifecyclePolicy#target}.
        :param cmk_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#cmk_arn DlmLifecyclePolicy#cmk_arn}.
        :param copy_tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#copy_tags DlmLifecyclePolicy#copy_tags}.
        :param deprecate_rule: deprecate_rule block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#deprecate_rule DlmLifecyclePolicy#deprecate_rule}
        :param retain_rule: retain_rule block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#retain_rule DlmLifecyclePolicy#retain_rule}
        '''
        if isinstance(deprecate_rule, dict):
            deprecate_rule = DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleDeprecateRule(**deprecate_rule)
        if isinstance(retain_rule, dict):
            retain_rule = DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleRetainRule(**retain_rule)
        self._values: typing.Dict[str, typing.Any] = {
            "encrypted": encrypted,
            "target": target,
        }
        if cmk_arn is not None:
            self._values["cmk_arn"] = cmk_arn
        if copy_tags is not None:
            self._values["copy_tags"] = copy_tags
        if deprecate_rule is not None:
            self._values["deprecate_rule"] = deprecate_rule
        if retain_rule is not None:
            self._values["retain_rule"] = retain_rule

    @builtins.property
    def encrypted(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#encrypted DlmLifecyclePolicy#encrypted}.'''
        result = self._values.get("encrypted")
        assert result is not None, "Required property 'encrypted' is missing"
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], result)

    @builtins.property
    def target(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#target DlmLifecyclePolicy#target}.'''
        result = self._values.get("target")
        assert result is not None, "Required property 'target' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cmk_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#cmk_arn DlmLifecyclePolicy#cmk_arn}.'''
        result = self._values.get("cmk_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def copy_tags(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#copy_tags DlmLifecyclePolicy#copy_tags}.'''
        result = self._values.get("copy_tags")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def deprecate_rule(
        self,
    ) -> typing.Optional["DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleDeprecateRule"]:
        '''deprecate_rule block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#deprecate_rule DlmLifecyclePolicy#deprecate_rule}
        '''
        result = self._values.get("deprecate_rule")
        return typing.cast(typing.Optional["DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleDeprecateRule"], result)

    @builtins.property
    def retain_rule(
        self,
    ) -> typing.Optional["DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleRetainRule"]:
        '''retain_rule block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#retain_rule DlmLifecyclePolicy#retain_rule}
        '''
        result = self._values.get("retain_rule")
        return typing.cast(typing.Optional["DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleRetainRule"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.dlm.DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleDeprecateRule",
    jsii_struct_bases=[],
    name_mapping={"interval": "interval", "interval_unit": "intervalUnit"},
)
class DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleDeprecateRule:
    def __init__(self, *, interval: jsii.Number, interval_unit: builtins.str) -> None:
        '''
        :param interval: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#interval DlmLifecyclePolicy#interval}.
        :param interval_unit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#interval_unit DlmLifecyclePolicy#interval_unit}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "interval": interval,
            "interval_unit": interval_unit,
        }

    @builtins.property
    def interval(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#interval DlmLifecyclePolicy#interval}.'''
        result = self._values.get("interval")
        assert result is not None, "Required property 'interval' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def interval_unit(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#interval_unit DlmLifecyclePolicy#interval_unit}.'''
        result = self._values.get("interval_unit")
        assert result is not None, "Required property 'interval_unit' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleDeprecateRule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleDeprecateRuleOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.dlm.DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleDeprecateRuleOutputReference",
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
    @jsii.member(jsii_name="intervalInput")
    def interval_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "intervalInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="intervalUnitInput")
    def interval_unit_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "intervalUnitInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="interval")
    def interval(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "interval"))

    @interval.setter
    def interval(self, value: jsii.Number) -> None:
        jsii.set(self, "interval", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="intervalUnit")
    def interval_unit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "intervalUnit"))

    @interval_unit.setter
    def interval_unit(self, value: builtins.str) -> None:
        jsii.set(self, "intervalUnit", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleDeprecateRule]:
        return typing.cast(typing.Optional[DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleDeprecateRule], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleDeprecateRule],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.dlm.DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleRetainRule",
    jsii_struct_bases=[],
    name_mapping={"interval": "interval", "interval_unit": "intervalUnit"},
)
class DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleRetainRule:
    def __init__(self, *, interval: jsii.Number, interval_unit: builtins.str) -> None:
        '''
        :param interval: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#interval DlmLifecyclePolicy#interval}.
        :param interval_unit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#interval_unit DlmLifecyclePolicy#interval_unit}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "interval": interval,
            "interval_unit": interval_unit,
        }

    @builtins.property
    def interval(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#interval DlmLifecyclePolicy#interval}.'''
        result = self._values.get("interval")
        assert result is not None, "Required property 'interval' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def interval_unit(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#interval_unit DlmLifecyclePolicy#interval_unit}.'''
        result = self._values.get("interval_unit")
        assert result is not None, "Required property 'interval_unit' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleRetainRule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleRetainRuleOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.dlm.DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleRetainRuleOutputReference",
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
    @jsii.member(jsii_name="intervalInput")
    def interval_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "intervalInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="intervalUnitInput")
    def interval_unit_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "intervalUnitInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="interval")
    def interval(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "interval"))

    @interval.setter
    def interval(self, value: jsii.Number) -> None:
        jsii.set(self, "interval", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="intervalUnit")
    def interval_unit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "intervalUnit"))

    @interval_unit.setter
    def interval_unit(self, value: builtins.str) -> None:
        jsii.set(self, "intervalUnit", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleRetainRule]:
        return typing.cast(typing.Optional[DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleRetainRule], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleRetainRule],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.dlm.DlmLifecyclePolicyPolicyDetailsScheduleRetainRule",
    jsii_struct_bases=[],
    name_mapping={"count": "count"},
)
class DlmLifecyclePolicyPolicyDetailsScheduleRetainRule:
    def __init__(self, *, count: jsii.Number) -> None:
        '''
        :param count: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#count DlmLifecyclePolicy#count}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "count": count,
        }

    @builtins.property
    def count(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dlm_lifecycle_policy#count DlmLifecyclePolicy#count}.'''
        result = self._values.get("count")
        assert result is not None, "Required property 'count' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DlmLifecyclePolicyPolicyDetailsScheduleRetainRule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DlmLifecyclePolicyPolicyDetailsScheduleRetainRuleOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.dlm.DlmLifecyclePolicyPolicyDetailsScheduleRetainRuleOutputReference",
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
    @jsii.member(jsii_name="countInput")
    def count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "countInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="count")
    def count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "count"))

    @count.setter
    def count(self, value: jsii.Number) -> None:
        jsii.set(self, "count", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DlmLifecyclePolicyPolicyDetailsScheduleRetainRule]:
        return typing.cast(typing.Optional[DlmLifecyclePolicyPolicyDetailsScheduleRetainRule], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DlmLifecyclePolicyPolicyDetailsScheduleRetainRule],
    ) -> None:
        jsii.set(self, "internalValue", value)


__all__ = [
    "DlmLifecyclePolicy",
    "DlmLifecyclePolicyConfig",
    "DlmLifecyclePolicyPolicyDetails",
    "DlmLifecyclePolicyPolicyDetailsOutputReference",
    "DlmLifecyclePolicyPolicyDetailsSchedule",
    "DlmLifecyclePolicyPolicyDetailsScheduleCreateRule",
    "DlmLifecyclePolicyPolicyDetailsScheduleCreateRuleOutputReference",
    "DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRule",
    "DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleDeprecateRule",
    "DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleDeprecateRuleOutputReference",
    "DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleRetainRule",
    "DlmLifecyclePolicyPolicyDetailsScheduleCrossRegionCopyRuleRetainRuleOutputReference",
    "DlmLifecyclePolicyPolicyDetailsScheduleRetainRule",
    "DlmLifecyclePolicyPolicyDetailsScheduleRetainRuleOutputReference",
]

publication.publish()
