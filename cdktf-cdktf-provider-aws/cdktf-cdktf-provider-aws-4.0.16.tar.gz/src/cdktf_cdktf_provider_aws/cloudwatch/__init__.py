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


class CloudwatchCompositeAlarm(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudwatch.CloudwatchCompositeAlarm",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_composite_alarm aws_cloudwatch_composite_alarm}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        alarm_name: builtins.str,
        alarm_rule: builtins.str,
        actions_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        alarm_actions: typing.Optional[typing.Sequence[builtins.str]] = None,
        alarm_description: typing.Optional[builtins.str] = None,
        insufficient_data_actions: typing.Optional[typing.Sequence[builtins.str]] = None,
        ok_actions: typing.Optional[typing.Sequence[builtins.str]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_composite_alarm aws_cloudwatch_composite_alarm} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param alarm_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_composite_alarm#alarm_name CloudwatchCompositeAlarm#alarm_name}.
        :param alarm_rule: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_composite_alarm#alarm_rule CloudwatchCompositeAlarm#alarm_rule}.
        :param actions_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_composite_alarm#actions_enabled CloudwatchCompositeAlarm#actions_enabled}.
        :param alarm_actions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_composite_alarm#alarm_actions CloudwatchCompositeAlarm#alarm_actions}.
        :param alarm_description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_composite_alarm#alarm_description CloudwatchCompositeAlarm#alarm_description}.
        :param insufficient_data_actions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_composite_alarm#insufficient_data_actions CloudwatchCompositeAlarm#insufficient_data_actions}.
        :param ok_actions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_composite_alarm#ok_actions CloudwatchCompositeAlarm#ok_actions}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_composite_alarm#tags CloudwatchCompositeAlarm#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_composite_alarm#tags_all CloudwatchCompositeAlarm#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = CloudwatchCompositeAlarmConfig(
            alarm_name=alarm_name,
            alarm_rule=alarm_rule,
            actions_enabled=actions_enabled,
            alarm_actions=alarm_actions,
            alarm_description=alarm_description,
            insufficient_data_actions=insufficient_data_actions,
            ok_actions=ok_actions,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetActionsEnabled")
    def reset_actions_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetActionsEnabled", []))

    @jsii.member(jsii_name="resetAlarmActions")
    def reset_alarm_actions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAlarmActions", []))

    @jsii.member(jsii_name="resetAlarmDescription")
    def reset_alarm_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAlarmDescription", []))

    @jsii.member(jsii_name="resetInsufficientDataActions")
    def reset_insufficient_data_actions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInsufficientDataActions", []))

    @jsii.member(jsii_name="resetOkActions")
    def reset_ok_actions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOkActions", []))

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
    @jsii.member(jsii_name="actionsEnabledInput")
    def actions_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "actionsEnabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="alarmActionsInput")
    def alarm_actions_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "alarmActionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="alarmDescriptionInput")
    def alarm_description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "alarmDescriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="alarmNameInput")
    def alarm_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "alarmNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="alarmRuleInput")
    def alarm_rule_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "alarmRuleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="insufficientDataActionsInput")
    def insufficient_data_actions_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "insufficientDataActionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="okActionsInput")
    def ok_actions_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "okActionsInput"))

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
    @jsii.member(jsii_name="actionsEnabled")
    def actions_enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "actionsEnabled"))

    @actions_enabled.setter
    def actions_enabled(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "actionsEnabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="alarmActions")
    def alarm_actions(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "alarmActions"))

    @alarm_actions.setter
    def alarm_actions(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "alarmActions", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="alarmDescription")
    def alarm_description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "alarmDescription"))

    @alarm_description.setter
    def alarm_description(self, value: builtins.str) -> None:
        jsii.set(self, "alarmDescription", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="alarmName")
    def alarm_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "alarmName"))

    @alarm_name.setter
    def alarm_name(self, value: builtins.str) -> None:
        jsii.set(self, "alarmName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="alarmRule")
    def alarm_rule(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "alarmRule"))

    @alarm_rule.setter
    def alarm_rule(self, value: builtins.str) -> None:
        jsii.set(self, "alarmRule", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="insufficientDataActions")
    def insufficient_data_actions(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "insufficientDataActions"))

    @insufficient_data_actions.setter
    def insufficient_data_actions(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "insufficientDataActions", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="okActions")
    def ok_actions(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "okActions"))

    @ok_actions.setter
    def ok_actions(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "okActions", value)

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
    jsii_type="@cdktf/provider-aws.cloudwatch.CloudwatchCompositeAlarmConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "alarm_name": "alarmName",
        "alarm_rule": "alarmRule",
        "actions_enabled": "actionsEnabled",
        "alarm_actions": "alarmActions",
        "alarm_description": "alarmDescription",
        "insufficient_data_actions": "insufficientDataActions",
        "ok_actions": "okActions",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class CloudwatchCompositeAlarmConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        alarm_name: builtins.str,
        alarm_rule: builtins.str,
        actions_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        alarm_actions: typing.Optional[typing.Sequence[builtins.str]] = None,
        alarm_description: typing.Optional[builtins.str] = None,
        insufficient_data_actions: typing.Optional[typing.Sequence[builtins.str]] = None,
        ok_actions: typing.Optional[typing.Sequence[builtins.str]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS CloudWatch.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param alarm_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_composite_alarm#alarm_name CloudwatchCompositeAlarm#alarm_name}.
        :param alarm_rule: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_composite_alarm#alarm_rule CloudwatchCompositeAlarm#alarm_rule}.
        :param actions_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_composite_alarm#actions_enabled CloudwatchCompositeAlarm#actions_enabled}.
        :param alarm_actions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_composite_alarm#alarm_actions CloudwatchCompositeAlarm#alarm_actions}.
        :param alarm_description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_composite_alarm#alarm_description CloudwatchCompositeAlarm#alarm_description}.
        :param insufficient_data_actions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_composite_alarm#insufficient_data_actions CloudwatchCompositeAlarm#insufficient_data_actions}.
        :param ok_actions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_composite_alarm#ok_actions CloudwatchCompositeAlarm#ok_actions}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_composite_alarm#tags CloudwatchCompositeAlarm#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_composite_alarm#tags_all CloudwatchCompositeAlarm#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "alarm_name": alarm_name,
            "alarm_rule": alarm_rule,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if actions_enabled is not None:
            self._values["actions_enabled"] = actions_enabled
        if alarm_actions is not None:
            self._values["alarm_actions"] = alarm_actions
        if alarm_description is not None:
            self._values["alarm_description"] = alarm_description
        if insufficient_data_actions is not None:
            self._values["insufficient_data_actions"] = insufficient_data_actions
        if ok_actions is not None:
            self._values["ok_actions"] = ok_actions
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
    def alarm_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_composite_alarm#alarm_name CloudwatchCompositeAlarm#alarm_name}.'''
        result = self._values.get("alarm_name")
        assert result is not None, "Required property 'alarm_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def alarm_rule(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_composite_alarm#alarm_rule CloudwatchCompositeAlarm#alarm_rule}.'''
        result = self._values.get("alarm_rule")
        assert result is not None, "Required property 'alarm_rule' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def actions_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_composite_alarm#actions_enabled CloudwatchCompositeAlarm#actions_enabled}.'''
        result = self._values.get("actions_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def alarm_actions(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_composite_alarm#alarm_actions CloudwatchCompositeAlarm#alarm_actions}.'''
        result = self._values.get("alarm_actions")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def alarm_description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_composite_alarm#alarm_description CloudwatchCompositeAlarm#alarm_description}.'''
        result = self._values.get("alarm_description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def insufficient_data_actions(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_composite_alarm#insufficient_data_actions CloudwatchCompositeAlarm#insufficient_data_actions}.'''
        result = self._values.get("insufficient_data_actions")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def ok_actions(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_composite_alarm#ok_actions CloudwatchCompositeAlarm#ok_actions}.'''
        result = self._values.get("ok_actions")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_composite_alarm#tags CloudwatchCompositeAlarm#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_composite_alarm#tags_all CloudwatchCompositeAlarm#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudwatchCompositeAlarmConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudwatchDashboard(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudwatch.CloudwatchDashboard",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_dashboard aws_cloudwatch_dashboard}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        dashboard_body: builtins.str,
        dashboard_name: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_dashboard aws_cloudwatch_dashboard} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param dashboard_body: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_dashboard#dashboard_body CloudwatchDashboard#dashboard_body}.
        :param dashboard_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_dashboard#dashboard_name CloudwatchDashboard#dashboard_name}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = CloudwatchDashboardConfig(
            dashboard_body=dashboard_body,
            dashboard_name=dashboard_name,
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
    @jsii.member(jsii_name="dashboardArn")
    def dashboard_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dashboardArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dashboardBodyInput")
    def dashboard_body_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dashboardBodyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dashboardNameInput")
    def dashboard_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dashboardNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dashboardBody")
    def dashboard_body(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dashboardBody"))

    @dashboard_body.setter
    def dashboard_body(self, value: builtins.str) -> None:
        jsii.set(self, "dashboardBody", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dashboardName")
    def dashboard_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dashboardName"))

    @dashboard_name.setter
    def dashboard_name(self, value: builtins.str) -> None:
        jsii.set(self, "dashboardName", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudwatch.CloudwatchDashboardConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "dashboard_body": "dashboardBody",
        "dashboard_name": "dashboardName",
    },
)
class CloudwatchDashboardConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        dashboard_body: builtins.str,
        dashboard_name: builtins.str,
    ) -> None:
        '''AWS CloudWatch.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param dashboard_body: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_dashboard#dashboard_body CloudwatchDashboard#dashboard_body}.
        :param dashboard_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_dashboard#dashboard_name CloudwatchDashboard#dashboard_name}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "dashboard_body": dashboard_body,
            "dashboard_name": dashboard_name,
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
    def dashboard_body(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_dashboard#dashboard_body CloudwatchDashboard#dashboard_body}.'''
        result = self._values.get("dashboard_body")
        assert result is not None, "Required property 'dashboard_body' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def dashboard_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_dashboard#dashboard_name CloudwatchDashboard#dashboard_name}.'''
        result = self._values.get("dashboard_name")
        assert result is not None, "Required property 'dashboard_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudwatchDashboardConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudwatchLogDestination(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudwatch.CloudwatchLogDestination",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_destination aws_cloudwatch_log_destination}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        role_arn: builtins.str,
        target_arn: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_destination aws_cloudwatch_log_destination} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_destination#name CloudwatchLogDestination#name}.
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_destination#role_arn CloudwatchLogDestination#role_arn}.
        :param target_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_destination#target_arn CloudwatchLogDestination#target_arn}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = CloudwatchLogDestinationConfig(
            name=name,
            role_arn=role_arn,
            target_arn=target_arn,
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
    @jsii.member(jsii_name="roleArnInput")
    def role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetArnInput")
    def target_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @role_arn.setter
    def role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "roleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetArn")
    def target_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetArn"))

    @target_arn.setter
    def target_arn(self, value: builtins.str) -> None:
        jsii.set(self, "targetArn", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudwatch.CloudwatchLogDestinationConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "role_arn": "roleArn",
        "target_arn": "targetArn",
    },
)
class CloudwatchLogDestinationConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        role_arn: builtins.str,
        target_arn: builtins.str,
    ) -> None:
        '''AWS CloudWatch.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_destination#name CloudwatchLogDestination#name}.
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_destination#role_arn CloudwatchLogDestination#role_arn}.
        :param target_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_destination#target_arn CloudwatchLogDestination#target_arn}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "role_arn": role_arn,
            "target_arn": target_arn,
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_destination#name CloudwatchLogDestination#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def role_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_destination#role_arn CloudwatchLogDestination#role_arn}.'''
        result = self._values.get("role_arn")
        assert result is not None, "Required property 'role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def target_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_destination#target_arn CloudwatchLogDestination#target_arn}.'''
        result = self._values.get("target_arn")
        assert result is not None, "Required property 'target_arn' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudwatchLogDestinationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudwatchLogDestinationPolicy(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudwatch.CloudwatchLogDestinationPolicy",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_destination_policy aws_cloudwatch_log_destination_policy}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        access_policy: builtins.str,
        destination_name: builtins.str,
        force_update: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_destination_policy aws_cloudwatch_log_destination_policy} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param access_policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_destination_policy#access_policy CloudwatchLogDestinationPolicy#access_policy}.
        :param destination_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_destination_policy#destination_name CloudwatchLogDestinationPolicy#destination_name}.
        :param force_update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_destination_policy#force_update CloudwatchLogDestinationPolicy#force_update}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = CloudwatchLogDestinationPolicyConfig(
            access_policy=access_policy,
            destination_name=destination_name,
            force_update=force_update,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetForceUpdate")
    def reset_force_update(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetForceUpdate", []))

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
    @jsii.member(jsii_name="accessPolicyInput")
    def access_policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accessPolicyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="destinationNameInput")
    def destination_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "destinationNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="forceUpdateInput")
    def force_update_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "forceUpdateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessPolicy")
    def access_policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accessPolicy"))

    @access_policy.setter
    def access_policy(self, value: builtins.str) -> None:
        jsii.set(self, "accessPolicy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="destinationName")
    def destination_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destinationName"))

    @destination_name.setter
    def destination_name(self, value: builtins.str) -> None:
        jsii.set(self, "destinationName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="forceUpdate")
    def force_update(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "forceUpdate"))

    @force_update.setter
    def force_update(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "forceUpdate", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudwatch.CloudwatchLogDestinationPolicyConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "access_policy": "accessPolicy",
        "destination_name": "destinationName",
        "force_update": "forceUpdate",
    },
)
class CloudwatchLogDestinationPolicyConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        access_policy: builtins.str,
        destination_name: builtins.str,
        force_update: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''AWS CloudWatch.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param access_policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_destination_policy#access_policy CloudwatchLogDestinationPolicy#access_policy}.
        :param destination_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_destination_policy#destination_name CloudwatchLogDestinationPolicy#destination_name}.
        :param force_update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_destination_policy#force_update CloudwatchLogDestinationPolicy#force_update}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "access_policy": access_policy,
            "destination_name": destination_name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if force_update is not None:
            self._values["force_update"] = force_update

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
    def access_policy(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_destination_policy#access_policy CloudwatchLogDestinationPolicy#access_policy}.'''
        result = self._values.get("access_policy")
        assert result is not None, "Required property 'access_policy' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def destination_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_destination_policy#destination_name CloudwatchLogDestinationPolicy#destination_name}.'''
        result = self._values.get("destination_name")
        assert result is not None, "Required property 'destination_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def force_update(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_destination_policy#force_update CloudwatchLogDestinationPolicy#force_update}.'''
        result = self._values.get("force_update")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudwatchLogDestinationPolicyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudwatchLogGroup(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudwatch.CloudwatchLogGroup",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_group aws_cloudwatch_log_group}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        kms_key_id: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        name_prefix: typing.Optional[builtins.str] = None,
        retention_in_days: typing.Optional[jsii.Number] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_group aws_cloudwatch_log_group} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param kms_key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_group#kms_key_id CloudwatchLogGroup#kms_key_id}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_group#name CloudwatchLogGroup#name}.
        :param name_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_group#name_prefix CloudwatchLogGroup#name_prefix}.
        :param retention_in_days: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_group#retention_in_days CloudwatchLogGroup#retention_in_days}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_group#tags CloudwatchLogGroup#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_group#tags_all CloudwatchLogGroup#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = CloudwatchLogGroupConfig(
            kms_key_id=kms_key_id,
            name=name,
            name_prefix=name_prefix,
            retention_in_days=retention_in_days,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetKmsKeyId")
    def reset_kms_key_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKmsKeyId", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetNamePrefix")
    def reset_name_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamePrefix", []))

    @jsii.member(jsii_name="resetRetentionInDays")
    def reset_retention_in_days(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRetentionInDays", []))

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
    @jsii.member(jsii_name="kmsKeyIdInput")
    def kms_key_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kmsKeyIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namePrefixInput")
    def name_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namePrefixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="retentionInDaysInput")
    def retention_in_days_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "retentionInDaysInput"))

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
    @jsii.member(jsii_name="kmsKeyId")
    def kms_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsKeyId"))

    @kms_key_id.setter
    def kms_key_id(self, value: builtins.str) -> None:
        jsii.set(self, "kmsKeyId", value)

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
    @jsii.member(jsii_name="retentionInDays")
    def retention_in_days(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "retentionInDays"))

    @retention_in_days.setter
    def retention_in_days(self, value: jsii.Number) -> None:
        jsii.set(self, "retentionInDays", value)

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
    jsii_type="@cdktf/provider-aws.cloudwatch.CloudwatchLogGroupConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "kms_key_id": "kmsKeyId",
        "name": "name",
        "name_prefix": "namePrefix",
        "retention_in_days": "retentionInDays",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class CloudwatchLogGroupConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        kms_key_id: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        name_prefix: typing.Optional[builtins.str] = None,
        retention_in_days: typing.Optional[jsii.Number] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS CloudWatch.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param kms_key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_group#kms_key_id CloudwatchLogGroup#kms_key_id}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_group#name CloudwatchLogGroup#name}.
        :param name_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_group#name_prefix CloudwatchLogGroup#name_prefix}.
        :param retention_in_days: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_group#retention_in_days CloudwatchLogGroup#retention_in_days}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_group#tags CloudwatchLogGroup#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_group#tags_all CloudwatchLogGroup#tags_all}.
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
        if kms_key_id is not None:
            self._values["kms_key_id"] = kms_key_id
        if name is not None:
            self._values["name"] = name
        if name_prefix is not None:
            self._values["name_prefix"] = name_prefix
        if retention_in_days is not None:
            self._values["retention_in_days"] = retention_in_days
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
    def kms_key_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_group#kms_key_id CloudwatchLogGroup#kms_key_id}.'''
        result = self._values.get("kms_key_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_group#name CloudwatchLogGroup#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_group#name_prefix CloudwatchLogGroup#name_prefix}.'''
        result = self._values.get("name_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def retention_in_days(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_group#retention_in_days CloudwatchLogGroup#retention_in_days}.'''
        result = self._values.get("retention_in_days")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_group#tags CloudwatchLogGroup#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_group#tags_all CloudwatchLogGroup#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudwatchLogGroupConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudwatchLogMetricFilter(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudwatch.CloudwatchLogMetricFilter",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_metric_filter aws_cloudwatch_log_metric_filter}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        log_group_name: builtins.str,
        metric_transformation: "CloudwatchLogMetricFilterMetricTransformation",
        name: builtins.str,
        pattern: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_metric_filter aws_cloudwatch_log_metric_filter} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param log_group_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_metric_filter#log_group_name CloudwatchLogMetricFilter#log_group_name}.
        :param metric_transformation: metric_transformation block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_metric_filter#metric_transformation CloudwatchLogMetricFilter#metric_transformation}
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_metric_filter#name CloudwatchLogMetricFilter#name}.
        :param pattern: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_metric_filter#pattern CloudwatchLogMetricFilter#pattern}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = CloudwatchLogMetricFilterConfig(
            log_group_name=log_group_name,
            metric_transformation=metric_transformation,
            name=name,
            pattern=pattern,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putMetricTransformation")
    def put_metric_transformation(
        self,
        *,
        name: builtins.str,
        namespace: builtins.str,
        value: builtins.str,
        default_value: typing.Optional[builtins.str] = None,
        dimensions: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        unit: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_metric_filter#name CloudwatchLogMetricFilter#name}.
        :param namespace: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_metric_filter#namespace CloudwatchLogMetricFilter#namespace}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_metric_filter#value CloudwatchLogMetricFilter#value}.
        :param default_value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_metric_filter#default_value CloudwatchLogMetricFilter#default_value}.
        :param dimensions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_metric_filter#dimensions CloudwatchLogMetricFilter#dimensions}.
        :param unit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_metric_filter#unit CloudwatchLogMetricFilter#unit}.
        '''
        value_ = CloudwatchLogMetricFilterMetricTransformation(
            name=name,
            namespace=namespace,
            value=value,
            default_value=default_value,
            dimensions=dimensions,
            unit=unit,
        )

        return typing.cast(None, jsii.invoke(self, "putMetricTransformation", [value_]))

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
    @jsii.member(jsii_name="metricTransformation")
    def metric_transformation(
        self,
    ) -> "CloudwatchLogMetricFilterMetricTransformationOutputReference":
        return typing.cast("CloudwatchLogMetricFilterMetricTransformationOutputReference", jsii.get(self, "metricTransformation"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logGroupNameInput")
    def log_group_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "logGroupNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="metricTransformationInput")
    def metric_transformation_input(
        self,
    ) -> typing.Optional["CloudwatchLogMetricFilterMetricTransformation"]:
        return typing.cast(typing.Optional["CloudwatchLogMetricFilterMetricTransformation"], jsii.get(self, "metricTransformationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="patternInput")
    def pattern_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "patternInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logGroupName")
    def log_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "logGroupName"))

    @log_group_name.setter
    def log_group_name(self, value: builtins.str) -> None:
        jsii.set(self, "logGroupName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pattern")
    def pattern(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pattern"))

    @pattern.setter
    def pattern(self, value: builtins.str) -> None:
        jsii.set(self, "pattern", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudwatch.CloudwatchLogMetricFilterConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "log_group_name": "logGroupName",
        "metric_transformation": "metricTransformation",
        "name": "name",
        "pattern": "pattern",
    },
)
class CloudwatchLogMetricFilterConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        log_group_name: builtins.str,
        metric_transformation: "CloudwatchLogMetricFilterMetricTransformation",
        name: builtins.str,
        pattern: builtins.str,
    ) -> None:
        '''AWS CloudWatch.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param log_group_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_metric_filter#log_group_name CloudwatchLogMetricFilter#log_group_name}.
        :param metric_transformation: metric_transformation block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_metric_filter#metric_transformation CloudwatchLogMetricFilter#metric_transformation}
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_metric_filter#name CloudwatchLogMetricFilter#name}.
        :param pattern: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_metric_filter#pattern CloudwatchLogMetricFilter#pattern}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(metric_transformation, dict):
            metric_transformation = CloudwatchLogMetricFilterMetricTransformation(**metric_transformation)
        self._values: typing.Dict[str, typing.Any] = {
            "log_group_name": log_group_name,
            "metric_transformation": metric_transformation,
            "name": name,
            "pattern": pattern,
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
    def log_group_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_metric_filter#log_group_name CloudwatchLogMetricFilter#log_group_name}.'''
        result = self._values.get("log_group_name")
        assert result is not None, "Required property 'log_group_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def metric_transformation(self) -> "CloudwatchLogMetricFilterMetricTransformation":
        '''metric_transformation block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_metric_filter#metric_transformation CloudwatchLogMetricFilter#metric_transformation}
        '''
        result = self._values.get("metric_transformation")
        assert result is not None, "Required property 'metric_transformation' is missing"
        return typing.cast("CloudwatchLogMetricFilterMetricTransformation", result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_metric_filter#name CloudwatchLogMetricFilter#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def pattern(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_metric_filter#pattern CloudwatchLogMetricFilter#pattern}.'''
        result = self._values.get("pattern")
        assert result is not None, "Required property 'pattern' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudwatchLogMetricFilterConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudwatch.CloudwatchLogMetricFilterMetricTransformation",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "namespace": "namespace",
        "value": "value",
        "default_value": "defaultValue",
        "dimensions": "dimensions",
        "unit": "unit",
    },
)
class CloudwatchLogMetricFilterMetricTransformation:
    def __init__(
        self,
        *,
        name: builtins.str,
        namespace: builtins.str,
        value: builtins.str,
        default_value: typing.Optional[builtins.str] = None,
        dimensions: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        unit: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_metric_filter#name CloudwatchLogMetricFilter#name}.
        :param namespace: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_metric_filter#namespace CloudwatchLogMetricFilter#namespace}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_metric_filter#value CloudwatchLogMetricFilter#value}.
        :param default_value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_metric_filter#default_value CloudwatchLogMetricFilter#default_value}.
        :param dimensions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_metric_filter#dimensions CloudwatchLogMetricFilter#dimensions}.
        :param unit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_metric_filter#unit CloudwatchLogMetricFilter#unit}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "namespace": namespace,
            "value": value,
        }
        if default_value is not None:
            self._values["default_value"] = default_value
        if dimensions is not None:
            self._values["dimensions"] = dimensions
        if unit is not None:
            self._values["unit"] = unit

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_metric_filter#name CloudwatchLogMetricFilter#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def namespace(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_metric_filter#namespace CloudwatchLogMetricFilter#namespace}.'''
        result = self._values.get("namespace")
        assert result is not None, "Required property 'namespace' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_metric_filter#value CloudwatchLogMetricFilter#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def default_value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_metric_filter#default_value CloudwatchLogMetricFilter#default_value}.'''
        result = self._values.get("default_value")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def dimensions(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_metric_filter#dimensions CloudwatchLogMetricFilter#dimensions}.'''
        result = self._values.get("dimensions")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def unit(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_metric_filter#unit CloudwatchLogMetricFilter#unit}.'''
        result = self._values.get("unit")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudwatchLogMetricFilterMetricTransformation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudwatchLogMetricFilterMetricTransformationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudwatch.CloudwatchLogMetricFilterMetricTransformationOutputReference",
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

    @jsii.member(jsii_name="resetDefaultValue")
    def reset_default_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefaultValue", []))

    @jsii.member(jsii_name="resetDimensions")
    def reset_dimensions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDimensions", []))

    @jsii.member(jsii_name="resetUnit")
    def reset_unit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUnit", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultValueInput")
    def default_value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "defaultValueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dimensionsInput")
    def dimensions_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "dimensionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="unitInput")
    def unit_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "unitInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "valueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultValue")
    def default_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "defaultValue"))

    @default_value.setter
    def default_value(self, value: builtins.str) -> None:
        jsii.set(self, "defaultValue", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dimensions")
    def dimensions(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "dimensions"))

    @dimensions.setter
    def dimensions(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "dimensions", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        jsii.set(self, "namespace", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="unit")
    def unit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "unit"))

    @unit.setter
    def unit(self, value: builtins.str) -> None:
        jsii.set(self, "unit", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        jsii.set(self, "value", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CloudwatchLogMetricFilterMetricTransformation]:
        return typing.cast(typing.Optional[CloudwatchLogMetricFilterMetricTransformation], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CloudwatchLogMetricFilterMetricTransformation],
    ) -> None:
        jsii.set(self, "internalValue", value)


