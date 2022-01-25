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


class DataAwsSqsQueue(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.sqs.DataAwsSqsQueue",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/sqs_queue aws_sqs_queue}.'''

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
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/sqs_queue aws_sqs_queue} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/sqs_queue#name DataAwsSqsQueue#name}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/sqs_queue#tags DataAwsSqsQueue#tags}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsSqsQueueConfig(
            name=name,
            tags=tags,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

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
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

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
    jsii_type="@cdktf/provider-aws.sqs.DataAwsSqsQueueConfig",
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
class DataAwsSqsQueueConfig(cdktf.TerraformMetaArguments):
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
        '''AWS Simple Queue Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/sqs_queue#name DataAwsSqsQueue#name}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/sqs_queue#tags DataAwsSqsQueue#tags}.
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/sqs_queue#name DataAwsSqsQueue#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/sqs_queue#tags DataAwsSqsQueue#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsSqsQueueConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SqsQueue(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.sqs.SqsQueue",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/sqs_queue aws_sqs_queue}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        content_based_deduplication: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        deduplication_scope: typing.Optional[builtins.str] = None,
        delay_seconds: typing.Optional[jsii.Number] = None,
        fifo_queue: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        fifo_throughput_limit: typing.Optional[builtins.str] = None,
        kms_data_key_reuse_period_seconds: typing.Optional[jsii.Number] = None,
        kms_master_key_id: typing.Optional[builtins.str] = None,
        max_message_size: typing.Optional[jsii.Number] = None,
        message_retention_seconds: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        name_prefix: typing.Optional[builtins.str] = None,
        policy: typing.Optional[builtins.str] = None,
        receive_wait_time_seconds: typing.Optional[jsii.Number] = None,
        redrive_allow_policy: typing.Optional[builtins.str] = None,
        redrive_policy: typing.Optional[builtins.str] = None,
        sqs_managed_sse_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        visibility_timeout_seconds: typing.Optional[jsii.Number] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/sqs_queue aws_sqs_queue} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param content_based_deduplication: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sqs_queue#content_based_deduplication SqsQueue#content_based_deduplication}.
        :param deduplication_scope: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sqs_queue#deduplication_scope SqsQueue#deduplication_scope}.
        :param delay_seconds: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sqs_queue#delay_seconds SqsQueue#delay_seconds}.
        :param fifo_queue: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sqs_queue#fifo_queue SqsQueue#fifo_queue}.
        :param fifo_throughput_limit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sqs_queue#fifo_throughput_limit SqsQueue#fifo_throughput_limit}.
        :param kms_data_key_reuse_period_seconds: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sqs_queue#kms_data_key_reuse_period_seconds SqsQueue#kms_data_key_reuse_period_seconds}.
        :param kms_master_key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sqs_queue#kms_master_key_id SqsQueue#kms_master_key_id}.
        :param max_message_size: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sqs_queue#max_message_size SqsQueue#max_message_size}.
        :param message_retention_seconds: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sqs_queue#message_retention_seconds SqsQueue#message_retention_seconds}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sqs_queue#name SqsQueue#name}.
        :param name_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sqs_queue#name_prefix SqsQueue#name_prefix}.
        :param policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sqs_queue#policy SqsQueue#policy}.
        :param receive_wait_time_seconds: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sqs_queue#receive_wait_time_seconds SqsQueue#receive_wait_time_seconds}.
        :param redrive_allow_policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sqs_queue#redrive_allow_policy SqsQueue#redrive_allow_policy}.
        :param redrive_policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sqs_queue#redrive_policy SqsQueue#redrive_policy}.
        :param sqs_managed_sse_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sqs_queue#sqs_managed_sse_enabled SqsQueue#sqs_managed_sse_enabled}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sqs_queue#tags SqsQueue#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sqs_queue#tags_all SqsQueue#tags_all}.
        :param visibility_timeout_seconds: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sqs_queue#visibility_timeout_seconds SqsQueue#visibility_timeout_seconds}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = SqsQueueConfig(
            content_based_deduplication=content_based_deduplication,
            deduplication_scope=deduplication_scope,
            delay_seconds=delay_seconds,
            fifo_queue=fifo_queue,
            fifo_throughput_limit=fifo_throughput_limit,
            kms_data_key_reuse_period_seconds=kms_data_key_reuse_period_seconds,
            kms_master_key_id=kms_master_key_id,
            max_message_size=max_message_size,
            message_retention_seconds=message_retention_seconds,
            name=name,
            name_prefix=name_prefix,
            policy=policy,
            receive_wait_time_seconds=receive_wait_time_seconds,
            redrive_allow_policy=redrive_allow_policy,
            redrive_policy=redrive_policy,
            sqs_managed_sse_enabled=sqs_managed_sse_enabled,
            tags=tags,
            tags_all=tags_all,
            visibility_timeout_seconds=visibility_timeout_seconds,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetContentBasedDeduplication")
    def reset_content_based_deduplication(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetContentBasedDeduplication", []))

    @jsii.member(jsii_name="resetDeduplicationScope")
    def reset_deduplication_scope(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeduplicationScope", []))

    @jsii.member(jsii_name="resetDelaySeconds")
    def reset_delay_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDelaySeconds", []))

    @jsii.member(jsii_name="resetFifoQueue")
    def reset_fifo_queue(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFifoQueue", []))

    @jsii.member(jsii_name="resetFifoThroughputLimit")
    def reset_fifo_throughput_limit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFifoThroughputLimit", []))

    @jsii.member(jsii_name="resetKmsDataKeyReusePeriodSeconds")
    def reset_kms_data_key_reuse_period_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKmsDataKeyReusePeriodSeconds", []))

    @jsii.member(jsii_name="resetKmsMasterKeyId")
    def reset_kms_master_key_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKmsMasterKeyId", []))

    @jsii.member(jsii_name="resetMaxMessageSize")
    def reset_max_message_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxMessageSize", []))

    @jsii.member(jsii_name="resetMessageRetentionSeconds")
    def reset_message_retention_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMessageRetentionSeconds", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetNamePrefix")
    def reset_name_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamePrefix", []))

    @jsii.member(jsii_name="resetPolicy")
    def reset_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPolicy", []))

    @jsii.member(jsii_name="resetReceiveWaitTimeSeconds")
    def reset_receive_wait_time_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReceiveWaitTimeSeconds", []))

    @jsii.member(jsii_name="resetRedriveAllowPolicy")
    def reset_redrive_allow_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRedriveAllowPolicy", []))

    @jsii.member(jsii_name="resetRedrivePolicy")
    def reset_redrive_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRedrivePolicy", []))

    @jsii.member(jsii_name="resetSqsManagedSseEnabled")
    def reset_sqs_managed_sse_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSqsManagedSseEnabled", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetVisibilityTimeoutSeconds")
    def reset_visibility_timeout_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVisibilityTimeoutSeconds", []))

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
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="contentBasedDeduplicationInput")
    def content_based_deduplication_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "contentBasedDeduplicationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deduplicationScopeInput")
    def deduplication_scope_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deduplicationScopeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="delaySecondsInput")
    def delay_seconds_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "delaySecondsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fifoQueueInput")
    def fifo_queue_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "fifoQueueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fifoThroughputLimitInput")
    def fifo_throughput_limit_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fifoThroughputLimitInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsDataKeyReusePeriodSecondsInput")
    def kms_data_key_reuse_period_seconds_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "kmsDataKeyReusePeriodSecondsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsMasterKeyIdInput")
    def kms_master_key_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kmsMasterKeyIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxMessageSizeInput")
    def max_message_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxMessageSizeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="messageRetentionSecondsInput")
    def message_retention_seconds_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "messageRetentionSecondsInput"))

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
    @jsii.member(jsii_name="receiveWaitTimeSecondsInput")
    def receive_wait_time_seconds_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "receiveWaitTimeSecondsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="redriveAllowPolicyInput")
    def redrive_allow_policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "redriveAllowPolicyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="redrivePolicyInput")
    def redrive_policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "redrivePolicyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sqsManagedSseEnabledInput")
    def sqs_managed_sse_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "sqsManagedSseEnabledInput"))

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
    @jsii.member(jsii_name="visibilityTimeoutSecondsInput")
    def visibility_timeout_seconds_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "visibilityTimeoutSecondsInput"))

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
    @jsii.member(jsii_name="deduplicationScope")
    def deduplication_scope(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deduplicationScope"))

    @deduplication_scope.setter
    def deduplication_scope(self, value: builtins.str) -> None:
        jsii.set(self, "deduplicationScope", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="delaySeconds")
    def delay_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "delaySeconds"))

    @delay_seconds.setter
    def delay_seconds(self, value: jsii.Number) -> None:
        jsii.set(self, "delaySeconds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fifoQueue")
    def fifo_queue(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "fifoQueue"))

    @fifo_queue.setter
    def fifo_queue(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "fifoQueue", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fifoThroughputLimit")
    def fifo_throughput_limit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fifoThroughputLimit"))

    @fifo_throughput_limit.setter
    def fifo_throughput_limit(self, value: builtins.str) -> None:
        jsii.set(self, "fifoThroughputLimit", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsDataKeyReusePeriodSeconds")
    def kms_data_key_reuse_period_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "kmsDataKeyReusePeriodSeconds"))

    @kms_data_key_reuse_period_seconds.setter
    def kms_data_key_reuse_period_seconds(self, value: jsii.Number) -> None:
        jsii.set(self, "kmsDataKeyReusePeriodSeconds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsMasterKeyId")
    def kms_master_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsMasterKeyId"))

    @kms_master_key_id.setter
    def kms_master_key_id(self, value: builtins.str) -> None:
        jsii.set(self, "kmsMasterKeyId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxMessageSize")
    def max_message_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxMessageSize"))

    @max_message_size.setter
    def max_message_size(self, value: jsii.Number) -> None:
        jsii.set(self, "maxMessageSize", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="messageRetentionSeconds")
    def message_retention_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "messageRetentionSeconds"))

    @message_retention_seconds.setter
    def message_retention_seconds(self, value: jsii.Number) -> None:
        jsii.set(self, "messageRetentionSeconds", value)

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
    @jsii.member(jsii_name="receiveWaitTimeSeconds")
    def receive_wait_time_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "receiveWaitTimeSeconds"))

    @receive_wait_time_seconds.setter
    def receive_wait_time_seconds(self, value: jsii.Number) -> None:
        jsii.set(self, "receiveWaitTimeSeconds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="redriveAllowPolicy")
    def redrive_allow_policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "redriveAllowPolicy"))

    @redrive_allow_policy.setter
    def redrive_allow_policy(self, value: builtins.str) -> None:
        jsii.set(self, "redriveAllowPolicy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="redrivePolicy")
    def redrive_policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "redrivePolicy"))

    @redrive_policy.setter
    def redrive_policy(self, value: builtins.str) -> None:
        jsii.set(self, "redrivePolicy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sqsManagedSseEnabled")
    def sqs_managed_sse_enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "sqsManagedSseEnabled"))

    @sqs_managed_sse_enabled.setter
    def sqs_managed_sse_enabled(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "sqsManagedSseEnabled", value)

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
    @jsii.member(jsii_name="visibilityTimeoutSeconds")
    def visibility_timeout_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "visibilityTimeoutSeconds"))

    @visibility_timeout_seconds.setter
    def visibility_timeout_seconds(self, value: jsii.Number) -> None:
        jsii.set(self, "visibilityTimeoutSeconds", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.sqs.SqsQueueConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "content_based_deduplication": "contentBasedDeduplication",
        "deduplication_scope": "deduplicationScope",
        "delay_seconds": "delaySeconds",
        "fifo_queue": "fifoQueue",
        "fifo_throughput_limit": "fifoThroughputLimit",
        "kms_data_key_reuse_period_seconds": "kmsDataKeyReusePeriodSeconds",
        "kms_master_key_id": "kmsMasterKeyId",
        "max_message_size": "maxMessageSize",
        "message_retention_seconds": "messageRetentionSeconds",
        "name": "name",
        "name_prefix": "namePrefix",
        "policy": "policy",
        "receive_wait_time_seconds": "receiveWaitTimeSeconds",
        "redrive_allow_policy": "redriveAllowPolicy",
        "redrive_policy": "redrivePolicy",
        "sqs_managed_sse_enabled": "sqsManagedSseEnabled",
        "tags": "tags",
        "tags_all": "tagsAll",
        "visibility_timeout_seconds": "visibilityTimeoutSeconds",
    },
)
class SqsQueueConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        content_based_deduplication: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        deduplication_scope: typing.Optional[builtins.str] = None,
        delay_seconds: typing.Optional[jsii.Number] = None,
        fifo_queue: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        fifo_throughput_limit: typing.Optional[builtins.str] = None,
        kms_data_key_reuse_period_seconds: typing.Optional[jsii.Number] = None,
        kms_master_key_id: typing.Optional[builtins.str] = None,
        max_message_size: typing.Optional[jsii.Number] = None,
        message_retention_seconds: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        name_prefix: typing.Optional[builtins.str] = None,
        policy: typing.Optional[builtins.str] = None,
        receive_wait_time_seconds: typing.Optional[jsii.Number] = None,
        redrive_allow_policy: typing.Optional[builtins.str] = None,
        redrive_policy: typing.Optional[builtins.str] = None,
        sqs_managed_sse_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        visibility_timeout_seconds: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''AWS Simple Queue Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param content_based_deduplication: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sqs_queue#content_based_deduplication SqsQueue#content_based_deduplication}.
        :param deduplication_scope: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sqs_queue#deduplication_scope SqsQueue#deduplication_scope}.
        :param delay_seconds: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sqs_queue#delay_seconds SqsQueue#delay_seconds}.
        :param fifo_queue: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sqs_queue#fifo_queue SqsQueue#fifo_queue}.
        :param fifo_throughput_limit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sqs_queue#fifo_throughput_limit SqsQueue#fifo_throughput_limit}.
        :param kms_data_key_reuse_period_seconds: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sqs_queue#kms_data_key_reuse_period_seconds SqsQueue#kms_data_key_reuse_period_seconds}.
        :param kms_master_key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sqs_queue#kms_master_key_id SqsQueue#kms_master_key_id}.
        :param max_message_size: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sqs_queue#max_message_size SqsQueue#max_message_size}.
        :param message_retention_seconds: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sqs_queue#message_retention_seconds SqsQueue#message_retention_seconds}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sqs_queue#name SqsQueue#name}.
        :param name_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sqs_queue#name_prefix SqsQueue#name_prefix}.
        :param policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sqs_queue#policy SqsQueue#policy}.
        :param receive_wait_time_seconds: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sqs_queue#receive_wait_time_seconds SqsQueue#receive_wait_time_seconds}.
        :param redrive_allow_policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sqs_queue#redrive_allow_policy SqsQueue#redrive_allow_policy}.
        :param redrive_policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sqs_queue#redrive_policy SqsQueue#redrive_policy}.
        :param sqs_managed_sse_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sqs_queue#sqs_managed_sse_enabled SqsQueue#sqs_managed_sse_enabled}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sqs_queue#tags SqsQueue#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sqs_queue#tags_all SqsQueue#tags_all}.
        :param visibility_timeout_seconds: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sqs_queue#visibility_timeout_seconds SqsQueue#visibility_timeout_seconds}.
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
        if content_based_deduplication is not None:
            self._values["content_based_deduplication"] = content_based_deduplication
        if deduplication_scope is not None:
            self._values["deduplication_scope"] = deduplication_scope
        if delay_seconds is not None:
            self._values["delay_seconds"] = delay_seconds
        if fifo_queue is not None:
            self._values["fifo_queue"] = fifo_queue
        if fifo_throughput_limit is not None:
            self._values["fifo_throughput_limit"] = fifo_throughput_limit
        if kms_data_key_reuse_period_seconds is not None:
            self._values["kms_data_key_reuse_period_seconds"] = kms_data_key_reuse_period_seconds
        if kms_master_key_id is not None:
            self._values["kms_master_key_id"] = kms_master_key_id
        if max_message_size is not None:
            self._values["max_message_size"] = max_message_size
        if message_retention_seconds is not None:
            self._values["message_retention_seconds"] = message_retention_seconds
        if name is not None:
            self._values["name"] = name
        if name_prefix is not None:
            self._values["name_prefix"] = name_prefix
        if policy is not None:
            self._values["policy"] = policy
        if receive_wait_time_seconds is not None:
            self._values["receive_wait_time_seconds"] = receive_wait_time_seconds
        if redrive_allow_policy is not None:
            self._values["redrive_allow_policy"] = redrive_allow_policy
        if redrive_policy is not None:
            self._values["redrive_policy"] = redrive_policy
        if sqs_managed_sse_enabled is not None:
            self._values["sqs_managed_sse_enabled"] = sqs_managed_sse_enabled
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if visibility_timeout_seconds is not None:
            self._values["visibility_timeout_seconds"] = visibility_timeout_seconds

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
    def content_based_deduplication(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sqs_queue#content_based_deduplication SqsQueue#content_based_deduplication}.'''
        result = self._values.get("content_based_deduplication")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def deduplication_scope(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sqs_queue#deduplication_scope SqsQueue#deduplication_scope}.'''
        result = self._values.get("deduplication_scope")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delay_seconds(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sqs_queue#delay_seconds SqsQueue#delay_seconds}.'''
        result = self._values.get("delay_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def fifo_queue(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sqs_queue#fifo_queue SqsQueue#fifo_queue}.'''
        result = self._values.get("fifo_queue")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def fifo_throughput_limit(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sqs_queue#fifo_throughput_limit SqsQueue#fifo_throughput_limit}.'''
        result = self._values.get("fifo_throughput_limit")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def kms_data_key_reuse_period_seconds(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sqs_queue#kms_data_key_reuse_period_seconds SqsQueue#kms_data_key_reuse_period_seconds}.'''
        result = self._values.get("kms_data_key_reuse_period_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def kms_master_key_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sqs_queue#kms_master_key_id SqsQueue#kms_master_key_id}.'''
        result = self._values.get("kms_master_key_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_message_size(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sqs_queue#max_message_size SqsQueue#max_message_size}.'''
        result = self._values.get("max_message_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def message_retention_seconds(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sqs_queue#message_retention_seconds SqsQueue#message_retention_seconds}.'''
        result = self._values.get("message_retention_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sqs_queue#name SqsQueue#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sqs_queue#name_prefix SqsQueue#name_prefix}.'''
        result = self._values.get("name_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def policy(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sqs_queue#policy SqsQueue#policy}.'''
        result = self._values.get("policy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def receive_wait_time_seconds(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sqs_queue#receive_wait_time_seconds SqsQueue#receive_wait_time_seconds}.'''
        result = self._values.get("receive_wait_time_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def redrive_allow_policy(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sqs_queue#redrive_allow_policy SqsQueue#redrive_allow_policy}.'''
        result = self._values.get("redrive_allow_policy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def redrive_policy(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sqs_queue#redrive_policy SqsQueue#redrive_policy}.'''
        result = self._values.get("redrive_policy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sqs_managed_sse_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sqs_queue#sqs_managed_sse_enabled SqsQueue#sqs_managed_sse_enabled}.'''
        result = self._values.get("sqs_managed_sse_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sqs_queue#tags SqsQueue#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sqs_queue#tags_all SqsQueue#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def visibility_timeout_seconds(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sqs_queue#visibility_timeout_seconds SqsQueue#visibility_timeout_seconds}.'''
        result = self._values.get("visibility_timeout_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SqsQueueConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SqsQueuePolicy(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.sqs.SqsQueuePolicy",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/sqs_queue_policy aws_sqs_queue_policy}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        policy: builtins.str,
        queue_url: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/sqs_queue_policy aws_sqs_queue_policy} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sqs_queue_policy#policy SqsQueuePolicy#policy}.
        :param queue_url: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sqs_queue_policy#queue_url SqsQueuePolicy#queue_url}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = SqsQueuePolicyConfig(
            policy=policy,
            queue_url=queue_url,
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
    @jsii.member(jsii_name="queueUrlInput")
    def queue_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "queueUrlInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policy")
    def policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policy"))

    @policy.setter
    def policy(self, value: builtins.str) -> None:
        jsii.set(self, "policy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="queueUrl")
    def queue_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "queueUrl"))

    @queue_url.setter
    def queue_url(self, value: builtins.str) -> None:
        jsii.set(self, "queueUrl", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.sqs.SqsQueuePolicyConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "policy": "policy",
        "queue_url": "queueUrl",
    },
)
class SqsQueuePolicyConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        policy: builtins.str,
        queue_url: builtins.str,
    ) -> None:
        '''AWS Simple Queue Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sqs_queue_policy#policy SqsQueuePolicy#policy}.
        :param queue_url: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sqs_queue_policy#queue_url SqsQueuePolicy#queue_url}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "policy": policy,
            "queue_url": queue_url,
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sqs_queue_policy#policy SqsQueuePolicy#policy}.'''
        result = self._values.get("policy")
        assert result is not None, "Required property 'policy' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def queue_url(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/sqs_queue_policy#queue_url SqsQueuePolicy#queue_url}.'''
        result = self._values.get("queue_url")
        assert result is not None, "Required property 'queue_url' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SqsQueuePolicyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "DataAwsSqsQueue",
    "DataAwsSqsQueueConfig",
    "SqsQueue",
    "SqsQueueConfig",
    "SqsQueuePolicy",
    "SqsQueuePolicyConfig",
]

publication.publish()
