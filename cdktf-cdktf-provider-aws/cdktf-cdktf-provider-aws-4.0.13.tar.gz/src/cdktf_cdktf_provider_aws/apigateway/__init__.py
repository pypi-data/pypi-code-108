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


class ApiGatewayAccount(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.apigateway.ApiGatewayAccount",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_account aws_api_gateway_account}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        cloudwatch_role_arn: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_account aws_api_gateway_account} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param cloudwatch_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_account#cloudwatch_role_arn ApiGatewayAccount#cloudwatch_role_arn}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ApiGatewayAccountConfig(
            cloudwatch_role_arn=cloudwatch_role_arn,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetCloudwatchRoleArn")
    def reset_cloudwatch_role_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCloudwatchRoleArn", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.member(jsii_name="throttleSettings")
    def throttle_settings(
        self,
        index: builtins.str,
    ) -> "ApiGatewayAccountThrottleSettings":
        '''
        :param index: -
        '''
        return typing.cast("ApiGatewayAccountThrottleSettings", jsii.invoke(self, "throttleSettings", [index]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cloudwatchRoleArnInput")
    def cloudwatch_role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cloudwatchRoleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cloudwatchRoleArn")
    def cloudwatch_role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cloudwatchRoleArn"))

    @cloudwatch_role_arn.setter
    def cloudwatch_role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "cloudwatchRoleArn", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.apigateway.ApiGatewayAccountConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "cloudwatch_role_arn": "cloudwatchRoleArn",
    },
)
class ApiGatewayAccountConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        cloudwatch_role_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''API Gateway.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param cloudwatch_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_account#cloudwatch_role_arn ApiGatewayAccount#cloudwatch_role_arn}.
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
        if cloudwatch_role_arn is not None:
            self._values["cloudwatch_role_arn"] = cloudwatch_role_arn

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
    def cloudwatch_role_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_account#cloudwatch_role_arn ApiGatewayAccount#cloudwatch_role_arn}.'''
        result = self._values.get("cloudwatch_role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApiGatewayAccountConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ApiGatewayAccountThrottleSettings(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.apigateway.ApiGatewayAccountThrottleSettings",
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
    @jsii.member(jsii_name="burstLimit")
    def burst_limit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "burstLimit"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rateLimit")
    def rate_limit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "rateLimit"))


