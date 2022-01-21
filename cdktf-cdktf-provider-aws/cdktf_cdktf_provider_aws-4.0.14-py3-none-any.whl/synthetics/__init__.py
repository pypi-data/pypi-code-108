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


class SyntheticsCanary(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.synthetics.SyntheticsCanary",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary aws_synthetics_canary}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        artifact_s3_location: builtins.str,
        execution_role_arn: builtins.str,
        handler: builtins.str,
        name: builtins.str,
        runtime_version: builtins.str,
        schedule: "SyntheticsCanarySchedule",
        artifact_config: typing.Optional["SyntheticsCanaryArtifactConfig"] = None,
        failure_retention_period: typing.Optional[jsii.Number] = None,
        run_config: typing.Optional["SyntheticsCanaryRunConfig"] = None,
        s3_bucket: typing.Optional[builtins.str] = None,
        s3_key: typing.Optional[builtins.str] = None,
        s3_version: typing.Optional[builtins.str] = None,
        start_canary: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        success_retention_period: typing.Optional[jsii.Number] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        vpc_config: typing.Optional["SyntheticsCanaryVpcConfig"] = None,
        zip_file: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary aws_synthetics_canary} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param artifact_s3_location: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#artifact_s3_location SyntheticsCanary#artifact_s3_location}.
        :param execution_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#execution_role_arn SyntheticsCanary#execution_role_arn}.
        :param handler: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#handler SyntheticsCanary#handler}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#name SyntheticsCanary#name}.
        :param runtime_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#runtime_version SyntheticsCanary#runtime_version}.
        :param schedule: schedule block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#schedule SyntheticsCanary#schedule}
        :param artifact_config: artifact_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#artifact_config SyntheticsCanary#artifact_config}
        :param failure_retention_period: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#failure_retention_period SyntheticsCanary#failure_retention_period}.
        :param run_config: run_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#run_config SyntheticsCanary#run_config}
        :param s3_bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#s3_bucket SyntheticsCanary#s3_bucket}.
        :param s3_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#s3_key SyntheticsCanary#s3_key}.
        :param s3_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#s3_version SyntheticsCanary#s3_version}.
        :param start_canary: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#start_canary SyntheticsCanary#start_canary}.
        :param success_retention_period: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#success_retention_period SyntheticsCanary#success_retention_period}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#tags SyntheticsCanary#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#tags_all SyntheticsCanary#tags_all}.
        :param vpc_config: vpc_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#vpc_config SyntheticsCanary#vpc_config}
        :param zip_file: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#zip_file SyntheticsCanary#zip_file}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = SyntheticsCanaryConfig(
            artifact_s3_location=artifact_s3_location,
            execution_role_arn=execution_role_arn,
            handler=handler,
            name=name,
            runtime_version=runtime_version,
            schedule=schedule,
            artifact_config=artifact_config,
            failure_retention_period=failure_retention_period,
            run_config=run_config,
            s3_bucket=s3_bucket,
            s3_key=s3_key,
            s3_version=s3_version,
            start_canary=start_canary,
            success_retention_period=success_retention_period,
            tags=tags,
            tags_all=tags_all,
            vpc_config=vpc_config,
            zip_file=zip_file,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putArtifactConfig")
    def put_artifact_config(
        self,
        *,
        s3_encryption: typing.Optional["SyntheticsCanaryArtifactConfigS3Encryption"] = None,
    ) -> None:
        '''
        :param s3_encryption: s3_encryption block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#s3_encryption SyntheticsCanary#s3_encryption}
        '''
        value = SyntheticsCanaryArtifactConfig(s3_encryption=s3_encryption)

        return typing.cast(None, jsii.invoke(self, "putArtifactConfig", [value]))

    @jsii.member(jsii_name="putRunConfig")
    def put_run_config(
        self,
        *,
        active_tracing: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        memory_in_mb: typing.Optional[jsii.Number] = None,
        timeout_in_seconds: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param active_tracing: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#active_tracing SyntheticsCanary#active_tracing}.
        :param memory_in_mb: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#memory_in_mb SyntheticsCanary#memory_in_mb}.
        :param timeout_in_seconds: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#timeout_in_seconds SyntheticsCanary#timeout_in_seconds}.
        '''
        value = SyntheticsCanaryRunConfig(
            active_tracing=active_tracing,
            memory_in_mb=memory_in_mb,
            timeout_in_seconds=timeout_in_seconds,
        )

        return typing.cast(None, jsii.invoke(self, "putRunConfig", [value]))

    @jsii.member(jsii_name="putSchedule")
    def put_schedule(
        self,
        *,
        expression: builtins.str,
        duration_in_seconds: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param expression: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#expression SyntheticsCanary#expression}.
        :param duration_in_seconds: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#duration_in_seconds SyntheticsCanary#duration_in_seconds}.
        '''
        value = SyntheticsCanarySchedule(
            expression=expression, duration_in_seconds=duration_in_seconds
        )

        return typing.cast(None, jsii.invoke(self, "putSchedule", [value]))

    @jsii.member(jsii_name="putVpcConfig")
    def put_vpc_config(
        self,
        *,
        security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        subnet_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param security_group_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#security_group_ids SyntheticsCanary#security_group_ids}.
        :param subnet_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#subnet_ids SyntheticsCanary#subnet_ids}.
        '''
        value = SyntheticsCanaryVpcConfig(
            security_group_ids=security_group_ids, subnet_ids=subnet_ids
        )

        return typing.cast(None, jsii.invoke(self, "putVpcConfig", [value]))

    @jsii.member(jsii_name="resetArtifactConfig")
    def reset_artifact_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetArtifactConfig", []))

    @jsii.member(jsii_name="resetFailureRetentionPeriod")
    def reset_failure_retention_period(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFailureRetentionPeriod", []))

    @jsii.member(jsii_name="resetRunConfig")
    def reset_run_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRunConfig", []))

    @jsii.member(jsii_name="resetS3Bucket")
    def reset_s3_bucket(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetS3Bucket", []))

    @jsii.member(jsii_name="resetS3Key")
    def reset_s3_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetS3Key", []))

    @jsii.member(jsii_name="resetS3Version")
    def reset_s3_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetS3Version", []))

    @jsii.member(jsii_name="resetStartCanary")
    def reset_start_canary(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStartCanary", []))

    @jsii.member(jsii_name="resetSuccessRetentionPeriod")
    def reset_success_retention_period(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSuccessRetentionPeriod", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetVpcConfig")
    def reset_vpc_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVpcConfig", []))

    @jsii.member(jsii_name="resetZipFile")
    def reset_zip_file(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetZipFile", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.member(jsii_name="timeline")
    def timeline(self, index: builtins.str) -> "SyntheticsCanaryTimeline":
        '''
        :param index: -
        '''
        return typing.cast("SyntheticsCanaryTimeline", jsii.invoke(self, "timeline", [index]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="artifactConfig")
    def artifact_config(self) -> "SyntheticsCanaryArtifactConfigOutputReference":
        return typing.cast("SyntheticsCanaryArtifactConfigOutputReference", jsii.get(self, "artifactConfig"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="engineArn")
    def engine_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "engineArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="runConfig")
    def run_config(self) -> "SyntheticsCanaryRunConfigOutputReference":
        return typing.cast("SyntheticsCanaryRunConfigOutputReference", jsii.get(self, "runConfig"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="schedule")
    def schedule(self) -> "SyntheticsCanaryScheduleOutputReference":
        return typing.cast("SyntheticsCanaryScheduleOutputReference", jsii.get(self, "schedule"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceLocationArn")
    def source_location_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceLocationArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcConfig")
    def vpc_config(self) -> "SyntheticsCanaryVpcConfigOutputReference":
        return typing.cast("SyntheticsCanaryVpcConfigOutputReference", jsii.get(self, "vpcConfig"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="artifactConfigInput")
    def artifact_config_input(
        self,
    ) -> typing.Optional["SyntheticsCanaryArtifactConfig"]:
        return typing.cast(typing.Optional["SyntheticsCanaryArtifactConfig"], jsii.get(self, "artifactConfigInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="artifactS3LocationInput")
    def artifact_s3_location_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "artifactS3LocationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="executionRoleArnInput")
    def execution_role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "executionRoleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="failureRetentionPeriodInput")
    def failure_retention_period_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "failureRetentionPeriodInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="handlerInput")
    def handler_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "handlerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="runConfigInput")
    def run_config_input(self) -> typing.Optional["SyntheticsCanaryRunConfig"]:
        return typing.cast(typing.Optional["SyntheticsCanaryRunConfig"], jsii.get(self, "runConfigInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="runtimeVersionInput")
    def runtime_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "runtimeVersionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3BucketInput")
    def s3_bucket_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "s3BucketInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3KeyInput")
    def s3_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "s3KeyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3VersionInput")
    def s3_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "s3VersionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="scheduleInput")
    def schedule_input(self) -> typing.Optional["SyntheticsCanarySchedule"]:
        return typing.cast(typing.Optional["SyntheticsCanarySchedule"], jsii.get(self, "scheduleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="startCanaryInput")
    def start_canary_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "startCanaryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="successRetentionPeriodInput")
    def success_retention_period_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "successRetentionPeriodInput"))

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
    @jsii.member(jsii_name="vpcConfigInput")
    def vpc_config_input(self) -> typing.Optional["SyntheticsCanaryVpcConfig"]:
        return typing.cast(typing.Optional["SyntheticsCanaryVpcConfig"], jsii.get(self, "vpcConfigInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="zipFileInput")
    def zip_file_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "zipFileInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="artifactS3Location")
    def artifact_s3_location(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "artifactS3Location"))

    @artifact_s3_location.setter
    def artifact_s3_location(self, value: builtins.str) -> None:
        jsii.set(self, "artifactS3Location", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="executionRoleArn")
    def execution_role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "executionRoleArn"))

    @execution_role_arn.setter
    def execution_role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "executionRoleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="failureRetentionPeriod")
    def failure_retention_period(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "failureRetentionPeriod"))

    @failure_retention_period.setter
    def failure_retention_period(self, value: jsii.Number) -> None:
        jsii.set(self, "failureRetentionPeriod", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="handler")
    def handler(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "handler"))

    @handler.setter
    def handler(self, value: builtins.str) -> None:
        jsii.set(self, "handler", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="runtimeVersion")
    def runtime_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "runtimeVersion"))

    @runtime_version.setter
    def runtime_version(self, value: builtins.str) -> None:
        jsii.set(self, "runtimeVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3Bucket")
    def s3_bucket(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "s3Bucket"))

    @s3_bucket.setter
    def s3_bucket(self, value: builtins.str) -> None:
        jsii.set(self, "s3Bucket", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3Key")
    def s3_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "s3Key"))

    @s3_key.setter
    def s3_key(self, value: builtins.str) -> None:
        jsii.set(self, "s3Key", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3Version")
    def s3_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "s3Version"))

    @s3_version.setter
    def s3_version(self, value: builtins.str) -> None:
        jsii.set(self, "s3Version", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="startCanary")
    def start_canary(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "startCanary"))

    @start_canary.setter
    def start_canary(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "startCanary", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="successRetentionPeriod")
    def success_retention_period(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "successRetentionPeriod"))

    @success_retention_period.setter
    def success_retention_period(self, value: jsii.Number) -> None:
        jsii.set(self, "successRetentionPeriod", value)

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
    @jsii.member(jsii_name="zipFile")
    def zip_file(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zipFile"))

    @zip_file.setter
    def zip_file(self, value: builtins.str) -> None:
        jsii.set(self, "zipFile", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.synthetics.SyntheticsCanaryArtifactConfig",
    jsii_struct_bases=[],
    name_mapping={"s3_encryption": "s3Encryption"},
)
class SyntheticsCanaryArtifactConfig:
    def __init__(
        self,
        *,
        s3_encryption: typing.Optional["SyntheticsCanaryArtifactConfigS3Encryption"] = None,
    ) -> None:
        '''
        :param s3_encryption: s3_encryption block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#s3_encryption SyntheticsCanary#s3_encryption}
        '''
        if isinstance(s3_encryption, dict):
            s3_encryption = SyntheticsCanaryArtifactConfigS3Encryption(**s3_encryption)
        self._values: typing.Dict[str, typing.Any] = {}
        if s3_encryption is not None:
            self._values["s3_encryption"] = s3_encryption

    @builtins.property
    def s3_encryption(
        self,
    ) -> typing.Optional["SyntheticsCanaryArtifactConfigS3Encryption"]:
        '''s3_encryption block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#s3_encryption SyntheticsCanary#s3_encryption}
        '''
        result = self._values.get("s3_encryption")
        return typing.cast(typing.Optional["SyntheticsCanaryArtifactConfigS3Encryption"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SyntheticsCanaryArtifactConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SyntheticsCanaryArtifactConfigOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.synthetics.SyntheticsCanaryArtifactConfigOutputReference",
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

    @jsii.member(jsii_name="putS3Encryption")
    def put_s3_encryption(
        self,
        *,
        encryption_mode: typing.Optional[builtins.str] = None,
        kms_key_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param encryption_mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#encryption_mode SyntheticsCanary#encryption_mode}.
        :param kms_key_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#kms_key_arn SyntheticsCanary#kms_key_arn}.
        '''
        value = SyntheticsCanaryArtifactConfigS3Encryption(
            encryption_mode=encryption_mode, kms_key_arn=kms_key_arn
        )

        return typing.cast(None, jsii.invoke(self, "putS3Encryption", [value]))

    @jsii.member(jsii_name="resetS3Encryption")
    def reset_s3_encryption(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetS3Encryption", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3Encryption")
    def s3_encryption(
        self,
    ) -> "SyntheticsCanaryArtifactConfigS3EncryptionOutputReference":
        return typing.cast("SyntheticsCanaryArtifactConfigS3EncryptionOutputReference", jsii.get(self, "s3Encryption"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3EncryptionInput")
    def s3_encryption_input(
        self,
    ) -> typing.Optional["SyntheticsCanaryArtifactConfigS3Encryption"]:
        return typing.cast(typing.Optional["SyntheticsCanaryArtifactConfigS3Encryption"], jsii.get(self, "s3EncryptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[SyntheticsCanaryArtifactConfig]:
        return typing.cast(typing.Optional[SyntheticsCanaryArtifactConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[SyntheticsCanaryArtifactConfig],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.synthetics.SyntheticsCanaryArtifactConfigS3Encryption",
    jsii_struct_bases=[],
    name_mapping={"encryption_mode": "encryptionMode", "kms_key_arn": "kmsKeyArn"},
)
class SyntheticsCanaryArtifactConfigS3Encryption:
    def __init__(
        self,
        *,
        encryption_mode: typing.Optional[builtins.str] = None,
        kms_key_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param encryption_mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#encryption_mode SyntheticsCanary#encryption_mode}.
        :param kms_key_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#kms_key_arn SyntheticsCanary#kms_key_arn}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if encryption_mode is not None:
            self._values["encryption_mode"] = encryption_mode
        if kms_key_arn is not None:
            self._values["kms_key_arn"] = kms_key_arn

    @builtins.property
    def encryption_mode(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#encryption_mode SyntheticsCanary#encryption_mode}.'''
        result = self._values.get("encryption_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def kms_key_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#kms_key_arn SyntheticsCanary#kms_key_arn}.'''
        result = self._values.get("kms_key_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SyntheticsCanaryArtifactConfigS3Encryption(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SyntheticsCanaryArtifactConfigS3EncryptionOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.synthetics.SyntheticsCanaryArtifactConfigS3EncryptionOutputReference",
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

    @jsii.member(jsii_name="resetEncryptionMode")
    def reset_encryption_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEncryptionMode", []))

    @jsii.member(jsii_name="resetKmsKeyArn")
    def reset_kms_key_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKmsKeyArn", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptionModeInput")
    def encryption_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "encryptionModeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyArnInput")
    def kms_key_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kmsKeyArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptionMode")
    def encryption_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "encryptionMode"))

    @encryption_mode.setter
    def encryption_mode(self, value: builtins.str) -> None:
        jsii.set(self, "encryptionMode", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyArn")
    def kms_key_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsKeyArn"))

    @kms_key_arn.setter
    def kms_key_arn(self, value: builtins.str) -> None:
        jsii.set(self, "kmsKeyArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[SyntheticsCanaryArtifactConfigS3Encryption]:
        return typing.cast(typing.Optional[SyntheticsCanaryArtifactConfigS3Encryption], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[SyntheticsCanaryArtifactConfigS3Encryption],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.synthetics.SyntheticsCanaryConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "artifact_s3_location": "artifactS3Location",
        "execution_role_arn": "executionRoleArn",
        "handler": "handler",
        "name": "name",
        "runtime_version": "runtimeVersion",
        "schedule": "schedule",
        "artifact_config": "artifactConfig",
        "failure_retention_period": "failureRetentionPeriod",
        "run_config": "runConfig",
        "s3_bucket": "s3Bucket",
        "s3_key": "s3Key",
        "s3_version": "s3Version",
        "start_canary": "startCanary",
        "success_retention_period": "successRetentionPeriod",
        "tags": "tags",
        "tags_all": "tagsAll",
        "vpc_config": "vpcConfig",
        "zip_file": "zipFile",
    },
)
class SyntheticsCanaryConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        artifact_s3_location: builtins.str,
        execution_role_arn: builtins.str,
        handler: builtins.str,
        name: builtins.str,
        runtime_version: builtins.str,
        schedule: "SyntheticsCanarySchedule",
        artifact_config: typing.Optional[SyntheticsCanaryArtifactConfig] = None,
        failure_retention_period: typing.Optional[jsii.Number] = None,
        run_config: typing.Optional["SyntheticsCanaryRunConfig"] = None,
        s3_bucket: typing.Optional[builtins.str] = None,
        s3_key: typing.Optional[builtins.str] = None,
        s3_version: typing.Optional[builtins.str] = None,
        start_canary: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        success_retention_period: typing.Optional[jsii.Number] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        vpc_config: typing.Optional["SyntheticsCanaryVpcConfig"] = None,
        zip_file: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Synthetics.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param artifact_s3_location: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#artifact_s3_location SyntheticsCanary#artifact_s3_location}.
        :param execution_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#execution_role_arn SyntheticsCanary#execution_role_arn}.
        :param handler: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#handler SyntheticsCanary#handler}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#name SyntheticsCanary#name}.
        :param runtime_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#runtime_version SyntheticsCanary#runtime_version}.
        :param schedule: schedule block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#schedule SyntheticsCanary#schedule}
        :param artifact_config: artifact_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#artifact_config SyntheticsCanary#artifact_config}
        :param failure_retention_period: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#failure_retention_period SyntheticsCanary#failure_retention_period}.
        :param run_config: run_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#run_config SyntheticsCanary#run_config}
        :param s3_bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#s3_bucket SyntheticsCanary#s3_bucket}.
        :param s3_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#s3_key SyntheticsCanary#s3_key}.
        :param s3_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#s3_version SyntheticsCanary#s3_version}.
        :param start_canary: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#start_canary SyntheticsCanary#start_canary}.
        :param success_retention_period: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#success_retention_period SyntheticsCanary#success_retention_period}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#tags SyntheticsCanary#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#tags_all SyntheticsCanary#tags_all}.
        :param vpc_config: vpc_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#vpc_config SyntheticsCanary#vpc_config}
        :param zip_file: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#zip_file SyntheticsCanary#zip_file}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(schedule, dict):
            schedule = SyntheticsCanarySchedule(**schedule)
        if isinstance(artifact_config, dict):
            artifact_config = SyntheticsCanaryArtifactConfig(**artifact_config)
        if isinstance(run_config, dict):
            run_config = SyntheticsCanaryRunConfig(**run_config)
        if isinstance(vpc_config, dict):
            vpc_config = SyntheticsCanaryVpcConfig(**vpc_config)
        self._values: typing.Dict[str, typing.Any] = {
            "artifact_s3_location": artifact_s3_location,
            "execution_role_arn": execution_role_arn,
            "handler": handler,
            "name": name,
            "runtime_version": runtime_version,
            "schedule": schedule,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if artifact_config is not None:
            self._values["artifact_config"] = artifact_config
        if failure_retention_period is not None:
            self._values["failure_retention_period"] = failure_retention_period
        if run_config is not None:
            self._values["run_config"] = run_config
        if s3_bucket is not None:
            self._values["s3_bucket"] = s3_bucket
        if s3_key is not None:
            self._values["s3_key"] = s3_key
        if s3_version is not None:
            self._values["s3_version"] = s3_version
        if start_canary is not None:
            self._values["start_canary"] = start_canary
        if success_retention_period is not None:
            self._values["success_retention_period"] = success_retention_period
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if vpc_config is not None:
            self._values["vpc_config"] = vpc_config
        if zip_file is not None:
            self._values["zip_file"] = zip_file

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
    def artifact_s3_location(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#artifact_s3_location SyntheticsCanary#artifact_s3_location}.'''
        result = self._values.get("artifact_s3_location")
        assert result is not None, "Required property 'artifact_s3_location' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def execution_role_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#execution_role_arn SyntheticsCanary#execution_role_arn}.'''
        result = self._values.get("execution_role_arn")
        assert result is not None, "Required property 'execution_role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def handler(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#handler SyntheticsCanary#handler}.'''
        result = self._values.get("handler")
        assert result is not None, "Required property 'handler' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#name SyntheticsCanary#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def runtime_version(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#runtime_version SyntheticsCanary#runtime_version}.'''
        result = self._values.get("runtime_version")
        assert result is not None, "Required property 'runtime_version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def schedule(self) -> "SyntheticsCanarySchedule":
        '''schedule block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#schedule SyntheticsCanary#schedule}
        '''
        result = self._values.get("schedule")
        assert result is not None, "Required property 'schedule' is missing"
        return typing.cast("SyntheticsCanarySchedule", result)

    @builtins.property
    def artifact_config(self) -> typing.Optional[SyntheticsCanaryArtifactConfig]:
        '''artifact_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#artifact_config SyntheticsCanary#artifact_config}
        '''
        result = self._values.get("artifact_config")
        return typing.cast(typing.Optional[SyntheticsCanaryArtifactConfig], result)

    @builtins.property
    def failure_retention_period(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#failure_retention_period SyntheticsCanary#failure_retention_period}.'''
        result = self._values.get("failure_retention_period")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def run_config(self) -> typing.Optional["SyntheticsCanaryRunConfig"]:
        '''run_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#run_config SyntheticsCanary#run_config}
        '''
        result = self._values.get("run_config")
        return typing.cast(typing.Optional["SyntheticsCanaryRunConfig"], result)

    @builtins.property
    def s3_bucket(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#s3_bucket SyntheticsCanary#s3_bucket}.'''
        result = self._values.get("s3_bucket")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def s3_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#s3_key SyntheticsCanary#s3_key}.'''
        result = self._values.get("s3_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def s3_version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#s3_version SyntheticsCanary#s3_version}.'''
        result = self._values.get("s3_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def start_canary(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#start_canary SyntheticsCanary#start_canary}.'''
        result = self._values.get("start_canary")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def success_retention_period(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#success_retention_period SyntheticsCanary#success_retention_period}.'''
        result = self._values.get("success_retention_period")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#tags SyntheticsCanary#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#tags_all SyntheticsCanary#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def vpc_config(self) -> typing.Optional["SyntheticsCanaryVpcConfig"]:
        '''vpc_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#vpc_config SyntheticsCanary#vpc_config}
        '''
        result = self._values.get("vpc_config")
        return typing.cast(typing.Optional["SyntheticsCanaryVpcConfig"], result)

    @builtins.property
    def zip_file(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#zip_file SyntheticsCanary#zip_file}.'''
        result = self._values.get("zip_file")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SyntheticsCanaryConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.synthetics.SyntheticsCanaryRunConfig",
    jsii_struct_bases=[],
    name_mapping={
        "active_tracing": "activeTracing",
        "memory_in_mb": "memoryInMb",
        "timeout_in_seconds": "timeoutInSeconds",
    },
)
class SyntheticsCanaryRunConfig:
    def __init__(
        self,
        *,
        active_tracing: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        memory_in_mb: typing.Optional[jsii.Number] = None,
        timeout_in_seconds: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param active_tracing: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#active_tracing SyntheticsCanary#active_tracing}.
        :param memory_in_mb: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#memory_in_mb SyntheticsCanary#memory_in_mb}.
        :param timeout_in_seconds: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#timeout_in_seconds SyntheticsCanary#timeout_in_seconds}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if active_tracing is not None:
            self._values["active_tracing"] = active_tracing
        if memory_in_mb is not None:
            self._values["memory_in_mb"] = memory_in_mb
        if timeout_in_seconds is not None:
            self._values["timeout_in_seconds"] = timeout_in_seconds

    @builtins.property
    def active_tracing(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#active_tracing SyntheticsCanary#active_tracing}.'''
        result = self._values.get("active_tracing")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def memory_in_mb(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#memory_in_mb SyntheticsCanary#memory_in_mb}.'''
        result = self._values.get("memory_in_mb")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def timeout_in_seconds(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#timeout_in_seconds SyntheticsCanary#timeout_in_seconds}.'''
        result = self._values.get("timeout_in_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SyntheticsCanaryRunConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SyntheticsCanaryRunConfigOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.synthetics.SyntheticsCanaryRunConfigOutputReference",
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

    @jsii.member(jsii_name="resetActiveTracing")
    def reset_active_tracing(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetActiveTracing", []))

    @jsii.member(jsii_name="resetMemoryInMb")
    def reset_memory_in_mb(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMemoryInMb", []))

    @jsii.member(jsii_name="resetTimeoutInSeconds")
    def reset_timeout_in_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeoutInSeconds", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="activeTracingInput")
    def active_tracing_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "activeTracingInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="memoryInMbInput")
    def memory_in_mb_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "memoryInMbInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutInSecondsInput")
    def timeout_in_seconds_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "timeoutInSecondsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="activeTracing")
    def active_tracing(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "activeTracing"))

    @active_tracing.setter
    def active_tracing(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "activeTracing", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="memoryInMb")
    def memory_in_mb(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "memoryInMb"))

    @memory_in_mb.setter
    def memory_in_mb(self, value: jsii.Number) -> None:
        jsii.set(self, "memoryInMb", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutInSeconds")
    def timeout_in_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "timeoutInSeconds"))

    @timeout_in_seconds.setter
    def timeout_in_seconds(self, value: jsii.Number) -> None:
        jsii.set(self, "timeoutInSeconds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[SyntheticsCanaryRunConfig]:
        return typing.cast(typing.Optional[SyntheticsCanaryRunConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[SyntheticsCanaryRunConfig]) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.synthetics.SyntheticsCanarySchedule",
    jsii_struct_bases=[],
    name_mapping={
        "expression": "expression",
        "duration_in_seconds": "durationInSeconds",
    },
)
class SyntheticsCanarySchedule:
    def __init__(
        self,
        *,
        expression: builtins.str,
        duration_in_seconds: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param expression: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#expression SyntheticsCanary#expression}.
        :param duration_in_seconds: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#duration_in_seconds SyntheticsCanary#duration_in_seconds}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "expression": expression,
        }
        if duration_in_seconds is not None:
            self._values["duration_in_seconds"] = duration_in_seconds

    @builtins.property
    def expression(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#expression SyntheticsCanary#expression}.'''
        result = self._values.get("expression")
        assert result is not None, "Required property 'expression' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def duration_in_seconds(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#duration_in_seconds SyntheticsCanary#duration_in_seconds}.'''
        result = self._values.get("duration_in_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SyntheticsCanarySchedule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SyntheticsCanaryScheduleOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.synthetics.SyntheticsCanaryScheduleOutputReference",
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

    @jsii.member(jsii_name="resetDurationInSeconds")
    def reset_duration_in_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDurationInSeconds", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="durationInSecondsInput")
    def duration_in_seconds_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "durationInSecondsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="expressionInput")
    def expression_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "expressionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="durationInSeconds")
    def duration_in_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "durationInSeconds"))

    @duration_in_seconds.setter
    def duration_in_seconds(self, value: jsii.Number) -> None:
        jsii.set(self, "durationInSeconds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="expression")
    def expression(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "expression"))

    @expression.setter
    def expression(self, value: builtins.str) -> None:
        jsii.set(self, "expression", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[SyntheticsCanarySchedule]:
        return typing.cast(typing.Optional[SyntheticsCanarySchedule], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[SyntheticsCanarySchedule]) -> None:
        jsii.set(self, "internalValue", value)


class SyntheticsCanaryTimeline(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.synthetics.SyntheticsCanaryTimeline",
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
    @jsii.member(jsii_name="created")
    def created(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "created"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lastModified")
    def last_modified(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lastModified"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lastStarted")
    def last_started(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lastStarted"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lastStopped")
    def last_stopped(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lastStopped"))


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.synthetics.SyntheticsCanaryVpcConfig",
    jsii_struct_bases=[],
    name_mapping={"security_group_ids": "securityGroupIds", "subnet_ids": "subnetIds"},
)
class SyntheticsCanaryVpcConfig:
    def __init__(
        self,
        *,
        security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        subnet_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param security_group_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#security_group_ids SyntheticsCanary#security_group_ids}.
        :param subnet_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#subnet_ids SyntheticsCanary#subnet_ids}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if security_group_ids is not None:
            self._values["security_group_ids"] = security_group_ids
        if subnet_ids is not None:
            self._values["subnet_ids"] = subnet_ids

    @builtins.property
    def security_group_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#security_group_ids SyntheticsCanary#security_group_ids}.'''
        result = self._values.get("security_group_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def subnet_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/synthetics_canary#subnet_ids SyntheticsCanary#subnet_ids}.'''
        result = self._values.get("subnet_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SyntheticsCanaryVpcConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SyntheticsCanaryVpcConfigOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.synthetics.SyntheticsCanaryVpcConfigOutputReference",
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

    @jsii.member(jsii_name="resetSecurityGroupIds")
    def reset_security_group_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecurityGroupIds", []))

    @jsii.member(jsii_name="resetSubnetIds")
    def reset_subnet_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSubnetIds", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroupIdsInput")
    def security_group_ids_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "securityGroupIdsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnetIdsInput")
    def subnet_ids_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "subnetIdsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroupIds")
    def security_group_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "securityGroupIds"))

    @security_group_ids.setter
    def security_group_ids(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "securityGroupIds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnetIds")
    def subnet_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "subnetIds"))

    @subnet_ids.setter
    def subnet_ids(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "subnetIds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[SyntheticsCanaryVpcConfig]:
        return typing.cast(typing.Optional[SyntheticsCanaryVpcConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[SyntheticsCanaryVpcConfig]) -> None:
        jsii.set(self, "internalValue", value)


__all__ = [
    "SyntheticsCanary",
    "SyntheticsCanaryArtifactConfig",
    "SyntheticsCanaryArtifactConfigOutputReference",
    "SyntheticsCanaryArtifactConfigS3Encryption",
    "SyntheticsCanaryArtifactConfigS3EncryptionOutputReference",
    "SyntheticsCanaryConfig",
    "SyntheticsCanaryRunConfig",
    "SyntheticsCanaryRunConfigOutputReference",
    "SyntheticsCanarySchedule",
    "SyntheticsCanaryScheduleOutputReference",
    "SyntheticsCanaryTimeline",
    "SyntheticsCanaryVpcConfig",
    "SyntheticsCanaryVpcConfigOutputReference",
]

publication.publish()
