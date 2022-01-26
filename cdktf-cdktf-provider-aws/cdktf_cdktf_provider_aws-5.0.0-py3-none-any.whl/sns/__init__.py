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


class DataAwsSnsTopic(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.sns.DataAwsSnsTopic",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/sns_topic aws_sns_topic}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/sns_topic aws_sns_topic} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/sns_topic#name DataAwsSnsTopic#name}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsSnsTopicConfig(
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
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

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
    jsii_type="@cdktf/provider-aws.sns.DataAwsSnsTopicConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
    },
)
class DataAwsSnsTopicConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
    ) -> None:
        '''AWS Simple Notification Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/sns_topic#name DataAwsSnsTopic#name}.
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
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/sns_topic#name DataAwsSnsTopic#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsSnsTopicConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SnsPlatformApplication(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.sns.SnsPlatformApplication",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/sns_platform_application aws_sns_platform_application}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        platform: builtins.str,
        platform_credential: builtins.str,
        event_delivery_failure_topic_arn: typing.Optional[builtins.str] = None,
        event_endpoint_created_topic_arn: typing.Optional[builtins.str] = None,
        event_endpoint_deleted_topic_arn: typing.Optional[builtins.str] = None,
        event_endpoint_updated_topic_arn: typing.Optional[builtins.str] = None,
        failure_feedback_role_arn: typing.Optional[builtins.str] = None,
        platform_principal: typing.Optional[builtins.str] = None,
        success_feedback_role_arn: typing.Optional[builtins.str] = None,
        success_feedback_sample_rate: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/sns_platform_application aws_sns_platform_application} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_platform_application#name SnsPlatformApplication#name}.
        :param platform: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_platform_application#platform SnsPlatformApplication#platform}.
        :param platform_credential: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_platform_application#platform_credential SnsPlatformApplication#platform_credential}.
        :param event_delivery_failure_topic_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_platform_application#event_delivery_failure_topic_arn SnsPlatformApplication#event_delivery_failure_topic_arn}.
        :param event_endpoint_created_topic_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_platform_application#event_endpoint_created_topic_arn SnsPlatformApplication#event_endpoint_created_topic_arn}.
        :param event_endpoint_deleted_topic_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_platform_application#event_endpoint_deleted_topic_arn SnsPlatformApplication#event_endpoint_deleted_topic_arn}.
        :param event_endpoint_updated_topic_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_platform_application#event_endpoint_updated_topic_arn SnsPlatformApplication#event_endpoint_updated_topic_arn}.
        :param failure_feedback_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_platform_application#failure_feedback_role_arn SnsPlatformApplication#failure_feedback_role_arn}.
        :param platform_principal: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_platform_application#platform_principal SnsPlatformApplication#platform_principal}.
        :param success_feedback_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_platform_application#success_feedback_role_arn SnsPlatformApplication#success_feedback_role_arn}.
        :param success_feedback_sample_rate: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_platform_application#success_feedback_sample_rate SnsPlatformApplication#success_feedback_sample_rate}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = SnsPlatformApplicationConfig(
            name=name,
            platform=platform,
            platform_credential=platform_credential,
            event_delivery_failure_topic_arn=event_delivery_failure_topic_arn,
            event_endpoint_created_topic_arn=event_endpoint_created_topic_arn,
            event_endpoint_deleted_topic_arn=event_endpoint_deleted_topic_arn,
            event_endpoint_updated_topic_arn=event_endpoint_updated_topic_arn,
            failure_feedback_role_arn=failure_feedback_role_arn,
            platform_principal=platform_principal,
            success_feedback_role_arn=success_feedback_role_arn,
            success_feedback_sample_rate=success_feedback_sample_rate,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetEventDeliveryFailureTopicArn")
    def reset_event_delivery_failure_topic_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEventDeliveryFailureTopicArn", []))

    @jsii.member(jsii_name="resetEventEndpointCreatedTopicArn")
    def reset_event_endpoint_created_topic_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEventEndpointCreatedTopicArn", []))

    @jsii.member(jsii_name="resetEventEndpointDeletedTopicArn")
    def reset_event_endpoint_deleted_topic_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEventEndpointDeletedTopicArn", []))

    @jsii.member(jsii_name="resetEventEndpointUpdatedTopicArn")
    def reset_event_endpoint_updated_topic_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEventEndpointUpdatedTopicArn", []))

    @jsii.member(jsii_name="resetFailureFeedbackRoleArn")
    def reset_failure_feedback_role_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFailureFeedbackRoleArn", []))

    @jsii.member(jsii_name="resetPlatformPrincipal")
    def reset_platform_principal(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPlatformPrincipal", []))

    @jsii.member(jsii_name="resetSuccessFeedbackRoleArn")
    def reset_success_feedback_role_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSuccessFeedbackRoleArn", []))

    @jsii.member(jsii_name="resetSuccessFeedbackSampleRate")
    def reset_success_feedback_sample_rate(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSuccessFeedbackSampleRate", []))

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
    @jsii.member(jsii_name="eventDeliveryFailureTopicArnInput")
    def event_delivery_failure_topic_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "eventDeliveryFailureTopicArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="eventEndpointCreatedTopicArnInput")
    def event_endpoint_created_topic_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "eventEndpointCreatedTopicArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="eventEndpointDeletedTopicArnInput")
    def event_endpoint_deleted_topic_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "eventEndpointDeletedTopicArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="eventEndpointUpdatedTopicArnInput")
    def event_endpoint_updated_topic_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "eventEndpointUpdatedTopicArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="failureFeedbackRoleArnInput")
    def failure_feedback_role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "failureFeedbackRoleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="platformCredentialInput")
    def platform_credential_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "platformCredentialInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="platformInput")
    def platform_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "platformInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="platformPrincipalInput")
    def platform_principal_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "platformPrincipalInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="successFeedbackRoleArnInput")
    def success_feedback_role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "successFeedbackRoleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="successFeedbackSampleRateInput")
    def success_feedback_sample_rate_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "successFeedbackSampleRateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="eventDeliveryFailureTopicArn")
    def event_delivery_failure_topic_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "eventDeliveryFailureTopicArn"))

    @event_delivery_failure_topic_arn.setter
    def event_delivery_failure_topic_arn(self, value: builtins.str) -> None:
        jsii.set(self, "eventDeliveryFailureTopicArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="eventEndpointCreatedTopicArn")
    def event_endpoint_created_topic_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "eventEndpointCreatedTopicArn"))

    @event_endpoint_created_topic_arn.setter
    def event_endpoint_created_topic_arn(self, value: builtins.str) -> None:
        jsii.set(self, "eventEndpointCreatedTopicArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="eventEndpointDeletedTopicArn")
    def event_endpoint_deleted_topic_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "eventEndpointDeletedTopicArn"))

    @event_endpoint_deleted_topic_arn.setter
    def event_endpoint_deleted_topic_arn(self, value: builtins.str) -> None:
        jsii.set(self, "eventEndpointDeletedTopicArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="eventEndpointUpdatedTopicArn")
    def event_endpoint_updated_topic_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "eventEndpointUpdatedTopicArn"))

    @event_endpoint_updated_topic_arn.setter
    def event_endpoint_updated_topic_arn(self, value: builtins.str) -> None:
        jsii.set(self, "eventEndpointUpdatedTopicArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="failureFeedbackRoleArn")
    def failure_feedback_role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "failureFeedbackRoleArn"))

    @failure_feedback_role_arn.setter
    def failure_feedback_role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "failureFeedbackRoleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="platform")
    def platform(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "platform"))

    @platform.setter
    def platform(self, value: builtins.str) -> None:
        jsii.set(self, "platform", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="platformCredential")
    def platform_credential(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "platformCredential"))

    @platform_credential.setter
    def platform_credential(self, value: builtins.str) -> None:
        jsii.set(self, "platformCredential", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="platformPrincipal")
    def platform_principal(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "platformPrincipal"))

    @platform_principal.setter
    def platform_principal(self, value: builtins.str) -> None:
        jsii.set(self, "platformPrincipal", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="successFeedbackRoleArn")
    def success_feedback_role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "successFeedbackRoleArn"))

    @success_feedback_role_arn.setter
    def success_feedback_role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "successFeedbackRoleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="successFeedbackSampleRate")
    def success_feedback_sample_rate(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "successFeedbackSampleRate"))

    @success_feedback_sample_rate.setter
    def success_feedback_sample_rate(self, value: builtins.str) -> None:
        jsii.set(self, "successFeedbackSampleRate", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.sns.SnsPlatformApplicationConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "platform": "platform",
        "platform_credential": "platformCredential",
        "event_delivery_failure_topic_arn": "eventDeliveryFailureTopicArn",
        "event_endpoint_created_topic_arn": "eventEndpointCreatedTopicArn",
        "event_endpoint_deleted_topic_arn": "eventEndpointDeletedTopicArn",
        "event_endpoint_updated_topic_arn": "eventEndpointUpdatedTopicArn",
        "failure_feedback_role_arn": "failureFeedbackRoleArn",
        "platform_principal": "platformPrincipal",
        "success_feedback_role_arn": "successFeedbackRoleArn",
        "success_feedback_sample_rate": "successFeedbackSampleRate",
    },
)
class SnsPlatformApplicationConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        platform: builtins.str,
        platform_credential: builtins.str,
        event_delivery_failure_topic_arn: typing.Optional[builtins.str] = None,
        event_endpoint_created_topic_arn: typing.Optional[builtins.str] = None,
        event_endpoint_deleted_topic_arn: typing.Optional[builtins.str] = None,
        event_endpoint_updated_topic_arn: typing.Optional[builtins.str] = None,
        failure_feedback_role_arn: typing.Optional[builtins.str] = None,
        platform_principal: typing.Optional[builtins.str] = None,
        success_feedback_role_arn: typing.Optional[builtins.str] = None,
        success_feedback_sample_rate: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Simple Notification Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_platform_application#name SnsPlatformApplication#name}.
        :param platform: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_platform_application#platform SnsPlatformApplication#platform}.
        :param platform_credential: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_platform_application#platform_credential SnsPlatformApplication#platform_credential}.
        :param event_delivery_failure_topic_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_platform_application#event_delivery_failure_topic_arn SnsPlatformApplication#event_delivery_failure_topic_arn}.
        :param event_endpoint_created_topic_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_platform_application#event_endpoint_created_topic_arn SnsPlatformApplication#event_endpoint_created_topic_arn}.
        :param event_endpoint_deleted_topic_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_platform_application#event_endpoint_deleted_topic_arn SnsPlatformApplication#event_endpoint_deleted_topic_arn}.
        :param event_endpoint_updated_topic_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_platform_application#event_endpoint_updated_topic_arn SnsPlatformApplication#event_endpoint_updated_topic_arn}.
        :param failure_feedback_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_platform_application#failure_feedback_role_arn SnsPlatformApplication#failure_feedback_role_arn}.
        :param platform_principal: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_platform_application#platform_principal SnsPlatformApplication#platform_principal}.
        :param success_feedback_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_platform_application#success_feedback_role_arn SnsPlatformApplication#success_feedback_role_arn}.
        :param success_feedback_sample_rate: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_platform_application#success_feedback_sample_rate SnsPlatformApplication#success_feedback_sample_rate}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "platform": platform,
            "platform_credential": platform_credential,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if event_delivery_failure_topic_arn is not None:
            self._values["event_delivery_failure_topic_arn"] = event_delivery_failure_topic_arn
        if event_endpoint_created_topic_arn is not None:
            self._values["event_endpoint_created_topic_arn"] = event_endpoint_created_topic_arn
        if event_endpoint_deleted_topic_arn is not None:
            self._values["event_endpoint_deleted_topic_arn"] = event_endpoint_deleted_topic_arn
        if event_endpoint_updated_topic_arn is not None:
            self._values["event_endpoint_updated_topic_arn"] = event_endpoint_updated_topic_arn
        if failure_feedback_role_arn is not None:
            self._values["failure_feedback_role_arn"] = failure_feedback_role_arn
        if platform_principal is not None:
            self._values["platform_principal"] = platform_principal
        if success_feedback_role_arn is not None:
            self._values["success_feedback_role_arn"] = success_feedback_role_arn
        if success_feedback_sample_rate is not None:
            self._values["success_feedback_sample_rate"] = success_feedback_sample_rate

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_platform_application#name SnsPlatformApplication#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def platform(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_platform_application#platform SnsPlatformApplication#platform}.'''
        result = self._values.get("platform")
        assert result is not None, "Required property 'platform' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def platform_credential(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_platform_application#platform_credential SnsPlatformApplication#platform_credential}.'''
        result = self._values.get("platform_credential")
        assert result is not None, "Required property 'platform_credential' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def event_delivery_failure_topic_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_platform_application#event_delivery_failure_topic_arn SnsPlatformApplication#event_delivery_failure_topic_arn}.'''
        result = self._values.get("event_delivery_failure_topic_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def event_endpoint_created_topic_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_platform_application#event_endpoint_created_topic_arn SnsPlatformApplication#event_endpoint_created_topic_arn}.'''
        result = self._values.get("event_endpoint_created_topic_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def event_endpoint_deleted_topic_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_platform_application#event_endpoint_deleted_topic_arn SnsPlatformApplication#event_endpoint_deleted_topic_arn}.'''
        result = self._values.get("event_endpoint_deleted_topic_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def event_endpoint_updated_topic_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_platform_application#event_endpoint_updated_topic_arn SnsPlatformApplication#event_endpoint_updated_topic_arn}.'''
        result = self._values.get("event_endpoint_updated_topic_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def failure_feedback_role_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_platform_application#failure_feedback_role_arn SnsPlatformApplication#failure_feedback_role_arn}.'''
        result = self._values.get("failure_feedback_role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def platform_principal(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_platform_application#platform_principal SnsPlatformApplication#platform_principal}.'''
        result = self._values.get("platform_principal")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def success_feedback_role_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_platform_application#success_feedback_role_arn SnsPlatformApplication#success_feedback_role_arn}.'''
        result = self._values.get("success_feedback_role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def success_feedback_sample_rate(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_platform_application#success_feedback_sample_rate SnsPlatformApplication#success_feedback_sample_rate}.'''
        result = self._values.get("success_feedback_sample_rate")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SnsPlatformApplicationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SnsSmsPreferences(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.sns.SnsSmsPreferences",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/sns_sms_preferences aws_sns_sms_preferences}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        default_sender_id: typing.Optional[builtins.str] = None,
        default_sms_type: typing.Optional[builtins.str] = None,
        delivery_status_iam_role_arn: typing.Optional[builtins.str] = None,
        delivery_status_success_sampling_rate: typing.Optional[builtins.str] = None,
        monthly_spend_limit: typing.Optional[jsii.Number] = None,
        usage_report_s3_bucket: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/sns_sms_preferences aws_sns_sms_preferences} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param default_sender_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_sms_preferences#default_sender_id SnsSmsPreferences#default_sender_id}.
        :param default_sms_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_sms_preferences#default_sms_type SnsSmsPreferences#default_sms_type}.
        :param delivery_status_iam_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_sms_preferences#delivery_status_iam_role_arn SnsSmsPreferences#delivery_status_iam_role_arn}.
        :param delivery_status_success_sampling_rate: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_sms_preferences#delivery_status_success_sampling_rate SnsSmsPreferences#delivery_status_success_sampling_rate}.
        :param monthly_spend_limit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_sms_preferences#monthly_spend_limit SnsSmsPreferences#monthly_spend_limit}.
        :param usage_report_s3_bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_sms_preferences#usage_report_s3_bucket SnsSmsPreferences#usage_report_s3_bucket}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = SnsSmsPreferencesConfig(
            default_sender_id=default_sender_id,
            default_sms_type=default_sms_type,
            delivery_status_iam_role_arn=delivery_status_iam_role_arn,
            delivery_status_success_sampling_rate=delivery_status_success_sampling_rate,
            monthly_spend_limit=monthly_spend_limit,
            usage_report_s3_bucket=usage_report_s3_bucket,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetDefaultSenderId")
    def reset_default_sender_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefaultSenderId", []))

    @jsii.member(jsii_name="resetDefaultSmsType")
    def reset_default_sms_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefaultSmsType", []))

    @jsii.member(jsii_name="resetDeliveryStatusIamRoleArn")
    def reset_delivery_status_iam_role_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeliveryStatusIamRoleArn", []))

    @jsii.member(jsii_name="resetDeliveryStatusSuccessSamplingRate")
    def reset_delivery_status_success_sampling_rate(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeliveryStatusSuccessSamplingRate", []))

    @jsii.member(jsii_name="resetMonthlySpendLimit")
    def reset_monthly_spend_limit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMonthlySpendLimit", []))

    @jsii.member(jsii_name="resetUsageReportS3Bucket")
    def reset_usage_report_s3_bucket(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsageReportS3Bucket", []))

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
    @jsii.member(jsii_name="defaultSenderIdInput")
    def default_sender_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "defaultSenderIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultSmsTypeInput")
    def default_sms_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "defaultSmsTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deliveryStatusIamRoleArnInput")
    def delivery_status_iam_role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deliveryStatusIamRoleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deliveryStatusSuccessSamplingRateInput")
    def delivery_status_success_sampling_rate_input(
        self,
    ) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deliveryStatusSuccessSamplingRateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="monthlySpendLimitInput")
    def monthly_spend_limit_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "monthlySpendLimitInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="usageReportS3BucketInput")
    def usage_report_s3_bucket_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usageReportS3BucketInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultSenderId")
    def default_sender_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "defaultSenderId"))

    @default_sender_id.setter
    def default_sender_id(self, value: builtins.str) -> None:
        jsii.set(self, "defaultSenderId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultSmsType")
    def default_sms_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "defaultSmsType"))

    @default_sms_type.setter
    def default_sms_type(self, value: builtins.str) -> None:
        jsii.set(self, "defaultSmsType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deliveryStatusIamRoleArn")
    def delivery_status_iam_role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deliveryStatusIamRoleArn"))

    @delivery_status_iam_role_arn.setter
    def delivery_status_iam_role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "deliveryStatusIamRoleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deliveryStatusSuccessSamplingRate")
    def delivery_status_success_sampling_rate(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deliveryStatusSuccessSamplingRate"))

    @delivery_status_success_sampling_rate.setter
    def delivery_status_success_sampling_rate(self, value: builtins.str) -> None:
        jsii.set(self, "deliveryStatusSuccessSamplingRate", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="monthlySpendLimit")
    def monthly_spend_limit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "monthlySpendLimit"))

    @monthly_spend_limit.setter
    def monthly_spend_limit(self, value: jsii.Number) -> None:
        jsii.set(self, "monthlySpendLimit", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="usageReportS3Bucket")
    def usage_report_s3_bucket(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "usageReportS3Bucket"))

    @usage_report_s3_bucket.setter
    def usage_report_s3_bucket(self, value: builtins.str) -> None:
        jsii.set(self, "usageReportS3Bucket", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.sns.SnsSmsPreferencesConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "default_sender_id": "defaultSenderId",
        "default_sms_type": "defaultSmsType",
        "delivery_status_iam_role_arn": "deliveryStatusIamRoleArn",
        "delivery_status_success_sampling_rate": "deliveryStatusSuccessSamplingRate",
        "monthly_spend_limit": "monthlySpendLimit",
        "usage_report_s3_bucket": "usageReportS3Bucket",
    },
)
class SnsSmsPreferencesConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        default_sender_id: typing.Optional[builtins.str] = None,
        default_sms_type: typing.Optional[builtins.str] = None,
        delivery_status_iam_role_arn: typing.Optional[builtins.str] = None,
        delivery_status_success_sampling_rate: typing.Optional[builtins.str] = None,
        monthly_spend_limit: typing.Optional[jsii.Number] = None,
        usage_report_s3_bucket: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Simple Notification Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param default_sender_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_sms_preferences#default_sender_id SnsSmsPreferences#default_sender_id}.
        :param default_sms_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_sms_preferences#default_sms_type SnsSmsPreferences#default_sms_type}.
        :param delivery_status_iam_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_sms_preferences#delivery_status_iam_role_arn SnsSmsPreferences#delivery_status_iam_role_arn}.
        :param delivery_status_success_sampling_rate: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_sms_preferences#delivery_status_success_sampling_rate SnsSmsPreferences#delivery_status_success_sampling_rate}.
        :param monthly_spend_limit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_sms_preferences#monthly_spend_limit SnsSmsPreferences#monthly_spend_limit}.
        :param usage_report_s3_bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_sms_preferences#usage_report_s3_bucket SnsSmsPreferences#usage_report_s3_bucket}.
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
        if default_sender_id is not None:
            self._values["default_sender_id"] = default_sender_id
        if default_sms_type is not None:
            self._values["default_sms_type"] = default_sms_type
        if delivery_status_iam_role_arn is not None:
            self._values["delivery_status_iam_role_arn"] = delivery_status_iam_role_arn
        if delivery_status_success_sampling_rate is not None:
            self._values["delivery_status_success_sampling_rate"] = delivery_status_success_sampling_rate
        if monthly_spend_limit is not None:
            self._values["monthly_spend_limit"] = monthly_spend_limit
        if usage_report_s3_bucket is not None:
            self._values["usage_report_s3_bucket"] = usage_report_s3_bucket

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

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
    def default_sender_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_sms_preferences#default_sender_id SnsSmsPreferences#default_sender_id}.'''
        result = self._values.get("default_sender_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def default_sms_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_sms_preferences#default_sms_type SnsSmsPreferences#default_sms_type}.'''
        result = self._values.get("default_sms_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delivery_status_iam_role_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_sms_preferences#delivery_status_iam_role_arn SnsSmsPreferences#delivery_status_iam_role_arn}.'''
        result = self._values.get("delivery_status_iam_role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delivery_status_success_sampling_rate(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_sms_preferences#delivery_status_success_sampling_rate SnsSmsPreferences#delivery_status_success_sampling_rate}.'''
        result = self._values.get("delivery_status_success_sampling_rate")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def monthly_spend_limit(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_sms_preferences#monthly_spend_limit SnsSmsPreferences#monthly_spend_limit}.'''
        result = self._values.get("monthly_spend_limit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def usage_report_s3_bucket(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_sms_preferences#usage_report_s3_bucket SnsSmsPreferences#usage_report_s3_bucket}.'''
        result = self._values.get("usage_report_s3_bucket")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SnsSmsPreferencesConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SnsTopic(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.sns.SnsTopic",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/sns_topic aws_sns_topic}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        application_failure_feedback_role_arn: typing.Optional[builtins.str] = None,
        application_success_feedback_role_arn: typing.Optional[builtins.str] = None,
        application_success_feedback_sample_rate: typing.Optional[jsii.Number] = None,
        content_based_deduplication: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        delivery_policy: typing.Optional[builtins.str] = None,
        display_name: typing.Optional[builtins.str] = None,
        fifo_topic: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        firehose_failure_feedback_role_arn: typing.Optional[builtins.str] = None,
        firehose_success_feedback_role_arn: typing.Optional[builtins.str] = None,
        firehose_success_feedback_sample_rate: typing.Optional[jsii.Number] = None,
        http_failure_feedback_role_arn: typing.Optional[builtins.str] = None,
        http_success_feedback_role_arn: typing.Optional[builtins.str] = None,
        http_success_feedback_sample_rate: typing.Optional[jsii.Number] = None,
        kms_master_key_id: typing.Optional[builtins.str] = None,
        lambda_failure_feedback_role_arn: typing.Optional[builtins.str] = None,
        lambda_success_feedback_role_arn: typing.Optional[builtins.str] = None,
        lambda_success_feedback_sample_rate: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        name_prefix: typing.Optional[builtins.str] = None,
        policy: typing.Optional[builtins.str] = None,
        sqs_failure_feedback_role_arn: typing.Optional[builtins.str] = None,
        sqs_success_feedback_role_arn: typing.Optional[builtins.str] = None,
        sqs_success_feedback_sample_rate: typing.Optional[jsii.Number] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/sns_topic aws_sns_topic} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param application_failure_feedback_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#application_failure_feedback_role_arn SnsTopic#application_failure_feedback_role_arn}.
        :param application_success_feedback_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#application_success_feedback_role_arn SnsTopic#application_success_feedback_role_arn}.
        :param application_success_feedback_sample_rate: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#application_success_feedback_sample_rate SnsTopic#application_success_feedback_sample_rate}.
        :param content_based_deduplication: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#content_based_deduplication SnsTopic#content_based_deduplication}.
        :param delivery_policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#delivery_policy SnsTopic#delivery_policy}.
        :param display_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#display_name SnsTopic#display_name}.
        :param fifo_topic: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#fifo_topic SnsTopic#fifo_topic}.
        :param firehose_failure_feedback_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#firehose_failure_feedback_role_arn SnsTopic#firehose_failure_feedback_role_arn}.
        :param firehose_success_feedback_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#firehose_success_feedback_role_arn SnsTopic#firehose_success_feedback_role_arn}.
        :param firehose_success_feedback_sample_rate: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#firehose_success_feedback_sample_rate SnsTopic#firehose_success_feedback_sample_rate}.
        :param http_failure_feedback_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#http_failure_feedback_role_arn SnsTopic#http_failure_feedback_role_arn}.
        :param http_success_feedback_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#http_success_feedback_role_arn SnsTopic#http_success_feedback_role_arn}.
        :param http_success_feedback_sample_rate: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#http_success_feedback_sample_rate SnsTopic#http_success_feedback_sample_rate}.
        :param kms_master_key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#kms_master_key_id SnsTopic#kms_master_key_id}.
        :param lambda_failure_feedback_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#lambda_failure_feedback_role_arn SnsTopic#lambda_failure_feedback_role_arn}.
        :param lambda_success_feedback_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#lambda_success_feedback_role_arn SnsTopic#lambda_success_feedback_role_arn}.
        :param lambda_success_feedback_sample_rate: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#lambda_success_feedback_sample_rate SnsTopic#lambda_success_feedback_sample_rate}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#name SnsTopic#name}.
        :param name_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#name_prefix SnsTopic#name_prefix}.
        :param policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#policy SnsTopic#policy}.
        :param sqs_failure_feedback_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#sqs_failure_feedback_role_arn SnsTopic#sqs_failure_feedback_role_arn}.
        :param sqs_success_feedback_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#sqs_success_feedback_role_arn SnsTopic#sqs_success_feedback_role_arn}.
        :param sqs_success_feedback_sample_rate: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#sqs_success_feedback_sample_rate SnsTopic#sqs_success_feedback_sample_rate}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#tags SnsTopic#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#tags_all SnsTopic#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = SnsTopicConfig(
            application_failure_feedback_role_arn=application_failure_feedback_role_arn,
            application_success_feedback_role_arn=application_success_feedback_role_arn,
            application_success_feedback_sample_rate=application_success_feedback_sample_rate,
            content_based_deduplication=content_based_deduplication,
            delivery_policy=delivery_policy,
            display_name=display_name,
            fifo_topic=fifo_topic,
            firehose_failure_feedback_role_arn=firehose_failure_feedback_role_arn,
            firehose_success_feedback_role_arn=firehose_success_feedback_role_arn,
            firehose_success_feedback_sample_rate=firehose_success_feedback_sample_rate,
            http_failure_feedback_role_arn=http_failure_feedback_role_arn,
            http_success_feedback_role_arn=http_success_feedback_role_arn,
            http_success_feedback_sample_rate=http_success_feedback_sample_rate,
            kms_master_key_id=kms_master_key_id,
            lambda_failure_feedback_role_arn=lambda_failure_feedback_role_arn,
            lambda_success_feedback_role_arn=lambda_success_feedback_role_arn,
            lambda_success_feedback_sample_rate=lambda_success_feedback_sample_rate,
            name=name,
            name_prefix=name_prefix,
            policy=policy,
            sqs_failure_feedback_role_arn=sqs_failure_feedback_role_arn,
            sqs_success_feedback_role_arn=sqs_success_feedback_role_arn,
            sqs_success_feedback_sample_rate=sqs_success_feedback_sample_rate,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetApplicationFailureFeedbackRoleArn")
    def reset_application_failure_feedback_role_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetApplicationFailureFeedbackRoleArn", []))

    @jsii.member(jsii_name="resetApplicationSuccessFeedbackRoleArn")
    def reset_application_success_feedback_role_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetApplicationSuccessFeedbackRoleArn", []))

    @jsii.member(jsii_name="resetApplicationSuccessFeedbackSampleRate")
    def reset_application_success_feedback_sample_rate(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetApplicationSuccessFeedbackSampleRate", []))

    @jsii.member(jsii_name="resetContentBasedDeduplication")
    def reset_content_based_deduplication(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetContentBasedDeduplication", []))

    @jsii.member(jsii_name="resetDeliveryPolicy")
    def reset_delivery_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeliveryPolicy", []))

    @jsii.member(jsii_name="resetDisplayName")
    def reset_display_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDisplayName", []))

    @jsii.member(jsii_name="resetFifoTopic")
    def reset_fifo_topic(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFifoTopic", []))

    @jsii.member(jsii_name="resetFirehoseFailureFeedbackRoleArn")
    def reset_firehose_failure_feedback_role_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFirehoseFailureFeedbackRoleArn", []))

    @jsii.member(jsii_name="resetFirehoseSuccessFeedbackRoleArn")
    def reset_firehose_success_feedback_role_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFirehoseSuccessFeedbackRoleArn", []))

    @jsii.member(jsii_name="resetFirehoseSuccessFeedbackSampleRate")
    def reset_firehose_success_feedback_sample_rate(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFirehoseSuccessFeedbackSampleRate", []))

    @jsii.member(jsii_name="resetHttpFailureFeedbackRoleArn")
    def reset_http_failure_feedback_role_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHttpFailureFeedbackRoleArn", []))

    @jsii.member(jsii_name="resetHttpSuccessFeedbackRoleArn")
    def reset_http_success_feedback_role_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHttpSuccessFeedbackRoleArn", []))

    @jsii.member(jsii_name="resetHttpSuccessFeedbackSampleRate")
    def reset_http_success_feedback_sample_rate(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHttpSuccessFeedbackSampleRate", []))

    @jsii.member(jsii_name="resetKmsMasterKeyId")
    def reset_kms_master_key_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKmsMasterKeyId", []))

    @jsii.member(jsii_name="resetLambdaFailureFeedbackRoleArn")
    def reset_lambda_failure_feedback_role_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLambdaFailureFeedbackRoleArn", []))

    @jsii.member(jsii_name="resetLambdaSuccessFeedbackRoleArn")
    def reset_lambda_success_feedback_role_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLambdaSuccessFeedbackRoleArn", []))

    @jsii.member(jsii_name="resetLambdaSuccessFeedbackSampleRate")
    def reset_lambda_success_feedback_sample_rate(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLambdaSuccessFeedbackSampleRate", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetNamePrefix")
    def reset_name_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamePrefix", []))

    @jsii.member(jsii_name="resetPolicy")
    def reset_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPolicy", []))

    @jsii.member(jsii_name="resetSqsFailureFeedbackRoleArn")
    def reset_sqs_failure_feedback_role_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSqsFailureFeedbackRoleArn", []))

    @jsii.member(jsii_name="resetSqsSuccessFeedbackRoleArn")
    def reset_sqs_success_feedback_role_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSqsSuccessFeedbackRoleArn", []))

    @jsii.member(jsii_name="resetSqsSuccessFeedbackSampleRate")
    def reset_sqs_success_feedback_sample_rate(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSqsSuccessFeedbackSampleRate", []))

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
    @jsii.member(jsii_name="owner")
    def owner(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "owner"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="applicationFailureFeedbackRoleArnInput")
    def application_failure_feedback_role_arn_input(
        self,
    ) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "applicationFailureFeedbackRoleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="applicationSuccessFeedbackRoleArnInput")
    def application_success_feedback_role_arn_input(
        self,
    ) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "applicationSuccessFeedbackRoleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="applicationSuccessFeedbackSampleRateInput")
    def application_success_feedback_sample_rate_input(
        self,
    ) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "applicationSuccessFeedbackSampleRateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="contentBasedDeduplicationInput")
    def content_based_deduplication_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "contentBasedDeduplicationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deliveryPolicyInput")
    def delivery_policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deliveryPolicyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="displayNameInput")
    def display_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "displayNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fifoTopicInput")
    def fifo_topic_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "fifoTopicInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firehoseFailureFeedbackRoleArnInput")
    def firehose_failure_feedback_role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "firehoseFailureFeedbackRoleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firehoseSuccessFeedbackRoleArnInput")
    def firehose_success_feedback_role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "firehoseSuccessFeedbackRoleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firehoseSuccessFeedbackSampleRateInput")
    def firehose_success_feedback_sample_rate_input(
        self,
    ) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "firehoseSuccessFeedbackSampleRateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="httpFailureFeedbackRoleArnInput")
    def http_failure_feedback_role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "httpFailureFeedbackRoleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="httpSuccessFeedbackRoleArnInput")
    def http_success_feedback_role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "httpSuccessFeedbackRoleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="httpSuccessFeedbackSampleRateInput")
    def http_success_feedback_sample_rate_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "httpSuccessFeedbackSampleRateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsMasterKeyIdInput")
    def kms_master_key_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kmsMasterKeyIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambdaFailureFeedbackRoleArnInput")
    def lambda_failure_feedback_role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "lambdaFailureFeedbackRoleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambdaSuccessFeedbackRoleArnInput")
    def lambda_success_feedback_role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "lambdaSuccessFeedbackRoleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambdaSuccessFeedbackSampleRateInput")
    def lambda_success_feedback_sample_rate_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "lambdaSuccessFeedbackSampleRateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namePrefixInput")
    def name_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namePrefixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyInput")
    def policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "policyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sqsFailureFeedbackRoleArnInput")
    def sqs_failure_feedback_role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sqsFailureFeedbackRoleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sqsSuccessFeedbackRoleArnInput")
    def sqs_success_feedback_role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sqsSuccessFeedbackRoleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sqsSuccessFeedbackSampleRateInput")
    def sqs_success_feedback_sample_rate_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "sqsSuccessFeedbackSampleRateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAllInput")
    def tags_all_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsAllInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="applicationFailureFeedbackRoleArn")
    def application_failure_feedback_role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "applicationFailureFeedbackRoleArn"))

    @application_failure_feedback_role_arn.setter
    def application_failure_feedback_role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "applicationFailureFeedbackRoleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="applicationSuccessFeedbackRoleArn")
    def application_success_feedback_role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "applicationSuccessFeedbackRoleArn"))

    @application_success_feedback_role_arn.setter
    def application_success_feedback_role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "applicationSuccessFeedbackRoleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="applicationSuccessFeedbackSampleRate")
    def application_success_feedback_sample_rate(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "applicationSuccessFeedbackSampleRate"))

    @application_success_feedback_sample_rate.setter
    def application_success_feedback_sample_rate(self, value: jsii.Number) -> None:
        jsii.set(self, "applicationSuccessFeedbackSampleRate", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="contentBasedDeduplication")
    def content_based_deduplication(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "contentBasedDeduplication"))

    @content_based_deduplication.setter
    def content_based_deduplication(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "contentBasedDeduplication", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deliveryPolicy")
    def delivery_policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deliveryPolicy"))

    @delivery_policy.setter
    def delivery_policy(self, value: builtins.str) -> None:
        jsii.set(self, "deliveryPolicy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="displayName")
    def display_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "displayName"))

    @display_name.setter
    def display_name(self, value: builtins.str) -> None:
        jsii.set(self, "displayName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fifoTopic")
    def fifo_topic(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "fifoTopic"))

    @fifo_topic.setter
    def fifo_topic(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "fifoTopic", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firehoseFailureFeedbackRoleArn")
    def firehose_failure_feedback_role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "firehoseFailureFeedbackRoleArn"))

    @firehose_failure_feedback_role_arn.setter
    def firehose_failure_feedback_role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "firehoseFailureFeedbackRoleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firehoseSuccessFeedbackRoleArn")
    def firehose_success_feedback_role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "firehoseSuccessFeedbackRoleArn"))

    @firehose_success_feedback_role_arn.setter
    def firehose_success_feedback_role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "firehoseSuccessFeedbackRoleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firehoseSuccessFeedbackSampleRate")
    def firehose_success_feedback_sample_rate(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "firehoseSuccessFeedbackSampleRate"))

    @firehose_success_feedback_sample_rate.setter
    def firehose_success_feedback_sample_rate(self, value: jsii.Number) -> None:
        jsii.set(self, "firehoseSuccessFeedbackSampleRate", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="httpFailureFeedbackRoleArn")
    def http_failure_feedback_role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "httpFailureFeedbackRoleArn"))

    @http_failure_feedback_role_arn.setter
    def http_failure_feedback_role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "httpFailureFeedbackRoleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="httpSuccessFeedbackRoleArn")
    def http_success_feedback_role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "httpSuccessFeedbackRoleArn"))

    @http_success_feedback_role_arn.setter
    def http_success_feedback_role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "httpSuccessFeedbackRoleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="httpSuccessFeedbackSampleRate")
    def http_success_feedback_sample_rate(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "httpSuccessFeedbackSampleRate"))

    @http_success_feedback_sample_rate.setter
    def http_success_feedback_sample_rate(self, value: jsii.Number) -> None:
        jsii.set(self, "httpSuccessFeedbackSampleRate", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsMasterKeyId")
    def kms_master_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsMasterKeyId"))

    @kms_master_key_id.setter
    def kms_master_key_id(self, value: builtins.str) -> None:
        jsii.set(self, "kmsMasterKeyId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambdaFailureFeedbackRoleArn")
    def lambda_failure_feedback_role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lambdaFailureFeedbackRoleArn"))

    @lambda_failure_feedback_role_arn.setter
    def lambda_failure_feedback_role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "lambdaFailureFeedbackRoleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambdaSuccessFeedbackRoleArn")
    def lambda_success_feedback_role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lambdaSuccessFeedbackRoleArn"))

    @lambda_success_feedback_role_arn.setter
    def lambda_success_feedback_role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "lambdaSuccessFeedbackRoleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambdaSuccessFeedbackSampleRate")
    def lambda_success_feedback_sample_rate(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "lambdaSuccessFeedbackSampleRate"))

    @lambda_success_feedback_sample_rate.setter
    def lambda_success_feedback_sample_rate(self, value: jsii.Number) -> None:
        jsii.set(self, "lambdaSuccessFeedbackSampleRate", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namePrefix")
    def name_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namePrefix"))

    @name_prefix.setter
    def name_prefix(self, value: builtins.str) -> None:
        jsii.set(self, "namePrefix", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policy")
    def policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policy"))

    @policy.setter
    def policy(self, value: builtins.str) -> None:
        jsii.set(self, "policy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sqsFailureFeedbackRoleArn")
    def sqs_failure_feedback_role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sqsFailureFeedbackRoleArn"))

    @sqs_failure_feedback_role_arn.setter
    def sqs_failure_feedback_role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "sqsFailureFeedbackRoleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sqsSuccessFeedbackRoleArn")
    def sqs_success_feedback_role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sqsSuccessFeedbackRoleArn"))

    @sqs_success_feedback_role_arn.setter
    def sqs_success_feedback_role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "sqsSuccessFeedbackRoleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sqsSuccessFeedbackSampleRate")
    def sqs_success_feedback_sample_rate(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "sqsSuccessFeedbackSampleRate"))

    @sqs_success_feedback_sample_rate.setter
    def sqs_success_feedback_sample_rate(self, value: jsii.Number) -> None:
        jsii.set(self, "sqsSuccessFeedbackSampleRate", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        jsii.set(self, "tags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAll")
    def tags_all(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tagsAll"))

    @tags_all.setter
    def tags_all(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        jsii.set(self, "tagsAll", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.sns.SnsTopicConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "application_failure_feedback_role_arn": "applicationFailureFeedbackRoleArn",
        "application_success_feedback_role_arn": "applicationSuccessFeedbackRoleArn",
        "application_success_feedback_sample_rate": "applicationSuccessFeedbackSampleRate",
        "content_based_deduplication": "contentBasedDeduplication",
        "delivery_policy": "deliveryPolicy",
        "display_name": "displayName",
        "fifo_topic": "fifoTopic",
        "firehose_failure_feedback_role_arn": "firehoseFailureFeedbackRoleArn",
        "firehose_success_feedback_role_arn": "firehoseSuccessFeedbackRoleArn",
        "firehose_success_feedback_sample_rate": "firehoseSuccessFeedbackSampleRate",
        "http_failure_feedback_role_arn": "httpFailureFeedbackRoleArn",
        "http_success_feedback_role_arn": "httpSuccessFeedbackRoleArn",
        "http_success_feedback_sample_rate": "httpSuccessFeedbackSampleRate",
        "kms_master_key_id": "kmsMasterKeyId",
        "lambda_failure_feedback_role_arn": "lambdaFailureFeedbackRoleArn",
        "lambda_success_feedback_role_arn": "lambdaSuccessFeedbackRoleArn",
        "lambda_success_feedback_sample_rate": "lambdaSuccessFeedbackSampleRate",
        "name": "name",
        "name_prefix": "namePrefix",
        "policy": "policy",
        "sqs_failure_feedback_role_arn": "sqsFailureFeedbackRoleArn",
        "sqs_success_feedback_role_arn": "sqsSuccessFeedbackRoleArn",
        "sqs_success_feedback_sample_rate": "sqsSuccessFeedbackSampleRate",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class SnsTopicConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        application_failure_feedback_role_arn: typing.Optional[builtins.str] = None,
        application_success_feedback_role_arn: typing.Optional[builtins.str] = None,
        application_success_feedback_sample_rate: typing.Optional[jsii.Number] = None,
        content_based_deduplication: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        delivery_policy: typing.Optional[builtins.str] = None,
        display_name: typing.Optional[builtins.str] = None,
        fifo_topic: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        firehose_failure_feedback_role_arn: typing.Optional[builtins.str] = None,
        firehose_success_feedback_role_arn: typing.Optional[builtins.str] = None,
        firehose_success_feedback_sample_rate: typing.Optional[jsii.Number] = None,
        http_failure_feedback_role_arn: typing.Optional[builtins.str] = None,
        http_success_feedback_role_arn: typing.Optional[builtins.str] = None,
        http_success_feedback_sample_rate: typing.Optional[jsii.Number] = None,
        kms_master_key_id: typing.Optional[builtins.str] = None,
        lambda_failure_feedback_role_arn: typing.Optional[builtins.str] = None,
        lambda_success_feedback_role_arn: typing.Optional[builtins.str] = None,
        lambda_success_feedback_sample_rate: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        name_prefix: typing.Optional[builtins.str] = None,
        policy: typing.Optional[builtins.str] = None,
        sqs_failure_feedback_role_arn: typing.Optional[builtins.str] = None,
        sqs_success_feedback_role_arn: typing.Optional[builtins.str] = None,
        sqs_success_feedback_sample_rate: typing.Optional[jsii.Number] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''AWS Simple Notification Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param application_failure_feedback_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#application_failure_feedback_role_arn SnsTopic#application_failure_feedback_role_arn}.
        :param application_success_feedback_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#application_success_feedback_role_arn SnsTopic#application_success_feedback_role_arn}.
        :param application_success_feedback_sample_rate: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#application_success_feedback_sample_rate SnsTopic#application_success_feedback_sample_rate}.
        :param content_based_deduplication: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#content_based_deduplication SnsTopic#content_based_deduplication}.
        :param delivery_policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#delivery_policy SnsTopic#delivery_policy}.
        :param display_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#display_name SnsTopic#display_name}.
        :param fifo_topic: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#fifo_topic SnsTopic#fifo_topic}.
        :param firehose_failure_feedback_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#firehose_failure_feedback_role_arn SnsTopic#firehose_failure_feedback_role_arn}.
        :param firehose_success_feedback_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#firehose_success_feedback_role_arn SnsTopic#firehose_success_feedback_role_arn}.
        :param firehose_success_feedback_sample_rate: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#firehose_success_feedback_sample_rate SnsTopic#firehose_success_feedback_sample_rate}.
        :param http_failure_feedback_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#http_failure_feedback_role_arn SnsTopic#http_failure_feedback_role_arn}.
        :param http_success_feedback_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#http_success_feedback_role_arn SnsTopic#http_success_feedback_role_arn}.
        :param http_success_feedback_sample_rate: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#http_success_feedback_sample_rate SnsTopic#http_success_feedback_sample_rate}.
        :param kms_master_key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#kms_master_key_id SnsTopic#kms_master_key_id}.
        :param lambda_failure_feedback_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#lambda_failure_feedback_role_arn SnsTopic#lambda_failure_feedback_role_arn}.
        :param lambda_success_feedback_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#lambda_success_feedback_role_arn SnsTopic#lambda_success_feedback_role_arn}.
        :param lambda_success_feedback_sample_rate: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#lambda_success_feedback_sample_rate SnsTopic#lambda_success_feedback_sample_rate}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#name SnsTopic#name}.
        :param name_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#name_prefix SnsTopic#name_prefix}.
        :param policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#policy SnsTopic#policy}.
        :param sqs_failure_feedback_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#sqs_failure_feedback_role_arn SnsTopic#sqs_failure_feedback_role_arn}.
        :param sqs_success_feedback_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#sqs_success_feedback_role_arn SnsTopic#sqs_success_feedback_role_arn}.
        :param sqs_success_feedback_sample_rate: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#sqs_success_feedback_sample_rate SnsTopic#sqs_success_feedback_sample_rate}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#tags SnsTopic#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#tags_all SnsTopic#tags_all}.
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
        if application_failure_feedback_role_arn is not None:
            self._values["application_failure_feedback_role_arn"] = application_failure_feedback_role_arn
        if application_success_feedback_role_arn is not None:
            self._values["application_success_feedback_role_arn"] = application_success_feedback_role_arn
        if application_success_feedback_sample_rate is not None:
            self._values["application_success_feedback_sample_rate"] = application_success_feedback_sample_rate
        if content_based_deduplication is not None:
            self._values["content_based_deduplication"] = content_based_deduplication
        if delivery_policy is not None:
            self._values["delivery_policy"] = delivery_policy
        if display_name is not None:
            self._values["display_name"] = display_name
        if fifo_topic is not None:
            self._values["fifo_topic"] = fifo_topic
        if firehose_failure_feedback_role_arn is not None:
            self._values["firehose_failure_feedback_role_arn"] = firehose_failure_feedback_role_arn
        if firehose_success_feedback_role_arn is not None:
            self._values["firehose_success_feedback_role_arn"] = firehose_success_feedback_role_arn
        if firehose_success_feedback_sample_rate is not None:
            self._values["firehose_success_feedback_sample_rate"] = firehose_success_feedback_sample_rate
        if http_failure_feedback_role_arn is not None:
            self._values["http_failure_feedback_role_arn"] = http_failure_feedback_role_arn
        if http_success_feedback_role_arn is not None:
            self._values["http_success_feedback_role_arn"] = http_success_feedback_role_arn
        if http_success_feedback_sample_rate is not None:
            self._values["http_success_feedback_sample_rate"] = http_success_feedback_sample_rate
        if kms_master_key_id is not None:
            self._values["kms_master_key_id"] = kms_master_key_id
        if lambda_failure_feedback_role_arn is not None:
            self._values["lambda_failure_feedback_role_arn"] = lambda_failure_feedback_role_arn
        if lambda_success_feedback_role_arn is not None:
            self._values["lambda_success_feedback_role_arn"] = lambda_success_feedback_role_arn
        if lambda_success_feedback_sample_rate is not None:
            self._values["lambda_success_feedback_sample_rate"] = lambda_success_feedback_sample_rate
        if name is not None:
            self._values["name"] = name
        if name_prefix is not None:
            self._values["name_prefix"] = name_prefix
        if policy is not None:
            self._values["policy"] = policy
        if sqs_failure_feedback_role_arn is not None:
            self._values["sqs_failure_feedback_role_arn"] = sqs_failure_feedback_role_arn
        if sqs_success_feedback_role_arn is not None:
            self._values["sqs_success_feedback_role_arn"] = sqs_success_feedback_role_arn
        if sqs_success_feedback_sample_rate is not None:
            self._values["sqs_success_feedback_sample_rate"] = sqs_success_feedback_sample_rate
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

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
    def application_failure_feedback_role_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#application_failure_feedback_role_arn SnsTopic#application_failure_feedback_role_arn}.'''
        result = self._values.get("application_failure_feedback_role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def application_success_feedback_role_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#application_success_feedback_role_arn SnsTopic#application_success_feedback_role_arn}.'''
        result = self._values.get("application_success_feedback_role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def application_success_feedback_sample_rate(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#application_success_feedback_sample_rate SnsTopic#application_success_feedback_sample_rate}.'''
        result = self._values.get("application_success_feedback_sample_rate")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def content_based_deduplication(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#content_based_deduplication SnsTopic#content_based_deduplication}.'''
        result = self._values.get("content_based_deduplication")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def delivery_policy(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#delivery_policy SnsTopic#delivery_policy}.'''
        result = self._values.get("delivery_policy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def display_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#display_name SnsTopic#display_name}.'''
        result = self._values.get("display_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def fifo_topic(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#fifo_topic SnsTopic#fifo_topic}.'''
        result = self._values.get("fifo_topic")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def firehose_failure_feedback_role_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#firehose_failure_feedback_role_arn SnsTopic#firehose_failure_feedback_role_arn}.'''
        result = self._values.get("firehose_failure_feedback_role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def firehose_success_feedback_role_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#firehose_success_feedback_role_arn SnsTopic#firehose_success_feedback_role_arn}.'''
        result = self._values.get("firehose_success_feedback_role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def firehose_success_feedback_sample_rate(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#firehose_success_feedback_sample_rate SnsTopic#firehose_success_feedback_sample_rate}.'''
        result = self._values.get("firehose_success_feedback_sample_rate")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def http_failure_feedback_role_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#http_failure_feedback_role_arn SnsTopic#http_failure_feedback_role_arn}.'''
        result = self._values.get("http_failure_feedback_role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def http_success_feedback_role_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#http_success_feedback_role_arn SnsTopic#http_success_feedback_role_arn}.'''
        result = self._values.get("http_success_feedback_role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def http_success_feedback_sample_rate(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#http_success_feedback_sample_rate SnsTopic#http_success_feedback_sample_rate}.'''
        result = self._values.get("http_success_feedback_sample_rate")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def kms_master_key_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#kms_master_key_id SnsTopic#kms_master_key_id}.'''
        result = self._values.get("kms_master_key_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def lambda_failure_feedback_role_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#lambda_failure_feedback_role_arn SnsTopic#lambda_failure_feedback_role_arn}.'''
        result = self._values.get("lambda_failure_feedback_role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def lambda_success_feedback_role_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#lambda_success_feedback_role_arn SnsTopic#lambda_success_feedback_role_arn}.'''
        result = self._values.get("lambda_success_feedback_role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def lambda_success_feedback_sample_rate(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#lambda_success_feedback_sample_rate SnsTopic#lambda_success_feedback_sample_rate}.'''
        result = self._values.get("lambda_success_feedback_sample_rate")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#name SnsTopic#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#name_prefix SnsTopic#name_prefix}.'''
        result = self._values.get("name_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def policy(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#policy SnsTopic#policy}.'''
        result = self._values.get("policy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sqs_failure_feedback_role_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#sqs_failure_feedback_role_arn SnsTopic#sqs_failure_feedback_role_arn}.'''
        result = self._values.get("sqs_failure_feedback_role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sqs_success_feedback_role_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#sqs_success_feedback_role_arn SnsTopic#sqs_success_feedback_role_arn}.'''
        result = self._values.get("sqs_success_feedback_role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sqs_success_feedback_sample_rate(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#sqs_success_feedback_sample_rate SnsTopic#sqs_success_feedback_sample_rate}.'''
        result = self._values.get("sqs_success_feedback_sample_rate")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#tags SnsTopic#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def tags_all(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic#tags_all SnsTopic#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SnsTopicConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SnsTopicPolicy(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.sns.SnsTopicPolicy",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/sns_topic_policy aws_sns_topic_policy}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        arn: builtins.str,
        policy: builtins.str,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/sns_topic_policy aws_sns_topic_policy} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic_policy#arn SnsTopicPolicy#arn}.
        :param policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic_policy#policy SnsTopicPolicy#policy}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = SnsTopicPolicyConfig(
            arn=arn,
            policy=policy,
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
    @jsii.member(jsii_name="owner")
    def owner(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "owner"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arnInput")
    def arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "arnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyInput")
    def policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "policyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @arn.setter
    def arn(self, value: builtins.str) -> None:
        jsii.set(self, "arn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policy")
    def policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policy"))

    @policy.setter
    def policy(self, value: builtins.str) -> None:
        jsii.set(self, "policy", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.sns.SnsTopicPolicyConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "arn": "arn",
        "policy": "policy",
    },
)
class SnsTopicPolicyConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        arn: builtins.str,
        policy: builtins.str,
    ) -> None:
        '''AWS Simple Notification Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic_policy#arn SnsTopicPolicy#arn}.
        :param policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic_policy#policy SnsTopicPolicy#policy}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "arn": arn,
            "policy": policy,
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
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

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
    def arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic_policy#arn SnsTopicPolicy#arn}.'''
        result = self._values.get("arn")
        assert result is not None, "Required property 'arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def policy(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic_policy#policy SnsTopicPolicy#policy}.'''
        result = self._values.get("policy")
        assert result is not None, "Required property 'policy' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SnsTopicPolicyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SnsTopicSubscription(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.sns.SnsTopicSubscription",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/sns_topic_subscription aws_sns_topic_subscription}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        endpoint: builtins.str,
        protocol: builtins.str,
        topic_arn: builtins.str,
        confirmation_timeout_in_minutes: typing.Optional[jsii.Number] = None,
        delivery_policy: typing.Optional[builtins.str] = None,
        endpoint_auto_confirms: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        filter_policy: typing.Optional[builtins.str] = None,
        raw_message_delivery: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        redrive_policy: typing.Optional[builtins.str] = None,
        subscription_role_arn: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/sns_topic_subscription aws_sns_topic_subscription} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param endpoint: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic_subscription#endpoint SnsTopicSubscription#endpoint}.
        :param protocol: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic_subscription#protocol SnsTopicSubscription#protocol}.
        :param topic_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic_subscription#topic_arn SnsTopicSubscription#topic_arn}.
        :param confirmation_timeout_in_minutes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic_subscription#confirmation_timeout_in_minutes SnsTopicSubscription#confirmation_timeout_in_minutes}.
        :param delivery_policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic_subscription#delivery_policy SnsTopicSubscription#delivery_policy}.
        :param endpoint_auto_confirms: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic_subscription#endpoint_auto_confirms SnsTopicSubscription#endpoint_auto_confirms}.
        :param filter_policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic_subscription#filter_policy SnsTopicSubscription#filter_policy}.
        :param raw_message_delivery: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic_subscription#raw_message_delivery SnsTopicSubscription#raw_message_delivery}.
        :param redrive_policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic_subscription#redrive_policy SnsTopicSubscription#redrive_policy}.
        :param subscription_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic_subscription#subscription_role_arn SnsTopicSubscription#subscription_role_arn}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = SnsTopicSubscriptionConfig(
            endpoint=endpoint,
            protocol=protocol,
            topic_arn=topic_arn,
            confirmation_timeout_in_minutes=confirmation_timeout_in_minutes,
            delivery_policy=delivery_policy,
            endpoint_auto_confirms=endpoint_auto_confirms,
            filter_policy=filter_policy,
            raw_message_delivery=raw_message_delivery,
            redrive_policy=redrive_policy,
            subscription_role_arn=subscription_role_arn,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetConfirmationTimeoutInMinutes")
    def reset_confirmation_timeout_in_minutes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConfirmationTimeoutInMinutes", []))

    @jsii.member(jsii_name="resetDeliveryPolicy")
    def reset_delivery_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeliveryPolicy", []))

    @jsii.member(jsii_name="resetEndpointAutoConfirms")
    def reset_endpoint_auto_confirms(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEndpointAutoConfirms", []))

    @jsii.member(jsii_name="resetFilterPolicy")
    def reset_filter_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFilterPolicy", []))

    @jsii.member(jsii_name="resetRawMessageDelivery")
    def reset_raw_message_delivery(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRawMessageDelivery", []))

    @jsii.member(jsii_name="resetRedrivePolicy")
    def reset_redrive_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRedrivePolicy", []))

    @jsii.member(jsii_name="resetSubscriptionRoleArn")
    def reset_subscription_role_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSubscriptionRoleArn", []))

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
    @jsii.member(jsii_name="confirmationWasAuthenticated")
    def confirmation_was_authenticated(self) -> cdktf.IResolvable:
        return typing.cast(cdktf.IResolvable, jsii.get(self, "confirmationWasAuthenticated"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ownerId")
    def owner_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ownerId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pendingConfirmation")
    def pending_confirmation(self) -> cdktf.IResolvable:
        return typing.cast(cdktf.IResolvable, jsii.get(self, "pendingConfirmation"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="confirmationTimeoutInMinutesInput")
    def confirmation_timeout_in_minutes_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "confirmationTimeoutInMinutesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deliveryPolicyInput")
    def delivery_policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deliveryPolicyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpointAutoConfirmsInput")
    def endpoint_auto_confirms_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "endpointAutoConfirmsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpointInput")
    def endpoint_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "endpointInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="filterPolicyInput")
    def filter_policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "filterPolicyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="protocolInput")
    def protocol_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "protocolInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rawMessageDeliveryInput")
    def raw_message_delivery_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "rawMessageDeliveryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="redrivePolicyInput")
    def redrive_policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "redrivePolicyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subscriptionRoleArnInput")
    def subscription_role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "subscriptionRoleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="topicArnInput")
    def topic_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "topicArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="confirmationTimeoutInMinutes")
    def confirmation_timeout_in_minutes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "confirmationTimeoutInMinutes"))

    @confirmation_timeout_in_minutes.setter
    def confirmation_timeout_in_minutes(self, value: jsii.Number) -> None:
        jsii.set(self, "confirmationTimeoutInMinutes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deliveryPolicy")
    def delivery_policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deliveryPolicy"))

    @delivery_policy.setter
    def delivery_policy(self, value: builtins.str) -> None:
        jsii.set(self, "deliveryPolicy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpoint")
    def endpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endpoint"))

    @endpoint.setter
    def endpoint(self, value: builtins.str) -> None:
        jsii.set(self, "endpoint", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpointAutoConfirms")
    def endpoint_auto_confirms(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "endpointAutoConfirms"))

    @endpoint_auto_confirms.setter
    def endpoint_auto_confirms(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "endpointAutoConfirms", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="filterPolicy")
    def filter_policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "filterPolicy"))

    @filter_policy.setter
    def filter_policy(self, value: builtins.str) -> None:
        jsii.set(self, "filterPolicy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="protocol")
    def protocol(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "protocol"))

    @protocol.setter
    def protocol(self, value: builtins.str) -> None:
        jsii.set(self, "protocol", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rawMessageDelivery")
    def raw_message_delivery(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "rawMessageDelivery"))

    @raw_message_delivery.setter
    def raw_message_delivery(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "rawMessageDelivery", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="redrivePolicy")
    def redrive_policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "redrivePolicy"))

    @redrive_policy.setter
    def redrive_policy(self, value: builtins.str) -> None:
        jsii.set(self, "redrivePolicy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subscriptionRoleArn")
    def subscription_role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "subscriptionRoleArn"))

    @subscription_role_arn.setter
    def subscription_role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "subscriptionRoleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="topicArn")
    def topic_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "topicArn"))

    @topic_arn.setter
    def topic_arn(self, value: builtins.str) -> None:
        jsii.set(self, "topicArn", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.sns.SnsTopicSubscriptionConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "endpoint": "endpoint",
        "protocol": "protocol",
        "topic_arn": "topicArn",
        "confirmation_timeout_in_minutes": "confirmationTimeoutInMinutes",
        "delivery_policy": "deliveryPolicy",
        "endpoint_auto_confirms": "endpointAutoConfirms",
        "filter_policy": "filterPolicy",
        "raw_message_delivery": "rawMessageDelivery",
        "redrive_policy": "redrivePolicy",
        "subscription_role_arn": "subscriptionRoleArn",
    },
)
class SnsTopicSubscriptionConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        endpoint: builtins.str,
        protocol: builtins.str,
        topic_arn: builtins.str,
        confirmation_timeout_in_minutes: typing.Optional[jsii.Number] = None,
        delivery_policy: typing.Optional[builtins.str] = None,
        endpoint_auto_confirms: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        filter_policy: typing.Optional[builtins.str] = None,
        raw_message_delivery: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        redrive_policy: typing.Optional[builtins.str] = None,
        subscription_role_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Simple Notification Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param endpoint: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic_subscription#endpoint SnsTopicSubscription#endpoint}.
        :param protocol: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic_subscription#protocol SnsTopicSubscription#protocol}.
        :param topic_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic_subscription#topic_arn SnsTopicSubscription#topic_arn}.
        :param confirmation_timeout_in_minutes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic_subscription#confirmation_timeout_in_minutes SnsTopicSubscription#confirmation_timeout_in_minutes}.
        :param delivery_policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic_subscription#delivery_policy SnsTopicSubscription#delivery_policy}.
        :param endpoint_auto_confirms: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic_subscription#endpoint_auto_confirms SnsTopicSubscription#endpoint_auto_confirms}.
        :param filter_policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic_subscription#filter_policy SnsTopicSubscription#filter_policy}.
        :param raw_message_delivery: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic_subscription#raw_message_delivery SnsTopicSubscription#raw_message_delivery}.
        :param redrive_policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic_subscription#redrive_policy SnsTopicSubscription#redrive_policy}.
        :param subscription_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic_subscription#subscription_role_arn SnsTopicSubscription#subscription_role_arn}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "endpoint": endpoint,
            "protocol": protocol,
            "topic_arn": topic_arn,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if confirmation_timeout_in_minutes is not None:
            self._values["confirmation_timeout_in_minutes"] = confirmation_timeout_in_minutes
        if delivery_policy is not None:
            self._values["delivery_policy"] = delivery_policy
        if endpoint_auto_confirms is not None:
            self._values["endpoint_auto_confirms"] = endpoint_auto_confirms
        if filter_policy is not None:
            self._values["filter_policy"] = filter_policy
        if raw_message_delivery is not None:
            self._values["raw_message_delivery"] = raw_message_delivery
        if redrive_policy is not None:
            self._values["redrive_policy"] = redrive_policy
        if subscription_role_arn is not None:
            self._values["subscription_role_arn"] = subscription_role_arn

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

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
    def endpoint(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic_subscription#endpoint SnsTopicSubscription#endpoint}.'''
        result = self._values.get("endpoint")
        assert result is not None, "Required property 'endpoint' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def protocol(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic_subscription#protocol SnsTopicSubscription#protocol}.'''
        result = self._values.get("protocol")
        assert result is not None, "Required property 'protocol' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def topic_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic_subscription#topic_arn SnsTopicSubscription#topic_arn}.'''
        result = self._values.get("topic_arn")
        assert result is not None, "Required property 'topic_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def confirmation_timeout_in_minutes(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic_subscription#confirmation_timeout_in_minutes SnsTopicSubscription#confirmation_timeout_in_minutes}.'''
        result = self._values.get("confirmation_timeout_in_minutes")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def delivery_policy(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic_subscription#delivery_policy SnsTopicSubscription#delivery_policy}.'''
        result = self._values.get("delivery_policy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def endpoint_auto_confirms(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic_subscription#endpoint_auto_confirms SnsTopicSubscription#endpoint_auto_confirms}.'''
        result = self._values.get("endpoint_auto_confirms")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def filter_policy(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic_subscription#filter_policy SnsTopicSubscription#filter_policy}.'''
        result = self._values.get("filter_policy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def raw_message_delivery(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic_subscription#raw_message_delivery SnsTopicSubscription#raw_message_delivery}.'''
        result = self._values.get("raw_message_delivery")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def redrive_policy(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic_subscription#redrive_policy SnsTopicSubscription#redrive_policy}.'''
        result = self._values.get("redrive_policy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def subscription_role_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sns_topic_subscription#subscription_role_arn SnsTopicSubscription#subscription_role_arn}.'''
        result = self._values.get("subscription_role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SnsTopicSubscriptionConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "DataAwsSnsTopic",
    "DataAwsSnsTopicConfig",
    "SnsPlatformApplication",
    "SnsPlatformApplicationConfig",
    "SnsSmsPreferences",
    "SnsSmsPreferencesConfig",
    "SnsTopic",
    "SnsTopicConfig",
    "SnsTopicPolicy",
    "SnsTopicPolicyConfig",
    "SnsTopicSubscription",
    "SnsTopicSubscriptionConfig",
]

publication.publish()