class ApiGatewayApiKey(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.apigateway.ApiGatewayApiKey",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_api_key aws_api_gateway_api_key}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        value: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_api_key aws_api_gateway_api_key} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_api_key#name ApiGatewayApiKey#name}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_api_key#description ApiGatewayApiKey#description}.
        :param enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_api_key#enabled ApiGatewayApiKey#enabled}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_api_key#tags ApiGatewayApiKey#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_api_key#tags_all ApiGatewayApiKey#tags_all}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_api_key#value ApiGatewayApiKey#value}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ApiGatewayApiKeyConfig(
            name=name,
            description=description,
            enabled=enabled,
            tags=tags,
            tags_all=tags_all,
            value=value,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetValue")
    def reset_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValue", []))

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
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enabledInput"))

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
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "valueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "enabled", value)

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

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        jsii.set(self, "value", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.apigateway.ApiGatewayApiKeyConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "description": "description",
        "enabled": "enabled",
        "tags": "tags",
        "tags_all": "tagsAll",
        "value": "value",
    },
)
class ApiGatewayApiKeyConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''API Gateway.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_api_key#name ApiGatewayApiKey#name}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_api_key#description ApiGatewayApiKey#description}.
        :param enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_api_key#enabled ApiGatewayApiKey#enabled}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_api_key#tags ApiGatewayApiKey#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_api_key#tags_all ApiGatewayApiKey#tags_all}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_api_key#value ApiGatewayApiKey#value}.
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
        if description is not None:
            self._values["description"] = description
        if enabled is not None:
            self._values["enabled"] = enabled
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if value is not None:
            self._values["value"] = value

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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_api_key#name ApiGatewayApiKey#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_api_key#description ApiGatewayApiKey#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_api_key#enabled ApiGatewayApiKey#enabled}.'''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_api_key#tags ApiGatewayApiKey#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_api_key#tags_all ApiGatewayApiKey#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_api_key#value ApiGatewayApiKey#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApiGatewayApiKeyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ApiGatewayAuthorizer(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.apigateway.ApiGatewayAuthorizer",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_authorizer aws_api_gateway_authorizer}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        rest_api_id: builtins.str,
        authorizer_credentials: typing.Optional[builtins.str] = None,
        authorizer_result_ttl_in_seconds: typing.Optional[jsii.Number] = None,
        authorizer_uri: typing.Optional[builtins.str] = None,
        identity_source: typing.Optional[builtins.str] = None,
        identity_validation_expression: typing.Optional[builtins.str] = None,
        provider_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        type: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_authorizer aws_api_gateway_authorizer} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_authorizer#name ApiGatewayAuthorizer#name}.
        :param rest_api_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_authorizer#rest_api_id ApiGatewayAuthorizer#rest_api_id}.
        :param authorizer_credentials: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_authorizer#authorizer_credentials ApiGatewayAuthorizer#authorizer_credentials}.
        :param authorizer_result_ttl_in_seconds: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_authorizer#authorizer_result_ttl_in_seconds ApiGatewayAuthorizer#authorizer_result_ttl_in_seconds}.
        :param authorizer_uri: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_authorizer#authorizer_uri ApiGatewayAuthorizer#authorizer_uri}.
        :param identity_source: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_authorizer#identity_source ApiGatewayAuthorizer#identity_source}.
        :param identity_validation_expression: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_authorizer#identity_validation_expression ApiGatewayAuthorizer#identity_validation_expression}.
        :param provider_arns: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_authorizer#provider_arns ApiGatewayAuthorizer#provider_arns}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_authorizer#type ApiGatewayAuthorizer#type}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ApiGatewayAuthorizerConfig(
            name=name,
            rest_api_id=rest_api_id,
            authorizer_credentials=authorizer_credentials,
            authorizer_result_ttl_in_seconds=authorizer_result_ttl_in_seconds,
            authorizer_uri=authorizer_uri,
            identity_source=identity_source,
            identity_validation_expression=identity_validation_expression,
            provider_arns=provider_arns,
            type=type,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetAuthorizerCredentials")
    def reset_authorizer_credentials(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthorizerCredentials", []))

    @jsii.member(jsii_name="resetAuthorizerResultTtlInSeconds")
    def reset_authorizer_result_ttl_in_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthorizerResultTtlInSeconds", []))

    @jsii.member(jsii_name="resetAuthorizerUri")
    def reset_authorizer_uri(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthorizerUri", []))

    @jsii.member(jsii_name="resetIdentitySource")
    def reset_identity_source(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIdentitySource", []))

    @jsii.member(jsii_name="resetIdentityValidationExpression")
    def reset_identity_validation_expression(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIdentityValidationExpression", []))

    @jsii.member(jsii_name="resetProviderArns")
    def reset_provider_arns(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProviderArns", []))

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
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authorizerCredentialsInput")
    def authorizer_credentials_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "authorizerCredentialsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authorizerResultTtlInSecondsInput")
    def authorizer_result_ttl_in_seconds_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "authorizerResultTtlInSecondsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authorizerUriInput")
    def authorizer_uri_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "authorizerUriInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identitySourceInput")
    def identity_source_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "identitySourceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identityValidationExpressionInput")
    def identity_validation_expression_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "identityValidationExpressionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="providerArnsInput")
    def provider_arns_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "providerArnsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restApiIdInput")
    def rest_api_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "restApiIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authorizerCredentials")
    def authorizer_credentials(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authorizerCredentials"))

    @authorizer_credentials.setter
    def authorizer_credentials(self, value: builtins.str) -> None:
        jsii.set(self, "authorizerCredentials", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authorizerResultTtlInSeconds")
    def authorizer_result_ttl_in_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "authorizerResultTtlInSeconds"))

    @authorizer_result_ttl_in_seconds.setter
    def authorizer_result_ttl_in_seconds(self, value: jsii.Number) -> None:
        jsii.set(self, "authorizerResultTtlInSeconds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authorizerUri")
    def authorizer_uri(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authorizerUri"))

    @authorizer_uri.setter
    def authorizer_uri(self, value: builtins.str) -> None:
        jsii.set(self, "authorizerUri", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identitySource")
    def identity_source(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identitySource"))

    @identity_source.setter
    def identity_source(self, value: builtins.str) -> None:
        jsii.set(self, "identitySource", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identityValidationExpression")
    def identity_validation_expression(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityValidationExpression"))

    @identity_validation_expression.setter
    def identity_validation_expression(self, value: builtins.str) -> None:
        jsii.set(self, "identityValidationExpression", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="providerArns")
    def provider_arns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "providerArns"))

    @provider_arns.setter
    def provider_arns(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "providerArns", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restApiId")
    def rest_api_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "restApiId"))

    @rest_api_id.setter
    def rest_api_id(self, value: builtins.str) -> None:
        jsii.set(self, "restApiId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        jsii.set(self, "type", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.apigateway.ApiGatewayAuthorizerConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "rest_api_id": "restApiId",
        "authorizer_credentials": "authorizerCredentials",
        "authorizer_result_ttl_in_seconds": "authorizerResultTtlInSeconds",
        "authorizer_uri": "authorizerUri",
        "identity_source": "identitySource",
        "identity_validation_expression": "identityValidationExpression",
        "provider_arns": "providerArns",
        "type": "type",
    },
)
class ApiGatewayAuthorizerConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        rest_api_id: builtins.str,
        authorizer_credentials: typing.Optional[builtins.str] = None,
        authorizer_result_ttl_in_seconds: typing.Optional[jsii.Number] = None,
        authorizer_uri: typing.Optional[builtins.str] = None,
        identity_source: typing.Optional[builtins.str] = None,
        identity_validation_expression: typing.Optional[builtins.str] = None,
        provider_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''API Gateway.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_authorizer#name ApiGatewayAuthorizer#name}.
        :param rest_api_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_authorizer#rest_api_id ApiGatewayAuthorizer#rest_api_id}.
        :param authorizer_credentials: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_authorizer#authorizer_credentials ApiGatewayAuthorizer#authorizer_credentials}.
        :param authorizer_result_ttl_in_seconds: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_authorizer#authorizer_result_ttl_in_seconds ApiGatewayAuthorizer#authorizer_result_ttl_in_seconds}.
        :param authorizer_uri: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_authorizer#authorizer_uri ApiGatewayAuthorizer#authorizer_uri}.
        :param identity_source: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_authorizer#identity_source ApiGatewayAuthorizer#identity_source}.
        :param identity_validation_expression: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_authorizer#identity_validation_expression ApiGatewayAuthorizer#identity_validation_expression}.
        :param provider_arns: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_authorizer#provider_arns ApiGatewayAuthorizer#provider_arns}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_authorizer#type ApiGatewayAuthorizer#type}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "rest_api_id": rest_api_id,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if authorizer_credentials is not None:
            self._values["authorizer_credentials"] = authorizer_credentials
        if authorizer_result_ttl_in_seconds is not None:
            self._values["authorizer_result_ttl_in_seconds"] = authorizer_result_ttl_in_seconds
        if authorizer_uri is not None:
            self._values["authorizer_uri"] = authorizer_uri
        if identity_source is not None:
            self._values["identity_source"] = identity_source
        if identity_validation_expression is not None:
            self._values["identity_validation_expression"] = identity_validation_expression
        if provider_arns is not None:
            self._values["provider_arns"] = provider_arns
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
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_authorizer#name ApiGatewayAuthorizer#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def rest_api_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_authorizer#rest_api_id ApiGatewayAuthorizer#rest_api_id}.'''
        result = self._values.get("rest_api_id")
        assert result is not None, "Required property 'rest_api_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def authorizer_credentials(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_authorizer#authorizer_credentials ApiGatewayAuthorizer#authorizer_credentials}.'''
        result = self._values.get("authorizer_credentials")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def authorizer_result_ttl_in_seconds(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_authorizer#authorizer_result_ttl_in_seconds ApiGatewayAuthorizer#authorizer_result_ttl_in_seconds}.'''
        result = self._values.get("authorizer_result_ttl_in_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def authorizer_uri(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_authorizer#authorizer_uri ApiGatewayAuthorizer#authorizer_uri}.'''
        result = self._values.get("authorizer_uri")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def identity_source(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_authorizer#identity_source ApiGatewayAuthorizer#identity_source}.'''
        result = self._values.get("identity_source")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def identity_validation_expression(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_authorizer#identity_validation_expression ApiGatewayAuthorizer#identity_validation_expression}.'''
        result = self._values.get("identity_validation_expression")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def provider_arns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_authorizer#provider_arns ApiGatewayAuthorizer#provider_arns}.'''
        result = self._values.get("provider_arns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_authorizer#type ApiGatewayAuthorizer#type}.'''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApiGatewayAuthorizerConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ApiGatewayBasePathMapping(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.apigateway.ApiGatewayBasePathMapping",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_base_path_mapping aws_api_gateway_base_path_mapping}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        api_id: builtins.str,
        domain_name: builtins.str,
        base_path: typing.Optional[builtins.str] = None,
        stage_name: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_base_path_mapping aws_api_gateway_base_path_mapping} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param api_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_base_path_mapping#api_id ApiGatewayBasePathMapping#api_id}.
        :param domain_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_base_path_mapping#domain_name ApiGatewayBasePathMapping#domain_name}.
        :param base_path: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_base_path_mapping#base_path ApiGatewayBasePathMapping#base_path}.
        :param stage_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_base_path_mapping#stage_name ApiGatewayBasePathMapping#stage_name}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ApiGatewayBasePathMappingConfig(
            api_id=api_id,
            domain_name=domain_name,
            base_path=base_path,
            stage_name=stage_name,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetBasePath")
    def reset_base_path(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBasePath", []))

    @jsii.member(jsii_name="resetStageName")
    def reset_stage_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStageName", []))

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
    @jsii.member(jsii_name="apiIdInput")
    def api_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "apiIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="basePathInput")
    def base_path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "basePathInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainNameInput")
    def domain_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "domainNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stageNameInput")
    def stage_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stageNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiId")
    def api_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "apiId"))

    @api_id.setter
    def api_id(self, value: builtins.str) -> None:
        jsii.set(self, "apiId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="basePath")
    def base_path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "basePath"))

    @base_path.setter
    def base_path(self, value: builtins.str) -> None:
        jsii.set(self, "basePath", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainName")
    def domain_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "domainName"))

    @domain_name.setter
    def domain_name(self, value: builtins.str) -> None:
        jsii.set(self, "domainName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stageName")
    def stage_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "stageName"))

    @stage_name.setter
    def stage_name(self, value: builtins.str) -> None:
        jsii.set(self, "stageName", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.apigateway.ApiGatewayBasePathMappingConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "api_id": "apiId",
        "domain_name": "domainName",
        "base_path": "basePath",
        "stage_name": "stageName",
    },
)
class ApiGatewayBasePathMappingConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        api_id: builtins.str,
        domain_name: builtins.str,
        base_path: typing.Optional[builtins.str] = None,
        stage_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''API Gateway.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param api_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_base_path_mapping#api_id ApiGatewayBasePathMapping#api_id}.
        :param domain_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_base_path_mapping#domain_name ApiGatewayBasePathMapping#domain_name}.
        :param base_path: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_base_path_mapping#base_path ApiGatewayBasePathMapping#base_path}.
        :param stage_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_base_path_mapping#stage_name ApiGatewayBasePathMapping#stage_name}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "api_id": api_id,
            "domain_name": domain_name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if base_path is not None:
            self._values["base_path"] = base_path
        if stage_name is not None:
            self._values["stage_name"] = stage_name

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
    def api_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_base_path_mapping#api_id ApiGatewayBasePathMapping#api_id}.'''
        result = self._values.get("api_id")
        assert result is not None, "Required property 'api_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def domain_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_base_path_mapping#domain_name ApiGatewayBasePathMapping#domain_name}.'''
        result = self._values.get("domain_name")
        assert result is not None, "Required property 'domain_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def base_path(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_base_path_mapping#base_path ApiGatewayBasePathMapping#base_path}.'''
        result = self._values.get("base_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def stage_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_base_path_mapping#stage_name ApiGatewayBasePathMapping#stage_name}.'''
        result = self._values.get("stage_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApiGatewayBasePathMappingConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ApiGatewayClientCertificate(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.apigateway.ApiGatewayClientCertificate",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_client_certificate aws_api_gateway_client_certificate}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_client_certificate aws_api_gateway_client_certificate} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_client_certificate#description ApiGatewayClientCertificate#description}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_client_certificate#tags ApiGatewayClientCertificate#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_client_certificate#tags_all ApiGatewayClientCertificate#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ApiGatewayClientCertificateConfig(
            description=description,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

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
    @jsii.member(jsii_name="createdDate")
    def created_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdDate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="expirationDate")
    def expiration_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "expirationDate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pemEncodedCertificate")
    def pem_encoded_certificate(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pemEncodedCertificate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

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
    jsii_type="@cdktf/provider-aws.apigateway.ApiGatewayClientCertificateConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "description": "description",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class ApiGatewayClientCertificateConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        description: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''API Gateway.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_client_certificate#description ApiGatewayClientCertificate#description}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_client_certificate#tags ApiGatewayClientCertificate#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_client_certificate#tags_all ApiGatewayClientCertificate#tags_all}.
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
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_client_certificate#description ApiGatewayClientCertificate#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_client_certificate#tags ApiGatewayClientCertificate#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_client_certificate#tags_all ApiGatewayClientCertificate#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApiGatewayClientCertificateConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ApiGatewayDeployment(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.apigateway.ApiGatewayDeployment",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_deployment aws_api_gateway_deployment}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        rest_api_id: builtins.str,
        description: typing.Optional[builtins.str] = None,
        stage_description: typing.Optional[builtins.str] = None,
        stage_name: typing.Optional[builtins.str] = None,
        triggers: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        variables: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_deployment aws_api_gateway_deployment} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param rest_api_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_deployment#rest_api_id ApiGatewayDeployment#rest_api_id}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_deployment#description ApiGatewayDeployment#description}.
        :param stage_description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_deployment#stage_description ApiGatewayDeployment#stage_description}.
        :param stage_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_deployment#stage_name ApiGatewayDeployment#stage_name}.
        :param triggers: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_deployment#triggers ApiGatewayDeployment#triggers}.
        :param variables: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_deployment#variables ApiGatewayDeployment#variables}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ApiGatewayDeploymentConfig(
            rest_api_id=rest_api_id,
            description=description,
            stage_description=stage_description,
            stage_name=stage_name,
            triggers=triggers,
            variables=variables,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetStageDescription")
    def reset_stage_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStageDescription", []))

    @jsii.member(jsii_name="resetStageName")
    def reset_stage_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStageName", []))

    @jsii.member(jsii_name="resetTriggers")
    def reset_triggers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTriggers", []))

    @jsii.member(jsii_name="resetVariables")
    def reset_variables(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVariables", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createdDate")
    def created_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdDate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="executionArn")
    def execution_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "executionArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="invokeUrl")
    def invoke_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "invokeUrl"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restApiIdInput")
    def rest_api_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "restApiIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stageDescriptionInput")
    def stage_description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stageDescriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stageNameInput")
    def stage_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stageNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="triggersInput")
    def triggers_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "triggersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="variablesInput")
    def variables_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "variablesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restApiId")
    def rest_api_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "restApiId"))

    @rest_api_id.setter
    def rest_api_id(self, value: builtins.str) -> None:
        jsii.set(self, "restApiId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stageDescription")
    def stage_description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "stageDescription"))

    @stage_description.setter
    def stage_description(self, value: builtins.str) -> None:
        jsii.set(self, "stageDescription", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stageName")
    def stage_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "stageName"))

    @stage_name.setter
    def stage_name(self, value: builtins.str) -> None:
        jsii.set(self, "stageName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="triggers")
    def triggers(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "triggers"))

    @triggers.setter
    def triggers(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "triggers", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="variables")
    def variables(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "variables"))

    @variables.setter
    def variables(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "variables", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.apigateway.ApiGatewayDeploymentConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "rest_api_id": "restApiId",
        "description": "description",
        "stage_description": "stageDescription",
        "stage_name": "stageName",
        "triggers": "triggers",
        "variables": "variables",
    },
)
class ApiGatewayDeploymentConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        rest_api_id: builtins.str,
        description: typing.Optional[builtins.str] = None,
        stage_description: typing.Optional[builtins.str] = None,
        stage_name: typing.Optional[builtins.str] = None,
        triggers: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        variables: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''API Gateway.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param rest_api_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_deployment#rest_api_id ApiGatewayDeployment#rest_api_id}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_deployment#description ApiGatewayDeployment#description}.
        :param stage_description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_deployment#stage_description ApiGatewayDeployment#stage_description}.
        :param stage_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_deployment#stage_name ApiGatewayDeployment#stage_name}.
        :param triggers: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_deployment#triggers ApiGatewayDeployment#triggers}.
        :param variables: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_deployment#variables ApiGatewayDeployment#variables}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "rest_api_id": rest_api_id,
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
        if stage_description is not None:
            self._values["stage_description"] = stage_description
        if stage_name is not None:
            self._values["stage_name"] = stage_name
        if triggers is not None:
            self._values["triggers"] = triggers
        if variables is not None:
            self._values["variables"] = variables

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
    def rest_api_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_deployment#rest_api_id ApiGatewayDeployment#rest_api_id}.'''
        result = self._values.get("rest_api_id")
        assert result is not None, "Required property 'rest_api_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_deployment#description ApiGatewayDeployment#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def stage_description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_deployment#stage_description ApiGatewayDeployment#stage_description}.'''
        result = self._values.get("stage_description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def stage_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_deployment#stage_name ApiGatewayDeployment#stage_name}.'''
        result = self._values.get("stage_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def triggers(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_deployment#triggers ApiGatewayDeployment#triggers}.'''
        result = self._values.get("triggers")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def variables(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_deployment#variables ApiGatewayDeployment#variables}.'''
        result = self._values.get("variables")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApiGatewayDeploymentConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ApiGatewayDocumentationPart(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.apigateway.ApiGatewayDocumentationPart",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_documentation_part aws_api_gateway_documentation_part}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        location: "ApiGatewayDocumentationPartLocation",
        properties: builtins.str,
        rest_api_id: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_documentation_part aws_api_gateway_documentation_part} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param location: location block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_documentation_part#location ApiGatewayDocumentationPart#location}
        :param properties: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_documentation_part#properties ApiGatewayDocumentationPart#properties}.
        :param rest_api_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_documentation_part#rest_api_id ApiGatewayDocumentationPart#rest_api_id}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ApiGatewayDocumentationPartConfig(
            location=location,
            properties=properties,
            rest_api_id=rest_api_id,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putLocation")
    def put_location(
        self,
        *,
        type: builtins.str,
        method: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        path: typing.Optional[builtins.str] = None,
        status_code: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_documentation_part#type ApiGatewayDocumentationPart#type}.
        :param method: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_documentation_part#method ApiGatewayDocumentationPart#method}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_documentation_part#name ApiGatewayDocumentationPart#name}.
        :param path: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_documentation_part#path ApiGatewayDocumentationPart#path}.
        :param status_code: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_documentation_part#status_code ApiGatewayDocumentationPart#status_code}.
        '''
        value = ApiGatewayDocumentationPartLocation(
            type=type, method=method, name=name, path=path, status_code=status_code
        )

        return typing.cast(None, jsii.invoke(self, "putLocation", [value]))

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
    @jsii.member(jsii_name="location")
    def location(self) -> "ApiGatewayDocumentationPartLocationOutputReference":
        return typing.cast("ApiGatewayDocumentationPartLocationOutputReference", jsii.get(self, "location"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="locationInput")
    def location_input(self) -> typing.Optional["ApiGatewayDocumentationPartLocation"]:
        return typing.cast(typing.Optional["ApiGatewayDocumentationPartLocation"], jsii.get(self, "locationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="propertiesInput")
    def properties_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "propertiesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restApiIdInput")
    def rest_api_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "restApiIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="properties")
    def properties(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "properties"))

    @properties.setter
    def properties(self, value: builtins.str) -> None:
        jsii.set(self, "properties", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restApiId")
    def rest_api_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "restApiId"))

    @rest_api_id.setter
    def rest_api_id(self, value: builtins.str) -> None:
        jsii.set(self, "restApiId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.apigateway.ApiGatewayDocumentationPartConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "location": "location",
        "properties": "properties",
        "rest_api_id": "restApiId",
    },
)
class ApiGatewayDocumentationPartConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        location: "ApiGatewayDocumentationPartLocation",
        properties: builtins.str,
        rest_api_id: builtins.str,
    ) -> None:
        '''API Gateway.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param location: location block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_documentation_part#location ApiGatewayDocumentationPart#location}
        :param properties: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_documentation_part#properties ApiGatewayDocumentationPart#properties}.
        :param rest_api_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_documentation_part#rest_api_id ApiGatewayDocumentationPart#rest_api_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(location, dict):
            location = ApiGatewayDocumentationPartLocation(**location)
        self._values: typing.Dict[str, typing.Any] = {
            "location": location,
            "properties": properties,
            "rest_api_id": rest_api_id,
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
    def location(self) -> "ApiGatewayDocumentationPartLocation":
        '''location block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_documentation_part#location ApiGatewayDocumentationPart#location}
        '''
        result = self._values.get("location")
        assert result is not None, "Required property 'location' is missing"
        return typing.cast("ApiGatewayDocumentationPartLocation", result)

    @builtins.property
    def properties(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_documentation_part#properties ApiGatewayDocumentationPart#properties}.'''
        result = self._values.get("properties")
        assert result is not None, "Required property 'properties' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def rest_api_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_documentation_part#rest_api_id ApiGatewayDocumentationPart#rest_api_id}.'''
        result = self._values.get("rest_api_id")
        assert result is not None, "Required property 'rest_api_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApiGatewayDocumentationPartConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.apigateway.ApiGatewayDocumentationPartLocation",
    jsii_struct_bases=[],
    name_mapping={
        "type": "type",
        "method": "method",
        "name": "name",
        "path": "path",
        "status_code": "statusCode",
    },
)
class ApiGatewayDocumentationPartLocation:
    def __init__(
        self,
        *,
        type: builtins.str,
        method: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        path: typing.Optional[builtins.str] = None,
        status_code: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_documentation_part#type ApiGatewayDocumentationPart#type}.
        :param method: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_documentation_part#method ApiGatewayDocumentationPart#method}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_documentation_part#name ApiGatewayDocumentationPart#name}.
        :param path: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_documentation_part#path ApiGatewayDocumentationPart#path}.
        :param status_code: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_documentation_part#status_code ApiGatewayDocumentationPart#status_code}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "type": type,
        }
        if method is not None:
            self._values["method"] = method
        if name is not None:
            self._values["name"] = name
        if path is not None:
            self._values["path"] = path
        if status_code is not None:
            self._values["status_code"] = status_code

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_documentation_part#type ApiGatewayDocumentationPart#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def method(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_documentation_part#method ApiGatewayDocumentationPart#method}.'''
        result = self._values.get("method")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_documentation_part#name ApiGatewayDocumentationPart#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def path(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_documentation_part#path ApiGatewayDocumentationPart#path}.'''
        result = self._values.get("path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def status_code(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_documentation_part#status_code ApiGatewayDocumentationPart#status_code}.'''
        result = self._values.get("status_code")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApiGatewayDocumentationPartLocation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ApiGatewayDocumentationPartLocationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.apigateway.ApiGatewayDocumentationPartLocationOutputReference",
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

    @jsii.member(jsii_name="resetMethod")
    def reset_method(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMethod", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetPath")
    def reset_path(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPath", []))

    @jsii.member(jsii_name="resetStatusCode")
    def reset_status_code(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStatusCode", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="methodInput")
    def method_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "methodInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pathInput")
    def path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pathInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statusCodeInput")
    def status_code_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "statusCodeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="method")
    def method(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "method"))

    @method.setter
    def method(self, value: builtins.str) -> None:
        jsii.set(self, "method", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "path"))

    @path.setter
    def path(self, value: builtins.str) -> None:
        jsii.set(self, "path", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statusCode")
    def status_code(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "statusCode"))

    @status_code.setter
    def status_code(self, value: builtins.str) -> None:
        jsii.set(self, "statusCode", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        jsii.set(self, "type", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ApiGatewayDocumentationPartLocation]:
        return typing.cast(typing.Optional[ApiGatewayDocumentationPartLocation], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ApiGatewayDocumentationPartLocation],
    ) -> None:
        jsii.set(self, "internalValue", value)


class ApiGatewayDocumentationVersion(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.apigateway.ApiGatewayDocumentationVersion",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_documentation_version aws_api_gateway_documentation_version}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        rest_api_id: builtins.str,
        version: builtins.str,
        description: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_documentation_version aws_api_gateway_documentation_version} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param rest_api_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_documentation_version#rest_api_id ApiGatewayDocumentationVersion#rest_api_id}.
        :param version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_documentation_version#version ApiGatewayDocumentationVersion#version}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_documentation_version#description ApiGatewayDocumentationVersion#description}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ApiGatewayDocumentationVersionConfig(
            rest_api_id=rest_api_id,
            version=version,
            description=description,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

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
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restApiIdInput")
    def rest_api_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "restApiIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="versionInput")
    def version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "versionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restApiId")
    def rest_api_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "restApiId"))

    @rest_api_id.setter
    def rest_api_id(self, value: builtins.str) -> None:
        jsii.set(self, "restApiId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @version.setter
    def version(self, value: builtins.str) -> None:
        jsii.set(self, "version", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.apigateway.ApiGatewayDocumentationVersionConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "rest_api_id": "restApiId",
        "version": "version",
        "description": "description",
    },
)
class ApiGatewayDocumentationVersionConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        rest_api_id: builtins.str,
        version: builtins.str,
        description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''API Gateway.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param rest_api_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_documentation_version#rest_api_id ApiGatewayDocumentationVersion#rest_api_id}.
        :param version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_documentation_version#version ApiGatewayDocumentationVersion#version}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_documentation_version#description ApiGatewayDocumentationVersion#description}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "rest_api_id": rest_api_id,
            "version": version,
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
    def rest_api_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_documentation_version#rest_api_id ApiGatewayDocumentationVersion#rest_api_id}.'''
        result = self._values.get("rest_api_id")
        assert result is not None, "Required property 'rest_api_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def version(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_documentation_version#version ApiGatewayDocumentationVersion#version}.'''
        result = self._values.get("version")
        assert result is not None, "Required property 'version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_documentation_version#description ApiGatewayDocumentationVersion#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApiGatewayDocumentationVersionConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ApiGatewayDomainName(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.apigateway.ApiGatewayDomainName",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_domain_name aws_api_gateway_domain_name}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        domain_name: builtins.str,
        certificate_arn: typing.Optional[builtins.str] = None,
        certificate_body: typing.Optional[builtins.str] = None,
        certificate_chain: typing.Optional[builtins.str] = None,
        certificate_name: typing.Optional[builtins.str] = None,
        certificate_private_key: typing.Optional[builtins.str] = None,
        endpoint_configuration: typing.Optional["ApiGatewayDomainNameEndpointConfiguration"] = None,
        mutual_tls_authentication: typing.Optional["ApiGatewayDomainNameMutualTlsAuthentication"] = None,
        regional_certificate_arn: typing.Optional[builtins.str] = None,
        regional_certificate_name: typing.Optional[builtins.str] = None,
        security_policy: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_domain_name aws_api_gateway_domain_name} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param domain_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_domain_name#domain_name ApiGatewayDomainName#domain_name}.
        :param certificate_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_domain_name#certificate_arn ApiGatewayDomainName#certificate_arn}.
        :param certificate_body: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_domain_name#certificate_body ApiGatewayDomainName#certificate_body}.
        :param certificate_chain: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_domain_name#certificate_chain ApiGatewayDomainName#certificate_chain}.
        :param certificate_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_domain_name#certificate_name ApiGatewayDomainName#certificate_name}.
        :param certificate_private_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_domain_name#certificate_private_key ApiGatewayDomainName#certificate_private_key}.
        :param endpoint_configuration: endpoint_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_domain_name#endpoint_configuration ApiGatewayDomainName#endpoint_configuration}
        :param mutual_tls_authentication: mutual_tls_authentication block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_domain_name#mutual_tls_authentication ApiGatewayDomainName#mutual_tls_authentication}
        :param regional_certificate_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_domain_name#regional_certificate_arn ApiGatewayDomainName#regional_certificate_arn}.
        :param regional_certificate_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_domain_name#regional_certificate_name ApiGatewayDomainName#regional_certificate_name}.
        :param security_policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_domain_name#security_policy ApiGatewayDomainName#security_policy}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_domain_name#tags ApiGatewayDomainName#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_domain_name#tags_all ApiGatewayDomainName#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ApiGatewayDomainNameConfig(
            domain_name=domain_name,
            certificate_arn=certificate_arn,
            certificate_body=certificate_body,
            certificate_chain=certificate_chain,
            certificate_name=certificate_name,
            certificate_private_key=certificate_private_key,
            endpoint_configuration=endpoint_configuration,
            mutual_tls_authentication=mutual_tls_authentication,
            regional_certificate_arn=regional_certificate_arn,
            regional_certificate_name=regional_certificate_name,
            security_policy=security_policy,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putEndpointConfiguration")
    def put_endpoint_configuration(
        self,
        *,
        types: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param types: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_domain_name#types ApiGatewayDomainName#types}.
        '''
        value = ApiGatewayDomainNameEndpointConfiguration(types=types)

        return typing.cast(None, jsii.invoke(self, "putEndpointConfiguration", [value]))

    @jsii.member(jsii_name="putMutualTlsAuthentication")
    def put_mutual_tls_authentication(
        self,
        *,
        truststore_uri: builtins.str,
        truststore_version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param truststore_uri: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_domain_name#truststore_uri ApiGatewayDomainName#truststore_uri}.
        :param truststore_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_domain_name#truststore_version ApiGatewayDomainName#truststore_version}.
        '''
        value = ApiGatewayDomainNameMutualTlsAuthentication(
            truststore_uri=truststore_uri, truststore_version=truststore_version
        )

        return typing.cast(None, jsii.invoke(self, "putMutualTlsAuthentication", [value]))

    @jsii.member(jsii_name="resetCertificateArn")
    def reset_certificate_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCertificateArn", []))

    @jsii.member(jsii_name="resetCertificateBody")
    def reset_certificate_body(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCertificateBody", []))

    @jsii.member(jsii_name="resetCertificateChain")
    def reset_certificate_chain(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCertificateChain", []))

    @jsii.member(jsii_name="resetCertificateName")
    def reset_certificate_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCertificateName", []))

    @jsii.member(jsii_name="resetCertificatePrivateKey")
    def reset_certificate_private_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCertificatePrivateKey", []))

    @jsii.member(jsii_name="resetEndpointConfiguration")
    def reset_endpoint_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEndpointConfiguration", []))

    @jsii.member(jsii_name="resetMutualTlsAuthentication")
    def reset_mutual_tls_authentication(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMutualTlsAuthentication", []))

    @jsii.member(jsii_name="resetRegionalCertificateArn")
    def reset_regional_certificate_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegionalCertificateArn", []))

    @jsii.member(jsii_name="resetRegionalCertificateName")
    def reset_regional_certificate_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegionalCertificateName", []))

    @jsii.member(jsii_name="resetSecurityPolicy")
    def reset_security_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecurityPolicy", []))

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
    @jsii.member(jsii_name="certificateUploadDate")
    def certificate_upload_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificateUploadDate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cloudfrontDomainName")
    def cloudfront_domain_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cloudfrontDomainName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cloudfrontZoneId")
    def cloudfront_zone_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cloudfrontZoneId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpointConfiguration")
    def endpoint_configuration(
        self,
    ) -> "ApiGatewayDomainNameEndpointConfigurationOutputReference":
        return typing.cast("ApiGatewayDomainNameEndpointConfigurationOutputReference", jsii.get(self, "endpointConfiguration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mutualTlsAuthentication")
    def mutual_tls_authentication(
        self,
    ) -> "ApiGatewayDomainNameMutualTlsAuthenticationOutputReference":
        return typing.cast("ApiGatewayDomainNameMutualTlsAuthenticationOutputReference", jsii.get(self, "mutualTlsAuthentication"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="regionalDomainName")
    def regional_domain_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "regionalDomainName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="regionalZoneId")
    def regional_zone_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "regionalZoneId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certificateArnInput")
    def certificate_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certificateArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certificateBodyInput")
    def certificate_body_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certificateBodyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certificateChainInput")
    def certificate_chain_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certificateChainInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certificateNameInput")
    def certificate_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certificateNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certificatePrivateKeyInput")
    def certificate_private_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certificatePrivateKeyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainNameInput")
    def domain_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "domainNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpointConfigurationInput")
    def endpoint_configuration_input(
        self,
    ) -> typing.Optional["ApiGatewayDomainNameEndpointConfiguration"]:
        return typing.cast(typing.Optional["ApiGatewayDomainNameEndpointConfiguration"], jsii.get(self, "endpointConfigurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mutualTlsAuthenticationInput")
    def mutual_tls_authentication_input(
        self,
    ) -> typing.Optional["ApiGatewayDomainNameMutualTlsAuthentication"]:
        return typing.cast(typing.Optional["ApiGatewayDomainNameMutualTlsAuthentication"], jsii.get(self, "mutualTlsAuthenticationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="regionalCertificateArnInput")
    def regional_certificate_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "regionalCertificateArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="regionalCertificateNameInput")
    def regional_certificate_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "regionalCertificateNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityPolicyInput")
    def security_policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "securityPolicyInput"))

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
    @jsii.member(jsii_name="certificateArn")
    def certificate_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificateArn"))

    @certificate_arn.setter
    def certificate_arn(self, value: builtins.str) -> None:
        jsii.set(self, "certificateArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certificateBody")
    def certificate_body(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificateBody"))

    @certificate_body.setter
    def certificate_body(self, value: builtins.str) -> None:
        jsii.set(self, "certificateBody", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certificateChain")
    def certificate_chain(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificateChain"))

    @certificate_chain.setter
    def certificate_chain(self, value: builtins.str) -> None:
        jsii.set(self, "certificateChain", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certificateName")
    def certificate_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificateName"))

    @certificate_name.setter
    def certificate_name(self, value: builtins.str) -> None:
        jsii.set(self, "certificateName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certificatePrivateKey")
    def certificate_private_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificatePrivateKey"))

    @certificate_private_key.setter
    def certificate_private_key(self, value: builtins.str) -> None:
        jsii.set(self, "certificatePrivateKey", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainName")
    def domain_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "domainName"))

    @domain_name.setter
    def domain_name(self, value: builtins.str) -> None:
        jsii.set(self, "domainName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="regionalCertificateArn")
    def regional_certificate_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "regionalCertificateArn"))

    @regional_certificate_arn.setter
    def regional_certificate_arn(self, value: builtins.str) -> None:
        jsii.set(self, "regionalCertificateArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="regionalCertificateName")
    def regional_certificate_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "regionalCertificateName"))

    @regional_certificate_name.setter
    def regional_certificate_name(self, value: builtins.str) -> None:
        jsii.set(self, "regionalCertificateName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityPolicy")
    def security_policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "securityPolicy"))

    @security_policy.setter
    def security_policy(self, value: builtins.str) -> None:
        jsii.set(self, "securityPolicy", value)

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
    jsii_type="@cdktf/provider-aws.apigateway.ApiGatewayDomainNameConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "domain_name": "domainName",
        "certificate_arn": "certificateArn",
        "certificate_body": "certificateBody",
        "certificate_chain": "certificateChain",
        "certificate_name": "certificateName",
        "certificate_private_key": "certificatePrivateKey",
        "endpoint_configuration": "endpointConfiguration",
        "mutual_tls_authentication": "mutualTlsAuthentication",
        "regional_certificate_arn": "regionalCertificateArn",
        "regional_certificate_name": "regionalCertificateName",
        "security_policy": "securityPolicy",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class ApiGatewayDomainNameConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        domain_name: builtins.str,
        certificate_arn: typing.Optional[builtins.str] = None,
        certificate_body: typing.Optional[builtins.str] = None,
        certificate_chain: typing.Optional[builtins.str] = None,
        certificate_name: typing.Optional[builtins.str] = None,
        certificate_private_key: typing.Optional[builtins.str] = None,
        endpoint_configuration: typing.Optional["ApiGatewayDomainNameEndpointConfiguration"] = None,
        mutual_tls_authentication: typing.Optional["ApiGatewayDomainNameMutualTlsAuthentication"] = None,
        regional_certificate_arn: typing.Optional[builtins.str] = None,
        regional_certificate_name: typing.Optional[builtins.str] = None,
        security_policy: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''API Gateway.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param domain_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_domain_name#domain_name ApiGatewayDomainName#domain_name}.
        :param certificate_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_domain_name#certificate_arn ApiGatewayDomainName#certificate_arn}.
        :param certificate_body: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_domain_name#certificate_body ApiGatewayDomainName#certificate_body}.
        :param certificate_chain: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_domain_name#certificate_chain ApiGatewayDomainName#certificate_chain}.
        :param certificate_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_domain_name#certificate_name ApiGatewayDomainName#certificate_name}.
        :param certificate_private_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_domain_name#certificate_private_key ApiGatewayDomainName#certificate_private_key}.
        :param endpoint_configuration: endpoint_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_domain_name#endpoint_configuration ApiGatewayDomainName#endpoint_configuration}
        :param mutual_tls_authentication: mutual_tls_authentication block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_domain_name#mutual_tls_authentication ApiGatewayDomainName#mutual_tls_authentication}
        :param regional_certificate_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_domain_name#regional_certificate_arn ApiGatewayDomainName#regional_certificate_arn}.
        :param regional_certificate_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_domain_name#regional_certificate_name ApiGatewayDomainName#regional_certificate_name}.
        :param security_policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_domain_name#security_policy ApiGatewayDomainName#security_policy}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_domain_name#tags ApiGatewayDomainName#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_domain_name#tags_all ApiGatewayDomainName#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(endpoint_configuration, dict):
            endpoint_configuration = ApiGatewayDomainNameEndpointConfiguration(**endpoint_configuration)
        if isinstance(mutual_tls_authentication, dict):
            mutual_tls_authentication = ApiGatewayDomainNameMutualTlsAuthentication(**mutual_tls_authentication)
        self._values: typing.Dict[str, typing.Any] = {
            "domain_name": domain_name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if certificate_arn is not None:
            self._values["certificate_arn"] = certificate_arn
        if certificate_body is not None:
            self._values["certificate_body"] = certificate_body
        if certificate_chain is not None:
            self._values["certificate_chain"] = certificate_chain
        if certificate_name is not None:
            self._values["certificate_name"] = certificate_name
        if certificate_private_key is not None:
            self._values["certificate_private_key"] = certificate_private_key
        if endpoint_configuration is not None:
            self._values["endpoint_configuration"] = endpoint_configuration
        if mutual_tls_authentication is not None:
            self._values["mutual_tls_authentication"] = mutual_tls_authentication
        if regional_certificate_arn is not None:
            self._values["regional_certificate_arn"] = regional_certificate_arn
        if regional_certificate_name is not None:
            self._values["regional_certificate_name"] = regional_certificate_name
        if security_policy is not None:
            self._values["security_policy"] = security_policy
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
    def domain_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_domain_name#domain_name ApiGatewayDomainName#domain_name}.'''
        result = self._values.get("domain_name")
        assert result is not None, "Required property 'domain_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def certificate_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_domain_name#certificate_arn ApiGatewayDomainName#certificate_arn}.'''
        result = self._values.get("certificate_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def certificate_body(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_domain_name#certificate_body ApiGatewayDomainName#certificate_body}.'''
        result = self._values.get("certificate_body")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def certificate_chain(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_domain_name#certificate_chain ApiGatewayDomainName#certificate_chain}.'''
        result = self._values.get("certificate_chain")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def certificate_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_domain_name#certificate_name ApiGatewayDomainName#certificate_name}.'''
        result = self._values.get("certificate_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def certificate_private_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_domain_name#certificate_private_key ApiGatewayDomainName#certificate_private_key}.'''
        result = self._values.get("certificate_private_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def endpoint_configuration(
        self,
    ) -> typing.Optional["ApiGatewayDomainNameEndpointConfiguration"]:
        '''endpoint_configuration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_domain_name#endpoint_configuration ApiGatewayDomainName#endpoint_configuration}
        '''
        result = self._values.get("endpoint_configuration")
        return typing.cast(typing.Optional["ApiGatewayDomainNameEndpointConfiguration"], result)

    @builtins.property
    def mutual_tls_authentication(
        self,
    ) -> typing.Optional["ApiGatewayDomainNameMutualTlsAuthentication"]:
        '''mutual_tls_authentication block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_domain_name#mutual_tls_authentication ApiGatewayDomainName#mutual_tls_authentication}
        '''
        result = self._values.get("mutual_tls_authentication")
        return typing.cast(typing.Optional["ApiGatewayDomainNameMutualTlsAuthentication"], result)

    @builtins.property
    def regional_certificate_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_domain_name#regional_certificate_arn ApiGatewayDomainName#regional_certificate_arn}.'''
        result = self._values.get("regional_certificate_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def regional_certificate_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_domain_name#regional_certificate_name ApiGatewayDomainName#regional_certificate_name}.'''
        result = self._values.get("regional_certificate_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def security_policy(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_domain_name#security_policy ApiGatewayDomainName#security_policy}.'''
        result = self._values.get("security_policy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_domain_name#tags ApiGatewayDomainName#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_domain_name#tags_all ApiGatewayDomainName#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApiGatewayDomainNameConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.apigateway.ApiGatewayDomainNameEndpointConfiguration",
    jsii_struct_bases=[],
    name_mapping={"types": "types"},
)
class ApiGatewayDomainNameEndpointConfiguration:
    def __init__(self, *, types: typing.Sequence[builtins.str]) -> None:
        '''
        :param types: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_domain_name#types ApiGatewayDomainName#types}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "types": types,
        }

    @builtins.property
    def types(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_domain_name#types ApiGatewayDomainName#types}.'''
        result = self._values.get("types")
        assert result is not None, "Required property 'types' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApiGatewayDomainNameEndpointConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ApiGatewayDomainNameEndpointConfigurationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.apigateway.ApiGatewayDomainNameEndpointConfigurationOutputReference",
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
    @jsii.member(jsii_name="typesInput")
    def types_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "typesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="types")
    def types(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "types"))

    @types.setter
    def types(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "types", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ApiGatewayDomainNameEndpointConfiguration]:
        return typing.cast(typing.Optional[ApiGatewayDomainNameEndpointConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ApiGatewayDomainNameEndpointConfiguration],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.apigateway.ApiGatewayDomainNameMutualTlsAuthentication",
    jsii_struct_bases=[],
    name_mapping={
        "truststore_uri": "truststoreUri",
        "truststore_version": "truststoreVersion",
    },
)
class ApiGatewayDomainNameMutualTlsAuthentication:
    def __init__(
        self,
        *,
        truststore_uri: builtins.str,
        truststore_version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param truststore_uri: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_domain_name#truststore_uri ApiGatewayDomainName#truststore_uri}.
        :param truststore_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_domain_name#truststore_version ApiGatewayDomainName#truststore_version}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "truststore_uri": truststore_uri,
        }
        if truststore_version is not None:
            self._values["truststore_version"] = truststore_version

    @builtins.property
    def truststore_uri(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_domain_name#truststore_uri ApiGatewayDomainName#truststore_uri}.'''
        result = self._values.get("truststore_uri")
        assert result is not None, "Required property 'truststore_uri' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def truststore_version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_domain_name#truststore_version ApiGatewayDomainName#truststore_version}.'''
        result = self._values.get("truststore_version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApiGatewayDomainNameMutualTlsAuthentication(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ApiGatewayDomainNameMutualTlsAuthenticationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.apigateway.ApiGatewayDomainNameMutualTlsAuthenticationOutputReference",
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

    @jsii.member(jsii_name="resetTruststoreVersion")
    def reset_truststore_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTruststoreVersion", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="truststoreUriInput")
    def truststore_uri_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "truststoreUriInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="truststoreVersionInput")
    def truststore_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "truststoreVersionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="truststoreUri")
    def truststore_uri(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "truststoreUri"))

    @truststore_uri.setter
    def truststore_uri(self, value: builtins.str) -> None:
        jsii.set(self, "truststoreUri", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="truststoreVersion")
    def truststore_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "truststoreVersion"))

    @truststore_version.setter
    def truststore_version(self, value: builtins.str) -> None:
        jsii.set(self, "truststoreVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ApiGatewayDomainNameMutualTlsAuthentication]:
        return typing.cast(typing.Optional[ApiGatewayDomainNameMutualTlsAuthentication], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ApiGatewayDomainNameMutualTlsAuthentication],
    ) -> None:
        jsii.set(self, "internalValue", value)


class ApiGatewayGatewayResponse(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.apigateway.ApiGatewayGatewayResponse",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_gateway_response aws_api_gateway_gateway_response}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        response_type: builtins.str,
        rest_api_id: builtins.str,
        response_parameters: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        response_templates: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        status_code: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_gateway_response aws_api_gateway_gateway_response} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param response_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_gateway_response#response_type ApiGatewayGatewayResponse#response_type}.
        :param rest_api_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_gateway_response#rest_api_id ApiGatewayGatewayResponse#rest_api_id}.
        :param response_parameters: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_gateway_response#response_parameters ApiGatewayGatewayResponse#response_parameters}.
        :param response_templates: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_gateway_response#response_templates ApiGatewayGatewayResponse#response_templates}.
        :param status_code: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_gateway_response#status_code ApiGatewayGatewayResponse#status_code}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ApiGatewayGatewayResponseConfig(
            response_type=response_type,
            rest_api_id=rest_api_id,
            response_parameters=response_parameters,
            response_templates=response_templates,
            status_code=status_code,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetResponseParameters")
    def reset_response_parameters(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResponseParameters", []))

    @jsii.member(jsii_name="resetResponseTemplates")
    def reset_response_templates(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResponseTemplates", []))

    @jsii.member(jsii_name="resetStatusCode")
    def reset_status_code(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStatusCode", []))

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
    @jsii.member(jsii_name="responseParametersInput")
    def response_parameters_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "responseParametersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="responseTemplatesInput")
    def response_templates_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "responseTemplatesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="responseTypeInput")
    def response_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "responseTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restApiIdInput")
    def rest_api_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "restApiIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statusCodeInput")
    def status_code_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "statusCodeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="responseParameters")
    def response_parameters(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "responseParameters"))

    @response_parameters.setter
    def response_parameters(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "responseParameters", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="responseTemplates")
    def response_templates(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "responseTemplates"))

    @response_templates.setter
    def response_templates(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "responseTemplates", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="responseType")
    def response_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "responseType"))

    @response_type.setter
    def response_type(self, value: builtins.str) -> None:
        jsii.set(self, "responseType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restApiId")
    def rest_api_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "restApiId"))

    @rest_api_id.setter
    def rest_api_id(self, value: builtins.str) -> None:
        jsii.set(self, "restApiId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statusCode")
    def status_code(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "statusCode"))

    @status_code.setter
    def status_code(self, value: builtins.str) -> None:
        jsii.set(self, "statusCode", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.apigateway.ApiGatewayGatewayResponseConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "response_type": "responseType",
        "rest_api_id": "restApiId",
        "response_parameters": "responseParameters",
        "response_templates": "responseTemplates",
        "status_code": "statusCode",
    },
)
class ApiGatewayGatewayResponseConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        response_type: builtins.str,
        rest_api_id: builtins.str,
        response_parameters: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        response_templates: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        status_code: typing.Optional[builtins.str] = None,
    ) -> None:
        '''API Gateway.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param response_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_gateway_response#response_type ApiGatewayGatewayResponse#response_type}.
        :param rest_api_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_gateway_response#rest_api_id ApiGatewayGatewayResponse#rest_api_id}.
        :param response_parameters: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_gateway_response#response_parameters ApiGatewayGatewayResponse#response_parameters}.
        :param response_templates: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_gateway_response#response_templates ApiGatewayGatewayResponse#response_templates}.
        :param status_code: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_gateway_response#status_code ApiGatewayGatewayResponse#status_code}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "response_type": response_type,
            "rest_api_id": rest_api_id,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if response_parameters is not None:
            self._values["response_parameters"] = response_parameters
        if response_templates is not None:
            self._values["response_templates"] = response_templates
        if status_code is not None:
            self._values["status_code"] = status_code

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
    def response_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_gateway_response#response_type ApiGatewayGatewayResponse#response_type}.'''
        result = self._values.get("response_type")
        assert result is not None, "Required property 'response_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def rest_api_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_gateway_response#rest_api_id ApiGatewayGatewayResponse#rest_api_id}.'''
        result = self._values.get("rest_api_id")
        assert result is not None, "Required property 'rest_api_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def response_parameters(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_gateway_response#response_parameters ApiGatewayGatewayResponse#response_parameters}.'''
        result = self._values.get("response_parameters")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def response_templates(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_gateway_response#response_templates ApiGatewayGatewayResponse#response_templates}.'''
        result = self._values.get("response_templates")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def status_code(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_gateway_response#status_code ApiGatewayGatewayResponse#status_code}.'''
        result = self._values.get("status_code")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApiGatewayGatewayResponseConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ApiGatewayIntegration(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.apigateway.ApiGatewayIntegration",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration aws_api_gateway_integration}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        http_method: builtins.str,
        resource_id: builtins.str,
        rest_api_id: builtins.str,
        type: builtins.str,
        cache_key_parameters: typing.Optional[typing.Sequence[builtins.str]] = None,
        cache_namespace: typing.Optional[builtins.str] = None,
        connection_id: typing.Optional[builtins.str] = None,
        connection_type: typing.Optional[builtins.str] = None,
        content_handling: typing.Optional[builtins.str] = None,
        credentials: typing.Optional[builtins.str] = None,
        integration_http_method: typing.Optional[builtins.str] = None,
        passthrough_behavior: typing.Optional[builtins.str] = None,
        request_parameters: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        request_templates: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeout_milliseconds: typing.Optional[jsii.Number] = None,
        tls_config: typing.Optional["ApiGatewayIntegrationTlsConfig"] = None,
        uri: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration aws_api_gateway_integration} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param http_method: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration#http_method ApiGatewayIntegration#http_method}.
        :param resource_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration#resource_id ApiGatewayIntegration#resource_id}.
        :param rest_api_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration#rest_api_id ApiGatewayIntegration#rest_api_id}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration#type ApiGatewayIntegration#type}.
        :param cache_key_parameters: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration#cache_key_parameters ApiGatewayIntegration#cache_key_parameters}.
        :param cache_namespace: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration#cache_namespace ApiGatewayIntegration#cache_namespace}.
        :param connection_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration#connection_id ApiGatewayIntegration#connection_id}.
        :param connection_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration#connection_type ApiGatewayIntegration#connection_type}.
        :param content_handling: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration#content_handling ApiGatewayIntegration#content_handling}.
        :param credentials: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration#credentials ApiGatewayIntegration#credentials}.
        :param integration_http_method: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration#integration_http_method ApiGatewayIntegration#integration_http_method}.
        :param passthrough_behavior: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration#passthrough_behavior ApiGatewayIntegration#passthrough_behavior}.
        :param request_parameters: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration#request_parameters ApiGatewayIntegration#request_parameters}.
        :param request_templates: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration#request_templates ApiGatewayIntegration#request_templates}.
        :param timeout_milliseconds: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration#timeout_milliseconds ApiGatewayIntegration#timeout_milliseconds}.
        :param tls_config: tls_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration#tls_config ApiGatewayIntegration#tls_config}
        :param uri: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration#uri ApiGatewayIntegration#uri}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ApiGatewayIntegrationConfig(
            http_method=http_method,
            resource_id=resource_id,
            rest_api_id=rest_api_id,
            type=type,
            cache_key_parameters=cache_key_parameters,
            cache_namespace=cache_namespace,
            connection_id=connection_id,
            connection_type=connection_type,
            content_handling=content_handling,
            credentials=credentials,
            integration_http_method=integration_http_method,
            passthrough_behavior=passthrough_behavior,
            request_parameters=request_parameters,
            request_templates=request_templates,
            timeout_milliseconds=timeout_milliseconds,
            tls_config=tls_config,
            uri=uri,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putTlsConfig")
    def put_tls_config(
        self,
        *,
        insecure_skip_verification: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param insecure_skip_verification: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration#insecure_skip_verification ApiGatewayIntegration#insecure_skip_verification}.
        '''
        value = ApiGatewayIntegrationTlsConfig(
            insecure_skip_verification=insecure_skip_verification
        )

        return typing.cast(None, jsii.invoke(self, "putTlsConfig", [value]))

    @jsii.member(jsii_name="resetCacheKeyParameters")
    def reset_cache_key_parameters(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCacheKeyParameters", []))

    @jsii.member(jsii_name="resetCacheNamespace")
    def reset_cache_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCacheNamespace", []))

    @jsii.member(jsii_name="resetConnectionId")
    def reset_connection_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConnectionId", []))

    @jsii.member(jsii_name="resetConnectionType")
    def reset_connection_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConnectionType", []))

    @jsii.member(jsii_name="resetContentHandling")
    def reset_content_handling(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetContentHandling", []))

    @jsii.member(jsii_name="resetCredentials")
    def reset_credentials(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCredentials", []))

    @jsii.member(jsii_name="resetIntegrationHttpMethod")
    def reset_integration_http_method(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIntegrationHttpMethod", []))

    @jsii.member(jsii_name="resetPassthroughBehavior")
    def reset_passthrough_behavior(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPassthroughBehavior", []))

    @jsii.member(jsii_name="resetRequestParameters")
    def reset_request_parameters(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequestParameters", []))

    @jsii.member(jsii_name="resetRequestTemplates")
    def reset_request_templates(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequestTemplates", []))

    @jsii.member(jsii_name="resetTimeoutMilliseconds")
    def reset_timeout_milliseconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeoutMilliseconds", []))

    @jsii.member(jsii_name="resetTlsConfig")
    def reset_tls_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTlsConfig", []))

    @jsii.member(jsii_name="resetUri")
    def reset_uri(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUri", []))

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
    @jsii.member(jsii_name="tlsConfig")
    def tls_config(self) -> "ApiGatewayIntegrationTlsConfigOutputReference":
        return typing.cast("ApiGatewayIntegrationTlsConfigOutputReference", jsii.get(self, "tlsConfig"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cacheKeyParametersInput")
    def cache_key_parameters_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "cacheKeyParametersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cacheNamespaceInput")
    def cache_namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cacheNamespaceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="connectionIdInput")
    def connection_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "connectionIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="connectionTypeInput")
    def connection_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "connectionTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="contentHandlingInput")
    def content_handling_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "contentHandlingInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="credentialsInput")
    def credentials_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "credentialsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="httpMethodInput")
    def http_method_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "httpMethodInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="integrationHttpMethodInput")
    def integration_http_method_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "integrationHttpMethodInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="passthroughBehaviorInput")
    def passthrough_behavior_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passthroughBehaviorInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requestParametersInput")
    def request_parameters_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "requestParametersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requestTemplatesInput")
    def request_templates_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "requestTemplatesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceIdInput")
    def resource_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "resourceIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restApiIdInput")
    def rest_api_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "restApiIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutMillisecondsInput")
    def timeout_milliseconds_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "timeoutMillisecondsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tlsConfigInput")
    def tls_config_input(self) -> typing.Optional["ApiGatewayIntegrationTlsConfig"]:
        return typing.cast(typing.Optional["ApiGatewayIntegrationTlsConfig"], jsii.get(self, "tlsConfigInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="uriInput")
    def uri_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "uriInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cacheKeyParameters")
    def cache_key_parameters(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "cacheKeyParameters"))

    @cache_key_parameters.setter
    def cache_key_parameters(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "cacheKeyParameters", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cacheNamespace")
    def cache_namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cacheNamespace"))

    @cache_namespace.setter
    def cache_namespace(self, value: builtins.str) -> None:
        jsii.set(self, "cacheNamespace", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="connectionId")
    def connection_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "connectionId"))

    @connection_id.setter
    def connection_id(self, value: builtins.str) -> None:
        jsii.set(self, "connectionId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="connectionType")
    def connection_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "connectionType"))

    @connection_type.setter
    def connection_type(self, value: builtins.str) -> None:
        jsii.set(self, "connectionType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="contentHandling")
    def content_handling(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "contentHandling"))

    @content_handling.setter
    def content_handling(self, value: builtins.str) -> None:
        jsii.set(self, "contentHandling", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="credentials")
    def credentials(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "credentials"))

    @credentials.setter
    def credentials(self, value: builtins.str) -> None:
        jsii.set(self, "credentials", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="httpMethod")
    def http_method(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "httpMethod"))

    @http_method.setter
    def http_method(self, value: builtins.str) -> None:
        jsii.set(self, "httpMethod", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="integrationHttpMethod")
    def integration_http_method(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "integrationHttpMethod"))

    @integration_http_method.setter
    def integration_http_method(self, value: builtins.str) -> None:
        jsii.set(self, "integrationHttpMethod", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="passthroughBehavior")
    def passthrough_behavior(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "passthroughBehavior"))

    @passthrough_behavior.setter
    def passthrough_behavior(self, value: builtins.str) -> None:
        jsii.set(self, "passthroughBehavior", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requestParameters")
    def request_parameters(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "requestParameters"))

    @request_parameters.setter
    def request_parameters(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "requestParameters", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requestTemplates")
    def request_templates(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "requestTemplates"))

    @request_templates.setter
    def request_templates(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "requestTemplates", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceId")
    def resource_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "resourceId"))

    @resource_id.setter
    def resource_id(self, value: builtins.str) -> None:
        jsii.set(self, "resourceId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restApiId")
    def rest_api_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "restApiId"))

    @rest_api_id.setter
    def rest_api_id(self, value: builtins.str) -> None:
        jsii.set(self, "restApiId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutMilliseconds")
    def timeout_milliseconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "timeoutMilliseconds"))

    @timeout_milliseconds.setter
    def timeout_milliseconds(self, value: jsii.Number) -> None:
        jsii.set(self, "timeoutMilliseconds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        jsii.set(self, "type", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="uri")
    def uri(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uri"))

    @uri.setter
    def uri(self, value: builtins.str) -> None:
        jsii.set(self, "uri", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.apigateway.ApiGatewayIntegrationConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "http_method": "httpMethod",
        "resource_id": "resourceId",
        "rest_api_id": "restApiId",
        "type": "type",
        "cache_key_parameters": "cacheKeyParameters",
        "cache_namespace": "cacheNamespace",
        "connection_id": "connectionId",
        "connection_type": "connectionType",
        "content_handling": "contentHandling",
        "credentials": "credentials",
        "integration_http_method": "integrationHttpMethod",
        "passthrough_behavior": "passthroughBehavior",
        "request_parameters": "requestParameters",
        "request_templates": "requestTemplates",
        "timeout_milliseconds": "timeoutMilliseconds",
        "tls_config": "tlsConfig",
        "uri": "uri",
    },
)
class ApiGatewayIntegrationConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        http_method: builtins.str,
        resource_id: builtins.str,
        rest_api_id: builtins.str,
        type: builtins.str,
        cache_key_parameters: typing.Optional[typing.Sequence[builtins.str]] = None,
        cache_namespace: typing.Optional[builtins.str] = None,
        connection_id: typing.Optional[builtins.str] = None,
        connection_type: typing.Optional[builtins.str] = None,
        content_handling: typing.Optional[builtins.str] = None,
        credentials: typing.Optional[builtins.str] = None,
        integration_http_method: typing.Optional[builtins.str] = None,
        passthrough_behavior: typing.Optional[builtins.str] = None,
        request_parameters: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        request_templates: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeout_milliseconds: typing.Optional[jsii.Number] = None,
        tls_config: typing.Optional["ApiGatewayIntegrationTlsConfig"] = None,
        uri: typing.Optional[builtins.str] = None,
    ) -> None:
        '''API Gateway.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param http_method: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration#http_method ApiGatewayIntegration#http_method}.
        :param resource_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration#resource_id ApiGatewayIntegration#resource_id}.
        :param rest_api_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration#rest_api_id ApiGatewayIntegration#rest_api_id}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration#type ApiGatewayIntegration#type}.
        :param cache_key_parameters: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration#cache_key_parameters ApiGatewayIntegration#cache_key_parameters}.
        :param cache_namespace: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration#cache_namespace ApiGatewayIntegration#cache_namespace}.
        :param connection_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration#connection_id ApiGatewayIntegration#connection_id}.
        :param connection_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration#connection_type ApiGatewayIntegration#connection_type}.
        :param content_handling: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration#content_handling ApiGatewayIntegration#content_handling}.
        :param credentials: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration#credentials ApiGatewayIntegration#credentials}.
        :param integration_http_method: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration#integration_http_method ApiGatewayIntegration#integration_http_method}.
        :param passthrough_behavior: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration#passthrough_behavior ApiGatewayIntegration#passthrough_behavior}.
        :param request_parameters: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration#request_parameters ApiGatewayIntegration#request_parameters}.
        :param request_templates: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration#request_templates ApiGatewayIntegration#request_templates}.
        :param timeout_milliseconds: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration#timeout_milliseconds ApiGatewayIntegration#timeout_milliseconds}.
        :param tls_config: tls_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration#tls_config ApiGatewayIntegration#tls_config}
        :param uri: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration#uri ApiGatewayIntegration#uri}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(tls_config, dict):
            tls_config = ApiGatewayIntegrationTlsConfig(**tls_config)
        self._values: typing.Dict[str, typing.Any] = {
            "http_method": http_method,
            "resource_id": resource_id,
            "rest_api_id": rest_api_id,
            "type": type,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if cache_key_parameters is not None:
            self._values["cache_key_parameters"] = cache_key_parameters
        if cache_namespace is not None:
            self._values["cache_namespace"] = cache_namespace
        if connection_id is not None:
            self._values["connection_id"] = connection_id
        if connection_type is not None:
            self._values["connection_type"] = connection_type
        if content_handling is not None:
            self._values["content_handling"] = content_handling
        if credentials is not None:
            self._values["credentials"] = credentials
        if integration_http_method is not None:
            self._values["integration_http_method"] = integration_http_method
        if passthrough_behavior is not None:
            self._values["passthrough_behavior"] = passthrough_behavior
        if request_parameters is not None:
            self._values["request_parameters"] = request_parameters
        if request_templates is not None:
            self._values["request_templates"] = request_templates
        if timeout_milliseconds is not None:
            self._values["timeout_milliseconds"] = timeout_milliseconds
        if tls_config is not None:
            self._values["tls_config"] = tls_config
        if uri is not None:
            self._values["uri"] = uri

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
    def http_method(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration#http_method ApiGatewayIntegration#http_method}.'''
        result = self._values.get("http_method")
        assert result is not None, "Required property 'http_method' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def resource_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration#resource_id ApiGatewayIntegration#resource_id}.'''
        result = self._values.get("resource_id")
        assert result is not None, "Required property 'resource_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def rest_api_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration#rest_api_id ApiGatewayIntegration#rest_api_id}.'''
        result = self._values.get("rest_api_id")
        assert result is not None, "Required property 'rest_api_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration#type ApiGatewayIntegration#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cache_key_parameters(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration#cache_key_parameters ApiGatewayIntegration#cache_key_parameters}.'''
        result = self._values.get("cache_key_parameters")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def cache_namespace(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration#cache_namespace ApiGatewayIntegration#cache_namespace}.'''
        result = self._values.get("cache_namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def connection_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration#connection_id ApiGatewayIntegration#connection_id}.'''
        result = self._values.get("connection_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def connection_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration#connection_type ApiGatewayIntegration#connection_type}.'''
        result = self._values.get("connection_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def content_handling(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration#content_handling ApiGatewayIntegration#content_handling}.'''
        result = self._values.get("content_handling")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def credentials(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration#credentials ApiGatewayIntegration#credentials}.'''
        result = self._values.get("credentials")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def integration_http_method(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration#integration_http_method ApiGatewayIntegration#integration_http_method}.'''
        result = self._values.get("integration_http_method")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def passthrough_behavior(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration#passthrough_behavior ApiGatewayIntegration#passthrough_behavior}.'''
        result = self._values.get("passthrough_behavior")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def request_parameters(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration#request_parameters ApiGatewayIntegration#request_parameters}.'''
        result = self._values.get("request_parameters")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def request_templates(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration#request_templates ApiGatewayIntegration#request_templates}.'''
        result = self._values.get("request_templates")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def timeout_milliseconds(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration#timeout_milliseconds ApiGatewayIntegration#timeout_milliseconds}.'''
        result = self._values.get("timeout_milliseconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def tls_config(self) -> typing.Optional["ApiGatewayIntegrationTlsConfig"]:
        '''tls_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration#tls_config ApiGatewayIntegration#tls_config}
        '''
        result = self._values.get("tls_config")
        return typing.cast(typing.Optional["ApiGatewayIntegrationTlsConfig"], result)

    @builtins.property
    def uri(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration#uri ApiGatewayIntegration#uri}.'''
        result = self._values.get("uri")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApiGatewayIntegrationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ApiGatewayIntegrationResponse(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.apigateway.ApiGatewayIntegrationResponse",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration_response aws_api_gateway_integration_response}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        http_method: builtins.str,
        resource_id: builtins.str,
        rest_api_id: builtins.str,
        status_code: builtins.str,
        content_handling: typing.Optional[builtins.str] = None,
        response_parameters: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        response_templates: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        selection_pattern: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration_response aws_api_gateway_integration_response} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param http_method: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration_response#http_method ApiGatewayIntegrationResponse#http_method}.
        :param resource_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration_response#resource_id ApiGatewayIntegrationResponse#resource_id}.
        :param rest_api_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration_response#rest_api_id ApiGatewayIntegrationResponse#rest_api_id}.
        :param status_code: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration_response#status_code ApiGatewayIntegrationResponse#status_code}.
        :param content_handling: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration_response#content_handling ApiGatewayIntegrationResponse#content_handling}.
        :param response_parameters: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration_response#response_parameters ApiGatewayIntegrationResponse#response_parameters}.
        :param response_templates: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration_response#response_templates ApiGatewayIntegrationResponse#response_templates}.
        :param selection_pattern: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration_response#selection_pattern ApiGatewayIntegrationResponse#selection_pattern}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ApiGatewayIntegrationResponseConfig(
            http_method=http_method,
            resource_id=resource_id,
            rest_api_id=rest_api_id,
            status_code=status_code,
            content_handling=content_handling,
            response_parameters=response_parameters,
            response_templates=response_templates,
            selection_pattern=selection_pattern,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetContentHandling")
    def reset_content_handling(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetContentHandling", []))

    @jsii.member(jsii_name="resetResponseParameters")
    def reset_response_parameters(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResponseParameters", []))

    @jsii.member(jsii_name="resetResponseTemplates")
    def reset_response_templates(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResponseTemplates", []))

    @jsii.member(jsii_name="resetSelectionPattern")
    def reset_selection_pattern(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSelectionPattern", []))

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
    @jsii.member(jsii_name="contentHandlingInput")
    def content_handling_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "contentHandlingInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="httpMethodInput")
    def http_method_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "httpMethodInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceIdInput")
    def resource_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "resourceIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="responseParametersInput")
    def response_parameters_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "responseParametersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="responseTemplatesInput")
    def response_templates_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "responseTemplatesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restApiIdInput")
    def rest_api_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "restApiIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="selectionPatternInput")
    def selection_pattern_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "selectionPatternInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statusCodeInput")
    def status_code_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "statusCodeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="contentHandling")
    def content_handling(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "contentHandling"))

    @content_handling.setter
    def content_handling(self, value: builtins.str) -> None:
        jsii.set(self, "contentHandling", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="httpMethod")
    def http_method(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "httpMethod"))

    @http_method.setter
    def http_method(self, value: builtins.str) -> None:
        jsii.set(self, "httpMethod", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceId")
    def resource_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "resourceId"))

    @resource_id.setter
    def resource_id(self, value: builtins.str) -> None:
        jsii.set(self, "resourceId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="responseParameters")
    def response_parameters(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "responseParameters"))

    @response_parameters.setter
    def response_parameters(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "responseParameters", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="responseTemplates")
    def response_templates(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "responseTemplates"))

    @response_templates.setter
    def response_templates(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "responseTemplates", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restApiId")
    def rest_api_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "restApiId"))

    @rest_api_id.setter
    def rest_api_id(self, value: builtins.str) -> None:
        jsii.set(self, "restApiId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="selectionPattern")
    def selection_pattern(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "selectionPattern"))

    @selection_pattern.setter
    def selection_pattern(self, value: builtins.str) -> None:
        jsii.set(self, "selectionPattern", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statusCode")
    def status_code(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "statusCode"))

    @status_code.setter
    def status_code(self, value: builtins.str) -> None:
        jsii.set(self, "statusCode", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.apigateway.ApiGatewayIntegrationResponseConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "http_method": "httpMethod",
        "resource_id": "resourceId",
        "rest_api_id": "restApiId",
        "status_code": "statusCode",
        "content_handling": "contentHandling",
        "response_parameters": "responseParameters",
        "response_templates": "responseTemplates",
        "selection_pattern": "selectionPattern",
    },
)
class ApiGatewayIntegrationResponseConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        http_method: builtins.str,
        resource_id: builtins.str,
        rest_api_id: builtins.str,
        status_code: builtins.str,
        content_handling: typing.Optional[builtins.str] = None,
        response_parameters: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        response_templates: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        selection_pattern: typing.Optional[builtins.str] = None,
    ) -> None:
        '''API Gateway.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param http_method: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration_response#http_method ApiGatewayIntegrationResponse#http_method}.
        :param resource_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration_response#resource_id ApiGatewayIntegrationResponse#resource_id}.
        :param rest_api_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration_response#rest_api_id ApiGatewayIntegrationResponse#rest_api_id}.
        :param status_code: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration_response#status_code ApiGatewayIntegrationResponse#status_code}.
        :param content_handling: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration_response#content_handling ApiGatewayIntegrationResponse#content_handling}.
        :param response_parameters: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration_response#response_parameters ApiGatewayIntegrationResponse#response_parameters}.
        :param response_templates: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration_response#response_templates ApiGatewayIntegrationResponse#response_templates}.
        :param selection_pattern: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration_response#selection_pattern ApiGatewayIntegrationResponse#selection_pattern}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "http_method": http_method,
            "resource_id": resource_id,
            "rest_api_id": rest_api_id,
            "status_code": status_code,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if content_handling is not None:
            self._values["content_handling"] = content_handling
        if response_parameters is not None:
            self._values["response_parameters"] = response_parameters
        if response_templates is not None:
            self._values["response_templates"] = response_templates
        if selection_pattern is not None:
            self._values["selection_pattern"] = selection_pattern

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
    def http_method(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration_response#http_method ApiGatewayIntegrationResponse#http_method}.'''
        result = self._values.get("http_method")
        assert result is not None, "Required property 'http_method' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def resource_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration_response#resource_id ApiGatewayIntegrationResponse#resource_id}.'''
        result = self._values.get("resource_id")
        assert result is not None, "Required property 'resource_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def rest_api_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration_response#rest_api_id ApiGatewayIntegrationResponse#rest_api_id}.'''
        result = self._values.get("rest_api_id")
        assert result is not None, "Required property 'rest_api_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def status_code(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration_response#status_code ApiGatewayIntegrationResponse#status_code}.'''
        result = self._values.get("status_code")
        assert result is not None, "Required property 'status_code' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def content_handling(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration_response#content_handling ApiGatewayIntegrationResponse#content_handling}.'''
        result = self._values.get("content_handling")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def response_parameters(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration_response#response_parameters ApiGatewayIntegrationResponse#response_parameters}.'''
        result = self._values.get("response_parameters")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def response_templates(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration_response#response_templates ApiGatewayIntegrationResponse#response_templates}.'''
        result = self._values.get("response_templates")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def selection_pattern(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration_response#selection_pattern ApiGatewayIntegrationResponse#selection_pattern}.'''
        result = self._values.get("selection_pattern")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApiGatewayIntegrationResponseConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.apigateway.ApiGatewayIntegrationTlsConfig",
    jsii_struct_bases=[],
    name_mapping={"insecure_skip_verification": "insecureSkipVerification"},
)
class ApiGatewayIntegrationTlsConfig:
    def __init__(
        self,
        *,
        insecure_skip_verification: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param insecure_skip_verification: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration#insecure_skip_verification ApiGatewayIntegration#insecure_skip_verification}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if insecure_skip_verification is not None:
            self._values["insecure_skip_verification"] = insecure_skip_verification

    @builtins.property
    def insecure_skip_verification(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_integration#insecure_skip_verification ApiGatewayIntegration#insecure_skip_verification}.'''
        result = self._values.get("insecure_skip_verification")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApiGatewayIntegrationTlsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ApiGatewayIntegrationTlsConfigOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.apigateway.ApiGatewayIntegrationTlsConfigOutputReference",
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

    @jsii.member(jsii_name="resetInsecureSkipVerification")
    def reset_insecure_skip_verification(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInsecureSkipVerification", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="insecureSkipVerificationInput")
    def insecure_skip_verification_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "insecureSkipVerificationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="insecureSkipVerification")
    def insecure_skip_verification(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "insecureSkipVerification"))

    @insecure_skip_verification.setter
    def insecure_skip_verification(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "insecureSkipVerification", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ApiGatewayIntegrationTlsConfig]:
        return typing.cast(typing.Optional[ApiGatewayIntegrationTlsConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ApiGatewayIntegrationTlsConfig],
    ) -> None:
        jsii.set(self, "internalValue", value)


class ApiGatewayMethod(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.apigateway.ApiGatewayMethod",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method aws_api_gateway_method}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        authorization: builtins.str,
        http_method: builtins.str,
        resource_id: builtins.str,
        rest_api_id: builtins.str,
        api_key_required: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        authorization_scopes: typing.Optional[typing.Sequence[builtins.str]] = None,
        authorizer_id: typing.Optional[builtins.str] = None,
        operation_name: typing.Optional[builtins.str] = None,
        request_models: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        request_parameters: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.bool]]] = None,
        request_validator_id: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method aws_api_gateway_method} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param authorization: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method#authorization ApiGatewayMethod#authorization}.
        :param http_method: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method#http_method ApiGatewayMethod#http_method}.
        :param resource_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method#resource_id ApiGatewayMethod#resource_id}.
        :param rest_api_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method#rest_api_id ApiGatewayMethod#rest_api_id}.
        :param api_key_required: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method#api_key_required ApiGatewayMethod#api_key_required}.
        :param authorization_scopes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method#authorization_scopes ApiGatewayMethod#authorization_scopes}.
        :param authorizer_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method#authorizer_id ApiGatewayMethod#authorizer_id}.
        :param operation_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method#operation_name ApiGatewayMethod#operation_name}.
        :param request_models: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method#request_models ApiGatewayMethod#request_models}.
        :param request_parameters: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method#request_parameters ApiGatewayMethod#request_parameters}.
        :param request_validator_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method#request_validator_id ApiGatewayMethod#request_validator_id}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ApiGatewayMethodConfig(
            authorization=authorization,
            http_method=http_method,
            resource_id=resource_id,
            rest_api_id=rest_api_id,
            api_key_required=api_key_required,
            authorization_scopes=authorization_scopes,
            authorizer_id=authorizer_id,
            operation_name=operation_name,
            request_models=request_models,
            request_parameters=request_parameters,
            request_validator_id=request_validator_id,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetApiKeyRequired")
    def reset_api_key_required(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetApiKeyRequired", []))

    @jsii.member(jsii_name="resetAuthorizationScopes")
    def reset_authorization_scopes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthorizationScopes", []))

    @jsii.member(jsii_name="resetAuthorizerId")
    def reset_authorizer_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthorizerId", []))

    @jsii.member(jsii_name="resetOperationName")
    def reset_operation_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOperationName", []))

    @jsii.member(jsii_name="resetRequestModels")
    def reset_request_models(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequestModels", []))

    @jsii.member(jsii_name="resetRequestParameters")
    def reset_request_parameters(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequestParameters", []))

    @jsii.member(jsii_name="resetRequestValidatorId")
    def reset_request_validator_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequestValidatorId", []))

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
    @jsii.member(jsii_name="apiKeyRequiredInput")
    def api_key_required_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "apiKeyRequiredInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authorizationInput")
    def authorization_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "authorizationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authorizationScopesInput")
    def authorization_scopes_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "authorizationScopesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authorizerIdInput")
    def authorizer_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "authorizerIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="httpMethodInput")
    def http_method_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "httpMethodInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="operationNameInput")
    def operation_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "operationNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requestModelsInput")
    def request_models_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "requestModelsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requestParametersInput")
    def request_parameters_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.bool]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.bool]]], jsii.get(self, "requestParametersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requestValidatorIdInput")
    def request_validator_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "requestValidatorIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceIdInput")
    def resource_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "resourceIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restApiIdInput")
    def rest_api_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "restApiIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiKeyRequired")
    def api_key_required(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "apiKeyRequired"))

    @api_key_required.setter
    def api_key_required(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "apiKeyRequired", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authorization")
    def authorization(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authorization"))

    @authorization.setter
    def authorization(self, value: builtins.str) -> None:
        jsii.set(self, "authorization", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authorizationScopes")
    def authorization_scopes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "authorizationScopes"))

    @authorization_scopes.setter
    def authorization_scopes(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "authorizationScopes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authorizerId")
    def authorizer_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authorizerId"))

    @authorizer_id.setter
    def authorizer_id(self, value: builtins.str) -> None:
        jsii.set(self, "authorizerId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="httpMethod")
    def http_method(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "httpMethod"))

    @http_method.setter
    def http_method(self, value: builtins.str) -> None:
        jsii.set(self, "httpMethod", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="operationName")
    def operation_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "operationName"))

    @operation_name.setter
    def operation_name(self, value: builtins.str) -> None:
        jsii.set(self, "operationName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requestModels")
    def request_models(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "requestModels"))

    @request_models.setter
    def request_models(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "requestModels", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requestParameters")
    def request_parameters(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.bool]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.bool]], jsii.get(self, "requestParameters"))

    @request_parameters.setter
    def request_parameters(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.bool]],
    ) -> None:
        jsii.set(self, "requestParameters", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requestValidatorId")
    def request_validator_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "requestValidatorId"))

    @request_validator_id.setter
    def request_validator_id(self, value: builtins.str) -> None:
        jsii.set(self, "requestValidatorId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceId")
    def resource_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "resourceId"))

    @resource_id.setter
    def resource_id(self, value: builtins.str) -> None:
        jsii.set(self, "resourceId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restApiId")
    def rest_api_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "restApiId"))

    @rest_api_id.setter
    def rest_api_id(self, value: builtins.str) -> None:
        jsii.set(self, "restApiId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.apigateway.ApiGatewayMethodConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "authorization": "authorization",
        "http_method": "httpMethod",
        "resource_id": "resourceId",
        "rest_api_id": "restApiId",
        "api_key_required": "apiKeyRequired",
        "authorization_scopes": "authorizationScopes",
        "authorizer_id": "authorizerId",
        "operation_name": "operationName",
        "request_models": "requestModels",
        "request_parameters": "requestParameters",
        "request_validator_id": "requestValidatorId",
    },
)
class ApiGatewayMethodConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        authorization: builtins.str,
        http_method: builtins.str,
        resource_id: builtins.str,
        rest_api_id: builtins.str,
        api_key_required: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        authorization_scopes: typing.Optional[typing.Sequence[builtins.str]] = None,
        authorizer_id: typing.Optional[builtins.str] = None,
        operation_name: typing.Optional[builtins.str] = None,
        request_models: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        request_parameters: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.bool]]] = None,
        request_validator_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''API Gateway.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param authorization: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method#authorization ApiGatewayMethod#authorization}.
        :param http_method: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method#http_method ApiGatewayMethod#http_method}.
        :param resource_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method#resource_id ApiGatewayMethod#resource_id}.
        :param rest_api_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method#rest_api_id ApiGatewayMethod#rest_api_id}.
        :param api_key_required: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method#api_key_required ApiGatewayMethod#api_key_required}.
        :param authorization_scopes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method#authorization_scopes ApiGatewayMethod#authorization_scopes}.
        :param authorizer_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method#authorizer_id ApiGatewayMethod#authorizer_id}.
        :param operation_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method#operation_name ApiGatewayMethod#operation_name}.
        :param request_models: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method#request_models ApiGatewayMethod#request_models}.
        :param request_parameters: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method#request_parameters ApiGatewayMethod#request_parameters}.
        :param request_validator_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method#request_validator_id ApiGatewayMethod#request_validator_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "authorization": authorization,
            "http_method": http_method,
            "resource_id": resource_id,
            "rest_api_id": rest_api_id,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if api_key_required is not None:
            self._values["api_key_required"] = api_key_required
        if authorization_scopes is not None:
            self._values["authorization_scopes"] = authorization_scopes
        if authorizer_id is not None:
            self._values["authorizer_id"] = authorizer_id
        if operation_name is not None:
            self._values["operation_name"] = operation_name
        if request_models is not None:
            self._values["request_models"] = request_models
        if request_parameters is not None:
            self._values["request_parameters"] = request_parameters
        if request_validator_id is not None:
            self._values["request_validator_id"] = request_validator_id

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
    def authorization(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method#authorization ApiGatewayMethod#authorization}.'''
        result = self._values.get("authorization")
        assert result is not None, "Required property 'authorization' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def http_method(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method#http_method ApiGatewayMethod#http_method}.'''
        result = self._values.get("http_method")
        assert result is not None, "Required property 'http_method' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def resource_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method#resource_id ApiGatewayMethod#resource_id}.'''
        result = self._values.get("resource_id")
        assert result is not None, "Required property 'resource_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def rest_api_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method#rest_api_id ApiGatewayMethod#rest_api_id}.'''
        result = self._values.get("rest_api_id")
        assert result is not None, "Required property 'rest_api_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def api_key_required(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method#api_key_required ApiGatewayMethod#api_key_required}.'''
        result = self._values.get("api_key_required")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def authorization_scopes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method#authorization_scopes ApiGatewayMethod#authorization_scopes}.'''
        result = self._values.get("authorization_scopes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def authorizer_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method#authorizer_id ApiGatewayMethod#authorizer_id}.'''
        result = self._values.get("authorizer_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def operation_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method#operation_name ApiGatewayMethod#operation_name}.'''
        result = self._values.get("operation_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def request_models(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method#request_models ApiGatewayMethod#request_models}.'''
        result = self._values.get("request_models")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def request_parameters(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.bool]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method#request_parameters ApiGatewayMethod#request_parameters}.'''
        result = self._values.get("request_parameters")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.bool]]], result)

    @builtins.property
    def request_validator_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method#request_validator_id ApiGatewayMethod#request_validator_id}.'''
        result = self._values.get("request_validator_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApiGatewayMethodConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ApiGatewayMethodResponse(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.apigateway.ApiGatewayMethodResponse",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method_response aws_api_gateway_method_response}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        http_method: builtins.str,
        resource_id: builtins.str,
        rest_api_id: builtins.str,
        status_code: builtins.str,
        response_models: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        response_parameters: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.bool]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method_response aws_api_gateway_method_response} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param http_method: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method_response#http_method ApiGatewayMethodResponse#http_method}.
        :param resource_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method_response#resource_id ApiGatewayMethodResponse#resource_id}.
        :param rest_api_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method_response#rest_api_id ApiGatewayMethodResponse#rest_api_id}.
        :param status_code: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method_response#status_code ApiGatewayMethodResponse#status_code}.
        :param response_models: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method_response#response_models ApiGatewayMethodResponse#response_models}.
        :param response_parameters: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method_response#response_parameters ApiGatewayMethodResponse#response_parameters}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ApiGatewayMethodResponseConfig(
            http_method=http_method,
            resource_id=resource_id,
            rest_api_id=rest_api_id,
            status_code=status_code,
            response_models=response_models,
            response_parameters=response_parameters,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetResponseModels")
    def reset_response_models(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResponseModels", []))

    @jsii.member(jsii_name="resetResponseParameters")
    def reset_response_parameters(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResponseParameters", []))

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
    @jsii.member(jsii_name="httpMethodInput")
    def http_method_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "httpMethodInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceIdInput")
    def resource_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "resourceIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="responseModelsInput")
    def response_models_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "responseModelsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="responseParametersInput")
    def response_parameters_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.bool]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.bool]]], jsii.get(self, "responseParametersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restApiIdInput")
    def rest_api_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "restApiIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statusCodeInput")
    def status_code_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "statusCodeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="httpMethod")
    def http_method(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "httpMethod"))

    @http_method.setter
    def http_method(self, value: builtins.str) -> None:
        jsii.set(self, "httpMethod", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceId")
    def resource_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "resourceId"))

    @resource_id.setter
    def resource_id(self, value: builtins.str) -> None:
        jsii.set(self, "resourceId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="responseModels")
    def response_models(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "responseModels"))

    @response_models.setter
    def response_models(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "responseModels", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="responseParameters")
    def response_parameters(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.bool]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.bool]], jsii.get(self, "responseParameters"))

    @response_parameters.setter
    def response_parameters(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.bool]],
    ) -> None:
        jsii.set(self, "responseParameters", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restApiId")
    def rest_api_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "restApiId"))

    @rest_api_id.setter
    def rest_api_id(self, value: builtins.str) -> None:
        jsii.set(self, "restApiId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statusCode")
    def status_code(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "statusCode"))

    @status_code.setter
    def status_code(self, value: builtins.str) -> None:
        jsii.set(self, "statusCode", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.apigateway.ApiGatewayMethodResponseConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "http_method": "httpMethod",
        "resource_id": "resourceId",
        "rest_api_id": "restApiId",
        "status_code": "statusCode",
        "response_models": "responseModels",
        "response_parameters": "responseParameters",
    },
)
class ApiGatewayMethodResponseConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        http_method: builtins.str,
        resource_id: builtins.str,
        rest_api_id: builtins.str,
        status_code: builtins.str,
        response_models: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        response_parameters: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.bool]]] = None,
    ) -> None:
        '''API Gateway.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param http_method: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method_response#http_method ApiGatewayMethodResponse#http_method}.
        :param resource_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method_response#resource_id ApiGatewayMethodResponse#resource_id}.
        :param rest_api_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method_response#rest_api_id ApiGatewayMethodResponse#rest_api_id}.
        :param status_code: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method_response#status_code ApiGatewayMethodResponse#status_code}.
        :param response_models: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method_response#response_models ApiGatewayMethodResponse#response_models}.
        :param response_parameters: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method_response#response_parameters ApiGatewayMethodResponse#response_parameters}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "http_method": http_method,
            "resource_id": resource_id,
            "rest_api_id": rest_api_id,
            "status_code": status_code,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if response_models is not None:
            self._values["response_models"] = response_models
        if response_parameters is not None:
            self._values["response_parameters"] = response_parameters

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
    def http_method(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method_response#http_method ApiGatewayMethodResponse#http_method}.'''
        result = self._values.get("http_method")
        assert result is not None, "Required property 'http_method' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def resource_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method_response#resource_id ApiGatewayMethodResponse#resource_id}.'''
        result = self._values.get("resource_id")
        assert result is not None, "Required property 'resource_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def rest_api_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method_response#rest_api_id ApiGatewayMethodResponse#rest_api_id}.'''
        result = self._values.get("rest_api_id")
        assert result is not None, "Required property 'rest_api_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def status_code(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method_response#status_code ApiGatewayMethodResponse#status_code}.'''
        result = self._values.get("status_code")
        assert result is not None, "Required property 'status_code' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def response_models(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method_response#response_models ApiGatewayMethodResponse#response_models}.'''
        result = self._values.get("response_models")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def response_parameters(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.bool]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method_response#response_parameters ApiGatewayMethodResponse#response_parameters}.'''
        result = self._values.get("response_parameters")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.bool]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApiGatewayMethodResponseConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ApiGatewayMethodSettings(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.apigateway.ApiGatewayMethodSettings",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method_settings aws_api_gateway_method_settings}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        method_path: builtins.str,
        rest_api_id: builtins.str,
        settings: "ApiGatewayMethodSettingsSettings",
        stage_name: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method_settings aws_api_gateway_method_settings} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param method_path: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method_settings#method_path ApiGatewayMethodSettings#method_path}.
        :param rest_api_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method_settings#rest_api_id ApiGatewayMethodSettings#rest_api_id}.
        :param settings: settings block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method_settings#settings ApiGatewayMethodSettings#settings}
        :param stage_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method_settings#stage_name ApiGatewayMethodSettings#stage_name}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ApiGatewayMethodSettingsConfig(
            method_path=method_path,
            rest_api_id=rest_api_id,
            settings=settings,
            stage_name=stage_name,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putSettings")
    def put_settings(
        self,
        *,
        cache_data_encrypted: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        cache_ttl_in_seconds: typing.Optional[jsii.Number] = None,
        caching_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        data_trace_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        logging_level: typing.Optional[builtins.str] = None,
        metrics_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        require_authorization_for_cache_control: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        throttling_burst_limit: typing.Optional[jsii.Number] = None,
        throttling_rate_limit: typing.Optional[jsii.Number] = None,
        unauthorized_cache_control_header_strategy: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param cache_data_encrypted: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method_settings#cache_data_encrypted ApiGatewayMethodSettings#cache_data_encrypted}.
        :param cache_ttl_in_seconds: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method_settings#cache_ttl_in_seconds ApiGatewayMethodSettings#cache_ttl_in_seconds}.
        :param caching_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method_settings#caching_enabled ApiGatewayMethodSettings#caching_enabled}.
        :param data_trace_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method_settings#data_trace_enabled ApiGatewayMethodSettings#data_trace_enabled}.
        :param logging_level: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method_settings#logging_level ApiGatewayMethodSettings#logging_level}.
        :param metrics_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method_settings#metrics_enabled ApiGatewayMethodSettings#metrics_enabled}.
        :param require_authorization_for_cache_control: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method_settings#require_authorization_for_cache_control ApiGatewayMethodSettings#require_authorization_for_cache_control}.
        :param throttling_burst_limit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method_settings#throttling_burst_limit ApiGatewayMethodSettings#throttling_burst_limit}.
        :param throttling_rate_limit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method_settings#throttling_rate_limit ApiGatewayMethodSettings#throttling_rate_limit}.
        :param unauthorized_cache_control_header_strategy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method_settings#unauthorized_cache_control_header_strategy ApiGatewayMethodSettings#unauthorized_cache_control_header_strategy}.
        '''
        value = ApiGatewayMethodSettingsSettings(
            cache_data_encrypted=cache_data_encrypted,
            cache_ttl_in_seconds=cache_ttl_in_seconds,
            caching_enabled=caching_enabled,
            data_trace_enabled=data_trace_enabled,
            logging_level=logging_level,
            metrics_enabled=metrics_enabled,
            require_authorization_for_cache_control=require_authorization_for_cache_control,
            throttling_burst_limit=throttling_burst_limit,
            throttling_rate_limit=throttling_rate_limit,
            unauthorized_cache_control_header_strategy=unauthorized_cache_control_header_strategy,
        )

        return typing.cast(None, jsii.invoke(self, "putSettings", [value]))

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
    @jsii.member(jsii_name="settings")
    def settings(self) -> "ApiGatewayMethodSettingsSettingsOutputReference":
        return typing.cast("ApiGatewayMethodSettingsSettingsOutputReference", jsii.get(self, "settings"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="methodPathInput")
    def method_path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "methodPathInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restApiIdInput")
    def rest_api_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "restApiIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="settingsInput")
    def settings_input(self) -> typing.Optional["ApiGatewayMethodSettingsSettings"]:
        return typing.cast(typing.Optional["ApiGatewayMethodSettingsSettings"], jsii.get(self, "settingsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stageNameInput")
    def stage_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stageNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="methodPath")
    def method_path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "methodPath"))

    @method_path.setter
    def method_path(self, value: builtins.str) -> None:
        jsii.set(self, "methodPath", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restApiId")
    def rest_api_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "restApiId"))

    @rest_api_id.setter
    def rest_api_id(self, value: builtins.str) -> None:
        jsii.set(self, "restApiId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stageName")
    def stage_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "stageName"))

    @stage_name.setter
    def stage_name(self, value: builtins.str) -> None:
        jsii.set(self, "stageName", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.apigateway.ApiGatewayMethodSettingsConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "method_path": "methodPath",
        "rest_api_id": "restApiId",
        "settings": "settings",
        "stage_name": "stageName",
    },
)
class ApiGatewayMethodSettingsConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        method_path: builtins.str,
        rest_api_id: builtins.str,
        settings: "ApiGatewayMethodSettingsSettings",
        stage_name: builtins.str,
    ) -> None:
        '''API Gateway.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param method_path: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method_settings#method_path ApiGatewayMethodSettings#method_path}.
        :param rest_api_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method_settings#rest_api_id ApiGatewayMethodSettings#rest_api_id}.
        :param settings: settings block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method_settings#settings ApiGatewayMethodSettings#settings}
        :param stage_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method_settings#stage_name ApiGatewayMethodSettings#stage_name}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(settings, dict):
            settings = ApiGatewayMethodSettingsSettings(**settings)
        self._values: typing.Dict[str, typing.Any] = {
            "method_path": method_path,
            "rest_api_id": rest_api_id,
            "settings": settings,
            "stage_name": stage_name,
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
    def method_path(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method_settings#method_path ApiGatewayMethodSettings#method_path}.'''
        result = self._values.get("method_path")
        assert result is not None, "Required property 'method_path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def rest_api_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method_settings#rest_api_id ApiGatewayMethodSettings#rest_api_id}.'''
        result = self._values.get("rest_api_id")
        assert result is not None, "Required property 'rest_api_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def settings(self) -> "ApiGatewayMethodSettingsSettings":
        '''settings block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method_settings#settings ApiGatewayMethodSettings#settings}
        '''
        result = self._values.get("settings")
        assert result is not None, "Required property 'settings' is missing"
        return typing.cast("ApiGatewayMethodSettingsSettings", result)

    @builtins.property
    def stage_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method_settings#stage_name ApiGatewayMethodSettings#stage_name}.'''
        result = self._values.get("stage_name")
        assert result is not None, "Required property 'stage_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApiGatewayMethodSettingsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.apigateway.ApiGatewayMethodSettingsSettings",
    jsii_struct_bases=[],
    name_mapping={
        "cache_data_encrypted": "cacheDataEncrypted",
        "cache_ttl_in_seconds": "cacheTtlInSeconds",
        "caching_enabled": "cachingEnabled",
        "data_trace_enabled": "dataTraceEnabled",
        "logging_level": "loggingLevel",
        "metrics_enabled": "metricsEnabled",
        "require_authorization_for_cache_control": "requireAuthorizationForCacheControl",
        "throttling_burst_limit": "throttlingBurstLimit",
        "throttling_rate_limit": "throttlingRateLimit",
        "unauthorized_cache_control_header_strategy": "unauthorizedCacheControlHeaderStrategy",
    },
)
class ApiGatewayMethodSettingsSettings:
    def __init__(
        self,
        *,
        cache_data_encrypted: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        cache_ttl_in_seconds: typing.Optional[jsii.Number] = None,
        caching_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        data_trace_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        logging_level: typing.Optional[builtins.str] = None,
        metrics_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        require_authorization_for_cache_control: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        throttling_burst_limit: typing.Optional[jsii.Number] = None,
        throttling_rate_limit: typing.Optional[jsii.Number] = None,
        unauthorized_cache_control_header_strategy: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param cache_data_encrypted: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method_settings#cache_data_encrypted ApiGatewayMethodSettings#cache_data_encrypted}.
        :param cache_ttl_in_seconds: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method_settings#cache_ttl_in_seconds ApiGatewayMethodSettings#cache_ttl_in_seconds}.
        :param caching_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method_settings#caching_enabled ApiGatewayMethodSettings#caching_enabled}.
        :param data_trace_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method_settings#data_trace_enabled ApiGatewayMethodSettings#data_trace_enabled}.
        :param logging_level: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method_settings#logging_level ApiGatewayMethodSettings#logging_level}.
        :param metrics_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method_settings#metrics_enabled ApiGatewayMethodSettings#metrics_enabled}.
        :param require_authorization_for_cache_control: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method_settings#require_authorization_for_cache_control ApiGatewayMethodSettings#require_authorization_for_cache_control}.
        :param throttling_burst_limit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method_settings#throttling_burst_limit ApiGatewayMethodSettings#throttling_burst_limit}.
        :param throttling_rate_limit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method_settings#throttling_rate_limit ApiGatewayMethodSettings#throttling_rate_limit}.
        :param unauthorized_cache_control_header_strategy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method_settings#unauthorized_cache_control_header_strategy ApiGatewayMethodSettings#unauthorized_cache_control_header_strategy}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if cache_data_encrypted is not None:
            self._values["cache_data_encrypted"] = cache_data_encrypted
        if cache_ttl_in_seconds is not None:
            self._values["cache_ttl_in_seconds"] = cache_ttl_in_seconds
        if caching_enabled is not None:
            self._values["caching_enabled"] = caching_enabled
        if data_trace_enabled is not None:
            self._values["data_trace_enabled"] = data_trace_enabled
        if logging_level is not None:
            self._values["logging_level"] = logging_level
        if metrics_enabled is not None:
            self._values["metrics_enabled"] = metrics_enabled
        if require_authorization_for_cache_control is not None:
            self._values["require_authorization_for_cache_control"] = require_authorization_for_cache_control
        if throttling_burst_limit is not None:
            self._values["throttling_burst_limit"] = throttling_burst_limit
        if throttling_rate_limit is not None:
            self._values["throttling_rate_limit"] = throttling_rate_limit
        if unauthorized_cache_control_header_strategy is not None:
            self._values["unauthorized_cache_control_header_strategy"] = unauthorized_cache_control_header_strategy

    @builtins.property
    def cache_data_encrypted(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method_settings#cache_data_encrypted ApiGatewayMethodSettings#cache_data_encrypted}.'''
        result = self._values.get("cache_data_encrypted")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def cache_ttl_in_seconds(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method_settings#cache_ttl_in_seconds ApiGatewayMethodSettings#cache_ttl_in_seconds}.'''
        result = self._values.get("cache_ttl_in_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def caching_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method_settings#caching_enabled ApiGatewayMethodSettings#caching_enabled}.'''
        result = self._values.get("caching_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def data_trace_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method_settings#data_trace_enabled ApiGatewayMethodSettings#data_trace_enabled}.'''
        result = self._values.get("data_trace_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def logging_level(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method_settings#logging_level ApiGatewayMethodSettings#logging_level}.'''
        result = self._values.get("logging_level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def metrics_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method_settings#metrics_enabled ApiGatewayMethodSettings#metrics_enabled}.'''
        result = self._values.get("metrics_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def require_authorization_for_cache_control(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method_settings#require_authorization_for_cache_control ApiGatewayMethodSettings#require_authorization_for_cache_control}.'''
        result = self._values.get("require_authorization_for_cache_control")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def throttling_burst_limit(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method_settings#throttling_burst_limit ApiGatewayMethodSettings#throttling_burst_limit}.'''
        result = self._values.get("throttling_burst_limit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def throttling_rate_limit(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method_settings#throttling_rate_limit ApiGatewayMethodSettings#throttling_rate_limit}.'''
        result = self._values.get("throttling_rate_limit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def unauthorized_cache_control_header_strategy(
        self,
    ) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_method_settings#unauthorized_cache_control_header_strategy ApiGatewayMethodSettings#unauthorized_cache_control_header_strategy}.'''
        result = self._values.get("unauthorized_cache_control_header_strategy")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApiGatewayMethodSettingsSettings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ApiGatewayMethodSettingsSettingsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.apigateway.ApiGatewayMethodSettingsSettingsOutputReference",
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

    @jsii.member(jsii_name="resetCacheDataEncrypted")
    def reset_cache_data_encrypted(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCacheDataEncrypted", []))

    @jsii.member(jsii_name="resetCacheTtlInSeconds")
    def reset_cache_ttl_in_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCacheTtlInSeconds", []))

    @jsii.member(jsii_name="resetCachingEnabled")
    def reset_caching_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCachingEnabled", []))

    @jsii.member(jsii_name="resetDataTraceEnabled")
    def reset_data_trace_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDataTraceEnabled", []))

    @jsii.member(jsii_name="resetLoggingLevel")
    def reset_logging_level(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLoggingLevel", []))

    @jsii.member(jsii_name="resetMetricsEnabled")
    def reset_metrics_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMetricsEnabled", []))

    @jsii.member(jsii_name="resetRequireAuthorizationForCacheControl")
    def reset_require_authorization_for_cache_control(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequireAuthorizationForCacheControl", []))

    @jsii.member(jsii_name="resetThrottlingBurstLimit")
    def reset_throttling_burst_limit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetThrottlingBurstLimit", []))

    @jsii.member(jsii_name="resetThrottlingRateLimit")
    def reset_throttling_rate_limit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetThrottlingRateLimit", []))

    @jsii.member(jsii_name="resetUnauthorizedCacheControlHeaderStrategy")
    def reset_unauthorized_cache_control_header_strategy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUnauthorizedCacheControlHeaderStrategy", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cacheDataEncryptedInput")
    def cache_data_encrypted_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "cacheDataEncryptedInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cacheTtlInSecondsInput")
    def cache_ttl_in_seconds_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "cacheTtlInSecondsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cachingEnabledInput")
    def caching_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "cachingEnabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dataTraceEnabledInput")
    def data_trace_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "dataTraceEnabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="loggingLevelInput")
    def logging_level_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "loggingLevelInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="metricsEnabledInput")
    def metrics_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "metricsEnabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requireAuthorizationForCacheControlInput")
    def require_authorization_for_cache_control_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "requireAuthorizationForCacheControlInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="throttlingBurstLimitInput")
    def throttling_burst_limit_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "throttlingBurstLimitInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="throttlingRateLimitInput")
    def throttling_rate_limit_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "throttlingRateLimitInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="unauthorizedCacheControlHeaderStrategyInput")
    def unauthorized_cache_control_header_strategy_input(
        self,
    ) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "unauthorizedCacheControlHeaderStrategyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cacheDataEncrypted")
    def cache_data_encrypted(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "cacheDataEncrypted"))

    @cache_data_encrypted.setter
    def cache_data_encrypted(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "cacheDataEncrypted", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cacheTtlInSeconds")
    def cache_ttl_in_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "cacheTtlInSeconds"))

    @cache_ttl_in_seconds.setter
    def cache_ttl_in_seconds(self, value: jsii.Number) -> None:
        jsii.set(self, "cacheTtlInSeconds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cachingEnabled")
    def caching_enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "cachingEnabled"))

    @caching_enabled.setter
    def caching_enabled(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "cachingEnabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dataTraceEnabled")
    def data_trace_enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "dataTraceEnabled"))

    @data_trace_enabled.setter
    def data_trace_enabled(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "dataTraceEnabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="loggingLevel")
    def logging_level(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "loggingLevel"))

    @logging_level.setter
    def logging_level(self, value: builtins.str) -> None:
        jsii.set(self, "loggingLevel", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="metricsEnabled")
    def metrics_enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "metricsEnabled"))

    @metrics_enabled.setter
    def metrics_enabled(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "metricsEnabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requireAuthorizationForCacheControl")
    def require_authorization_for_cache_control(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "requireAuthorizationForCacheControl"))

    @require_authorization_for_cache_control.setter
    def require_authorization_for_cache_control(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "requireAuthorizationForCacheControl", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="throttlingBurstLimit")
    def throttling_burst_limit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "throttlingBurstLimit"))

    @throttling_burst_limit.setter
    def throttling_burst_limit(self, value: jsii.Number) -> None:
        jsii.set(self, "throttlingBurstLimit", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="throttlingRateLimit")
    def throttling_rate_limit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "throttlingRateLimit"))

    @throttling_rate_limit.setter
    def throttling_rate_limit(self, value: jsii.Number) -> None:
        jsii.set(self, "throttlingRateLimit", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="unauthorizedCacheControlHeaderStrategy")
    def unauthorized_cache_control_header_strategy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "unauthorizedCacheControlHeaderStrategy"))

    @unauthorized_cache_control_header_strategy.setter
    def unauthorized_cache_control_header_strategy(self, value: builtins.str) -> None:
        jsii.set(self, "unauthorizedCacheControlHeaderStrategy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ApiGatewayMethodSettingsSettings]:
        return typing.cast(typing.Optional[ApiGatewayMethodSettingsSettings], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ApiGatewayMethodSettingsSettings],
    ) -> None:
        jsii.set(self, "internalValue", value)


