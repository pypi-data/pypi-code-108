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


class DataAwsGuarddutyDetector(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.guardduty.DataAwsGuarddutyDetector",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/guardduty_detector aws_guardduty_detector}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/guardduty_detector aws_guardduty_detector} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsGuarddutyDetectorConfig(
            count=count, depends_on=depends_on, lifecycle=lifecycle, provider=provider
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
    @jsii.member(jsii_name="findingPublishingFrequency")
    def finding_publishing_frequency(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "findingPublishingFrequency"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceRoleArn")
    def service_role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceRoleArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.guardduty.DataAwsGuarddutyDetectorConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
    },
)
class DataAwsGuarddutyDetectorConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''AWS GuardDuty.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
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

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsGuarddutyDetectorConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GuarddutyDetector(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.guardduty.GuarddutyDetector",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/guardduty_detector aws_guardduty_detector}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        datasources: typing.Optional["GuarddutyDetectorDatasources"] = None,
        enable: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        finding_publishing_frequency: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/guardduty_detector aws_guardduty_detector} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param datasources: datasources block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_detector#datasources GuarddutyDetector#datasources}
        :param enable: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_detector#enable GuarddutyDetector#enable}.
        :param finding_publishing_frequency: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_detector#finding_publishing_frequency GuarddutyDetector#finding_publishing_frequency}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_detector#tags GuarddutyDetector#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_detector#tags_all GuarddutyDetector#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = GuarddutyDetectorConfig(
            datasources=datasources,
            enable=enable,
            finding_publishing_frequency=finding_publishing_frequency,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putDatasources")
    def put_datasources(
        self,
        *,
        s3_logs: typing.Optional["GuarddutyDetectorDatasourcesS3Logs"] = None,
    ) -> None:
        '''
        :param s3_logs: s3_logs block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_detector#s3_logs GuarddutyDetector#s3_logs}
        '''
        value = GuarddutyDetectorDatasources(s3_logs=s3_logs)

        return typing.cast(None, jsii.invoke(self, "putDatasources", [value]))

    @jsii.member(jsii_name="resetDatasources")
    def reset_datasources(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDatasources", []))

    @jsii.member(jsii_name="resetEnable")
    def reset_enable(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnable", []))

    @jsii.member(jsii_name="resetFindingPublishingFrequency")
    def reset_finding_publishing_frequency(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFindingPublishingFrequency", []))

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
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="datasources")
    def datasources(self) -> "GuarddutyDetectorDatasourcesOutputReference":
        return typing.cast("GuarddutyDetectorDatasourcesOutputReference", jsii.get(self, "datasources"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="datasourcesInput")
    def datasources_input(self) -> typing.Optional["GuarddutyDetectorDatasources"]:
        return typing.cast(typing.Optional["GuarddutyDetectorDatasources"], jsii.get(self, "datasourcesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableInput")
    def enable_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enableInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="findingPublishingFrequencyInput")
    def finding_publishing_frequency_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "findingPublishingFrequencyInput"))

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
    @jsii.member(jsii_name="enable")
    def enable(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enable"))

    @enable.setter
    def enable(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "enable", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="findingPublishingFrequency")
    def finding_publishing_frequency(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "findingPublishingFrequency"))

    @finding_publishing_frequency.setter
    def finding_publishing_frequency(self, value: builtins.str) -> None:
        jsii.set(self, "findingPublishingFrequency", value)

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
    jsii_type="@cdktf/provider-aws.guardduty.GuarddutyDetectorConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "datasources": "datasources",
        "enable": "enable",
        "finding_publishing_frequency": "findingPublishingFrequency",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class GuarddutyDetectorConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        datasources: typing.Optional["GuarddutyDetectorDatasources"] = None,
        enable: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        finding_publishing_frequency: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS GuardDuty.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param datasources: datasources block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_detector#datasources GuarddutyDetector#datasources}
        :param enable: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_detector#enable GuarddutyDetector#enable}.
        :param finding_publishing_frequency: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_detector#finding_publishing_frequency GuarddutyDetector#finding_publishing_frequency}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_detector#tags GuarddutyDetector#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_detector#tags_all GuarddutyDetector#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(datasources, dict):
            datasources = GuarddutyDetectorDatasources(**datasources)
        self._values: typing.Dict[str, typing.Any] = {}
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if datasources is not None:
            self._values["datasources"] = datasources
        if enable is not None:
            self._values["enable"] = enable
        if finding_publishing_frequency is not None:
            self._values["finding_publishing_frequency"] = finding_publishing_frequency
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
    def datasources(self) -> typing.Optional["GuarddutyDetectorDatasources"]:
        '''datasources block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_detector#datasources GuarddutyDetector#datasources}
        '''
        result = self._values.get("datasources")
        return typing.cast(typing.Optional["GuarddutyDetectorDatasources"], result)

    @builtins.property
    def enable(self) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_detector#enable GuarddutyDetector#enable}.'''
        result = self._values.get("enable")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def finding_publishing_frequency(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_detector#finding_publishing_frequency GuarddutyDetector#finding_publishing_frequency}.'''
        result = self._values.get("finding_publishing_frequency")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_detector#tags GuarddutyDetector#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_detector#tags_all GuarddutyDetector#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GuarddutyDetectorConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.guardduty.GuarddutyDetectorDatasources",
    jsii_struct_bases=[],
    name_mapping={"s3_logs": "s3Logs"},
)
class GuarddutyDetectorDatasources:
    def __init__(
        self,
        *,
        s3_logs: typing.Optional["GuarddutyDetectorDatasourcesS3Logs"] = None,
    ) -> None:
        '''
        :param s3_logs: s3_logs block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_detector#s3_logs GuarddutyDetector#s3_logs}
        '''
        if isinstance(s3_logs, dict):
            s3_logs = GuarddutyDetectorDatasourcesS3Logs(**s3_logs)
        self._values: typing.Dict[str, typing.Any] = {}
        if s3_logs is not None:
            self._values["s3_logs"] = s3_logs

    @builtins.property
    def s3_logs(self) -> typing.Optional["GuarddutyDetectorDatasourcesS3Logs"]:
        '''s3_logs block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_detector#s3_logs GuarddutyDetector#s3_logs}
        '''
        result = self._values.get("s3_logs")
        return typing.cast(typing.Optional["GuarddutyDetectorDatasourcesS3Logs"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GuarddutyDetectorDatasources(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GuarddutyDetectorDatasourcesOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.guardduty.GuarddutyDetectorDatasourcesOutputReference",
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

    @jsii.member(jsii_name="putS3Logs")
    def put_s3_logs(
        self,
        *,
        enable: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        '''
        :param enable: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_detector#enable GuarddutyDetector#enable}.
        '''
        value = GuarddutyDetectorDatasourcesS3Logs(enable=enable)

        return typing.cast(None, jsii.invoke(self, "putS3Logs", [value]))

    @jsii.member(jsii_name="resetS3Logs")
    def reset_s3_logs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetS3Logs", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3Logs")
    def s3_logs(self) -> "GuarddutyDetectorDatasourcesS3LogsOutputReference":
        return typing.cast("GuarddutyDetectorDatasourcesS3LogsOutputReference", jsii.get(self, "s3Logs"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3LogsInput")
    def s3_logs_input(self) -> typing.Optional["GuarddutyDetectorDatasourcesS3Logs"]:
        return typing.cast(typing.Optional["GuarddutyDetectorDatasourcesS3Logs"], jsii.get(self, "s3LogsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[GuarddutyDetectorDatasources]:
        return typing.cast(typing.Optional[GuarddutyDetectorDatasources], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GuarddutyDetectorDatasources],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.guardduty.GuarddutyDetectorDatasourcesS3Logs",
    jsii_struct_bases=[],
    name_mapping={"enable": "enable"},
)
class GuarddutyDetectorDatasourcesS3Logs:
    def __init__(
        self,
        *,
        enable: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        '''
        :param enable: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_detector#enable GuarddutyDetector#enable}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "enable": enable,
        }

    @builtins.property
    def enable(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_detector#enable GuarddutyDetector#enable}.'''
        result = self._values.get("enable")
        assert result is not None, "Required property 'enable' is missing"
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GuarddutyDetectorDatasourcesS3Logs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GuarddutyDetectorDatasourcesS3LogsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.guardduty.GuarddutyDetectorDatasourcesS3LogsOutputReference",
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
    @jsii.member(jsii_name="enableInput")
    def enable_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enableInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enable")
    def enable(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enable"))

    @enable.setter
    def enable(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "enable", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[GuarddutyDetectorDatasourcesS3Logs]:
        return typing.cast(typing.Optional[GuarddutyDetectorDatasourcesS3Logs], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GuarddutyDetectorDatasourcesS3Logs],
    ) -> None:
        jsii.set(self, "internalValue", value)


class GuarddutyFilter(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.guardduty.GuarddutyFilter",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/guardduty_filter aws_guardduty_filter}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        action: builtins.str,
        detector_id: builtins.str,
        finding_criteria: "GuarddutyFilterFindingCriteria",
        name: builtins.str,
        rank: jsii.Number,
        description: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/guardduty_filter aws_guardduty_filter} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param action: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_filter#action GuarddutyFilter#action}.
        :param detector_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_filter#detector_id GuarddutyFilter#detector_id}.
        :param finding_criteria: finding_criteria block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_filter#finding_criteria GuarddutyFilter#finding_criteria}
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_filter#name GuarddutyFilter#name}.
        :param rank: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_filter#rank GuarddutyFilter#rank}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_filter#description GuarddutyFilter#description}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_filter#tags GuarddutyFilter#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_filter#tags_all GuarddutyFilter#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = GuarddutyFilterConfig(
            action=action,
            detector_id=detector_id,
            finding_criteria=finding_criteria,
            name=name,
            rank=rank,
            description=description,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putFindingCriteria")
    def put_finding_criteria(
        self,
        *,
        criterion: typing.Sequence["GuarddutyFilterFindingCriteriaCriterion"],
    ) -> None:
        '''
        :param criterion: criterion block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_filter#criterion GuarddutyFilter#criterion}
        '''
        value = GuarddutyFilterFindingCriteria(criterion=criterion)

        return typing.cast(None, jsii.invoke(self, "putFindingCriteria", [value]))

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
    @jsii.member(jsii_name="findingCriteria")
    def finding_criteria(self) -> "GuarddutyFilterFindingCriteriaOutputReference":
        return typing.cast("GuarddutyFilterFindingCriteriaOutputReference", jsii.get(self, "findingCriteria"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="actionInput")
    def action_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "actionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="detectorIdInput")
    def detector_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "detectorIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="findingCriteriaInput")
    def finding_criteria_input(
        self,
    ) -> typing.Optional["GuarddutyFilterFindingCriteria"]:
        return typing.cast(typing.Optional["GuarddutyFilterFindingCriteria"], jsii.get(self, "findingCriteriaInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rankInput")
    def rank_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "rankInput"))

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
    @jsii.member(jsii_name="action")
    def action(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "action"))

    @action.setter
    def action(self, value: builtins.str) -> None:
        jsii.set(self, "action", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="detectorId")
    def detector_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "detectorId"))

    @detector_id.setter
    def detector_id(self, value: builtins.str) -> None:
        jsii.set(self, "detectorId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rank")
    def rank(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "rank"))

    @rank.setter
    def rank(self, value: jsii.Number) -> None:
        jsii.set(self, "rank", value)

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
    jsii_type="@cdktf/provider-aws.guardduty.GuarddutyFilterConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "action": "action",
        "detector_id": "detectorId",
        "finding_criteria": "findingCriteria",
        "name": "name",
        "rank": "rank",
        "description": "description",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class GuarddutyFilterConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        action: builtins.str,
        detector_id: builtins.str,
        finding_criteria: "GuarddutyFilterFindingCriteria",
        name: builtins.str,
        rank: jsii.Number,
        description: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS GuardDuty.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param action: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_filter#action GuarddutyFilter#action}.
        :param detector_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_filter#detector_id GuarddutyFilter#detector_id}.
        :param finding_criteria: finding_criteria block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_filter#finding_criteria GuarddutyFilter#finding_criteria}
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_filter#name GuarddutyFilter#name}.
        :param rank: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_filter#rank GuarddutyFilter#rank}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_filter#description GuarddutyFilter#description}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_filter#tags GuarddutyFilter#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_filter#tags_all GuarddutyFilter#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(finding_criteria, dict):
            finding_criteria = GuarddutyFilterFindingCriteria(**finding_criteria)
        self._values: typing.Dict[str, typing.Any] = {
            "action": action,
            "detector_id": detector_id,
            "finding_criteria": finding_criteria,
            "name": name,
            "rank": rank,
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
    def action(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_filter#action GuarddutyFilter#action}.'''
        result = self._values.get("action")
        assert result is not None, "Required property 'action' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def detector_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_filter#detector_id GuarddutyFilter#detector_id}.'''
        result = self._values.get("detector_id")
        assert result is not None, "Required property 'detector_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def finding_criteria(self) -> "GuarddutyFilterFindingCriteria":
        '''finding_criteria block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_filter#finding_criteria GuarddutyFilter#finding_criteria}
        '''
        result = self._values.get("finding_criteria")
        assert result is not None, "Required property 'finding_criteria' is missing"
        return typing.cast("GuarddutyFilterFindingCriteria", result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_filter#name GuarddutyFilter#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def rank(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_filter#rank GuarddutyFilter#rank}.'''
        result = self._values.get("rank")
        assert result is not None, "Required property 'rank' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_filter#description GuarddutyFilter#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_filter#tags GuarddutyFilter#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_filter#tags_all GuarddutyFilter#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GuarddutyFilterConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.guardduty.GuarddutyFilterFindingCriteria",
    jsii_struct_bases=[],
    name_mapping={"criterion": "criterion"},
)
class GuarddutyFilterFindingCriteria:
    def __init__(
        self,
        *,
        criterion: typing.Sequence["GuarddutyFilterFindingCriteriaCriterion"],
    ) -> None:
        '''
        :param criterion: criterion block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_filter#criterion GuarddutyFilter#criterion}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "criterion": criterion,
        }

    @builtins.property
    def criterion(self) -> typing.List["GuarddutyFilterFindingCriteriaCriterion"]:
        '''criterion block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_filter#criterion GuarddutyFilter#criterion}
        '''
        result = self._values.get("criterion")
        assert result is not None, "Required property 'criterion' is missing"
        return typing.cast(typing.List["GuarddutyFilterFindingCriteriaCriterion"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GuarddutyFilterFindingCriteria(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.guardduty.GuarddutyFilterFindingCriteriaCriterion",
    jsii_struct_bases=[],
    name_mapping={
        "field": "field",
        "equal_to": "equalTo",
        "greater_than": "greaterThan",
        "greater_than_or_equal": "greaterThanOrEqual",
        "less_than": "lessThan",
        "less_than_or_equal": "lessThanOrEqual",
        "not_equals": "notEquals",
    },
)
class GuarddutyFilterFindingCriteriaCriterion:
    def __init__(
        self,
        *,
        field: builtins.str,
        equal_to: typing.Optional[typing.Sequence[builtins.str]] = None,
        greater_than: typing.Optional[builtins.str] = None,
        greater_than_or_equal: typing.Optional[builtins.str] = None,
        less_than: typing.Optional[builtins.str] = None,
        less_than_or_equal: typing.Optional[builtins.str] = None,
        not_equals: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param field: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_filter#field GuarddutyFilter#field}.
        :param equal_to: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_filter#equals GuarddutyFilter#equals}.
        :param greater_than: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_filter#greater_than GuarddutyFilter#greater_than}.
        :param greater_than_or_equal: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_filter#greater_than_or_equal GuarddutyFilter#greater_than_or_equal}.
        :param less_than: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_filter#less_than GuarddutyFilter#less_than}.
        :param less_than_or_equal: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_filter#less_than_or_equal GuarddutyFilter#less_than_or_equal}.
        :param not_equals: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_filter#not_equals GuarddutyFilter#not_equals}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "field": field,
        }
        if equal_to is not None:
            self._values["equal_to"] = equal_to
        if greater_than is not None:
            self._values["greater_than"] = greater_than
        if greater_than_or_equal is not None:
            self._values["greater_than_or_equal"] = greater_than_or_equal
        if less_than is not None:
            self._values["less_than"] = less_than
        if less_than_or_equal is not None:
            self._values["less_than_or_equal"] = less_than_or_equal
        if not_equals is not None:
            self._values["not_equals"] = not_equals

    @builtins.property
    def field(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_filter#field GuarddutyFilter#field}.'''
        result = self._values.get("field")
        assert result is not None, "Required property 'field' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def equal_to(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_filter#equals GuarddutyFilter#equals}.'''
        result = self._values.get("equal_to")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def greater_than(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_filter#greater_than GuarddutyFilter#greater_than}.'''
        result = self._values.get("greater_than")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def greater_than_or_equal(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_filter#greater_than_or_equal GuarddutyFilter#greater_than_or_equal}.'''
        result = self._values.get("greater_than_or_equal")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def less_than(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_filter#less_than GuarddutyFilter#less_than}.'''
        result = self._values.get("less_than")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def less_than_or_equal(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_filter#less_than_or_equal GuarddutyFilter#less_than_or_equal}.'''
        result = self._values.get("less_than_or_equal")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def not_equals(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_filter#not_equals GuarddutyFilter#not_equals}.'''
        result = self._values.get("not_equals")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GuarddutyFilterFindingCriteriaCriterion(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GuarddutyFilterFindingCriteriaOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.guardduty.GuarddutyFilterFindingCriteriaOutputReference",
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
    @jsii.member(jsii_name="criterionInput")
    def criterion_input(
        self,
    ) -> typing.Optional[typing.List[GuarddutyFilterFindingCriteriaCriterion]]:
        return typing.cast(typing.Optional[typing.List[GuarddutyFilterFindingCriteriaCriterion]], jsii.get(self, "criterionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="criterion")
    def criterion(self) -> typing.List[GuarddutyFilterFindingCriteriaCriterion]:
        return typing.cast(typing.List[GuarddutyFilterFindingCriteriaCriterion], jsii.get(self, "criterion"))

    @criterion.setter
    def criterion(
        self,
        value: typing.List[GuarddutyFilterFindingCriteriaCriterion],
    ) -> None:
        jsii.set(self, "criterion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[GuarddutyFilterFindingCriteria]:
        return typing.cast(typing.Optional[GuarddutyFilterFindingCriteria], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GuarddutyFilterFindingCriteria],
    ) -> None:
        jsii.set(self, "internalValue", value)


class GuarddutyInviteAccepter(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.guardduty.GuarddutyInviteAccepter",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/guardduty_invite_accepter aws_guardduty_invite_accepter}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        detector_id: builtins.str,
        master_account_id: builtins.str,
        timeouts: typing.Optional["GuarddutyInviteAccepterTimeouts"] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/guardduty_invite_accepter aws_guardduty_invite_accepter} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param detector_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_invite_accepter#detector_id GuarddutyInviteAccepter#detector_id}.
        :param master_account_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_invite_accepter#master_account_id GuarddutyInviteAccepter#master_account_id}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_invite_accepter#timeouts GuarddutyInviteAccepter#timeouts}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = GuarddutyInviteAccepterConfig(
            detector_id=detector_id,
            master_account_id=master_account_id,
            timeouts=timeouts,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(self, *, create: typing.Optional[builtins.str] = None) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_invite_accepter#create GuarddutyInviteAccepter#create}.
        '''
        value = GuarddutyInviteAccepterTimeouts(create=create)

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

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
    def timeouts(self) -> "GuarddutyInviteAccepterTimeoutsOutputReference":
        return typing.cast("GuarddutyInviteAccepterTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="detectorIdInput")
    def detector_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "detectorIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="masterAccountIdInput")
    def master_account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "masterAccountIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(self) -> typing.Optional["GuarddutyInviteAccepterTimeouts"]:
        return typing.cast(typing.Optional["GuarddutyInviteAccepterTimeouts"], jsii.get(self, "timeoutsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="detectorId")
    def detector_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "detectorId"))

    @detector_id.setter
    def detector_id(self, value: builtins.str) -> None:
        jsii.set(self, "detectorId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="masterAccountId")
    def master_account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "masterAccountId"))

    @master_account_id.setter
    def master_account_id(self, value: builtins.str) -> None:
        jsii.set(self, "masterAccountId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.guardduty.GuarddutyInviteAccepterConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "detector_id": "detectorId",
        "master_account_id": "masterAccountId",
        "timeouts": "timeouts",
    },
)
class GuarddutyInviteAccepterConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        detector_id: builtins.str,
        master_account_id: builtins.str,
        timeouts: typing.Optional["GuarddutyInviteAccepterTimeouts"] = None,
    ) -> None:
        '''AWS GuardDuty.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param detector_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_invite_accepter#detector_id GuarddutyInviteAccepter#detector_id}.
        :param master_account_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_invite_accepter#master_account_id GuarddutyInviteAccepter#master_account_id}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_invite_accepter#timeouts GuarddutyInviteAccepter#timeouts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(timeouts, dict):
            timeouts = GuarddutyInviteAccepterTimeouts(**timeouts)
        self._values: typing.Dict[str, typing.Any] = {
            "detector_id": detector_id,
            "master_account_id": master_account_id,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
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
    def detector_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_invite_accepter#detector_id GuarddutyInviteAccepter#detector_id}.'''
        result = self._values.get("detector_id")
        assert result is not None, "Required property 'detector_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def master_account_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_invite_accepter#master_account_id GuarddutyInviteAccepter#master_account_id}.'''
        result = self._values.get("master_account_id")
        assert result is not None, "Required property 'master_account_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def timeouts(self) -> typing.Optional["GuarddutyInviteAccepterTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_invite_accepter#timeouts GuarddutyInviteAccepter#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["GuarddutyInviteAccepterTimeouts"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GuarddutyInviteAccepterConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.guardduty.GuarddutyInviteAccepterTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create"},
)
class GuarddutyInviteAccepterTimeouts:
    def __init__(self, *, create: typing.Optional[builtins.str] = None) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_invite_accepter#create GuarddutyInviteAccepter#create}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if create is not None:
            self._values["create"] = create

    @builtins.property
    def create(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_invite_accepter#create GuarddutyInviteAccepter#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GuarddutyInviteAccepterTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GuarddutyInviteAccepterTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.guardduty.GuarddutyInviteAccepterTimeoutsOutputReference",
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
    def internal_value(self) -> typing.Optional[GuarddutyInviteAccepterTimeouts]:
        return typing.cast(typing.Optional[GuarddutyInviteAccepterTimeouts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GuarddutyInviteAccepterTimeouts],
    ) -> None:
        jsii.set(self, "internalValue", value)


class GuarddutyIpset(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.guardduty.GuarddutyIpset",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/guardduty_ipset aws_guardduty_ipset}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        activate: typing.Union[builtins.bool, cdktf.IResolvable],
        detector_id: builtins.str,
        format: builtins.str,
        location: builtins.str,
        name: builtins.str,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/guardduty_ipset aws_guardduty_ipset} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param activate: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_ipset#activate GuarddutyIpset#activate}.
        :param detector_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_ipset#detector_id GuarddutyIpset#detector_id}.
        :param format: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_ipset#format GuarddutyIpset#format}.
        :param location: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_ipset#location GuarddutyIpset#location}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_ipset#name GuarddutyIpset#name}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_ipset#tags GuarddutyIpset#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_ipset#tags_all GuarddutyIpset#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = GuarddutyIpsetConfig(
            activate=activate,
            detector_id=detector_id,
            format=format,
            location=location,
            name=name,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

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
    @jsii.member(jsii_name="activateInput")
    def activate_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "activateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="detectorIdInput")
    def detector_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "detectorIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="formatInput")
    def format_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "formatInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="locationInput")
    def location_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "locationInput"))

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
    @jsii.member(jsii_name="activate")
    def activate(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "activate"))

    @activate.setter
    def activate(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "activate", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="detectorId")
    def detector_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "detectorId"))

    @detector_id.setter
    def detector_id(self, value: builtins.str) -> None:
        jsii.set(self, "detectorId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="format")
    def format(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "format"))

    @format.setter
    def format(self, value: builtins.str) -> None:
        jsii.set(self, "format", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="location")
    def location(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "location"))

    @location.setter
    def location(self, value: builtins.str) -> None:
        jsii.set(self, "location", value)

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
    jsii_type="@cdktf/provider-aws.guardduty.GuarddutyIpsetConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "activate": "activate",
        "detector_id": "detectorId",
        "format": "format",
        "location": "location",
        "name": "name",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class GuarddutyIpsetConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        activate: typing.Union[builtins.bool, cdktf.IResolvable],
        detector_id: builtins.str,
        format: builtins.str,
        location: builtins.str,
        name: builtins.str,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS GuardDuty.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param activate: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_ipset#activate GuarddutyIpset#activate}.
        :param detector_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_ipset#detector_id GuarddutyIpset#detector_id}.
        :param format: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_ipset#format GuarddutyIpset#format}.
        :param location: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_ipset#location GuarddutyIpset#location}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_ipset#name GuarddutyIpset#name}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_ipset#tags GuarddutyIpset#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_ipset#tags_all GuarddutyIpset#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "activate": activate,
            "detector_id": detector_id,
            "format": format,
            "location": location,
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
    def activate(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_ipset#activate GuarddutyIpset#activate}.'''
        result = self._values.get("activate")
        assert result is not None, "Required property 'activate' is missing"
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], result)

    @builtins.property
    def detector_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_ipset#detector_id GuarddutyIpset#detector_id}.'''
        result = self._values.get("detector_id")
        assert result is not None, "Required property 'detector_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def format(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_ipset#format GuarddutyIpset#format}.'''
        result = self._values.get("format")
        assert result is not None, "Required property 'format' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def location(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_ipset#location GuarddutyIpset#location}.'''
        result = self._values.get("location")
        assert result is not None, "Required property 'location' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_ipset#name GuarddutyIpset#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_ipset#tags GuarddutyIpset#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_ipset#tags_all GuarddutyIpset#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GuarddutyIpsetConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GuarddutyMember(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.guardduty.GuarddutyMember",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/guardduty_member aws_guardduty_member}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        account_id: builtins.str,
        detector_id: builtins.str,
        email: builtins.str,
        disable_email_notification: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        invitation_message: typing.Optional[builtins.str] = None,
        invite: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        timeouts: typing.Optional["GuarddutyMemberTimeouts"] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/guardduty_member aws_guardduty_member} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param account_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_member#account_id GuarddutyMember#account_id}.
        :param detector_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_member#detector_id GuarddutyMember#detector_id}.
        :param email: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_member#email GuarddutyMember#email}.
        :param disable_email_notification: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_member#disable_email_notification GuarddutyMember#disable_email_notification}.
        :param invitation_message: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_member#invitation_message GuarddutyMember#invitation_message}.
        :param invite: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_member#invite GuarddutyMember#invite}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_member#timeouts GuarddutyMember#timeouts}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = GuarddutyMemberConfig(
            account_id=account_id,
            detector_id=detector_id,
            email=email,
            disable_email_notification=disable_email_notification,
            invitation_message=invitation_message,
            invite=invite,
            timeouts=timeouts,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_member#create GuarddutyMember#create}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_member#update GuarddutyMember#update}.
        '''
        value = GuarddutyMemberTimeouts(create=create, update=update)

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetDisableEmailNotification")
    def reset_disable_email_notification(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDisableEmailNotification", []))

    @jsii.member(jsii_name="resetInvitationMessage")
    def reset_invitation_message(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInvitationMessage", []))

    @jsii.member(jsii_name="resetInvite")
    def reset_invite(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInvite", []))

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
    @jsii.member(jsii_name="relationshipStatus")
    def relationship_status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "relationshipStatus"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "GuarddutyMemberTimeoutsOutputReference":
        return typing.cast("GuarddutyMemberTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="detectorIdInput")
    def detector_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "detectorIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="disableEmailNotificationInput")
    def disable_email_notification_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "disableEmailNotificationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="emailInput")
    def email_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "emailInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="invitationMessageInput")
    def invitation_message_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "invitationMessageInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inviteInput")
    def invite_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "inviteInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(self) -> typing.Optional["GuarddutyMemberTimeouts"]:
        return typing.cast(typing.Optional["GuarddutyMemberTimeouts"], jsii.get(self, "timeoutsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: builtins.str) -> None:
        jsii.set(self, "accountId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="detectorId")
    def detector_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "detectorId"))

    @detector_id.setter
    def detector_id(self, value: builtins.str) -> None:
        jsii.set(self, "detectorId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="disableEmailNotification")
    def disable_email_notification(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "disableEmailNotification"))

    @disable_email_notification.setter
    def disable_email_notification(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "disableEmailNotification", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="email")
    def email(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "email"))

    @email.setter
    def email(self, value: builtins.str) -> None:
        jsii.set(self, "email", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="invitationMessage")
    def invitation_message(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "invitationMessage"))

    @invitation_message.setter
    def invitation_message(self, value: builtins.str) -> None:
        jsii.set(self, "invitationMessage", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="invite")
    def invite(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "invite"))

    @invite.setter
    def invite(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "invite", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.guardduty.GuarddutyMemberConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "account_id": "accountId",
        "detector_id": "detectorId",
        "email": "email",
        "disable_email_notification": "disableEmailNotification",
        "invitation_message": "invitationMessage",
        "invite": "invite",
        "timeouts": "timeouts",
    },
)
class GuarddutyMemberConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        account_id: builtins.str,
        detector_id: builtins.str,
        email: builtins.str,
        disable_email_notification: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        invitation_message: typing.Optional[builtins.str] = None,
        invite: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        timeouts: typing.Optional["GuarddutyMemberTimeouts"] = None,
    ) -> None:
        '''AWS GuardDuty.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param account_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_member#account_id GuarddutyMember#account_id}.
        :param detector_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_member#detector_id GuarddutyMember#detector_id}.
        :param email: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_member#email GuarddutyMember#email}.
        :param disable_email_notification: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_member#disable_email_notification GuarddutyMember#disable_email_notification}.
        :param invitation_message: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_member#invitation_message GuarddutyMember#invitation_message}.
        :param invite: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_member#invite GuarddutyMember#invite}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_member#timeouts GuarddutyMember#timeouts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(timeouts, dict):
            timeouts = GuarddutyMemberTimeouts(**timeouts)
        self._values: typing.Dict[str, typing.Any] = {
            "account_id": account_id,
            "detector_id": detector_id,
            "email": email,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if disable_email_notification is not None:
            self._values["disable_email_notification"] = disable_email_notification
        if invitation_message is not None:
            self._values["invitation_message"] = invitation_message
        if invite is not None:
            self._values["invite"] = invite
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
    def account_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_member#account_id GuarddutyMember#account_id}.'''
        result = self._values.get("account_id")
        assert result is not None, "Required property 'account_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def detector_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_member#detector_id GuarddutyMember#detector_id}.'''
        result = self._values.get("detector_id")
        assert result is not None, "Required property 'detector_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def email(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_member#email GuarddutyMember#email}.'''
        result = self._values.get("email")
        assert result is not None, "Required property 'email' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def disable_email_notification(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_member#disable_email_notification GuarddutyMember#disable_email_notification}.'''
        result = self._values.get("disable_email_notification")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def invitation_message(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_member#invitation_message GuarddutyMember#invitation_message}.'''
        result = self._values.get("invitation_message")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def invite(self) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_member#invite GuarddutyMember#invite}.'''
        result = self._values.get("invite")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["GuarddutyMemberTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_member#timeouts GuarddutyMember#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["GuarddutyMemberTimeouts"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GuarddutyMemberConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.guardduty.GuarddutyMemberTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "update": "update"},
)
class GuarddutyMemberTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_member#create GuarddutyMember#create}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_member#update GuarddutyMember#update}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if create is not None:
            self._values["create"] = create
        if update is not None:
            self._values["update"] = update

    @builtins.property
    def create(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_member#create GuarddutyMember#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_member#update GuarddutyMember#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GuarddutyMemberTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GuarddutyMemberTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.guardduty.GuarddutyMemberTimeoutsOutputReference",
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

    @jsii.member(jsii_name="resetUpdate")
    def reset_update(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpdate", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createInput")
    def create_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createInput"))

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
    @jsii.member(jsii_name="update")
    def update(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "update"))

    @update.setter
    def update(self, value: builtins.str) -> None:
        jsii.set(self, "update", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[GuarddutyMemberTimeouts]:
        return typing.cast(typing.Optional[GuarddutyMemberTimeouts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[GuarddutyMemberTimeouts]) -> None:
        jsii.set(self, "internalValue", value)


class GuarddutyOrganizationAdminAccount(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.guardduty.GuarddutyOrganizationAdminAccount",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/guardduty_organization_admin_account aws_guardduty_organization_admin_account}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        admin_account_id: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/guardduty_organization_admin_account aws_guardduty_organization_admin_account} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param admin_account_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_organization_admin_account#admin_account_id GuarddutyOrganizationAdminAccount#admin_account_id}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = GuarddutyOrganizationAdminAccountConfig(
            admin_account_id=admin_account_id,
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
    @jsii.member(jsii_name="adminAccountIdInput")
    def admin_account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "adminAccountIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="adminAccountId")
    def admin_account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "adminAccountId"))

    @admin_account_id.setter
    def admin_account_id(self, value: builtins.str) -> None:
        jsii.set(self, "adminAccountId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.guardduty.GuarddutyOrganizationAdminAccountConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "admin_account_id": "adminAccountId",
    },
)
class GuarddutyOrganizationAdminAccountConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        admin_account_id: builtins.str,
    ) -> None:
        '''AWS GuardDuty.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param admin_account_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_organization_admin_account#admin_account_id GuarddutyOrganizationAdminAccount#admin_account_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "admin_account_id": admin_account_id,
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
    def admin_account_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_organization_admin_account#admin_account_id GuarddutyOrganizationAdminAccount#admin_account_id}.'''
        result = self._values.get("admin_account_id")
        assert result is not None, "Required property 'admin_account_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GuarddutyOrganizationAdminAccountConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GuarddutyOrganizationConfiguration(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.guardduty.GuarddutyOrganizationConfiguration",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/guardduty_organization_configuration aws_guardduty_organization_configuration}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        auto_enable: typing.Union[builtins.bool, cdktf.IResolvable],
        detector_id: builtins.str,
        datasources: typing.Optional["GuarddutyOrganizationConfigurationDatasources"] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/guardduty_organization_configuration aws_guardduty_organization_configuration} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param auto_enable: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_organization_configuration#auto_enable GuarddutyOrganizationConfiguration#auto_enable}.
        :param detector_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_organization_configuration#detector_id GuarddutyOrganizationConfiguration#detector_id}.
        :param datasources: datasources block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_organization_configuration#datasources GuarddutyOrganizationConfiguration#datasources}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = GuarddutyOrganizationConfigurationConfig(
            auto_enable=auto_enable,
            detector_id=detector_id,
            datasources=datasources,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putDatasources")
    def put_datasources(
        self,
        *,
        s3_logs: typing.Optional["GuarddutyOrganizationConfigurationDatasourcesS3Logs"] = None,
    ) -> None:
        '''
        :param s3_logs: s3_logs block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_organization_configuration#s3_logs GuarddutyOrganizationConfiguration#s3_logs}
        '''
        value = GuarddutyOrganizationConfigurationDatasources(s3_logs=s3_logs)

        return typing.cast(None, jsii.invoke(self, "putDatasources", [value]))

    @jsii.member(jsii_name="resetDatasources")
    def reset_datasources(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDatasources", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="datasources")
    def datasources(
        self,
    ) -> "GuarddutyOrganizationConfigurationDatasourcesOutputReference":
        return typing.cast("GuarddutyOrganizationConfigurationDatasourcesOutputReference", jsii.get(self, "datasources"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoEnableInput")
    def auto_enable_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "autoEnableInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="datasourcesInput")
    def datasources_input(
        self,
    ) -> typing.Optional["GuarddutyOrganizationConfigurationDatasources"]:
        return typing.cast(typing.Optional["GuarddutyOrganizationConfigurationDatasources"], jsii.get(self, "datasourcesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="detectorIdInput")
    def detector_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "detectorIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoEnable")
    def auto_enable(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "autoEnable"))

    @auto_enable.setter
    def auto_enable(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "autoEnable", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="detectorId")
    def detector_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "detectorId"))

    @detector_id.setter
    def detector_id(self, value: builtins.str) -> None:
        jsii.set(self, "detectorId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.guardduty.GuarddutyOrganizationConfigurationConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "auto_enable": "autoEnable",
        "detector_id": "detectorId",
        "datasources": "datasources",
    },
)
class GuarddutyOrganizationConfigurationConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        auto_enable: typing.Union[builtins.bool, cdktf.IResolvable],
        detector_id: builtins.str,
        datasources: typing.Optional["GuarddutyOrganizationConfigurationDatasources"] = None,
    ) -> None:
        '''AWS GuardDuty.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param auto_enable: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_organization_configuration#auto_enable GuarddutyOrganizationConfiguration#auto_enable}.
        :param detector_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_organization_configuration#detector_id GuarddutyOrganizationConfiguration#detector_id}.
        :param datasources: datasources block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_organization_configuration#datasources GuarddutyOrganizationConfiguration#datasources}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(datasources, dict):
            datasources = GuarddutyOrganizationConfigurationDatasources(**datasources)
        self._values: typing.Dict[str, typing.Any] = {
            "auto_enable": auto_enable,
            "detector_id": detector_id,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if datasources is not None:
            self._values["datasources"] = datasources

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
    def auto_enable(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_organization_configuration#auto_enable GuarddutyOrganizationConfiguration#auto_enable}.'''
        result = self._values.get("auto_enable")
        assert result is not None, "Required property 'auto_enable' is missing"
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], result)

    @builtins.property
    def detector_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_organization_configuration#detector_id GuarddutyOrganizationConfiguration#detector_id}.'''
        result = self._values.get("detector_id")
        assert result is not None, "Required property 'detector_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def datasources(
        self,
    ) -> typing.Optional["GuarddutyOrganizationConfigurationDatasources"]:
        '''datasources block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_organization_configuration#datasources GuarddutyOrganizationConfiguration#datasources}
        '''
        result = self._values.get("datasources")
        return typing.cast(typing.Optional["GuarddutyOrganizationConfigurationDatasources"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GuarddutyOrganizationConfigurationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.guardduty.GuarddutyOrganizationConfigurationDatasources",
    jsii_struct_bases=[],
    name_mapping={"s3_logs": "s3Logs"},
)
class GuarddutyOrganizationConfigurationDatasources:
    def __init__(
        self,
        *,
        s3_logs: typing.Optional["GuarddutyOrganizationConfigurationDatasourcesS3Logs"] = None,
    ) -> None:
        '''
        :param s3_logs: s3_logs block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_organization_configuration#s3_logs GuarddutyOrganizationConfiguration#s3_logs}
        '''
        if isinstance(s3_logs, dict):
            s3_logs = GuarddutyOrganizationConfigurationDatasourcesS3Logs(**s3_logs)
        self._values: typing.Dict[str, typing.Any] = {}
        if s3_logs is not None:
            self._values["s3_logs"] = s3_logs

    @builtins.property
    def s3_logs(
        self,
    ) -> typing.Optional["GuarddutyOrganizationConfigurationDatasourcesS3Logs"]:
        '''s3_logs block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_organization_configuration#s3_logs GuarddutyOrganizationConfiguration#s3_logs}
        '''
        result = self._values.get("s3_logs")
        return typing.cast(typing.Optional["GuarddutyOrganizationConfigurationDatasourcesS3Logs"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GuarddutyOrganizationConfigurationDatasources(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GuarddutyOrganizationConfigurationDatasourcesOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.guardduty.GuarddutyOrganizationConfigurationDatasourcesOutputReference",
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

    @jsii.member(jsii_name="putS3Logs")
    def put_s3_logs(
        self,
        *,
        auto_enable: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        '''
        :param auto_enable: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_organization_configuration#auto_enable GuarddutyOrganizationConfiguration#auto_enable}.
        '''
        value = GuarddutyOrganizationConfigurationDatasourcesS3Logs(
            auto_enable=auto_enable
        )

        return typing.cast(None, jsii.invoke(self, "putS3Logs", [value]))

    @jsii.member(jsii_name="resetS3Logs")
    def reset_s3_logs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetS3Logs", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3Logs")
    def s3_logs(
        self,
    ) -> "GuarddutyOrganizationConfigurationDatasourcesS3LogsOutputReference":
        return typing.cast("GuarddutyOrganizationConfigurationDatasourcesS3LogsOutputReference", jsii.get(self, "s3Logs"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3LogsInput")
    def s3_logs_input(
        self,
    ) -> typing.Optional["GuarddutyOrganizationConfigurationDatasourcesS3Logs"]:
        return typing.cast(typing.Optional["GuarddutyOrganizationConfigurationDatasourcesS3Logs"], jsii.get(self, "s3LogsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[GuarddutyOrganizationConfigurationDatasources]:
        return typing.cast(typing.Optional[GuarddutyOrganizationConfigurationDatasources], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GuarddutyOrganizationConfigurationDatasources],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.guardduty.GuarddutyOrganizationConfigurationDatasourcesS3Logs",
    jsii_struct_bases=[],
    name_mapping={"auto_enable": "autoEnable"},
)
class GuarddutyOrganizationConfigurationDatasourcesS3Logs:
    def __init__(
        self,
        *,
        auto_enable: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        '''
        :param auto_enable: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_organization_configuration#auto_enable GuarddutyOrganizationConfiguration#auto_enable}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "auto_enable": auto_enable,
        }

    @builtins.property
    def auto_enable(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_organization_configuration#auto_enable GuarddutyOrganizationConfiguration#auto_enable}.'''
        result = self._values.get("auto_enable")
        assert result is not None, "Required property 'auto_enable' is missing"
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GuarddutyOrganizationConfigurationDatasourcesS3Logs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GuarddutyOrganizationConfigurationDatasourcesS3LogsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.guardduty.GuarddutyOrganizationConfigurationDatasourcesS3LogsOutputReference",
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
    @jsii.member(jsii_name="autoEnableInput")
    def auto_enable_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "autoEnableInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoEnable")
    def auto_enable(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "autoEnable"))

    @auto_enable.setter
    def auto_enable(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "autoEnable", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[GuarddutyOrganizationConfigurationDatasourcesS3Logs]:
        return typing.cast(typing.Optional[GuarddutyOrganizationConfigurationDatasourcesS3Logs], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GuarddutyOrganizationConfigurationDatasourcesS3Logs],
    ) -> None:
        jsii.set(self, "internalValue", value)


class GuarddutyPublishingDestination(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.guardduty.GuarddutyPublishingDestination",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/guardduty_publishing_destination aws_guardduty_publishing_destination}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        destination_arn: builtins.str,
        detector_id: builtins.str,
        kms_key_arn: builtins.str,
        destination_type: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/guardduty_publishing_destination aws_guardduty_publishing_destination} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param destination_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_publishing_destination#destination_arn GuarddutyPublishingDestination#destination_arn}.
        :param detector_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_publishing_destination#detector_id GuarddutyPublishingDestination#detector_id}.
        :param kms_key_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_publishing_destination#kms_key_arn GuarddutyPublishingDestination#kms_key_arn}.
        :param destination_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_publishing_destination#destination_type GuarddutyPublishingDestination#destination_type}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = GuarddutyPublishingDestinationConfig(
            destination_arn=destination_arn,
            detector_id=detector_id,
            kms_key_arn=kms_key_arn,
            destination_type=destination_type,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetDestinationType")
    def reset_destination_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDestinationType", []))

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
    @jsii.member(jsii_name="destinationArnInput")
    def destination_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "destinationArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="destinationTypeInput")
    def destination_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "destinationTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="detectorIdInput")
    def detector_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "detectorIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyArnInput")
    def kms_key_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kmsKeyArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="destinationArn")
    def destination_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destinationArn"))

    @destination_arn.setter
    def destination_arn(self, value: builtins.str) -> None:
        jsii.set(self, "destinationArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="destinationType")
    def destination_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destinationType"))

    @destination_type.setter
    def destination_type(self, value: builtins.str) -> None:
        jsii.set(self, "destinationType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="detectorId")
    def detector_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "detectorId"))

    @detector_id.setter
    def detector_id(self, value: builtins.str) -> None:
        jsii.set(self, "detectorId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyArn")
    def kms_key_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsKeyArn"))

    @kms_key_arn.setter
    def kms_key_arn(self, value: builtins.str) -> None:
        jsii.set(self, "kmsKeyArn", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.guardduty.GuarddutyPublishingDestinationConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "destination_arn": "destinationArn",
        "detector_id": "detectorId",
        "kms_key_arn": "kmsKeyArn",
        "destination_type": "destinationType",
    },
)
class GuarddutyPublishingDestinationConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        destination_arn: builtins.str,
        detector_id: builtins.str,
        kms_key_arn: builtins.str,
        destination_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS GuardDuty.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param destination_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_publishing_destination#destination_arn GuarddutyPublishingDestination#destination_arn}.
        :param detector_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_publishing_destination#detector_id GuarddutyPublishingDestination#detector_id}.
        :param kms_key_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_publishing_destination#kms_key_arn GuarddutyPublishingDestination#kms_key_arn}.
        :param destination_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_publishing_destination#destination_type GuarddutyPublishingDestination#destination_type}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "destination_arn": destination_arn,
            "detector_id": detector_id,
            "kms_key_arn": kms_key_arn,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if destination_type is not None:
            self._values["destination_type"] = destination_type

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
    def destination_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_publishing_destination#destination_arn GuarddutyPublishingDestination#destination_arn}.'''
        result = self._values.get("destination_arn")
        assert result is not None, "Required property 'destination_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def detector_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_publishing_destination#detector_id GuarddutyPublishingDestination#detector_id}.'''
        result = self._values.get("detector_id")
        assert result is not None, "Required property 'detector_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def kms_key_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_publishing_destination#kms_key_arn GuarddutyPublishingDestination#kms_key_arn}.'''
        result = self._values.get("kms_key_arn")
        assert result is not None, "Required property 'kms_key_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def destination_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_publishing_destination#destination_type GuarddutyPublishingDestination#destination_type}.'''
        result = self._values.get("destination_type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GuarddutyPublishingDestinationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GuarddutyThreatintelset(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.guardduty.GuarddutyThreatintelset",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/guardduty_threatintelset aws_guardduty_threatintelset}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        activate: typing.Union[builtins.bool, cdktf.IResolvable],
        detector_id: builtins.str,
        format: builtins.str,
        location: builtins.str,
        name: builtins.str,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/guardduty_threatintelset aws_guardduty_threatintelset} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param activate: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_threatintelset#activate GuarddutyThreatintelset#activate}.
        :param detector_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_threatintelset#detector_id GuarddutyThreatintelset#detector_id}.
        :param format: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_threatintelset#format GuarddutyThreatintelset#format}.
        :param location: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_threatintelset#location GuarddutyThreatintelset#location}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_threatintelset#name GuarddutyThreatintelset#name}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_threatintelset#tags GuarddutyThreatintelset#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_threatintelset#tags_all GuarddutyThreatintelset#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = GuarddutyThreatintelsetConfig(
            activate=activate,
            detector_id=detector_id,
            format=format,
            location=location,
            name=name,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

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
    @jsii.member(jsii_name="activateInput")
    def activate_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "activateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="detectorIdInput")
    def detector_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "detectorIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="formatInput")
    def format_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "formatInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="locationInput")
    def location_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "locationInput"))

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
    @jsii.member(jsii_name="activate")
    def activate(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "activate"))

    @activate.setter
    def activate(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "activate", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="detectorId")
    def detector_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "detectorId"))

    @detector_id.setter
    def detector_id(self, value: builtins.str) -> None:
        jsii.set(self, "detectorId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="format")
    def format(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "format"))

    @format.setter
    def format(self, value: builtins.str) -> None:
        jsii.set(self, "format", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="location")
    def location(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "location"))

    @location.setter
    def location(self, value: builtins.str) -> None:
        jsii.set(self, "location", value)

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
    jsii_type="@cdktf/provider-aws.guardduty.GuarddutyThreatintelsetConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "activate": "activate",
        "detector_id": "detectorId",
        "format": "format",
        "location": "location",
        "name": "name",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class GuarddutyThreatintelsetConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        activate: typing.Union[builtins.bool, cdktf.IResolvable],
        detector_id: builtins.str,
        format: builtins.str,
        location: builtins.str,
        name: builtins.str,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS GuardDuty.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param activate: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_threatintelset#activate GuarddutyThreatintelset#activate}.
        :param detector_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_threatintelset#detector_id GuarddutyThreatintelset#detector_id}.
        :param format: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_threatintelset#format GuarddutyThreatintelset#format}.
        :param location: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_threatintelset#location GuarddutyThreatintelset#location}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_threatintelset#name GuarddutyThreatintelset#name}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_threatintelset#tags GuarddutyThreatintelset#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_threatintelset#tags_all GuarddutyThreatintelset#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "activate": activate,
            "detector_id": detector_id,
            "format": format,
            "location": location,
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
    def activate(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_threatintelset#activate GuarddutyThreatintelset#activate}.'''
        result = self._values.get("activate")
        assert result is not None, "Required property 'activate' is missing"
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], result)

    @builtins.property
    def detector_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_threatintelset#detector_id GuarddutyThreatintelset#detector_id}.'''
        result = self._values.get("detector_id")
        assert result is not None, "Required property 'detector_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def format(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_threatintelset#format GuarddutyThreatintelset#format}.'''
        result = self._values.get("format")
        assert result is not None, "Required property 'format' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def location(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_threatintelset#location GuarddutyThreatintelset#location}.'''
        result = self._values.get("location")
        assert result is not None, "Required property 'location' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_threatintelset#name GuarddutyThreatintelset#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_threatintelset#tags GuarddutyThreatintelset#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/guardduty_threatintelset#tags_all GuarddutyThreatintelset#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GuarddutyThreatintelsetConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "DataAwsGuarddutyDetector",
    "DataAwsGuarddutyDetectorConfig",
    "GuarddutyDetector",
    "GuarddutyDetectorConfig",
    "GuarddutyDetectorDatasources",
    "GuarddutyDetectorDatasourcesOutputReference",
    "GuarddutyDetectorDatasourcesS3Logs",
    "GuarddutyDetectorDatasourcesS3LogsOutputReference",
    "GuarddutyFilter",
    "GuarddutyFilterConfig",
    "GuarddutyFilterFindingCriteria",
    "GuarddutyFilterFindingCriteriaCriterion",
    "GuarddutyFilterFindingCriteriaOutputReference",
    "GuarddutyInviteAccepter",
    "GuarddutyInviteAccepterConfig",
    "GuarddutyInviteAccepterTimeouts",
    "GuarddutyInviteAccepterTimeoutsOutputReference",
    "GuarddutyIpset",
    "GuarddutyIpsetConfig",
    "GuarddutyMember",
    "GuarddutyMemberConfig",
    "GuarddutyMemberTimeouts",
    "GuarddutyMemberTimeoutsOutputReference",
    "GuarddutyOrganizationAdminAccount",
    "GuarddutyOrganizationAdminAccountConfig",
    "GuarddutyOrganizationConfiguration",
    "GuarddutyOrganizationConfigurationConfig",
    "GuarddutyOrganizationConfigurationDatasources",
    "GuarddutyOrganizationConfigurationDatasourcesOutputReference",
    "GuarddutyOrganizationConfigurationDatasourcesS3Logs",
    "GuarddutyOrganizationConfigurationDatasourcesS3LogsOutputReference",
    "GuarddutyPublishingDestination",
    "GuarddutyPublishingDestinationConfig",
    "GuarddutyThreatintelset",
    "GuarddutyThreatintelsetConfig",
]

publication.publish()