class CloudwatchLogResourcePolicy(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudwatch.CloudwatchLogResourcePolicy",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_resource_policy aws_cloudwatch_log_resource_policy}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        policy_document: builtins.str,
        policy_name: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_resource_policy aws_cloudwatch_log_resource_policy} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param policy_document: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_resource_policy#policy_document CloudwatchLogResourcePolicy#policy_document}.
        :param policy_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_resource_policy#policy_name CloudwatchLogResourcePolicy#policy_name}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = CloudwatchLogResourcePolicyConfig(
            policy_document=policy_document,
            policy_name=policy_name,
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
    @jsii.member(jsii_name="policyDocumentInput")
    def policy_document_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "policyDocumentInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyNameInput")
    def policy_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "policyNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyDocument")
    def policy_document(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policyDocument"))

    @policy_document.setter
    def policy_document(self, value: builtins.str) -> None:
        jsii.set(self, "policyDocument", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyName")
    def policy_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policyName"))

    @policy_name.setter
    def policy_name(self, value: builtins.str) -> None:
        jsii.set(self, "policyName", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudwatch.CloudwatchLogResourcePolicyConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "policy_document": "policyDocument",
        "policy_name": "policyName",
    },
)
class CloudwatchLogResourcePolicyConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        policy_document: builtins.str,
        policy_name: builtins.str,
    ) -> None:
        '''AWS CloudWatch.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param policy_document: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_resource_policy#policy_document CloudwatchLogResourcePolicy#policy_document}.
        :param policy_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_resource_policy#policy_name CloudwatchLogResourcePolicy#policy_name}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "policy_document": policy_document,
            "policy_name": policy_name,
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
    def policy_document(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_resource_policy#policy_document CloudwatchLogResourcePolicy#policy_document}.'''
        result = self._values.get("policy_document")
        assert result is not None, "Required property 'policy_document' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def policy_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_resource_policy#policy_name CloudwatchLogResourcePolicy#policy_name}.'''
        result = self._values.get("policy_name")
        assert result is not None, "Required property 'policy_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudwatchLogResourcePolicyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudwatchLogStream(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudwatch.CloudwatchLogStream",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_stream aws_cloudwatch_log_stream}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        log_group_name: builtins.str,
        name: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_stream aws_cloudwatch_log_stream} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param log_group_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_stream#log_group_name CloudwatchLogStream#log_group_name}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_stream#name CloudwatchLogStream#name}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = CloudwatchLogStreamConfig(
            log_group_name=log_group_name,
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
    @jsii.member(jsii_name="logGroupNameInput")
    def log_group_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "logGroupNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logGroupName")
    def log_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "logGroupName"))

    @log_group_name.setter
    def log_group_name(self, value: builtins.str) -> None:
        jsii.set(self, "logGroupName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudwatch.CloudwatchLogStreamConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "log_group_name": "logGroupName",
        "name": "name",
    },
)
class CloudwatchLogStreamConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        log_group_name: builtins.str,
        name: builtins.str,
    ) -> None:
        '''AWS CloudWatch.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param log_group_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_stream#log_group_name CloudwatchLogStream#log_group_name}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_stream#name CloudwatchLogStream#name}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "log_group_name": log_group_name,
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
    def log_group_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_stream#log_group_name CloudwatchLogStream#log_group_name}.'''
        result = self._values.get("log_group_name")
        assert result is not None, "Required property 'log_group_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_stream#name CloudwatchLogStream#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudwatchLogStreamConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudwatchLogSubscriptionFilter(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudwatch.CloudwatchLogSubscriptionFilter",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_subscription_filter aws_cloudwatch_log_subscription_filter}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        destination_arn: builtins.str,
        filter_pattern: builtins.str,
        log_group_name: builtins.str,
        name: builtins.str,
        distribution: typing.Optional[builtins.str] = None,
        role_arn: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_subscription_filter aws_cloudwatch_log_subscription_filter} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param destination_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_subscription_filter#destination_arn CloudwatchLogSubscriptionFilter#destination_arn}.
        :param filter_pattern: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_subscription_filter#filter_pattern CloudwatchLogSubscriptionFilter#filter_pattern}.
        :param log_group_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_subscription_filter#log_group_name CloudwatchLogSubscriptionFilter#log_group_name}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_subscription_filter#name CloudwatchLogSubscriptionFilter#name}.
        :param distribution: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_subscription_filter#distribution CloudwatchLogSubscriptionFilter#distribution}.
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_subscription_filter#role_arn CloudwatchLogSubscriptionFilter#role_arn}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = CloudwatchLogSubscriptionFilterConfig(
            destination_arn=destination_arn,
            filter_pattern=filter_pattern,
            log_group_name=log_group_name,
            name=name,
            distribution=distribution,
            role_arn=role_arn,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetDistribution")
    def reset_distribution(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDistribution", []))

    @jsii.member(jsii_name="resetRoleArn")
    def reset_role_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRoleArn", []))

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
    @jsii.member(jsii_name="distributionInput")
    def distribution_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "distributionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="filterPatternInput")
    def filter_pattern_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "filterPatternInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logGroupNameInput")
    def log_group_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "logGroupNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArnInput")
    def role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="destinationArn")
    def destination_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destinationArn"))

    @destination_arn.setter
    def destination_arn(self, value: builtins.str) -> None:
        jsii.set(self, "destinationArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="distribution")
    def distribution(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "distribution"))

    @distribution.setter
    def distribution(self, value: builtins.str) -> None:
        jsii.set(self, "distribution", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="filterPattern")
    def filter_pattern(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "filterPattern"))

    @filter_pattern.setter
    def filter_pattern(self, value: builtins.str) -> None:
        jsii.set(self, "filterPattern", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logGroupName")
    def log_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "logGroupName"))

    @log_group_name.setter
    def log_group_name(self, value: builtins.str) -> None:
        jsii.set(self, "logGroupName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @role_arn.setter
    def role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "roleArn", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudwatch.CloudwatchLogSubscriptionFilterConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "destination_arn": "destinationArn",
        "filter_pattern": "filterPattern",
        "log_group_name": "logGroupName",
        "name": "name",
        "distribution": "distribution",
        "role_arn": "roleArn",
    },
)
class CloudwatchLogSubscriptionFilterConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        destination_arn: builtins.str,
        filter_pattern: builtins.str,
        log_group_name: builtins.str,
        name: builtins.str,
        distribution: typing.Optional[builtins.str] = None,
        role_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS CloudWatch.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param destination_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_subscription_filter#destination_arn CloudwatchLogSubscriptionFilter#destination_arn}.
        :param filter_pattern: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_subscription_filter#filter_pattern CloudwatchLogSubscriptionFilter#filter_pattern}.
        :param log_group_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_subscription_filter#log_group_name CloudwatchLogSubscriptionFilter#log_group_name}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_subscription_filter#name CloudwatchLogSubscriptionFilter#name}.
        :param distribution: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_subscription_filter#distribution CloudwatchLogSubscriptionFilter#distribution}.
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_subscription_filter#role_arn CloudwatchLogSubscriptionFilter#role_arn}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "destination_arn": destination_arn,
            "filter_pattern": filter_pattern,
            "log_group_name": log_group_name,
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
        if distribution is not None:
            self._values["distribution"] = distribution
        if role_arn is not None:
            self._values["role_arn"] = role_arn

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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_subscription_filter#destination_arn CloudwatchLogSubscriptionFilter#destination_arn}.'''
        result = self._values.get("destination_arn")
        assert result is not None, "Required property 'destination_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def filter_pattern(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_subscription_filter#filter_pattern CloudwatchLogSubscriptionFilter#filter_pattern}.'''
        result = self._values.get("filter_pattern")
        assert result is not None, "Required property 'filter_pattern' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def log_group_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_subscription_filter#log_group_name CloudwatchLogSubscriptionFilter#log_group_name}.'''
        result = self._values.get("log_group_name")
        assert result is not None, "Required property 'log_group_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_subscription_filter#name CloudwatchLogSubscriptionFilter#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def distribution(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_subscription_filter#distribution CloudwatchLogSubscriptionFilter#distribution}.'''
        result = self._values.get("distribution")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def role_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_log_subscription_filter#role_arn CloudwatchLogSubscriptionFilter#role_arn}.'''
        result = self._values.get("role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudwatchLogSubscriptionFilterConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudwatchMetricAlarm(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudwatch.CloudwatchMetricAlarm",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm aws_cloudwatch_metric_alarm}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        alarm_name: builtins.str,
        comparison_operator: builtins.str,
        evaluation_periods: jsii.Number,
        actions_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        alarm_actions: typing.Optional[typing.Sequence[builtins.str]] = None,
        alarm_description: typing.Optional[builtins.str] = None,
        datapoints_to_alarm: typing.Optional[jsii.Number] = None,
        dimensions: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        evaluate_low_sample_count_percentiles: typing.Optional[builtins.str] = None,
        extended_statistic: typing.Optional[builtins.str] = None,
        insufficient_data_actions: typing.Optional[typing.Sequence[builtins.str]] = None,
        metric_name: typing.Optional[builtins.str] = None,
        metric_query: typing.Optional[typing.Sequence["CloudwatchMetricAlarmMetricQuery"]] = None,
        namespace: typing.Optional[builtins.str] = None,
        ok_actions: typing.Optional[typing.Sequence[builtins.str]] = None,
        period: typing.Optional[jsii.Number] = None,
        statistic: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        threshold: typing.Optional[jsii.Number] = None,
        threshold_metric_id: typing.Optional[builtins.str] = None,
        treat_missing_data: typing.Optional[builtins.str] = None,
        unit: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm aws_cloudwatch_metric_alarm} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param alarm_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#alarm_name CloudwatchMetricAlarm#alarm_name}.
        :param comparison_operator: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#comparison_operator CloudwatchMetricAlarm#comparison_operator}.
        :param evaluation_periods: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#evaluation_periods CloudwatchMetricAlarm#evaluation_periods}.
        :param actions_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#actions_enabled CloudwatchMetricAlarm#actions_enabled}.
        :param alarm_actions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#alarm_actions CloudwatchMetricAlarm#alarm_actions}.
        :param alarm_description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#alarm_description CloudwatchMetricAlarm#alarm_description}.
        :param datapoints_to_alarm: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#datapoints_to_alarm CloudwatchMetricAlarm#datapoints_to_alarm}.
        :param dimensions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#dimensions CloudwatchMetricAlarm#dimensions}.
        :param evaluate_low_sample_count_percentiles: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#evaluate_low_sample_count_percentiles CloudwatchMetricAlarm#evaluate_low_sample_count_percentiles}.
        :param extended_statistic: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#extended_statistic CloudwatchMetricAlarm#extended_statistic}.
        :param insufficient_data_actions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#insufficient_data_actions CloudwatchMetricAlarm#insufficient_data_actions}.
        :param metric_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#metric_name CloudwatchMetricAlarm#metric_name}.
        :param metric_query: metric_query block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#metric_query CloudwatchMetricAlarm#metric_query}
        :param namespace: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#namespace CloudwatchMetricAlarm#namespace}.
        :param ok_actions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#ok_actions CloudwatchMetricAlarm#ok_actions}.
        :param period: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#period CloudwatchMetricAlarm#period}.
        :param statistic: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#statistic CloudwatchMetricAlarm#statistic}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#tags CloudwatchMetricAlarm#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#tags_all CloudwatchMetricAlarm#tags_all}.
        :param threshold: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#threshold CloudwatchMetricAlarm#threshold}.
        :param threshold_metric_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#threshold_metric_id CloudwatchMetricAlarm#threshold_metric_id}.
        :param treat_missing_data: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#treat_missing_data CloudwatchMetricAlarm#treat_missing_data}.
        :param unit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#unit CloudwatchMetricAlarm#unit}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = CloudwatchMetricAlarmConfig(
            alarm_name=alarm_name,
            comparison_operator=comparison_operator,
            evaluation_periods=evaluation_periods,
            actions_enabled=actions_enabled,
            alarm_actions=alarm_actions,
            alarm_description=alarm_description,
            datapoints_to_alarm=datapoints_to_alarm,
            dimensions=dimensions,
            evaluate_low_sample_count_percentiles=evaluate_low_sample_count_percentiles,
            extended_statistic=extended_statistic,
            insufficient_data_actions=insufficient_data_actions,
            metric_name=metric_name,
            metric_query=metric_query,
            namespace=namespace,
            ok_actions=ok_actions,
            period=period,
            statistic=statistic,
            tags=tags,
            tags_all=tags_all,
            threshold=threshold,
            threshold_metric_id=threshold_metric_id,
            treat_missing_data=treat_missing_data,
            unit=unit,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetActionsEnabled")
    def reset_actions_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetActionsEnabled", []))

    @jsii.member(jsii_name="resetAlarmActions")
    def reset_alarm_actions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAlarmActions", []))

    @jsii.member(jsii_name="resetAlarmDescription")
    def reset_alarm_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAlarmDescription", []))

    @jsii.member(jsii_name="resetDatapointsToAlarm")
    def reset_datapoints_to_alarm(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDatapointsToAlarm", []))

    @jsii.member(jsii_name="resetDimensions")
    def reset_dimensions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDimensions", []))

    @jsii.member(jsii_name="resetEvaluateLowSampleCountPercentiles")
    def reset_evaluate_low_sample_count_percentiles(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEvaluateLowSampleCountPercentiles", []))

    @jsii.member(jsii_name="resetExtendedStatistic")
    def reset_extended_statistic(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExtendedStatistic", []))

    @jsii.member(jsii_name="resetInsufficientDataActions")
    def reset_insufficient_data_actions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInsufficientDataActions", []))

    @jsii.member(jsii_name="resetMetricName")
    def reset_metric_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMetricName", []))

    @jsii.member(jsii_name="resetMetricQuery")
    def reset_metric_query(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMetricQuery", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @jsii.member(jsii_name="resetOkActions")
    def reset_ok_actions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOkActions", []))

    @jsii.member(jsii_name="resetPeriod")
    def reset_period(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPeriod", []))

    @jsii.member(jsii_name="resetStatistic")
    def reset_statistic(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStatistic", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetThreshold")
    def reset_threshold(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetThreshold", []))

    @jsii.member(jsii_name="resetThresholdMetricId")
    def reset_threshold_metric_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetThresholdMetricId", []))

    @jsii.member(jsii_name="resetTreatMissingData")
    def reset_treat_missing_data(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTreatMissingData", []))

    @jsii.member(jsii_name="resetUnit")
    def reset_unit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUnit", []))

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
    @jsii.member(jsii_name="actionsEnabledInput")
    def actions_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "actionsEnabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="alarmActionsInput")
    def alarm_actions_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "alarmActionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="alarmDescriptionInput")
    def alarm_description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "alarmDescriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="alarmNameInput")
    def alarm_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "alarmNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="comparisonOperatorInput")
    def comparison_operator_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "comparisonOperatorInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="datapointsToAlarmInput")
    def datapoints_to_alarm_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "datapointsToAlarmInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dimensionsInput")
    def dimensions_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "dimensionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="evaluateLowSampleCountPercentilesInput")
    def evaluate_low_sample_count_percentiles_input(
        self,
    ) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "evaluateLowSampleCountPercentilesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="evaluationPeriodsInput")
    def evaluation_periods_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "evaluationPeriodsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="extendedStatisticInput")
    def extended_statistic_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "extendedStatisticInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="insufficientDataActionsInput")
    def insufficient_data_actions_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "insufficientDataActionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="metricNameInput")
    def metric_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "metricNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="metricQueryInput")
    def metric_query_input(
        self,
    ) -> typing.Optional[typing.List["CloudwatchMetricAlarmMetricQuery"]]:
        return typing.cast(typing.Optional[typing.List["CloudwatchMetricAlarmMetricQuery"]], jsii.get(self, "metricQueryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="okActionsInput")
    def ok_actions_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "okActionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="periodInput")
    def period_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "periodInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statisticInput")
    def statistic_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "statisticInput"))

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
    @jsii.member(jsii_name="thresholdInput")
    def threshold_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "thresholdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="thresholdMetricIdInput")
    def threshold_metric_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "thresholdMetricIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="treatMissingDataInput")
    def treat_missing_data_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "treatMissingDataInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="unitInput")
    def unit_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "unitInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="actionsEnabled")
    def actions_enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "actionsEnabled"))

    @actions_enabled.setter
    def actions_enabled(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "actionsEnabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="alarmActions")
    def alarm_actions(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "alarmActions"))

    @alarm_actions.setter
    def alarm_actions(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "alarmActions", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="alarmDescription")
    def alarm_description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "alarmDescription"))

    @alarm_description.setter
    def alarm_description(self, value: builtins.str) -> None:
        jsii.set(self, "alarmDescription", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="alarmName")
    def alarm_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "alarmName"))

    @alarm_name.setter
    def alarm_name(self, value: builtins.str) -> None:
        jsii.set(self, "alarmName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="comparisonOperator")
    def comparison_operator(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "comparisonOperator"))

    @comparison_operator.setter
    def comparison_operator(self, value: builtins.str) -> None:
        jsii.set(self, "comparisonOperator", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="datapointsToAlarm")
    def datapoints_to_alarm(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "datapointsToAlarm"))

    @datapoints_to_alarm.setter
    def datapoints_to_alarm(self, value: jsii.Number) -> None:
        jsii.set(self, "datapointsToAlarm", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dimensions")
    def dimensions(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "dimensions"))

    @dimensions.setter
    def dimensions(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "dimensions", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="evaluateLowSampleCountPercentiles")
    def evaluate_low_sample_count_percentiles(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "evaluateLowSampleCountPercentiles"))

    @evaluate_low_sample_count_percentiles.setter
    def evaluate_low_sample_count_percentiles(self, value: builtins.str) -> None:
        jsii.set(self, "evaluateLowSampleCountPercentiles", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="evaluationPeriods")
    def evaluation_periods(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "evaluationPeriods"))

    @evaluation_periods.setter
    def evaluation_periods(self, value: jsii.Number) -> None:
        jsii.set(self, "evaluationPeriods", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="extendedStatistic")
    def extended_statistic(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "extendedStatistic"))

    @extended_statistic.setter
    def extended_statistic(self, value: builtins.str) -> None:
        jsii.set(self, "extendedStatistic", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="insufficientDataActions")
    def insufficient_data_actions(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "insufficientDataActions"))

    @insufficient_data_actions.setter
    def insufficient_data_actions(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "insufficientDataActions", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="metricName")
    def metric_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "metricName"))

    @metric_name.setter
    def metric_name(self, value: builtins.str) -> None:
        jsii.set(self, "metricName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="metricQuery")
    def metric_query(self) -> typing.List["CloudwatchMetricAlarmMetricQuery"]:
        return typing.cast(typing.List["CloudwatchMetricAlarmMetricQuery"], jsii.get(self, "metricQuery"))

    @metric_query.setter
    def metric_query(
        self,
        value: typing.List["CloudwatchMetricAlarmMetricQuery"],
    ) -> None:
        jsii.set(self, "metricQuery", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        jsii.set(self, "namespace", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="okActions")
    def ok_actions(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "okActions"))

    @ok_actions.setter
    def ok_actions(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "okActions", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="period")
    def period(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "period"))

    @period.setter
    def period(self, value: jsii.Number) -> None:
        jsii.set(self, "period", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statistic")
    def statistic(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "statistic"))

    @statistic.setter
    def statistic(self, value: builtins.str) -> None:
        jsii.set(self, "statistic", value)

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
    @jsii.member(jsii_name="threshold")
    def threshold(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "threshold"))

    @threshold.setter
    def threshold(self, value: jsii.Number) -> None:
        jsii.set(self, "threshold", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="thresholdMetricId")
    def threshold_metric_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "thresholdMetricId"))

    @threshold_metric_id.setter
    def threshold_metric_id(self, value: builtins.str) -> None:
        jsii.set(self, "thresholdMetricId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="treatMissingData")
    def treat_missing_data(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "treatMissingData"))

    @treat_missing_data.setter
    def treat_missing_data(self, value: builtins.str) -> None:
        jsii.set(self, "treatMissingData", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="unit")
    def unit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "unit"))

    @unit.setter
    def unit(self, value: builtins.str) -> None:
        jsii.set(self, "unit", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudwatch.CloudwatchMetricAlarmConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "alarm_name": "alarmName",
        "comparison_operator": "comparisonOperator",
        "evaluation_periods": "evaluationPeriods",
        "actions_enabled": "actionsEnabled",
        "alarm_actions": "alarmActions",
        "alarm_description": "alarmDescription",
        "datapoints_to_alarm": "datapointsToAlarm",
        "dimensions": "dimensions",
        "evaluate_low_sample_count_percentiles": "evaluateLowSampleCountPercentiles",
        "extended_statistic": "extendedStatistic",
        "insufficient_data_actions": "insufficientDataActions",
        "metric_name": "metricName",
        "metric_query": "metricQuery",
        "namespace": "namespace",
        "ok_actions": "okActions",
        "period": "period",
        "statistic": "statistic",
        "tags": "tags",
        "tags_all": "tagsAll",
        "threshold": "threshold",
        "threshold_metric_id": "thresholdMetricId",
        "treat_missing_data": "treatMissingData",
        "unit": "unit",
    },
)
class CloudwatchMetricAlarmConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        alarm_name: builtins.str,
        comparison_operator: builtins.str,
        evaluation_periods: jsii.Number,
        actions_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        alarm_actions: typing.Optional[typing.Sequence[builtins.str]] = None,
        alarm_description: typing.Optional[builtins.str] = None,
        datapoints_to_alarm: typing.Optional[jsii.Number] = None,
        dimensions: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        evaluate_low_sample_count_percentiles: typing.Optional[builtins.str] = None,
        extended_statistic: typing.Optional[builtins.str] = None,
        insufficient_data_actions: typing.Optional[typing.Sequence[builtins.str]] = None,
        metric_name: typing.Optional[builtins.str] = None,
        metric_query: typing.Optional[typing.Sequence["CloudwatchMetricAlarmMetricQuery"]] = None,
        namespace: typing.Optional[builtins.str] = None,
        ok_actions: typing.Optional[typing.Sequence[builtins.str]] = None,
        period: typing.Optional[jsii.Number] = None,
        statistic: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        threshold: typing.Optional[jsii.Number] = None,
        threshold_metric_id: typing.Optional[builtins.str] = None,
        treat_missing_data: typing.Optional[builtins.str] = None,
        unit: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS CloudWatch.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param alarm_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#alarm_name CloudwatchMetricAlarm#alarm_name}.
        :param comparison_operator: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#comparison_operator CloudwatchMetricAlarm#comparison_operator}.
        :param evaluation_periods: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#evaluation_periods CloudwatchMetricAlarm#evaluation_periods}.
        :param actions_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#actions_enabled CloudwatchMetricAlarm#actions_enabled}.
        :param alarm_actions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#alarm_actions CloudwatchMetricAlarm#alarm_actions}.
        :param alarm_description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#alarm_description CloudwatchMetricAlarm#alarm_description}.
        :param datapoints_to_alarm: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#datapoints_to_alarm CloudwatchMetricAlarm#datapoints_to_alarm}.
        :param dimensions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#dimensions CloudwatchMetricAlarm#dimensions}.
        :param evaluate_low_sample_count_percentiles: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#evaluate_low_sample_count_percentiles CloudwatchMetricAlarm#evaluate_low_sample_count_percentiles}.
        :param extended_statistic: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#extended_statistic CloudwatchMetricAlarm#extended_statistic}.
        :param insufficient_data_actions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#insufficient_data_actions CloudwatchMetricAlarm#insufficient_data_actions}.
        :param metric_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#metric_name CloudwatchMetricAlarm#metric_name}.
        :param metric_query: metric_query block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#metric_query CloudwatchMetricAlarm#metric_query}
        :param namespace: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#namespace CloudwatchMetricAlarm#namespace}.
        :param ok_actions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#ok_actions CloudwatchMetricAlarm#ok_actions}.
        :param period: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#period CloudwatchMetricAlarm#period}.
        :param statistic: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#statistic CloudwatchMetricAlarm#statistic}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#tags CloudwatchMetricAlarm#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#tags_all CloudwatchMetricAlarm#tags_all}.
        :param threshold: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#threshold CloudwatchMetricAlarm#threshold}.
        :param threshold_metric_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#threshold_metric_id CloudwatchMetricAlarm#threshold_metric_id}.
        :param treat_missing_data: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#treat_missing_data CloudwatchMetricAlarm#treat_missing_data}.
        :param unit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#unit CloudwatchMetricAlarm#unit}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "alarm_name": alarm_name,
            "comparison_operator": comparison_operator,
            "evaluation_periods": evaluation_periods,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if actions_enabled is not None:
            self._values["actions_enabled"] = actions_enabled
        if alarm_actions is not None:
            self._values["alarm_actions"] = alarm_actions
        if alarm_description is not None:
            self._values["alarm_description"] = alarm_description
        if datapoints_to_alarm is not None:
            self._values["datapoints_to_alarm"] = datapoints_to_alarm
        if dimensions is not None:
            self._values["dimensions"] = dimensions
        if evaluate_low_sample_count_percentiles is not None:
            self._values["evaluate_low_sample_count_percentiles"] = evaluate_low_sample_count_percentiles
        if extended_statistic is not None:
            self._values["extended_statistic"] = extended_statistic
        if insufficient_data_actions is not None:
            self._values["insufficient_data_actions"] = insufficient_data_actions
        if metric_name is not None:
            self._values["metric_name"] = metric_name
        if metric_query is not None:
            self._values["metric_query"] = metric_query
        if namespace is not None:
            self._values["namespace"] = namespace
        if ok_actions is not None:
            self._values["ok_actions"] = ok_actions
        if period is not None:
            self._values["period"] = period
        if statistic is not None:
            self._values["statistic"] = statistic
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if threshold is not None:
            self._values["threshold"] = threshold
        if threshold_metric_id is not None:
            self._values["threshold_metric_id"] = threshold_metric_id
        if treat_missing_data is not None:
            self._values["treat_missing_data"] = treat_missing_data
        if unit is not None:
            self._values["unit"] = unit

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
    def alarm_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#alarm_name CloudwatchMetricAlarm#alarm_name}.'''
        result = self._values.get("alarm_name")
        assert result is not None, "Required property 'alarm_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def comparison_operator(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#comparison_operator CloudwatchMetricAlarm#comparison_operator}.'''
        result = self._values.get("comparison_operator")
        assert result is not None, "Required property 'comparison_operator' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def evaluation_periods(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#evaluation_periods CloudwatchMetricAlarm#evaluation_periods}.'''
        result = self._values.get("evaluation_periods")
        assert result is not None, "Required property 'evaluation_periods' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def actions_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#actions_enabled CloudwatchMetricAlarm#actions_enabled}.'''
        result = self._values.get("actions_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def alarm_actions(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#alarm_actions CloudwatchMetricAlarm#alarm_actions}.'''
        result = self._values.get("alarm_actions")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def alarm_description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#alarm_description CloudwatchMetricAlarm#alarm_description}.'''
        result = self._values.get("alarm_description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def datapoints_to_alarm(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#datapoints_to_alarm CloudwatchMetricAlarm#datapoints_to_alarm}.'''
        result = self._values.get("datapoints_to_alarm")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def dimensions(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#dimensions CloudwatchMetricAlarm#dimensions}.'''
        result = self._values.get("dimensions")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def evaluate_low_sample_count_percentiles(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#evaluate_low_sample_count_percentiles CloudwatchMetricAlarm#evaluate_low_sample_count_percentiles}.'''
        result = self._values.get("evaluate_low_sample_count_percentiles")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def extended_statistic(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#extended_statistic CloudwatchMetricAlarm#extended_statistic}.'''
        result = self._values.get("extended_statistic")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def insufficient_data_actions(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#insufficient_data_actions CloudwatchMetricAlarm#insufficient_data_actions}.'''
        result = self._values.get("insufficient_data_actions")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def metric_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#metric_name CloudwatchMetricAlarm#metric_name}.'''
        result = self._values.get("metric_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def metric_query(
        self,
    ) -> typing.Optional[typing.List["CloudwatchMetricAlarmMetricQuery"]]:
        '''metric_query block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#metric_query CloudwatchMetricAlarm#metric_query}
        '''
        result = self._values.get("metric_query")
        return typing.cast(typing.Optional[typing.List["CloudwatchMetricAlarmMetricQuery"]], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#namespace CloudwatchMetricAlarm#namespace}.'''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ok_actions(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#ok_actions CloudwatchMetricAlarm#ok_actions}.'''
        result = self._values.get("ok_actions")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def period(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#period CloudwatchMetricAlarm#period}.'''
        result = self._values.get("period")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def statistic(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#statistic CloudwatchMetricAlarm#statistic}.'''
        result = self._values.get("statistic")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#tags CloudwatchMetricAlarm#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#tags_all CloudwatchMetricAlarm#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def threshold(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#threshold CloudwatchMetricAlarm#threshold}.'''
        result = self._values.get("threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def threshold_metric_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#threshold_metric_id CloudwatchMetricAlarm#threshold_metric_id}.'''
        result = self._values.get("threshold_metric_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def treat_missing_data(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#treat_missing_data CloudwatchMetricAlarm#treat_missing_data}.'''
        result = self._values.get("treat_missing_data")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def unit(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#unit CloudwatchMetricAlarm#unit}.'''
        result = self._values.get("unit")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudwatchMetricAlarmConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudwatch.CloudwatchMetricAlarmMetricQuery",
    jsii_struct_bases=[],
    name_mapping={
        "id": "id",
        "account_id": "accountId",
        "expression": "expression",
        "label": "label",
        "metric": "metric",
        "return_data": "returnData",
    },
)
class CloudwatchMetricAlarmMetricQuery:
    def __init__(
        self,
        *,
        id: builtins.str,
        account_id: typing.Optional[builtins.str] = None,
        expression: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        metric: typing.Optional["CloudwatchMetricAlarmMetricQueryMetric"] = None,
        return_data: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#id CloudwatchMetricAlarm#id}.
        :param account_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#account_id CloudwatchMetricAlarm#account_id}.
        :param expression: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#expression CloudwatchMetricAlarm#expression}.
        :param label: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#label CloudwatchMetricAlarm#label}.
        :param metric: metric block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#metric CloudwatchMetricAlarm#metric}
        :param return_data: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#return_data CloudwatchMetricAlarm#return_data}.
        '''
        if isinstance(metric, dict):
            metric = CloudwatchMetricAlarmMetricQueryMetric(**metric)
        self._values: typing.Dict[str, typing.Any] = {
            "id": id,
        }
        if account_id is not None:
            self._values["account_id"] = account_id
        if expression is not None:
            self._values["expression"] = expression
        if label is not None:
            self._values["label"] = label
        if metric is not None:
            self._values["metric"] = metric
        if return_data is not None:
            self._values["return_data"] = return_data

    @builtins.property
    def id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#id CloudwatchMetricAlarm#id}.'''
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def account_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#account_id CloudwatchMetricAlarm#account_id}.'''
        result = self._values.get("account_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def expression(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#expression CloudwatchMetricAlarm#expression}.'''
        result = self._values.get("expression")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def label(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#label CloudwatchMetricAlarm#label}.'''
        result = self._values.get("label")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def metric(self) -> typing.Optional["CloudwatchMetricAlarmMetricQueryMetric"]:
        '''metric block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#metric CloudwatchMetricAlarm#metric}
        '''
        result = self._values.get("metric")
        return typing.cast(typing.Optional["CloudwatchMetricAlarmMetricQueryMetric"], result)

    @builtins.property
    def return_data(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#return_data CloudwatchMetricAlarm#return_data}.'''
        result = self._values.get("return_data")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudwatchMetricAlarmMetricQuery(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudwatch.CloudwatchMetricAlarmMetricQueryMetric",
    jsii_struct_bases=[],
    name_mapping={
        "metric_name": "metricName",
        "period": "period",
        "stat": "stat",
        "dimensions": "dimensions",
        "namespace": "namespace",
        "unit": "unit",
    },
)
class CloudwatchMetricAlarmMetricQueryMetric:
    def __init__(
        self,
        *,
        metric_name: builtins.str,
        period: jsii.Number,
        stat: builtins.str,
        dimensions: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        namespace: typing.Optional[builtins.str] = None,
        unit: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param metric_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#metric_name CloudwatchMetricAlarm#metric_name}.
        :param period: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#period CloudwatchMetricAlarm#period}.
        :param stat: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#stat CloudwatchMetricAlarm#stat}.
        :param dimensions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#dimensions CloudwatchMetricAlarm#dimensions}.
        :param namespace: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#namespace CloudwatchMetricAlarm#namespace}.
        :param unit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#unit CloudwatchMetricAlarm#unit}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "metric_name": metric_name,
            "period": period,
            "stat": stat,
        }
        if dimensions is not None:
            self._values["dimensions"] = dimensions
        if namespace is not None:
            self._values["namespace"] = namespace
        if unit is not None:
            self._values["unit"] = unit

    @builtins.property
    def metric_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#metric_name CloudwatchMetricAlarm#metric_name}.'''
        result = self._values.get("metric_name")
        assert result is not None, "Required property 'metric_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def period(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#period CloudwatchMetricAlarm#period}.'''
        result = self._values.get("period")
        assert result is not None, "Required property 'period' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def stat(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#stat CloudwatchMetricAlarm#stat}.'''
        result = self._values.get("stat")
        assert result is not None, "Required property 'stat' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def dimensions(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#dimensions CloudwatchMetricAlarm#dimensions}.'''
        result = self._values.get("dimensions")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#namespace CloudwatchMetricAlarm#namespace}.'''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def unit(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm#unit CloudwatchMetricAlarm#unit}.'''
        result = self._values.get("unit")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudwatchMetricAlarmMetricQueryMetric(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudwatchMetricAlarmMetricQueryMetricOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudwatch.CloudwatchMetricAlarmMetricQueryMetricOutputReference",
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

    @jsii.member(jsii_name="resetDimensions")
    def reset_dimensions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDimensions", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @jsii.member(jsii_name="resetUnit")
    def reset_unit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUnit", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dimensionsInput")
    def dimensions_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "dimensionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="metricNameInput")
    def metric_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "metricNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="periodInput")
    def period_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "periodInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statInput")
    def stat_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "statInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="unitInput")
    def unit_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "unitInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dimensions")
    def dimensions(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "dimensions"))

    @dimensions.setter
    def dimensions(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "dimensions", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="metricName")
    def metric_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "metricName"))

    @metric_name.setter
    def metric_name(self, value: builtins.str) -> None:
        jsii.set(self, "metricName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        jsii.set(self, "namespace", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="period")
    def period(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "period"))

    @period.setter
    def period(self, value: jsii.Number) -> None:
        jsii.set(self, "period", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stat")
    def stat(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "stat"))

    @stat.setter
    def stat(self, value: builtins.str) -> None:
        jsii.set(self, "stat", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="unit")
    def unit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "unit"))

    @unit.setter
    def unit(self, value: builtins.str) -> None:
        jsii.set(self, "unit", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[CloudwatchMetricAlarmMetricQueryMetric]:
        return typing.cast(typing.Optional[CloudwatchMetricAlarmMetricQueryMetric], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CloudwatchMetricAlarmMetricQueryMetric],
    ) -> None:
        jsii.set(self, "internalValue", value)


class CloudwatchMetricStream(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudwatch.CloudwatchMetricStream",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_stream aws_cloudwatch_metric_stream}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        firehose_arn: builtins.str,
        output_format: builtins.str,
        role_arn: builtins.str,
        exclude_filter: typing.Optional[typing.Sequence["CloudwatchMetricStreamExcludeFilter"]] = None,
        include_filter: typing.Optional[typing.Sequence["CloudwatchMetricStreamIncludeFilter"]] = None,
        name: typing.Optional[builtins.str] = None,
        name_prefix: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["CloudwatchMetricStreamTimeouts"] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_stream aws_cloudwatch_metric_stream} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param firehose_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_stream#firehose_arn CloudwatchMetricStream#firehose_arn}.
        :param output_format: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_stream#output_format CloudwatchMetricStream#output_format}.
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_stream#role_arn CloudwatchMetricStream#role_arn}.
        :param exclude_filter: exclude_filter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_stream#exclude_filter CloudwatchMetricStream#exclude_filter}
        :param include_filter: include_filter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_stream#include_filter CloudwatchMetricStream#include_filter}
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_stream#name CloudwatchMetricStream#name}.
        :param name_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_stream#name_prefix CloudwatchMetricStream#name_prefix}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_stream#tags CloudwatchMetricStream#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_stream#tags_all CloudwatchMetricStream#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_stream#timeouts CloudwatchMetricStream#timeouts}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = CloudwatchMetricStreamConfig(
            firehose_arn=firehose_arn,
            output_format=output_format,
            role_arn=role_arn,
            exclude_filter=exclude_filter,
            include_filter=include_filter,
            name=name,
            name_prefix=name_prefix,
            tags=tags,
            tags_all=tags_all,
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
        delete: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_stream#create CloudwatchMetricStream#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_stream#delete CloudwatchMetricStream#delete}.
        '''
        value = CloudwatchMetricStreamTimeouts(create=create, delete=delete)

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetExcludeFilter")
    def reset_exclude_filter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExcludeFilter", []))

    @jsii.member(jsii_name="resetIncludeFilter")
    def reset_include_filter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIncludeFilter", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetNamePrefix")
    def reset_name_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamePrefix", []))

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
    @jsii.member(jsii_name="creationDate")
    def creation_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "creationDate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lastUpdateDate")
    def last_update_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lastUpdateDate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "CloudwatchMetricStreamTimeoutsOutputReference":
        return typing.cast("CloudwatchMetricStreamTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="excludeFilterInput")
    def exclude_filter_input(
        self,
    ) -> typing.Optional[typing.List["CloudwatchMetricStreamExcludeFilter"]]:
        return typing.cast(typing.Optional[typing.List["CloudwatchMetricStreamExcludeFilter"]], jsii.get(self, "excludeFilterInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firehoseArnInput")
    def firehose_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "firehoseArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="includeFilterInput")
    def include_filter_input(
        self,
    ) -> typing.Optional[typing.List["CloudwatchMetricStreamIncludeFilter"]]:
        return typing.cast(typing.Optional[typing.List["CloudwatchMetricStreamIncludeFilter"]], jsii.get(self, "includeFilterInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namePrefixInput")
    def name_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namePrefixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="outputFormatInput")
    def output_format_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "outputFormatInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArnInput")
    def role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleArnInput"))

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
    def timeouts_input(self) -> typing.Optional["CloudwatchMetricStreamTimeouts"]:
        return typing.cast(typing.Optional["CloudwatchMetricStreamTimeouts"], jsii.get(self, "timeoutsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="excludeFilter")
    def exclude_filter(self) -> typing.List["CloudwatchMetricStreamExcludeFilter"]:
        return typing.cast(typing.List["CloudwatchMetricStreamExcludeFilter"], jsii.get(self, "excludeFilter"))

    @exclude_filter.setter
    def exclude_filter(
        self,
        value: typing.List["CloudwatchMetricStreamExcludeFilter"],
    ) -> None:
        jsii.set(self, "excludeFilter", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firehoseArn")
    def firehose_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "firehoseArn"))

    @firehose_arn.setter
    def firehose_arn(self, value: builtins.str) -> None:
        jsii.set(self, "firehoseArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="includeFilter")
    def include_filter(self) -> typing.List["CloudwatchMetricStreamIncludeFilter"]:
        return typing.cast(typing.List["CloudwatchMetricStreamIncludeFilter"], jsii.get(self, "includeFilter"))

    @include_filter.setter
    def include_filter(
        self,
        value: typing.List["CloudwatchMetricStreamIncludeFilter"],
    ) -> None:
        jsii.set(self, "includeFilter", value)

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
    @jsii.member(jsii_name="outputFormat")
    def output_format(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "outputFormat"))

    @output_format.setter
    def output_format(self, value: builtins.str) -> None:
        jsii.set(self, "outputFormat", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @role_arn.setter
    def role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "roleArn", value)

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
    jsii_type="@cdktf/provider-aws.cloudwatch.CloudwatchMetricStreamConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "firehose_arn": "firehoseArn",
        "output_format": "outputFormat",
        "role_arn": "roleArn",
        "exclude_filter": "excludeFilter",
        "include_filter": "includeFilter",
        "name": "name",
        "name_prefix": "namePrefix",
        "tags": "tags",
        "tags_all": "tagsAll",
        "timeouts": "timeouts",
    },
)
class CloudwatchMetricStreamConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        firehose_arn: builtins.str,
        output_format: builtins.str,
        role_arn: builtins.str,
        exclude_filter: typing.Optional[typing.Sequence["CloudwatchMetricStreamExcludeFilter"]] = None,
        include_filter: typing.Optional[typing.Sequence["CloudwatchMetricStreamIncludeFilter"]] = None,
        name: typing.Optional[builtins.str] = None,
        name_prefix: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["CloudwatchMetricStreamTimeouts"] = None,
    ) -> None:
        '''AWS CloudWatch.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param firehose_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_stream#firehose_arn CloudwatchMetricStream#firehose_arn}.
        :param output_format: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_stream#output_format CloudwatchMetricStream#output_format}.
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_stream#role_arn CloudwatchMetricStream#role_arn}.
        :param exclude_filter: exclude_filter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_stream#exclude_filter CloudwatchMetricStream#exclude_filter}
        :param include_filter: include_filter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_stream#include_filter CloudwatchMetricStream#include_filter}
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_stream#name CloudwatchMetricStream#name}.
        :param name_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_stream#name_prefix CloudwatchMetricStream#name_prefix}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_stream#tags CloudwatchMetricStream#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_stream#tags_all CloudwatchMetricStream#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_stream#timeouts CloudwatchMetricStream#timeouts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(timeouts, dict):
            timeouts = CloudwatchMetricStreamTimeouts(**timeouts)
        self._values: typing.Dict[str, typing.Any] = {
            "firehose_arn": firehose_arn,
            "output_format": output_format,
            "role_arn": role_arn,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if exclude_filter is not None:
            self._values["exclude_filter"] = exclude_filter
        if include_filter is not None:
            self._values["include_filter"] = include_filter
        if name is not None:
            self._values["name"] = name
        if name_prefix is not None:
            self._values["name_prefix"] = name_prefix
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
    def firehose_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_stream#firehose_arn CloudwatchMetricStream#firehose_arn}.'''
        result = self._values.get("firehose_arn")
        assert result is not None, "Required property 'firehose_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def output_format(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_stream#output_format CloudwatchMetricStream#output_format}.'''
        result = self._values.get("output_format")
        assert result is not None, "Required property 'output_format' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def role_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_stream#role_arn CloudwatchMetricStream#role_arn}.'''
        result = self._values.get("role_arn")
        assert result is not None, "Required property 'role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def exclude_filter(
        self,
    ) -> typing.Optional[typing.List["CloudwatchMetricStreamExcludeFilter"]]:
        '''exclude_filter block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_stream#exclude_filter CloudwatchMetricStream#exclude_filter}
        '''
        result = self._values.get("exclude_filter")
        return typing.cast(typing.Optional[typing.List["CloudwatchMetricStreamExcludeFilter"]], result)

    @builtins.property
    def include_filter(
        self,
    ) -> typing.Optional[typing.List["CloudwatchMetricStreamIncludeFilter"]]:
        '''include_filter block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_stream#include_filter CloudwatchMetricStream#include_filter}
        '''
        result = self._values.get("include_filter")
        return typing.cast(typing.Optional[typing.List["CloudwatchMetricStreamIncludeFilter"]], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_stream#name CloudwatchMetricStream#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_stream#name_prefix CloudwatchMetricStream#name_prefix}.'''
        result = self._values.get("name_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_stream#tags CloudwatchMetricStream#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_stream#tags_all CloudwatchMetricStream#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["CloudwatchMetricStreamTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_stream#timeouts CloudwatchMetricStream#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["CloudwatchMetricStreamTimeouts"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudwatchMetricStreamConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudwatch.CloudwatchMetricStreamExcludeFilter",
    jsii_struct_bases=[],
    name_mapping={"namespace": "namespace"},
)
class CloudwatchMetricStreamExcludeFilter:
    def __init__(self, *, namespace: builtins.str) -> None:
        '''
        :param namespace: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_stream#namespace CloudwatchMetricStream#namespace}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "namespace": namespace,
        }

    @builtins.property
    def namespace(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_stream#namespace CloudwatchMetricStream#namespace}.'''
        result = self._values.get("namespace")
        assert result is not None, "Required property 'namespace' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudwatchMetricStreamExcludeFilter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudwatch.CloudwatchMetricStreamIncludeFilter",
    jsii_struct_bases=[],
    name_mapping={"namespace": "namespace"},
)
class CloudwatchMetricStreamIncludeFilter:
    def __init__(self, *, namespace: builtins.str) -> None:
        '''
        :param namespace: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_stream#namespace CloudwatchMetricStream#namespace}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "namespace": namespace,
        }

    @builtins.property
    def namespace(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_stream#namespace CloudwatchMetricStream#namespace}.'''
        result = self._values.get("namespace")
        assert result is not None, "Required property 'namespace' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudwatchMetricStreamIncludeFilter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudwatch.CloudwatchMetricStreamTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete"},
)
class CloudwatchMetricStreamTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_stream#create CloudwatchMetricStream#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_stream#delete CloudwatchMetricStream#delete}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if create is not None:
            self._values["create"] = create
        if delete is not None:
            self._values["delete"] = delete

    @builtins.property
    def create(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_stream#create CloudwatchMetricStream#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_stream#delete CloudwatchMetricStream#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudwatchMetricStreamTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudwatchMetricStreamTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudwatch.CloudwatchMetricStreamTimeoutsOutputReference",
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

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createInput")
    def create_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deleteInput")
    def delete_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deleteInput"))

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
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[CloudwatchMetricStreamTimeouts]:
        return typing.cast(typing.Optional[CloudwatchMetricStreamTimeouts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CloudwatchMetricStreamTimeouts],
    ) -> None:
        jsii.set(self, "internalValue", value)


class CloudwatchQueryDefinition(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudwatch.CloudwatchQueryDefinition",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_query_definition aws_cloudwatch_query_definition}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        query_string: builtins.str,
        log_group_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_query_definition aws_cloudwatch_query_definition} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_query_definition#name CloudwatchQueryDefinition#name}.
        :param query_string: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_query_definition#query_string CloudwatchQueryDefinition#query_string}.
        :param log_group_names: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_query_definition#log_group_names CloudwatchQueryDefinition#log_group_names}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = CloudwatchQueryDefinitionConfig(
            name=name,
            query_string=query_string,
            log_group_names=log_group_names,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetLogGroupNames")
    def reset_log_group_names(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogGroupNames", []))

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
    @jsii.member(jsii_name="queryDefinitionId")
    def query_definition_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "queryDefinitionId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logGroupNamesInput")
    def log_group_names_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "logGroupNamesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="queryStringInput")
    def query_string_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "queryStringInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logGroupNames")
    def log_group_names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "logGroupNames"))

    @log_group_names.setter
    def log_group_names(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "logGroupNames", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="queryString")
    def query_string(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "queryString"))

    @query_string.setter
    def query_string(self, value: builtins.str) -> None:
        jsii.set(self, "queryString", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudwatch.CloudwatchQueryDefinitionConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "query_string": "queryString",
        "log_group_names": "logGroupNames",
    },
)
class CloudwatchQueryDefinitionConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        query_string: builtins.str,
        log_group_names: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''AWS CloudWatch.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_query_definition#name CloudwatchQueryDefinition#name}.
        :param query_string: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_query_definition#query_string CloudwatchQueryDefinition#query_string}.
        :param log_group_names: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_query_definition#log_group_names CloudwatchQueryDefinition#log_group_names}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "query_string": query_string,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if log_group_names is not None:
            self._values["log_group_names"] = log_group_names

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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_query_definition#name CloudwatchQueryDefinition#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def query_string(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_query_definition#query_string CloudwatchQueryDefinition#query_string}.'''
        result = self._values.get("query_string")
        assert result is not None, "Required property 'query_string' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def log_group_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudwatch_query_definition#log_group_names CloudwatchQueryDefinition#log_group_names}.'''
        result = self._values.get("log_group_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudwatchQueryDefinitionConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsCloudwatchLogGroup(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudwatch.DataAwsCloudwatchLogGroup",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/cloudwatch_log_group aws_cloudwatch_log_group}.'''

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
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/cloudwatch_log_group aws_cloudwatch_log_group} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudwatch_log_group#name DataAwsCloudwatchLogGroup#name}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudwatch_log_group#tags DataAwsCloudwatchLogGroup#tags}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsCloudwatchLogGroupConfig(
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
    @jsii.member(jsii_name="creationTime")
    def creation_time(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "creationTime"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyId")
    def kms_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsKeyId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="retentionInDays")
    def retention_in_days(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "retentionInDays"))

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
    jsii_type="@cdktf/provider-aws.cloudwatch.DataAwsCloudwatchLogGroupConfig",
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
class DataAwsCloudwatchLogGroupConfig(cdktf.TerraformMetaArguments):
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
        '''AWS CloudWatch.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudwatch_log_group#name DataAwsCloudwatchLogGroup#name}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudwatch_log_group#tags DataAwsCloudwatchLogGroup#tags}.
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudwatch_log_group#name DataAwsCloudwatchLogGroup#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudwatch_log_group#tags DataAwsCloudwatchLogGroup#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsCloudwatchLogGroupConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsCloudwatchLogGroups(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudwatch.DataAwsCloudwatchLogGroups",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/cloudwatch_log_groups aws_cloudwatch_log_groups}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        log_group_name_prefix: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/cloudwatch_log_groups aws_cloudwatch_log_groups} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param log_group_name_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudwatch_log_groups#log_group_name_prefix DataAwsCloudwatchLogGroups#log_group_name_prefix}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsCloudwatchLogGroupsConfig(
            log_group_name_prefix=log_group_name_prefix,
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
    @jsii.member(jsii_name="arns")
    def arns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "arns"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logGroupNames")
    def log_group_names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "logGroupNames"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logGroupNamePrefixInput")
    def log_group_name_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "logGroupNamePrefixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logGroupNamePrefix")
    def log_group_name_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "logGroupNamePrefix"))

    @log_group_name_prefix.setter
    def log_group_name_prefix(self, value: builtins.str) -> None:
        jsii.set(self, "logGroupNamePrefix", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudwatch.DataAwsCloudwatchLogGroupsConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "log_group_name_prefix": "logGroupNamePrefix",
    },
)
class DataAwsCloudwatchLogGroupsConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        log_group_name_prefix: builtins.str,
    ) -> None:
        '''AWS CloudWatch.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param log_group_name_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudwatch_log_groups#log_group_name_prefix DataAwsCloudwatchLogGroups#log_group_name_prefix}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "log_group_name_prefix": log_group_name_prefix,
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
    def log_group_name_prefix(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudwatch_log_groups#log_group_name_prefix DataAwsCloudwatchLogGroups#log_group_name_prefix}.'''
        result = self._values.get("log_group_name_prefix")
        assert result is not None, "Required property 'log_group_name_prefix' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsCloudwatchLogGroupsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CloudwatchCompositeAlarm",
    "CloudwatchCompositeAlarmConfig",
    "CloudwatchDashboard",
    "CloudwatchDashboardConfig",
    "CloudwatchLogDestination",
    "CloudwatchLogDestinationConfig",
    "CloudwatchLogDestinationPolicy",
    "CloudwatchLogDestinationPolicyConfig",
    "CloudwatchLogGroup",
    "CloudwatchLogGroupConfig",
    "CloudwatchLogMetricFilter",
    "CloudwatchLogMetricFilterConfig",
    "CloudwatchLogMetricFilterMetricTransformation",
    "CloudwatchLogMetricFilterMetricTransformationOutputReference",
    "CloudwatchLogResourcePolicy",
    "CloudwatchLogResourcePolicyConfig",
    "CloudwatchLogStream",
    "CloudwatchLogStreamConfig",
    "CloudwatchLogSubscriptionFilter",
    "CloudwatchLogSubscriptionFilterConfig",
    "CloudwatchMetricAlarm",
    "CloudwatchMetricAlarmConfig",
    "CloudwatchMetricAlarmMetricQuery",
    "CloudwatchMetricAlarmMetricQueryMetric",
    "CloudwatchMetricAlarmMetricQueryMetricOutputReference",
    "CloudwatchMetricStream",
    "CloudwatchMetricStreamConfig",
    "CloudwatchMetricStreamExcludeFilter",
    "CloudwatchMetricStreamIncludeFilter",
    "CloudwatchMetricStreamTimeouts",
    "CloudwatchMetricStreamTimeoutsOutputReference",
    "CloudwatchQueryDefinition",
    "CloudwatchQueryDefinitionConfig",
    "DataAwsCloudwatchLogGroup",
    "DataAwsCloudwatchLogGroupConfig",
    "DataAwsCloudwatchLogGroups",
    "DataAwsCloudwatchLogGroupsConfig",
]

publication.publish()