class ApiGatewayModel(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.apigateway.ApiGatewayModel",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_model aws_api_gateway_model}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        content_type: builtins.str,
        name: builtins.str,
        rest_api_id: builtins.str,
        description: typing.Optional[builtins.str] = None,
        schema: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_model aws_api_gateway_model} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param content_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_model#content_type ApiGatewayModel#content_type}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_model#name ApiGatewayModel#name}.
        :param rest_api_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_model#rest_api_id ApiGatewayModel#rest_api_id}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_model#description ApiGatewayModel#description}.
        :param schema: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_model#schema ApiGatewayModel#schema}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ApiGatewayModelConfig(
            content_type=content_type,
            name=name,
            rest_api_id=rest_api_id,
            description=description,
            schema=schema,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetSchema")
    def reset_schema(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSchema", []))

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
    @jsii.member(jsii_name="contentTypeInput")
    def content_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "contentTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restApiIdInput")
    def rest_api_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "restApiIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="schemaInput")
    def schema_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "schemaInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="contentType")
    def content_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "contentType"))

    @content_type.setter
    def content_type(self, value: builtins.str) -> None:
        jsii.set(self, "contentType", value)

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
    @jsii.member(jsii_name="restApiId")
    def rest_api_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "restApiId"))

    @rest_api_id.setter
    def rest_api_id(self, value: builtins.str) -> None:
        jsii.set(self, "restApiId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="schema")
    def schema(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "schema"))

    @schema.setter
    def schema(self, value: builtins.str) -> None:
        jsii.set(self, "schema", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.apigateway.ApiGatewayModelConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "content_type": "contentType",
        "name": "name",
        "rest_api_id": "restApiId",
        "description": "description",
        "schema": "schema",
    },
)
class ApiGatewayModelConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        content_type: builtins.str,
        name: builtins.str,
        rest_api_id: builtins.str,
        description: typing.Optional[builtins.str] = None,
        schema: typing.Optional[builtins.str] = None,
    ) -> None:
        '''API Gateway.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param content_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_model#content_type ApiGatewayModel#content_type}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_model#name ApiGatewayModel#name}.
        :param rest_api_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_model#rest_api_id ApiGatewayModel#rest_api_id}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_model#description ApiGatewayModel#description}.
        :param schema: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_model#schema ApiGatewayModel#schema}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "content_type": content_type,
            "name": name,
            "rest_api_id": rest_api_id,
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
        if schema is not None:
            self._values["schema"] = schema

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
    def content_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_model#content_type ApiGatewayModel#content_type}.'''
        result = self._values.get("content_type")
        assert result is not None, "Required property 'content_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_model#name ApiGatewayModel#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def rest_api_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_model#rest_api_id ApiGatewayModel#rest_api_id}.'''
        result = self._values.get("rest_api_id")
        assert result is not None, "Required property 'rest_api_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_model#description ApiGatewayModel#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def schema(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_model#schema ApiGatewayModel#schema}.'''
        result = self._values.get("schema")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApiGatewayModelConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ApiGatewayRequestValidator(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.apigateway.ApiGatewayRequestValidator",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_request_validator aws_api_gateway_request_validator}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        rest_api_id: builtins.str,
        validate_request_body: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        validate_request_parameters: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_request_validator aws_api_gateway_request_validator} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_request_validator#name ApiGatewayRequestValidator#name}.
        :param rest_api_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_request_validator#rest_api_id ApiGatewayRequestValidator#rest_api_id}.
        :param validate_request_body: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_request_validator#validate_request_body ApiGatewayRequestValidator#validate_request_body}.
        :param validate_request_parameters: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_request_validator#validate_request_parameters ApiGatewayRequestValidator#validate_request_parameters}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ApiGatewayRequestValidatorConfig(
            name=name,
            rest_api_id=rest_api_id,
            validate_request_body=validate_request_body,
            validate_request_parameters=validate_request_parameters,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetValidateRequestBody")
    def reset_validate_request_body(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValidateRequestBody", []))

    @jsii.member(jsii_name="resetValidateRequestParameters")
    def reset_validate_request_parameters(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValidateRequestParameters", []))

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
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restApiIdInput")
    def rest_api_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "restApiIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="validateRequestBodyInput")
    def validate_request_body_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "validateRequestBodyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="validateRequestParametersInput")
    def validate_request_parameters_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "validateRequestParametersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restApiId")
    def rest_api_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "restApiId"))

    @rest_api_id.setter
    def rest_api_id(self, value: builtins.str) -> None:
        jsii.set(self, "restApiId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="validateRequestBody")
    def validate_request_body(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "validateRequestBody"))

    @validate_request_body.setter
    def validate_request_body(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "validateRequestBody", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="validateRequestParameters")
    def validate_request_parameters(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "validateRequestParameters"))

    @validate_request_parameters.setter
    def validate_request_parameters(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "validateRequestParameters", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.apigateway.ApiGatewayRequestValidatorConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "rest_api_id": "restApiId",
        "validate_request_body": "validateRequestBody",
        "validate_request_parameters": "validateRequestParameters",
    },
)
class ApiGatewayRequestValidatorConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        rest_api_id: builtins.str,
        validate_request_body: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        validate_request_parameters: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''API Gateway.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_request_validator#name ApiGatewayRequestValidator#name}.
        :param rest_api_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_request_validator#rest_api_id ApiGatewayRequestValidator#rest_api_id}.
        :param validate_request_body: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_request_validator#validate_request_body ApiGatewayRequestValidator#validate_request_body}.
        :param validate_request_parameters: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_request_validator#validate_request_parameters ApiGatewayRequestValidator#validate_request_parameters}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "rest_api_id": rest_api_id,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if validate_request_body is not None:
            self._values["validate_request_body"] = validate_request_body
        if validate_request_parameters is not None:
            self._values["validate_request_parameters"] = validate_request_parameters

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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_request_validator#name ApiGatewayRequestValidator#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def rest_api_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_request_validator#rest_api_id ApiGatewayRequestValidator#rest_api_id}.'''
        result = self._values.get("rest_api_id")
        assert result is not None, "Required property 'rest_api_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def validate_request_body(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_request_validator#validate_request_body ApiGatewayRequestValidator#validate_request_body}.'''
        result = self._values.get("validate_request_body")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def validate_request_parameters(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_request_validator#validate_request_parameters ApiGatewayRequestValidator#validate_request_parameters}.'''
        result = self._values.get("validate_request_parameters")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApiGatewayRequestValidatorConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ApiGatewayResource(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.apigateway.ApiGatewayResource",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_resource aws_api_gateway_resource}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        parent_id: builtins.str,
        path_part: builtins.str,
        rest_api_id: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_resource aws_api_gateway_resource} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param parent_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_resource#parent_id ApiGatewayResource#parent_id}.
        :param path_part: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_resource#path_part ApiGatewayResource#path_part}.
        :param rest_api_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_resource#rest_api_id ApiGatewayResource#rest_api_id}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ApiGatewayResourceConfig(
            parent_id=parent_id,
            path_part=path_part,
            rest_api_id=rest_api_id,
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
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "path"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parentIdInput")
    def parent_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "parentIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pathPartInput")
    def path_part_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pathPartInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restApiIdInput")
    def rest_api_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "restApiIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parentId")
    def parent_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "parentId"))

    @parent_id.setter
    def parent_id(self, value: builtins.str) -> None:
        jsii.set(self, "parentId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pathPart")
    def path_part(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pathPart"))

    @path_part.setter
    def path_part(self, value: builtins.str) -> None:
        jsii.set(self, "pathPart", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restApiId")
    def rest_api_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "restApiId"))

    @rest_api_id.setter
    def rest_api_id(self, value: builtins.str) -> None:
        jsii.set(self, "restApiId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.apigateway.ApiGatewayResourceConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "parent_id": "parentId",
        "path_part": "pathPart",
        "rest_api_id": "restApiId",
    },
)
class ApiGatewayResourceConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        parent_id: builtins.str,
        path_part: builtins.str,
        rest_api_id: builtins.str,
    ) -> None:
        '''API Gateway.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param parent_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_resource#parent_id ApiGatewayResource#parent_id}.
        :param path_part: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_resource#path_part ApiGatewayResource#path_part}.
        :param rest_api_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_resource#rest_api_id ApiGatewayResource#rest_api_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "parent_id": parent_id,
            "path_part": path_part,
            "rest_api_id": rest_api_id,
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
    def parent_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_resource#parent_id ApiGatewayResource#parent_id}.'''
        result = self._values.get("parent_id")
        assert result is not None, "Required property 'parent_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def path_part(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_resource#path_part ApiGatewayResource#path_part}.'''
        result = self._values.get("path_part")
        assert result is not None, "Required property 'path_part' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def rest_api_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_resource#rest_api_id ApiGatewayResource#rest_api_id}.'''
        result = self._values.get("rest_api_id")
        assert result is not None, "Required property 'rest_api_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApiGatewayResourceConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ApiGatewayRestApi(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.apigateway.ApiGatewayRestApi",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_rest_api aws_api_gateway_rest_api}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        api_key_source: typing.Optional[builtins.str] = None,
        binary_media_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        body: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        disable_execute_api_endpoint: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        endpoint_configuration: typing.Optional["ApiGatewayRestApiEndpointConfiguration"] = None,
        minimum_compression_size: typing.Optional[jsii.Number] = None,
        parameters: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        policy: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_rest_api aws_api_gateway_rest_api} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_rest_api#name ApiGatewayRestApi#name}.
        :param api_key_source: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_rest_api#api_key_source ApiGatewayRestApi#api_key_source}.
        :param binary_media_types: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_rest_api#binary_media_types ApiGatewayRestApi#binary_media_types}.
        :param body: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_rest_api#body ApiGatewayRestApi#body}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_rest_api#description ApiGatewayRestApi#description}.
        :param disable_execute_api_endpoint: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_rest_api#disable_execute_api_endpoint ApiGatewayRestApi#disable_execute_api_endpoint}.
        :param endpoint_configuration: endpoint_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_rest_api#endpoint_configuration ApiGatewayRestApi#endpoint_configuration}
        :param minimum_compression_size: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_rest_api#minimum_compression_size ApiGatewayRestApi#minimum_compression_size}.
        :param parameters: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_rest_api#parameters ApiGatewayRestApi#parameters}.
        :param policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_rest_api#policy ApiGatewayRestApi#policy}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_rest_api#tags ApiGatewayRestApi#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_rest_api#tags_all ApiGatewayRestApi#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ApiGatewayRestApiConfig(
            name=name,
            api_key_source=api_key_source,
            binary_media_types=binary_media_types,
            body=body,
            description=description,
            disable_execute_api_endpoint=disable_execute_api_endpoint,
            endpoint_configuration=endpoint_configuration,
            minimum_compression_size=minimum_compression_size,
            parameters=parameters,
            policy=policy,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putEndpointConfiguration")
    def put_endpoint_configuration(
        self,
        *,
        types: typing.Sequence[builtins.str],
        vpc_endpoint_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param types: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_rest_api#types ApiGatewayRestApi#types}.
        :param vpc_endpoint_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_rest_api#vpc_endpoint_ids ApiGatewayRestApi#vpc_endpoint_ids}.
        '''
        value = ApiGatewayRestApiEndpointConfiguration(
            types=types, vpc_endpoint_ids=vpc_endpoint_ids
        )

        return typing.cast(None, jsii.invoke(self, "putEndpointConfiguration", [value]))

    @jsii.member(jsii_name="resetApiKeySource")
    def reset_api_key_source(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetApiKeySource", []))

    @jsii.member(jsii_name="resetBinaryMediaTypes")
    def reset_binary_media_types(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBinaryMediaTypes", []))

    @jsii.member(jsii_name="resetBody")
    def reset_body(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBody", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetDisableExecuteApiEndpoint")
    def reset_disable_execute_api_endpoint(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDisableExecuteApiEndpoint", []))

    @jsii.member(jsii_name="resetEndpointConfiguration")
    def reset_endpoint_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEndpointConfiguration", []))

    @jsii.member(jsii_name="resetMinimumCompressionSize")
    def reset_minimum_compression_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinimumCompressionSize", []))

    @jsii.member(jsii_name="resetParameters")
    def reset_parameters(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetParameters", []))

    @jsii.member(jsii_name="resetPolicy")
    def reset_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPolicy", []))

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
    @jsii.member(jsii_name="createdDate")
    def created_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdDate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpointConfiguration")
    def endpoint_configuration(
        self,
    ) -> "ApiGatewayRestApiEndpointConfigurationOutputReference":
        return typing.cast("ApiGatewayRestApiEndpointConfigurationOutputReference", jsii.get(self, "endpointConfiguration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="executionArn")
    def execution_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "executionArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rootResourceId")
    def root_resource_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rootResourceId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiKeySourceInput")
    def api_key_source_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "apiKeySourceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="binaryMediaTypesInput")
    def binary_media_types_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "binaryMediaTypesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bodyInput")
    def body_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bodyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="disableExecuteApiEndpointInput")
    def disable_execute_api_endpoint_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "disableExecuteApiEndpointInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpointConfigurationInput")
    def endpoint_configuration_input(
        self,
    ) -> typing.Optional["ApiGatewayRestApiEndpointConfiguration"]:
        return typing.cast(typing.Optional["ApiGatewayRestApiEndpointConfiguration"], jsii.get(self, "endpointConfigurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="minimumCompressionSizeInput")
    def minimum_compression_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minimumCompressionSizeInput"))

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
    @jsii.member(jsii_name="policyInput")
    def policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "policyInput"))

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
    @jsii.member(jsii_name="apiKeySource")
    def api_key_source(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "apiKeySource"))

    @api_key_source.setter
    def api_key_source(self, value: builtins.str) -> None:
        jsii.set(self, "apiKeySource", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="binaryMediaTypes")
    def binary_media_types(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "binaryMediaTypes"))

    @binary_media_types.setter
    def binary_media_types(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "binaryMediaTypes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="body")
    def body(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "body"))

    @body.setter
    def body(self, value: builtins.str) -> None:
        jsii.set(self, "body", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="disableExecuteApiEndpoint")
    def disable_execute_api_endpoint(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "disableExecuteApiEndpoint"))

    @disable_execute_api_endpoint.setter
    def disable_execute_api_endpoint(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "disableExecuteApiEndpoint", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="minimumCompressionSize")
    def minimum_compression_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minimumCompressionSize"))

    @minimum_compression_size.setter
    def minimum_compression_size(self, value: jsii.Number) -> None:
        jsii.set(self, "minimumCompressionSize", value)

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
    @jsii.member(jsii_name="policy")
    def policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policy"))

    @policy.setter
    def policy(self, value: builtins.str) -> None:
        jsii.set(self, "policy", value)

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
    jsii_type="@cdktf/provider-aws.apigateway.ApiGatewayRestApiConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "api_key_source": "apiKeySource",
        "binary_media_types": "binaryMediaTypes",
        "body": "body",
        "description": "description",
        "disable_execute_api_endpoint": "disableExecuteApiEndpoint",
        "endpoint_configuration": "endpointConfiguration",
        "minimum_compression_size": "minimumCompressionSize",
        "parameters": "parameters",
        "policy": "policy",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class ApiGatewayRestApiConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        api_key_source: typing.Optional[builtins.str] = None,
        binary_media_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        body: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        disable_execute_api_endpoint: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        endpoint_configuration: typing.Optional["ApiGatewayRestApiEndpointConfiguration"] = None,
        minimum_compression_size: typing.Optional[jsii.Number] = None,
        parameters: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        policy: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''API Gateway.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_rest_api#name ApiGatewayRestApi#name}.
        :param api_key_source: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_rest_api#api_key_source ApiGatewayRestApi#api_key_source}.
        :param binary_media_types: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_rest_api#binary_media_types ApiGatewayRestApi#binary_media_types}.
        :param body: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_rest_api#body ApiGatewayRestApi#body}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_rest_api#description ApiGatewayRestApi#description}.
        :param disable_execute_api_endpoint: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_rest_api#disable_execute_api_endpoint ApiGatewayRestApi#disable_execute_api_endpoint}.
        :param endpoint_configuration: endpoint_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_rest_api#endpoint_configuration ApiGatewayRestApi#endpoint_configuration}
        :param minimum_compression_size: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_rest_api#minimum_compression_size ApiGatewayRestApi#minimum_compression_size}.
        :param parameters: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_rest_api#parameters ApiGatewayRestApi#parameters}.
        :param policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_rest_api#policy ApiGatewayRestApi#policy}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_rest_api#tags ApiGatewayRestApi#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_rest_api#tags_all ApiGatewayRestApi#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(endpoint_configuration, dict):
            endpoint_configuration = ApiGatewayRestApiEndpointConfiguration(**endpoint_configuration)
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
        if api_key_source is not None:
            self._values["api_key_source"] = api_key_source
        if binary_media_types is not None:
            self._values["binary_media_types"] = binary_media_types
        if body is not None:
            self._values["body"] = body
        if description is not None:
            self._values["description"] = description
        if disable_execute_api_endpoint is not None:
            self._values["disable_execute_api_endpoint"] = disable_execute_api_endpoint
        if endpoint_configuration is not None:
            self._values["endpoint_configuration"] = endpoint_configuration
        if minimum_compression_size is not None:
            self._values["minimum_compression_size"] = minimum_compression_size
        if parameters is not None:
            self._values["parameters"] = parameters
        if policy is not None:
            self._values["policy"] = policy
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_rest_api#name ApiGatewayRestApi#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def api_key_source(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_rest_api#api_key_source ApiGatewayRestApi#api_key_source}.'''
        result = self._values.get("api_key_source")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def binary_media_types(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_rest_api#binary_media_types ApiGatewayRestApi#binary_media_types}.'''
        result = self._values.get("binary_media_types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def body(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_rest_api#body ApiGatewayRestApi#body}.'''
        result = self._values.get("body")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_rest_api#description ApiGatewayRestApi#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def disable_execute_api_endpoint(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_rest_api#disable_execute_api_endpoint ApiGatewayRestApi#disable_execute_api_endpoint}.'''
        result = self._values.get("disable_execute_api_endpoint")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def endpoint_configuration(
        self,
    ) -> typing.Optional["ApiGatewayRestApiEndpointConfiguration"]:
        '''endpoint_configuration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_rest_api#endpoint_configuration ApiGatewayRestApi#endpoint_configuration}
        '''
        result = self._values.get("endpoint_configuration")
        return typing.cast(typing.Optional["ApiGatewayRestApiEndpointConfiguration"], result)

    @builtins.property
    def minimum_compression_size(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_rest_api#minimum_compression_size ApiGatewayRestApi#minimum_compression_size}.'''
        result = self._values.get("minimum_compression_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def parameters(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_rest_api#parameters ApiGatewayRestApi#parameters}.'''
        result = self._values.get("parameters")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def policy(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_rest_api#policy ApiGatewayRestApi#policy}.'''
        result = self._values.get("policy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_rest_api#tags ApiGatewayRestApi#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_rest_api#tags_all ApiGatewayRestApi#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApiGatewayRestApiConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.apigateway.ApiGatewayRestApiEndpointConfiguration",
    jsii_struct_bases=[],
    name_mapping={"types": "types", "vpc_endpoint_ids": "vpcEndpointIds"},
)
class ApiGatewayRestApiEndpointConfiguration:
    def __init__(
        self,
        *,
        types: typing.Sequence[builtins.str],
        vpc_endpoint_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param types: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_rest_api#types ApiGatewayRestApi#types}.
        :param vpc_endpoint_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_rest_api#vpc_endpoint_ids ApiGatewayRestApi#vpc_endpoint_ids}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "types": types,
        }
        if vpc_endpoint_ids is not None:
            self._values["vpc_endpoint_ids"] = vpc_endpoint_ids

    @builtins.property
    def types(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_rest_api#types ApiGatewayRestApi#types}.'''
        result = self._values.get("types")
        assert result is not None, "Required property 'types' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def vpc_endpoint_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_rest_api#vpc_endpoint_ids ApiGatewayRestApi#vpc_endpoint_ids}.'''
        result = self._values.get("vpc_endpoint_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApiGatewayRestApiEndpointConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ApiGatewayRestApiEndpointConfigurationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.apigateway.ApiGatewayRestApiEndpointConfigurationOutputReference",
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

    @jsii.member(jsii_name="resetVpcEndpointIds")
    def reset_vpc_endpoint_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVpcEndpointIds", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="typesInput")
    def types_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "typesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcEndpointIdsInput")
    def vpc_endpoint_ids_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "vpcEndpointIdsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="types")
    def types(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "types"))

    @types.setter
    def types(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "types", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcEndpointIds")
    def vpc_endpoint_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "vpcEndpointIds"))

    @vpc_endpoint_ids.setter
    def vpc_endpoint_ids(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "vpcEndpointIds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ApiGatewayRestApiEndpointConfiguration]:
        return typing.cast(typing.Optional[ApiGatewayRestApiEndpointConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ApiGatewayRestApiEndpointConfiguration],
    ) -> None:
        jsii.set(self, "internalValue", value)


class ApiGatewayRestApiPolicy(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.apigateway.ApiGatewayRestApiPolicy",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_rest_api_policy aws_api_gateway_rest_api_policy}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        policy: builtins.str,
        rest_api_id: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_rest_api_policy aws_api_gateway_rest_api_policy} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_rest_api_policy#policy ApiGatewayRestApiPolicy#policy}.
        :param rest_api_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_rest_api_policy#rest_api_id ApiGatewayRestApiPolicy#rest_api_id}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ApiGatewayRestApiPolicyConfig(
            policy=policy,
            rest_api_id=rest_api_id,
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
    @jsii.member(jsii_name="restApiIdInput")
    def rest_api_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "restApiIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policy")
    def policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policy"))

    @policy.setter
    def policy(self, value: builtins.str) -> None:
        jsii.set(self, "policy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restApiId")
    def rest_api_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "restApiId"))

    @rest_api_id.setter
    def rest_api_id(self, value: builtins.str) -> None:
        jsii.set(self, "restApiId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.apigateway.ApiGatewayRestApiPolicyConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "policy": "policy",
        "rest_api_id": "restApiId",
    },
)
class ApiGatewayRestApiPolicyConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        policy: builtins.str,
        rest_api_id: builtins.str,
    ) -> None:
        '''API Gateway.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_rest_api_policy#policy ApiGatewayRestApiPolicy#policy}.
        :param rest_api_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_rest_api_policy#rest_api_id ApiGatewayRestApiPolicy#rest_api_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "policy": policy,
            "rest_api_id": rest_api_id,
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_rest_api_policy#policy ApiGatewayRestApiPolicy#policy}.'''
        result = self._values.get("policy")
        assert result is not None, "Required property 'policy' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def rest_api_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_rest_api_policy#rest_api_id ApiGatewayRestApiPolicy#rest_api_id}.'''
        result = self._values.get("rest_api_id")
        assert result is not None, "Required property 'rest_api_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApiGatewayRestApiPolicyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ApiGatewayStage(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.apigateway.ApiGatewayStage",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_stage aws_api_gateway_stage}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        deployment_id: builtins.str,
        rest_api_id: builtins.str,
        stage_name: builtins.str,
        access_log_settings: typing.Optional["ApiGatewayStageAccessLogSettings"] = None,
        cache_cluster_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        cache_cluster_size: typing.Optional[builtins.str] = None,
        client_certificate_id: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        documentation_version: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        variables: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        xray_tracing_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_stage aws_api_gateway_stage} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param deployment_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_stage#deployment_id ApiGatewayStage#deployment_id}.
        :param rest_api_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_stage#rest_api_id ApiGatewayStage#rest_api_id}.
        :param stage_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_stage#stage_name ApiGatewayStage#stage_name}.
        :param access_log_settings: access_log_settings block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_stage#access_log_settings ApiGatewayStage#access_log_settings}
        :param cache_cluster_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_stage#cache_cluster_enabled ApiGatewayStage#cache_cluster_enabled}.
        :param cache_cluster_size: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_stage#cache_cluster_size ApiGatewayStage#cache_cluster_size}.
        :param client_certificate_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_stage#client_certificate_id ApiGatewayStage#client_certificate_id}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_stage#description ApiGatewayStage#description}.
        :param documentation_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_stage#documentation_version ApiGatewayStage#documentation_version}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_stage#tags ApiGatewayStage#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_stage#tags_all ApiGatewayStage#tags_all}.
        :param variables: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_stage#variables ApiGatewayStage#variables}.
        :param xray_tracing_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_stage#xray_tracing_enabled ApiGatewayStage#xray_tracing_enabled}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ApiGatewayStageConfig(
            deployment_id=deployment_id,
            rest_api_id=rest_api_id,
            stage_name=stage_name,
            access_log_settings=access_log_settings,
            cache_cluster_enabled=cache_cluster_enabled,
            cache_cluster_size=cache_cluster_size,
            client_certificate_id=client_certificate_id,
            description=description,
            documentation_version=documentation_version,
            tags=tags,
            tags_all=tags_all,
            variables=variables,
            xray_tracing_enabled=xray_tracing_enabled,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putAccessLogSettings")
    def put_access_log_settings(
        self,
        *,
        destination_arn: builtins.str,
        format: builtins.str,
    ) -> None:
        '''
        :param destination_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_stage#destination_arn ApiGatewayStage#destination_arn}.
        :param format: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_stage#format ApiGatewayStage#format}.
        '''
        value = ApiGatewayStageAccessLogSettings(
            destination_arn=destination_arn, format=format
        )

        return typing.cast(None, jsii.invoke(self, "putAccessLogSettings", [value]))

    @jsii.member(jsii_name="resetAccessLogSettings")
    def reset_access_log_settings(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccessLogSettings", []))

    @jsii.member(jsii_name="resetCacheClusterEnabled")
    def reset_cache_cluster_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCacheClusterEnabled", []))

    @jsii.member(jsii_name="resetCacheClusterSize")
    def reset_cache_cluster_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCacheClusterSize", []))

    @jsii.member(jsii_name="resetClientCertificateId")
    def reset_client_certificate_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClientCertificateId", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetDocumentationVersion")
    def reset_documentation_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDocumentationVersion", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetVariables")
    def reset_variables(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVariables", []))

    @jsii.member(jsii_name="resetXrayTracingEnabled")
    def reset_xray_tracing_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetXrayTracingEnabled", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessLogSettings")
    def access_log_settings(self) -> "ApiGatewayStageAccessLogSettingsOutputReference":
        return typing.cast("ApiGatewayStageAccessLogSettingsOutputReference", jsii.get(self, "accessLogSettings"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="executionArn")
    def execution_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "executionArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="invokeUrl")
    def invoke_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "invokeUrl"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessLogSettingsInput")
    def access_log_settings_input(
        self,
    ) -> typing.Optional["ApiGatewayStageAccessLogSettings"]:
        return typing.cast(typing.Optional["ApiGatewayStageAccessLogSettings"], jsii.get(self, "accessLogSettingsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cacheClusterEnabledInput")
    def cache_cluster_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "cacheClusterEnabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cacheClusterSizeInput")
    def cache_cluster_size_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cacheClusterSizeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clientCertificateIdInput")
    def client_certificate_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clientCertificateIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deploymentIdInput")
    def deployment_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deploymentIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="documentationVersionInput")
    def documentation_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "documentationVersionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restApiIdInput")
    def rest_api_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "restApiIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stageNameInput")
    def stage_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stageNameInput"))

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
    @jsii.member(jsii_name="variablesInput")
    def variables_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "variablesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="xrayTracingEnabledInput")
    def xray_tracing_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "xrayTracingEnabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cacheClusterEnabled")
    def cache_cluster_enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "cacheClusterEnabled"))

    @cache_cluster_enabled.setter
    def cache_cluster_enabled(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "cacheClusterEnabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cacheClusterSize")
    def cache_cluster_size(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cacheClusterSize"))

    @cache_cluster_size.setter
    def cache_cluster_size(self, value: builtins.str) -> None:
        jsii.set(self, "cacheClusterSize", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clientCertificateId")
    def client_certificate_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientCertificateId"))

    @client_certificate_id.setter
    def client_certificate_id(self, value: builtins.str) -> None:
        jsii.set(self, "clientCertificateId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deploymentId")
    def deployment_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deploymentId"))

    @deployment_id.setter
    def deployment_id(self, value: builtins.str) -> None:
        jsii.set(self, "deploymentId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="documentationVersion")
    def documentation_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "documentationVersion"))

    @documentation_version.setter
    def documentation_version(self, value: builtins.str) -> None:
        jsii.set(self, "documentationVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restApiId")
    def rest_api_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "restApiId"))

    @rest_api_id.setter
    def rest_api_id(self, value: builtins.str) -> None:
        jsii.set(self, "restApiId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stageName")
    def stage_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "stageName"))

    @stage_name.setter
    def stage_name(self, value: builtins.str) -> None:
        jsii.set(self, "stageName", value)

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
    @jsii.member(jsii_name="variables")
    def variables(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "variables"))

    @variables.setter
    def variables(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "variables", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="xrayTracingEnabled")
    def xray_tracing_enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "xrayTracingEnabled"))

    @xray_tracing_enabled.setter
    def xray_tracing_enabled(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "xrayTracingEnabled", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.apigateway.ApiGatewayStageAccessLogSettings",
    jsii_struct_bases=[],
    name_mapping={"destination_arn": "destinationArn", "format": "format"},
)
class ApiGatewayStageAccessLogSettings:
    def __init__(self, *, destination_arn: builtins.str, format: builtins.str) -> None:
        '''
        :param destination_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_stage#destination_arn ApiGatewayStage#destination_arn}.
        :param format: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_stage#format ApiGatewayStage#format}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "destination_arn": destination_arn,
            "format": format,
        }

    @builtins.property
    def destination_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_stage#destination_arn ApiGatewayStage#destination_arn}.'''
        result = self._values.get("destination_arn")
        assert result is not None, "Required property 'destination_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def format(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_stage#format ApiGatewayStage#format}.'''
        result = self._values.get("format")
        assert result is not None, "Required property 'format' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApiGatewayStageAccessLogSettings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ApiGatewayStageAccessLogSettingsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.apigateway.ApiGatewayStageAccessLogSettingsOutputReference",
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
    @jsii.member(jsii_name="destinationArnInput")
    def destination_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "destinationArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="formatInput")
    def format_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "formatInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="destinationArn")
    def destination_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destinationArn"))

    @destination_arn.setter
    def destination_arn(self, value: builtins.str) -> None:
        jsii.set(self, "destinationArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="format")
    def format(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "format"))

    @format.setter
    def format(self, value: builtins.str) -> None:
        jsii.set(self, "format", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ApiGatewayStageAccessLogSettings]:
        return typing.cast(typing.Optional[ApiGatewayStageAccessLogSettings], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ApiGatewayStageAccessLogSettings],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.apigateway.ApiGatewayStageConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "deployment_id": "deploymentId",
        "rest_api_id": "restApiId",
        "stage_name": "stageName",
        "access_log_settings": "accessLogSettings",
        "cache_cluster_enabled": "cacheClusterEnabled",
        "cache_cluster_size": "cacheClusterSize",
        "client_certificate_id": "clientCertificateId",
        "description": "description",
        "documentation_version": "documentationVersion",
        "tags": "tags",
        "tags_all": "tagsAll",
        "variables": "variables",
        "xray_tracing_enabled": "xrayTracingEnabled",
    },
)
class ApiGatewayStageConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        deployment_id: builtins.str,
        rest_api_id: builtins.str,
        stage_name: builtins.str,
        access_log_settings: typing.Optional[ApiGatewayStageAccessLogSettings] = None,
        cache_cluster_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        cache_cluster_size: typing.Optional[builtins.str] = None,
        client_certificate_id: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        documentation_version: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        variables: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        xray_tracing_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''API Gateway.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param deployment_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_stage#deployment_id ApiGatewayStage#deployment_id}.
        :param rest_api_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_stage#rest_api_id ApiGatewayStage#rest_api_id}.
        :param stage_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_stage#stage_name ApiGatewayStage#stage_name}.
        :param access_log_settings: access_log_settings block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_stage#access_log_settings ApiGatewayStage#access_log_settings}
        :param cache_cluster_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_stage#cache_cluster_enabled ApiGatewayStage#cache_cluster_enabled}.
        :param cache_cluster_size: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_stage#cache_cluster_size ApiGatewayStage#cache_cluster_size}.
        :param client_certificate_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_stage#client_certificate_id ApiGatewayStage#client_certificate_id}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_stage#description ApiGatewayStage#description}.
        :param documentation_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_stage#documentation_version ApiGatewayStage#documentation_version}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_stage#tags ApiGatewayStage#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_stage#tags_all ApiGatewayStage#tags_all}.
        :param variables: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_stage#variables ApiGatewayStage#variables}.
        :param xray_tracing_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_stage#xray_tracing_enabled ApiGatewayStage#xray_tracing_enabled}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(access_log_settings, dict):
            access_log_settings = ApiGatewayStageAccessLogSettings(**access_log_settings)
        self._values: typing.Dict[str, typing.Any] = {
            "deployment_id": deployment_id,
            "rest_api_id": rest_api_id,
            "stage_name": stage_name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if access_log_settings is not None:
            self._values["access_log_settings"] = access_log_settings
        if cache_cluster_enabled is not None:
            self._values["cache_cluster_enabled"] = cache_cluster_enabled
        if cache_cluster_size is not None:
            self._values["cache_cluster_size"] = cache_cluster_size
        if client_certificate_id is not None:
            self._values["client_certificate_id"] = client_certificate_id
        if description is not None:
            self._values["description"] = description
        if documentation_version is not None:
            self._values["documentation_version"] = documentation_version
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if variables is not None:
            self._values["variables"] = variables
        if xray_tracing_enabled is not None:
            self._values["xray_tracing_enabled"] = xray_tracing_enabled

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
    def deployment_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_stage#deployment_id ApiGatewayStage#deployment_id}.'''
        result = self._values.get("deployment_id")
        assert result is not None, "Required property 'deployment_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def rest_api_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_stage#rest_api_id ApiGatewayStage#rest_api_id}.'''
        result = self._values.get("rest_api_id")
        assert result is not None, "Required property 'rest_api_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def stage_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_stage#stage_name ApiGatewayStage#stage_name}.'''
        result = self._values.get("stage_name")
        assert result is not None, "Required property 'stage_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def access_log_settings(self) -> typing.Optional[ApiGatewayStageAccessLogSettings]:
        '''access_log_settings block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_stage#access_log_settings ApiGatewayStage#access_log_settings}
        '''
        result = self._values.get("access_log_settings")
        return typing.cast(typing.Optional[ApiGatewayStageAccessLogSettings], result)

    @builtins.property
    def cache_cluster_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_stage#cache_cluster_enabled ApiGatewayStage#cache_cluster_enabled}.'''
        result = self._values.get("cache_cluster_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def cache_cluster_size(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_stage#cache_cluster_size ApiGatewayStage#cache_cluster_size}.'''
        result = self._values.get("cache_cluster_size")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def client_certificate_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_stage#client_certificate_id ApiGatewayStage#client_certificate_id}.'''
        result = self._values.get("client_certificate_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_stage#description ApiGatewayStage#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def documentation_version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_stage#documentation_version ApiGatewayStage#documentation_version}.'''
        result = self._values.get("documentation_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_stage#tags ApiGatewayStage#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_stage#tags_all ApiGatewayStage#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def variables(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_stage#variables ApiGatewayStage#variables}.'''
        result = self._values.get("variables")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def xray_tracing_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_stage#xray_tracing_enabled ApiGatewayStage#xray_tracing_enabled}.'''
        result = self._values.get("xray_tracing_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApiGatewayStageConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ApiGatewayUsagePlan(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.apigateway.ApiGatewayUsagePlan",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_usage_plan aws_api_gateway_usage_plan}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        api_stages: typing.Optional[typing.Sequence["ApiGatewayUsagePlanApiStages"]] = None,
        description: typing.Optional[builtins.str] = None,
        product_code: typing.Optional[builtins.str] = None,
        quota_settings: typing.Optional["ApiGatewayUsagePlanQuotaSettings"] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        throttle_settings: typing.Optional["ApiGatewayUsagePlanThrottleSettings"] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_usage_plan aws_api_gateway_usage_plan} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_usage_plan#name ApiGatewayUsagePlan#name}.
        :param api_stages: api_stages block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_usage_plan#api_stages ApiGatewayUsagePlan#api_stages}
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_usage_plan#description ApiGatewayUsagePlan#description}.
        :param product_code: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_usage_plan#product_code ApiGatewayUsagePlan#product_code}.
        :param quota_settings: quota_settings block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_usage_plan#quota_settings ApiGatewayUsagePlan#quota_settings}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_usage_plan#tags ApiGatewayUsagePlan#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_usage_plan#tags_all ApiGatewayUsagePlan#tags_all}.
        :param throttle_settings: throttle_settings block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_usage_plan#throttle_settings ApiGatewayUsagePlan#throttle_settings}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ApiGatewayUsagePlanConfig(
            name=name,
            api_stages=api_stages,
            description=description,
            product_code=product_code,
            quota_settings=quota_settings,
            tags=tags,
            tags_all=tags_all,
            throttle_settings=throttle_settings,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putQuotaSettings")
    def put_quota_settings(
        self,
        *,
        limit: jsii.Number,
        period: builtins.str,
        offset: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param limit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_usage_plan#limit ApiGatewayUsagePlan#limit}.
        :param period: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_usage_plan#period ApiGatewayUsagePlan#period}.
        :param offset: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_usage_plan#offset ApiGatewayUsagePlan#offset}.
        '''
        value = ApiGatewayUsagePlanQuotaSettings(
            limit=limit, period=period, offset=offset
        )

        return typing.cast(None, jsii.invoke(self, "putQuotaSettings", [value]))

    @jsii.member(jsii_name="putThrottleSettings")
    def put_throttle_settings(
        self,
        *,
        burst_limit: typing.Optional[jsii.Number] = None,
        rate_limit: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param burst_limit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_usage_plan#burst_limit ApiGatewayUsagePlan#burst_limit}.
        :param rate_limit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_usage_plan#rate_limit ApiGatewayUsagePlan#rate_limit}.
        '''
        value = ApiGatewayUsagePlanThrottleSettings(
            burst_limit=burst_limit, rate_limit=rate_limit
        )

        return typing.cast(None, jsii.invoke(self, "putThrottleSettings", [value]))

    @jsii.member(jsii_name="resetApiStages")
    def reset_api_stages(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetApiStages", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetProductCode")
    def reset_product_code(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProductCode", []))

    @jsii.member(jsii_name="resetQuotaSettings")
    def reset_quota_settings(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetQuotaSettings", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetThrottleSettings")
    def reset_throttle_settings(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetThrottleSettings", []))

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
    @jsii.member(jsii_name="quotaSettings")
    def quota_settings(self) -> "ApiGatewayUsagePlanQuotaSettingsOutputReference":
        return typing.cast("ApiGatewayUsagePlanQuotaSettingsOutputReference", jsii.get(self, "quotaSettings"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="throttleSettings")
    def throttle_settings(self) -> "ApiGatewayUsagePlanThrottleSettingsOutputReference":
        return typing.cast("ApiGatewayUsagePlanThrottleSettingsOutputReference", jsii.get(self, "throttleSettings"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiStagesInput")
    def api_stages_input(
        self,
    ) -> typing.Optional[typing.List["ApiGatewayUsagePlanApiStages"]]:
        return typing.cast(typing.Optional[typing.List["ApiGatewayUsagePlanApiStages"]], jsii.get(self, "apiStagesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="productCodeInput")
    def product_code_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "productCodeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="quotaSettingsInput")
    def quota_settings_input(
        self,
    ) -> typing.Optional["ApiGatewayUsagePlanQuotaSettings"]:
        return typing.cast(typing.Optional["ApiGatewayUsagePlanQuotaSettings"], jsii.get(self, "quotaSettingsInput"))

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
    @jsii.member(jsii_name="throttleSettingsInput")
    def throttle_settings_input(
        self,
    ) -> typing.Optional["ApiGatewayUsagePlanThrottleSettings"]:
        return typing.cast(typing.Optional["ApiGatewayUsagePlanThrottleSettings"], jsii.get(self, "throttleSettingsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiStages")
    def api_stages(self) -> typing.List["ApiGatewayUsagePlanApiStages"]:
        return typing.cast(typing.List["ApiGatewayUsagePlanApiStages"], jsii.get(self, "apiStages"))

    @api_stages.setter
    def api_stages(self, value: typing.List["ApiGatewayUsagePlanApiStages"]) -> None:
        jsii.set(self, "apiStages", value)

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
    @jsii.member(jsii_name="productCode")
    def product_code(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "productCode"))

    @product_code.setter
    def product_code(self, value: builtins.str) -> None:
        jsii.set(self, "productCode", value)

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
    jsii_type="@cdktf/provider-aws.apigateway.ApiGatewayUsagePlanApiStages",
    jsii_struct_bases=[],
    name_mapping={"api_id": "apiId", "stage": "stage", "throttle": "throttle"},
)
class ApiGatewayUsagePlanApiStages:
    def __init__(
        self,
        *,
        api_id: builtins.str,
        stage: builtins.str,
        throttle: typing.Optional[typing.Sequence["ApiGatewayUsagePlanApiStagesThrottle"]] = None,
    ) -> None:
        '''
        :param api_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_usage_plan#api_id ApiGatewayUsagePlan#api_id}.
        :param stage: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_usage_plan#stage ApiGatewayUsagePlan#stage}.
        :param throttle: throttle block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_usage_plan#throttle ApiGatewayUsagePlan#throttle}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "api_id": api_id,
            "stage": stage,
        }
        if throttle is not None:
            self._values["throttle"] = throttle

    @builtins.property
    def api_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_usage_plan#api_id ApiGatewayUsagePlan#api_id}.'''
        result = self._values.get("api_id")
        assert result is not None, "Required property 'api_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def stage(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_usage_plan#stage ApiGatewayUsagePlan#stage}.'''
        result = self._values.get("stage")
        assert result is not None, "Required property 'stage' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def throttle(
        self,
    ) -> typing.Optional[typing.List["ApiGatewayUsagePlanApiStagesThrottle"]]:
        '''throttle block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_usage_plan#throttle ApiGatewayUsagePlan#throttle}
        '''
        result = self._values.get("throttle")
        return typing.cast(typing.Optional[typing.List["ApiGatewayUsagePlanApiStagesThrottle"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApiGatewayUsagePlanApiStages(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.apigateway.ApiGatewayUsagePlanApiStagesThrottle",
    jsii_struct_bases=[],
    name_mapping={
        "path": "path",
        "burst_limit": "burstLimit",
        "rate_limit": "rateLimit",
    },
)
class ApiGatewayUsagePlanApiStagesThrottle:
    def __init__(
        self,
        *,
        path: builtins.str,
        burst_limit: typing.Optional[jsii.Number] = None,
        rate_limit: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param path: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_usage_plan#path ApiGatewayUsagePlan#path}.
        :param burst_limit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_usage_plan#burst_limit ApiGatewayUsagePlan#burst_limit}.
        :param rate_limit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_usage_plan#rate_limit ApiGatewayUsagePlan#rate_limit}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "path": path,
        }
        if burst_limit is not None:
            self._values["burst_limit"] = burst_limit
        if rate_limit is not None:
            self._values["rate_limit"] = rate_limit

    @builtins.property
    def path(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_usage_plan#path ApiGatewayUsagePlan#path}.'''
        result = self._values.get("path")
        assert result is not None, "Required property 'path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def burst_limit(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_usage_plan#burst_limit ApiGatewayUsagePlan#burst_limit}.'''
        result = self._values.get("burst_limit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def rate_limit(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_usage_plan#rate_limit ApiGatewayUsagePlan#rate_limit}.'''
        result = self._values.get("rate_limit")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApiGatewayUsagePlanApiStagesThrottle(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.apigateway.ApiGatewayUsagePlanConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "api_stages": "apiStages",
        "description": "description",
        "product_code": "productCode",
        "quota_settings": "quotaSettings",
        "tags": "tags",
        "tags_all": "tagsAll",
        "throttle_settings": "throttleSettings",
    },
)
class ApiGatewayUsagePlanConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        api_stages: typing.Optional[typing.Sequence[ApiGatewayUsagePlanApiStages]] = None,
        description: typing.Optional[builtins.str] = None,
        product_code: typing.Optional[builtins.str] = None,
        quota_settings: typing.Optional["ApiGatewayUsagePlanQuotaSettings"] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        throttle_settings: typing.Optional["ApiGatewayUsagePlanThrottleSettings"] = None,
    ) -> None:
        '''API Gateway.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_usage_plan#name ApiGatewayUsagePlan#name}.
        :param api_stages: api_stages block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_usage_plan#api_stages ApiGatewayUsagePlan#api_stages}
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_usage_plan#description ApiGatewayUsagePlan#description}.
        :param product_code: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_usage_plan#product_code ApiGatewayUsagePlan#product_code}.
        :param quota_settings: quota_settings block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_usage_plan#quota_settings ApiGatewayUsagePlan#quota_settings}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_usage_plan#tags ApiGatewayUsagePlan#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_usage_plan#tags_all ApiGatewayUsagePlan#tags_all}.
        :param throttle_settings: throttle_settings block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_usage_plan#throttle_settings ApiGatewayUsagePlan#throttle_settings}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(quota_settings, dict):
            quota_settings = ApiGatewayUsagePlanQuotaSettings(**quota_settings)
        if isinstance(throttle_settings, dict):
            throttle_settings = ApiGatewayUsagePlanThrottleSettings(**throttle_settings)
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
        if api_stages is not None:
            self._values["api_stages"] = api_stages
        if description is not None:
            self._values["description"] = description
        if product_code is not None:
            self._values["product_code"] = product_code
        if quota_settings is not None:
            self._values["quota_settings"] = quota_settings
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if throttle_settings is not None:
            self._values["throttle_settings"] = throttle_settings

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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_usage_plan#name ApiGatewayUsagePlan#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def api_stages(self) -> typing.Optional[typing.List[ApiGatewayUsagePlanApiStages]]:
        '''api_stages block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_usage_plan#api_stages ApiGatewayUsagePlan#api_stages}
        '''
        result = self._values.get("api_stages")
        return typing.cast(typing.Optional[typing.List[ApiGatewayUsagePlanApiStages]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_usage_plan#description ApiGatewayUsagePlan#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def product_code(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_usage_plan#product_code ApiGatewayUsagePlan#product_code}.'''
        result = self._values.get("product_code")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def quota_settings(self) -> typing.Optional["ApiGatewayUsagePlanQuotaSettings"]:
        '''quota_settings block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_usage_plan#quota_settings ApiGatewayUsagePlan#quota_settings}
        '''
        result = self._values.get("quota_settings")
        return typing.cast(typing.Optional["ApiGatewayUsagePlanQuotaSettings"], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_usage_plan#tags ApiGatewayUsagePlan#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_usage_plan#tags_all ApiGatewayUsagePlan#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def throttle_settings(
        self,
    ) -> typing.Optional["ApiGatewayUsagePlanThrottleSettings"]:
        '''throttle_settings block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_usage_plan#throttle_settings ApiGatewayUsagePlan#throttle_settings}
        '''
        result = self._values.get("throttle_settings")
        return typing.cast(typing.Optional["ApiGatewayUsagePlanThrottleSettings"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApiGatewayUsagePlanConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ApiGatewayUsagePlanKey(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.apigateway.ApiGatewayUsagePlanKey",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_usage_plan_key aws_api_gateway_usage_plan_key}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        key_id: builtins.str,
        key_type: builtins.str,
        usage_plan_id: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_usage_plan_key aws_api_gateway_usage_plan_key} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_usage_plan_key#key_id ApiGatewayUsagePlanKey#key_id}.
        :param key_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_usage_plan_key#key_type ApiGatewayUsagePlanKey#key_type}.
        :param usage_plan_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_usage_plan_key#usage_plan_id ApiGatewayUsagePlanKey#usage_plan_id}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ApiGatewayUsagePlanKeyConfig(
            key_id=key_id,
            key_type=key_type,
            usage_plan_id=usage_plan_id,
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
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyIdInput")
    def key_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyTypeInput")
    def key_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="usagePlanIdInput")
    def usage_plan_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usagePlanIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyId")
    def key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keyId"))

    @key_id.setter
    def key_id(self, value: builtins.str) -> None:
        jsii.set(self, "keyId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyType")
    def key_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keyType"))

    @key_type.setter
    def key_type(self, value: builtins.str) -> None:
        jsii.set(self, "keyType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="usagePlanId")
    def usage_plan_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "usagePlanId"))

    @usage_plan_id.setter
    def usage_plan_id(self, value: builtins.str) -> None:
        jsii.set(self, "usagePlanId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.apigateway.ApiGatewayUsagePlanKeyConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "key_id": "keyId",
        "key_type": "keyType",
        "usage_plan_id": "usagePlanId",
    },
)
class ApiGatewayUsagePlanKeyConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        key_id: builtins.str,
        key_type: builtins.str,
        usage_plan_id: builtins.str,
    ) -> None:
        '''API Gateway.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_usage_plan_key#key_id ApiGatewayUsagePlanKey#key_id}.
        :param key_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_usage_plan_key#key_type ApiGatewayUsagePlanKey#key_type}.
        :param usage_plan_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_usage_plan_key#usage_plan_id ApiGatewayUsagePlanKey#usage_plan_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "key_id": key_id,
            "key_type": key_type,
            "usage_plan_id": usage_plan_id,
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
    def key_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_usage_plan_key#key_id ApiGatewayUsagePlanKey#key_id}.'''
        result = self._values.get("key_id")
        assert result is not None, "Required property 'key_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def key_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_usage_plan_key#key_type ApiGatewayUsagePlanKey#key_type}.'''
        result = self._values.get("key_type")
        assert result is not None, "Required property 'key_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def usage_plan_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_usage_plan_key#usage_plan_id ApiGatewayUsagePlanKey#usage_plan_id}.'''
        result = self._values.get("usage_plan_id")
        assert result is not None, "Required property 'usage_plan_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApiGatewayUsagePlanKeyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.apigateway.ApiGatewayUsagePlanQuotaSettings",
    jsii_struct_bases=[],
    name_mapping={"limit": "limit", "period": "period", "offset": "offset"},
)
class ApiGatewayUsagePlanQuotaSettings:
    def __init__(
        self,
        *,
        limit: jsii.Number,
        period: builtins.str,
        offset: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param limit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_usage_plan#limit ApiGatewayUsagePlan#limit}.
        :param period: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_usage_plan#period ApiGatewayUsagePlan#period}.
        :param offset: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_usage_plan#offset ApiGatewayUsagePlan#offset}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "limit": limit,
            "period": period,
        }
        if offset is not None:
            self._values["offset"] = offset

    @builtins.property
    def limit(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_usage_plan#limit ApiGatewayUsagePlan#limit}.'''
        result = self._values.get("limit")
        assert result is not None, "Required property 'limit' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def period(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_usage_plan#period ApiGatewayUsagePlan#period}.'''
        result = self._values.get("period")
        assert result is not None, "Required property 'period' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def offset(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_usage_plan#offset ApiGatewayUsagePlan#offset}.'''
        result = self._values.get("offset")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApiGatewayUsagePlanQuotaSettings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ApiGatewayUsagePlanQuotaSettingsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.apigateway.ApiGatewayUsagePlanQuotaSettingsOutputReference",
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

    @jsii.member(jsii_name="resetOffset")
    def reset_offset(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOffset", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="limitInput")
    def limit_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "limitInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="offsetInput")
    def offset_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "offsetInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="periodInput")
    def period_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "periodInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="limit")
    def limit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "limit"))

    @limit.setter
    def limit(self, value: jsii.Number) -> None:
        jsii.set(self, "limit", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="offset")
    def offset(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "offset"))

    @offset.setter
    def offset(self, value: jsii.Number) -> None:
        jsii.set(self, "offset", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="period")
    def period(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "period"))

    @period.setter
    def period(self, value: builtins.str) -> None:
        jsii.set(self, "period", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ApiGatewayUsagePlanQuotaSettings]:
        return typing.cast(typing.Optional[ApiGatewayUsagePlanQuotaSettings], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ApiGatewayUsagePlanQuotaSettings],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.apigateway.ApiGatewayUsagePlanThrottleSettings",
    jsii_struct_bases=[],
    name_mapping={"burst_limit": "burstLimit", "rate_limit": "rateLimit"},
)
class ApiGatewayUsagePlanThrottleSettings:
    def __init__(
        self,
        *,
        burst_limit: typing.Optional[jsii.Number] = None,
        rate_limit: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param burst_limit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_usage_plan#burst_limit ApiGatewayUsagePlan#burst_limit}.
        :param rate_limit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_usage_plan#rate_limit ApiGatewayUsagePlan#rate_limit}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if burst_limit is not None:
            self._values["burst_limit"] = burst_limit
        if rate_limit is not None:
            self._values["rate_limit"] = rate_limit

    @builtins.property
    def burst_limit(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_usage_plan#burst_limit ApiGatewayUsagePlan#burst_limit}.'''
        result = self._values.get("burst_limit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def rate_limit(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_usage_plan#rate_limit ApiGatewayUsagePlan#rate_limit}.'''
        result = self._values.get("rate_limit")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApiGatewayUsagePlanThrottleSettings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ApiGatewayUsagePlanThrottleSettingsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.apigateway.ApiGatewayUsagePlanThrottleSettingsOutputReference",
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

    @jsii.member(jsii_name="resetBurstLimit")
    def reset_burst_limit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBurstLimit", []))

    @jsii.member(jsii_name="resetRateLimit")
    def reset_rate_limit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRateLimit", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="burstLimitInput")
    def burst_limit_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "burstLimitInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rateLimitInput")
    def rate_limit_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "rateLimitInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="burstLimit")
    def burst_limit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "burstLimit"))

    @burst_limit.setter
    def burst_limit(self, value: jsii.Number) -> None:
        jsii.set(self, "burstLimit", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rateLimit")
    def rate_limit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "rateLimit"))

    @rate_limit.setter
    def rate_limit(self, value: jsii.Number) -> None:
        jsii.set(self, "rateLimit", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ApiGatewayUsagePlanThrottleSettings]:
        return typing.cast(typing.Optional[ApiGatewayUsagePlanThrottleSettings], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ApiGatewayUsagePlanThrottleSettings],
    ) -> None:
        jsii.set(self, "internalValue", value)


class ApiGatewayVpcLink(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.apigateway.ApiGatewayVpcLink",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_vpc_link aws_api_gateway_vpc_link}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        target_arns: typing.Sequence[builtins.str],
        description: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_vpc_link aws_api_gateway_vpc_link} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_vpc_link#name ApiGatewayVpcLink#name}.
        :param target_arns: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_vpc_link#target_arns ApiGatewayVpcLink#target_arns}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_vpc_link#description ApiGatewayVpcLink#description}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_vpc_link#tags ApiGatewayVpcLink#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_vpc_link#tags_all ApiGatewayVpcLink#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ApiGatewayVpcLinkConfig(
            name=name,
            target_arns=target_arns,
            description=description,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

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
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

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
    @jsii.member(jsii_name="targetArnsInput")
    def target_arns_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "targetArnsInput"))

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

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetArns")
    def target_arns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "targetArns"))

    @target_arns.setter
    def target_arns(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "targetArns", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.apigateway.ApiGatewayVpcLinkConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "target_arns": "targetArns",
        "description": "description",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class ApiGatewayVpcLinkConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        target_arns: typing.Sequence[builtins.str],
        description: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''API Gateway.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_vpc_link#name ApiGatewayVpcLink#name}.
        :param target_arns: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_vpc_link#target_arns ApiGatewayVpcLink#target_arns}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_vpc_link#description ApiGatewayVpcLink#description}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_vpc_link#tags ApiGatewayVpcLink#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_vpc_link#tags_all ApiGatewayVpcLink#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "target_arns": target_arns,
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_vpc_link#name ApiGatewayVpcLink#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def target_arns(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_vpc_link#target_arns ApiGatewayVpcLink#target_arns}.'''
        result = self._values.get("target_arns")
        assert result is not None, "Required property 'target_arns' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_vpc_link#description ApiGatewayVpcLink#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_vpc_link#tags ApiGatewayVpcLink#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/api_gateway_vpc_link#tags_all ApiGatewayVpcLink#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApiGatewayVpcLinkConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsApiGatewayApiKey(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.apigateway.DataAwsApiGatewayApiKey",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/api_gateway_api_key aws_api_gateway_api_key}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        id: builtins.str,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/api_gateway_api_key aws_api_gateway_api_key} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/api_gateway_api_key#id DataAwsApiGatewayApiKey#id}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/api_gateway_api_key#tags DataAwsApiGatewayApiKey#tags}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsApiGatewayApiKeyConfig(
            id=id,
            tags=tags,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

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
    @jsii.member(jsii_name="createdDate")
    def created_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdDate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "enabled"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lastUpdatedDate")
    def last_updated_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lastUpdatedDate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        jsii.set(self, "id", value)

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
    jsii_type="@cdktf/provider-aws.apigateway.DataAwsApiGatewayApiKeyConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "id": "id",
        "tags": "tags",
    },
)
class DataAwsApiGatewayApiKeyConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        id: builtins.str,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''API Gateway.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/api_gateway_api_key#id DataAwsApiGatewayApiKey#id}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/api_gateway_api_key#tags DataAwsApiGatewayApiKey#tags}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "id": id,
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
    def id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/api_gateway_api_key#id DataAwsApiGatewayApiKey#id}.'''
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/api_gateway_api_key#tags DataAwsApiGatewayApiKey#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsApiGatewayApiKeyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsApiGatewayDomainName(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.apigateway.DataAwsApiGatewayDomainName",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/api_gateway_domain_name aws_api_gateway_domain_name}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        domain_name: builtins.str,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/api_gateway_domain_name aws_api_gateway_domain_name} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param domain_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/api_gateway_domain_name#domain_name DataAwsApiGatewayDomainName#domain_name}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/api_gateway_domain_name#tags DataAwsApiGatewayDomainName#tags}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsApiGatewayDomainNameConfig(
            domain_name=domain_name,
            tags=tags,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="endpointConfiguration")
    def endpoint_configuration(
        self,
        index: builtins.str,
    ) -> "DataAwsApiGatewayDomainNameEndpointConfiguration":
        '''
        :param index: -
        '''
        return typing.cast("DataAwsApiGatewayDomainNameEndpointConfiguration", jsii.invoke(self, "endpointConfiguration", [index]))

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
    @jsii.member(jsii_name="certificateArn")
    def certificate_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificateArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certificateName")
    def certificate_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificateName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certificateUploadDate")
    def certificate_upload_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificateUploadDate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cloudfrontDomainName")
    def cloudfront_domain_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cloudfrontDomainName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cloudfrontZoneId")
    def cloudfront_zone_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cloudfrontZoneId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="regionalCertificateArn")
    def regional_certificate_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "regionalCertificateArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="regionalCertificateName")
    def regional_certificate_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "regionalCertificateName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="regionalDomainName")
    def regional_domain_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "regionalDomainName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="regionalZoneId")
    def regional_zone_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "regionalZoneId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityPolicy")
    def security_policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "securityPolicy"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainNameInput")
    def domain_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "domainNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainName")
    def domain_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "domainName"))

    @domain_name.setter
    def domain_name(self, value: builtins.str) -> None:
        jsii.set(self, "domainName", value)

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
    jsii_type="@cdktf/provider-aws.apigateway.DataAwsApiGatewayDomainNameConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "domain_name": "domainName",
        "tags": "tags",
    },
)
class DataAwsApiGatewayDomainNameConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        domain_name: builtins.str,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''API Gateway.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param domain_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/api_gateway_domain_name#domain_name DataAwsApiGatewayDomainName#domain_name}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/api_gateway_domain_name#tags DataAwsApiGatewayDomainName#tags}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "domain_name": domain_name,
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
    def domain_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/api_gateway_domain_name#domain_name DataAwsApiGatewayDomainName#domain_name}.'''
        result = self._values.get("domain_name")
        assert result is not None, "Required property 'domain_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/api_gateway_domain_name#tags DataAwsApiGatewayDomainName#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsApiGatewayDomainNameConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsApiGatewayDomainNameEndpointConfiguration(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.apigateway.DataAwsApiGatewayDomainNameEndpointConfiguration",
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
    @jsii.member(jsii_name="types")
    def types(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "types"))


