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


class GameliftAlias(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.gamelift.GameliftAlias",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/gamelift_alias aws_gamelift_alias}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        routing_strategy: "GameliftAliasRoutingStrategy",
        description: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/gamelift_alias aws_gamelift_alias} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_alias#name GameliftAlias#name}.
        :param routing_strategy: routing_strategy block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_alias#routing_strategy GameliftAlias#routing_strategy}
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_alias#description GameliftAlias#description}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_alias#tags GameliftAlias#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_alias#tags_all GameliftAlias#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = GameliftAliasConfig(
            name=name,
            routing_strategy=routing_strategy,
            description=description,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putRoutingStrategy")
    def put_routing_strategy(
        self,
        *,
        type: builtins.str,
        fleet_id: typing.Optional[builtins.str] = None,
        message: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_alias#type GameliftAlias#type}.
        :param fleet_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_alias#fleet_id GameliftAlias#fleet_id}.
        :param message: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_alias#message GameliftAlias#message}.
        '''
        value = GameliftAliasRoutingStrategy(
            type=type, fleet_id=fleet_id, message=message
        )

        return typing.cast(None, jsii.invoke(self, "putRoutingStrategy", [value]))

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
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="routingStrategy")
    def routing_strategy(self) -> "GameliftAliasRoutingStrategyOutputReference":
        return typing.cast("GameliftAliasRoutingStrategyOutputReference", jsii.get(self, "routingStrategy"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="routingStrategyInput")
    def routing_strategy_input(self) -> typing.Optional["GameliftAliasRoutingStrategy"]:
        return typing.cast(typing.Optional["GameliftAliasRoutingStrategy"], jsii.get(self, "routingStrategyInput"))

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
    jsii_type="@cdktf/provider-aws.gamelift.GameliftAliasConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "routing_strategy": "routingStrategy",
        "description": "description",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class GameliftAliasConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        routing_strategy: "GameliftAliasRoutingStrategy",
        description: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS GameLift.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_alias#name GameliftAlias#name}.
        :param routing_strategy: routing_strategy block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_alias#routing_strategy GameliftAlias#routing_strategy}
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_alias#description GameliftAlias#description}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_alias#tags GameliftAlias#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_alias#tags_all GameliftAlias#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(routing_strategy, dict):
            routing_strategy = GameliftAliasRoutingStrategy(**routing_strategy)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "routing_strategy": routing_strategy,
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
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_alias#name GameliftAlias#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def routing_strategy(self) -> "GameliftAliasRoutingStrategy":
        '''routing_strategy block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_alias#routing_strategy GameliftAlias#routing_strategy}
        '''
        result = self._values.get("routing_strategy")
        assert result is not None, "Required property 'routing_strategy' is missing"
        return typing.cast("GameliftAliasRoutingStrategy", result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_alias#description GameliftAlias#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_alias#tags GameliftAlias#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_alias#tags_all GameliftAlias#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GameliftAliasConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.gamelift.GameliftAliasRoutingStrategy",
    jsii_struct_bases=[],
    name_mapping={"type": "type", "fleet_id": "fleetId", "message": "message"},
)
class GameliftAliasRoutingStrategy:
    def __init__(
        self,
        *,
        type: builtins.str,
        fleet_id: typing.Optional[builtins.str] = None,
        message: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_alias#type GameliftAlias#type}.
        :param fleet_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_alias#fleet_id GameliftAlias#fleet_id}.
        :param message: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_alias#message GameliftAlias#message}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "type": type,
        }
        if fleet_id is not None:
            self._values["fleet_id"] = fleet_id
        if message is not None:
            self._values["message"] = message

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_alias#type GameliftAlias#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def fleet_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_alias#fleet_id GameliftAlias#fleet_id}.'''
        result = self._values.get("fleet_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def message(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_alias#message GameliftAlias#message}.'''
        result = self._values.get("message")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GameliftAliasRoutingStrategy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GameliftAliasRoutingStrategyOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.gamelift.GameliftAliasRoutingStrategyOutputReference",
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

    @jsii.member(jsii_name="resetFleetId")
    def reset_fleet_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFleetId", []))

    @jsii.member(jsii_name="resetMessage")
    def reset_message(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMessage", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fleetIdInput")
    def fleet_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fleetIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="messageInput")
    def message_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "messageInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fleetId")
    def fleet_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fleetId"))

    @fleet_id.setter
    def fleet_id(self, value: builtins.str) -> None:
        jsii.set(self, "fleetId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="message")
    def message(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "message"))

    @message.setter
    def message(self, value: builtins.str) -> None:
        jsii.set(self, "message", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        jsii.set(self, "type", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[GameliftAliasRoutingStrategy]:
        return typing.cast(typing.Optional[GameliftAliasRoutingStrategy], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GameliftAliasRoutingStrategy],
    ) -> None:
        jsii.set(self, "internalValue", value)


class GameliftBuild(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.gamelift.GameliftBuild",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/gamelift_build aws_gamelift_build}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        operating_system: builtins.str,
        storage_location: "GameliftBuildStorageLocation",
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        version: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/gamelift_build aws_gamelift_build} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_build#name GameliftBuild#name}.
        :param operating_system: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_build#operating_system GameliftBuild#operating_system}.
        :param storage_location: storage_location block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_build#storage_location GameliftBuild#storage_location}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_build#tags GameliftBuild#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_build#tags_all GameliftBuild#tags_all}.
        :param version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_build#version GameliftBuild#version}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = GameliftBuildConfig(
            name=name,
            operating_system=operating_system,
            storage_location=storage_location,
            tags=tags,
            tags_all=tags_all,
            version=version,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putStorageLocation")
    def put_storage_location(
        self,
        *,
        bucket: builtins.str,
        key: builtins.str,
        role_arn: builtins.str,
    ) -> None:
        '''
        :param bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_build#bucket GameliftBuild#bucket}.
        :param key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_build#key GameliftBuild#key}.
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_build#role_arn GameliftBuild#role_arn}.
        '''
        value = GameliftBuildStorageLocation(bucket=bucket, key=key, role_arn=role_arn)

        return typing.cast(None, jsii.invoke(self, "putStorageLocation", [value]))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetVersion")
    def reset_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVersion", []))

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
    @jsii.member(jsii_name="storageLocation")
    def storage_location(self) -> "GameliftBuildStorageLocationOutputReference":
        return typing.cast("GameliftBuildStorageLocationOutputReference", jsii.get(self, "storageLocation"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="operatingSystemInput")
    def operating_system_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "operatingSystemInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="storageLocationInput")
    def storage_location_input(self) -> typing.Optional["GameliftBuildStorageLocation"]:
        return typing.cast(typing.Optional["GameliftBuildStorageLocation"], jsii.get(self, "storageLocationInput"))

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
    @jsii.member(jsii_name="versionInput")
    def version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "versionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="operatingSystem")
    def operating_system(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "operatingSystem"))

    @operating_system.setter
    def operating_system(self, value: builtins.str) -> None:
        jsii.set(self, "operatingSystem", value)

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
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @version.setter
    def version(self, value: builtins.str) -> None:
        jsii.set(self, "version", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.gamelift.GameliftBuildConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "operating_system": "operatingSystem",
        "storage_location": "storageLocation",
        "tags": "tags",
        "tags_all": "tagsAll",
        "version": "version",
    },
)
class GameliftBuildConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        operating_system: builtins.str,
        storage_location: "GameliftBuildStorageLocation",
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS GameLift.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_build#name GameliftBuild#name}.
        :param operating_system: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_build#operating_system GameliftBuild#operating_system}.
        :param storage_location: storage_location block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_build#storage_location GameliftBuild#storage_location}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_build#tags GameliftBuild#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_build#tags_all GameliftBuild#tags_all}.
        :param version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_build#version GameliftBuild#version}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(storage_location, dict):
            storage_location = GameliftBuildStorageLocation(**storage_location)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "operating_system": operating_system,
            "storage_location": storage_location,
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
        if version is not None:
            self._values["version"] = version

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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_build#name GameliftBuild#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def operating_system(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_build#operating_system GameliftBuild#operating_system}.'''
        result = self._values.get("operating_system")
        assert result is not None, "Required property 'operating_system' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def storage_location(self) -> "GameliftBuildStorageLocation":
        '''storage_location block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_build#storage_location GameliftBuild#storage_location}
        '''
        result = self._values.get("storage_location")
        assert result is not None, "Required property 'storage_location' is missing"
        return typing.cast("GameliftBuildStorageLocation", result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_build#tags GameliftBuild#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_build#tags_all GameliftBuild#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_build#version GameliftBuild#version}.'''
        result = self._values.get("version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GameliftBuildConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.gamelift.GameliftBuildStorageLocation",
    jsii_struct_bases=[],
    name_mapping={"bucket": "bucket", "key": "key", "role_arn": "roleArn"},
)
class GameliftBuildStorageLocation:
    def __init__(
        self,
        *,
        bucket: builtins.str,
        key: builtins.str,
        role_arn: builtins.str,
    ) -> None:
        '''
        :param bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_build#bucket GameliftBuild#bucket}.
        :param key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_build#key GameliftBuild#key}.
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_build#role_arn GameliftBuild#role_arn}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "bucket": bucket,
            "key": key,
            "role_arn": role_arn,
        }

    @builtins.property
    def bucket(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_build#bucket GameliftBuild#bucket}.'''
        result = self._values.get("bucket")
        assert result is not None, "Required property 'bucket' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_build#key GameliftBuild#key}.'''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def role_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_build#role_arn GameliftBuild#role_arn}.'''
        result = self._values.get("role_arn")
        assert result is not None, "Required property 'role_arn' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GameliftBuildStorageLocation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GameliftBuildStorageLocationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.gamelift.GameliftBuildStorageLocationOutputReference",
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
    @jsii.member(jsii_name="bucketInput")
    def bucket_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bucketInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyInput")
    def key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArnInput")
    def role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucket"))

    @bucket.setter
    def bucket(self, value: builtins.str) -> None:
        jsii.set(self, "bucket", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        jsii.set(self, "key", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @role_arn.setter
    def role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "roleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[GameliftBuildStorageLocation]:
        return typing.cast(typing.Optional[GameliftBuildStorageLocation], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GameliftBuildStorageLocation],
    ) -> None:
        jsii.set(self, "internalValue", value)


class GameliftFleet(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.gamelift.GameliftFleet",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet aws_gamelift_fleet}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        build_id: builtins.str,
        ec2_instance_type: builtins.str,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        ec2_inbound_permission: typing.Optional[typing.Sequence["GameliftFleetEc2InboundPermission"]] = None,
        fleet_type: typing.Optional[builtins.str] = None,
        instance_role_arn: typing.Optional[builtins.str] = None,
        metric_groups: typing.Optional[typing.Sequence[builtins.str]] = None,
        new_game_session_protection_policy: typing.Optional[builtins.str] = None,
        resource_creation_limit_policy: typing.Optional["GameliftFleetResourceCreationLimitPolicy"] = None,
        runtime_configuration: typing.Optional["GameliftFleetRuntimeConfiguration"] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["GameliftFleetTimeouts"] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet aws_gamelift_fleet} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param build_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#build_id GameliftFleet#build_id}.
        :param ec2_instance_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#ec2_instance_type GameliftFleet#ec2_instance_type}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#name GameliftFleet#name}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#description GameliftFleet#description}.
        :param ec2_inbound_permission: ec2_inbound_permission block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#ec2_inbound_permission GameliftFleet#ec2_inbound_permission}
        :param fleet_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#fleet_type GameliftFleet#fleet_type}.
        :param instance_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#instance_role_arn GameliftFleet#instance_role_arn}.
        :param metric_groups: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#metric_groups GameliftFleet#metric_groups}.
        :param new_game_session_protection_policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#new_game_session_protection_policy GameliftFleet#new_game_session_protection_policy}.
        :param resource_creation_limit_policy: resource_creation_limit_policy block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#resource_creation_limit_policy GameliftFleet#resource_creation_limit_policy}
        :param runtime_configuration: runtime_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#runtime_configuration GameliftFleet#runtime_configuration}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#tags GameliftFleet#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#tags_all GameliftFleet#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#timeouts GameliftFleet#timeouts}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = GameliftFleetConfig(
            build_id=build_id,
            ec2_instance_type=ec2_instance_type,
            name=name,
            description=description,
            ec2_inbound_permission=ec2_inbound_permission,
            fleet_type=fleet_type,
            instance_role_arn=instance_role_arn,
            metric_groups=metric_groups,
            new_game_session_protection_policy=new_game_session_protection_policy,
            resource_creation_limit_policy=resource_creation_limit_policy,
            runtime_configuration=runtime_configuration,
            tags=tags,
            tags_all=tags_all,
            timeouts=timeouts,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putResourceCreationLimitPolicy")
    def put_resource_creation_limit_policy(
        self,
        *,
        new_game_sessions_per_creator: typing.Optional[jsii.Number] = None,
        policy_period_in_minutes: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param new_game_sessions_per_creator: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#new_game_sessions_per_creator GameliftFleet#new_game_sessions_per_creator}.
        :param policy_period_in_minutes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#policy_period_in_minutes GameliftFleet#policy_period_in_minutes}.
        '''
        value = GameliftFleetResourceCreationLimitPolicy(
            new_game_sessions_per_creator=new_game_sessions_per_creator,
            policy_period_in_minutes=policy_period_in_minutes,
        )

        return typing.cast(None, jsii.invoke(self, "putResourceCreationLimitPolicy", [value]))

    @jsii.member(jsii_name="putRuntimeConfiguration")
    def put_runtime_configuration(
        self,
        *,
        game_session_activation_timeout_seconds: typing.Optional[jsii.Number] = None,
        max_concurrent_game_session_activations: typing.Optional[jsii.Number] = None,
        server_process: typing.Optional[typing.Sequence["GameliftFleetRuntimeConfigurationServerProcess"]] = None,
    ) -> None:
        '''
        :param game_session_activation_timeout_seconds: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#game_session_activation_timeout_seconds GameliftFleet#game_session_activation_timeout_seconds}.
        :param max_concurrent_game_session_activations: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#max_concurrent_game_session_activations GameliftFleet#max_concurrent_game_session_activations}.
        :param server_process: server_process block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#server_process GameliftFleet#server_process}
        '''
        value = GameliftFleetRuntimeConfiguration(
            game_session_activation_timeout_seconds=game_session_activation_timeout_seconds,
            max_concurrent_game_session_activations=max_concurrent_game_session_activations,
            server_process=server_process,
        )

        return typing.cast(None, jsii.invoke(self, "putRuntimeConfiguration", [value]))

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#create GameliftFleet#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#delete GameliftFleet#delete}.
        '''
        value = GameliftFleetTimeouts(create=create, delete=delete)

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetEc2InboundPermission")
    def reset_ec2_inbound_permission(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEc2InboundPermission", []))

    @jsii.member(jsii_name="resetFleetType")
    def reset_fleet_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFleetType", []))

    @jsii.member(jsii_name="resetInstanceRoleArn")
    def reset_instance_role_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstanceRoleArn", []))

    @jsii.member(jsii_name="resetMetricGroups")
    def reset_metric_groups(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMetricGroups", []))

    @jsii.member(jsii_name="resetNewGameSessionProtectionPolicy")
    def reset_new_game_session_protection_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNewGameSessionProtectionPolicy", []))

    @jsii.member(jsii_name="resetResourceCreationLimitPolicy")
    def reset_resource_creation_limit_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResourceCreationLimitPolicy", []))

    @jsii.member(jsii_name="resetRuntimeConfiguration")
    def reset_runtime_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRuntimeConfiguration", []))

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
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logPaths")
    def log_paths(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "logPaths"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="operatingSystem")
    def operating_system(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "operatingSystem"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceCreationLimitPolicy")
    def resource_creation_limit_policy(
        self,
    ) -> "GameliftFleetResourceCreationLimitPolicyOutputReference":
        return typing.cast("GameliftFleetResourceCreationLimitPolicyOutputReference", jsii.get(self, "resourceCreationLimitPolicy"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="runtimeConfiguration")
    def runtime_configuration(
        self,
    ) -> "GameliftFleetRuntimeConfigurationOutputReference":
        return typing.cast("GameliftFleetRuntimeConfigurationOutputReference", jsii.get(self, "runtimeConfiguration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "GameliftFleetTimeoutsOutputReference":
        return typing.cast("GameliftFleetTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="buildIdInput")
    def build_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "buildIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ec2InboundPermissionInput")
    def ec2_inbound_permission_input(
        self,
    ) -> typing.Optional[typing.List["GameliftFleetEc2InboundPermission"]]:
        return typing.cast(typing.Optional[typing.List["GameliftFleetEc2InboundPermission"]], jsii.get(self, "ec2InboundPermissionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ec2InstanceTypeInput")
    def ec2_instance_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ec2InstanceTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fleetTypeInput")
    def fleet_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fleetTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceRoleArnInput")
    def instance_role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "instanceRoleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="metricGroupsInput")
    def metric_groups_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "metricGroupsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="newGameSessionProtectionPolicyInput")
    def new_game_session_protection_policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "newGameSessionProtectionPolicyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceCreationLimitPolicyInput")
    def resource_creation_limit_policy_input(
        self,
    ) -> typing.Optional["GameliftFleetResourceCreationLimitPolicy"]:
        return typing.cast(typing.Optional["GameliftFleetResourceCreationLimitPolicy"], jsii.get(self, "resourceCreationLimitPolicyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="runtimeConfigurationInput")
    def runtime_configuration_input(
        self,
    ) -> typing.Optional["GameliftFleetRuntimeConfiguration"]:
        return typing.cast(typing.Optional["GameliftFleetRuntimeConfiguration"], jsii.get(self, "runtimeConfigurationInput"))

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
    def timeouts_input(self) -> typing.Optional["GameliftFleetTimeouts"]:
        return typing.cast(typing.Optional["GameliftFleetTimeouts"], jsii.get(self, "timeoutsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="buildId")
    def build_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "buildId"))

    @build_id.setter
    def build_id(self, value: builtins.str) -> None:
        jsii.set(self, "buildId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ec2InboundPermission")
    def ec2_inbound_permission(
        self,
    ) -> typing.List["GameliftFleetEc2InboundPermission"]:
        return typing.cast(typing.List["GameliftFleetEc2InboundPermission"], jsii.get(self, "ec2InboundPermission"))

    @ec2_inbound_permission.setter
    def ec2_inbound_permission(
        self,
        value: typing.List["GameliftFleetEc2InboundPermission"],
    ) -> None:
        jsii.set(self, "ec2InboundPermission", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ec2InstanceType")
    def ec2_instance_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ec2InstanceType"))

    @ec2_instance_type.setter
    def ec2_instance_type(self, value: builtins.str) -> None:
        jsii.set(self, "ec2InstanceType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fleetType")
    def fleet_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fleetType"))

    @fleet_type.setter
    def fleet_type(self, value: builtins.str) -> None:
        jsii.set(self, "fleetType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceRoleArn")
    def instance_role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "instanceRoleArn"))

    @instance_role_arn.setter
    def instance_role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "instanceRoleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="metricGroups")
    def metric_groups(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "metricGroups"))

    @metric_groups.setter
    def metric_groups(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "metricGroups", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="newGameSessionProtectionPolicy")
    def new_game_session_protection_policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "newGameSessionProtectionPolicy"))

    @new_game_session_protection_policy.setter
    def new_game_session_protection_policy(self, value: builtins.str) -> None:
        jsii.set(self, "newGameSessionProtectionPolicy", value)

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
    jsii_type="@cdktf/provider-aws.gamelift.GameliftFleetConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "build_id": "buildId",
        "ec2_instance_type": "ec2InstanceType",
        "name": "name",
        "description": "description",
        "ec2_inbound_permission": "ec2InboundPermission",
        "fleet_type": "fleetType",
        "instance_role_arn": "instanceRoleArn",
        "metric_groups": "metricGroups",
        "new_game_session_protection_policy": "newGameSessionProtectionPolicy",
        "resource_creation_limit_policy": "resourceCreationLimitPolicy",
        "runtime_configuration": "runtimeConfiguration",
        "tags": "tags",
        "tags_all": "tagsAll",
        "timeouts": "timeouts",
    },
)
class GameliftFleetConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        build_id: builtins.str,
        ec2_instance_type: builtins.str,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        ec2_inbound_permission: typing.Optional[typing.Sequence["GameliftFleetEc2InboundPermission"]] = None,
        fleet_type: typing.Optional[builtins.str] = None,
        instance_role_arn: typing.Optional[builtins.str] = None,
        metric_groups: typing.Optional[typing.Sequence[builtins.str]] = None,
        new_game_session_protection_policy: typing.Optional[builtins.str] = None,
        resource_creation_limit_policy: typing.Optional["GameliftFleetResourceCreationLimitPolicy"] = None,
        runtime_configuration: typing.Optional["GameliftFleetRuntimeConfiguration"] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["GameliftFleetTimeouts"] = None,
    ) -> None:
        '''AWS GameLift.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param build_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#build_id GameliftFleet#build_id}.
        :param ec2_instance_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#ec2_instance_type GameliftFleet#ec2_instance_type}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#name GameliftFleet#name}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#description GameliftFleet#description}.
        :param ec2_inbound_permission: ec2_inbound_permission block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#ec2_inbound_permission GameliftFleet#ec2_inbound_permission}
        :param fleet_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#fleet_type GameliftFleet#fleet_type}.
        :param instance_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#instance_role_arn GameliftFleet#instance_role_arn}.
        :param metric_groups: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#metric_groups GameliftFleet#metric_groups}.
        :param new_game_session_protection_policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#new_game_session_protection_policy GameliftFleet#new_game_session_protection_policy}.
        :param resource_creation_limit_policy: resource_creation_limit_policy block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#resource_creation_limit_policy GameliftFleet#resource_creation_limit_policy}
        :param runtime_configuration: runtime_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#runtime_configuration GameliftFleet#runtime_configuration}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#tags GameliftFleet#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#tags_all GameliftFleet#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#timeouts GameliftFleet#timeouts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(resource_creation_limit_policy, dict):
            resource_creation_limit_policy = GameliftFleetResourceCreationLimitPolicy(**resource_creation_limit_policy)
        if isinstance(runtime_configuration, dict):
            runtime_configuration = GameliftFleetRuntimeConfiguration(**runtime_configuration)
        if isinstance(timeouts, dict):
            timeouts = GameliftFleetTimeouts(**timeouts)
        self._values: typing.Dict[str, typing.Any] = {
            "build_id": build_id,
            "ec2_instance_type": ec2_instance_type,
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
        if description is not None:
            self._values["description"] = description
        if ec2_inbound_permission is not None:
            self._values["ec2_inbound_permission"] = ec2_inbound_permission
        if fleet_type is not None:
            self._values["fleet_type"] = fleet_type
        if instance_role_arn is not None:
            self._values["instance_role_arn"] = instance_role_arn
        if metric_groups is not None:
            self._values["metric_groups"] = metric_groups
        if new_game_session_protection_policy is not None:
            self._values["new_game_session_protection_policy"] = new_game_session_protection_policy
        if resource_creation_limit_policy is not None:
            self._values["resource_creation_limit_policy"] = resource_creation_limit_policy
        if runtime_configuration is not None:
            self._values["runtime_configuration"] = runtime_configuration
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
    def build_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#build_id GameliftFleet#build_id}.'''
        result = self._values.get("build_id")
        assert result is not None, "Required property 'build_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ec2_instance_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#ec2_instance_type GameliftFleet#ec2_instance_type}.'''
        result = self._values.get("ec2_instance_type")
        assert result is not None, "Required property 'ec2_instance_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#name GameliftFleet#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#description GameliftFleet#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ec2_inbound_permission(
        self,
    ) -> typing.Optional[typing.List["GameliftFleetEc2InboundPermission"]]:
        '''ec2_inbound_permission block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#ec2_inbound_permission GameliftFleet#ec2_inbound_permission}
        '''
        result = self._values.get("ec2_inbound_permission")
        return typing.cast(typing.Optional[typing.List["GameliftFleetEc2InboundPermission"]], result)

    @builtins.property
    def fleet_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#fleet_type GameliftFleet#fleet_type}.'''
        result = self._values.get("fleet_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_role_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#instance_role_arn GameliftFleet#instance_role_arn}.'''
        result = self._values.get("instance_role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def metric_groups(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#metric_groups GameliftFleet#metric_groups}.'''
        result = self._values.get("metric_groups")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def new_game_session_protection_policy(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#new_game_session_protection_policy GameliftFleet#new_game_session_protection_policy}.'''
        result = self._values.get("new_game_session_protection_policy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def resource_creation_limit_policy(
        self,
    ) -> typing.Optional["GameliftFleetResourceCreationLimitPolicy"]:
        '''resource_creation_limit_policy block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#resource_creation_limit_policy GameliftFleet#resource_creation_limit_policy}
        '''
        result = self._values.get("resource_creation_limit_policy")
        return typing.cast(typing.Optional["GameliftFleetResourceCreationLimitPolicy"], result)

    @builtins.property
    def runtime_configuration(
        self,
    ) -> typing.Optional["GameliftFleetRuntimeConfiguration"]:
        '''runtime_configuration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#runtime_configuration GameliftFleet#runtime_configuration}
        '''
        result = self._values.get("runtime_configuration")
        return typing.cast(typing.Optional["GameliftFleetRuntimeConfiguration"], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#tags GameliftFleet#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#tags_all GameliftFleet#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["GameliftFleetTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#timeouts GameliftFleet#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["GameliftFleetTimeouts"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GameliftFleetConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.gamelift.GameliftFleetEc2InboundPermission",
    jsii_struct_bases=[],
    name_mapping={
        "from_port": "fromPort",
        "ip_range": "ipRange",
        "protocol": "protocol",
        "to_port": "toPort",
    },
)
class GameliftFleetEc2InboundPermission:
    def __init__(
        self,
        *,
        from_port: jsii.Number,
        ip_range: builtins.str,
        protocol: builtins.str,
        to_port: jsii.Number,
    ) -> None:
        '''
        :param from_port: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#from_port GameliftFleet#from_port}.
        :param ip_range: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#ip_range GameliftFleet#ip_range}.
        :param protocol: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#protocol GameliftFleet#protocol}.
        :param to_port: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#to_port GameliftFleet#to_port}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "from_port": from_port,
            "ip_range": ip_range,
            "protocol": protocol,
            "to_port": to_port,
        }

    @builtins.property
    def from_port(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#from_port GameliftFleet#from_port}.'''
        result = self._values.get("from_port")
        assert result is not None, "Required property 'from_port' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def ip_range(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#ip_range GameliftFleet#ip_range}.'''
        result = self._values.get("ip_range")
        assert result is not None, "Required property 'ip_range' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def protocol(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#protocol GameliftFleet#protocol}.'''
        result = self._values.get("protocol")
        assert result is not None, "Required property 'protocol' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def to_port(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#to_port GameliftFleet#to_port}.'''
        result = self._values.get("to_port")
        assert result is not None, "Required property 'to_port' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GameliftFleetEc2InboundPermission(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.gamelift.GameliftFleetResourceCreationLimitPolicy",
    jsii_struct_bases=[],
    name_mapping={
        "new_game_sessions_per_creator": "newGameSessionsPerCreator",
        "policy_period_in_minutes": "policyPeriodInMinutes",
    },
)
class GameliftFleetResourceCreationLimitPolicy:
    def __init__(
        self,
        *,
        new_game_sessions_per_creator: typing.Optional[jsii.Number] = None,
        policy_period_in_minutes: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param new_game_sessions_per_creator: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#new_game_sessions_per_creator GameliftFleet#new_game_sessions_per_creator}.
        :param policy_period_in_minutes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#policy_period_in_minutes GameliftFleet#policy_period_in_minutes}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if new_game_sessions_per_creator is not None:
            self._values["new_game_sessions_per_creator"] = new_game_sessions_per_creator
        if policy_period_in_minutes is not None:
            self._values["policy_period_in_minutes"] = policy_period_in_minutes

    @builtins.property
    def new_game_sessions_per_creator(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#new_game_sessions_per_creator GameliftFleet#new_game_sessions_per_creator}.'''
        result = self._values.get("new_game_sessions_per_creator")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def policy_period_in_minutes(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#policy_period_in_minutes GameliftFleet#policy_period_in_minutes}.'''
        result = self._values.get("policy_period_in_minutes")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GameliftFleetResourceCreationLimitPolicy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GameliftFleetResourceCreationLimitPolicyOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.gamelift.GameliftFleetResourceCreationLimitPolicyOutputReference",
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

    @jsii.member(jsii_name="resetNewGameSessionsPerCreator")
    def reset_new_game_sessions_per_creator(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNewGameSessionsPerCreator", []))

    @jsii.member(jsii_name="resetPolicyPeriodInMinutes")
    def reset_policy_period_in_minutes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPolicyPeriodInMinutes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="newGameSessionsPerCreatorInput")
    def new_game_sessions_per_creator_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "newGameSessionsPerCreatorInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyPeriodInMinutesInput")
    def policy_period_in_minutes_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "policyPeriodInMinutesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="newGameSessionsPerCreator")
    def new_game_sessions_per_creator(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "newGameSessionsPerCreator"))

    @new_game_sessions_per_creator.setter
    def new_game_sessions_per_creator(self, value: jsii.Number) -> None:
        jsii.set(self, "newGameSessionsPerCreator", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyPeriodInMinutes")
    def policy_period_in_minutes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "policyPeriodInMinutes"))

    @policy_period_in_minutes.setter
    def policy_period_in_minutes(self, value: jsii.Number) -> None:
        jsii.set(self, "policyPeriodInMinutes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[GameliftFleetResourceCreationLimitPolicy]:
        return typing.cast(typing.Optional[GameliftFleetResourceCreationLimitPolicy], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GameliftFleetResourceCreationLimitPolicy],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.gamelift.GameliftFleetRuntimeConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "game_session_activation_timeout_seconds": "gameSessionActivationTimeoutSeconds",
        "max_concurrent_game_session_activations": "maxConcurrentGameSessionActivations",
        "server_process": "serverProcess",
    },
)
class GameliftFleetRuntimeConfiguration:
    def __init__(
        self,
        *,
        game_session_activation_timeout_seconds: typing.Optional[jsii.Number] = None,
        max_concurrent_game_session_activations: typing.Optional[jsii.Number] = None,
        server_process: typing.Optional[typing.Sequence["GameliftFleetRuntimeConfigurationServerProcess"]] = None,
    ) -> None:
        '''
        :param game_session_activation_timeout_seconds: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#game_session_activation_timeout_seconds GameliftFleet#game_session_activation_timeout_seconds}.
        :param max_concurrent_game_session_activations: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#max_concurrent_game_session_activations GameliftFleet#max_concurrent_game_session_activations}.
        :param server_process: server_process block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#server_process GameliftFleet#server_process}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if game_session_activation_timeout_seconds is not None:
            self._values["game_session_activation_timeout_seconds"] = game_session_activation_timeout_seconds
        if max_concurrent_game_session_activations is not None:
            self._values["max_concurrent_game_session_activations"] = max_concurrent_game_session_activations
        if server_process is not None:
            self._values["server_process"] = server_process

    @builtins.property
    def game_session_activation_timeout_seconds(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#game_session_activation_timeout_seconds GameliftFleet#game_session_activation_timeout_seconds}.'''
        result = self._values.get("game_session_activation_timeout_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_concurrent_game_session_activations(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#max_concurrent_game_session_activations GameliftFleet#max_concurrent_game_session_activations}.'''
        result = self._values.get("max_concurrent_game_session_activations")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def server_process(
        self,
    ) -> typing.Optional[typing.List["GameliftFleetRuntimeConfigurationServerProcess"]]:
        '''server_process block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#server_process GameliftFleet#server_process}
        '''
        result = self._values.get("server_process")
        return typing.cast(typing.Optional[typing.List["GameliftFleetRuntimeConfigurationServerProcess"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GameliftFleetRuntimeConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GameliftFleetRuntimeConfigurationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.gamelift.GameliftFleetRuntimeConfigurationOutputReference",
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

    @jsii.member(jsii_name="resetGameSessionActivationTimeoutSeconds")
    def reset_game_session_activation_timeout_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGameSessionActivationTimeoutSeconds", []))

    @jsii.member(jsii_name="resetMaxConcurrentGameSessionActivations")
    def reset_max_concurrent_game_session_activations(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxConcurrentGameSessionActivations", []))

    @jsii.member(jsii_name="resetServerProcess")
    def reset_server_process(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServerProcess", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="gameSessionActivationTimeoutSecondsInput")
    def game_session_activation_timeout_seconds_input(
        self,
    ) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "gameSessionActivationTimeoutSecondsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxConcurrentGameSessionActivationsInput")
    def max_concurrent_game_session_activations_input(
        self,
    ) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxConcurrentGameSessionActivationsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serverProcessInput")
    def server_process_input(
        self,
    ) -> typing.Optional[typing.List["GameliftFleetRuntimeConfigurationServerProcess"]]:
        return typing.cast(typing.Optional[typing.List["GameliftFleetRuntimeConfigurationServerProcess"]], jsii.get(self, "serverProcessInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="gameSessionActivationTimeoutSeconds")
    def game_session_activation_timeout_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "gameSessionActivationTimeoutSeconds"))

    @game_session_activation_timeout_seconds.setter
    def game_session_activation_timeout_seconds(self, value: jsii.Number) -> None:
        jsii.set(self, "gameSessionActivationTimeoutSeconds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxConcurrentGameSessionActivations")
    def max_concurrent_game_session_activations(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxConcurrentGameSessionActivations"))

    @max_concurrent_game_session_activations.setter
    def max_concurrent_game_session_activations(self, value: jsii.Number) -> None:
        jsii.set(self, "maxConcurrentGameSessionActivations", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serverProcess")
    def server_process(
        self,
    ) -> typing.List["GameliftFleetRuntimeConfigurationServerProcess"]:
        return typing.cast(typing.List["GameliftFleetRuntimeConfigurationServerProcess"], jsii.get(self, "serverProcess"))

    @server_process.setter
    def server_process(
        self,
        value: typing.List["GameliftFleetRuntimeConfigurationServerProcess"],
    ) -> None:
        jsii.set(self, "serverProcess", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[GameliftFleetRuntimeConfiguration]:
        return typing.cast(typing.Optional[GameliftFleetRuntimeConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GameliftFleetRuntimeConfiguration],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.gamelift.GameliftFleetRuntimeConfigurationServerProcess",
    jsii_struct_bases=[],
    name_mapping={
        "concurrent_executions": "concurrentExecutions",
        "launch_path": "launchPath",
        "parameters": "parameters",
    },
)
class GameliftFleetRuntimeConfigurationServerProcess:
    def __init__(
        self,
        *,
        concurrent_executions: jsii.Number,
        launch_path: builtins.str,
        parameters: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param concurrent_executions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#concurrent_executions GameliftFleet#concurrent_executions}.
        :param launch_path: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#launch_path GameliftFleet#launch_path}.
        :param parameters: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#parameters GameliftFleet#parameters}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "concurrent_executions": concurrent_executions,
            "launch_path": launch_path,
        }
        if parameters is not None:
            self._values["parameters"] = parameters

    @builtins.property
    def concurrent_executions(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#concurrent_executions GameliftFleet#concurrent_executions}.'''
        result = self._values.get("concurrent_executions")
        assert result is not None, "Required property 'concurrent_executions' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def launch_path(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#launch_path GameliftFleet#launch_path}.'''
        result = self._values.get("launch_path")
        assert result is not None, "Required property 'launch_path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def parameters(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#parameters GameliftFleet#parameters}.'''
        result = self._values.get("parameters")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GameliftFleetRuntimeConfigurationServerProcess(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.gamelift.GameliftFleetTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete"},
)
class GameliftFleetTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#create GameliftFleet#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#delete GameliftFleet#delete}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if create is not None:
            self._values["create"] = create
        if delete is not None:
            self._values["delete"] = delete

    @builtins.property
    def create(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#create GameliftFleet#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_fleet#delete GameliftFleet#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GameliftFleetTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GameliftFleetTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.gamelift.GameliftFleetTimeoutsOutputReference",
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
    def internal_value(self) -> typing.Optional[GameliftFleetTimeouts]:
        return typing.cast(typing.Optional[GameliftFleetTimeouts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[GameliftFleetTimeouts]) -> None:
        jsii.set(self, "internalValue", value)


class GameliftGameSessionQueue(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.gamelift.GameliftGameSessionQueue",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/gamelift_game_session_queue aws_gamelift_game_session_queue}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        destinations: typing.Optional[typing.Sequence[builtins.str]] = None,
        player_latency_policy: typing.Optional[typing.Sequence["GameliftGameSessionQueuePlayerLatencyPolicy"]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeout_in_seconds: typing.Optional[jsii.Number] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/gamelift_game_session_queue aws_gamelift_game_session_queue} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_game_session_queue#name GameliftGameSessionQueue#name}.
        :param destinations: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_game_session_queue#destinations GameliftGameSessionQueue#destinations}.
        :param player_latency_policy: player_latency_policy block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_game_session_queue#player_latency_policy GameliftGameSessionQueue#player_latency_policy}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_game_session_queue#tags GameliftGameSessionQueue#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_game_session_queue#tags_all GameliftGameSessionQueue#tags_all}.
        :param timeout_in_seconds: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_game_session_queue#timeout_in_seconds GameliftGameSessionQueue#timeout_in_seconds}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = GameliftGameSessionQueueConfig(
            name=name,
            destinations=destinations,
            player_latency_policy=player_latency_policy,
            tags=tags,
            tags_all=tags_all,
            timeout_in_seconds=timeout_in_seconds,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetDestinations")
    def reset_destinations(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDestinations", []))

    @jsii.member(jsii_name="resetPlayerLatencyPolicy")
    def reset_player_latency_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPlayerLatencyPolicy", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetTimeoutInSeconds")
    def reset_timeout_in_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeoutInSeconds", []))

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
    @jsii.member(jsii_name="destinationsInput")
    def destinations_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "destinationsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="playerLatencyPolicyInput")
    def player_latency_policy_input(
        self,
    ) -> typing.Optional[typing.List["GameliftGameSessionQueuePlayerLatencyPolicy"]]:
        return typing.cast(typing.Optional[typing.List["GameliftGameSessionQueuePlayerLatencyPolicy"]], jsii.get(self, "playerLatencyPolicyInput"))

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
    @jsii.member(jsii_name="timeoutInSecondsInput")
    def timeout_in_seconds_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "timeoutInSecondsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="destinations")
    def destinations(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "destinations"))

    @destinations.setter
    def destinations(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "destinations", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="playerLatencyPolicy")
    def player_latency_policy(
        self,
    ) -> typing.List["GameliftGameSessionQueuePlayerLatencyPolicy"]:
        return typing.cast(typing.List["GameliftGameSessionQueuePlayerLatencyPolicy"], jsii.get(self, "playerLatencyPolicy"))

    @player_latency_policy.setter
    def player_latency_policy(
        self,
        value: typing.List["GameliftGameSessionQueuePlayerLatencyPolicy"],
    ) -> None:
        jsii.set(self, "playerLatencyPolicy", value)

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
    @jsii.member(jsii_name="timeoutInSeconds")
    def timeout_in_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "timeoutInSeconds"))

    @timeout_in_seconds.setter
    def timeout_in_seconds(self, value: jsii.Number) -> None:
        jsii.set(self, "timeoutInSeconds", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.gamelift.GameliftGameSessionQueueConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "destinations": "destinations",
        "player_latency_policy": "playerLatencyPolicy",
        "tags": "tags",
        "tags_all": "tagsAll",
        "timeout_in_seconds": "timeoutInSeconds",
    },
)
class GameliftGameSessionQueueConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        destinations: typing.Optional[typing.Sequence[builtins.str]] = None,
        player_latency_policy: typing.Optional[typing.Sequence["GameliftGameSessionQueuePlayerLatencyPolicy"]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeout_in_seconds: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''AWS GameLift.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_game_session_queue#name GameliftGameSessionQueue#name}.
        :param destinations: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_game_session_queue#destinations GameliftGameSessionQueue#destinations}.
        :param player_latency_policy: player_latency_policy block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_game_session_queue#player_latency_policy GameliftGameSessionQueue#player_latency_policy}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_game_session_queue#tags GameliftGameSessionQueue#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_game_session_queue#tags_all GameliftGameSessionQueue#tags_all}.
        :param timeout_in_seconds: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_game_session_queue#timeout_in_seconds GameliftGameSessionQueue#timeout_in_seconds}.
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
        if destinations is not None:
            self._values["destinations"] = destinations
        if player_latency_policy is not None:
            self._values["player_latency_policy"] = player_latency_policy
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if timeout_in_seconds is not None:
            self._values["timeout_in_seconds"] = timeout_in_seconds

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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_game_session_queue#name GameliftGameSessionQueue#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def destinations(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_game_session_queue#destinations GameliftGameSessionQueue#destinations}.'''
        result = self._values.get("destinations")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def player_latency_policy(
        self,
    ) -> typing.Optional[typing.List["GameliftGameSessionQueuePlayerLatencyPolicy"]]:
        '''player_latency_policy block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_game_session_queue#player_latency_policy GameliftGameSessionQueue#player_latency_policy}
        '''
        result = self._values.get("player_latency_policy")
        return typing.cast(typing.Optional[typing.List["GameliftGameSessionQueuePlayerLatencyPolicy"]], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_game_session_queue#tags GameliftGameSessionQueue#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_game_session_queue#tags_all GameliftGameSessionQueue#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def timeout_in_seconds(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_game_session_queue#timeout_in_seconds GameliftGameSessionQueue#timeout_in_seconds}.'''
        result = self._values.get("timeout_in_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GameliftGameSessionQueueConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.gamelift.GameliftGameSessionQueuePlayerLatencyPolicy",
    jsii_struct_bases=[],
    name_mapping={
        "maximum_individual_player_latency_milliseconds": "maximumIndividualPlayerLatencyMilliseconds",
        "policy_duration_seconds": "policyDurationSeconds",
    },
)
class GameliftGameSessionQueuePlayerLatencyPolicy:
    def __init__(
        self,
        *,
        maximum_individual_player_latency_milliseconds: jsii.Number,
        policy_duration_seconds: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param maximum_individual_player_latency_milliseconds: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_game_session_queue#maximum_individual_player_latency_milliseconds GameliftGameSessionQueue#maximum_individual_player_latency_milliseconds}.
        :param policy_duration_seconds: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_game_session_queue#policy_duration_seconds GameliftGameSessionQueue#policy_duration_seconds}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "maximum_individual_player_latency_milliseconds": maximum_individual_player_latency_milliseconds,
        }
        if policy_duration_seconds is not None:
            self._values["policy_duration_seconds"] = policy_duration_seconds

    @builtins.property
    def maximum_individual_player_latency_milliseconds(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_game_session_queue#maximum_individual_player_latency_milliseconds GameliftGameSessionQueue#maximum_individual_player_latency_milliseconds}.'''
        result = self._values.get("maximum_individual_player_latency_milliseconds")
        assert result is not None, "Required property 'maximum_individual_player_latency_milliseconds' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def policy_duration_seconds(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/gamelift_game_session_queue#policy_duration_seconds GameliftGameSessionQueue#policy_duration_seconds}.'''
        result = self._values.get("policy_duration_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GameliftGameSessionQueuePlayerLatencyPolicy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "GameliftAlias",
    "GameliftAliasConfig",
    "GameliftAliasRoutingStrategy",
    "GameliftAliasRoutingStrategyOutputReference",
    "GameliftBuild",
    "GameliftBuildConfig",
    "GameliftBuildStorageLocation",
    "GameliftBuildStorageLocationOutputReference",
    "GameliftFleet",
    "GameliftFleetConfig",
    "GameliftFleetEc2InboundPermission",
    "GameliftFleetResourceCreationLimitPolicy",
    "GameliftFleetResourceCreationLimitPolicyOutputReference",
    "GameliftFleetRuntimeConfiguration",
    "GameliftFleetRuntimeConfigurationOutputReference",
    "GameliftFleetRuntimeConfigurationServerProcess",
    "GameliftFleetTimeouts",
    "GameliftFleetTimeoutsOutputReference",
    "GameliftGameSessionQueue",
    "GameliftGameSessionQueueConfig",
    "GameliftGameSessionQueuePlayerLatencyPolicy",
]

publication.publish()
