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


class BackupGlobalSettings(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.backup.BackupGlobalSettings",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/backup_global_settings aws_backup_global_settings}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        global_settings: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/backup_global_settings aws_backup_global_settings} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param global_settings: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_global_settings#global_settings BackupGlobalSettings#global_settings}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = BackupGlobalSettingsConfig(
            global_settings=global_settings,
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
    @jsii.member(jsii_name="globalSettingsInput")
    def global_settings_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "globalSettingsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="globalSettings")
    def global_settings(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "globalSettings"))

    @global_settings.setter
    def global_settings(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "globalSettings", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.backup.BackupGlobalSettingsConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "global_settings": "globalSettings",
    },
)
class BackupGlobalSettingsConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        global_settings: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        '''AWS Backup.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param global_settings: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_global_settings#global_settings BackupGlobalSettings#global_settings}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "global_settings": global_settings,
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
    def global_settings(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_global_settings#global_settings BackupGlobalSettings#global_settings}.'''
        result = self._values.get("global_settings")
        assert result is not None, "Required property 'global_settings' is missing"
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BackupGlobalSettingsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class BackupPlan(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.backup.BackupPlan",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/backup_plan aws_backup_plan}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        rule: typing.Sequence["BackupPlanRule"],
        advanced_backup_setting: typing.Optional[typing.Sequence["BackupPlanAdvancedBackupSetting"]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/backup_plan aws_backup_plan} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_plan#name BackupPlan#name}.
        :param rule: rule block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_plan#rule BackupPlan#rule}
        :param advanced_backup_setting: advanced_backup_setting block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_plan#advanced_backup_setting BackupPlan#advanced_backup_setting}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_plan#tags BackupPlan#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_plan#tags_all BackupPlan#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = BackupPlanConfig(
            name=name,
            rule=rule,
            advanced_backup_setting=advanced_backup_setting,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetAdvancedBackupSetting")
    def reset_advanced_backup_setting(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAdvancedBackupSetting", []))

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
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="advancedBackupSettingInput")
    def advanced_backup_setting_input(
        self,
    ) -> typing.Optional[typing.List["BackupPlanAdvancedBackupSetting"]]:
        return typing.cast(typing.Optional[typing.List["BackupPlanAdvancedBackupSetting"]], jsii.get(self, "advancedBackupSettingInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ruleInput")
    def rule_input(self) -> typing.Optional[typing.List["BackupPlanRule"]]:
        return typing.cast(typing.Optional[typing.List["BackupPlanRule"]], jsii.get(self, "ruleInput"))

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
    @jsii.member(jsii_name="advancedBackupSetting")
    def advanced_backup_setting(self) -> typing.List["BackupPlanAdvancedBackupSetting"]:
        return typing.cast(typing.List["BackupPlanAdvancedBackupSetting"], jsii.get(self, "advancedBackupSetting"))

    @advanced_backup_setting.setter
    def advanced_backup_setting(
        self,
        value: typing.List["BackupPlanAdvancedBackupSetting"],
    ) -> None:
        jsii.set(self, "advancedBackupSetting", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rule")
    def rule(self) -> typing.List["BackupPlanRule"]:
        return typing.cast(typing.List["BackupPlanRule"], jsii.get(self, "rule"))

    @rule.setter
    def rule(self, value: typing.List["BackupPlanRule"]) -> None:
        jsii.set(self, "rule", value)

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
    jsii_type="@cdktf/provider-aws.backup.BackupPlanAdvancedBackupSetting",
    jsii_struct_bases=[],
    name_mapping={"backup_options": "backupOptions", "resource_type": "resourceType"},
)
class BackupPlanAdvancedBackupSetting:
    def __init__(
        self,
        *,
        backup_options: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
        resource_type: builtins.str,
    ) -> None:
        '''
        :param backup_options: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_plan#backup_options BackupPlan#backup_options}.
        :param resource_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_plan#resource_type BackupPlan#resource_type}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "backup_options": backup_options,
            "resource_type": resource_type,
        }

    @builtins.property
    def backup_options(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_plan#backup_options BackupPlan#backup_options}.'''
        result = self._values.get("backup_options")
        assert result is not None, "Required property 'backup_options' is missing"
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def resource_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_plan#resource_type BackupPlan#resource_type}.'''
        result = self._values.get("resource_type")
        assert result is not None, "Required property 'resource_type' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BackupPlanAdvancedBackupSetting(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.backup.BackupPlanConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "rule": "rule",
        "advanced_backup_setting": "advancedBackupSetting",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class BackupPlanConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        rule: typing.Sequence["BackupPlanRule"],
        advanced_backup_setting: typing.Optional[typing.Sequence[BackupPlanAdvancedBackupSetting]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS Backup.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_plan#name BackupPlan#name}.
        :param rule: rule block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_plan#rule BackupPlan#rule}
        :param advanced_backup_setting: advanced_backup_setting block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_plan#advanced_backup_setting BackupPlan#advanced_backup_setting}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_plan#tags BackupPlan#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_plan#tags_all BackupPlan#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "rule": rule,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if advanced_backup_setting is not None:
            self._values["advanced_backup_setting"] = advanced_backup_setting
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
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_plan#name BackupPlan#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def rule(self) -> typing.List["BackupPlanRule"]:
        '''rule block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_plan#rule BackupPlan#rule}
        '''
        result = self._values.get("rule")
        assert result is not None, "Required property 'rule' is missing"
        return typing.cast(typing.List["BackupPlanRule"], result)

    @builtins.property
    def advanced_backup_setting(
        self,
    ) -> typing.Optional[typing.List[BackupPlanAdvancedBackupSetting]]:
        '''advanced_backup_setting block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_plan#advanced_backup_setting BackupPlan#advanced_backup_setting}
        '''
        result = self._values.get("advanced_backup_setting")
        return typing.cast(typing.Optional[typing.List[BackupPlanAdvancedBackupSetting]], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_plan#tags BackupPlan#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_plan#tags_all BackupPlan#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BackupPlanConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.backup.BackupPlanRule",
    jsii_struct_bases=[],
    name_mapping={
        "rule_name": "ruleName",
        "target_vault_name": "targetVaultName",
        "completion_window": "completionWindow",
        "copy_action": "copyAction",
        "enable_continuous_backup": "enableContinuousBackup",
        "lifecycle": "lifecycle",
        "recovery_point_tags": "recoveryPointTags",
        "schedule": "schedule",
        "start_window": "startWindow",
    },
)
class BackupPlanRule:
    def __init__(
        self,
        *,
        rule_name: builtins.str,
        target_vault_name: builtins.str,
        completion_window: typing.Optional[jsii.Number] = None,
        copy_action: typing.Optional[typing.Sequence["BackupPlanRuleCopyAction"]] = None,
        enable_continuous_backup: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        lifecycle: typing.Optional["BackupPlanRuleLifecycle"] = None,
        recovery_point_tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        schedule: typing.Optional[builtins.str] = None,
        start_window: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param rule_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_plan#rule_name BackupPlan#rule_name}.
        :param target_vault_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_plan#target_vault_name BackupPlan#target_vault_name}.
        :param completion_window: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_plan#completion_window BackupPlan#completion_window}.
        :param copy_action: copy_action block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_plan#copy_action BackupPlan#copy_action}
        :param enable_continuous_backup: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_plan#enable_continuous_backup BackupPlan#enable_continuous_backup}.
        :param lifecycle: lifecycle block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_plan#lifecycle BackupPlan#lifecycle}
        :param recovery_point_tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_plan#recovery_point_tags BackupPlan#recovery_point_tags}.
        :param schedule: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_plan#schedule BackupPlan#schedule}.
        :param start_window: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_plan#start_window BackupPlan#start_window}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = BackupPlanRuleLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "rule_name": rule_name,
            "target_vault_name": target_vault_name,
        }
        if completion_window is not None:
            self._values["completion_window"] = completion_window
        if copy_action is not None:
            self._values["copy_action"] = copy_action
        if enable_continuous_backup is not None:
            self._values["enable_continuous_backup"] = enable_continuous_backup
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if recovery_point_tags is not None:
            self._values["recovery_point_tags"] = recovery_point_tags
        if schedule is not None:
            self._values["schedule"] = schedule
        if start_window is not None:
            self._values["start_window"] = start_window

    @builtins.property
    def rule_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_plan#rule_name BackupPlan#rule_name}.'''
        result = self._values.get("rule_name")
        assert result is not None, "Required property 'rule_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def target_vault_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_plan#target_vault_name BackupPlan#target_vault_name}.'''
        result = self._values.get("target_vault_name")
        assert result is not None, "Required property 'target_vault_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def completion_window(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_plan#completion_window BackupPlan#completion_window}.'''
        result = self._values.get("completion_window")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def copy_action(self) -> typing.Optional[typing.List["BackupPlanRuleCopyAction"]]:
        '''copy_action block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_plan#copy_action BackupPlan#copy_action}
        '''
        result = self._values.get("copy_action")
        return typing.cast(typing.Optional[typing.List["BackupPlanRuleCopyAction"]], result)

    @builtins.property
    def enable_continuous_backup(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_plan#enable_continuous_backup BackupPlan#enable_continuous_backup}.'''
        result = self._values.get("enable_continuous_backup")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional["BackupPlanRuleLifecycle"]:
        '''lifecycle block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_plan#lifecycle BackupPlan#lifecycle}
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional["BackupPlanRuleLifecycle"], result)

    @builtins.property
    def recovery_point_tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_plan#recovery_point_tags BackupPlan#recovery_point_tags}.'''
        result = self._values.get("recovery_point_tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def schedule(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_plan#schedule BackupPlan#schedule}.'''
        result = self._values.get("schedule")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def start_window(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_plan#start_window BackupPlan#start_window}.'''
        result = self._values.get("start_window")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BackupPlanRule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.backup.BackupPlanRuleCopyAction",
    jsii_struct_bases=[],
    name_mapping={
        "destination_vault_arn": "destinationVaultArn",
        "lifecycle": "lifecycle",
    },
)
class BackupPlanRuleCopyAction:
    def __init__(
        self,
        *,
        destination_vault_arn: builtins.str,
        lifecycle: typing.Optional["BackupPlanRuleCopyActionLifecycle"] = None,
    ) -> None:
        '''
        :param destination_vault_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_plan#destination_vault_arn BackupPlan#destination_vault_arn}.
        :param lifecycle: lifecycle block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_plan#lifecycle BackupPlan#lifecycle}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = BackupPlanRuleCopyActionLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "destination_vault_arn": destination_vault_arn,
        }
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle

    @builtins.property
    def destination_vault_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_plan#destination_vault_arn BackupPlan#destination_vault_arn}.'''
        result = self._values.get("destination_vault_arn")
        assert result is not None, "Required property 'destination_vault_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def lifecycle(self) -> typing.Optional["BackupPlanRuleCopyActionLifecycle"]:
        '''lifecycle block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_plan#lifecycle BackupPlan#lifecycle}
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional["BackupPlanRuleCopyActionLifecycle"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BackupPlanRuleCopyAction(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.backup.BackupPlanRuleCopyActionLifecycle",
    jsii_struct_bases=[],
    name_mapping={
        "cold_storage_after": "coldStorageAfter",
        "delete_after": "deleteAfter",
    },
)
class BackupPlanRuleCopyActionLifecycle:
    def __init__(
        self,
        *,
        cold_storage_after: typing.Optional[jsii.Number] = None,
        delete_after: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param cold_storage_after: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_plan#cold_storage_after BackupPlan#cold_storage_after}.
        :param delete_after: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_plan#delete_after BackupPlan#delete_after}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if cold_storage_after is not None:
            self._values["cold_storage_after"] = cold_storage_after
        if delete_after is not None:
            self._values["delete_after"] = delete_after

    @builtins.property
    def cold_storage_after(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_plan#cold_storage_after BackupPlan#cold_storage_after}.'''
        result = self._values.get("cold_storage_after")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def delete_after(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_plan#delete_after BackupPlan#delete_after}.'''
        result = self._values.get("delete_after")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BackupPlanRuleCopyActionLifecycle(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class BackupPlanRuleCopyActionLifecycleOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.backup.BackupPlanRuleCopyActionLifecycleOutputReference",
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

    @jsii.member(jsii_name="resetColdStorageAfter")
    def reset_cold_storage_after(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetColdStorageAfter", []))

    @jsii.member(jsii_name="resetDeleteAfter")
    def reset_delete_after(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeleteAfter", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="coldStorageAfterInput")
    def cold_storage_after_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "coldStorageAfterInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deleteAfterInput")
    def delete_after_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "deleteAfterInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="coldStorageAfter")
    def cold_storage_after(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "coldStorageAfter"))

    @cold_storage_after.setter
    def cold_storage_after(self, value: jsii.Number) -> None:
        jsii.set(self, "coldStorageAfter", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deleteAfter")
    def delete_after(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "deleteAfter"))

    @delete_after.setter
    def delete_after(self, value: jsii.Number) -> None:
        jsii.set(self, "deleteAfter", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[BackupPlanRuleCopyActionLifecycle]:
        return typing.cast(typing.Optional[BackupPlanRuleCopyActionLifecycle], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[BackupPlanRuleCopyActionLifecycle],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.backup.BackupPlanRuleLifecycle",
    jsii_struct_bases=[],
    name_mapping={
        "cold_storage_after": "coldStorageAfter",
        "delete_after": "deleteAfter",
    },
)
class BackupPlanRuleLifecycle:
    def __init__(
        self,
        *,
        cold_storage_after: typing.Optional[jsii.Number] = None,
        delete_after: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param cold_storage_after: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_plan#cold_storage_after BackupPlan#cold_storage_after}.
        :param delete_after: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_plan#delete_after BackupPlan#delete_after}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if cold_storage_after is not None:
            self._values["cold_storage_after"] = cold_storage_after
        if delete_after is not None:
            self._values["delete_after"] = delete_after

    @builtins.property
    def cold_storage_after(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_plan#cold_storage_after BackupPlan#cold_storage_after}.'''
        result = self._values.get("cold_storage_after")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def delete_after(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_plan#delete_after BackupPlan#delete_after}.'''
        result = self._values.get("delete_after")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BackupPlanRuleLifecycle(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class BackupPlanRuleLifecycleOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.backup.BackupPlanRuleLifecycleOutputReference",
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

    @jsii.member(jsii_name="resetColdStorageAfter")
    def reset_cold_storage_after(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetColdStorageAfter", []))

    @jsii.member(jsii_name="resetDeleteAfter")
    def reset_delete_after(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeleteAfter", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="coldStorageAfterInput")
    def cold_storage_after_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "coldStorageAfterInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deleteAfterInput")
    def delete_after_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "deleteAfterInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="coldStorageAfter")
    def cold_storage_after(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "coldStorageAfter"))

    @cold_storage_after.setter
    def cold_storage_after(self, value: jsii.Number) -> None:
        jsii.set(self, "coldStorageAfter", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deleteAfter")
    def delete_after(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "deleteAfter"))

    @delete_after.setter
    def delete_after(self, value: jsii.Number) -> None:
        jsii.set(self, "deleteAfter", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[BackupPlanRuleLifecycle]:
        return typing.cast(typing.Optional[BackupPlanRuleLifecycle], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[BackupPlanRuleLifecycle]) -> None:
        jsii.set(self, "internalValue", value)


class BackupRegionSettings(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.backup.BackupRegionSettings",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/backup_region_settings aws_backup_region_settings}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        resource_type_opt_in_preference: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.bool]],
        resource_type_management_preference: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.bool]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/backup_region_settings aws_backup_region_settings} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param resource_type_opt_in_preference: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_region_settings#resource_type_opt_in_preference BackupRegionSettings#resource_type_opt_in_preference}.
        :param resource_type_management_preference: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_region_settings#resource_type_management_preference BackupRegionSettings#resource_type_management_preference}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = BackupRegionSettingsConfig(
            resource_type_opt_in_preference=resource_type_opt_in_preference,
            resource_type_management_preference=resource_type_management_preference,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetResourceTypeManagementPreference")
    def reset_resource_type_management_preference(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResourceTypeManagementPreference", []))

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
    @jsii.member(jsii_name="resourceTypeManagementPreferenceInput")
    def resource_type_management_preference_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.bool]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.bool]]], jsii.get(self, "resourceTypeManagementPreferenceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceTypeOptInPreferenceInput")
    def resource_type_opt_in_preference_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.bool]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.bool]]], jsii.get(self, "resourceTypeOptInPreferenceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceTypeManagementPreference")
    def resource_type_management_preference(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.bool]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.bool]], jsii.get(self, "resourceTypeManagementPreference"))

    @resource_type_management_preference.setter
    def resource_type_management_preference(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.bool]],
    ) -> None:
        jsii.set(self, "resourceTypeManagementPreference", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceTypeOptInPreference")
    def resource_type_opt_in_preference(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.bool]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.bool]], jsii.get(self, "resourceTypeOptInPreference"))

    @resource_type_opt_in_preference.setter
    def resource_type_opt_in_preference(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.bool]],
    ) -> None:
        jsii.set(self, "resourceTypeOptInPreference", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.backup.BackupRegionSettingsConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "resource_type_opt_in_preference": "resourceTypeOptInPreference",
        "resource_type_management_preference": "resourceTypeManagementPreference",
    },
)
class BackupRegionSettingsConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        resource_type_opt_in_preference: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.bool]],
        resource_type_management_preference: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.bool]]] = None,
    ) -> None:
        '''AWS Backup.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param resource_type_opt_in_preference: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_region_settings#resource_type_opt_in_preference BackupRegionSettings#resource_type_opt_in_preference}.
        :param resource_type_management_preference: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_region_settings#resource_type_management_preference BackupRegionSettings#resource_type_management_preference}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "resource_type_opt_in_preference": resource_type_opt_in_preference,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if resource_type_management_preference is not None:
            self._values["resource_type_management_preference"] = resource_type_management_preference

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
    def resource_type_opt_in_preference(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.bool]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_region_settings#resource_type_opt_in_preference BackupRegionSettings#resource_type_opt_in_preference}.'''
        result = self._values.get("resource_type_opt_in_preference")
        assert result is not None, "Required property 'resource_type_opt_in_preference' is missing"
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.bool]], result)

    @builtins.property
    def resource_type_management_preference(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.bool]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_region_settings#resource_type_management_preference BackupRegionSettings#resource_type_management_preference}.'''
        result = self._values.get("resource_type_management_preference")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.bool]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BackupRegionSettingsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class BackupSelection(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.backup.BackupSelection",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/backup_selection aws_backup_selection}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        iam_role_arn: builtins.str,
        name: builtins.str,
        plan_id: builtins.str,
        condition: typing.Optional[typing.Sequence["BackupSelectionCondition"]] = None,
        not_resources: typing.Optional[typing.Sequence[builtins.str]] = None,
        resources: typing.Optional[typing.Sequence[builtins.str]] = None,
        selection_tag: typing.Optional[typing.Sequence["BackupSelectionSelectionTag"]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/backup_selection aws_backup_selection} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param iam_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_selection#iam_role_arn BackupSelection#iam_role_arn}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_selection#name BackupSelection#name}.
        :param plan_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_selection#plan_id BackupSelection#plan_id}.
        :param condition: condition block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_selection#condition BackupSelection#condition}
        :param not_resources: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_selection#not_resources BackupSelection#not_resources}.
        :param resources: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_selection#resources BackupSelection#resources}.
        :param selection_tag: selection_tag block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_selection#selection_tag BackupSelection#selection_tag}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = BackupSelectionConfig(
            iam_role_arn=iam_role_arn,
            name=name,
            plan_id=plan_id,
            condition=condition,
            not_resources=not_resources,
            resources=resources,
            selection_tag=selection_tag,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetCondition")
    def reset_condition(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCondition", []))

    @jsii.member(jsii_name="resetNotResources")
    def reset_not_resources(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNotResources", []))

    @jsii.member(jsii_name="resetResources")
    def reset_resources(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResources", []))

    @jsii.member(jsii_name="resetSelectionTag")
    def reset_selection_tag(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSelectionTag", []))

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
    @jsii.member(jsii_name="conditionInput")
    def condition_input(
        self,
    ) -> typing.Optional[typing.List["BackupSelectionCondition"]]:
        return typing.cast(typing.Optional[typing.List["BackupSelectionCondition"]], jsii.get(self, "conditionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="iamRoleArnInput")
    def iam_role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "iamRoleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="notResourcesInput")
    def not_resources_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "notResourcesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="planIdInput")
    def plan_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "planIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourcesInput")
    def resources_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "resourcesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="selectionTagInput")
    def selection_tag_input(
        self,
    ) -> typing.Optional[typing.List["BackupSelectionSelectionTag"]]:
        return typing.cast(typing.Optional[typing.List["BackupSelectionSelectionTag"]], jsii.get(self, "selectionTagInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="condition")
    def condition(self) -> typing.List["BackupSelectionCondition"]:
        return typing.cast(typing.List["BackupSelectionCondition"], jsii.get(self, "condition"))

    @condition.setter
    def condition(self, value: typing.List["BackupSelectionCondition"]) -> None:
        jsii.set(self, "condition", value)

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
    @jsii.member(jsii_name="notResources")
    def not_resources(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "notResources"))

    @not_resources.setter
    def not_resources(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "notResources", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="planId")
    def plan_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "planId"))

    @plan_id.setter
    def plan_id(self, value: builtins.str) -> None:
        jsii.set(self, "planId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resources")
    def resources(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "resources"))

    @resources.setter
    def resources(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "resources", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="selectionTag")
    def selection_tag(self) -> typing.List["BackupSelectionSelectionTag"]:
        return typing.cast(typing.List["BackupSelectionSelectionTag"], jsii.get(self, "selectionTag"))

    @selection_tag.setter
    def selection_tag(self, value: typing.List["BackupSelectionSelectionTag"]) -> None:
        jsii.set(self, "selectionTag", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.backup.BackupSelectionCondition",
    jsii_struct_bases=[],
    name_mapping={
        "string_equals": "stringEquals",
        "string_like": "stringLike",
        "string_not_equals": "stringNotEquals",
        "string_not_like": "stringNotLike",
    },
)
class BackupSelectionCondition:
    def __init__(
        self,
        *,
        string_equals: typing.Optional[typing.Sequence["BackupSelectionConditionStringEquals"]] = None,
        string_like: typing.Optional[typing.Sequence["BackupSelectionConditionStringLike"]] = None,
        string_not_equals: typing.Optional[typing.Sequence["BackupSelectionConditionStringNotEquals"]] = None,
        string_not_like: typing.Optional[typing.Sequence["BackupSelectionConditionStringNotLike"]] = None,
    ) -> None:
        '''
        :param string_equals: string_equals block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_selection#string_equals BackupSelection#string_equals}
        :param string_like: string_like block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_selection#string_like BackupSelection#string_like}
        :param string_not_equals: string_not_equals block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_selection#string_not_equals BackupSelection#string_not_equals}
        :param string_not_like: string_not_like block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_selection#string_not_like BackupSelection#string_not_like}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if string_equals is not None:
            self._values["string_equals"] = string_equals
        if string_like is not None:
            self._values["string_like"] = string_like
        if string_not_equals is not None:
            self._values["string_not_equals"] = string_not_equals
        if string_not_like is not None:
            self._values["string_not_like"] = string_not_like

    @builtins.property
    def string_equals(
        self,
    ) -> typing.Optional[typing.List["BackupSelectionConditionStringEquals"]]:
        '''string_equals block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_selection#string_equals BackupSelection#string_equals}
        '''
        result = self._values.get("string_equals")
        return typing.cast(typing.Optional[typing.List["BackupSelectionConditionStringEquals"]], result)

    @builtins.property
    def string_like(
        self,
    ) -> typing.Optional[typing.List["BackupSelectionConditionStringLike"]]:
        '''string_like block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_selection#string_like BackupSelection#string_like}
        '''
        result = self._values.get("string_like")
        return typing.cast(typing.Optional[typing.List["BackupSelectionConditionStringLike"]], result)

    @builtins.property
    def string_not_equals(
        self,
    ) -> typing.Optional[typing.List["BackupSelectionConditionStringNotEquals"]]:
        '''string_not_equals block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_selection#string_not_equals BackupSelection#string_not_equals}
        '''
        result = self._values.get("string_not_equals")
        return typing.cast(typing.Optional[typing.List["BackupSelectionConditionStringNotEquals"]], result)

    @builtins.property
    def string_not_like(
        self,
    ) -> typing.Optional[typing.List["BackupSelectionConditionStringNotLike"]]:
        '''string_not_like block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_selection#string_not_like BackupSelection#string_not_like}
        '''
        result = self._values.get("string_not_like")
        return typing.cast(typing.Optional[typing.List["BackupSelectionConditionStringNotLike"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BackupSelectionCondition(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.backup.BackupSelectionConditionStringEquals",
    jsii_struct_bases=[],
    name_mapping={"key": "key", "value": "value"},
)
class BackupSelectionConditionStringEquals:
    def __init__(self, *, key: builtins.str, value: builtins.str) -> None:
        '''
        :param key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_selection#key BackupSelection#key}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_selection#value BackupSelection#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "key": key,
            "value": value,
        }

    @builtins.property
    def key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_selection#key BackupSelection#key}.'''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_selection#value BackupSelection#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BackupSelectionConditionStringEquals(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.backup.BackupSelectionConditionStringLike",
    jsii_struct_bases=[],
    name_mapping={"key": "key", "value": "value"},
)
class BackupSelectionConditionStringLike:
    def __init__(self, *, key: builtins.str, value: builtins.str) -> None:
        '''
        :param key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_selection#key BackupSelection#key}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_selection#value BackupSelection#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "key": key,
            "value": value,
        }

    @builtins.property
    def key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_selection#key BackupSelection#key}.'''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_selection#value BackupSelection#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BackupSelectionConditionStringLike(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.backup.BackupSelectionConditionStringNotEquals",
    jsii_struct_bases=[],
    name_mapping={"key": "key", "value": "value"},
)
class BackupSelectionConditionStringNotEquals:
    def __init__(self, *, key: builtins.str, value: builtins.str) -> None:
        '''
        :param key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_selection#key BackupSelection#key}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_selection#value BackupSelection#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "key": key,
            "value": value,
        }

    @builtins.property
    def key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_selection#key BackupSelection#key}.'''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_selection#value BackupSelection#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BackupSelectionConditionStringNotEquals(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.backup.BackupSelectionConditionStringNotLike",
    jsii_struct_bases=[],
    name_mapping={"key": "key", "value": "value"},
)
class BackupSelectionConditionStringNotLike:
    def __init__(self, *, key: builtins.str, value: builtins.str) -> None:
        '''
        :param key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_selection#key BackupSelection#key}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_selection#value BackupSelection#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "key": key,
            "value": value,
        }

    @builtins.property
    def key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_selection#key BackupSelection#key}.'''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_selection#value BackupSelection#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BackupSelectionConditionStringNotLike(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.backup.BackupSelectionConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "iam_role_arn": "iamRoleArn",
        "name": "name",
        "plan_id": "planId",
        "condition": "condition",
        "not_resources": "notResources",
        "resources": "resources",
        "selection_tag": "selectionTag",
    },
)
class BackupSelectionConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        iam_role_arn: builtins.str,
        name: builtins.str,
        plan_id: builtins.str,
        condition: typing.Optional[typing.Sequence[BackupSelectionCondition]] = None,
        not_resources: typing.Optional[typing.Sequence[builtins.str]] = None,
        resources: typing.Optional[typing.Sequence[builtins.str]] = None,
        selection_tag: typing.Optional[typing.Sequence["BackupSelectionSelectionTag"]] = None,
    ) -> None:
        '''AWS Backup.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param iam_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_selection#iam_role_arn BackupSelection#iam_role_arn}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_selection#name BackupSelection#name}.
        :param plan_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_selection#plan_id BackupSelection#plan_id}.
        :param condition: condition block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_selection#condition BackupSelection#condition}
        :param not_resources: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_selection#not_resources BackupSelection#not_resources}.
        :param resources: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_selection#resources BackupSelection#resources}.
        :param selection_tag: selection_tag block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_selection#selection_tag BackupSelection#selection_tag}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "iam_role_arn": iam_role_arn,
            "name": name,
            "plan_id": plan_id,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if condition is not None:
            self._values["condition"] = condition
        if not_resources is not None:
            self._values["not_resources"] = not_resources
        if resources is not None:
            self._values["resources"] = resources
        if selection_tag is not None:
            self._values["selection_tag"] = selection_tag

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
    def iam_role_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_selection#iam_role_arn BackupSelection#iam_role_arn}.'''
        result = self._values.get("iam_role_arn")
        assert result is not None, "Required property 'iam_role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_selection#name BackupSelection#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def plan_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_selection#plan_id BackupSelection#plan_id}.'''
        result = self._values.get("plan_id")
        assert result is not None, "Required property 'plan_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def condition(self) -> typing.Optional[typing.List[BackupSelectionCondition]]:
        '''condition block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_selection#condition BackupSelection#condition}
        '''
        result = self._values.get("condition")
        return typing.cast(typing.Optional[typing.List[BackupSelectionCondition]], result)

    @builtins.property
    def not_resources(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_selection#not_resources BackupSelection#not_resources}.'''
        result = self._values.get("not_resources")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def resources(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_selection#resources BackupSelection#resources}.'''
        result = self._values.get("resources")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def selection_tag(
        self,
    ) -> typing.Optional[typing.List["BackupSelectionSelectionTag"]]:
        '''selection_tag block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_selection#selection_tag BackupSelection#selection_tag}
        '''
        result = self._values.get("selection_tag")
        return typing.cast(typing.Optional[typing.List["BackupSelectionSelectionTag"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BackupSelectionConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.backup.BackupSelectionSelectionTag",
    jsii_struct_bases=[],
    name_mapping={"key": "key", "type": "type", "value": "value"},
)
class BackupSelectionSelectionTag:
    def __init__(
        self,
        *,
        key: builtins.str,
        type: builtins.str,
        value: builtins.str,
    ) -> None:
        '''
        :param key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_selection#key BackupSelection#key}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_selection#type BackupSelection#type}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_selection#value BackupSelection#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "key": key,
            "type": type,
            "value": value,
        }

    @builtins.property
    def key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_selection#key BackupSelection#key}.'''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_selection#type BackupSelection#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_selection#value BackupSelection#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BackupSelectionSelectionTag(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class BackupVault(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.backup.BackupVault",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/backup_vault aws_backup_vault}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        kms_key_arn: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/backup_vault aws_backup_vault} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_vault#name BackupVault#name}.
        :param kms_key_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_vault#kms_key_arn BackupVault#kms_key_arn}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_vault#tags BackupVault#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_vault#tags_all BackupVault#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = BackupVaultConfig(
            name=name,
            kms_key_arn=kms_key_arn,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetKmsKeyArn")
    def reset_kms_key_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKmsKeyArn", []))

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
    @jsii.member(jsii_name="recoveryPoints")
    def recovery_points(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "recoveryPoints"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyArnInput")
    def kms_key_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kmsKeyArnInput"))

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
    @jsii.member(jsii_name="kmsKeyArn")
    def kms_key_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsKeyArn"))

    @kms_key_arn.setter
    def kms_key_arn(self, value: builtins.str) -> None:
        jsii.set(self, "kmsKeyArn", value)

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
    jsii_type="@cdktf/provider-aws.backup.BackupVaultConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "kms_key_arn": "kmsKeyArn",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class BackupVaultConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        kms_key_arn: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS Backup.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_vault#name BackupVault#name}.
        :param kms_key_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_vault#kms_key_arn BackupVault#kms_key_arn}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_vault#tags BackupVault#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_vault#tags_all BackupVault#tags_all}.
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
        if kms_key_arn is not None:
            self._values["kms_key_arn"] = kms_key_arn
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
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_vault#name BackupVault#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def kms_key_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_vault#kms_key_arn BackupVault#kms_key_arn}.'''
        result = self._values.get("kms_key_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_vault#tags BackupVault#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_vault#tags_all BackupVault#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BackupVaultConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class BackupVaultLockConfiguration(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.backup.BackupVaultLockConfiguration",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/backup_vault_lock_configuration aws_backup_vault_lock_configuration}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        backup_vault_name: builtins.str,
        changeable_for_days: typing.Optional[jsii.Number] = None,
        max_retention_days: typing.Optional[jsii.Number] = None,
        min_retention_days: typing.Optional[jsii.Number] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/backup_vault_lock_configuration aws_backup_vault_lock_configuration} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param backup_vault_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_vault_lock_configuration#backup_vault_name BackupVaultLockConfiguration#backup_vault_name}.
        :param changeable_for_days: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_vault_lock_configuration#changeable_for_days BackupVaultLockConfiguration#changeable_for_days}.
        :param max_retention_days: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_vault_lock_configuration#max_retention_days BackupVaultLockConfiguration#max_retention_days}.
        :param min_retention_days: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_vault_lock_configuration#min_retention_days BackupVaultLockConfiguration#min_retention_days}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = BackupVaultLockConfigurationConfig(
            backup_vault_name=backup_vault_name,
            changeable_for_days=changeable_for_days,
            max_retention_days=max_retention_days,
            min_retention_days=min_retention_days,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetChangeableForDays")
    def reset_changeable_for_days(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetChangeableForDays", []))

    @jsii.member(jsii_name="resetMaxRetentionDays")
    def reset_max_retention_days(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxRetentionDays", []))

    @jsii.member(jsii_name="resetMinRetentionDays")
    def reset_min_retention_days(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinRetentionDays", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="backupVaultArn")
    def backup_vault_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "backupVaultArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="backupVaultNameInput")
    def backup_vault_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "backupVaultNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="changeableForDaysInput")
    def changeable_for_days_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "changeableForDaysInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxRetentionDaysInput")
    def max_retention_days_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxRetentionDaysInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="minRetentionDaysInput")
    def min_retention_days_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minRetentionDaysInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="backupVaultName")
    def backup_vault_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "backupVaultName"))

    @backup_vault_name.setter
    def backup_vault_name(self, value: builtins.str) -> None:
        jsii.set(self, "backupVaultName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="changeableForDays")
    def changeable_for_days(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "changeableForDays"))

    @changeable_for_days.setter
    def changeable_for_days(self, value: jsii.Number) -> None:
        jsii.set(self, "changeableForDays", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxRetentionDays")
    def max_retention_days(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxRetentionDays"))

    @max_retention_days.setter
    def max_retention_days(self, value: jsii.Number) -> None:
        jsii.set(self, "maxRetentionDays", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="minRetentionDays")
    def min_retention_days(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minRetentionDays"))

    @min_retention_days.setter
    def min_retention_days(self, value: jsii.Number) -> None:
        jsii.set(self, "minRetentionDays", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.backup.BackupVaultLockConfigurationConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "backup_vault_name": "backupVaultName",
        "changeable_for_days": "changeableForDays",
        "max_retention_days": "maxRetentionDays",
        "min_retention_days": "minRetentionDays",
    },
)
class BackupVaultLockConfigurationConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        backup_vault_name: builtins.str,
        changeable_for_days: typing.Optional[jsii.Number] = None,
        max_retention_days: typing.Optional[jsii.Number] = None,
        min_retention_days: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''AWS Backup.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param backup_vault_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_vault_lock_configuration#backup_vault_name BackupVaultLockConfiguration#backup_vault_name}.
        :param changeable_for_days: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_vault_lock_configuration#changeable_for_days BackupVaultLockConfiguration#changeable_for_days}.
        :param max_retention_days: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_vault_lock_configuration#max_retention_days BackupVaultLockConfiguration#max_retention_days}.
        :param min_retention_days: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_vault_lock_configuration#min_retention_days BackupVaultLockConfiguration#min_retention_days}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "backup_vault_name": backup_vault_name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if changeable_for_days is not None:
            self._values["changeable_for_days"] = changeable_for_days
        if max_retention_days is not None:
            self._values["max_retention_days"] = max_retention_days
        if min_retention_days is not None:
            self._values["min_retention_days"] = min_retention_days

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
    def backup_vault_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_vault_lock_configuration#backup_vault_name BackupVaultLockConfiguration#backup_vault_name}.'''
        result = self._values.get("backup_vault_name")
        assert result is not None, "Required property 'backup_vault_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def changeable_for_days(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_vault_lock_configuration#changeable_for_days BackupVaultLockConfiguration#changeable_for_days}.'''
        result = self._values.get("changeable_for_days")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_retention_days(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_vault_lock_configuration#max_retention_days BackupVaultLockConfiguration#max_retention_days}.'''
        result = self._values.get("max_retention_days")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_retention_days(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_vault_lock_configuration#min_retention_days BackupVaultLockConfiguration#min_retention_days}.'''
        result = self._values.get("min_retention_days")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BackupVaultLockConfigurationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class BackupVaultNotifications(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.backup.BackupVaultNotifications",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/backup_vault_notifications aws_backup_vault_notifications}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        backup_vault_events: typing.Sequence[builtins.str],
        backup_vault_name: builtins.str,
        sns_topic_arn: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/backup_vault_notifications aws_backup_vault_notifications} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param backup_vault_events: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_vault_notifications#backup_vault_events BackupVaultNotifications#backup_vault_events}.
        :param backup_vault_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_vault_notifications#backup_vault_name BackupVaultNotifications#backup_vault_name}.
        :param sns_topic_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_vault_notifications#sns_topic_arn BackupVaultNotifications#sns_topic_arn}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = BackupVaultNotificationsConfig(
            backup_vault_events=backup_vault_events,
            backup_vault_name=backup_vault_name,
            sns_topic_arn=sns_topic_arn,
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
    @jsii.member(jsii_name="backupVaultArn")
    def backup_vault_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "backupVaultArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="backupVaultEventsInput")
    def backup_vault_events_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "backupVaultEventsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="backupVaultNameInput")
    def backup_vault_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "backupVaultNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snsTopicArnInput")
    def sns_topic_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "snsTopicArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="backupVaultEvents")
    def backup_vault_events(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "backupVaultEvents"))

    @backup_vault_events.setter
    def backup_vault_events(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "backupVaultEvents", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="backupVaultName")
    def backup_vault_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "backupVaultName"))

    @backup_vault_name.setter
    def backup_vault_name(self, value: builtins.str) -> None:
        jsii.set(self, "backupVaultName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snsTopicArn")
    def sns_topic_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "snsTopicArn"))

    @sns_topic_arn.setter
    def sns_topic_arn(self, value: builtins.str) -> None:
        jsii.set(self, "snsTopicArn", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.backup.BackupVaultNotificationsConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "backup_vault_events": "backupVaultEvents",
        "backup_vault_name": "backupVaultName",
        "sns_topic_arn": "snsTopicArn",
    },
)
class BackupVaultNotificationsConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        backup_vault_events: typing.Sequence[builtins.str],
        backup_vault_name: builtins.str,
        sns_topic_arn: builtins.str,
    ) -> None:
        '''AWS Backup.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param backup_vault_events: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_vault_notifications#backup_vault_events BackupVaultNotifications#backup_vault_events}.
        :param backup_vault_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_vault_notifications#backup_vault_name BackupVaultNotifications#backup_vault_name}.
        :param sns_topic_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_vault_notifications#sns_topic_arn BackupVaultNotifications#sns_topic_arn}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "backup_vault_events": backup_vault_events,
            "backup_vault_name": backup_vault_name,
            "sns_topic_arn": sns_topic_arn,
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
    def backup_vault_events(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_vault_notifications#backup_vault_events BackupVaultNotifications#backup_vault_events}.'''
        result = self._values.get("backup_vault_events")
        assert result is not None, "Required property 'backup_vault_events' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def backup_vault_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_vault_notifications#backup_vault_name BackupVaultNotifications#backup_vault_name}.'''
        result = self._values.get("backup_vault_name")
        assert result is not None, "Required property 'backup_vault_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def sns_topic_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_vault_notifications#sns_topic_arn BackupVaultNotifications#sns_topic_arn}.'''
        result = self._values.get("sns_topic_arn")
        assert result is not None, "Required property 'sns_topic_arn' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BackupVaultNotificationsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class BackupVaultPolicy(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.backup.BackupVaultPolicy",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/backup_vault_policy aws_backup_vault_policy}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        backup_vault_name: builtins.str,
        policy: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/backup_vault_policy aws_backup_vault_policy} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param backup_vault_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_vault_policy#backup_vault_name BackupVaultPolicy#backup_vault_name}.
        :param policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_vault_policy#policy BackupVaultPolicy#policy}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = BackupVaultPolicyConfig(
            backup_vault_name=backup_vault_name,
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
    @jsii.member(jsii_name="backupVaultArn")
    def backup_vault_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "backupVaultArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="backupVaultNameInput")
    def backup_vault_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "backupVaultNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyInput")
    def policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "policyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="backupVaultName")
    def backup_vault_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "backupVaultName"))

    @backup_vault_name.setter
    def backup_vault_name(self, value: builtins.str) -> None:
        jsii.set(self, "backupVaultName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policy")
    def policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policy"))

    @policy.setter
    def policy(self, value: builtins.str) -> None:
        jsii.set(self, "policy", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.backup.BackupVaultPolicyConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "backup_vault_name": "backupVaultName",
        "policy": "policy",
    },
)
class BackupVaultPolicyConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        backup_vault_name: builtins.str,
        policy: builtins.str,
    ) -> None:
        '''AWS Backup.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param backup_vault_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_vault_policy#backup_vault_name BackupVaultPolicy#backup_vault_name}.
        :param policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_vault_policy#policy BackupVaultPolicy#policy}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "backup_vault_name": backup_vault_name,
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
    def backup_vault_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_vault_policy#backup_vault_name BackupVaultPolicy#backup_vault_name}.'''
        result = self._values.get("backup_vault_name")
        assert result is not None, "Required property 'backup_vault_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def policy(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/backup_vault_policy#policy BackupVaultPolicy#policy}.'''
        result = self._values.get("policy")
        assert result is not None, "Required property 'policy' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BackupVaultPolicyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsBackupPlan(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.backup.DataAwsBackupPlan",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/backup_plan aws_backup_plan}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        plan_id: builtins.str,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/backup_plan aws_backup_plan} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param plan_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/backup_plan#plan_id DataAwsBackupPlan#plan_id}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/backup_plan#tags DataAwsBackupPlan#tags}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsBackupPlanConfig(
            plan_id=plan_id,
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
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="planIdInput")
    def plan_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "planIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="planId")
    def plan_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "planId"))

    @plan_id.setter
    def plan_id(self, value: builtins.str) -> None:
        jsii.set(self, "planId", value)

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
    jsii_type="@cdktf/provider-aws.backup.DataAwsBackupPlanConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "plan_id": "planId",
        "tags": "tags",
    },
)
class DataAwsBackupPlanConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        plan_id: builtins.str,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS Backup.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param plan_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/backup_plan#plan_id DataAwsBackupPlan#plan_id}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/backup_plan#tags DataAwsBackupPlan#tags}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "plan_id": plan_id,
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
    def plan_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/backup_plan#plan_id DataAwsBackupPlan#plan_id}.'''
        result = self._values.get("plan_id")
        assert result is not None, "Required property 'plan_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/backup_plan#tags DataAwsBackupPlan#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsBackupPlanConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsBackupSelection(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.backup.DataAwsBackupSelection",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/backup_selection aws_backup_selection}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        plan_id: builtins.str,
        selection_id: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/backup_selection aws_backup_selection} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param plan_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/backup_selection#plan_id DataAwsBackupSelection#plan_id}.
        :param selection_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/backup_selection#selection_id DataAwsBackupSelection#selection_id}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsBackupSelectionConfig(
            plan_id=plan_id,
            selection_id=selection_id,
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
    @jsii.member(jsii_name="iamRoleArn")
    def iam_role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "iamRoleArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resources")
    def resources(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "resources"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="planIdInput")
    def plan_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "planIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="selectionIdInput")
    def selection_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "selectionIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="planId")
    def plan_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "planId"))

    @plan_id.setter
    def plan_id(self, value: builtins.str) -> None:
        jsii.set(self, "planId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="selectionId")
    def selection_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "selectionId"))

    @selection_id.setter
    def selection_id(self, value: builtins.str) -> None:
        jsii.set(self, "selectionId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.backup.DataAwsBackupSelectionConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "plan_id": "planId",
        "selection_id": "selectionId",
    },
)
class DataAwsBackupSelectionConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        plan_id: builtins.str,
        selection_id: builtins.str,
    ) -> None:
        '''AWS Backup.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param plan_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/backup_selection#plan_id DataAwsBackupSelection#plan_id}.
        :param selection_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/backup_selection#selection_id DataAwsBackupSelection#selection_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "plan_id": plan_id,
            "selection_id": selection_id,
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
    def plan_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/backup_selection#plan_id DataAwsBackupSelection#plan_id}.'''
        result = self._values.get("plan_id")
        assert result is not None, "Required property 'plan_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def selection_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/backup_selection#selection_id DataAwsBackupSelection#selection_id}.'''
        result = self._values.get("selection_id")
        assert result is not None, "Required property 'selection_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsBackupSelectionConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsBackupVault(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.backup.DataAwsBackupVault",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/backup_vault aws_backup_vault}.'''

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
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/backup_vault aws_backup_vault} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/backup_vault#name DataAwsBackupVault#name}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/backup_vault#tags DataAwsBackupVault#tags}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsBackupVaultConfig(
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
    @jsii.member(jsii_name="kmsKeyArn")
    def kms_key_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsKeyArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="recoveryPoints")
    def recovery_points(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "recoveryPoints"))

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
    jsii_type="@cdktf/provider-aws.backup.DataAwsBackupVaultConfig",
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
class DataAwsBackupVaultConfig(cdktf.TerraformMetaArguments):
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
        '''AWS Backup.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/backup_vault#name DataAwsBackupVault#name}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/backup_vault#tags DataAwsBackupVault#tags}.
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/backup_vault#name DataAwsBackupVault#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/backup_vault#tags DataAwsBackupVault#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsBackupVaultConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "BackupGlobalSettings",
    "BackupGlobalSettingsConfig",
    "BackupPlan",
    "BackupPlanAdvancedBackupSetting",
    "BackupPlanConfig",
    "BackupPlanRule",
    "BackupPlanRuleCopyAction",
    "BackupPlanRuleCopyActionLifecycle",
    "BackupPlanRuleCopyActionLifecycleOutputReference",
    "BackupPlanRuleLifecycle",
    "BackupPlanRuleLifecycleOutputReference",
    "BackupRegionSettings",
    "BackupRegionSettingsConfig",
    "BackupSelection",
    "BackupSelectionCondition",
    "BackupSelectionConditionStringEquals",
    "BackupSelectionConditionStringLike",
    "BackupSelectionConditionStringNotEquals",
    "BackupSelectionConditionStringNotLike",
    "BackupSelectionConfig",
    "BackupSelectionSelectionTag",
    "BackupVault",
    "BackupVaultConfig",
    "BackupVaultLockConfiguration",
    "BackupVaultLockConfigurationConfig",
    "BackupVaultNotifications",
    "BackupVaultNotificationsConfig",
    "BackupVaultPolicy",
    "BackupVaultPolicyConfig",
    "DataAwsBackupPlan",
    "DataAwsBackupPlanConfig",
    "DataAwsBackupSelection",
    "DataAwsBackupSelectionConfig",
    "DataAwsBackupVault",
    "DataAwsBackupVaultConfig",
]

publication.publish()
