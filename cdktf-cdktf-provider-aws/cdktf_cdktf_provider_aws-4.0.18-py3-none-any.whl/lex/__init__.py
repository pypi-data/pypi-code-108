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


class DataAwsLexBot(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lex.DataAwsLexBot",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/lex_bot aws_lex_bot}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        version: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/lex_bot aws_lex_bot} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/lex_bot#name DataAwsLexBot#name}.
        :param version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/lex_bot#version DataAwsLexBot#version}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsLexBotConfig(
            name=name,
            version=version,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

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
    @jsii.member(jsii_name="checksum")
    def checksum(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "checksum"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="childDirected")
    def child_directed(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "childDirected"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createdDate")
    def created_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdDate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="detectSentiment")
    def detect_sentiment(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "detectSentiment"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableModelImprovements")
    def enable_model_improvements(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "enableModelImprovements"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="failureReason")
    def failure_reason(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "failureReason"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idleSessionTtlInSeconds")
    def idle_session_ttl_in_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "idleSessionTtlInSeconds"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lastUpdatedDate")
    def last_updated_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lastUpdatedDate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="locale")
    def locale(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "locale"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nluIntentConfidenceThreshold")
    def nlu_intent_confidence_threshold(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "nluIntentConfidenceThreshold"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="voiceId")
    def voice_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "voiceId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

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
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @version.setter
    def version(self, value: builtins.str) -> None:
        jsii.set(self, "version", value)


class DataAwsLexBotAlias(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lex.DataAwsLexBotAlias",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/lex_bot_alias aws_lex_bot_alias}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        bot_name: builtins.str,
        name: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/lex_bot_alias aws_lex_bot_alias} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param bot_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/lex_bot_alias#bot_name DataAwsLexBotAlias#bot_name}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/lex_bot_alias#name DataAwsLexBotAlias#name}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsLexBotAliasConfig(
            bot_name=bot_name,
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
    @jsii.member(jsii_name="botVersion")
    def bot_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "botVersion"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="checksum")
    def checksum(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "checksum"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createdDate")
    def created_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdDate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lastUpdatedDate")
    def last_updated_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lastUpdatedDate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="botNameInput")
    def bot_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "botNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="botName")
    def bot_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "botName"))

    @bot_name.setter
    def bot_name(self, value: builtins.str) -> None:
        jsii.set(self, "botName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lex.DataAwsLexBotAliasConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "bot_name": "botName",
        "name": "name",
    },
)
class DataAwsLexBotAliasConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        bot_name: builtins.str,
        name: builtins.str,
    ) -> None:
        '''AWS Lex.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param bot_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/lex_bot_alias#bot_name DataAwsLexBotAlias#bot_name}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/lex_bot_alias#name DataAwsLexBotAlias#name}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "bot_name": bot_name,
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
    def bot_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/lex_bot_alias#bot_name DataAwsLexBotAlias#bot_name}.'''
        result = self._values.get("bot_name")
        assert result is not None, "Required property 'bot_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/lex_bot_alias#name DataAwsLexBotAlias#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsLexBotAliasConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lex.DataAwsLexBotConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "version": "version",
    },
)
class DataAwsLexBotConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Lex.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/lex_bot#name DataAwsLexBot#name}.
        :param version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/lex_bot#version DataAwsLexBot#version}.
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/lex_bot#name DataAwsLexBot#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/lex_bot#version DataAwsLexBot#version}.'''
        result = self._values.get("version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsLexBotConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsLexIntent(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lex.DataAwsLexIntent",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/lex_intent aws_lex_intent}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        version: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/lex_intent aws_lex_intent} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/lex_intent#name DataAwsLexIntent#name}.
        :param version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/lex_intent#version DataAwsLexIntent#version}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsLexIntentConfig(
            name=name,
            version=version,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

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
    @jsii.member(jsii_name="checksum")
    def checksum(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "checksum"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createdDate")
    def created_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdDate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lastUpdatedDate")
    def last_updated_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lastUpdatedDate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parentIntentSignature")
    def parent_intent_signature(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "parentIntentSignature"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

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
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @version.setter
    def version(self, value: builtins.str) -> None:
        jsii.set(self, "version", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lex.DataAwsLexIntentConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "version": "version",
    },
)
class DataAwsLexIntentConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Lex.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/lex_intent#name DataAwsLexIntent#name}.
        :param version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/lex_intent#version DataAwsLexIntent#version}.
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/lex_intent#name DataAwsLexIntent#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/lex_intent#version DataAwsLexIntent#version}.'''
        result = self._values.get("version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsLexIntentConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsLexSlotType(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lex.DataAwsLexSlotType",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/lex_slot_type aws_lex_slot_type}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        version: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/lex_slot_type aws_lex_slot_type} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/lex_slot_type#name DataAwsLexSlotType#name}.
        :param version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/lex_slot_type#version DataAwsLexSlotType#version}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsLexSlotTypeConfig(
            name=name,
            version=version,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="enumerationValue")
    def enumeration_value(
        self,
        index: builtins.str,
    ) -> "DataAwsLexSlotTypeEnumerationValue":
        '''
        :param index: -
        '''
        return typing.cast("DataAwsLexSlotTypeEnumerationValue", jsii.invoke(self, "enumerationValue", [index]))

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
    @jsii.member(jsii_name="checksum")
    def checksum(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "checksum"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createdDate")
    def created_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdDate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lastUpdatedDate")
    def last_updated_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lastUpdatedDate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="valueSelectionStrategy")
    def value_selection_strategy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "valueSelectionStrategy"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

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
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @version.setter
    def version(self, value: builtins.str) -> None:
        jsii.set(self, "version", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lex.DataAwsLexSlotTypeConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "version": "version",
    },
)
class DataAwsLexSlotTypeConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Lex.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/lex_slot_type#name DataAwsLexSlotType#name}.
        :param version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/lex_slot_type#version DataAwsLexSlotType#version}.
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/lex_slot_type#name DataAwsLexSlotType#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/lex_slot_type#version DataAwsLexSlotType#version}.'''
        result = self._values.get("version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsLexSlotTypeConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsLexSlotTypeEnumerationValue(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lex.DataAwsLexSlotTypeEnumerationValue",
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
    @jsii.member(jsii_name="synonyms")
    def synonyms(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "synonyms"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))


