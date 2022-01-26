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


class GlacierVault(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.glacier.GlacierVault",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/glacier_vault aws_glacier_vault}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        access_policy: typing.Optional[builtins.str] = None,
        notification: typing.Optional["GlacierVaultNotification"] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/glacier_vault aws_glacier_vault} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/glacier_vault#name GlacierVault#name}.
        :param access_policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/glacier_vault#access_policy GlacierVault#access_policy}.
        :param notification: notification block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/glacier_vault#notification GlacierVault#notification}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/glacier_vault#tags GlacierVault#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/glacier_vault#tags_all GlacierVault#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = GlacierVaultConfig(
            name=name,
            access_policy=access_policy,
            notification=notification,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putNotification")
    def put_notification(
        self,
        *,
        events: typing.Sequence[builtins.str],
        sns_topic: builtins.str,
    ) -> None:
        '''
        :param events: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/glacier_vault#events GlacierVault#events}.
        :param sns_topic: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/glacier_vault#sns_topic GlacierVault#sns_topic}.
        '''
        value = GlacierVaultNotification(events=events, sns_topic=sns_topic)

        return typing.cast(None, jsii.invoke(self, "putNotification", [value]))

    @jsii.member(jsii_name="resetAccessPolicy")
    def reset_access_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccessPolicy", []))

    @jsii.member(jsii_name="resetNotification")
    def reset_notification(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNotification", []))

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
    @jsii.member(jsii_name="location")
    def location(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "location"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="notification")
    def notification(self) -> "GlacierVaultNotificationOutputReference":
        return typing.cast("GlacierVaultNotificationOutputReference", jsii.get(self, "notification"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessPolicyInput")
    def access_policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accessPolicyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="notificationInput")
    def notification_input(self) -> typing.Optional["GlacierVaultNotification"]:
        return typing.cast(typing.Optional["GlacierVaultNotification"], jsii.get(self, "notificationInput"))

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
    @jsii.member(jsii_name="accessPolicy")
    def access_policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accessPolicy"))

    @access_policy.setter
    def access_policy(self, value: builtins.str) -> None:
        jsii.set(self, "accessPolicy", value)

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
    jsii_type="@cdktf/provider-aws.glacier.GlacierVaultConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "access_policy": "accessPolicy",
        "notification": "notification",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class GlacierVaultConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        access_policy: typing.Optional[builtins.str] = None,
        notification: typing.Optional["GlacierVaultNotification"] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS Glacier.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/glacier_vault#name GlacierVault#name}.
        :param access_policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/glacier_vault#access_policy GlacierVault#access_policy}.
        :param notification: notification block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/glacier_vault#notification GlacierVault#notification}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/glacier_vault#tags GlacierVault#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/glacier_vault#tags_all GlacierVault#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(notification, dict):
            notification = GlacierVaultNotification(**notification)
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
        if access_policy is not None:
            self._values["access_policy"] = access_policy
        if notification is not None:
            self._values["notification"] = notification
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/glacier_vault#name GlacierVault#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def access_policy(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/glacier_vault#access_policy GlacierVault#access_policy}.'''
        result = self._values.get("access_policy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def notification(self) -> typing.Optional["GlacierVaultNotification"]:
        '''notification block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/glacier_vault#notification GlacierVault#notification}
        '''
        result = self._values.get("notification")
        return typing.cast(typing.Optional["GlacierVaultNotification"], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/glacier_vault#tags GlacierVault#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/glacier_vault#tags_all GlacierVault#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GlacierVaultConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GlacierVaultLock(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.glacier.GlacierVaultLock",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/glacier_vault_lock aws_glacier_vault_lock}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        complete_lock: typing.Union[builtins.bool, cdktf.IResolvable],
        policy: builtins.str,
        vault_name: builtins.str,
        ignore_deletion_error: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/glacier_vault_lock aws_glacier_vault_lock} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param complete_lock: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/glacier_vault_lock#complete_lock GlacierVaultLock#complete_lock}.
        :param policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/glacier_vault_lock#policy GlacierVaultLock#policy}.
        :param vault_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/glacier_vault_lock#vault_name GlacierVaultLock#vault_name}.
        :param ignore_deletion_error: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/glacier_vault_lock#ignore_deletion_error GlacierVaultLock#ignore_deletion_error}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = GlacierVaultLockConfig(
            complete_lock=complete_lock,
            policy=policy,
            vault_name=vault_name,
            ignore_deletion_error=ignore_deletion_error,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetIgnoreDeletionError")
    def reset_ignore_deletion_error(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIgnoreDeletionError", []))

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
    @jsii.member(jsii_name="completeLockInput")
    def complete_lock_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "completeLockInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ignoreDeletionErrorInput")
    def ignore_deletion_error_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "ignoreDeletionErrorInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyInput")
    def policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "policyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vaultNameInput")
    def vault_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "vaultNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="completeLock")
    def complete_lock(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "completeLock"))

    @complete_lock.setter
    def complete_lock(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "completeLock", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ignoreDeletionError")
    def ignore_deletion_error(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "ignoreDeletionError"))

    @ignore_deletion_error.setter
    def ignore_deletion_error(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "ignoreDeletionError", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policy")
    def policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policy"))

    @policy.setter
    def policy(self, value: builtins.str) -> None:
        jsii.set(self, "policy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vaultName")
    def vault_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "vaultName"))

    @vault_name.setter
    def vault_name(self, value: builtins.str) -> None:
        jsii.set(self, "vaultName", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.glacier.GlacierVaultLockConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "complete_lock": "completeLock",
        "policy": "policy",
        "vault_name": "vaultName",
        "ignore_deletion_error": "ignoreDeletionError",
    },
)
class GlacierVaultLockConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        complete_lock: typing.Union[builtins.bool, cdktf.IResolvable],
        policy: builtins.str,
        vault_name: builtins.str,
        ignore_deletion_error: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''AWS Glacier.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param complete_lock: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/glacier_vault_lock#complete_lock GlacierVaultLock#complete_lock}.
        :param policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/glacier_vault_lock#policy GlacierVaultLock#policy}.
        :param vault_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/glacier_vault_lock#vault_name GlacierVaultLock#vault_name}.
        :param ignore_deletion_error: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/glacier_vault_lock#ignore_deletion_error GlacierVaultLock#ignore_deletion_error}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "complete_lock": complete_lock,
            "policy": policy,
            "vault_name": vault_name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if ignore_deletion_error is not None:
            self._values["ignore_deletion_error"] = ignore_deletion_error

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
    def complete_lock(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/glacier_vault_lock#complete_lock GlacierVaultLock#complete_lock}.'''
        result = self._values.get("complete_lock")
        assert result is not None, "Required property 'complete_lock' is missing"
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], result)

    @builtins.property
    def policy(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/glacier_vault_lock#policy GlacierVaultLock#policy}.'''
        result = self._values.get("policy")
        assert result is not None, "Required property 'policy' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def vault_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/glacier_vault_lock#vault_name GlacierVaultLock#vault_name}.'''
        result = self._values.get("vault_name")
        assert result is not None, "Required property 'vault_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ignore_deletion_error(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/glacier_vault_lock#ignore_deletion_error GlacierVaultLock#ignore_deletion_error}.'''
        result = self._values.get("ignore_deletion_error")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GlacierVaultLockConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.glacier.GlacierVaultNotification",
    jsii_struct_bases=[],
    name_mapping={"events": "events", "sns_topic": "snsTopic"},
)
class GlacierVaultNotification:
    def __init__(
        self,
        *,
        events: typing.Sequence[builtins.str],
        sns_topic: builtins.str,
    ) -> None:
        '''
        :param events: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/glacier_vault#events GlacierVault#events}.
        :param sns_topic: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/glacier_vault#sns_topic GlacierVault#sns_topic}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "events": events,
            "sns_topic": sns_topic,
        }

    @builtins.property
    def events(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/glacier_vault#events GlacierVault#events}.'''
        result = self._values.get("events")
        assert result is not None, "Required property 'events' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def sns_topic(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/glacier_vault#sns_topic GlacierVault#sns_topic}.'''
        result = self._values.get("sns_topic")
        assert result is not None, "Required property 'sns_topic' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GlacierVaultNotification(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GlacierVaultNotificationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.glacier.GlacierVaultNotificationOutputReference",
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
    @jsii.member(jsii_name="eventsInput")
    def events_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "eventsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snsTopicInput")
    def sns_topic_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "snsTopicInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="events")
    def events(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "events"))

    @events.setter
    def events(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "events", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snsTopic")
    def sns_topic(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "snsTopic"))

    @sns_topic.setter
    def sns_topic(self, value: builtins.str) -> None:
        jsii.set(self, "snsTopic", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[GlacierVaultNotification]:
        return typing.cast(typing.Optional[GlacierVaultNotification], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[GlacierVaultNotification]) -> None:
        jsii.set(self, "internalValue", value)


__all__ = [
    "GlacierVault",
    "GlacierVaultConfig",
    "GlacierVaultLock",
    "GlacierVaultLockConfig",
    "GlacierVaultNotification",
    "GlacierVaultNotificationOutputReference",
]

publication.publish()