class DataAwsApiGatewayResource(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.apigateway.DataAwsApiGatewayResource",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/api_gateway_resource aws_api_gateway_resource}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        path: builtins.str,
        rest_api_id: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/api_gateway_resource aws_api_gateway_resource} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param path: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/api_gateway_resource#path DataAwsApiGatewayResource#path}.
        :param rest_api_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/api_gateway_resource#rest_api_id DataAwsApiGatewayResource#rest_api_id}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsApiGatewayResourceConfig(
            path=path,
            rest_api_id=rest_api_id,
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
    @jsii.member(jsii_name="parentId")
    def parent_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "parentId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pathPart")
    def path_part(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pathPart"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pathInput")
    def path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pathInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restApiIdInput")
    def rest_api_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "restApiIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "path"))

    @path.setter
    def path(self, value: builtins.str) -> None:
        jsii.set(self, "path", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restApiId")
    def rest_api_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "restApiId"))

    @rest_api_id.setter
    def rest_api_id(self, value: builtins.str) -> None:
        jsii.set(self, "restApiId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.apigateway.DataAwsApiGatewayResourceConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "path": "path",
        "rest_api_id": "restApiId",
    },
)
class DataAwsApiGatewayResourceConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        path: builtins.str,
        rest_api_id: builtins.str,
    ) -> None:
        '''API Gateway.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param path: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/api_gateway_resource#path DataAwsApiGatewayResource#path}.
        :param rest_api_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/api_gateway_resource#rest_api_id DataAwsApiGatewayResource#rest_api_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "path": path,
            "rest_api_id": rest_api_id,
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
    def path(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/api_gateway_resource#path DataAwsApiGatewayResource#path}.'''
        result = self._values.get("path")
        assert result is not None, "Required property 'path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def rest_api_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/api_gateway_resource#rest_api_id DataAwsApiGatewayResource#rest_api_id}.'''
        result = self._values.get("rest_api_id")
        assert result is not None, "Required property 'rest_api_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsApiGatewayResourceConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsApiGatewayRestApi(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.apigateway.DataAwsApiGatewayRestApi",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/api_gateway_rest_api aws_api_gateway_rest_api}.'''

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
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/api_gateway_rest_api aws_api_gateway_rest_api} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/api_gateway_rest_api#name DataAwsApiGatewayRestApi#name}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/api_gateway_rest_api#tags DataAwsApiGatewayRestApi#tags}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsApiGatewayRestApiConfig(
            name=name,
            tags=tags,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="endpointConfiguration")
    def endpoint_configuration(
        self,
        index: builtins.str,
    ) -> "DataAwsApiGatewayRestApiEndpointConfiguration":
        '''
        :param index: -
        '''
        return typing.cast("DataAwsApiGatewayRestApiEndpointConfiguration", jsii.invoke(self, "endpointConfiguration", [index]))

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
    @jsii.member(jsii_name="apiKeySource")
    def api_key_source(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "apiKeySource"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="binaryMediaTypes")
    def binary_media_types(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "binaryMediaTypes"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="executionArn")
    def execution_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "executionArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="minimumCompressionSize")
    def minimum_compression_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minimumCompressionSize"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policy")
    def policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policy"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rootResourceId")
    def root_resource_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rootResourceId"))

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
    jsii_type="@cdktf/provider-aws.apigateway.DataAwsApiGatewayRestApiConfig",
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
class DataAwsApiGatewayRestApiConfig(cdktf.TerraformMetaArguments):
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
        '''API Gateway.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/api_gateway_rest_api#name DataAwsApiGatewayRestApi#name}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/api_gateway_rest_api#tags DataAwsApiGatewayRestApi#tags}.
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/api_gateway_rest_api#name DataAwsApiGatewayRestApi#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/api_gateway_rest_api#tags DataAwsApiGatewayRestApi#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsApiGatewayRestApiConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsApiGatewayRestApiEndpointConfiguration(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.apigateway.DataAwsApiGatewayRestApiEndpointConfiguration",
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
    @jsii.member(jsii_name="types")
    def types(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "types"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcEndpointIds")
    def vpc_endpoint_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "vpcEndpointIds"))