class LexBot(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lex.LexBot",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/lex_bot aws_lex_bot}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        abort_statement: "LexBotAbortStatement",
        child_directed: typing.Union[builtins.bool, cdktf.IResolvable],
        intent: typing.Sequence["LexBotIntent"],
        name: builtins.str,
        clarification_prompt: typing.Optional["LexBotClarificationPrompt"] = None,
        create_version: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        description: typing.Optional[builtins.str] = None,
        detect_sentiment: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        enable_model_improvements: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        idle_session_ttl_in_seconds: typing.Optional[jsii.Number] = None,
        locale: typing.Optional[builtins.str] = None,
        nlu_intent_confidence_threshold: typing.Optional[jsii.Number] = None,
        process_behavior: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional["LexBotTimeouts"] = None,
        voice_id: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/lex_bot aws_lex_bot} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param abort_statement: abort_statement block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#abort_statement LexBot#abort_statement}
        :param child_directed: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#child_directed LexBot#child_directed}.
        :param intent: intent block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#intent LexBot#intent}
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#name LexBot#name}.
        :param clarification_prompt: clarification_prompt block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#clarification_prompt LexBot#clarification_prompt}
        :param create_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#create_version LexBot#create_version}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#description LexBot#description}.
        :param detect_sentiment: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#detect_sentiment LexBot#detect_sentiment}.
        :param enable_model_improvements: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#enable_model_improvements LexBot#enable_model_improvements}.
        :param idle_session_ttl_in_seconds: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#idle_session_ttl_in_seconds LexBot#idle_session_ttl_in_seconds}.
        :param locale: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#locale LexBot#locale}.
        :param nlu_intent_confidence_threshold: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#nlu_intent_confidence_threshold LexBot#nlu_intent_confidence_threshold}.
        :param process_behavior: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#process_behavior LexBot#process_behavior}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#timeouts LexBot#timeouts}
        :param voice_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#voice_id LexBot#voice_id}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = LexBotConfig(
            abort_statement=abort_statement,
            child_directed=child_directed,
            intent=intent,
            name=name,
            clarification_prompt=clarification_prompt,
            create_version=create_version,
            description=description,
            detect_sentiment=detect_sentiment,
            enable_model_improvements=enable_model_improvements,
            idle_session_ttl_in_seconds=idle_session_ttl_in_seconds,
            locale=locale,
            nlu_intent_confidence_threshold=nlu_intent_confidence_threshold,
            process_behavior=process_behavior,
            timeouts=timeouts,
            voice_id=voice_id,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putAbortStatement")
    def put_abort_statement(
        self,
        *,
        message: typing.Sequence["LexBotAbortStatementMessage"],
        response_card: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param message: message block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#message LexBot#message}
        :param response_card: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#response_card LexBot#response_card}.
        '''
        value = LexBotAbortStatement(message=message, response_card=response_card)

        return typing.cast(None, jsii.invoke(self, "putAbortStatement", [value]))

    @jsii.member(jsii_name="putClarificationPrompt")
    def put_clarification_prompt(
        self,
        *,
        max_attempts: jsii.Number,
        message: typing.Sequence["LexBotClarificationPromptMessage"],
        response_card: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param max_attempts: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#max_attempts LexBot#max_attempts}.
        :param message: message block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#message LexBot#message}
        :param response_card: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#response_card LexBot#response_card}.
        '''
        value = LexBotClarificationPrompt(
            max_attempts=max_attempts, message=message, response_card=response_card
        )

        return typing.cast(None, jsii.invoke(self, "putClarificationPrompt", [value]))

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#create LexBot#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#delete LexBot#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#update LexBot#update}.
        '''
        value = LexBotTimeouts(create=create, delete=delete, update=update)

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetClarificationPrompt")
    def reset_clarification_prompt(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClarificationPrompt", []))

    @jsii.member(jsii_name="resetCreateVersion")
    def reset_create_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreateVersion", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetDetectSentiment")
    def reset_detect_sentiment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDetectSentiment", []))

    @jsii.member(jsii_name="resetEnableModelImprovements")
    def reset_enable_model_improvements(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableModelImprovements", []))

    @jsii.member(jsii_name="resetIdleSessionTtlInSeconds")
    def reset_idle_session_ttl_in_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIdleSessionTtlInSeconds", []))

    @jsii.member(jsii_name="resetLocale")
    def reset_locale(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLocale", []))

    @jsii.member(jsii_name="resetNluIntentConfidenceThreshold")
    def reset_nlu_intent_confidence_threshold(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNluIntentConfidenceThreshold", []))

    @jsii.member(jsii_name="resetProcessBehavior")
    def reset_process_behavior(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProcessBehavior", []))

    @jsii.member(jsii_name="resetTimeouts")
    def reset_timeouts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeouts", []))

    @jsii.member(jsii_name="resetVoiceId")
    def reset_voice_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVoiceId", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="abortStatement")
    def abort_statement(self) -> "LexBotAbortStatementOutputReference":
        return typing.cast("LexBotAbortStatementOutputReference", jsii.get(self, "abortStatement"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="checksum")
    def checksum(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "checksum"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clarificationPrompt")
    def clarification_prompt(self) -> "LexBotClarificationPromptOutputReference":
        return typing.cast("LexBotClarificationPromptOutputReference", jsii.get(self, "clarificationPrompt"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createdDate")
    def created_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdDate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="failureReason")
    def failure_reason(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "failureReason"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lastUpdatedDate")
    def last_updated_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lastUpdatedDate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "LexBotTimeoutsOutputReference":
        return typing.cast("LexBotTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="abortStatementInput")
    def abort_statement_input(self) -> typing.Optional["LexBotAbortStatement"]:
        return typing.cast(typing.Optional["LexBotAbortStatement"], jsii.get(self, "abortStatementInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="childDirectedInput")
    def child_directed_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "childDirectedInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clarificationPromptInput")
    def clarification_prompt_input(
        self,
    ) -> typing.Optional["LexBotClarificationPrompt"]:
        return typing.cast(typing.Optional["LexBotClarificationPrompt"], jsii.get(self, "clarificationPromptInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createVersionInput")
    def create_version_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "createVersionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="detectSentimentInput")
    def detect_sentiment_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "detectSentimentInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableModelImprovementsInput")
    def enable_model_improvements_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enableModelImprovementsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idleSessionTtlInSecondsInput")
    def idle_session_ttl_in_seconds_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "idleSessionTtlInSecondsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="intentInput")
    def intent_input(self) -> typing.Optional[typing.List["LexBotIntent"]]:
        return typing.cast(typing.Optional[typing.List["LexBotIntent"]], jsii.get(self, "intentInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="localeInput")
    def locale_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "localeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nluIntentConfidenceThresholdInput")
    def nlu_intent_confidence_threshold_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "nluIntentConfidenceThresholdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="processBehaviorInput")
    def process_behavior_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "processBehaviorInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(self) -> typing.Optional["LexBotTimeouts"]:
        return typing.cast(typing.Optional["LexBotTimeouts"], jsii.get(self, "timeoutsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="voiceIdInput")
    def voice_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "voiceIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="childDirected")
    def child_directed(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "childDirected"))

    @child_directed.setter
    def child_directed(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "childDirected", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createVersion")
    def create_version(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "createVersion"))

    @create_version.setter
    def create_version(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "createVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="detectSentiment")
    def detect_sentiment(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "detectSentiment"))

    @detect_sentiment.setter
    def detect_sentiment(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "detectSentiment", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableModelImprovements")
    def enable_model_improvements(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enableModelImprovements"))

    @enable_model_improvements.setter
    def enable_model_improvements(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "enableModelImprovements", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idleSessionTtlInSeconds")
    def idle_session_ttl_in_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "idleSessionTtlInSeconds"))

    @idle_session_ttl_in_seconds.setter
    def idle_session_ttl_in_seconds(self, value: jsii.Number) -> None:
        jsii.set(self, "idleSessionTtlInSeconds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="intent")
    def intent(self) -> typing.List["LexBotIntent"]:
        return typing.cast(typing.List["LexBotIntent"], jsii.get(self, "intent"))

    @intent.setter
    def intent(self, value: typing.List["LexBotIntent"]) -> None:
        jsii.set(self, "intent", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="locale")
    def locale(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "locale"))

    @locale.setter
    def locale(self, value: builtins.str) -> None:
        jsii.set(self, "locale", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nluIntentConfidenceThreshold")
    def nlu_intent_confidence_threshold(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "nluIntentConfidenceThreshold"))

    @nlu_intent_confidence_threshold.setter
    def nlu_intent_confidence_threshold(self, value: jsii.Number) -> None:
        jsii.set(self, "nluIntentConfidenceThreshold", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="processBehavior")
    def process_behavior(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "processBehavior"))

    @process_behavior.setter
    def process_behavior(self, value: builtins.str) -> None:
        jsii.set(self, "processBehavior", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="voiceId")
    def voice_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "voiceId"))

    @voice_id.setter
    def voice_id(self, value: builtins.str) -> None:
        jsii.set(self, "voiceId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lex.LexBotAbortStatement",
    jsii_struct_bases=[],
    name_mapping={"message": "message", "response_card": "responseCard"},
)
class LexBotAbortStatement:
    def __init__(
        self,
        *,
        message: typing.Sequence["LexBotAbortStatementMessage"],
        response_card: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param message: message block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#message LexBot#message}
        :param response_card: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#response_card LexBot#response_card}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "message": message,
        }
        if response_card is not None:
            self._values["response_card"] = response_card

    @builtins.property
    def message(self) -> typing.List["LexBotAbortStatementMessage"]:
        '''message block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#message LexBot#message}
        '''
        result = self._values.get("message")
        assert result is not None, "Required property 'message' is missing"
        return typing.cast(typing.List["LexBotAbortStatementMessage"], result)

    @builtins.property
    def response_card(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#response_card LexBot#response_card}.'''
        result = self._values.get("response_card")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LexBotAbortStatement(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lex.LexBotAbortStatementMessage",
    jsii_struct_bases=[],
    name_mapping={
        "content": "content",
        "content_type": "contentType",
        "group_number": "groupNumber",
    },
)
class LexBotAbortStatementMessage:
    def __init__(
        self,
        *,
        content: builtins.str,
        content_type: builtins.str,
        group_number: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param content: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#content LexBot#content}.
        :param content_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#content_type LexBot#content_type}.
        :param group_number: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#group_number LexBot#group_number}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "content": content,
            "content_type": content_type,
        }
        if group_number is not None:
            self._values["group_number"] = group_number

    @builtins.property
    def content(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#content LexBot#content}.'''
        result = self._values.get("content")
        assert result is not None, "Required property 'content' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def content_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#content_type LexBot#content_type}.'''
        result = self._values.get("content_type")
        assert result is not None, "Required property 'content_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def group_number(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#group_number LexBot#group_number}.'''
        result = self._values.get("group_number")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LexBotAbortStatementMessage(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LexBotAbortStatementOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lex.LexBotAbortStatementOutputReference",
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

    @jsii.member(jsii_name="resetResponseCard")
    def reset_response_card(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResponseCard", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="messageInput")
    def message_input(
        self,
    ) -> typing.Optional[typing.List[LexBotAbortStatementMessage]]:
        return typing.cast(typing.Optional[typing.List[LexBotAbortStatementMessage]], jsii.get(self, "messageInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="responseCardInput")
    def response_card_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "responseCardInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="message")
    def message(self) -> typing.List[LexBotAbortStatementMessage]:
        return typing.cast(typing.List[LexBotAbortStatementMessage], jsii.get(self, "message"))

    @message.setter
    def message(self, value: typing.List[LexBotAbortStatementMessage]) -> None:
        jsii.set(self, "message", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="responseCard")
    def response_card(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "responseCard"))

    @response_card.setter
    def response_card(self, value: builtins.str) -> None:
        jsii.set(self, "responseCard", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[LexBotAbortStatement]:
        return typing.cast(typing.Optional[LexBotAbortStatement], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[LexBotAbortStatement]) -> None:
        jsii.set(self, "internalValue", value)


class LexBotAlias(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lex.LexBotAlias",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/lex_bot_alias aws_lex_bot_alias}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        bot_name: builtins.str,
        bot_version: builtins.str,
        name: builtins.str,
        conversation_logs: typing.Optional["LexBotAliasConversationLogs"] = None,
        description: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional["LexBotAliasTimeouts"] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/lex_bot_alias aws_lex_bot_alias} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param bot_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot_alias#bot_name LexBotAlias#bot_name}.
        :param bot_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot_alias#bot_version LexBotAlias#bot_version}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot_alias#name LexBotAlias#name}.
        :param conversation_logs: conversation_logs block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot_alias#conversation_logs LexBotAlias#conversation_logs}
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot_alias#description LexBotAlias#description}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot_alias#timeouts LexBotAlias#timeouts}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = LexBotAliasConfig(
            bot_name=bot_name,
            bot_version=bot_version,
            name=name,
            conversation_logs=conversation_logs,
            description=description,
            timeouts=timeouts,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putConversationLogs")
    def put_conversation_logs(
        self,
        *,
        iam_role_arn: builtins.str,
        log_settings: typing.Optional[typing.Sequence["LexBotAliasConversationLogsLogSettings"]] = None,
    ) -> None:
        '''
        :param iam_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot_alias#iam_role_arn LexBotAlias#iam_role_arn}.
        :param log_settings: log_settings block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot_alias#log_settings LexBotAlias#log_settings}
        '''
        value = LexBotAliasConversationLogs(
            iam_role_arn=iam_role_arn, log_settings=log_settings
        )

        return typing.cast(None, jsii.invoke(self, "putConversationLogs", [value]))

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot_alias#create LexBotAlias#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot_alias#delete LexBotAlias#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot_alias#update LexBotAlias#update}.
        '''
        value = LexBotAliasTimeouts(create=create, delete=delete, update=update)

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetConversationLogs")
    def reset_conversation_logs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConversationLogs", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

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
    @jsii.member(jsii_name="checksum")
    def checksum(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "checksum"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="conversationLogs")
    def conversation_logs(self) -> "LexBotAliasConversationLogsOutputReference":
        return typing.cast("LexBotAliasConversationLogsOutputReference", jsii.get(self, "conversationLogs"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createdDate")
    def created_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdDate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lastUpdatedDate")
    def last_updated_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lastUpdatedDate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "LexBotAliasTimeoutsOutputReference":
        return typing.cast("LexBotAliasTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="botNameInput")
    def bot_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "botNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="botVersionInput")
    def bot_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "botVersionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="conversationLogsInput")
    def conversation_logs_input(self) -> typing.Optional["LexBotAliasConversationLogs"]:
        return typing.cast(typing.Optional["LexBotAliasConversationLogs"], jsii.get(self, "conversationLogsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(self) -> typing.Optional["LexBotAliasTimeouts"]:
        return typing.cast(typing.Optional["LexBotAliasTimeouts"], jsii.get(self, "timeoutsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="botName")
    def bot_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "botName"))

    @bot_name.setter
    def bot_name(self, value: builtins.str) -> None:
        jsii.set(self, "botName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="botVersion")
    def bot_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "botVersion"))

    @bot_version.setter
    def bot_version(self, value: builtins.str) -> None:
        jsii.set(self, "botVersion", value)

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


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lex.LexBotAliasConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "bot_name": "botName",
        "bot_version": "botVersion",
        "name": "name",
        "conversation_logs": "conversationLogs",
        "description": "description",
        "timeouts": "timeouts",
    },
)
class LexBotAliasConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        bot_name: builtins.str,
        bot_version: builtins.str,
        name: builtins.str,
        conversation_logs: typing.Optional["LexBotAliasConversationLogs"] = None,
        description: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional["LexBotAliasTimeouts"] = None,
    ) -> None:
        '''AWS Lex.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param bot_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot_alias#bot_name LexBotAlias#bot_name}.
        :param bot_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot_alias#bot_version LexBotAlias#bot_version}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot_alias#name LexBotAlias#name}.
        :param conversation_logs: conversation_logs block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot_alias#conversation_logs LexBotAlias#conversation_logs}
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot_alias#description LexBotAlias#description}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot_alias#timeouts LexBotAlias#timeouts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(conversation_logs, dict):
            conversation_logs = LexBotAliasConversationLogs(**conversation_logs)
        if isinstance(timeouts, dict):
            timeouts = LexBotAliasTimeouts(**timeouts)
        self._values: typing.Dict[str, typing.Any] = {
            "bot_name": bot_name,
            "bot_version": bot_version,
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
        if conversation_logs is not None:
            self._values["conversation_logs"] = conversation_logs
        if description is not None:
            self._values["description"] = description
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
    def bot_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot_alias#bot_name LexBotAlias#bot_name}.'''
        result = self._values.get("bot_name")
        assert result is not None, "Required property 'bot_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def bot_version(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot_alias#bot_version LexBotAlias#bot_version}.'''
        result = self._values.get("bot_version")
        assert result is not None, "Required property 'bot_version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot_alias#name LexBotAlias#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def conversation_logs(self) -> typing.Optional["LexBotAliasConversationLogs"]:
        '''conversation_logs block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot_alias#conversation_logs LexBotAlias#conversation_logs}
        '''
        result = self._values.get("conversation_logs")
        return typing.cast(typing.Optional["LexBotAliasConversationLogs"], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot_alias#description LexBotAlias#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["LexBotAliasTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot_alias#timeouts LexBotAlias#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["LexBotAliasTimeouts"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LexBotAliasConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lex.LexBotAliasConversationLogs",
    jsii_struct_bases=[],
    name_mapping={"iam_role_arn": "iamRoleArn", "log_settings": "logSettings"},
)
class LexBotAliasConversationLogs:
    def __init__(
        self,
        *,
        iam_role_arn: builtins.str,
        log_settings: typing.Optional[typing.Sequence["LexBotAliasConversationLogsLogSettings"]] = None,
    ) -> None:
        '''
        :param iam_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot_alias#iam_role_arn LexBotAlias#iam_role_arn}.
        :param log_settings: log_settings block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot_alias#log_settings LexBotAlias#log_settings}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "iam_role_arn": iam_role_arn,
        }
        if log_settings is not None:
            self._values["log_settings"] = log_settings

    @builtins.property
    def iam_role_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot_alias#iam_role_arn LexBotAlias#iam_role_arn}.'''
        result = self._values.get("iam_role_arn")
        assert result is not None, "Required property 'iam_role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def log_settings(
        self,
    ) -> typing.Optional[typing.List["LexBotAliasConversationLogsLogSettings"]]:
        '''log_settings block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot_alias#log_settings LexBotAlias#log_settings}
        '''
        result = self._values.get("log_settings")
        return typing.cast(typing.Optional[typing.List["LexBotAliasConversationLogsLogSettings"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LexBotAliasConversationLogs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lex.LexBotAliasConversationLogsLogSettings",
    jsii_struct_bases=[],
    name_mapping={
        "destination": "destination",
        "log_type": "logType",
        "resource_arn": "resourceArn",
        "kms_key_arn": "kmsKeyArn",
    },
)
class LexBotAliasConversationLogsLogSettings:
    def __init__(
        self,
        *,
        destination: builtins.str,
        log_type: builtins.str,
        resource_arn: builtins.str,
        kms_key_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot_alias#destination LexBotAlias#destination}.
        :param log_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot_alias#log_type LexBotAlias#log_type}.
        :param resource_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot_alias#resource_arn LexBotAlias#resource_arn}.
        :param kms_key_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot_alias#kms_key_arn LexBotAlias#kms_key_arn}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "destination": destination,
            "log_type": log_type,
            "resource_arn": resource_arn,
        }
        if kms_key_arn is not None:
            self._values["kms_key_arn"] = kms_key_arn

    @builtins.property
    def destination(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot_alias#destination LexBotAlias#destination}.'''
        result = self._values.get("destination")
        assert result is not None, "Required property 'destination' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def log_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot_alias#log_type LexBotAlias#log_type}.'''
        result = self._values.get("log_type")
        assert result is not None, "Required property 'log_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def resource_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot_alias#resource_arn LexBotAlias#resource_arn}.'''
        result = self._values.get("resource_arn")
        assert result is not None, "Required property 'resource_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def kms_key_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot_alias#kms_key_arn LexBotAlias#kms_key_arn}.'''
        result = self._values.get("kms_key_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LexBotAliasConversationLogsLogSettings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LexBotAliasConversationLogsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lex.LexBotAliasConversationLogsOutputReference",
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

    @jsii.member(jsii_name="resetLogSettings")
    def reset_log_settings(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogSettings", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="iamRoleArnInput")
    def iam_role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "iamRoleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logSettingsInput")
    def log_settings_input(
        self,
    ) -> typing.Optional[typing.List[LexBotAliasConversationLogsLogSettings]]:
        return typing.cast(typing.Optional[typing.List[LexBotAliasConversationLogsLogSettings]], jsii.get(self, "logSettingsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="iamRoleArn")
    def iam_role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "iamRoleArn"))

    @iam_role_arn.setter
    def iam_role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "iamRoleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logSettings")
    def log_settings(self) -> typing.List[LexBotAliasConversationLogsLogSettings]:
        return typing.cast(typing.List[LexBotAliasConversationLogsLogSettings], jsii.get(self, "logSettings"))

    @log_settings.setter
    def log_settings(
        self,
        value: typing.List[LexBotAliasConversationLogsLogSettings],
    ) -> None:
        jsii.set(self, "logSettings", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[LexBotAliasConversationLogs]:
        return typing.cast(typing.Optional[LexBotAliasConversationLogs], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[LexBotAliasConversationLogs],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lex.LexBotAliasTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete", "update": "update"},
)
class LexBotAliasTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot_alias#create LexBotAlias#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot_alias#delete LexBotAlias#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot_alias#update LexBotAlias#update}.
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot_alias#create LexBotAlias#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot_alias#delete LexBotAlias#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot_alias#update LexBotAlias#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LexBotAliasTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LexBotAliasTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lex.LexBotAliasTimeoutsOutputReference",
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
    def internal_value(self) -> typing.Optional[LexBotAliasTimeouts]:
        return typing.cast(typing.Optional[LexBotAliasTimeouts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[LexBotAliasTimeouts]) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lex.LexBotClarificationPrompt",
    jsii_struct_bases=[],
    name_mapping={
        "max_attempts": "maxAttempts",
        "message": "message",
        "response_card": "responseCard",
    },
)
class LexBotClarificationPrompt:
    def __init__(
        self,
        *,
        max_attempts: jsii.Number,
        message: typing.Sequence["LexBotClarificationPromptMessage"],
        response_card: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param max_attempts: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#max_attempts LexBot#max_attempts}.
        :param message: message block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#message LexBot#message}
        :param response_card: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#response_card LexBot#response_card}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "max_attempts": max_attempts,
            "message": message,
        }
        if response_card is not None:
            self._values["response_card"] = response_card

    @builtins.property
    def max_attempts(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#max_attempts LexBot#max_attempts}.'''
        result = self._values.get("max_attempts")
        assert result is not None, "Required property 'max_attempts' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def message(self) -> typing.List["LexBotClarificationPromptMessage"]:
        '''message block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#message LexBot#message}
        '''
        result = self._values.get("message")
        assert result is not None, "Required property 'message' is missing"
        return typing.cast(typing.List["LexBotClarificationPromptMessage"], result)

    @builtins.property
    def response_card(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#response_card LexBot#response_card}.'''
        result = self._values.get("response_card")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LexBotClarificationPrompt(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lex.LexBotClarificationPromptMessage",
    jsii_struct_bases=[],
    name_mapping={
        "content": "content",
        "content_type": "contentType",
        "group_number": "groupNumber",
    },
)
class LexBotClarificationPromptMessage:
    def __init__(
        self,
        *,
        content: builtins.str,
        content_type: builtins.str,
        group_number: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param content: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#content LexBot#content}.
        :param content_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#content_type LexBot#content_type}.
        :param group_number: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#group_number LexBot#group_number}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "content": content,
            "content_type": content_type,
        }
        if group_number is not None:
            self._values["group_number"] = group_number

    @builtins.property
    def content(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#content LexBot#content}.'''
        result = self._values.get("content")
        assert result is not None, "Required property 'content' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def content_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#content_type LexBot#content_type}.'''
        result = self._values.get("content_type")
        assert result is not None, "Required property 'content_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def group_number(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#group_number LexBot#group_number}.'''
        result = self._values.get("group_number")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LexBotClarificationPromptMessage(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LexBotClarificationPromptOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lex.LexBotClarificationPromptOutputReference",
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

    @jsii.member(jsii_name="resetResponseCard")
    def reset_response_card(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResponseCard", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxAttemptsInput")
    def max_attempts_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxAttemptsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="messageInput")
    def message_input(
        self,
    ) -> typing.Optional[typing.List[LexBotClarificationPromptMessage]]:
        return typing.cast(typing.Optional[typing.List[LexBotClarificationPromptMessage]], jsii.get(self, "messageInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="responseCardInput")
    def response_card_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "responseCardInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxAttempts")
    def max_attempts(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxAttempts"))

    @max_attempts.setter
    def max_attempts(self, value: jsii.Number) -> None:
        jsii.set(self, "maxAttempts", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="message")
    def message(self) -> typing.List[LexBotClarificationPromptMessage]:
        return typing.cast(typing.List[LexBotClarificationPromptMessage], jsii.get(self, "message"))

    @message.setter
    def message(self, value: typing.List[LexBotClarificationPromptMessage]) -> None:
        jsii.set(self, "message", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="responseCard")
    def response_card(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "responseCard"))

    @response_card.setter
    def response_card(self, value: builtins.str) -> None:
        jsii.set(self, "responseCard", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[LexBotClarificationPrompt]:
        return typing.cast(typing.Optional[LexBotClarificationPrompt], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[LexBotClarificationPrompt]) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lex.LexBotConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "abort_statement": "abortStatement",
        "child_directed": "childDirected",
        "intent": "intent",
        "name": "name",
        "clarification_prompt": "clarificationPrompt",
        "create_version": "createVersion",
        "description": "description",
        "detect_sentiment": "detectSentiment",
        "enable_model_improvements": "enableModelImprovements",
        "idle_session_ttl_in_seconds": "idleSessionTtlInSeconds",
        "locale": "locale",
        "nlu_intent_confidence_threshold": "nluIntentConfidenceThreshold",
        "process_behavior": "processBehavior",
        "timeouts": "timeouts",
        "voice_id": "voiceId",
    },
)
class LexBotConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        abort_statement: LexBotAbortStatement,
        child_directed: typing.Union[builtins.bool, cdktf.IResolvable],
        intent: typing.Sequence["LexBotIntent"],
        name: builtins.str,
        clarification_prompt: typing.Optional[LexBotClarificationPrompt] = None,
        create_version: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        description: typing.Optional[builtins.str] = None,
        detect_sentiment: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        enable_model_improvements: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        idle_session_ttl_in_seconds: typing.Optional[jsii.Number] = None,
        locale: typing.Optional[builtins.str] = None,
        nlu_intent_confidence_threshold: typing.Optional[jsii.Number] = None,
        process_behavior: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional["LexBotTimeouts"] = None,
        voice_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Lex.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param abort_statement: abort_statement block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#abort_statement LexBot#abort_statement}
        :param child_directed: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#child_directed LexBot#child_directed}.
        :param intent: intent block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#intent LexBot#intent}
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#name LexBot#name}.
        :param clarification_prompt: clarification_prompt block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#clarification_prompt LexBot#clarification_prompt}
        :param create_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#create_version LexBot#create_version}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#description LexBot#description}.
        :param detect_sentiment: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#detect_sentiment LexBot#detect_sentiment}.
        :param enable_model_improvements: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#enable_model_improvements LexBot#enable_model_improvements}.
        :param idle_session_ttl_in_seconds: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#idle_session_ttl_in_seconds LexBot#idle_session_ttl_in_seconds}.
        :param locale: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#locale LexBot#locale}.
        :param nlu_intent_confidence_threshold: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#nlu_intent_confidence_threshold LexBot#nlu_intent_confidence_threshold}.
        :param process_behavior: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#process_behavior LexBot#process_behavior}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#timeouts LexBot#timeouts}
        :param voice_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#voice_id LexBot#voice_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(abort_statement, dict):
            abort_statement = LexBotAbortStatement(**abort_statement)
        if isinstance(clarification_prompt, dict):
            clarification_prompt = LexBotClarificationPrompt(**clarification_prompt)
        if isinstance(timeouts, dict):
            timeouts = LexBotTimeouts(**timeouts)
        self._values: typing.Dict[str, typing.Any] = {
            "abort_statement": abort_statement,
            "child_directed": child_directed,
            "intent": intent,
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
        if clarification_prompt is not None:
            self._values["clarification_prompt"] = clarification_prompt
        if create_version is not None:
            self._values["create_version"] = create_version
        if description is not None:
            self._values["description"] = description
        if detect_sentiment is not None:
            self._values["detect_sentiment"] = detect_sentiment
        if enable_model_improvements is not None:
            self._values["enable_model_improvements"] = enable_model_improvements
        if idle_session_ttl_in_seconds is not None:
            self._values["idle_session_ttl_in_seconds"] = idle_session_ttl_in_seconds
        if locale is not None:
            self._values["locale"] = locale
        if nlu_intent_confidence_threshold is not None:
            self._values["nlu_intent_confidence_threshold"] = nlu_intent_confidence_threshold
        if process_behavior is not None:
            self._values["process_behavior"] = process_behavior
        if timeouts is not None:
            self._values["timeouts"] = timeouts
        if voice_id is not None:
            self._values["voice_id"] = voice_id

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
    def abort_statement(self) -> LexBotAbortStatement:
        '''abort_statement block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#abort_statement LexBot#abort_statement}
        '''
        result = self._values.get("abort_statement")
        assert result is not None, "Required property 'abort_statement' is missing"
        return typing.cast(LexBotAbortStatement, result)

    @builtins.property
    def child_directed(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#child_directed LexBot#child_directed}.'''
        result = self._values.get("child_directed")
        assert result is not None, "Required property 'child_directed' is missing"
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], result)

    @builtins.property
    def intent(self) -> typing.List["LexBotIntent"]:
        '''intent block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#intent LexBot#intent}
        '''
        result = self._values.get("intent")
        assert result is not None, "Required property 'intent' is missing"
        return typing.cast(typing.List["LexBotIntent"], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#name LexBot#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def clarification_prompt(self) -> typing.Optional[LexBotClarificationPrompt]:
        '''clarification_prompt block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#clarification_prompt LexBot#clarification_prompt}
        '''
        result = self._values.get("clarification_prompt")
        return typing.cast(typing.Optional[LexBotClarificationPrompt], result)

    @builtins.property
    def create_version(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#create_version LexBot#create_version}.'''
        result = self._values.get("create_version")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#description LexBot#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def detect_sentiment(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#detect_sentiment LexBot#detect_sentiment}.'''
        result = self._values.get("detect_sentiment")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def enable_model_improvements(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#enable_model_improvements LexBot#enable_model_improvements}.'''
        result = self._values.get("enable_model_improvements")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def idle_session_ttl_in_seconds(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#idle_session_ttl_in_seconds LexBot#idle_session_ttl_in_seconds}.'''
        result = self._values.get("idle_session_ttl_in_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def locale(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#locale LexBot#locale}.'''
        result = self._values.get("locale")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def nlu_intent_confidence_threshold(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#nlu_intent_confidence_threshold LexBot#nlu_intent_confidence_threshold}.'''
        result = self._values.get("nlu_intent_confidence_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def process_behavior(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#process_behavior LexBot#process_behavior}.'''
        result = self._values.get("process_behavior")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["LexBotTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#timeouts LexBot#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["LexBotTimeouts"], result)

    @builtins.property
    def voice_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#voice_id LexBot#voice_id}.'''
        result = self._values.get("voice_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LexBotConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lex.LexBotIntent",
    jsii_struct_bases=[],
    name_mapping={"intent_name": "intentName", "intent_version": "intentVersion"},
)
class LexBotIntent:
    def __init__(
        self,
        *,
        intent_name: builtins.str,
        intent_version: builtins.str,
    ) -> None:
        '''
        :param intent_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#intent_name LexBot#intent_name}.
        :param intent_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#intent_version LexBot#intent_version}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "intent_name": intent_name,
            "intent_version": intent_version,
        }

    @builtins.property
    def intent_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#intent_name LexBot#intent_name}.'''
        result = self._values.get("intent_name")
        assert result is not None, "Required property 'intent_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def intent_version(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#intent_version LexBot#intent_version}.'''
        result = self._values.get("intent_version")
        assert result is not None, "Required property 'intent_version' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LexBotIntent(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lex.LexBotTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete", "update": "update"},
)
class LexBotTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#create LexBot#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#delete LexBot#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#update LexBot#update}.
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#create LexBot#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#delete LexBot#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_bot#update LexBot#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LexBotTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LexBotTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lex.LexBotTimeoutsOutputReference",
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
    def internal_value(self) -> typing.Optional[LexBotTimeouts]:
        return typing.cast(typing.Optional[LexBotTimeouts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[LexBotTimeouts]) -> None:
        jsii.set(self, "internalValue", value)


class LexIntent(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lex.LexIntent",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/lex_intent aws_lex_intent}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        fulfillment_activity: "LexIntentFulfillmentActivity",
        name: builtins.str,
        conclusion_statement: typing.Optional["LexIntentConclusionStatement"] = None,
        confirmation_prompt: typing.Optional["LexIntentConfirmationPrompt"] = None,
        create_version: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        description: typing.Optional[builtins.str] = None,
        dialog_code_hook: typing.Optional["LexIntentDialogCodeHook"] = None,
        follow_up_prompt: typing.Optional["LexIntentFollowUpPrompt"] = None,
        parent_intent_signature: typing.Optional[builtins.str] = None,
        rejection_statement: typing.Optional["LexIntentRejectionStatement"] = None,
        sample_utterances: typing.Optional[typing.Sequence[builtins.str]] = None,
        slot: typing.Optional[typing.Sequence["LexIntentSlot"]] = None,
        timeouts: typing.Optional["LexIntentTimeouts"] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/lex_intent aws_lex_intent} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param fulfillment_activity: fulfillment_activity block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#fulfillment_activity LexIntent#fulfillment_activity}
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#name LexIntent#name}.
        :param conclusion_statement: conclusion_statement block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#conclusion_statement LexIntent#conclusion_statement}
        :param confirmation_prompt: confirmation_prompt block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#confirmation_prompt LexIntent#confirmation_prompt}
        :param create_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#create_version LexIntent#create_version}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#description LexIntent#description}.
        :param dialog_code_hook: dialog_code_hook block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#dialog_code_hook LexIntent#dialog_code_hook}
        :param follow_up_prompt: follow_up_prompt block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#follow_up_prompt LexIntent#follow_up_prompt}
        :param parent_intent_signature: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#parent_intent_signature LexIntent#parent_intent_signature}.
        :param rejection_statement: rejection_statement block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#rejection_statement LexIntent#rejection_statement}
        :param sample_utterances: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#sample_utterances LexIntent#sample_utterances}.
        :param slot: slot block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#slot LexIntent#slot}
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#timeouts LexIntent#timeouts}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = LexIntentConfig(
            fulfillment_activity=fulfillment_activity,
            name=name,
            conclusion_statement=conclusion_statement,
            confirmation_prompt=confirmation_prompt,
            create_version=create_version,
            description=description,
            dialog_code_hook=dialog_code_hook,
            follow_up_prompt=follow_up_prompt,
            parent_intent_signature=parent_intent_signature,
            rejection_statement=rejection_statement,
            sample_utterances=sample_utterances,
            slot=slot,
            timeouts=timeouts,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putConclusionStatement")
    def put_conclusion_statement(
        self,
        *,
        message: typing.Sequence["LexIntentConclusionStatementMessage"],
        response_card: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param message: message block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#message LexIntent#message}
        :param response_card: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#response_card LexIntent#response_card}.
        '''
        value = LexIntentConclusionStatement(
            message=message, response_card=response_card
        )

        return typing.cast(None, jsii.invoke(self, "putConclusionStatement", [value]))

    @jsii.member(jsii_name="putConfirmationPrompt")
    def put_confirmation_prompt(
        self,
        *,
        max_attempts: jsii.Number,
        message: typing.Sequence["LexIntentConfirmationPromptMessage"],
        response_card: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param max_attempts: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#max_attempts LexIntent#max_attempts}.
        :param message: message block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#message LexIntent#message}
        :param response_card: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#response_card LexIntent#response_card}.
        '''
        value = LexIntentConfirmationPrompt(
            max_attempts=max_attempts, message=message, response_card=response_card
        )

        return typing.cast(None, jsii.invoke(self, "putConfirmationPrompt", [value]))

    @jsii.member(jsii_name="putDialogCodeHook")
    def put_dialog_code_hook(
        self,
        *,
        message_version: builtins.str,
        uri: builtins.str,
    ) -> None:
        '''
        :param message_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#message_version LexIntent#message_version}.
        :param uri: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#uri LexIntent#uri}.
        '''
        value = LexIntentDialogCodeHook(message_version=message_version, uri=uri)

        return typing.cast(None, jsii.invoke(self, "putDialogCodeHook", [value]))

    @jsii.member(jsii_name="putFollowUpPrompt")
    def put_follow_up_prompt(
        self,
        *,
        prompt: "LexIntentFollowUpPromptPrompt",
        rejection_statement: "LexIntentFollowUpPromptRejectionStatement",
    ) -> None:
        '''
        :param prompt: prompt block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#prompt LexIntent#prompt}
        :param rejection_statement: rejection_statement block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#rejection_statement LexIntent#rejection_statement}
        '''
        value = LexIntentFollowUpPrompt(
            prompt=prompt, rejection_statement=rejection_statement
        )

        return typing.cast(None, jsii.invoke(self, "putFollowUpPrompt", [value]))

    @jsii.member(jsii_name="putFulfillmentActivity")
    def put_fulfillment_activity(
        self,
        *,
        type: builtins.str,
        code_hook: typing.Optional["LexIntentFulfillmentActivityCodeHook"] = None,
    ) -> None:
        '''
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#type LexIntent#type}.
        :param code_hook: code_hook block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#code_hook LexIntent#code_hook}
        '''
        value = LexIntentFulfillmentActivity(type=type, code_hook=code_hook)

        return typing.cast(None, jsii.invoke(self, "putFulfillmentActivity", [value]))

    @jsii.member(jsii_name="putRejectionStatement")
    def put_rejection_statement(
        self,
        *,
        message: typing.Sequence["LexIntentRejectionStatementMessage"],
        response_card: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param message: message block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#message LexIntent#message}
        :param response_card: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#response_card LexIntent#response_card}.
        '''
        value = LexIntentRejectionStatement(
            message=message, response_card=response_card
        )

        return typing.cast(None, jsii.invoke(self, "putRejectionStatement", [value]))

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#create LexIntent#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#delete LexIntent#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#update LexIntent#update}.
        '''
        value = LexIntentTimeouts(create=create, delete=delete, update=update)

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetConclusionStatement")
    def reset_conclusion_statement(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConclusionStatement", []))

    @jsii.member(jsii_name="resetConfirmationPrompt")
    def reset_confirmation_prompt(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConfirmationPrompt", []))

    @jsii.member(jsii_name="resetCreateVersion")
    def reset_create_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreateVersion", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetDialogCodeHook")
    def reset_dialog_code_hook(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDialogCodeHook", []))

    @jsii.member(jsii_name="resetFollowUpPrompt")
    def reset_follow_up_prompt(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFollowUpPrompt", []))

    @jsii.member(jsii_name="resetParentIntentSignature")
    def reset_parent_intent_signature(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetParentIntentSignature", []))

    @jsii.member(jsii_name="resetRejectionStatement")
    def reset_rejection_statement(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRejectionStatement", []))

    @jsii.member(jsii_name="resetSampleUtterances")
    def reset_sample_utterances(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSampleUtterances", []))

    @jsii.member(jsii_name="resetSlot")
    def reset_slot(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSlot", []))

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
    @jsii.member(jsii_name="checksum")
    def checksum(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "checksum"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="conclusionStatement")
    def conclusion_statement(self) -> "LexIntentConclusionStatementOutputReference":
        return typing.cast("LexIntentConclusionStatementOutputReference", jsii.get(self, "conclusionStatement"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="confirmationPrompt")
    def confirmation_prompt(self) -> "LexIntentConfirmationPromptOutputReference":
        return typing.cast("LexIntentConfirmationPromptOutputReference", jsii.get(self, "confirmationPrompt"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createdDate")
    def created_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdDate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dialogCodeHook")
    def dialog_code_hook(self) -> "LexIntentDialogCodeHookOutputReference":
        return typing.cast("LexIntentDialogCodeHookOutputReference", jsii.get(self, "dialogCodeHook"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="followUpPrompt")
    def follow_up_prompt(self) -> "LexIntentFollowUpPromptOutputReference":
        return typing.cast("LexIntentFollowUpPromptOutputReference", jsii.get(self, "followUpPrompt"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fulfillmentActivity")
    def fulfillment_activity(self) -> "LexIntentFulfillmentActivityOutputReference":
        return typing.cast("LexIntentFulfillmentActivityOutputReference", jsii.get(self, "fulfillmentActivity"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lastUpdatedDate")
    def last_updated_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lastUpdatedDate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rejectionStatement")
    def rejection_statement(self) -> "LexIntentRejectionStatementOutputReference":
        return typing.cast("LexIntentRejectionStatementOutputReference", jsii.get(self, "rejectionStatement"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "LexIntentTimeoutsOutputReference":
        return typing.cast("LexIntentTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="conclusionStatementInput")
    def conclusion_statement_input(
        self,
    ) -> typing.Optional["LexIntentConclusionStatement"]:
        return typing.cast(typing.Optional["LexIntentConclusionStatement"], jsii.get(self, "conclusionStatementInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="confirmationPromptInput")
    def confirmation_prompt_input(
        self,
    ) -> typing.Optional["LexIntentConfirmationPrompt"]:
        return typing.cast(typing.Optional["LexIntentConfirmationPrompt"], jsii.get(self, "confirmationPromptInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createVersionInput")
    def create_version_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "createVersionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dialogCodeHookInput")
    def dialog_code_hook_input(self) -> typing.Optional["LexIntentDialogCodeHook"]:
        return typing.cast(typing.Optional["LexIntentDialogCodeHook"], jsii.get(self, "dialogCodeHookInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="followUpPromptInput")
    def follow_up_prompt_input(self) -> typing.Optional["LexIntentFollowUpPrompt"]:
        return typing.cast(typing.Optional["LexIntentFollowUpPrompt"], jsii.get(self, "followUpPromptInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fulfillmentActivityInput")
    def fulfillment_activity_input(
        self,
    ) -> typing.Optional["LexIntentFulfillmentActivity"]:
        return typing.cast(typing.Optional["LexIntentFulfillmentActivity"], jsii.get(self, "fulfillmentActivityInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parentIntentSignatureInput")
    def parent_intent_signature_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "parentIntentSignatureInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rejectionStatementInput")
    def rejection_statement_input(
        self,
    ) -> typing.Optional["LexIntentRejectionStatement"]:
        return typing.cast(typing.Optional["LexIntentRejectionStatement"], jsii.get(self, "rejectionStatementInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sampleUtterancesInput")
    def sample_utterances_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "sampleUtterancesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="slotInput")
    def slot_input(self) -> typing.Optional[typing.List["LexIntentSlot"]]:
        return typing.cast(typing.Optional[typing.List["LexIntentSlot"]], jsii.get(self, "slotInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(self) -> typing.Optional["LexIntentTimeouts"]:
        return typing.cast(typing.Optional["LexIntentTimeouts"], jsii.get(self, "timeoutsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createVersion")
    def create_version(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "createVersion"))

    @create_version.setter
    def create_version(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "createVersion", value)

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
    @jsii.member(jsii_name="parentIntentSignature")
    def parent_intent_signature(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "parentIntentSignature"))

    @parent_intent_signature.setter
    def parent_intent_signature(self, value: builtins.str) -> None:
        jsii.set(self, "parentIntentSignature", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sampleUtterances")
    def sample_utterances(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "sampleUtterances"))

    @sample_utterances.setter
    def sample_utterances(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "sampleUtterances", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="slot")
    def slot(self) -> typing.List["LexIntentSlot"]:
        return typing.cast(typing.List["LexIntentSlot"], jsii.get(self, "slot"))

    @slot.setter
    def slot(self, value: typing.List["LexIntentSlot"]) -> None:
        jsii.set(self, "slot", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lex.LexIntentConclusionStatement",
    jsii_struct_bases=[],
    name_mapping={"message": "message", "response_card": "responseCard"},
)
class LexIntentConclusionStatement:
    def __init__(
        self,
        *,
        message: typing.Sequence["LexIntentConclusionStatementMessage"],
        response_card: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param message: message block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#message LexIntent#message}
        :param response_card: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#response_card LexIntent#response_card}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "message": message,
        }
        if response_card is not None:
            self._values["response_card"] = response_card

    @builtins.property
    def message(self) -> typing.List["LexIntentConclusionStatementMessage"]:
        '''message block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#message LexIntent#message}
        '''
        result = self._values.get("message")
        assert result is not None, "Required property 'message' is missing"
        return typing.cast(typing.List["LexIntentConclusionStatementMessage"], result)

    @builtins.property
    def response_card(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#response_card LexIntent#response_card}.'''
        result = self._values.get("response_card")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LexIntentConclusionStatement(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lex.LexIntentConclusionStatementMessage",
    jsii_struct_bases=[],
    name_mapping={
        "content": "content",
        "content_type": "contentType",
        "group_number": "groupNumber",
    },
)
class LexIntentConclusionStatementMessage:
    def __init__(
        self,
        *,
        content: builtins.str,
        content_type: builtins.str,
        group_number: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param content: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#content LexIntent#content}.
        :param content_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#content_type LexIntent#content_type}.
        :param group_number: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#group_number LexIntent#group_number}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "content": content,
            "content_type": content_type,
        }
        if group_number is not None:
            self._values["group_number"] = group_number

    @builtins.property
    def content(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#content LexIntent#content}.'''
        result = self._values.get("content")
        assert result is not None, "Required property 'content' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def content_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#content_type LexIntent#content_type}.'''
        result = self._values.get("content_type")
        assert result is not None, "Required property 'content_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def group_number(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#group_number LexIntent#group_number}.'''
        result = self._values.get("group_number")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LexIntentConclusionStatementMessage(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LexIntentConclusionStatementOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lex.LexIntentConclusionStatementOutputReference",
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

    @jsii.member(jsii_name="resetResponseCard")
    def reset_response_card(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResponseCard", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="messageInput")
    def message_input(
        self,
    ) -> typing.Optional[typing.List[LexIntentConclusionStatementMessage]]:
        return typing.cast(typing.Optional[typing.List[LexIntentConclusionStatementMessage]], jsii.get(self, "messageInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="responseCardInput")
    def response_card_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "responseCardInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="message")
    def message(self) -> typing.List[LexIntentConclusionStatementMessage]:
        return typing.cast(typing.List[LexIntentConclusionStatementMessage], jsii.get(self, "message"))

    @message.setter
    def message(self, value: typing.List[LexIntentConclusionStatementMessage]) -> None:
        jsii.set(self, "message", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="responseCard")
    def response_card(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "responseCard"))

    @response_card.setter
    def response_card(self, value: builtins.str) -> None:
        jsii.set(self, "responseCard", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[LexIntentConclusionStatement]:
        return typing.cast(typing.Optional[LexIntentConclusionStatement], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[LexIntentConclusionStatement],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lex.LexIntentConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "fulfillment_activity": "fulfillmentActivity",
        "name": "name",
        "conclusion_statement": "conclusionStatement",
        "confirmation_prompt": "confirmationPrompt",
        "create_version": "createVersion",
        "description": "description",
        "dialog_code_hook": "dialogCodeHook",
        "follow_up_prompt": "followUpPrompt",
        "parent_intent_signature": "parentIntentSignature",
        "rejection_statement": "rejectionStatement",
        "sample_utterances": "sampleUtterances",
        "slot": "slot",
        "timeouts": "timeouts",
    },
)
class LexIntentConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        fulfillment_activity: "LexIntentFulfillmentActivity",
        name: builtins.str,
        conclusion_statement: typing.Optional[LexIntentConclusionStatement] = None,
        confirmation_prompt: typing.Optional["LexIntentConfirmationPrompt"] = None,
        create_version: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        description: typing.Optional[builtins.str] = None,
        dialog_code_hook: typing.Optional["LexIntentDialogCodeHook"] = None,
        follow_up_prompt: typing.Optional["LexIntentFollowUpPrompt"] = None,
        parent_intent_signature: typing.Optional[builtins.str] = None,
        rejection_statement: typing.Optional["LexIntentRejectionStatement"] = None,
        sample_utterances: typing.Optional[typing.Sequence[builtins.str]] = None,
        slot: typing.Optional[typing.Sequence["LexIntentSlot"]] = None,
        timeouts: typing.Optional["LexIntentTimeouts"] = None,
    ) -> None:
        '''AWS Lex.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param fulfillment_activity: fulfillment_activity block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#fulfillment_activity LexIntent#fulfillment_activity}
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#name LexIntent#name}.
        :param conclusion_statement: conclusion_statement block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#conclusion_statement LexIntent#conclusion_statement}
        :param confirmation_prompt: confirmation_prompt block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#confirmation_prompt LexIntent#confirmation_prompt}
        :param create_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#create_version LexIntent#create_version}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#description LexIntent#description}.
        :param dialog_code_hook: dialog_code_hook block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#dialog_code_hook LexIntent#dialog_code_hook}
        :param follow_up_prompt: follow_up_prompt block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#follow_up_prompt LexIntent#follow_up_prompt}
        :param parent_intent_signature: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#parent_intent_signature LexIntent#parent_intent_signature}.
        :param rejection_statement: rejection_statement block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#rejection_statement LexIntent#rejection_statement}
        :param sample_utterances: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#sample_utterances LexIntent#sample_utterances}.
        :param slot: slot block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#slot LexIntent#slot}
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#timeouts LexIntent#timeouts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(fulfillment_activity, dict):
            fulfillment_activity = LexIntentFulfillmentActivity(**fulfillment_activity)
        if isinstance(conclusion_statement, dict):
            conclusion_statement = LexIntentConclusionStatement(**conclusion_statement)
        if isinstance(confirmation_prompt, dict):
            confirmation_prompt = LexIntentConfirmationPrompt(**confirmation_prompt)
        if isinstance(dialog_code_hook, dict):
            dialog_code_hook = LexIntentDialogCodeHook(**dialog_code_hook)
        if isinstance(follow_up_prompt, dict):
            follow_up_prompt = LexIntentFollowUpPrompt(**follow_up_prompt)
        if isinstance(rejection_statement, dict):
            rejection_statement = LexIntentRejectionStatement(**rejection_statement)
        if isinstance(timeouts, dict):
            timeouts = LexIntentTimeouts(**timeouts)
        self._values: typing.Dict[str, typing.Any] = {
            "fulfillment_activity": fulfillment_activity,
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
        if conclusion_statement is not None:
            self._values["conclusion_statement"] = conclusion_statement
        if confirmation_prompt is not None:
            self._values["confirmation_prompt"] = confirmation_prompt
        if create_version is not None:
            self._values["create_version"] = create_version
        if description is not None:
            self._values["description"] = description
        if dialog_code_hook is not None:
            self._values["dialog_code_hook"] = dialog_code_hook
        if follow_up_prompt is not None:
            self._values["follow_up_prompt"] = follow_up_prompt
        if parent_intent_signature is not None:
            self._values["parent_intent_signature"] = parent_intent_signature
        if rejection_statement is not None:
            self._values["rejection_statement"] = rejection_statement
        if sample_utterances is not None:
            self._values["sample_utterances"] = sample_utterances
        if slot is not None:
            self._values["slot"] = slot
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
    def fulfillment_activity(self) -> "LexIntentFulfillmentActivity":
        '''fulfillment_activity block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#fulfillment_activity LexIntent#fulfillment_activity}
        '''
        result = self._values.get("fulfillment_activity")
        assert result is not None, "Required property 'fulfillment_activity' is missing"
        return typing.cast("LexIntentFulfillmentActivity", result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#name LexIntent#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def conclusion_statement(self) -> typing.Optional[LexIntentConclusionStatement]:
        '''conclusion_statement block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#conclusion_statement LexIntent#conclusion_statement}
        '''
        result = self._values.get("conclusion_statement")
        return typing.cast(typing.Optional[LexIntentConclusionStatement], result)

    @builtins.property
    def confirmation_prompt(self) -> typing.Optional["LexIntentConfirmationPrompt"]:
        '''confirmation_prompt block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#confirmation_prompt LexIntent#confirmation_prompt}
        '''
        result = self._values.get("confirmation_prompt")
        return typing.cast(typing.Optional["LexIntentConfirmationPrompt"], result)

    @builtins.property
    def create_version(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#create_version LexIntent#create_version}.'''
        result = self._values.get("create_version")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#description LexIntent#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def dialog_code_hook(self) -> typing.Optional["LexIntentDialogCodeHook"]:
        '''dialog_code_hook block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#dialog_code_hook LexIntent#dialog_code_hook}
        '''
        result = self._values.get("dialog_code_hook")
        return typing.cast(typing.Optional["LexIntentDialogCodeHook"], result)

    @builtins.property
    def follow_up_prompt(self) -> typing.Optional["LexIntentFollowUpPrompt"]:
        '''follow_up_prompt block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#follow_up_prompt LexIntent#follow_up_prompt}
        '''
        result = self._values.get("follow_up_prompt")
        return typing.cast(typing.Optional["LexIntentFollowUpPrompt"], result)

    @builtins.property
    def parent_intent_signature(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#parent_intent_signature LexIntent#parent_intent_signature}.'''
        result = self._values.get("parent_intent_signature")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rejection_statement(self) -> typing.Optional["LexIntentRejectionStatement"]:
        '''rejection_statement block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#rejection_statement LexIntent#rejection_statement}
        '''
        result = self._values.get("rejection_statement")
        return typing.cast(typing.Optional["LexIntentRejectionStatement"], result)

    @builtins.property
    def sample_utterances(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#sample_utterances LexIntent#sample_utterances}.'''
        result = self._values.get("sample_utterances")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def slot(self) -> typing.Optional[typing.List["LexIntentSlot"]]:
        '''slot block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#slot LexIntent#slot}
        '''
        result = self._values.get("slot")
        return typing.cast(typing.Optional[typing.List["LexIntentSlot"]], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["LexIntentTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#timeouts LexIntent#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["LexIntentTimeouts"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LexIntentConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lex.LexIntentConfirmationPrompt",
    jsii_struct_bases=[],
    name_mapping={
        "max_attempts": "maxAttempts",
        "message": "message",
        "response_card": "responseCard",
    },
)
class LexIntentConfirmationPrompt:
    def __init__(
        self,
        *,
        max_attempts: jsii.Number,
        message: typing.Sequence["LexIntentConfirmationPromptMessage"],
        response_card: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param max_attempts: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#max_attempts LexIntent#max_attempts}.
        :param message: message block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#message LexIntent#message}
        :param response_card: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#response_card LexIntent#response_card}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "max_attempts": max_attempts,
            "message": message,
        }
        if response_card is not None:
            self._values["response_card"] = response_card

    @builtins.property
    def max_attempts(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#max_attempts LexIntent#max_attempts}.'''
        result = self._values.get("max_attempts")
        assert result is not None, "Required property 'max_attempts' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def message(self) -> typing.List["LexIntentConfirmationPromptMessage"]:
        '''message block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#message LexIntent#message}
        '''
        result = self._values.get("message")
        assert result is not None, "Required property 'message' is missing"
        return typing.cast(typing.List["LexIntentConfirmationPromptMessage"], result)

    @builtins.property
    def response_card(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#response_card LexIntent#response_card}.'''
        result = self._values.get("response_card")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LexIntentConfirmationPrompt(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lex.LexIntentConfirmationPromptMessage",
    jsii_struct_bases=[],
    name_mapping={
        "content": "content",
        "content_type": "contentType",
        "group_number": "groupNumber",
    },
)
class LexIntentConfirmationPromptMessage:
    def __init__(
        self,
        *,
        content: builtins.str,
        content_type: builtins.str,
        group_number: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param content: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#content LexIntent#content}.
        :param content_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#content_type LexIntent#content_type}.
        :param group_number: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#group_number LexIntent#group_number}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "content": content,
            "content_type": content_type,
        }
        if group_number is not None:
            self._values["group_number"] = group_number

    @builtins.property
    def content(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#content LexIntent#content}.'''
        result = self._values.get("content")
        assert result is not None, "Required property 'content' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def content_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#content_type LexIntent#content_type}.'''
        result = self._values.get("content_type")
        assert result is not None, "Required property 'content_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def group_number(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#group_number LexIntent#group_number}.'''
        result = self._values.get("group_number")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LexIntentConfirmationPromptMessage(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LexIntentConfirmationPromptOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lex.LexIntentConfirmationPromptOutputReference",
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

    @jsii.member(jsii_name="resetResponseCard")
    def reset_response_card(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResponseCard", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxAttemptsInput")
    def max_attempts_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxAttemptsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="messageInput")
    def message_input(
        self,
    ) -> typing.Optional[typing.List[LexIntentConfirmationPromptMessage]]:
        return typing.cast(typing.Optional[typing.List[LexIntentConfirmationPromptMessage]], jsii.get(self, "messageInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="responseCardInput")
    def response_card_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "responseCardInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxAttempts")
    def max_attempts(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxAttempts"))

    @max_attempts.setter
    def max_attempts(self, value: jsii.Number) -> None:
        jsii.set(self, "maxAttempts", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="message")
    def message(self) -> typing.List[LexIntentConfirmationPromptMessage]:
        return typing.cast(typing.List[LexIntentConfirmationPromptMessage], jsii.get(self, "message"))

    @message.setter
    def message(self, value: typing.List[LexIntentConfirmationPromptMessage]) -> None:
        jsii.set(self, "message", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="responseCard")
    def response_card(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "responseCard"))

    @response_card.setter
    def response_card(self, value: builtins.str) -> None:
        jsii.set(self, "responseCard", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[LexIntentConfirmationPrompt]:
        return typing.cast(typing.Optional[LexIntentConfirmationPrompt], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[LexIntentConfirmationPrompt],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lex.LexIntentDialogCodeHook",
    jsii_struct_bases=[],
    name_mapping={"message_version": "messageVersion", "uri": "uri"},
)
class LexIntentDialogCodeHook:
    def __init__(self, *, message_version: builtins.str, uri: builtins.str) -> None:
        '''
        :param message_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#message_version LexIntent#message_version}.
        :param uri: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#uri LexIntent#uri}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "message_version": message_version,
            "uri": uri,
        }

    @builtins.property
    def message_version(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#message_version LexIntent#message_version}.'''
        result = self._values.get("message_version")
        assert result is not None, "Required property 'message_version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def uri(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#uri LexIntent#uri}.'''
        result = self._values.get("uri")
        assert result is not None, "Required property 'uri' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LexIntentDialogCodeHook(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LexIntentDialogCodeHookOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lex.LexIntentDialogCodeHookOutputReference",
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
    @jsii.member(jsii_name="messageVersionInput")
    def message_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "messageVersionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="uriInput")
    def uri_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "uriInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="messageVersion")
    def message_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "messageVersion"))

    @message_version.setter
    def message_version(self, value: builtins.str) -> None:
        jsii.set(self, "messageVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="uri")
    def uri(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uri"))

    @uri.setter
    def uri(self, value: builtins.str) -> None:
        jsii.set(self, "uri", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[LexIntentDialogCodeHook]:
        return typing.cast(typing.Optional[LexIntentDialogCodeHook], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[LexIntentDialogCodeHook]) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lex.LexIntentFollowUpPrompt",
    jsii_struct_bases=[],
    name_mapping={"prompt": "prompt", "rejection_statement": "rejectionStatement"},
)
class LexIntentFollowUpPrompt:
    def __init__(
        self,
        *,
        prompt: "LexIntentFollowUpPromptPrompt",
        rejection_statement: "LexIntentFollowUpPromptRejectionStatement",
    ) -> None:
        '''
        :param prompt: prompt block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#prompt LexIntent#prompt}
        :param rejection_statement: rejection_statement block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#rejection_statement LexIntent#rejection_statement}
        '''
        if isinstance(prompt, dict):
            prompt = LexIntentFollowUpPromptPrompt(**prompt)
        if isinstance(rejection_statement, dict):
            rejection_statement = LexIntentFollowUpPromptRejectionStatement(**rejection_statement)
        self._values: typing.Dict[str, typing.Any] = {
            "prompt": prompt,
            "rejection_statement": rejection_statement,
        }

    @builtins.property
    def prompt(self) -> "LexIntentFollowUpPromptPrompt":
        '''prompt block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#prompt LexIntent#prompt}
        '''
        result = self._values.get("prompt")
        assert result is not None, "Required property 'prompt' is missing"
        return typing.cast("LexIntentFollowUpPromptPrompt", result)

    @builtins.property
    def rejection_statement(self) -> "LexIntentFollowUpPromptRejectionStatement":
        '''rejection_statement block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#rejection_statement LexIntent#rejection_statement}
        '''
        result = self._values.get("rejection_statement")
        assert result is not None, "Required property 'rejection_statement' is missing"
        return typing.cast("LexIntentFollowUpPromptRejectionStatement", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LexIntentFollowUpPrompt(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LexIntentFollowUpPromptOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lex.LexIntentFollowUpPromptOutputReference",
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

    @jsii.member(jsii_name="putPrompt")
    def put_prompt(
        self,
        *,
        max_attempts: jsii.Number,
        message: typing.Sequence["LexIntentFollowUpPromptPromptMessage"],
        response_card: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param max_attempts: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#max_attempts LexIntent#max_attempts}.
        :param message: message block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#message LexIntent#message}
        :param response_card: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#response_card LexIntent#response_card}.
        '''
        value = LexIntentFollowUpPromptPrompt(
            max_attempts=max_attempts, message=message, response_card=response_card
        )

        return typing.cast(None, jsii.invoke(self, "putPrompt", [value]))

    @jsii.member(jsii_name="putRejectionStatement")
    def put_rejection_statement(
        self,
        *,
        message: typing.Sequence["LexIntentFollowUpPromptRejectionStatementMessage"],
        response_card: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param message: message block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#message LexIntent#message}
        :param response_card: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#response_card LexIntent#response_card}.
        '''
        value = LexIntentFollowUpPromptRejectionStatement(
            message=message, response_card=response_card
        )

        return typing.cast(None, jsii.invoke(self, "putRejectionStatement", [value]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="prompt")
    def prompt(self) -> "LexIntentFollowUpPromptPromptOutputReference":
        return typing.cast("LexIntentFollowUpPromptPromptOutputReference", jsii.get(self, "prompt"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rejectionStatement")
    def rejection_statement(
        self,
    ) -> "LexIntentFollowUpPromptRejectionStatementOutputReference":
        return typing.cast("LexIntentFollowUpPromptRejectionStatementOutputReference", jsii.get(self, "rejectionStatement"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="promptInput")
    def prompt_input(self) -> typing.Optional["LexIntentFollowUpPromptPrompt"]:
        return typing.cast(typing.Optional["LexIntentFollowUpPromptPrompt"], jsii.get(self, "promptInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rejectionStatementInput")
    def rejection_statement_input(
        self,
    ) -> typing.Optional["LexIntentFollowUpPromptRejectionStatement"]:
        return typing.cast(typing.Optional["LexIntentFollowUpPromptRejectionStatement"], jsii.get(self, "rejectionStatementInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[LexIntentFollowUpPrompt]:
        return typing.cast(typing.Optional[LexIntentFollowUpPrompt], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[LexIntentFollowUpPrompt]) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lex.LexIntentFollowUpPromptPrompt",
    jsii_struct_bases=[],
    name_mapping={
        "max_attempts": "maxAttempts",
        "message": "message",
        "response_card": "responseCard",
    },
)
class LexIntentFollowUpPromptPrompt:
    def __init__(
        self,
        *,
        max_attempts: jsii.Number,
        message: typing.Sequence["LexIntentFollowUpPromptPromptMessage"],
        response_card: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param max_attempts: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#max_attempts LexIntent#max_attempts}.
        :param message: message block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#message LexIntent#message}
        :param response_card: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#response_card LexIntent#response_card}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "max_attempts": max_attempts,
            "message": message,
        }
        if response_card is not None:
            self._values["response_card"] = response_card

    @builtins.property
    def max_attempts(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#max_attempts LexIntent#max_attempts}.'''
        result = self._values.get("max_attempts")
        assert result is not None, "Required property 'max_attempts' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def message(self) -> typing.List["LexIntentFollowUpPromptPromptMessage"]:
        '''message block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#message LexIntent#message}
        '''
        result = self._values.get("message")
        assert result is not None, "Required property 'message' is missing"
        return typing.cast(typing.List["LexIntentFollowUpPromptPromptMessage"], result)

    @builtins.property
    def response_card(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#response_card LexIntent#response_card}.'''
        result = self._values.get("response_card")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LexIntentFollowUpPromptPrompt(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lex.LexIntentFollowUpPromptPromptMessage",
    jsii_struct_bases=[],
    name_mapping={
        "content": "content",
        "content_type": "contentType",
        "group_number": "groupNumber",
    },
)
class LexIntentFollowUpPromptPromptMessage:
    def __init__(
        self,
        *,
        content: builtins.str,
        content_type: builtins.str,
        group_number: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param content: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#content LexIntent#content}.
        :param content_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#content_type LexIntent#content_type}.
        :param group_number: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#group_number LexIntent#group_number}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "content": content,
            "content_type": content_type,
        }
        if group_number is not None:
            self._values["group_number"] = group_number

    @builtins.property
    def content(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#content LexIntent#content}.'''
        result = self._values.get("content")
        assert result is not None, "Required property 'content' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def content_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#content_type LexIntent#content_type}.'''
        result = self._values.get("content_type")
        assert result is not None, "Required property 'content_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def group_number(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#group_number LexIntent#group_number}.'''
        result = self._values.get("group_number")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LexIntentFollowUpPromptPromptMessage(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LexIntentFollowUpPromptPromptOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lex.LexIntentFollowUpPromptPromptOutputReference",
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

    @jsii.member(jsii_name="resetResponseCard")
    def reset_response_card(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResponseCard", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxAttemptsInput")
    def max_attempts_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxAttemptsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="messageInput")
    def message_input(
        self,
    ) -> typing.Optional[typing.List[LexIntentFollowUpPromptPromptMessage]]:
        return typing.cast(typing.Optional[typing.List[LexIntentFollowUpPromptPromptMessage]], jsii.get(self, "messageInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="responseCardInput")
    def response_card_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "responseCardInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxAttempts")
    def max_attempts(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxAttempts"))

    @max_attempts.setter
    def max_attempts(self, value: jsii.Number) -> None:
        jsii.set(self, "maxAttempts", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="message")
    def message(self) -> typing.List[LexIntentFollowUpPromptPromptMessage]:
        return typing.cast(typing.List[LexIntentFollowUpPromptPromptMessage], jsii.get(self, "message"))

    @message.setter
    def message(self, value: typing.List[LexIntentFollowUpPromptPromptMessage]) -> None:
        jsii.set(self, "message", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="responseCard")
    def response_card(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "responseCard"))

    @response_card.setter
    def response_card(self, value: builtins.str) -> None:
        jsii.set(self, "responseCard", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[LexIntentFollowUpPromptPrompt]:
        return typing.cast(typing.Optional[LexIntentFollowUpPromptPrompt], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[LexIntentFollowUpPromptPrompt],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lex.LexIntentFollowUpPromptRejectionStatement",
    jsii_struct_bases=[],
    name_mapping={"message": "message", "response_card": "responseCard"},
)
class LexIntentFollowUpPromptRejectionStatement:
    def __init__(
        self,
        *,
        message: typing.Sequence["LexIntentFollowUpPromptRejectionStatementMessage"],
        response_card: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param message: message block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#message LexIntent#message}
        :param response_card: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#response_card LexIntent#response_card}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "message": message,
        }
        if response_card is not None:
            self._values["response_card"] = response_card

    @builtins.property
    def message(
        self,
    ) -> typing.List["LexIntentFollowUpPromptRejectionStatementMessage"]:
        '''message block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#message LexIntent#message}
        '''
        result = self._values.get("message")
        assert result is not None, "Required property 'message' is missing"
        return typing.cast(typing.List["LexIntentFollowUpPromptRejectionStatementMessage"], result)

    @builtins.property
    def response_card(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#response_card LexIntent#response_card}.'''
        result = self._values.get("response_card")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LexIntentFollowUpPromptRejectionStatement(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lex.LexIntentFollowUpPromptRejectionStatementMessage",
    jsii_struct_bases=[],
    name_mapping={
        "content": "content",
        "content_type": "contentType",
        "group_number": "groupNumber",
    },
)
class LexIntentFollowUpPromptRejectionStatementMessage:
    def __init__(
        self,
        *,
        content: builtins.str,
        content_type: builtins.str,
        group_number: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param content: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#content LexIntent#content}.
        :param content_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#content_type LexIntent#content_type}.
        :param group_number: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#group_number LexIntent#group_number}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "content": content,
            "content_type": content_type,
        }
        if group_number is not None:
            self._values["group_number"] = group_number

    @builtins.property
    def content(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#content LexIntent#content}.'''
        result = self._values.get("content")
        assert result is not None, "Required property 'content' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def content_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#content_type LexIntent#content_type}.'''
        result = self._values.get("content_type")
        assert result is not None, "Required property 'content_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def group_number(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#group_number LexIntent#group_number}.'''
        result = self._values.get("group_number")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LexIntentFollowUpPromptRejectionStatementMessage(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LexIntentFollowUpPromptRejectionStatementOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lex.LexIntentFollowUpPromptRejectionStatementOutputReference",
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

    @jsii.member(jsii_name="resetResponseCard")
    def reset_response_card(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResponseCard", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="messageInput")
    def message_input(
        self,
    ) -> typing.Optional[typing.List[LexIntentFollowUpPromptRejectionStatementMessage]]:
        return typing.cast(typing.Optional[typing.List[LexIntentFollowUpPromptRejectionStatementMessage]], jsii.get(self, "messageInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="responseCardInput")
    def response_card_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "responseCardInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="message")
    def message(self) -> typing.List[LexIntentFollowUpPromptRejectionStatementMessage]:
        return typing.cast(typing.List[LexIntentFollowUpPromptRejectionStatementMessage], jsii.get(self, "message"))

    @message.setter
    def message(
        self,
        value: typing.List[LexIntentFollowUpPromptRejectionStatementMessage],
    ) -> None:
        jsii.set(self, "message", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="responseCard")
    def response_card(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "responseCard"))

    @response_card.setter
    def response_card(self, value: builtins.str) -> None:
        jsii.set(self, "responseCard", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[LexIntentFollowUpPromptRejectionStatement]:
        return typing.cast(typing.Optional[LexIntentFollowUpPromptRejectionStatement], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[LexIntentFollowUpPromptRejectionStatement],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lex.LexIntentFulfillmentActivity",
    jsii_struct_bases=[],
    name_mapping={"type": "type", "code_hook": "codeHook"},
)
class LexIntentFulfillmentActivity:
    def __init__(
        self,
        *,
        type: builtins.str,
        code_hook: typing.Optional["LexIntentFulfillmentActivityCodeHook"] = None,
    ) -> None:
        '''
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#type LexIntent#type}.
        :param code_hook: code_hook block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#code_hook LexIntent#code_hook}
        '''
        if isinstance(code_hook, dict):
            code_hook = LexIntentFulfillmentActivityCodeHook(**code_hook)
        self._values: typing.Dict[str, typing.Any] = {
            "type": type,
        }
        if code_hook is not None:
            self._values["code_hook"] = code_hook

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#type LexIntent#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def code_hook(self) -> typing.Optional["LexIntentFulfillmentActivityCodeHook"]:
        '''code_hook block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#code_hook LexIntent#code_hook}
        '''
        result = self._values.get("code_hook")
        return typing.cast(typing.Optional["LexIntentFulfillmentActivityCodeHook"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LexIntentFulfillmentActivity(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lex.LexIntentFulfillmentActivityCodeHook",
    jsii_struct_bases=[],
    name_mapping={"message_version": "messageVersion", "uri": "uri"},
)
class LexIntentFulfillmentActivityCodeHook:
    def __init__(self, *, message_version: builtins.str, uri: builtins.str) -> None:
        '''
        :param message_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#message_version LexIntent#message_version}.
        :param uri: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#uri LexIntent#uri}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "message_version": message_version,
            "uri": uri,
        }

    @builtins.property
    def message_version(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#message_version LexIntent#message_version}.'''
        result = self._values.get("message_version")
        assert result is not None, "Required property 'message_version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def uri(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#uri LexIntent#uri}.'''
        result = self._values.get("uri")
        assert result is not None, "Required property 'uri' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LexIntentFulfillmentActivityCodeHook(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LexIntentFulfillmentActivityCodeHookOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lex.LexIntentFulfillmentActivityCodeHookOutputReference",
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
    @jsii.member(jsii_name="messageVersionInput")
    def message_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "messageVersionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="uriInput")
    def uri_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "uriInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="messageVersion")
    def message_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "messageVersion"))

    @message_version.setter
    def message_version(self, value: builtins.str) -> None:
        jsii.set(self, "messageVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="uri")
    def uri(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uri"))

    @uri.setter
    def uri(self, value: builtins.str) -> None:
        jsii.set(self, "uri", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[LexIntentFulfillmentActivityCodeHook]:
        return typing.cast(typing.Optional[LexIntentFulfillmentActivityCodeHook], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[LexIntentFulfillmentActivityCodeHook],
    ) -> None:
        jsii.set(self, "internalValue", value)


class LexIntentFulfillmentActivityOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lex.LexIntentFulfillmentActivityOutputReference",
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

    @jsii.member(jsii_name="putCodeHook")
    def put_code_hook(
        self,
        *,
        message_version: builtins.str,
        uri: builtins.str,
    ) -> None:
        '''
        :param message_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#message_version LexIntent#message_version}.
        :param uri: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#uri LexIntent#uri}.
        '''
        value = LexIntentFulfillmentActivityCodeHook(
            message_version=message_version, uri=uri
        )

        return typing.cast(None, jsii.invoke(self, "putCodeHook", [value]))

    @jsii.member(jsii_name="resetCodeHook")
    def reset_code_hook(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCodeHook", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="codeHook")
    def code_hook(self) -> LexIntentFulfillmentActivityCodeHookOutputReference:
        return typing.cast(LexIntentFulfillmentActivityCodeHookOutputReference, jsii.get(self, "codeHook"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="codeHookInput")
    def code_hook_input(self) -> typing.Optional[LexIntentFulfillmentActivityCodeHook]:
        return typing.cast(typing.Optional[LexIntentFulfillmentActivityCodeHook], jsii.get(self, "codeHookInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        jsii.set(self, "type", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[LexIntentFulfillmentActivity]:
        return typing.cast(typing.Optional[LexIntentFulfillmentActivity], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[LexIntentFulfillmentActivity],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lex.LexIntentRejectionStatement",
    jsii_struct_bases=[],
    name_mapping={"message": "message", "response_card": "responseCard"},
)
class LexIntentRejectionStatement:
    def __init__(
        self,
        *,
        message: typing.Sequence["LexIntentRejectionStatementMessage"],
        response_card: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param message: message block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#message LexIntent#message}
        :param response_card: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#response_card LexIntent#response_card}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "message": message,
        }
        if response_card is not None:
            self._values["response_card"] = response_card

    @builtins.property
    def message(self) -> typing.List["LexIntentRejectionStatementMessage"]:
        '''message block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#message LexIntent#message}
        '''
        result = self._values.get("message")
        assert result is not None, "Required property 'message' is missing"
        return typing.cast(typing.List["LexIntentRejectionStatementMessage"], result)

    @builtins.property
    def response_card(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#response_card LexIntent#response_card}.'''
        result = self._values.get("response_card")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LexIntentRejectionStatement(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lex.LexIntentRejectionStatementMessage",
    jsii_struct_bases=[],
    name_mapping={
        "content": "content",
        "content_type": "contentType",
        "group_number": "groupNumber",
    },
)
class LexIntentRejectionStatementMessage:
    def __init__(
        self,
        *,
        content: builtins.str,
        content_type: builtins.str,
        group_number: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param content: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#content LexIntent#content}.
        :param content_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#content_type LexIntent#content_type}.
        :param group_number: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#group_number LexIntent#group_number}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "content": content,
            "content_type": content_type,
        }
        if group_number is not None:
            self._values["group_number"] = group_number

    @builtins.property
    def content(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#content LexIntent#content}.'''
        result = self._values.get("content")
        assert result is not None, "Required property 'content' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def content_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#content_type LexIntent#content_type}.'''
        result = self._values.get("content_type")
        assert result is not None, "Required property 'content_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def group_number(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#group_number LexIntent#group_number}.'''
        result = self._values.get("group_number")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LexIntentRejectionStatementMessage(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LexIntentRejectionStatementOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lex.LexIntentRejectionStatementOutputReference",
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

    @jsii.member(jsii_name="resetResponseCard")
    def reset_response_card(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResponseCard", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="messageInput")
    def message_input(
        self,
    ) -> typing.Optional[typing.List[LexIntentRejectionStatementMessage]]:
        return typing.cast(typing.Optional[typing.List[LexIntentRejectionStatementMessage]], jsii.get(self, "messageInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="responseCardInput")
    def response_card_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "responseCardInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="message")
    def message(self) -> typing.List[LexIntentRejectionStatementMessage]:
        return typing.cast(typing.List[LexIntentRejectionStatementMessage], jsii.get(self, "message"))

    @message.setter
    def message(self, value: typing.List[LexIntentRejectionStatementMessage]) -> None:
        jsii.set(self, "message", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="responseCard")
    def response_card(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "responseCard"))

    @response_card.setter
    def response_card(self, value: builtins.str) -> None:
        jsii.set(self, "responseCard", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[LexIntentRejectionStatement]:
        return typing.cast(typing.Optional[LexIntentRejectionStatement], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[LexIntentRejectionStatement],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lex.LexIntentSlot",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "slot_constraint": "slotConstraint",
        "slot_type": "slotType",
        "description": "description",
        "priority": "priority",
        "response_card": "responseCard",
        "sample_utterances": "sampleUtterances",
        "slot_type_version": "slotTypeVersion",
        "value_elicitation_prompt": "valueElicitationPrompt",
    },
)
class LexIntentSlot:
    def __init__(
        self,
        *,
        name: builtins.str,
        slot_constraint: builtins.str,
        slot_type: builtins.str,
        description: typing.Optional[builtins.str] = None,
        priority: typing.Optional[jsii.Number] = None,
        response_card: typing.Optional[builtins.str] = None,
        sample_utterances: typing.Optional[typing.Sequence[builtins.str]] = None,
        slot_type_version: typing.Optional[builtins.str] = None,
        value_elicitation_prompt: typing.Optional["LexIntentSlotValueElicitationPrompt"] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#name LexIntent#name}.
        :param slot_constraint: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#slot_constraint LexIntent#slot_constraint}.
        :param slot_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#slot_type LexIntent#slot_type}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#description LexIntent#description}.
        :param priority: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#priority LexIntent#priority}.
        :param response_card: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#response_card LexIntent#response_card}.
        :param sample_utterances: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#sample_utterances LexIntent#sample_utterances}.
        :param slot_type_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#slot_type_version LexIntent#slot_type_version}.
        :param value_elicitation_prompt: value_elicitation_prompt block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#value_elicitation_prompt LexIntent#value_elicitation_prompt}
        '''
        if isinstance(value_elicitation_prompt, dict):
            value_elicitation_prompt = LexIntentSlotValueElicitationPrompt(**value_elicitation_prompt)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "slot_constraint": slot_constraint,
            "slot_type": slot_type,
        }
        if description is not None:
            self._values["description"] = description
        if priority is not None:
            self._values["priority"] = priority
        if response_card is not None:
            self._values["response_card"] = response_card
        if sample_utterances is not None:
            self._values["sample_utterances"] = sample_utterances
        if slot_type_version is not None:
            self._values["slot_type_version"] = slot_type_version
        if value_elicitation_prompt is not None:
            self._values["value_elicitation_prompt"] = value_elicitation_prompt

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#name LexIntent#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def slot_constraint(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#slot_constraint LexIntent#slot_constraint}.'''
        result = self._values.get("slot_constraint")
        assert result is not None, "Required property 'slot_constraint' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def slot_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#slot_type LexIntent#slot_type}.'''
        result = self._values.get("slot_type")
        assert result is not None, "Required property 'slot_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#description LexIntent#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def priority(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#priority LexIntent#priority}.'''
        result = self._values.get("priority")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def response_card(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#response_card LexIntent#response_card}.'''
        result = self._values.get("response_card")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sample_utterances(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#sample_utterances LexIntent#sample_utterances}.'''
        result = self._values.get("sample_utterances")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def slot_type_version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#slot_type_version LexIntent#slot_type_version}.'''
        result = self._values.get("slot_type_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def value_elicitation_prompt(
        self,
    ) -> typing.Optional["LexIntentSlotValueElicitationPrompt"]:
        '''value_elicitation_prompt block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#value_elicitation_prompt LexIntent#value_elicitation_prompt}
        '''
        result = self._values.get("value_elicitation_prompt")
        return typing.cast(typing.Optional["LexIntentSlotValueElicitationPrompt"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LexIntentSlot(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lex.LexIntentSlotValueElicitationPrompt",
    jsii_struct_bases=[],
    name_mapping={
        "max_attempts": "maxAttempts",
        "message": "message",
        "response_card": "responseCard",
    },
)
class LexIntentSlotValueElicitationPrompt:
    def __init__(
        self,
        *,
        max_attempts: jsii.Number,
        message: typing.Sequence["LexIntentSlotValueElicitationPromptMessage"],
        response_card: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param max_attempts: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#max_attempts LexIntent#max_attempts}.
        :param message: message block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#message LexIntent#message}
        :param response_card: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#response_card LexIntent#response_card}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "max_attempts": max_attempts,
            "message": message,
        }
        if response_card is not None:
            self._values["response_card"] = response_card

    @builtins.property
    def max_attempts(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#max_attempts LexIntent#max_attempts}.'''
        result = self._values.get("max_attempts")
        assert result is not None, "Required property 'max_attempts' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def message(self) -> typing.List["LexIntentSlotValueElicitationPromptMessage"]:
        '''message block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#message LexIntent#message}
        '''
        result = self._values.get("message")
        assert result is not None, "Required property 'message' is missing"
        return typing.cast(typing.List["LexIntentSlotValueElicitationPromptMessage"], result)

    @builtins.property
    def response_card(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#response_card LexIntent#response_card}.'''
        result = self._values.get("response_card")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LexIntentSlotValueElicitationPrompt(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lex.LexIntentSlotValueElicitationPromptMessage",
    jsii_struct_bases=[],
    name_mapping={
        "content": "content",
        "content_type": "contentType",
        "group_number": "groupNumber",
    },
)
class LexIntentSlotValueElicitationPromptMessage:
    def __init__(
        self,
        *,
        content: builtins.str,
        content_type: builtins.str,
        group_number: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param content: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#content LexIntent#content}.
        :param content_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#content_type LexIntent#content_type}.
        :param group_number: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#group_number LexIntent#group_number}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "content": content,
            "content_type": content_type,
        }
        if group_number is not None:
            self._values["group_number"] = group_number

    @builtins.property
    def content(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#content LexIntent#content}.'''
        result = self._values.get("content")
        assert result is not None, "Required property 'content' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def content_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#content_type LexIntent#content_type}.'''
        result = self._values.get("content_type")
        assert result is not None, "Required property 'content_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def group_number(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#group_number LexIntent#group_number}.'''
        result = self._values.get("group_number")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LexIntentSlotValueElicitationPromptMessage(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LexIntentSlotValueElicitationPromptOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lex.LexIntentSlotValueElicitationPromptOutputReference",
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

    @jsii.member(jsii_name="resetResponseCard")
    def reset_response_card(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResponseCard", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxAttemptsInput")
    def max_attempts_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxAttemptsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="messageInput")
    def message_input(
        self,
    ) -> typing.Optional[typing.List[LexIntentSlotValueElicitationPromptMessage]]:
        return typing.cast(typing.Optional[typing.List[LexIntentSlotValueElicitationPromptMessage]], jsii.get(self, "messageInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="responseCardInput")
    def response_card_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "responseCardInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxAttempts")
    def max_attempts(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxAttempts"))

    @max_attempts.setter
    def max_attempts(self, value: jsii.Number) -> None:
        jsii.set(self, "maxAttempts", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="message")
    def message(self) -> typing.List[LexIntentSlotValueElicitationPromptMessage]:
        return typing.cast(typing.List[LexIntentSlotValueElicitationPromptMessage], jsii.get(self, "message"))

    @message.setter
    def message(
        self,
        value: typing.List[LexIntentSlotValueElicitationPromptMessage],
    ) -> None:
        jsii.set(self, "message", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="responseCard")
    def response_card(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "responseCard"))

    @response_card.setter
    def response_card(self, value: builtins.str) -> None:
        jsii.set(self, "responseCard", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[LexIntentSlotValueElicitationPrompt]:
        return typing.cast(typing.Optional[LexIntentSlotValueElicitationPrompt], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[LexIntentSlotValueElicitationPrompt],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lex.LexIntentTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete", "update": "update"},
)
class LexIntentTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#create LexIntent#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#delete LexIntent#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#update LexIntent#update}.
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#create LexIntent#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#delete LexIntent#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_intent#update LexIntent#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LexIntentTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LexIntentTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lex.LexIntentTimeoutsOutputReference",
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
    def internal_value(self) -> typing.Optional[LexIntentTimeouts]:
        return typing.cast(typing.Optional[LexIntentTimeouts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[LexIntentTimeouts]) -> None:
        jsii.set(self, "internalValue", value)


class LexSlotType(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lex.LexSlotType",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/lex_slot_type aws_lex_slot_type}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        enumeration_value: typing.Sequence["LexSlotTypeEnumerationValue"],
        name: builtins.str,
        create_version: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        description: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional["LexSlotTypeTimeouts"] = None,
        value_selection_strategy: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/lex_slot_type aws_lex_slot_type} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param enumeration_value: enumeration_value block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_slot_type#enumeration_value LexSlotType#enumeration_value}
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_slot_type#name LexSlotType#name}.
        :param create_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_slot_type#create_version LexSlotType#create_version}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_slot_type#description LexSlotType#description}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_slot_type#timeouts LexSlotType#timeouts}
        :param value_selection_strategy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_slot_type#value_selection_strategy LexSlotType#value_selection_strategy}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = LexSlotTypeConfig(
            enumeration_value=enumeration_value,
            name=name,
            create_version=create_version,
            description=description,
            timeouts=timeouts,
            value_selection_strategy=value_selection_strategy,
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
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_slot_type#create LexSlotType#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_slot_type#delete LexSlotType#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_slot_type#update LexSlotType#update}.
        '''
        value = LexSlotTypeTimeouts(create=create, delete=delete, update=update)

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetCreateVersion")
    def reset_create_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreateVersion", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetTimeouts")
    def reset_timeouts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeouts", []))

    @jsii.member(jsii_name="resetValueSelectionStrategy")
    def reset_value_selection_strategy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValueSelectionStrategy", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="checksum")
    def checksum(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "checksum"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createdDate")
    def created_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdDate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lastUpdatedDate")
    def last_updated_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lastUpdatedDate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "LexSlotTypeTimeoutsOutputReference":
        return typing.cast("LexSlotTypeTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createVersionInput")
    def create_version_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "createVersionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enumerationValueInput")
    def enumeration_value_input(
        self,
    ) -> typing.Optional[typing.List["LexSlotTypeEnumerationValue"]]:
        return typing.cast(typing.Optional[typing.List["LexSlotTypeEnumerationValue"]], jsii.get(self, "enumerationValueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(self) -> typing.Optional["LexSlotTypeTimeouts"]:
        return typing.cast(typing.Optional["LexSlotTypeTimeouts"], jsii.get(self, "timeoutsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="valueSelectionStrategyInput")
    def value_selection_strategy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "valueSelectionStrategyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createVersion")
    def create_version(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "createVersion"))

    @create_version.setter
    def create_version(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "createVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enumerationValue")
    def enumeration_value(self) -> typing.List["LexSlotTypeEnumerationValue"]:
        return typing.cast(typing.List["LexSlotTypeEnumerationValue"], jsii.get(self, "enumerationValue"))

    @enumeration_value.setter
    def enumeration_value(
        self,
        value: typing.List["LexSlotTypeEnumerationValue"],
    ) -> None:
        jsii.set(self, "enumerationValue", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="valueSelectionStrategy")
    def value_selection_strategy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "valueSelectionStrategy"))

    @value_selection_strategy.setter
    def value_selection_strategy(self, value: builtins.str) -> None:
        jsii.set(self, "valueSelectionStrategy", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lex.LexSlotTypeConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "enumeration_value": "enumerationValue",
        "name": "name",
        "create_version": "createVersion",
        "description": "description",
        "timeouts": "timeouts",
        "value_selection_strategy": "valueSelectionStrategy",
    },
)
class LexSlotTypeConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        enumeration_value: typing.Sequence["LexSlotTypeEnumerationValue"],
        name: builtins.str,
        create_version: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        description: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional["LexSlotTypeTimeouts"] = None,
        value_selection_strategy: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Lex.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param enumeration_value: enumeration_value block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_slot_type#enumeration_value LexSlotType#enumeration_value}
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_slot_type#name LexSlotType#name}.
        :param create_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_slot_type#create_version LexSlotType#create_version}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_slot_type#description LexSlotType#description}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_slot_type#timeouts LexSlotType#timeouts}
        :param value_selection_strategy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_slot_type#value_selection_strategy LexSlotType#value_selection_strategy}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(timeouts, dict):
            timeouts = LexSlotTypeTimeouts(**timeouts)
        self._values: typing.Dict[str, typing.Any] = {
            "enumeration_value": enumeration_value,
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
        if create_version is not None:
            self._values["create_version"] = create_version
        if description is not None:
            self._values["description"] = description
        if timeouts is not None:
            self._values["timeouts"] = timeouts
        if value_selection_strategy is not None:
            self._values["value_selection_strategy"] = value_selection_strategy

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
    def enumeration_value(self) -> typing.List["LexSlotTypeEnumerationValue"]:
        '''enumeration_value block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_slot_type#enumeration_value LexSlotType#enumeration_value}
        '''
        result = self._values.get("enumeration_value")
        assert result is not None, "Required property 'enumeration_value' is missing"
        return typing.cast(typing.List["LexSlotTypeEnumerationValue"], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_slot_type#name LexSlotType#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def create_version(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_slot_type#create_version LexSlotType#create_version}.'''
        result = self._values.get("create_version")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_slot_type#description LexSlotType#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["LexSlotTypeTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_slot_type#timeouts LexSlotType#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["LexSlotTypeTimeouts"], result)

    @builtins.property
    def value_selection_strategy(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_slot_type#value_selection_strategy LexSlotType#value_selection_strategy}.'''
        result = self._values.get("value_selection_strategy")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LexSlotTypeConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lex.LexSlotTypeEnumerationValue",
    jsii_struct_bases=[],
    name_mapping={"value": "value", "synonyms": "synonyms"},
)
class LexSlotTypeEnumerationValue:
    def __init__(
        self,
        *,
        value: builtins.str,
        synonyms: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_slot_type#value LexSlotType#value}.
        :param synonyms: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_slot_type#synonyms LexSlotType#synonyms}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "value": value,
        }
        if synonyms is not None:
            self._values["synonyms"] = synonyms

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_slot_type#value LexSlotType#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def synonyms(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_slot_type#synonyms LexSlotType#synonyms}.'''
        result = self._values.get("synonyms")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LexSlotTypeEnumerationValue(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lex.LexSlotTypeTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete", "update": "update"},
)
class LexSlotTypeTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_slot_type#create LexSlotType#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_slot_type#delete LexSlotType#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_slot_type#update LexSlotType#update}.
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_slot_type#create LexSlotType#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_slot_type#delete LexSlotType#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lex_slot_type#update LexSlotType#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LexSlotTypeTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LexSlotTypeTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lex.LexSlotTypeTimeoutsOutputReference",
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
    def internal_value(self) -> typing.Optional[LexSlotTypeTimeouts]:
        return typing.cast(typing.Optional[LexSlotTypeTimeouts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[LexSlotTypeTimeouts]) -> None:
        jsii.set(self, "internalValue", value)


__all__ = [
    "DataAwsLexBot",
    "DataAwsLexBotAlias",
    "DataAwsLexBotAliasConfig",
    "DataAwsLexBotConfig",
    "DataAwsLexIntent",
    "DataAwsLexIntentConfig",
    "DataAwsLexSlotType",
    "DataAwsLexSlotTypeConfig",
    "DataAwsLexSlotTypeEnumerationValue",
    "LexBot",
    "LexBotAbortStatement",
    "LexBotAbortStatementMessage",
    "LexBotAbortStatementOutputReference",
    "LexBotAlias",
    "LexBotAliasConfig",
    "LexBotAliasConversationLogs",
    "LexBotAliasConversationLogsLogSettings",
    "LexBotAliasConversationLogsOutputReference",
    "LexBotAliasTimeouts",
    "LexBotAliasTimeoutsOutputReference",
    "LexBotClarificationPrompt",
    "LexBotClarificationPromptMessage",
    "LexBotClarificationPromptOutputReference",
    "LexBotConfig",
    "LexBotIntent",
    "LexBotTimeouts",
    "LexBotTimeoutsOutputReference",
    "LexIntent",
    "LexIntentConclusionStatement",
    "LexIntentConclusionStatementMessage",
    "LexIntentConclusionStatementOutputReference",
    "LexIntentConfig",
    "LexIntentConfirmationPrompt",
    "LexIntentConfirmationPromptMessage",
    "LexIntentConfirmationPromptOutputReference",
    "LexIntentDialogCodeHook",
    "LexIntentDialogCodeHookOutputReference",
    "LexIntentFollowUpPrompt",
    "LexIntentFollowUpPromptOutputReference",
    "LexIntentFollowUpPromptPrompt",
    "LexIntentFollowUpPromptPromptMessage",
    "LexIntentFollowUpPromptPromptOutputReference",
    "LexIntentFollowUpPromptRejectionStatement",
    "LexIntentFollowUpPromptRejectionStatementMessage",
    "LexIntentFollowUpPromptRejectionStatementOutputReference",
    "LexIntentFulfillmentActivity",
    "LexIntentFulfillmentActivityCodeHook",
    "LexIntentFulfillmentActivityCodeHookOutputReference",
    "LexIntentFulfillmentActivityOutputReference",
    "LexIntentRejectionStatement",
    "LexIntentRejectionStatementMessage",
    "LexIntentRejectionStatementOutputReference",
    "LexIntentSlot",
    "LexIntentSlotValueElicitationPrompt",
    "LexIntentSlotValueElicitationPromptMessage",
    "LexIntentSlotValueElicitationPromptOutputReference",
    "LexIntentTimeouts",
    "LexIntentTimeoutsOutputReference",
    "LexSlotType",
    "LexSlotTypeConfig",
    "LexSlotTypeEnumerationValue",
    "LexSlotTypeTimeouts",
    "LexSlotTypeTimeoutsOutputReference",
]

publication.publish()
