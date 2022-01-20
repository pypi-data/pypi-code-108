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


class CloudformationStack(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudformation.CloudformationStack",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack aws_cloudformation_stack}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        capabilities: typing.Optional[typing.Sequence[builtins.str]] = None,
        disable_rollback: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        iam_role_arn: typing.Optional[builtins.str] = None,
        notification_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        on_failure: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        policy_body: typing.Optional[builtins.str] = None,
        policy_url: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        template_body: typing.Optional[builtins.str] = None,
        template_url: typing.Optional[builtins.str] = None,
        timeout_in_minutes: typing.Optional[jsii.Number] = None,
        timeouts: typing.Optional["CloudformationStackTimeouts"] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack aws_cloudformation_stack} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack#name CloudformationStack#name}.
        :param capabilities: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack#capabilities CloudformationStack#capabilities}.
        :param disable_rollback: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack#disable_rollback CloudformationStack#disable_rollback}.
        :param iam_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack#iam_role_arn CloudformationStack#iam_role_arn}.
        :param notification_arns: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack#notification_arns CloudformationStack#notification_arns}.
        :param on_failure: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack#on_failure CloudformationStack#on_failure}.
        :param parameters: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack#parameters CloudformationStack#parameters}.
        :param policy_body: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack#policy_body CloudformationStack#policy_body}.
        :param policy_url: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack#policy_url CloudformationStack#policy_url}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack#tags CloudformationStack#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack#tags_all CloudformationStack#tags_all}.
        :param template_body: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack#template_body CloudformationStack#template_body}.
        :param template_url: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack#template_url CloudformationStack#template_url}.
        :param timeout_in_minutes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack#timeout_in_minutes CloudformationStack#timeout_in_minutes}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack#timeouts CloudformationStack#timeouts}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = CloudformationStackConfig(
            name=name,
            capabilities=capabilities,
            disable_rollback=disable_rollback,
            iam_role_arn=iam_role_arn,
            notification_arns=notification_arns,
            on_failure=on_failure,
            parameters=parameters,
            policy_body=policy_body,
            policy_url=policy_url,
            tags=tags,
            tags_all=tags_all,
            template_body=template_body,
            template_url=template_url,
            timeout_in_minutes=timeout_in_minutes,
            timeouts=timeouts,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="outputs")
    def outputs(self, key: builtins.str) -> builtins.str:
        '''
        :param key: -
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "outputs", [key]))

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack#create CloudformationStack#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack#delete CloudformationStack#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack#update CloudformationStack#update}.
        '''
        value = CloudformationStackTimeouts(
            create=create, delete=delete, update=update
        )

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetCapabilities")
    def reset_capabilities(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCapabilities", []))

    @jsii.member(jsii_name="resetDisableRollback")
    def reset_disable_rollback(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDisableRollback", []))

    @jsii.member(jsii_name="resetIamRoleArn")
    def reset_iam_role_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIamRoleArn", []))

    @jsii.member(jsii_name="resetNotificationArns")
    def reset_notification_arns(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNotificationArns", []))

    @jsii.member(jsii_name="resetOnFailure")
    def reset_on_failure(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOnFailure", []))

    @jsii.member(jsii_name="resetParameters")
    def reset_parameters(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetParameters", []))

    @jsii.member(jsii_name="resetPolicyBody")
    def reset_policy_body(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPolicyBody", []))

    @jsii.member(jsii_name="resetPolicyUrl")
    def reset_policy_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPolicyUrl", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetTemplateBody")
    def reset_template_body(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTemplateBody", []))

    @jsii.member(jsii_name="resetTemplateUrl")
    def reset_template_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTemplateUrl", []))

    @jsii.member(jsii_name="resetTimeoutInMinutes")
    def reset_timeout_in_minutes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeoutInMinutes", []))

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
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "CloudformationStackTimeoutsOutputReference":
        return typing.cast("CloudformationStackTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="capabilitiesInput")
    def capabilities_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "capabilitiesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="disableRollbackInput")
    def disable_rollback_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "disableRollbackInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="iamRoleArnInput")
    def iam_role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "iamRoleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="notificationArnsInput")
    def notification_arns_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "notificationArnsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="onFailureInput")
    def on_failure_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "onFailureInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parametersInput")
    def parameters_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "parametersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyBodyInput")
    def policy_body_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "policyBodyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyUrlInput")
    def policy_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "policyUrlInput"))

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
    @jsii.member(jsii_name="templateBodyInput")
    def template_body_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "templateBodyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="templateUrlInput")
    def template_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "templateUrlInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutInMinutesInput")
    def timeout_in_minutes_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "timeoutInMinutesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(self) -> typing.Optional["CloudformationStackTimeouts"]:
        return typing.cast(typing.Optional["CloudformationStackTimeouts"], jsii.get(self, "timeoutsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="capabilities")
    def capabilities(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "capabilities"))

    @capabilities.setter
    def capabilities(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "capabilities", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="disableRollback")
    def disable_rollback(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "disableRollback"))

    @disable_rollback.setter
    def disable_rollback(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "disableRollback", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="iamRoleArn")
    def iam_role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "iamRoleArn"))

    @iam_role_arn.setter
    def iam_role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "iamRoleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="notificationArns")
    def notification_arns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "notificationArns"))

    @notification_arns.setter
    def notification_arns(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "notificationArns", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="onFailure")
    def on_failure(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "onFailure"))

    @on_failure.setter
    def on_failure(self, value: builtins.str) -> None:
        jsii.set(self, "onFailure", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parameters")
    def parameters(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "parameters"))

    @parameters.setter
    def parameters(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "parameters", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyBody")
    def policy_body(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policyBody"))

    @policy_body.setter
    def policy_body(self, value: builtins.str) -> None:
        jsii.set(self, "policyBody", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyUrl")
    def policy_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policyUrl"))

    @policy_url.setter
    def policy_url(self, value: builtins.str) -> None:
        jsii.set(self, "policyUrl", value)

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
    @jsii.member(jsii_name="templateBody")
    def template_body(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "templateBody"))

    @template_body.setter
    def template_body(self, value: builtins.str) -> None:
        jsii.set(self, "templateBody", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="templateUrl")
    def template_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "templateUrl"))

    @template_url.setter
    def template_url(self, value: builtins.str) -> None:
        jsii.set(self, "templateUrl", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutInMinutes")
    def timeout_in_minutes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "timeoutInMinutes"))

    @timeout_in_minutes.setter
    def timeout_in_minutes(self, value: jsii.Number) -> None:
        jsii.set(self, "timeoutInMinutes", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudformation.CloudformationStackConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "capabilities": "capabilities",
        "disable_rollback": "disableRollback",
        "iam_role_arn": "iamRoleArn",
        "notification_arns": "notificationArns",
        "on_failure": "onFailure",
        "parameters": "parameters",
        "policy_body": "policyBody",
        "policy_url": "policyUrl",
        "tags": "tags",
        "tags_all": "tagsAll",
        "template_body": "templateBody",
        "template_url": "templateUrl",
        "timeout_in_minutes": "timeoutInMinutes",
        "timeouts": "timeouts",
    },
)
class CloudformationStackConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        capabilities: typing.Optional[typing.Sequence[builtins.str]] = None,
        disable_rollback: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        iam_role_arn: typing.Optional[builtins.str] = None,
        notification_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        on_failure: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        policy_body: typing.Optional[builtins.str] = None,
        policy_url: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        template_body: typing.Optional[builtins.str] = None,
        template_url: typing.Optional[builtins.str] = None,
        timeout_in_minutes: typing.Optional[jsii.Number] = None,
        timeouts: typing.Optional["CloudformationStackTimeouts"] = None,
    ) -> None:
        '''AWS CloudFormation.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack#name CloudformationStack#name}.
        :param capabilities: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack#capabilities CloudformationStack#capabilities}.
        :param disable_rollback: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack#disable_rollback CloudformationStack#disable_rollback}.
        :param iam_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack#iam_role_arn CloudformationStack#iam_role_arn}.
        :param notification_arns: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack#notification_arns CloudformationStack#notification_arns}.
        :param on_failure: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack#on_failure CloudformationStack#on_failure}.
        :param parameters: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack#parameters CloudformationStack#parameters}.
        :param policy_body: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack#policy_body CloudformationStack#policy_body}.
        :param policy_url: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack#policy_url CloudformationStack#policy_url}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack#tags CloudformationStack#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack#tags_all CloudformationStack#tags_all}.
        :param template_body: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack#template_body CloudformationStack#template_body}.
        :param template_url: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack#template_url CloudformationStack#template_url}.
        :param timeout_in_minutes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack#timeout_in_minutes CloudformationStack#timeout_in_minutes}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack#timeouts CloudformationStack#timeouts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(timeouts, dict):
            timeouts = CloudformationStackTimeouts(**timeouts)
        self._values: typing.Dict[str, typing.Any] = {
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
        if capabilities is not None:
            self._values["capabilities"] = capabilities
        if disable_rollback is not None:
            self._values["disable_rollback"] = disable_rollback
        if iam_role_arn is not None:
            self._values["iam_role_arn"] = iam_role_arn
        if notification_arns is not None:
            self._values["notification_arns"] = notification_arns
        if on_failure is not None:
            self._values["on_failure"] = on_failure
        if parameters is not None:
            self._values["parameters"] = parameters
        if policy_body is not None:
            self._values["policy_body"] = policy_body
        if policy_url is not None:
            self._values["policy_url"] = policy_url
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if template_body is not None:
            self._values["template_body"] = template_body
        if template_url is not None:
            self._values["template_url"] = template_url
        if timeout_in_minutes is not None:
            self._values["timeout_in_minutes"] = timeout_in_minutes
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
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack#name CloudformationStack#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def capabilities(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack#capabilities CloudformationStack#capabilities}.'''
        result = self._values.get("capabilities")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def disable_rollback(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack#disable_rollback CloudformationStack#disable_rollback}.'''
        result = self._values.get("disable_rollback")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def iam_role_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack#iam_role_arn CloudformationStack#iam_role_arn}.'''
        result = self._values.get("iam_role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def notification_arns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack#notification_arns CloudformationStack#notification_arns}.'''
        result = self._values.get("notification_arns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def on_failure(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack#on_failure CloudformationStack#on_failure}.'''
        result = self._values.get("on_failure")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parameters(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack#parameters CloudformationStack#parameters}.'''
        result = self._values.get("parameters")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def policy_body(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack#policy_body CloudformationStack#policy_body}.'''
        result = self._values.get("policy_body")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def policy_url(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack#policy_url CloudformationStack#policy_url}.'''
        result = self._values.get("policy_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack#tags CloudformationStack#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack#tags_all CloudformationStack#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def template_body(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack#template_body CloudformationStack#template_body}.'''
        result = self._values.get("template_body")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def template_url(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack#template_url CloudformationStack#template_url}.'''
        result = self._values.get("template_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timeout_in_minutes(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack#timeout_in_minutes CloudformationStack#timeout_in_minutes}.'''
        result = self._values.get("timeout_in_minutes")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["CloudformationStackTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack#timeouts CloudformationStack#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["CloudformationStackTimeouts"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudformationStackConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudformationStackSet(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudformation.CloudformationStackSet",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set aws_cloudformation_stack_set}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        administration_role_arn: typing.Optional[builtins.str] = None,
        auto_deployment: typing.Optional["CloudformationStackSetAutoDeployment"] = None,
        capabilities: typing.Optional[typing.Sequence[builtins.str]] = None,
        description: typing.Optional[builtins.str] = None,
        execution_role_name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        permission_model: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        template_body: typing.Optional[builtins.str] = None,
        template_url: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional["CloudformationStackSetTimeouts"] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set aws_cloudformation_stack_set} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set#name CloudformationStackSet#name}.
        :param administration_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set#administration_role_arn CloudformationStackSet#administration_role_arn}.
        :param auto_deployment: auto_deployment block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set#auto_deployment CloudformationStackSet#auto_deployment}
        :param capabilities: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set#capabilities CloudformationStackSet#capabilities}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set#description CloudformationStackSet#description}.
        :param execution_role_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set#execution_role_name CloudformationStackSet#execution_role_name}.
        :param parameters: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set#parameters CloudformationStackSet#parameters}.
        :param permission_model: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set#permission_model CloudformationStackSet#permission_model}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set#tags CloudformationStackSet#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set#tags_all CloudformationStackSet#tags_all}.
        :param template_body: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set#template_body CloudformationStackSet#template_body}.
        :param template_url: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set#template_url CloudformationStackSet#template_url}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set#timeouts CloudformationStackSet#timeouts}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = CloudformationStackSetConfig(
            name=name,
            administration_role_arn=administration_role_arn,
            auto_deployment=auto_deployment,
            capabilities=capabilities,
            description=description,
            execution_role_name=execution_role_name,
            parameters=parameters,
            permission_model=permission_model,
            tags=tags,
            tags_all=tags_all,
            template_body=template_body,
            template_url=template_url,
            timeouts=timeouts,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putAutoDeployment")
    def put_auto_deployment(
        self,
        *,
        enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        retain_stacks_on_account_removal: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set#enabled CloudformationStackSet#enabled}.
        :param retain_stacks_on_account_removal: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set#retain_stacks_on_account_removal CloudformationStackSet#retain_stacks_on_account_removal}.
        '''
        value = CloudformationStackSetAutoDeployment(
            enabled=enabled,
            retain_stacks_on_account_removal=retain_stacks_on_account_removal,
        )

        return typing.cast(None, jsii.invoke(self, "putAutoDeployment", [value]))

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(self, *, update: typing.Optional[builtins.str] = None) -> None:
        '''
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set#update CloudformationStackSet#update}.
        '''
        value = CloudformationStackSetTimeouts(update=update)

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetAdministrationRoleArn")
    def reset_administration_role_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAdministrationRoleArn", []))

    @jsii.member(jsii_name="resetAutoDeployment")
    def reset_auto_deployment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoDeployment", []))

    @jsii.member(jsii_name="resetCapabilities")
    def reset_capabilities(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCapabilities", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetExecutionRoleName")
    def reset_execution_role_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExecutionRoleName", []))

    @jsii.member(jsii_name="resetParameters")
    def reset_parameters(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetParameters", []))

    @jsii.member(jsii_name="resetPermissionModel")
    def reset_permission_model(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPermissionModel", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetTemplateBody")
    def reset_template_body(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTemplateBody", []))

    @jsii.member(jsii_name="resetTemplateUrl")
    def reset_template_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTemplateUrl", []))

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
    @jsii.member(jsii_name="autoDeployment")
    def auto_deployment(self) -> "CloudformationStackSetAutoDeploymentOutputReference":
        return typing.cast("CloudformationStackSetAutoDeploymentOutputReference", jsii.get(self, "autoDeployment"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stackSetId")
    def stack_set_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "stackSetId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "CloudformationStackSetTimeoutsOutputReference":
        return typing.cast("CloudformationStackSetTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="administrationRoleArnInput")
    def administration_role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "administrationRoleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoDeploymentInput")
    def auto_deployment_input(
        self,
    ) -> typing.Optional["CloudformationStackSetAutoDeployment"]:
        return typing.cast(typing.Optional["CloudformationStackSetAutoDeployment"], jsii.get(self, "autoDeploymentInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="capabilitiesInput")
    def capabilities_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "capabilitiesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="executionRoleNameInput")
    def execution_role_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "executionRoleNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parametersInput")
    def parameters_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "parametersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="permissionModelInput")
    def permission_model_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "permissionModelInput"))

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
    @jsii.member(jsii_name="templateBodyInput")
    def template_body_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "templateBodyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="templateUrlInput")
    def template_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "templateUrlInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(self) -> typing.Optional["CloudformationStackSetTimeouts"]:
        return typing.cast(typing.Optional["CloudformationStackSetTimeouts"], jsii.get(self, "timeoutsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="administrationRoleArn")
    def administration_role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "administrationRoleArn"))

    @administration_role_arn.setter
    def administration_role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "administrationRoleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="capabilities")
    def capabilities(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "capabilities"))

    @capabilities.setter
    def capabilities(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "capabilities", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="executionRoleName")
    def execution_role_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "executionRoleName"))

    @execution_role_name.setter
    def execution_role_name(self, value: builtins.str) -> None:
        jsii.set(self, "executionRoleName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parameters")
    def parameters(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "parameters"))

    @parameters.setter
    def parameters(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "parameters", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="permissionModel")
    def permission_model(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "permissionModel"))

    @permission_model.setter
    def permission_model(self, value: builtins.str) -> None:
        jsii.set(self, "permissionModel", value)

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
    @jsii.member(jsii_name="templateBody")
    def template_body(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "templateBody"))

    @template_body.setter
    def template_body(self, value: builtins.str) -> None:
        jsii.set(self, "templateBody", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="templateUrl")
    def template_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "templateUrl"))

    @template_url.setter
    def template_url(self, value: builtins.str) -> None:
        jsii.set(self, "templateUrl", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudformation.CloudformationStackSetAutoDeployment",
    jsii_struct_bases=[],
    name_mapping={
        "enabled": "enabled",
        "retain_stacks_on_account_removal": "retainStacksOnAccountRemoval",
    },
)
class CloudformationStackSetAutoDeployment:
    def __init__(
        self,
        *,
        enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        retain_stacks_on_account_removal: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set#enabled CloudformationStackSet#enabled}.
        :param retain_stacks_on_account_removal: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set#retain_stacks_on_account_removal CloudformationStackSet#retain_stacks_on_account_removal}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if enabled is not None:
            self._values["enabled"] = enabled
        if retain_stacks_on_account_removal is not None:
            self._values["retain_stacks_on_account_removal"] = retain_stacks_on_account_removal

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set#enabled CloudformationStackSet#enabled}.'''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def retain_stacks_on_account_removal(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set#retain_stacks_on_account_removal CloudformationStackSet#retain_stacks_on_account_removal}.'''
        result = self._values.get("retain_stacks_on_account_removal")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudformationStackSetAutoDeployment(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudformationStackSetAutoDeploymentOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudformation.CloudformationStackSetAutoDeploymentOutputReference",
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

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="resetRetainStacksOnAccountRemoval")
    def reset_retain_stacks_on_account_removal(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRetainStacksOnAccountRemoval", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="retainStacksOnAccountRemovalInput")
    def retain_stacks_on_account_removal_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "retainStacksOnAccountRemovalInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "enabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="retainStacksOnAccountRemoval")
    def retain_stacks_on_account_removal(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "retainStacksOnAccountRemoval"))

    @retain_stacks_on_account_removal.setter
    def retain_stacks_on_account_removal(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "retainStacksOnAccountRemoval", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[CloudformationStackSetAutoDeployment]:
        return typing.cast(typing.Optional[CloudformationStackSetAutoDeployment], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CloudformationStackSetAutoDeployment],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudformation.CloudformationStackSetConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "administration_role_arn": "administrationRoleArn",
        "auto_deployment": "autoDeployment",
        "capabilities": "capabilities",
        "description": "description",
        "execution_role_name": "executionRoleName",
        "parameters": "parameters",
        "permission_model": "permissionModel",
        "tags": "tags",
        "tags_all": "tagsAll",
        "template_body": "templateBody",
        "template_url": "templateUrl",
        "timeouts": "timeouts",
    },
)
class CloudformationStackSetConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        administration_role_arn: typing.Optional[builtins.str] = None,
        auto_deployment: typing.Optional[CloudformationStackSetAutoDeployment] = None,
        capabilities: typing.Optional[typing.Sequence[builtins.str]] = None,
        description: typing.Optional[builtins.str] = None,
        execution_role_name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        permission_model: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        template_body: typing.Optional[builtins.str] = None,
        template_url: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional["CloudformationStackSetTimeouts"] = None,
    ) -> None:
        '''AWS CloudFormation.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set#name CloudformationStackSet#name}.
        :param administration_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set#administration_role_arn CloudformationStackSet#administration_role_arn}.
        :param auto_deployment: auto_deployment block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set#auto_deployment CloudformationStackSet#auto_deployment}
        :param capabilities: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set#capabilities CloudformationStackSet#capabilities}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set#description CloudformationStackSet#description}.
        :param execution_role_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set#execution_role_name CloudformationStackSet#execution_role_name}.
        :param parameters: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set#parameters CloudformationStackSet#parameters}.
        :param permission_model: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set#permission_model CloudformationStackSet#permission_model}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set#tags CloudformationStackSet#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set#tags_all CloudformationStackSet#tags_all}.
        :param template_body: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set#template_body CloudformationStackSet#template_body}.
        :param template_url: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set#template_url CloudformationStackSet#template_url}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set#timeouts CloudformationStackSet#timeouts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(auto_deployment, dict):
            auto_deployment = CloudformationStackSetAutoDeployment(**auto_deployment)
        if isinstance(timeouts, dict):
            timeouts = CloudformationStackSetTimeouts(**timeouts)
        self._values: typing.Dict[str, typing.Any] = {
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
        if administration_role_arn is not None:
            self._values["administration_role_arn"] = administration_role_arn
        if auto_deployment is not None:
            self._values["auto_deployment"] = auto_deployment
        if capabilities is not None:
            self._values["capabilities"] = capabilities
        if description is not None:
            self._values["description"] = description
        if execution_role_name is not None:
            self._values["execution_role_name"] = execution_role_name
        if parameters is not None:
            self._values["parameters"] = parameters
        if permission_model is not None:
            self._values["permission_model"] = permission_model
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if template_body is not None:
            self._values["template_body"] = template_body
        if template_url is not None:
            self._values["template_url"] = template_url
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
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set#name CloudformationStackSet#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def administration_role_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set#administration_role_arn CloudformationStackSet#administration_role_arn}.'''
        result = self._values.get("administration_role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def auto_deployment(self) -> typing.Optional[CloudformationStackSetAutoDeployment]:
        '''auto_deployment block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set#auto_deployment CloudformationStackSet#auto_deployment}
        '''
        result = self._values.get("auto_deployment")
        return typing.cast(typing.Optional[CloudformationStackSetAutoDeployment], result)

    @builtins.property
    def capabilities(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set#capabilities CloudformationStackSet#capabilities}.'''
        result = self._values.get("capabilities")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set#description CloudformationStackSet#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def execution_role_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set#execution_role_name CloudformationStackSet#execution_role_name}.'''
        result = self._values.get("execution_role_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parameters(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set#parameters CloudformationStackSet#parameters}.'''
        result = self._values.get("parameters")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def permission_model(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set#permission_model CloudformationStackSet#permission_model}.'''
        result = self._values.get("permission_model")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set#tags CloudformationStackSet#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set#tags_all CloudformationStackSet#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def template_body(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set#template_body CloudformationStackSet#template_body}.'''
        result = self._values.get("template_body")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def template_url(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set#template_url CloudformationStackSet#template_url}.'''
        result = self._values.get("template_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["CloudformationStackSetTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set#timeouts CloudformationStackSet#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["CloudformationStackSetTimeouts"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudformationStackSetConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudformationStackSetInstance(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudformation.CloudformationStackSetInstance",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set_instance aws_cloudformation_stack_set_instance}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        stack_set_name: builtins.str,
        account_id: typing.Optional[builtins.str] = None,
        deployment_targets: typing.Optional["CloudformationStackSetInstanceDeploymentTargets"] = None,
        parameter_overrides: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        region: typing.Optional[builtins.str] = None,
        retain_stack: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        timeouts: typing.Optional["CloudformationStackSetInstanceTimeouts"] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set_instance aws_cloudformation_stack_set_instance} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param stack_set_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set_instance#stack_set_name CloudformationStackSetInstance#stack_set_name}.
        :param account_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set_instance#account_id CloudformationStackSetInstance#account_id}.
        :param deployment_targets: deployment_targets block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set_instance#deployment_targets CloudformationStackSetInstance#deployment_targets}
        :param parameter_overrides: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set_instance#parameter_overrides CloudformationStackSetInstance#parameter_overrides}.
        :param region: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set_instance#region CloudformationStackSetInstance#region}.
        :param retain_stack: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set_instance#retain_stack CloudformationStackSetInstance#retain_stack}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set_instance#timeouts CloudformationStackSetInstance#timeouts}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = CloudformationStackSetInstanceConfig(
            stack_set_name=stack_set_name,
            account_id=account_id,
            deployment_targets=deployment_targets,
            parameter_overrides=parameter_overrides,
            region=region,
            retain_stack=retain_stack,
            timeouts=timeouts,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putDeploymentTargets")
    def put_deployment_targets(
        self,
        *,
        organizational_unit_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param organizational_unit_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set_instance#organizational_unit_ids CloudformationStackSetInstance#organizational_unit_ids}.
        '''
        value = CloudformationStackSetInstanceDeploymentTargets(
            organizational_unit_ids=organizational_unit_ids
        )

        return typing.cast(None, jsii.invoke(self, "putDeploymentTargets", [value]))

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set_instance#create CloudformationStackSetInstance#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set_instance#delete CloudformationStackSetInstance#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set_instance#update CloudformationStackSetInstance#update}.
        '''
        value = CloudformationStackSetInstanceTimeouts(
            create=create, delete=delete, update=update
        )

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetAccountId")
    def reset_account_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccountId", []))

    @jsii.member(jsii_name="resetDeploymentTargets")
    def reset_deployment_targets(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeploymentTargets", []))

    @jsii.member(jsii_name="resetParameterOverrides")
    def reset_parameter_overrides(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetParameterOverrides", []))

    @jsii.member(jsii_name="resetRegion")
    def reset_region(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegion", []))

    @jsii.member(jsii_name="resetRetainStack")
    def reset_retain_stack(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRetainStack", []))

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
    @jsii.member(jsii_name="deploymentTargets")
    def deployment_targets(
        self,
    ) -> "CloudformationStackSetInstanceDeploymentTargetsOutputReference":
        return typing.cast("CloudformationStackSetInstanceDeploymentTargetsOutputReference", jsii.get(self, "deploymentTargets"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organizationalUnitId")
    def organizational_unit_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "organizationalUnitId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stackId")
    def stack_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "stackId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "CloudformationStackSetInstanceTimeoutsOutputReference":
        return typing.cast("CloudformationStackSetInstanceTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deploymentTargetsInput")
    def deployment_targets_input(
        self,
    ) -> typing.Optional["CloudformationStackSetInstanceDeploymentTargets"]:
        return typing.cast(typing.Optional["CloudformationStackSetInstanceDeploymentTargets"], jsii.get(self, "deploymentTargetsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parameterOverridesInput")
    def parameter_overrides_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "parameterOverridesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="regionInput")
    def region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "regionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="retainStackInput")
    def retain_stack_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "retainStackInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stackSetNameInput")
    def stack_set_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stackSetNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(
        self,
    ) -> typing.Optional["CloudformationStackSetInstanceTimeouts"]:
        return typing.cast(typing.Optional["CloudformationStackSetInstanceTimeouts"], jsii.get(self, "timeoutsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: builtins.str) -> None:
        jsii.set(self, "accountId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parameterOverrides")
    def parameter_overrides(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "parameterOverrides"))

    @parameter_overrides.setter
    def parameter_overrides(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "parameterOverrides", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @region.setter
    def region(self, value: builtins.str) -> None:
        jsii.set(self, "region", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="retainStack")
    def retain_stack(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "retainStack"))

    @retain_stack.setter
    def retain_stack(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "retainStack", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stackSetName")
    def stack_set_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "stackSetName"))

    @stack_set_name.setter
    def stack_set_name(self, value: builtins.str) -> None:
        jsii.set(self, "stackSetName", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudformation.CloudformationStackSetInstanceConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "stack_set_name": "stackSetName",
        "account_id": "accountId",
        "deployment_targets": "deploymentTargets",
        "parameter_overrides": "parameterOverrides",
        "region": "region",
        "retain_stack": "retainStack",
        "timeouts": "timeouts",
    },
)
class CloudformationStackSetInstanceConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        stack_set_name: builtins.str,
        account_id: typing.Optional[builtins.str] = None,
        deployment_targets: typing.Optional["CloudformationStackSetInstanceDeploymentTargets"] = None,
        parameter_overrides: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        region: typing.Optional[builtins.str] = None,
        retain_stack: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        timeouts: typing.Optional["CloudformationStackSetInstanceTimeouts"] = None,
    ) -> None:
        '''AWS CloudFormation.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param stack_set_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set_instance#stack_set_name CloudformationStackSetInstance#stack_set_name}.
        :param account_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set_instance#account_id CloudformationStackSetInstance#account_id}.
        :param deployment_targets: deployment_targets block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set_instance#deployment_targets CloudformationStackSetInstance#deployment_targets}
        :param parameter_overrides: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set_instance#parameter_overrides CloudformationStackSetInstance#parameter_overrides}.
        :param region: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set_instance#region CloudformationStackSetInstance#region}.
        :param retain_stack: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set_instance#retain_stack CloudformationStackSetInstance#retain_stack}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set_instance#timeouts CloudformationStackSetInstance#timeouts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(deployment_targets, dict):
            deployment_targets = CloudformationStackSetInstanceDeploymentTargets(**deployment_targets)
        if isinstance(timeouts, dict):
            timeouts = CloudformationStackSetInstanceTimeouts(**timeouts)
        self._values: typing.Dict[str, typing.Any] = {
            "stack_set_name": stack_set_name,
        }
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
        if deployment_targets is not None:
            self._values["deployment_targets"] = deployment_targets
        if parameter_overrides is not None:
            self._values["parameter_overrides"] = parameter_overrides
        if region is not None:
            self._values["region"] = region
        if retain_stack is not None:
            self._values["retain_stack"] = retain_stack
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
    def stack_set_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set_instance#stack_set_name CloudformationStackSetInstance#stack_set_name}.'''
        result = self._values.get("stack_set_name")
        assert result is not None, "Required property 'stack_set_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def account_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set_instance#account_id CloudformationStackSetInstance#account_id}.'''
        result = self._values.get("account_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def deployment_targets(
        self,
    ) -> typing.Optional["CloudformationStackSetInstanceDeploymentTargets"]:
        '''deployment_targets block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set_instance#deployment_targets CloudformationStackSetInstance#deployment_targets}
        '''
        result = self._values.get("deployment_targets")
        return typing.cast(typing.Optional["CloudformationStackSetInstanceDeploymentTargets"], result)

    @builtins.property
    def parameter_overrides(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set_instance#parameter_overrides CloudformationStackSetInstance#parameter_overrides}.'''
        result = self._values.get("parameter_overrides")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set_instance#region CloudformationStackSetInstance#region}.'''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def retain_stack(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set_instance#retain_stack CloudformationStackSetInstance#retain_stack}.'''
        result = self._values.get("retain_stack")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["CloudformationStackSetInstanceTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set_instance#timeouts CloudformationStackSetInstance#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["CloudformationStackSetInstanceTimeouts"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudformationStackSetInstanceConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudformation.CloudformationStackSetInstanceDeploymentTargets",
    jsii_struct_bases=[],
    name_mapping={"organizational_unit_ids": "organizationalUnitIds"},
)
class CloudformationStackSetInstanceDeploymentTargets:
    def __init__(
        self,
        *,
        organizational_unit_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param organizational_unit_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set_instance#organizational_unit_ids CloudformationStackSetInstance#organizational_unit_ids}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if organizational_unit_ids is not None:
            self._values["organizational_unit_ids"] = organizational_unit_ids

    @builtins.property
    def organizational_unit_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set_instance#organizational_unit_ids CloudformationStackSetInstance#organizational_unit_ids}.'''
        result = self._values.get("organizational_unit_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudformationStackSetInstanceDeploymentTargets(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudformationStackSetInstanceDeploymentTargetsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudformation.CloudformationStackSetInstanceDeploymentTargetsOutputReference",
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

    @jsii.member(jsii_name="resetOrganizationalUnitIds")
    def reset_organizational_unit_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOrganizationalUnitIds", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organizationalUnitIdsInput")
    def organizational_unit_ids_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "organizationalUnitIdsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organizationalUnitIds")
    def organizational_unit_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "organizationalUnitIds"))

    @organizational_unit_ids.setter
    def organizational_unit_ids(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "organizationalUnitIds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CloudformationStackSetInstanceDeploymentTargets]:
        return typing.cast(typing.Optional[CloudformationStackSetInstanceDeploymentTargets], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CloudformationStackSetInstanceDeploymentTargets],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudformation.CloudformationStackSetInstanceTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete", "update": "update"},
)
class CloudformationStackSetInstanceTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set_instance#create CloudformationStackSetInstance#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set_instance#delete CloudformationStackSetInstance#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set_instance#update CloudformationStackSetInstance#update}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if create is not None:
            self._values["create"] = create
        if delete is not None:
            self._values["delete"] = delete
        if update is not None:
            self._values["update"] = update

    @builtins.property
    def create(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set_instance#create CloudformationStackSetInstance#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set_instance#delete CloudformationStackSetInstance#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set_instance#update CloudformationStackSetInstance#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudformationStackSetInstanceTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudformationStackSetInstanceTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudformation.CloudformationStackSetInstanceTimeoutsOutputReference",
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

    @jsii.member(jsii_name="resetDelete")
    def reset_delete(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDelete", []))

    @jsii.member(jsii_name="resetUpdate")
    def reset_update(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpdate", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createInput")
    def create_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deleteInput")
    def delete_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deleteInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="updateInput")
    def update_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "updateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="create")
    def create(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "create"))

    @create.setter
    def create(self, value: builtins.str) -> None:
        jsii.set(self, "create", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="delete")
    def delete(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "delete"))

    @delete.setter
    def delete(self, value: builtins.str) -> None:
        jsii.set(self, "delete", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="update")
    def update(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "update"))

    @update.setter
    def update(self, value: builtins.str) -> None:
        jsii.set(self, "update", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[CloudformationStackSetInstanceTimeouts]:
        return typing.cast(typing.Optional[CloudformationStackSetInstanceTimeouts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CloudformationStackSetInstanceTimeouts],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudformation.CloudformationStackSetTimeouts",
    jsii_struct_bases=[],
    name_mapping={"update": "update"},
)
class CloudformationStackSetTimeouts:
    def __init__(self, *, update: typing.Optional[builtins.str] = None) -> None:
        '''
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set#update CloudformationStackSet#update}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if update is not None:
            self._values["update"] = update

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack_set#update CloudformationStackSet#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudformationStackSetTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudformationStackSetTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudformation.CloudformationStackSetTimeoutsOutputReference",
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

    @jsii.member(jsii_name="resetUpdate")
    def reset_update(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpdate", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="updateInput")
    def update_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "updateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="update")
    def update(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "update"))

    @update.setter
    def update(self, value: builtins.str) -> None:
        jsii.set(self, "update", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[CloudformationStackSetTimeouts]:
        return typing.cast(typing.Optional[CloudformationStackSetTimeouts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CloudformationStackSetTimeouts],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudformation.CloudformationStackTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete", "update": "update"},
)
class CloudformationStackTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack#create CloudformationStack#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack#delete CloudformationStack#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack#update CloudformationStack#update}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if create is not None:
            self._values["create"] = create
        if delete is not None:
            self._values["delete"] = delete
        if update is not None:
            self._values["update"] = update

    @builtins.property
    def create(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack#create CloudformationStack#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack#delete CloudformationStack#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_stack#update CloudformationStack#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudformationStackTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudformationStackTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudformation.CloudformationStackTimeoutsOutputReference",
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

    @jsii.member(jsii_name="resetDelete")
    def reset_delete(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDelete", []))

    @jsii.member(jsii_name="resetUpdate")
    def reset_update(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpdate", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createInput")
    def create_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deleteInput")
    def delete_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deleteInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="updateInput")
    def update_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "updateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="create")
    def create(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "create"))

    @create.setter
    def create(self, value: builtins.str) -> None:
        jsii.set(self, "create", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="delete")
    def delete(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "delete"))

    @delete.setter
    def delete(self, value: builtins.str) -> None:
        jsii.set(self, "delete", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="update")
    def update(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "update"))

    @update.setter
    def update(self, value: builtins.str) -> None:
        jsii.set(self, "update", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[CloudformationStackTimeouts]:
        return typing.cast(typing.Optional[CloudformationStackTimeouts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CloudformationStackTimeouts],
    ) -> None:
        jsii.set(self, "internalValue", value)


class CloudformationType(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudformation.CloudformationType",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_type aws_cloudformation_type}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        schema_handler_package: builtins.str,
        type_name: builtins.str,
        execution_role_arn: typing.Optional[builtins.str] = None,
        logging_config: typing.Optional["CloudformationTypeLoggingConfig"] = None,
        type: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_type aws_cloudformation_type} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param schema_handler_package: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_type#schema_handler_package CloudformationType#schema_handler_package}.
        :param type_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_type#type_name CloudformationType#type_name}.
        :param execution_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_type#execution_role_arn CloudformationType#execution_role_arn}.
        :param logging_config: logging_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_type#logging_config CloudformationType#logging_config}
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_type#type CloudformationType#type}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = CloudformationTypeConfig(
            schema_handler_package=schema_handler_package,
            type_name=type_name,
            execution_role_arn=execution_role_arn,
            logging_config=logging_config,
            type=type,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putLoggingConfig")
    def put_logging_config(
        self,
        *,
        log_group_name: builtins.str,
        log_role_arn: builtins.str,
    ) -> None:
        '''
        :param log_group_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_type#log_group_name CloudformationType#log_group_name}.
        :param log_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_type#log_role_arn CloudformationType#log_role_arn}.
        '''
        value = CloudformationTypeLoggingConfig(
            log_group_name=log_group_name, log_role_arn=log_role_arn
        )

        return typing.cast(None, jsii.invoke(self, "putLoggingConfig", [value]))

    @jsii.member(jsii_name="resetExecutionRoleArn")
    def reset_execution_role_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExecutionRoleArn", []))

    @jsii.member(jsii_name="resetLoggingConfig")
    def reset_logging_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLoggingConfig", []))

    @jsii.member(jsii_name="resetType")
    def reset_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetType", []))

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
    @jsii.member(jsii_name="defaultVersionId")
    def default_version_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "defaultVersionId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deprecatedStatus")
    def deprecated_status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deprecatedStatus"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="documentationUrl")
    def documentation_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "documentationUrl"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="isDefaultVersion")
    def is_default_version(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "isDefaultVersion"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="loggingConfig")
    def logging_config(self) -> "CloudformationTypeLoggingConfigOutputReference":
        return typing.cast("CloudformationTypeLoggingConfigOutputReference", jsii.get(self, "loggingConfig"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="provisioningType")
    def provisioning_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "provisioningType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="schema")
    def schema(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "schema"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceUrl")
    def source_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceUrl"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="typeArn")
    def type_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "typeArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="versionId")
    def version_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "versionId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="visibility")
    def visibility(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "visibility"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="executionRoleArnInput")
    def execution_role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "executionRoleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="loggingConfigInput")
    def logging_config_input(
        self,
    ) -> typing.Optional["CloudformationTypeLoggingConfig"]:
        return typing.cast(typing.Optional["CloudformationTypeLoggingConfig"], jsii.get(self, "loggingConfigInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="schemaHandlerPackageInput")
    def schema_handler_package_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "schemaHandlerPackageInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="typeNameInput")
    def type_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="executionRoleArn")
    def execution_role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "executionRoleArn"))

    @execution_role_arn.setter
    def execution_role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "executionRoleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="schemaHandlerPackage")
    def schema_handler_package(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "schemaHandlerPackage"))

    @schema_handler_package.setter
    def schema_handler_package(self, value: builtins.str) -> None:
        jsii.set(self, "schemaHandlerPackage", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        jsii.set(self, "type", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="typeName")
    def type_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "typeName"))

    @type_name.setter
    def type_name(self, value: builtins.str) -> None:
        jsii.set(self, "typeName", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudformation.CloudformationTypeConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "schema_handler_package": "schemaHandlerPackage",
        "type_name": "typeName",
        "execution_role_arn": "executionRoleArn",
        "logging_config": "loggingConfig",
        "type": "type",
    },
)
class CloudformationTypeConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        schema_handler_package: builtins.str,
        type_name: builtins.str,
        execution_role_arn: typing.Optional[builtins.str] = None,
        logging_config: typing.Optional["CloudformationTypeLoggingConfig"] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS CloudFormation.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param schema_handler_package: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_type#schema_handler_package CloudformationType#schema_handler_package}.
        :param type_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_type#type_name CloudformationType#type_name}.
        :param execution_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_type#execution_role_arn CloudformationType#execution_role_arn}.
        :param logging_config: logging_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_type#logging_config CloudformationType#logging_config}
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_type#type CloudformationType#type}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(logging_config, dict):
            logging_config = CloudformationTypeLoggingConfig(**logging_config)
        self._values: typing.Dict[str, typing.Any] = {
            "schema_handler_package": schema_handler_package,
            "type_name": type_name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if execution_role_arn is not None:
            self._values["execution_role_arn"] = execution_role_arn
        if logging_config is not None:
            self._values["logging_config"] = logging_config
        if type is not None:
            self._values["type"] = type

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
    def schema_handler_package(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_type#schema_handler_package CloudformationType#schema_handler_package}.'''
        result = self._values.get("schema_handler_package")
        assert result is not None, "Required property 'schema_handler_package' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_type#type_name CloudformationType#type_name}.'''
        result = self._values.get("type_name")
        assert result is not None, "Required property 'type_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def execution_role_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_type#execution_role_arn CloudformationType#execution_role_arn}.'''
        result = self._values.get("execution_role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def logging_config(self) -> typing.Optional["CloudformationTypeLoggingConfig"]:
        '''logging_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_type#logging_config CloudformationType#logging_config}
        '''
        result = self._values.get("logging_config")
        return typing.cast(typing.Optional["CloudformationTypeLoggingConfig"], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_type#type CloudformationType#type}.'''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudformationTypeConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudformation.CloudformationTypeLoggingConfig",
    jsii_struct_bases=[],
    name_mapping={"log_group_name": "logGroupName", "log_role_arn": "logRoleArn"},
)
class CloudformationTypeLoggingConfig:
    def __init__(
        self,
        *,
        log_group_name: builtins.str,
        log_role_arn: builtins.str,
    ) -> None:
        '''
        :param log_group_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_type#log_group_name CloudformationType#log_group_name}.
        :param log_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_type#log_role_arn CloudformationType#log_role_arn}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "log_group_name": log_group_name,
            "log_role_arn": log_role_arn,
        }

    @builtins.property
    def log_group_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_type#log_group_name CloudformationType#log_group_name}.'''
        result = self._values.get("log_group_name")
        assert result is not None, "Required property 'log_group_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def log_role_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudformation_type#log_role_arn CloudformationType#log_role_arn}.'''
        result = self._values.get("log_role_arn")
        assert result is not None, "Required property 'log_role_arn' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudformationTypeLoggingConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudformationTypeLoggingConfigOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudformation.CloudformationTypeLoggingConfigOutputReference",
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
    @jsii.member(jsii_name="logGroupNameInput")
    def log_group_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "logGroupNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logRoleArnInput")
    def log_role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "logRoleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logGroupName")
    def log_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "logGroupName"))

    @log_group_name.setter
    def log_group_name(self, value: builtins.str) -> None:
        jsii.set(self, "logGroupName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logRoleArn")
    def log_role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "logRoleArn"))

    @log_role_arn.setter
    def log_role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "logRoleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[CloudformationTypeLoggingConfig]:
        return typing.cast(typing.Optional[CloudformationTypeLoggingConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CloudformationTypeLoggingConfig],
    ) -> None:
        jsii.set(self, "internalValue", value)


class DataAwsCloudformationExport(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudformation.DataAwsCloudformationExport",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/cloudformation_export aws_cloudformation_export}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/cloudformation_export aws_cloudformation_export} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudformation_export#name DataAwsCloudformationExport#name}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsCloudformationExportConfig(
            name=name,
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
    @jsii.member(jsii_name="exportingStackId")
    def exporting_stack_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "exportingStackId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudformation.DataAwsCloudformationExportConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
    },
)
class DataAwsCloudformationExportConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
    ) -> None:
        '''AWS CloudFormation.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudformation_export#name DataAwsCloudformationExport#name}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
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
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudformation_export#name DataAwsCloudformationExport#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsCloudformationExportConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsCloudformationStack(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudformation.DataAwsCloudformationStack",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/cloudformation_stack aws_cloudformation_stack}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/cloudformation_stack aws_cloudformation_stack} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudformation_stack#name DataAwsCloudformationStack#name}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudformation_stack#tags DataAwsCloudformationStack#tags}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsCloudformationStackConfig(
            name=name,
            tags=tags,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="outputs")
    def outputs(self, key: builtins.str) -> builtins.str:
        '''
        :param key: -
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "outputs", [key]))

    @jsii.member(jsii_name="parameters")
    def parameters(self, key: builtins.str) -> builtins.str:
        '''
        :param key: -
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "parameters", [key]))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="capabilities")
    def capabilities(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "capabilities"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="disableRollback")
    def disable_rollback(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "disableRollback"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="iamRoleArn")
    def iam_role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "iamRoleArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="notificationArns")
    def notification_arns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "notificationArns"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="templateBody")
    def template_body(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "templateBody"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutInMinutes")
    def timeout_in_minutes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "timeoutInMinutes"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsInput"))

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


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudformation.DataAwsCloudformationStackConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "tags": "tags",
    },
)
class DataAwsCloudformationStackConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS CloudFormation.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudformation_stack#name DataAwsCloudformationStack#name}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudformation_stack#tags DataAwsCloudformationStack#tags}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
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
        if tags is not None:
            self._values["tags"] = tags

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
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudformation_stack#name DataAwsCloudformationStack#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudformation_stack#tags DataAwsCloudformationStack#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsCloudformationStackConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsCloudformationType(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudformation.DataAwsCloudformationType",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/cloudformation_type aws_cloudformation_type}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        type: typing.Optional[builtins.str] = None,
        type_name: typing.Optional[builtins.str] = None,
        version_id: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/cloudformation_type aws_cloudformation_type} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudformation_type#type DataAwsCloudformationType#type}.
        :param type_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudformation_type#type_name DataAwsCloudformationType#type_name}.
        :param version_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudformation_type#version_id DataAwsCloudformationType#version_id}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsCloudformationTypeConfig(
            type=type,
            type_name=type_name,
            version_id=version_id,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="loggingConfig")
    def logging_config(
        self,
        index: builtins.str,
    ) -> "DataAwsCloudformationTypeLoggingConfig":
        '''
        :param index: -
        '''
        return typing.cast("DataAwsCloudformationTypeLoggingConfig", jsii.invoke(self, "loggingConfig", [index]))

    @jsii.member(jsii_name="resetType")
    def reset_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetType", []))

    @jsii.member(jsii_name="resetTypeName")
    def reset_type_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTypeName", []))

    @jsii.member(jsii_name="resetVersionId")
    def reset_version_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVersionId", []))

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
    @jsii.member(jsii_name="defaultVersionId")
    def default_version_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "defaultVersionId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deprecatedStatus")
    def deprecated_status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deprecatedStatus"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="documentationUrl")
    def documentation_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "documentationUrl"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="executionRoleArn")
    def execution_role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "executionRoleArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="isDefaultVersion")
    def is_default_version(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "isDefaultVersion"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="provisioningType")
    def provisioning_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "provisioningType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="schema")
    def schema(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "schema"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceUrl")
    def source_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceUrl"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="typeArn")
    def type_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "typeArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="visibility")
    def visibility(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "visibility"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="typeNameInput")
    def type_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="versionIdInput")
    def version_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "versionIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        jsii.set(self, "type", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="typeName")
    def type_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "typeName"))

    @type_name.setter
    def type_name(self, value: builtins.str) -> None:
        jsii.set(self, "typeName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="versionId")
    def version_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "versionId"))

    @version_id.setter
    def version_id(self, value: builtins.str) -> None:
        jsii.set(self, "versionId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudformation.DataAwsCloudformationTypeConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "type": "type",
        "type_name": "typeName",
        "version_id": "versionId",
    },
)
class DataAwsCloudformationTypeConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        type: typing.Optional[builtins.str] = None,
        type_name: typing.Optional[builtins.str] = None,
        version_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS CloudFormation.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudformation_type#type DataAwsCloudformationType#type}.
        :param type_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudformation_type#type_name DataAwsCloudformationType#type_name}.
        :param version_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudformation_type#version_id DataAwsCloudformationType#version_id}.
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
        if type is not None:
            self._values["type"] = type
        if type_name is not None:
            self._values["type_name"] = type_name
        if version_id is not None:
            self._values["version_id"] = version_id

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
    def type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudformation_type#type DataAwsCloudformationType#type}.'''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudformation_type#type_name DataAwsCloudformationType#type_name}.'''
        result = self._values.get("type_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def version_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudformation_type#version_id DataAwsCloudformationType#version_id}.'''
        result = self._values.get("version_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsCloudformationTypeConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsCloudformationTypeLoggingConfig(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudformation.DataAwsCloudformationTypeLoggingConfig",
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
    @jsii.member(jsii_name="logGroupName")
    def log_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "logGroupName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logRoleArn")
    def log_role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "logRoleArn"))


__all__ = [
    "CloudformationStack",
    "CloudformationStackConfig",
    "CloudformationStackSet",
    "CloudformationStackSetAutoDeployment",
    "CloudformationStackSetAutoDeploymentOutputReference",
    "CloudformationStackSetConfig",
    "CloudformationStackSetInstance",
    "CloudformationStackSetInstanceConfig",
    "CloudformationStackSetInstanceDeploymentTargets",
    "CloudformationStackSetInstanceDeploymentTargetsOutputReference",
    "CloudformationStackSetInstanceTimeouts",
    "CloudformationStackSetInstanceTimeoutsOutputReference",
    "CloudformationStackSetTimeouts",
    "CloudformationStackSetTimeoutsOutputReference",
    "CloudformationStackTimeouts",
    "CloudformationStackTimeoutsOutputReference",
    "CloudformationType",
    "CloudformationTypeConfig",
    "CloudformationTypeLoggingConfig",
    "CloudformationTypeLoggingConfigOutputReference",
    "DataAwsCloudformationExport",
    "DataAwsCloudformationExportConfig",
    "DataAwsCloudformationStack",
    "DataAwsCloudformationStackConfig",
    "DataAwsCloudformationType",
    "DataAwsCloudformationTypeConfig",
    "DataAwsCloudformationTypeLoggingConfig",
]

publication.publish()