class DataAwsApiGatewayVpcLink(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.apigateway.DataAwsApiGatewayVpcLink",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/api_gateway_vpc_link aws_api_gateway_vpc_link}.'''

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
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/api_gateway_vpc_link aws_api_gateway_vpc_link} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/api_gateway_vpc_link#name DataAwsApiGatewayVpcLink#name}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/api_gateway_vpc_link#tags DataAwsApiGatewayVpcLink#tags}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsApiGatewayVpcLinkConfig(
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
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statusMessage")
    def status_message(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "statusMessage"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetArns")
    def target_arns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "targetArns"))

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
    jsii_type="@cdktf/provider-aws.apigateway.DataAwsApiGatewayVpcLinkConfig",
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
class DataAwsApiGatewayVpcLinkConfig(cdktf.TerraformMetaArguments):
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
        '''API Gateway.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/api_gateway_vpc_link#name DataAwsApiGatewayVpcLink#name}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/api_gateway_vpc_link#tags DataAwsApiGatewayVpcLink#tags}.
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/api_gateway_vpc_link#name DataAwsApiGatewayVpcLink#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/api_gateway_vpc_link#tags DataAwsApiGatewayVpcLink#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsApiGatewayVpcLinkConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ApiGatewayAccount",
    "ApiGatewayAccountConfig",
    "ApiGatewayAccountThrottleSettings",
    "ApiGatewayApiKey",
    "ApiGatewayApiKeyConfig",
    "ApiGatewayAuthorizer",
    "ApiGatewayAuthorizerConfig",
    "ApiGatewayBasePathMapping",
    "ApiGatewayBasePathMappingConfig",
    "ApiGatewayClientCertificate",
    "ApiGatewayClientCertificateConfig",
    "ApiGatewayDeployment",
    "ApiGatewayDeploymentConfig",
    "ApiGatewayDocumentationPart",
    "ApiGatewayDocumentationPartConfig",
    "ApiGatewayDocumentationPartLocation",
    "ApiGatewayDocumentationPartLocationOutputReference",
    "ApiGatewayDocumentationVersion",
    "ApiGatewayDocumentationVersionConfig",
    "ApiGatewayDomainName",
    "ApiGatewayDomainNameConfig",
    "ApiGatewayDomainNameEndpointConfiguration",
    "ApiGatewayDomainNameEndpointConfigurationOutputReference",
    "ApiGatewayDomainNameMutualTlsAuthentication",
    "ApiGatewayDomainNameMutualTlsAuthenticationOutputReference",
    "ApiGatewayGatewayResponse",
    "ApiGatewayGatewayResponseConfig",
    "ApiGatewayIntegration",
    "ApiGatewayIntegrationConfig",
    "ApiGatewayIntegrationResponse",
    "ApiGatewayIntegrationResponseConfig",
    "ApiGatewayIntegrationTlsConfig",
    "ApiGatewayIntegrationTlsConfigOutputReference",
    "ApiGatewayMethod",
    "ApiGatewayMethodConfig",
    "ApiGatewayMethodResponse",
    "ApiGatewayMethodResponseConfig",
    "ApiGatewayMethodSettings",
    "ApiGatewayMethodSettingsConfig",
    "ApiGatewayMethodSettingsSettings",
    "ApiGatewayMethodSettingsSettingsOutputReference",
    "ApiGatewayModel",
    "ApiGatewayModelConfig",
    "ApiGatewayRequestValidator",
    "ApiGatewayRequestValidatorConfig",
    "ApiGatewayResource",
    "ApiGatewayResourceConfig",
    "ApiGatewayRestApi",
    "ApiGatewayRestApiConfig",
    "ApiGatewayRestApiEndpointConfiguration",
    "ApiGatewayRestApiEndpointConfigurationOutputReference",
    "ApiGatewayRestApiPolicy",
    "ApiGatewayRestApiPolicyConfig",
    "ApiGatewayStage",
    "ApiGatewayStageAccessLogSettings",
    "ApiGatewayStageAccessLogSettingsOutputReference",
    "ApiGatewayStageConfig",
    "ApiGatewayUsagePlan",
    "ApiGatewayUsagePlanApiStages",
    "ApiGatewayUsagePlanApiStagesThrottle",
    "ApiGatewayUsagePlanConfig",
    "ApiGatewayUsagePlanKey",
    "ApiGatewayUsagePlanKeyConfig",
    "ApiGatewayUsagePlanQuotaSettings",
    "ApiGatewayUsagePlanQuotaSettingsOutputReference",
    "ApiGatewayUsagePlanThrottleSettings",
    "ApiGatewayUsagePlanThrottleSettingsOutputReference",
    "ApiGatewayVpcLink",
    "ApiGatewayVpcLinkConfig",
    "DataAwsApiGatewayApiKey",
    "DataAwsApiGatewayApiKeyConfig",
    "DataAwsApiGatewayDomainName",
    "DataAwsApiGatewayDomainNameConfig",
    "DataAwsApiGatewayDomainNameEndpointConfiguration",
    "DataAwsApiGatewayResource",
    "DataAwsApiGatewayResourceConfig",
    "DataAwsApiGatewayRestApi",
    "DataAwsApiGatewayRestApiConfig",
    "DataAwsApiGatewayRestApiEndpointConfiguration",
    "DataAwsApiGatewayVpcLink",
    "DataAwsApiGatewayVpcLinkConfig",
]

publication.publish()
