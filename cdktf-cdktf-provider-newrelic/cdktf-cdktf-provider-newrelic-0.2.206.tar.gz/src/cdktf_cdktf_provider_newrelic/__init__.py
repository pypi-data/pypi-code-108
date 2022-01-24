'''
# Terraform CDK newrelic Provider ~> 2.32

This repo builds and publishes the Terraform newrelic Provider bindings for [cdktf](https://cdk.tf).

## Available Packages

### NPM

The npm package is available at [https://www.npmjs.com/package/@cdktf/provider-newrelic](https://www.npmjs.com/package/@cdktf/provider-newrelic).

`npm install @cdktf/provider-newrelic`

### PyPI

The PyPI package is available at [https://pypi.org/project/cdktf-cdktf-provider-newrelic](https://pypi.org/project/cdktf-cdktf-provider-newrelic).

`pipenv install cdktf-cdktf-provider-newrelic`

### Nuget

The Nuget package is available at [https://www.nuget.org/packages/HashiCorp.Cdktf.Providers.Newrelic](https://www.nuget.org/packages/HashiCorp.Cdktf.Providers.Newrelic).

`dotnet add package HashiCorp.Cdktf.Providers.Newrelic`

### Maven

The Maven package is available at [https://mvnrepository.com/artifact/com.hashicorp/cdktf-provider-newrelic](https://mvnrepository.com/artifact/com.hashicorp/cdktf-provider-newrelic).

```
<dependency>
    <groupId>com.hashicorp</groupId>
    <artifactId>cdktf-provider-newrelic</artifactId>
    <version>[REPLACE WITH DESIRED VERSION]</version>
</dependency>
```

## Docs

Find auto-generated docs for this provider here: [./API.md](./API.md)

## Versioning

This project is explicitly not tracking the Terraform newrelic Provider version 1:1. In fact, it always tracks `latest` of `~> 2.32` with every release. If there are scenarios where you explicitly have to pin your provider version, you can do so by generating the [provider constructs manually](https://cdk.tf/imports).

These are the upstream dependencies:

* [Terraform CDK](https://cdk.tf)
* [Terraform newrelic Provider](https://github.com/terraform-providers/terraform-provider-newrelic)
* [Terraform Engine](https://terraform.io)

If there are breaking changes (backward incompatible) in any of the above, the major version of this project will be bumped. While the Terraform Engine and the Terraform newrelic Provider are relatively stable, the Terraform CDK is in an early stage. Therefore, it's likely that there will be breaking changes.

## Features / Issues / Bugs

Please report bugs and issues to the [terraform cdk](https://cdk.tf) project:

* [Create bug report](https://cdk.tf/bug)
* [Create feature request](https://cdk.tf/feature)

## Contributing

### projen

This is mostly based on [projen](https://github.com/eladb/projen), which takes care of generating the entire repository.

### cdktf-provider-project based on projen

There's a custom [project builder](https://github.com/hashicorp/cdktf-provider-project) which encapsulate the common settings for all `cdktf` providers.

### Provider Version

The provider version can be adjusted in [./.projenrc.js](./.projenrc.js).

### Repository Management

The repository is managed by [Repository Manager](https://github.com/hashicorp/cdktf-repository-manager/)
'''
import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from ._jsii import *

import cdktf
import constructs


class AlertChannel(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-newrelic.AlertChannel",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel newrelic_alert_channel}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        type: builtins.str,
        config: typing.Optional["AlertChannelConfigA"] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel newrelic_alert_channel} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: (Required) The name of the channel. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#name AlertChannel#name}
        :param type: (Required) The type of channel. One of: (webhook, email, opsgenie, pagerduty, slack, user, victorops). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#type AlertChannel#type}
        :param config: config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#config AlertChannel#config}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config_ = AlertChannelConfig(
            name=name,
            type=type,
            config=config,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config_])

    @jsii.member(jsii_name="putConfig")
    def put_config(
        self,
        *,
        api_key: typing.Optional[builtins.str] = None,
        auth_password: typing.Optional[builtins.str] = None,
        auth_type: typing.Optional[builtins.str] = None,
        auth_username: typing.Optional[builtins.str] = None,
        base_url: typing.Optional[builtins.str] = None,
        channel: typing.Optional[builtins.str] = None,
        headers: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        headers_string: typing.Optional[builtins.str] = None,
        include_json_attachment: typing.Optional[builtins.str] = None,
        key: typing.Optional[builtins.str] = None,
        payload: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        payload_string: typing.Optional[builtins.str] = None,
        payload_type: typing.Optional[builtins.str] = None,
        recipients: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
        route_key: typing.Optional[builtins.str] = None,
        service_key: typing.Optional[builtins.str] = None,
        tags: typing.Optional[builtins.str] = None,
        teams: typing.Optional[builtins.str] = None,
        url: typing.Optional[builtins.str] = None,
        user_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param api_key: The API key for integrating with OpsGenie. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#api_key AlertChannel#api_key}
        :param auth_password: Specifies an authentication password for use with a channel. Supported by the webhook channel type. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#auth_password AlertChannel#auth_password}
        :param auth_type: Specifies an authentication method for use with a channel. Supported by the webhook channel type. Only HTTP basic authentication is currently supported via the value BASIC. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#auth_type AlertChannel#auth_type}
        :param auth_username: Specifies an authentication username for use with a channel. Supported by the webhook channel type. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#auth_username AlertChannel#auth_username}
        :param base_url: The base URL of the webhook destination. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#base_url AlertChannel#base_url}
        :param channel: The Slack channel to send notifications to. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#channel AlertChannel#channel}
        :param headers: A map of key/value pairs that represents extra HTTP headers to be sent along with the webhook payload. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#headers AlertChannel#headers}
        :param headers_string: Use instead of headers if the desired payload is more complex than a list of key/value pairs (e.g. a set of headers that makes use of nested objects). The value provided should be a valid JSON string with escaped double quotes. Conflicts with headers. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#headers_string AlertChannel#headers_string}
        :param include_json_attachment: true or false. Flag for whether or not to attach a JSON document containing information about the associated alert to the email that is sent to recipients. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#include_json_attachment AlertChannel#include_json_attachment}
        :param key: The key for integrating with VictorOps. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#key AlertChannel#key}
        :param payload: A map of key/value pairs that represents the webhook payload. Must provide payload_type if setting this argument. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#payload AlertChannel#payload}
        :param payload_string: Use instead of payload if the desired payload is more complex than a list of key/value pairs (e.g. a payload that makes use of nested objects). The value provided should be a valid JSON string with escaped double quotes. Conflicts with payload. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#payload_string AlertChannel#payload_string}
        :param payload_type: Can either be application/json or application/x-www-form-urlencoded. The payload_type argument is required if payload is set. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#payload_type AlertChannel#payload_type}
        :param recipients: A set of recipients for targeting notifications. Multiple values are comma separated. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#recipients AlertChannel#recipients}
        :param region: The data center region to store your data. Valid values are US and EU. Default is US. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#region AlertChannel#region}
        :param route_key: The route key for integrating with VictorOps. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#route_key AlertChannel#route_key}
        :param service_key: Specifies the service key for integrating with Pagerduty. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#service_key AlertChannel#service_key}
        :param tags: A set of tags for targeting notifications. Multiple values are comma separated. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#tags AlertChannel#tags}
        :param teams: A set of teams for targeting notifications. Multiple values are comma separated. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#teams AlertChannel#teams}
        :param url: Your organization's Slack URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#url AlertChannel#url}
        :param user_id: The user ID for use with the user channel type. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#user_id AlertChannel#user_id}
        '''
        value = AlertChannelConfigA(
            api_key=api_key,
            auth_password=auth_password,
            auth_type=auth_type,
            auth_username=auth_username,
            base_url=base_url,
            channel=channel,
            headers=headers,
            headers_string=headers_string,
            include_json_attachment=include_json_attachment,
            key=key,
            payload=payload,
            payload_string=payload_string,
            payload_type=payload_type,
            recipients=recipients,
            region=region,
            route_key=route_key,
            service_key=service_key,
            tags=tags,
            teams=teams,
            url=url,
            user_id=user_id,
        )

        return typing.cast(None, jsii.invoke(self, "putConfig", [value]))

    @jsii.member(jsii_name="resetConfig")
    def reset_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConfig", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="config")
    def config(self) -> "AlertChannelConfigAOutputReference":
        return typing.cast("AlertChannelConfigAOutputReference", jsii.get(self, "config"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="configInput")
    def config_input(self) -> typing.Optional["AlertChannelConfigA"]:
        return typing.cast(typing.Optional["AlertChannelConfigA"], jsii.get(self, "configInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        jsii.set(self, "type", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.AlertChannelConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "type": "type",
        "config": "config",
    },
)
class AlertChannelConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        type: builtins.str,
        config: typing.Optional["AlertChannelConfigA"] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: (Required) The name of the channel. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#name AlertChannel#name}
        :param type: (Required) The type of channel. One of: (webhook, email, opsgenie, pagerduty, slack, user, victorops). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#type AlertChannel#type}
        :param config: config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#config AlertChannel#config}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(config, dict):
            config = AlertChannelConfigA(**config)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
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
        if config is not None:
            self._values["config"] = config

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
        '''(Required) The name of the channel.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#name AlertChannel#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''(Required) The type of channel. One of: (webhook, email, opsgenie, pagerduty, slack, user, victorops).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#type AlertChannel#type}
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def config(self) -> typing.Optional["AlertChannelConfigA"]:
        '''config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#config AlertChannel#config}
        '''
        result = self._values.get("config")
        return typing.cast(typing.Optional["AlertChannelConfigA"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AlertChannelConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.AlertChannelConfigA",
    jsii_struct_bases=[],
    name_mapping={
        "api_key": "apiKey",
        "auth_password": "authPassword",
        "auth_type": "authType",
        "auth_username": "authUsername",
        "base_url": "baseUrl",
        "channel": "channel",
        "headers": "headers",
        "headers_string": "headersString",
        "include_json_attachment": "includeJsonAttachment",
        "key": "key",
        "payload": "payload",
        "payload_string": "payloadString",
        "payload_type": "payloadType",
        "recipients": "recipients",
        "region": "region",
        "route_key": "routeKey",
        "service_key": "serviceKey",
        "tags": "tags",
        "teams": "teams",
        "url": "url",
        "user_id": "userId",
    },
)
class AlertChannelConfigA:
    def __init__(
        self,
        *,
        api_key: typing.Optional[builtins.str] = None,
        auth_password: typing.Optional[builtins.str] = None,
        auth_type: typing.Optional[builtins.str] = None,
        auth_username: typing.Optional[builtins.str] = None,
        base_url: typing.Optional[builtins.str] = None,
        channel: typing.Optional[builtins.str] = None,
        headers: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        headers_string: typing.Optional[builtins.str] = None,
        include_json_attachment: typing.Optional[builtins.str] = None,
        key: typing.Optional[builtins.str] = None,
        payload: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        payload_string: typing.Optional[builtins.str] = None,
        payload_type: typing.Optional[builtins.str] = None,
        recipients: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
        route_key: typing.Optional[builtins.str] = None,
        service_key: typing.Optional[builtins.str] = None,
        tags: typing.Optional[builtins.str] = None,
        teams: typing.Optional[builtins.str] = None,
        url: typing.Optional[builtins.str] = None,
        user_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param api_key: The API key for integrating with OpsGenie. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#api_key AlertChannel#api_key}
        :param auth_password: Specifies an authentication password for use with a channel. Supported by the webhook channel type. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#auth_password AlertChannel#auth_password}
        :param auth_type: Specifies an authentication method for use with a channel. Supported by the webhook channel type. Only HTTP basic authentication is currently supported via the value BASIC. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#auth_type AlertChannel#auth_type}
        :param auth_username: Specifies an authentication username for use with a channel. Supported by the webhook channel type. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#auth_username AlertChannel#auth_username}
        :param base_url: The base URL of the webhook destination. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#base_url AlertChannel#base_url}
        :param channel: The Slack channel to send notifications to. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#channel AlertChannel#channel}
        :param headers: A map of key/value pairs that represents extra HTTP headers to be sent along with the webhook payload. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#headers AlertChannel#headers}
        :param headers_string: Use instead of headers if the desired payload is more complex than a list of key/value pairs (e.g. a set of headers that makes use of nested objects). The value provided should be a valid JSON string with escaped double quotes. Conflicts with headers. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#headers_string AlertChannel#headers_string}
        :param include_json_attachment: true or false. Flag for whether or not to attach a JSON document containing information about the associated alert to the email that is sent to recipients. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#include_json_attachment AlertChannel#include_json_attachment}
        :param key: The key for integrating with VictorOps. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#key AlertChannel#key}
        :param payload: A map of key/value pairs that represents the webhook payload. Must provide payload_type if setting this argument. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#payload AlertChannel#payload}
        :param payload_string: Use instead of payload if the desired payload is more complex than a list of key/value pairs (e.g. a payload that makes use of nested objects). The value provided should be a valid JSON string with escaped double quotes. Conflicts with payload. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#payload_string AlertChannel#payload_string}
        :param payload_type: Can either be application/json or application/x-www-form-urlencoded. The payload_type argument is required if payload is set. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#payload_type AlertChannel#payload_type}
        :param recipients: A set of recipients for targeting notifications. Multiple values are comma separated. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#recipients AlertChannel#recipients}
        :param region: The data center region to store your data. Valid values are US and EU. Default is US. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#region AlertChannel#region}
        :param route_key: The route key for integrating with VictorOps. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#route_key AlertChannel#route_key}
        :param service_key: Specifies the service key for integrating with Pagerduty. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#service_key AlertChannel#service_key}
        :param tags: A set of tags for targeting notifications. Multiple values are comma separated. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#tags AlertChannel#tags}
        :param teams: A set of teams for targeting notifications. Multiple values are comma separated. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#teams AlertChannel#teams}
        :param url: Your organization's Slack URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#url AlertChannel#url}
        :param user_id: The user ID for use with the user channel type. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#user_id AlertChannel#user_id}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if api_key is not None:
            self._values["api_key"] = api_key
        if auth_password is not None:
            self._values["auth_password"] = auth_password
        if auth_type is not None:
            self._values["auth_type"] = auth_type
        if auth_username is not None:
            self._values["auth_username"] = auth_username
        if base_url is not None:
            self._values["base_url"] = base_url
        if channel is not None:
            self._values["channel"] = channel
        if headers is not None:
            self._values["headers"] = headers
        if headers_string is not None:
            self._values["headers_string"] = headers_string
        if include_json_attachment is not None:
            self._values["include_json_attachment"] = include_json_attachment
        if key is not None:
            self._values["key"] = key
        if payload is not None:
            self._values["payload"] = payload
        if payload_string is not None:
            self._values["payload_string"] = payload_string
        if payload_type is not None:
            self._values["payload_type"] = payload_type
        if recipients is not None:
            self._values["recipients"] = recipients
        if region is not None:
            self._values["region"] = region
        if route_key is not None:
            self._values["route_key"] = route_key
        if service_key is not None:
            self._values["service_key"] = service_key
        if tags is not None:
            self._values["tags"] = tags
        if teams is not None:
            self._values["teams"] = teams
        if url is not None:
            self._values["url"] = url
        if user_id is not None:
            self._values["user_id"] = user_id

    @builtins.property
    def api_key(self) -> typing.Optional[builtins.str]:
        '''The API key for integrating with OpsGenie.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#api_key AlertChannel#api_key}
        '''
        result = self._values.get("api_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def auth_password(self) -> typing.Optional[builtins.str]:
        '''Specifies an authentication password for use with a channel. Supported by the webhook channel type.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#auth_password AlertChannel#auth_password}
        '''
        result = self._values.get("auth_password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def auth_type(self) -> typing.Optional[builtins.str]:
        '''Specifies an authentication method for use with a channel.

        Supported by the webhook channel type. Only HTTP basic authentication is currently supported via the value BASIC.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#auth_type AlertChannel#auth_type}
        '''
        result = self._values.get("auth_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def auth_username(self) -> typing.Optional[builtins.str]:
        '''Specifies an authentication username for use with a channel. Supported by the webhook channel type.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#auth_username AlertChannel#auth_username}
        '''
        result = self._values.get("auth_username")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def base_url(self) -> typing.Optional[builtins.str]:
        '''The base URL of the webhook destination.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#base_url AlertChannel#base_url}
        '''
        result = self._values.get("base_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def channel(self) -> typing.Optional[builtins.str]:
        '''The Slack channel to send notifications to.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#channel AlertChannel#channel}
        '''
        result = self._values.get("channel")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def headers(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''A map of key/value pairs that represents extra HTTP headers to be sent along with the webhook payload.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#headers AlertChannel#headers}
        '''
        result = self._values.get("headers")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def headers_string(self) -> typing.Optional[builtins.str]:
        '''Use instead of headers if the desired payload is more complex than a list of key/value pairs (e.g. a set of headers that makes use of nested objects). The value provided should be a valid JSON string with escaped double quotes. Conflicts with headers.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#headers_string AlertChannel#headers_string}
        '''
        result = self._values.get("headers_string")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def include_json_attachment(self) -> typing.Optional[builtins.str]:
        '''true or false.

        Flag for whether or not to attach a JSON document containing information about the associated alert to the email that is sent to recipients.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#include_json_attachment AlertChannel#include_json_attachment}
        '''
        result = self._values.get("include_json_attachment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key(self) -> typing.Optional[builtins.str]:
        '''The key for integrating with VictorOps.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#key AlertChannel#key}
        '''
        result = self._values.get("key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def payload(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''A map of key/value pairs that represents the webhook payload. Must provide payload_type if setting this argument.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#payload AlertChannel#payload}
        '''
        result = self._values.get("payload")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def payload_string(self) -> typing.Optional[builtins.str]:
        '''Use instead of payload if the desired payload is more complex than a list of key/value pairs (e.g. a payload that makes use of nested objects). The value provided should be a valid JSON string with escaped double quotes. Conflicts with payload.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#payload_string AlertChannel#payload_string}
        '''
        result = self._values.get("payload_string")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def payload_type(self) -> typing.Optional[builtins.str]:
        '''Can either be application/json or application/x-www-form-urlencoded. The payload_type argument is required if payload is set.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#payload_type AlertChannel#payload_type}
        '''
        result = self._values.get("payload_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def recipients(self) -> typing.Optional[builtins.str]:
        '''A set of recipients for targeting notifications. Multiple values are comma separated.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#recipients AlertChannel#recipients}
        '''
        result = self._values.get("recipients")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''The data center region to store your data. Valid values are US and EU. Default is US.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#region AlertChannel#region}
        '''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def route_key(self) -> typing.Optional[builtins.str]:
        '''The route key for integrating with VictorOps.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#route_key AlertChannel#route_key}
        '''
        result = self._values.get("route_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def service_key(self) -> typing.Optional[builtins.str]:
        '''Specifies the service key for integrating with Pagerduty.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#service_key AlertChannel#service_key}
        '''
        result = self._values.get("service_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[builtins.str]:
        '''A set of tags for targeting notifications. Multiple values are comma separated.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#tags AlertChannel#tags}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def teams(self) -> typing.Optional[builtins.str]:
        '''A set of teams for targeting notifications. Multiple values are comma separated.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#teams AlertChannel#teams}
        '''
        result = self._values.get("teams")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def url(self) -> typing.Optional[builtins.str]:
        '''Your organization's Slack URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#url AlertChannel#url}
        '''
        result = self._values.get("url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def user_id(self) -> typing.Optional[builtins.str]:
        '''The user ID for use with the user channel type.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_channel#user_id AlertChannel#user_id}
        '''
        result = self._values.get("user_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AlertChannelConfigA(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AlertChannelConfigAOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-newrelic.AlertChannelConfigAOutputReference",
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

    @jsii.member(jsii_name="resetApiKey")
    def reset_api_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetApiKey", []))

    @jsii.member(jsii_name="resetAuthPassword")
    def reset_auth_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthPassword", []))

    @jsii.member(jsii_name="resetAuthType")
    def reset_auth_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthType", []))

    @jsii.member(jsii_name="resetAuthUsername")
    def reset_auth_username(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthUsername", []))

    @jsii.member(jsii_name="resetBaseUrl")
    def reset_base_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBaseUrl", []))

    @jsii.member(jsii_name="resetChannel")
    def reset_channel(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetChannel", []))

    @jsii.member(jsii_name="resetHeaders")
    def reset_headers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHeaders", []))

    @jsii.member(jsii_name="resetHeadersString")
    def reset_headers_string(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHeadersString", []))

    @jsii.member(jsii_name="resetIncludeJsonAttachment")
    def reset_include_json_attachment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIncludeJsonAttachment", []))

    @jsii.member(jsii_name="resetKey")
    def reset_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKey", []))

    @jsii.member(jsii_name="resetPayload")
    def reset_payload(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPayload", []))

    @jsii.member(jsii_name="resetPayloadString")
    def reset_payload_string(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPayloadString", []))

    @jsii.member(jsii_name="resetPayloadType")
    def reset_payload_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPayloadType", []))

    @jsii.member(jsii_name="resetRecipients")
    def reset_recipients(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRecipients", []))

    @jsii.member(jsii_name="resetRegion")
    def reset_region(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegion", []))

    @jsii.member(jsii_name="resetRouteKey")
    def reset_route_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRouteKey", []))

    @jsii.member(jsii_name="resetServiceKey")
    def reset_service_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServiceKey", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTeams")
    def reset_teams(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTeams", []))

    @jsii.member(jsii_name="resetUrl")
    def reset_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUrl", []))

    @jsii.member(jsii_name="resetUserId")
    def reset_user_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserId", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiKeyInput")
    def api_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "apiKeyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authPasswordInput")
    def auth_password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "authPasswordInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authTypeInput")
    def auth_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "authTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authUsernameInput")
    def auth_username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "authUsernameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="baseUrlInput")
    def base_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "baseUrlInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="channelInput")
    def channel_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "channelInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="headersInput")
    def headers_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "headersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="headersStringInput")
    def headers_string_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "headersStringInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="includeJsonAttachmentInput")
    def include_json_attachment_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "includeJsonAttachmentInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyInput")
    def key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="payloadInput")
    def payload_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "payloadInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="payloadStringInput")
    def payload_string_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "payloadStringInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="payloadTypeInput")
    def payload_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "payloadTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="recipientsInput")
    def recipients_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "recipientsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="regionInput")
    def region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "regionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="routeKeyInput")
    def route_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "routeKeyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceKeyInput")
    def service_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serviceKeyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="teamsInput")
    def teams_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "teamsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="urlInput")
    def url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "urlInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userIdInput")
    def user_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiKey")
    def api_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "apiKey"))

    @api_key.setter
    def api_key(self, value: builtins.str) -> None:
        jsii.set(self, "apiKey", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authPassword")
    def auth_password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authPassword"))

    @auth_password.setter
    def auth_password(self, value: builtins.str) -> None:
        jsii.set(self, "authPassword", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authType")
    def auth_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authType"))

    @auth_type.setter
    def auth_type(self, value: builtins.str) -> None:
        jsii.set(self, "authType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authUsername")
    def auth_username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authUsername"))

    @auth_username.setter
    def auth_username(self, value: builtins.str) -> None:
        jsii.set(self, "authUsername", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="baseUrl")
    def base_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "baseUrl"))

    @base_url.setter
    def base_url(self, value: builtins.str) -> None:
        jsii.set(self, "baseUrl", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="channel")
    def channel(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "channel"))

    @channel.setter
    def channel(self, value: builtins.str) -> None:
        jsii.set(self, "channel", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="headers")
    def headers(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "headers"))

    @headers.setter
    def headers(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "headers", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="headersString")
    def headers_string(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "headersString"))

    @headers_string.setter
    def headers_string(self, value: builtins.str) -> None:
        jsii.set(self, "headersString", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="includeJsonAttachment")
    def include_json_attachment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "includeJsonAttachment"))

    @include_json_attachment.setter
    def include_json_attachment(self, value: builtins.str) -> None:
        jsii.set(self, "includeJsonAttachment", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        jsii.set(self, "key", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="payload")
    def payload(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "payload"))

    @payload.setter
    def payload(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "payload", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="payloadString")
    def payload_string(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "payloadString"))

    @payload_string.setter
    def payload_string(self, value: builtins.str) -> None:
        jsii.set(self, "payloadString", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="payloadType")
    def payload_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "payloadType"))

    @payload_type.setter
    def payload_type(self, value: builtins.str) -> None:
        jsii.set(self, "payloadType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="recipients")
    def recipients(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "recipients"))

    @recipients.setter
    def recipients(self, value: builtins.str) -> None:
        jsii.set(self, "recipients", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @region.setter
    def region(self, value: builtins.str) -> None:
        jsii.set(self, "region", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="routeKey")
    def route_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "routeKey"))

    @route_key.setter
    def route_key(self, value: builtins.str) -> None:
        jsii.set(self, "routeKey", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceKey")
    def service_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceKey"))

    @service_key.setter
    def service_key(self, value: builtins.str) -> None:
        jsii.set(self, "serviceKey", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: builtins.str) -> None:
        jsii.set(self, "tags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="teams")
    def teams(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "teams"))

    @teams.setter
    def teams(self, value: builtins.str) -> None:
        jsii.set(self, "teams", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @url.setter
    def url(self, value: builtins.str) -> None:
        jsii.set(self, "url", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userId")
    def user_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userId"))

    @user_id.setter
    def user_id(self, value: builtins.str) -> None:
        jsii.set(self, "userId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[AlertChannelConfigA]:
        return typing.cast(typing.Optional[AlertChannelConfigA], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[AlertChannelConfigA]) -> None:
        jsii.set(self, "internalValue", value)


class AlertCondition(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-newrelic.AlertCondition",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/newrelic/r/alert_condition newrelic_alert_condition}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        entities: typing.Sequence[jsii.Number],
        metric: builtins.str,
        name: builtins.str,
        policy_id: jsii.Number,
        term: typing.Sequence["AlertConditionTerm"],
        type: builtins.str,
        condition_scope: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        gc_metric: typing.Optional[builtins.str] = None,
        runbook_url: typing.Optional[builtins.str] = None,
        user_defined_metric: typing.Optional[builtins.str] = None,
        user_defined_value_function: typing.Optional[builtins.str] = None,
        violation_close_timer: typing.Optional[jsii.Number] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/newrelic/r/alert_condition newrelic_alert_condition} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param entities: The instance IDs associated with this condition. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_condition#entities AlertCondition#entities}
        :param metric: The metric field accepts parameters based on the type set. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_condition#metric AlertCondition#metric}
        :param name: The title of the condition. Must be between 1 and 128 characters, inclusive. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_condition#name AlertCondition#name}
        :param policy_id: The ID of the policy where this condition should be used. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_condition#policy_id AlertCondition#policy_id}
        :param term: term block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_condition#term AlertCondition#term}
        :param type: The type of condition. One of: (apm_kt_metric, browser_metric, mobile_metric, servers_metric, apm_app_metric, apm_jvm_metric). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_condition#type AlertCondition#type}
        :param condition_scope: One of (application, instance). Choose application for most scenarios. If you are using the JVM plugin in New Relic, the instance setting allows your condition to trigger for specific app instances. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_condition#condition_scope AlertCondition#condition_scope}
        :param enabled: Whether the condition is enabled. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_condition#enabled AlertCondition#enabled}
        :param gc_metric: A valid Garbage Collection metric e.g. GC/G1 Young Generation. This is required if you are using apm_jvm_metric with gc_cpu_time condition type. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_condition#gc_metric AlertCondition#gc_metric}
        :param runbook_url: Runbook URL to display in notifications. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_condition#runbook_url AlertCondition#runbook_url}
        :param user_defined_metric: A custom metric to be evaluated. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_condition#user_defined_metric AlertCondition#user_defined_metric}
        :param user_defined_value_function: One of: (average, min, max, total, sample_size). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_condition#user_defined_value_function AlertCondition#user_defined_value_function}
        :param violation_close_timer: Automatically close instance-based violations, including JVM health metric violations, after the number of hours specified. Must be: 1, 2, 4, 8, 12 or 24. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_condition#violation_close_timer AlertCondition#violation_close_timer}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = AlertConditionConfig(
            entities=entities,
            metric=metric,
            name=name,
            policy_id=policy_id,
            term=term,
            type=type,
            condition_scope=condition_scope,
            enabled=enabled,
            gc_metric=gc_metric,
            runbook_url=runbook_url,
            user_defined_metric=user_defined_metric,
            user_defined_value_function=user_defined_value_function,
            violation_close_timer=violation_close_timer,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetConditionScope")
    def reset_condition_scope(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConditionScope", []))

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="resetGcMetric")
    def reset_gc_metric(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGcMetric", []))

    @jsii.member(jsii_name="resetRunbookUrl")
    def reset_runbook_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRunbookUrl", []))

    @jsii.member(jsii_name="resetUserDefinedMetric")
    def reset_user_defined_metric(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserDefinedMetric", []))

    @jsii.member(jsii_name="resetUserDefinedValueFunction")
    def reset_user_defined_value_function(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserDefinedValueFunction", []))

    @jsii.member(jsii_name="resetViolationCloseTimer")
    def reset_violation_close_timer(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetViolationCloseTimer", []))

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
    @jsii.member(jsii_name="conditionScopeInput")
    def condition_scope_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "conditionScopeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="entitiesInput")
    def entities_input(self) -> typing.Optional[typing.List[jsii.Number]]:
        return typing.cast(typing.Optional[typing.List[jsii.Number]], jsii.get(self, "entitiesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="gcMetricInput")
    def gc_metric_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "gcMetricInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="metricInput")
    def metric_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "metricInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyIdInput")
    def policy_id_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "policyIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="runbookUrlInput")
    def runbook_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "runbookUrlInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="termInput")
    def term_input(self) -> typing.Optional[typing.List["AlertConditionTerm"]]:
        return typing.cast(typing.Optional[typing.List["AlertConditionTerm"]], jsii.get(self, "termInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userDefinedMetricInput")
    def user_defined_metric_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userDefinedMetricInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userDefinedValueFunctionInput")
    def user_defined_value_function_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userDefinedValueFunctionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="violationCloseTimerInput")
    def violation_close_timer_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "violationCloseTimerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="conditionScope")
    def condition_scope(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "conditionScope"))

    @condition_scope.setter
    def condition_scope(self, value: builtins.str) -> None:
        jsii.set(self, "conditionScope", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "enabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="entities")
    def entities(self) -> typing.List[jsii.Number]:
        return typing.cast(typing.List[jsii.Number], jsii.get(self, "entities"))

    @entities.setter
    def entities(self, value: typing.List[jsii.Number]) -> None:
        jsii.set(self, "entities", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="gcMetric")
    def gc_metric(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gcMetric"))

    @gc_metric.setter
    def gc_metric(self, value: builtins.str) -> None:
        jsii.set(self, "gcMetric", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="metric")
    def metric(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "metric"))

    @metric.setter
    def metric(self, value: builtins.str) -> None:
        jsii.set(self, "metric", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyId")
    def policy_id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "policyId"))

    @policy_id.setter
    def policy_id(self, value: jsii.Number) -> None:
        jsii.set(self, "policyId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="runbookUrl")
    def runbook_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "runbookUrl"))

    @runbook_url.setter
    def runbook_url(self, value: builtins.str) -> None:
        jsii.set(self, "runbookUrl", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="term")
    def term(self) -> typing.List["AlertConditionTerm"]:
        return typing.cast(typing.List["AlertConditionTerm"], jsii.get(self, "term"))

    @term.setter
    def term(self, value: typing.List["AlertConditionTerm"]) -> None:
        jsii.set(self, "term", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        jsii.set(self, "type", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userDefinedMetric")
    def user_defined_metric(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userDefinedMetric"))

    @user_defined_metric.setter
    def user_defined_metric(self, value: builtins.str) -> None:
        jsii.set(self, "userDefinedMetric", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userDefinedValueFunction")
    def user_defined_value_function(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userDefinedValueFunction"))

    @user_defined_value_function.setter
    def user_defined_value_function(self, value: builtins.str) -> None:
        jsii.set(self, "userDefinedValueFunction", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="violationCloseTimer")
    def violation_close_timer(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "violationCloseTimer"))

    @violation_close_timer.setter
    def violation_close_timer(self, value: jsii.Number) -> None:
        jsii.set(self, "violationCloseTimer", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.AlertConditionConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "entities": "entities",
        "metric": "metric",
        "name": "name",
        "policy_id": "policyId",
        "term": "term",
        "type": "type",
        "condition_scope": "conditionScope",
        "enabled": "enabled",
        "gc_metric": "gcMetric",
        "runbook_url": "runbookUrl",
        "user_defined_metric": "userDefinedMetric",
        "user_defined_value_function": "userDefinedValueFunction",
        "violation_close_timer": "violationCloseTimer",
    },
)
class AlertConditionConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        entities: typing.Sequence[jsii.Number],
        metric: builtins.str,
        name: builtins.str,
        policy_id: jsii.Number,
        term: typing.Sequence["AlertConditionTerm"],
        type: builtins.str,
        condition_scope: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        gc_metric: typing.Optional[builtins.str] = None,
        runbook_url: typing.Optional[builtins.str] = None,
        user_defined_metric: typing.Optional[builtins.str] = None,
        user_defined_value_function: typing.Optional[builtins.str] = None,
        violation_close_timer: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param entities: The instance IDs associated with this condition. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_condition#entities AlertCondition#entities}
        :param metric: The metric field accepts parameters based on the type set. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_condition#metric AlertCondition#metric}
        :param name: The title of the condition. Must be between 1 and 128 characters, inclusive. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_condition#name AlertCondition#name}
        :param policy_id: The ID of the policy where this condition should be used. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_condition#policy_id AlertCondition#policy_id}
        :param term: term block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_condition#term AlertCondition#term}
        :param type: The type of condition. One of: (apm_kt_metric, browser_metric, mobile_metric, servers_metric, apm_app_metric, apm_jvm_metric). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_condition#type AlertCondition#type}
        :param condition_scope: One of (application, instance). Choose application for most scenarios. If you are using the JVM plugin in New Relic, the instance setting allows your condition to trigger for specific app instances. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_condition#condition_scope AlertCondition#condition_scope}
        :param enabled: Whether the condition is enabled. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_condition#enabled AlertCondition#enabled}
        :param gc_metric: A valid Garbage Collection metric e.g. GC/G1 Young Generation. This is required if you are using apm_jvm_metric with gc_cpu_time condition type. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_condition#gc_metric AlertCondition#gc_metric}
        :param runbook_url: Runbook URL to display in notifications. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_condition#runbook_url AlertCondition#runbook_url}
        :param user_defined_metric: A custom metric to be evaluated. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_condition#user_defined_metric AlertCondition#user_defined_metric}
        :param user_defined_value_function: One of: (average, min, max, total, sample_size). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_condition#user_defined_value_function AlertCondition#user_defined_value_function}
        :param violation_close_timer: Automatically close instance-based violations, including JVM health metric violations, after the number of hours specified. Must be: 1, 2, 4, 8, 12 or 24. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_condition#violation_close_timer AlertCondition#violation_close_timer}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "entities": entities,
            "metric": metric,
            "name": name,
            "policy_id": policy_id,
            "term": term,
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
        if condition_scope is not None:
            self._values["condition_scope"] = condition_scope
        if enabled is not None:
            self._values["enabled"] = enabled
        if gc_metric is not None:
            self._values["gc_metric"] = gc_metric
        if runbook_url is not None:
            self._values["runbook_url"] = runbook_url
        if user_defined_metric is not None:
            self._values["user_defined_metric"] = user_defined_metric
        if user_defined_value_function is not None:
            self._values["user_defined_value_function"] = user_defined_value_function
        if violation_close_timer is not None:
            self._values["violation_close_timer"] = violation_close_timer

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
    def entities(self) -> typing.List[jsii.Number]:
        '''The instance IDs associated with this condition.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_condition#entities AlertCondition#entities}
        '''
        result = self._values.get("entities")
        assert result is not None, "Required property 'entities' is missing"
        return typing.cast(typing.List[jsii.Number], result)

    @builtins.property
    def metric(self) -> builtins.str:
        '''The metric field accepts parameters based on the type set.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_condition#metric AlertCondition#metric}
        '''
        result = self._values.get("metric")
        assert result is not None, "Required property 'metric' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The title of the condition. Must be between 1 and 128 characters, inclusive.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_condition#name AlertCondition#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def policy_id(self) -> jsii.Number:
        '''The ID of the policy where this condition should be used.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_condition#policy_id AlertCondition#policy_id}
        '''
        result = self._values.get("policy_id")
        assert result is not None, "Required property 'policy_id' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def term(self) -> typing.List["AlertConditionTerm"]:
        '''term block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_condition#term AlertCondition#term}
        '''
        result = self._values.get("term")
        assert result is not None, "Required property 'term' is missing"
        return typing.cast(typing.List["AlertConditionTerm"], result)

    @builtins.property
    def type(self) -> builtins.str:
        '''The type of condition. One of: (apm_kt_metric, browser_metric, mobile_metric, servers_metric, apm_app_metric, apm_jvm_metric).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_condition#type AlertCondition#type}
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def condition_scope(self) -> typing.Optional[builtins.str]:
        '''One of (application, instance).

        Choose application for most scenarios. If you are using the JVM plugin in New Relic, the instance setting allows your condition to trigger for specific app instances.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_condition#condition_scope AlertCondition#condition_scope}
        '''
        result = self._values.get("condition_scope")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Whether the condition is enabled.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_condition#enabled AlertCondition#enabled}
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def gc_metric(self) -> typing.Optional[builtins.str]:
        '''A valid Garbage Collection metric e.g. GC/G1 Young Generation. This is required if you are using apm_jvm_metric with gc_cpu_time condition type.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_condition#gc_metric AlertCondition#gc_metric}
        '''
        result = self._values.get("gc_metric")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def runbook_url(self) -> typing.Optional[builtins.str]:
        '''Runbook URL to display in notifications.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_condition#runbook_url AlertCondition#runbook_url}
        '''
        result = self._values.get("runbook_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def user_defined_metric(self) -> typing.Optional[builtins.str]:
        '''A custom metric to be evaluated.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_condition#user_defined_metric AlertCondition#user_defined_metric}
        '''
        result = self._values.get("user_defined_metric")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def user_defined_value_function(self) -> typing.Optional[builtins.str]:
        '''One of: (average, min, max, total, sample_size).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_condition#user_defined_value_function AlertCondition#user_defined_value_function}
        '''
        result = self._values.get("user_defined_value_function")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def violation_close_timer(self) -> typing.Optional[jsii.Number]:
        '''Automatically close instance-based violations, including JVM health metric violations, after the number of hours specified.

        Must be: 1, 2, 4, 8, 12 or 24.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_condition#violation_close_timer AlertCondition#violation_close_timer}
        '''
        result = self._values.get("violation_close_timer")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AlertConditionConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.AlertConditionTerm",
    jsii_struct_bases=[],
    name_mapping={
        "duration": "duration",
        "threshold": "threshold",
        "time_function": "timeFunction",
        "operator": "operator",
        "priority": "priority",
    },
)
class AlertConditionTerm:
    def __init__(
        self,
        *,
        duration: jsii.Number,
        threshold: jsii.Number,
        time_function: builtins.str,
        operator: typing.Optional[builtins.str] = None,
        priority: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param duration: In minutes, must be in the range of 5 to 120, inclusive. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_condition#duration AlertCondition#duration}
        :param threshold: Must be 0 or greater. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_condition#threshold AlertCondition#threshold}
        :param time_function: One of (all, any). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_condition#time_function AlertCondition#time_function}
        :param operator: One of (above, below, equal). Defaults to equal. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_condition#operator AlertCondition#operator}
        :param priority: One of (critical, warning). Defaults to critical. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_condition#priority AlertCondition#priority}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "duration": duration,
            "threshold": threshold,
            "time_function": time_function,
        }
        if operator is not None:
            self._values["operator"] = operator
        if priority is not None:
            self._values["priority"] = priority

    @builtins.property
    def duration(self) -> jsii.Number:
        '''In minutes, must be in the range of 5 to 120, inclusive.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_condition#duration AlertCondition#duration}
        '''
        result = self._values.get("duration")
        assert result is not None, "Required property 'duration' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def threshold(self) -> jsii.Number:
        '''Must be 0 or greater.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_condition#threshold AlertCondition#threshold}
        '''
        result = self._values.get("threshold")
        assert result is not None, "Required property 'threshold' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def time_function(self) -> builtins.str:
        '''One of (all, any).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_condition#time_function AlertCondition#time_function}
        '''
        result = self._values.get("time_function")
        assert result is not None, "Required property 'time_function' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def operator(self) -> typing.Optional[builtins.str]:
        '''One of (above, below, equal). Defaults to equal.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_condition#operator AlertCondition#operator}
        '''
        result = self._values.get("operator")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def priority(self) -> typing.Optional[builtins.str]:
        '''One of (critical, warning). Defaults to critical.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_condition#priority AlertCondition#priority}
        '''
        result = self._values.get("priority")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AlertConditionTerm(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AlertMutingRule(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-newrelic.AlertMutingRule",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/newrelic/r/alert_muting_rule newrelic_alert_muting_rule}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        condition: "AlertMutingRuleCondition",
        enabled: typing.Union[builtins.bool, cdktf.IResolvable],
        name: builtins.str,
        account_id: typing.Optional[jsii.Number] = None,
        description: typing.Optional[builtins.str] = None,
        schedule: typing.Optional["AlertMutingRuleSchedule"] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/newrelic/r/alert_muting_rule newrelic_alert_muting_rule} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param condition: condition block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_muting_rule#condition AlertMutingRule#condition}
        :param enabled: Whether the MutingRule is enabled. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_muting_rule#enabled AlertMutingRule#enabled}
        :param name: The name of the MutingRule. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_muting_rule#name AlertMutingRule#name}
        :param account_id: The account id of the MutingRule.. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_muting_rule#account_id AlertMutingRule#account_id}
        :param description: The description of the MutingRule. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_muting_rule#description AlertMutingRule#description}
        :param schedule: schedule block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_muting_rule#schedule AlertMutingRule#schedule}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = AlertMutingRuleConfig(
            condition=condition,
            enabled=enabled,
            name=name,
            account_id=account_id,
            description=description,
            schedule=schedule,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putCondition")
    def put_condition(
        self,
        *,
        conditions: typing.Sequence["AlertMutingRuleConditionConditions"],
        operator: builtins.str,
    ) -> None:
        '''
        :param conditions: conditions block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_muting_rule#conditions AlertMutingRule#conditions}
        :param operator: The operator used to combine all the MutingRuleConditions within the group. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_muting_rule#operator AlertMutingRule#operator}
        '''
        value = AlertMutingRuleCondition(conditions=conditions, operator=operator)

        return typing.cast(None, jsii.invoke(self, "putCondition", [value]))

    @jsii.member(jsii_name="putSchedule")
    def put_schedule(
        self,
        *,
        time_zone: builtins.str,
        end_repeat: typing.Optional[builtins.str] = None,
        end_time: typing.Optional[builtins.str] = None,
        repeat: typing.Optional[builtins.str] = None,
        repeat_count: typing.Optional[jsii.Number] = None,
        start_time: typing.Optional[builtins.str] = None,
        weekly_repeat_days: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param time_zone: The time zone that applies to the MutingRule schedule. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_muting_rule#time_zone AlertMutingRule#time_zone}
        :param end_repeat: The datetime stamp when the MutingRule schedule should stop repeating. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_muting_rule#end_repeat AlertMutingRule#end_repeat}
        :param end_time: The datetime stamp representing when the MutingRule should end. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_muting_rule#end_time AlertMutingRule#end_time}
        :param repeat: The frequency the MutingRule schedule repeats. One of [DAILY, WEEKLY, MONTHLY]. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_muting_rule#repeat AlertMutingRule#repeat}
        :param repeat_count: The number of times the MutingRule schedule should repeat. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_muting_rule#repeat_count AlertMutingRule#repeat_count}
        :param start_time: The datetime stamp representing when the MutingRule should start. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_muting_rule#start_time AlertMutingRule#start_time}
        :param weekly_repeat_days: The day(s) of the week that a MutingRule should repeat when the repeat field is set to WEEKLY. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_muting_rule#weekly_repeat_days AlertMutingRule#weekly_repeat_days}
        '''
        value = AlertMutingRuleSchedule(
            time_zone=time_zone,
            end_repeat=end_repeat,
            end_time=end_time,
            repeat=repeat,
            repeat_count=repeat_count,
            start_time=start_time,
            weekly_repeat_days=weekly_repeat_days,
        )

        return typing.cast(None, jsii.invoke(self, "putSchedule", [value]))

    @jsii.member(jsii_name="resetAccountId")
    def reset_account_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccountId", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetSchedule")
    def reset_schedule(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSchedule", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="condition")
    def condition(self) -> "AlertMutingRuleConditionOutputReference":
        return typing.cast("AlertMutingRuleConditionOutputReference", jsii.get(self, "condition"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="schedule")
    def schedule(self) -> "AlertMutingRuleScheduleOutputReference":
        return typing.cast("AlertMutingRuleScheduleOutputReference", jsii.get(self, "schedule"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "accountIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="conditionInput")
    def condition_input(self) -> typing.Optional["AlertMutingRuleCondition"]:
        return typing.cast(typing.Optional["AlertMutingRuleCondition"], jsii.get(self, "conditionInput"))

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
    @jsii.member(jsii_name="scheduleInput")
    def schedule_input(self) -> typing.Optional["AlertMutingRuleSchedule"]:
        return typing.cast(typing.Optional["AlertMutingRuleSchedule"], jsii.get(self, "scheduleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: jsii.Number) -> None:
        jsii.set(self, "accountId", value)

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


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.AlertMutingRuleCondition",
    jsii_struct_bases=[],
    name_mapping={"conditions": "conditions", "operator": "operator"},
)
class AlertMutingRuleCondition:
    def __init__(
        self,
        *,
        conditions: typing.Sequence["AlertMutingRuleConditionConditions"],
        operator: builtins.str,
    ) -> None:
        '''
        :param conditions: conditions block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_muting_rule#conditions AlertMutingRule#conditions}
        :param operator: The operator used to combine all the MutingRuleConditions within the group. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_muting_rule#operator AlertMutingRule#operator}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "conditions": conditions,
            "operator": operator,
        }

    @builtins.property
    def conditions(self) -> typing.List["AlertMutingRuleConditionConditions"]:
        '''conditions block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_muting_rule#conditions AlertMutingRule#conditions}
        '''
        result = self._values.get("conditions")
        assert result is not None, "Required property 'conditions' is missing"
        return typing.cast(typing.List["AlertMutingRuleConditionConditions"], result)

    @builtins.property
    def operator(self) -> builtins.str:
        '''The operator used to combine all the MutingRuleConditions within the group.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_muting_rule#operator AlertMutingRule#operator}
        '''
        result = self._values.get("operator")
        assert result is not None, "Required property 'operator' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AlertMutingRuleCondition(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.AlertMutingRuleConditionConditions",
    jsii_struct_bases=[],
    name_mapping={
        "attribute": "attribute",
        "operator": "operator",
        "values": "values",
    },
)
class AlertMutingRuleConditionConditions:
    def __init__(
        self,
        *,
        attribute: builtins.str,
        operator: builtins.str,
        values: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param attribute: The attribute on a violation. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_muting_rule#attribute AlertMutingRule#attribute}
        :param operator: The operator used to compare the attribute's value with the supplied value(s). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_muting_rule#operator AlertMutingRule#operator}
        :param values: The value(s) to compare against the attribute's value. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_muting_rule#values AlertMutingRule#values}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "attribute": attribute,
            "operator": operator,
            "values": values,
        }

    @builtins.property
    def attribute(self) -> builtins.str:
        '''The attribute on a violation.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_muting_rule#attribute AlertMutingRule#attribute}
        '''
        result = self._values.get("attribute")
        assert result is not None, "Required property 'attribute' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def operator(self) -> builtins.str:
        '''The operator used to compare the attribute's value with the supplied value(s).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_muting_rule#operator AlertMutingRule#operator}
        '''
        result = self._values.get("operator")
        assert result is not None, "Required property 'operator' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def values(self) -> typing.List[builtins.str]:
        '''The value(s) to compare against the attribute's value.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_muting_rule#values AlertMutingRule#values}
        '''
        result = self._values.get("values")
        assert result is not None, "Required property 'values' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AlertMutingRuleConditionConditions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AlertMutingRuleConditionOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-newrelic.AlertMutingRuleConditionOutputReference",
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
    @jsii.member(jsii_name="conditionsInput")
    def conditions_input(
        self,
    ) -> typing.Optional[typing.List[AlertMutingRuleConditionConditions]]:
        return typing.cast(typing.Optional[typing.List[AlertMutingRuleConditionConditions]], jsii.get(self, "conditionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="operatorInput")
    def operator_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "operatorInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="conditions")
    def conditions(self) -> typing.List[AlertMutingRuleConditionConditions]:
        return typing.cast(typing.List[AlertMutingRuleConditionConditions], jsii.get(self, "conditions"))

    @conditions.setter
    def conditions(
        self,
        value: typing.List[AlertMutingRuleConditionConditions],
    ) -> None:
        jsii.set(self, "conditions", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="operator")
    def operator(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "operator"))

    @operator.setter
    def operator(self, value: builtins.str) -> None:
        jsii.set(self, "operator", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[AlertMutingRuleCondition]:
        return typing.cast(typing.Optional[AlertMutingRuleCondition], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[AlertMutingRuleCondition]) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.AlertMutingRuleConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "condition": "condition",
        "enabled": "enabled",
        "name": "name",
        "account_id": "accountId",
        "description": "description",
        "schedule": "schedule",
    },
)
class AlertMutingRuleConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        condition: AlertMutingRuleCondition,
        enabled: typing.Union[builtins.bool, cdktf.IResolvable],
        name: builtins.str,
        account_id: typing.Optional[jsii.Number] = None,
        description: typing.Optional[builtins.str] = None,
        schedule: typing.Optional["AlertMutingRuleSchedule"] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param condition: condition block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_muting_rule#condition AlertMutingRule#condition}
        :param enabled: Whether the MutingRule is enabled. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_muting_rule#enabled AlertMutingRule#enabled}
        :param name: The name of the MutingRule. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_muting_rule#name AlertMutingRule#name}
        :param account_id: The account id of the MutingRule.. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_muting_rule#account_id AlertMutingRule#account_id}
        :param description: The description of the MutingRule. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_muting_rule#description AlertMutingRule#description}
        :param schedule: schedule block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_muting_rule#schedule AlertMutingRule#schedule}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(condition, dict):
            condition = AlertMutingRuleCondition(**condition)
        if isinstance(schedule, dict):
            schedule = AlertMutingRuleSchedule(**schedule)
        self._values: typing.Dict[str, typing.Any] = {
            "condition": condition,
            "enabled": enabled,
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
        if account_id is not None:
            self._values["account_id"] = account_id
        if description is not None:
            self._values["description"] = description
        if schedule is not None:
            self._values["schedule"] = schedule

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
    def condition(self) -> AlertMutingRuleCondition:
        '''condition block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_muting_rule#condition AlertMutingRule#condition}
        '''
        result = self._values.get("condition")
        assert result is not None, "Required property 'condition' is missing"
        return typing.cast(AlertMutingRuleCondition, result)

    @builtins.property
    def enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        '''Whether the MutingRule is enabled.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_muting_rule#enabled AlertMutingRule#enabled}
        '''
        result = self._values.get("enabled")
        assert result is not None, "Required property 'enabled' is missing"
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the MutingRule.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_muting_rule#name AlertMutingRule#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def account_id(self) -> typing.Optional[jsii.Number]:
        '''The account id of the MutingRule..

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_muting_rule#account_id AlertMutingRule#account_id}
        '''
        result = self._values.get("account_id")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''The description of the MutingRule.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_muting_rule#description AlertMutingRule#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def schedule(self) -> typing.Optional["AlertMutingRuleSchedule"]:
        '''schedule block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_muting_rule#schedule AlertMutingRule#schedule}
        '''
        result = self._values.get("schedule")
        return typing.cast(typing.Optional["AlertMutingRuleSchedule"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AlertMutingRuleConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.AlertMutingRuleSchedule",
    jsii_struct_bases=[],
    name_mapping={
        "time_zone": "timeZone",
        "end_repeat": "endRepeat",
        "end_time": "endTime",
        "repeat": "repeat",
        "repeat_count": "repeatCount",
        "start_time": "startTime",
        "weekly_repeat_days": "weeklyRepeatDays",
    },
)
class AlertMutingRuleSchedule:
    def __init__(
        self,
        *,
        time_zone: builtins.str,
        end_repeat: typing.Optional[builtins.str] = None,
        end_time: typing.Optional[builtins.str] = None,
        repeat: typing.Optional[builtins.str] = None,
        repeat_count: typing.Optional[jsii.Number] = None,
        start_time: typing.Optional[builtins.str] = None,
        weekly_repeat_days: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param time_zone: The time zone that applies to the MutingRule schedule. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_muting_rule#time_zone AlertMutingRule#time_zone}
        :param end_repeat: The datetime stamp when the MutingRule schedule should stop repeating. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_muting_rule#end_repeat AlertMutingRule#end_repeat}
        :param end_time: The datetime stamp representing when the MutingRule should end. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_muting_rule#end_time AlertMutingRule#end_time}
        :param repeat: The frequency the MutingRule schedule repeats. One of [DAILY, WEEKLY, MONTHLY]. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_muting_rule#repeat AlertMutingRule#repeat}
        :param repeat_count: The number of times the MutingRule schedule should repeat. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_muting_rule#repeat_count AlertMutingRule#repeat_count}
        :param start_time: The datetime stamp representing when the MutingRule should start. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_muting_rule#start_time AlertMutingRule#start_time}
        :param weekly_repeat_days: The day(s) of the week that a MutingRule should repeat when the repeat field is set to WEEKLY. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_muting_rule#weekly_repeat_days AlertMutingRule#weekly_repeat_days}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "time_zone": time_zone,
        }
        if end_repeat is not None:
            self._values["end_repeat"] = end_repeat
        if end_time is not None:
            self._values["end_time"] = end_time
        if repeat is not None:
            self._values["repeat"] = repeat
        if repeat_count is not None:
            self._values["repeat_count"] = repeat_count
        if start_time is not None:
            self._values["start_time"] = start_time
        if weekly_repeat_days is not None:
            self._values["weekly_repeat_days"] = weekly_repeat_days

    @builtins.property
    def time_zone(self) -> builtins.str:
        '''The time zone that applies to the MutingRule schedule.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_muting_rule#time_zone AlertMutingRule#time_zone}
        '''
        result = self._values.get("time_zone")
        assert result is not None, "Required property 'time_zone' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def end_repeat(self) -> typing.Optional[builtins.str]:
        '''The datetime stamp when the MutingRule schedule should stop repeating.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_muting_rule#end_repeat AlertMutingRule#end_repeat}
        '''
        result = self._values.get("end_repeat")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def end_time(self) -> typing.Optional[builtins.str]:
        '''The datetime stamp representing when the MutingRule should end.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_muting_rule#end_time AlertMutingRule#end_time}
        '''
        result = self._values.get("end_time")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def repeat(self) -> typing.Optional[builtins.str]:
        '''The frequency the MutingRule schedule repeats. One of [DAILY, WEEKLY, MONTHLY].

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_muting_rule#repeat AlertMutingRule#repeat}
        '''
        result = self._values.get("repeat")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def repeat_count(self) -> typing.Optional[jsii.Number]:
        '''The number of times the MutingRule schedule should repeat.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_muting_rule#repeat_count AlertMutingRule#repeat_count}
        '''
        result = self._values.get("repeat_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def start_time(self) -> typing.Optional[builtins.str]:
        '''The datetime stamp representing when the MutingRule should start.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_muting_rule#start_time AlertMutingRule#start_time}
        '''
        result = self._values.get("start_time")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def weekly_repeat_days(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The day(s) of the week that a MutingRule should repeat when the repeat field is set to WEEKLY.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_muting_rule#weekly_repeat_days AlertMutingRule#weekly_repeat_days}
        '''
        result = self._values.get("weekly_repeat_days")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AlertMutingRuleSchedule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AlertMutingRuleScheduleOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-newrelic.AlertMutingRuleScheduleOutputReference",
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

    @jsii.member(jsii_name="resetEndRepeat")
    def reset_end_repeat(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEndRepeat", []))

    @jsii.member(jsii_name="resetEndTime")
    def reset_end_time(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEndTime", []))

    @jsii.member(jsii_name="resetRepeat")
    def reset_repeat(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRepeat", []))

    @jsii.member(jsii_name="resetRepeatCount")
    def reset_repeat_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRepeatCount", []))

    @jsii.member(jsii_name="resetStartTime")
    def reset_start_time(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStartTime", []))

    @jsii.member(jsii_name="resetWeeklyRepeatDays")
    def reset_weekly_repeat_days(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWeeklyRepeatDays", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endRepeatInput")
    def end_repeat_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "endRepeatInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endTimeInput")
    def end_time_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "endTimeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repeatCountInput")
    def repeat_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "repeatCountInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repeatInput")
    def repeat_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "repeatInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="startTimeInput")
    def start_time_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "startTimeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeZoneInput")
    def time_zone_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "timeZoneInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="weeklyRepeatDaysInput")
    def weekly_repeat_days_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "weeklyRepeatDaysInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endRepeat")
    def end_repeat(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endRepeat"))

    @end_repeat.setter
    def end_repeat(self, value: builtins.str) -> None:
        jsii.set(self, "endRepeat", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endTime")
    def end_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endTime"))

    @end_time.setter
    def end_time(self, value: builtins.str) -> None:
        jsii.set(self, "endTime", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repeat")
    def repeat(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repeat"))

    @repeat.setter
    def repeat(self, value: builtins.str) -> None:
        jsii.set(self, "repeat", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repeatCount")
    def repeat_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "repeatCount"))

    @repeat_count.setter
    def repeat_count(self, value: jsii.Number) -> None:
        jsii.set(self, "repeatCount", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="startTime")
    def start_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "startTime"))

    @start_time.setter
    def start_time(self, value: builtins.str) -> None:
        jsii.set(self, "startTime", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeZone")
    def time_zone(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "timeZone"))

    @time_zone.setter
    def time_zone(self, value: builtins.str) -> None:
        jsii.set(self, "timeZone", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="weeklyRepeatDays")
    def weekly_repeat_days(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "weeklyRepeatDays"))

    @weekly_repeat_days.setter
    def weekly_repeat_days(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "weeklyRepeatDays", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[AlertMutingRuleSchedule]:
        return typing.cast(typing.Optional[AlertMutingRuleSchedule], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[AlertMutingRuleSchedule]) -> None:
        jsii.set(self, "internalValue", value)


class AlertPolicy(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-newrelic.AlertPolicy",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/newrelic/r/alert_policy newrelic_alert_policy}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        account_id: typing.Optional[jsii.Number] = None,
        channel_ids: typing.Optional[typing.Sequence[jsii.Number]] = None,
        incident_preference: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/newrelic/r/alert_policy newrelic_alert_policy} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: The name of the policy. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_policy#name AlertPolicy#name}
        :param account_id: The New Relic account ID to operate on. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_policy#account_id AlertPolicy#account_id}
        :param channel_ids: An array of channel IDs (integers) to assign to the policy. Adding or removing channel IDs from this array will result in a new alert policy resource being created and the old one being destroyed. Also note that channel IDs cannot be imported via terraform import. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_policy#channel_ids AlertPolicy#channel_ids}
        :param incident_preference: The rollup strategy for the policy. Options include: PER_POLICY, PER_CONDITION, or PER_CONDITION_AND_TARGET. The default is PER_POLICY. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_policy#incident_preference AlertPolicy#incident_preference}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = AlertPolicyConfig(
            name=name,
            account_id=account_id,
            channel_ids=channel_ids,
            incident_preference=incident_preference,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetAccountId")
    def reset_account_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccountId", []))

    @jsii.member(jsii_name="resetChannelIds")
    def reset_channel_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetChannelIds", []))

    @jsii.member(jsii_name="resetIncidentPreference")
    def reset_incident_preference(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIncidentPreference", []))

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
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "accountIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="channelIdsInput")
    def channel_ids_input(self) -> typing.Optional[typing.List[jsii.Number]]:
        return typing.cast(typing.Optional[typing.List[jsii.Number]], jsii.get(self, "channelIdsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="incidentPreferenceInput")
    def incident_preference_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "incidentPreferenceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: jsii.Number) -> None:
        jsii.set(self, "accountId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="channelIds")
    def channel_ids(self) -> typing.List[jsii.Number]:
        return typing.cast(typing.List[jsii.Number], jsii.get(self, "channelIds"))

    @channel_ids.setter
    def channel_ids(self, value: typing.List[jsii.Number]) -> None:
        jsii.set(self, "channelIds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="incidentPreference")
    def incident_preference(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "incidentPreference"))

    @incident_preference.setter
    def incident_preference(self, value: builtins.str) -> None:
        jsii.set(self, "incidentPreference", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)


class AlertPolicyChannel(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-newrelic.AlertPolicyChannel",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/newrelic/r/alert_policy_channel newrelic_alert_policy_channel}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        channel_ids: typing.Sequence[jsii.Number],
        policy_id: jsii.Number,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/newrelic/r/alert_policy_channel newrelic_alert_policy_channel} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param channel_ids: Array of channel IDs to apply to the specified policy. We recommended sorting channel IDs in ascending order to avoid drift your Terraform state. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_policy_channel#channel_ids AlertPolicyChannel#channel_ids}
        :param policy_id: The ID of the policy. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_policy_channel#policy_id AlertPolicyChannel#policy_id}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = AlertPolicyChannelConfig(
            channel_ids=channel_ids,
            policy_id=policy_id,
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
    @jsii.member(jsii_name="channelIdsInput")
    def channel_ids_input(self) -> typing.Optional[typing.List[jsii.Number]]:
        return typing.cast(typing.Optional[typing.List[jsii.Number]], jsii.get(self, "channelIdsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyIdInput")
    def policy_id_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "policyIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="channelIds")
    def channel_ids(self) -> typing.List[jsii.Number]:
        return typing.cast(typing.List[jsii.Number], jsii.get(self, "channelIds"))

    @channel_ids.setter
    def channel_ids(self, value: typing.List[jsii.Number]) -> None:
        jsii.set(self, "channelIds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyId")
    def policy_id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "policyId"))

    @policy_id.setter
    def policy_id(self, value: jsii.Number) -> None:
        jsii.set(self, "policyId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.AlertPolicyChannelConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "channel_ids": "channelIds",
        "policy_id": "policyId",
    },
)
class AlertPolicyChannelConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        channel_ids: typing.Sequence[jsii.Number],
        policy_id: jsii.Number,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param channel_ids: Array of channel IDs to apply to the specified policy. We recommended sorting channel IDs in ascending order to avoid drift your Terraform state. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_policy_channel#channel_ids AlertPolicyChannel#channel_ids}
        :param policy_id: The ID of the policy. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_policy_channel#policy_id AlertPolicyChannel#policy_id}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "channel_ids": channel_ids,
            "policy_id": policy_id,
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
    def channel_ids(self) -> typing.List[jsii.Number]:
        '''Array of channel IDs to apply to the specified policy.

        We recommended sorting channel IDs in ascending order to avoid drift your Terraform state.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_policy_channel#channel_ids AlertPolicyChannel#channel_ids}
        '''
        result = self._values.get("channel_ids")
        assert result is not None, "Required property 'channel_ids' is missing"
        return typing.cast(typing.List[jsii.Number], result)

    @builtins.property
    def policy_id(self) -> jsii.Number:
        '''The ID of the policy.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_policy_channel#policy_id AlertPolicyChannel#policy_id}
        '''
        result = self._values.get("policy_id")
        assert result is not None, "Required property 'policy_id' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AlertPolicyChannelConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.AlertPolicyConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "account_id": "accountId",
        "channel_ids": "channelIds",
        "incident_preference": "incidentPreference",
    },
)
class AlertPolicyConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        account_id: typing.Optional[jsii.Number] = None,
        channel_ids: typing.Optional[typing.Sequence[jsii.Number]] = None,
        incident_preference: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: The name of the policy. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_policy#name AlertPolicy#name}
        :param account_id: The New Relic account ID to operate on. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_policy#account_id AlertPolicy#account_id}
        :param channel_ids: An array of channel IDs (integers) to assign to the policy. Adding or removing channel IDs from this array will result in a new alert policy resource being created and the old one being destroyed. Also note that channel IDs cannot be imported via terraform import. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_policy#channel_ids AlertPolicy#channel_ids}
        :param incident_preference: The rollup strategy for the policy. Options include: PER_POLICY, PER_CONDITION, or PER_CONDITION_AND_TARGET. The default is PER_POLICY. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_policy#incident_preference AlertPolicy#incident_preference}
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
        if account_id is not None:
            self._values["account_id"] = account_id
        if channel_ids is not None:
            self._values["channel_ids"] = channel_ids
        if incident_preference is not None:
            self._values["incident_preference"] = incident_preference

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
        '''The name of the policy.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_policy#name AlertPolicy#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def account_id(self) -> typing.Optional[jsii.Number]:
        '''The New Relic account ID to operate on.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_policy#account_id AlertPolicy#account_id}
        '''
        result = self._values.get("account_id")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def channel_ids(self) -> typing.Optional[typing.List[jsii.Number]]:
        '''An array of channel IDs (integers) to assign to the policy.

        Adding or removing channel IDs from this array will result in a new alert policy resource being created and the old one being destroyed. Also note that channel IDs cannot be imported via terraform import.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_policy#channel_ids AlertPolicy#channel_ids}
        '''
        result = self._values.get("channel_ids")
        return typing.cast(typing.Optional[typing.List[jsii.Number]], result)

    @builtins.property
    def incident_preference(self) -> typing.Optional[builtins.str]:
        '''The rollup strategy for the policy. Options include: PER_POLICY, PER_CONDITION, or PER_CONDITION_AND_TARGET. The default is PER_POLICY.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/alert_policy#incident_preference AlertPolicy#incident_preference}
        '''
        result = self._values.get("incident_preference")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AlertPolicyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ApiAccessKey(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-newrelic.ApiAccessKey",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/newrelic/r/api_access_key newrelic_api_access_key}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        account_id: jsii.Number,
        key_type: builtins.str,
        ingest_type: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        notes: typing.Optional[builtins.str] = None,
        user_id: typing.Optional[jsii.Number] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/newrelic/r/api_access_key newrelic_api_access_key} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param account_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/api_access_key#account_id ApiAccessKey#account_id}.
        :param key_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/api_access_key#key_type ApiAccessKey#key_type}.
        :param ingest_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/api_access_key#ingest_type ApiAccessKey#ingest_type}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/api_access_key#name ApiAccessKey#name}.
        :param notes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/api_access_key#notes ApiAccessKey#notes}.
        :param user_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/api_access_key#user_id ApiAccessKey#user_id}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ApiAccessKeyConfig(
            account_id=account_id,
            key_type=key_type,
            ingest_type=ingest_type,
            name=name,
            notes=notes,
            user_id=user_id,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetIngestType")
    def reset_ingest_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIngestType", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetNotes")
    def reset_notes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNotes", []))

    @jsii.member(jsii_name="resetUserId")
    def reset_user_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserId", []))

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
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "accountIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ingestTypeInput")
    def ingest_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ingestTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyTypeInput")
    def key_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="notesInput")
    def notes_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "notesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userIdInput")
    def user_id_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "userIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: jsii.Number) -> None:
        jsii.set(self, "accountId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ingestType")
    def ingest_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ingestType"))

    @ingest_type.setter
    def ingest_type(self, value: builtins.str) -> None:
        jsii.set(self, "ingestType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyType")
    def key_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keyType"))

    @key_type.setter
    def key_type(self, value: builtins.str) -> None:
        jsii.set(self, "keyType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="notes")
    def notes(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "notes"))

    @notes.setter
    def notes(self, value: builtins.str) -> None:
        jsii.set(self, "notes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userId")
    def user_id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "userId"))

    @user_id.setter
    def user_id(self, value: jsii.Number) -> None:
        jsii.set(self, "userId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.ApiAccessKeyConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "account_id": "accountId",
        "key_type": "keyType",
        "ingest_type": "ingestType",
        "name": "name",
        "notes": "notes",
        "user_id": "userId",
    },
)
class ApiAccessKeyConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        account_id: jsii.Number,
        key_type: builtins.str,
        ingest_type: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        notes: typing.Optional[builtins.str] = None,
        user_id: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param account_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/api_access_key#account_id ApiAccessKey#account_id}.
        :param key_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/api_access_key#key_type ApiAccessKey#key_type}.
        :param ingest_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/api_access_key#ingest_type ApiAccessKey#ingest_type}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/api_access_key#name ApiAccessKey#name}.
        :param notes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/api_access_key#notes ApiAccessKey#notes}.
        :param user_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/api_access_key#user_id ApiAccessKey#user_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "account_id": account_id,
            "key_type": key_type,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if ingest_type is not None:
            self._values["ingest_type"] = ingest_type
        if name is not None:
            self._values["name"] = name
        if notes is not None:
            self._values["notes"] = notes
        if user_id is not None:
            self._values["user_id"] = user_id

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
    def account_id(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/api_access_key#account_id ApiAccessKey#account_id}.'''
        result = self._values.get("account_id")
        assert result is not None, "Required property 'account_id' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def key_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/api_access_key#key_type ApiAccessKey#key_type}.'''
        result = self._values.get("key_type")
        assert result is not None, "Required property 'key_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ingest_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/api_access_key#ingest_type ApiAccessKey#ingest_type}.'''
        result = self._values.get("ingest_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/api_access_key#name ApiAccessKey#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def notes(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/api_access_key#notes ApiAccessKey#notes}.'''
        result = self._values.get("notes")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def user_id(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/api_access_key#user_id ApiAccessKey#user_id}.'''
        result = self._values.get("user_id")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApiAccessKeyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ApplicationSettings(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-newrelic.ApplicationSettings",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/newrelic/r/application_settings newrelic_application_settings}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        app_apdex_threshold: jsii.Number,
        enable_real_user_monitoring: typing.Union[builtins.bool, cdktf.IResolvable],
        end_user_apdex_threshold: jsii.Number,
        name: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/newrelic/r/application_settings newrelic_application_settings} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param app_apdex_threshold: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/application_settings#app_apdex_threshold ApplicationSettings#app_apdex_threshold}.
        :param enable_real_user_monitoring: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/application_settings#enable_real_user_monitoring ApplicationSettings#enable_real_user_monitoring}.
        :param end_user_apdex_threshold: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/application_settings#end_user_apdex_threshold ApplicationSettings#end_user_apdex_threshold}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/application_settings#name ApplicationSettings#name}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ApplicationSettingsConfig(
            app_apdex_threshold=app_apdex_threshold,
            enable_real_user_monitoring=enable_real_user_monitoring,
            end_user_apdex_threshold=end_user_apdex_threshold,
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
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="appApdexThresholdInput")
    def app_apdex_threshold_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "appApdexThresholdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableRealUserMonitoringInput")
    def enable_real_user_monitoring_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enableRealUserMonitoringInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endUserApdexThresholdInput")
    def end_user_apdex_threshold_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "endUserApdexThresholdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="appApdexThreshold")
    def app_apdex_threshold(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "appApdexThreshold"))

    @app_apdex_threshold.setter
    def app_apdex_threshold(self, value: jsii.Number) -> None:
        jsii.set(self, "appApdexThreshold", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableRealUserMonitoring")
    def enable_real_user_monitoring(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enableRealUserMonitoring"))

    @enable_real_user_monitoring.setter
    def enable_real_user_monitoring(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "enableRealUserMonitoring", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endUserApdexThreshold")
    def end_user_apdex_threshold(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "endUserApdexThreshold"))

    @end_user_apdex_threshold.setter
    def end_user_apdex_threshold(self, value: jsii.Number) -> None:
        jsii.set(self, "endUserApdexThreshold", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.ApplicationSettingsConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "app_apdex_threshold": "appApdexThreshold",
        "enable_real_user_monitoring": "enableRealUserMonitoring",
        "end_user_apdex_threshold": "endUserApdexThreshold",
        "name": "name",
    },
)
class ApplicationSettingsConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        app_apdex_threshold: jsii.Number,
        enable_real_user_monitoring: typing.Union[builtins.bool, cdktf.IResolvable],
        end_user_apdex_threshold: jsii.Number,
        name: builtins.str,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param app_apdex_threshold: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/application_settings#app_apdex_threshold ApplicationSettings#app_apdex_threshold}.
        :param enable_real_user_monitoring: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/application_settings#enable_real_user_monitoring ApplicationSettings#enable_real_user_monitoring}.
        :param end_user_apdex_threshold: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/application_settings#end_user_apdex_threshold ApplicationSettings#end_user_apdex_threshold}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/application_settings#name ApplicationSettings#name}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "app_apdex_threshold": app_apdex_threshold,
            "enable_real_user_monitoring": enable_real_user_monitoring,
            "end_user_apdex_threshold": end_user_apdex_threshold,
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
    def app_apdex_threshold(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/application_settings#app_apdex_threshold ApplicationSettings#app_apdex_threshold}.'''
        result = self._values.get("app_apdex_threshold")
        assert result is not None, "Required property 'app_apdex_threshold' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def enable_real_user_monitoring(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/application_settings#enable_real_user_monitoring ApplicationSettings#enable_real_user_monitoring}.'''
        result = self._values.get("enable_real_user_monitoring")
        assert result is not None, "Required property 'enable_real_user_monitoring' is missing"
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], result)

    @builtins.property
    def end_user_apdex_threshold(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/application_settings#end_user_apdex_threshold ApplicationSettings#end_user_apdex_threshold}.'''
        result = self._values.get("end_user_apdex_threshold")
        assert result is not None, "Required property 'end_user_apdex_threshold' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/application_settings#name ApplicationSettings#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApplicationSettingsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Dashboard(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-newrelic.Dashboard",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard newrelic_dashboard}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        title: builtins.str,
        editable: typing.Optional[builtins.str] = None,
        filter: typing.Optional["DashboardFilter"] = None,
        grid_column_count: typing.Optional[jsii.Number] = None,
        icon: typing.Optional[builtins.str] = None,
        visibility: typing.Optional[builtins.str] = None,
        widget: typing.Optional[typing.Sequence["DashboardWidget"]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard newrelic_dashboard} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param title: The title of the dashboard. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#title Dashboard#title}
        :param editable: Determines who can edit the dashboard in an account. Valid values are all, editable_by_all, editable_by_owner, or read_only. Defaults to editable_by_all. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#editable Dashboard#editable}
        :param filter: filter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#filter Dashboard#filter}
        :param grid_column_count: New Relic One supports a 3 column grid or a 12 column grid. New Relic Insights supports a 3 column grid. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#grid_column_count Dashboard#grid_column_count}
        :param icon: The icon for the dashboard. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#icon Dashboard#icon}
        :param visibility: Determines who can see the dashboard in an account. Valid values are all or owner. Defaults to all. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#visibility Dashboard#visibility}
        :param widget: widget block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#widget Dashboard#widget}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DashboardConfig(
            title=title,
            editable=editable,
            filter=filter,
            grid_column_count=grid_column_count,
            icon=icon,
            visibility=visibility,
            widget=widget,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putFilter")
    def put_filter(
        self,
        *,
        event_types: typing.Sequence[builtins.str],
        attributes: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param event_types: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#event_types Dashboard#event_types}.
        :param attributes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#attributes Dashboard#attributes}.
        '''
        value = DashboardFilter(event_types=event_types, attributes=attributes)

        return typing.cast(None, jsii.invoke(self, "putFilter", [value]))

    @jsii.member(jsii_name="resetEditable")
    def reset_editable(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEditable", []))

    @jsii.member(jsii_name="resetFilter")
    def reset_filter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFilter", []))

    @jsii.member(jsii_name="resetGridColumnCount")
    def reset_grid_column_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGridColumnCount", []))

    @jsii.member(jsii_name="resetIcon")
    def reset_icon(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIcon", []))

    @jsii.member(jsii_name="resetVisibility")
    def reset_visibility(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVisibility", []))

    @jsii.member(jsii_name="resetWidget")
    def reset_widget(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWidget", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dashboardUrl")
    def dashboard_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dashboardUrl"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="filter")
    def filter(self) -> "DashboardFilterOutputReference":
        return typing.cast("DashboardFilterOutputReference", jsii.get(self, "filter"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="editableInput")
    def editable_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "editableInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="filterInput")
    def filter_input(self) -> typing.Optional["DashboardFilter"]:
        return typing.cast(typing.Optional["DashboardFilter"], jsii.get(self, "filterInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="gridColumnCountInput")
    def grid_column_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "gridColumnCountInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="iconInput")
    def icon_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "iconInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="titleInput")
    def title_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "titleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="visibilityInput")
    def visibility_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "visibilityInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="widgetInput")
    def widget_input(self) -> typing.Optional[typing.List["DashboardWidget"]]:
        return typing.cast(typing.Optional[typing.List["DashboardWidget"]], jsii.get(self, "widgetInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="editable")
    def editable(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "editable"))

    @editable.setter
    def editable(self, value: builtins.str) -> None:
        jsii.set(self, "editable", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="gridColumnCount")
    def grid_column_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "gridColumnCount"))

    @grid_column_count.setter
    def grid_column_count(self, value: jsii.Number) -> None:
        jsii.set(self, "gridColumnCount", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="icon")
    def icon(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "icon"))

    @icon.setter
    def icon(self, value: builtins.str) -> None:
        jsii.set(self, "icon", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="title")
    def title(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "title"))

    @title.setter
    def title(self, value: builtins.str) -> None:
        jsii.set(self, "title", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="visibility")
    def visibility(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "visibility"))

    @visibility.setter
    def visibility(self, value: builtins.str) -> None:
        jsii.set(self, "visibility", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="widget")
    def widget(self) -> typing.List["DashboardWidget"]:
        return typing.cast(typing.List["DashboardWidget"], jsii.get(self, "widget"))

    @widget.setter
    def widget(self, value: typing.List["DashboardWidget"]) -> None:
        jsii.set(self, "widget", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.DashboardConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "title": "title",
        "editable": "editable",
        "filter": "filter",
        "grid_column_count": "gridColumnCount",
        "icon": "icon",
        "visibility": "visibility",
        "widget": "widget",
    },
)
class DashboardConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        title: builtins.str,
        editable: typing.Optional[builtins.str] = None,
        filter: typing.Optional["DashboardFilter"] = None,
        grid_column_count: typing.Optional[jsii.Number] = None,
        icon: typing.Optional[builtins.str] = None,
        visibility: typing.Optional[builtins.str] = None,
        widget: typing.Optional[typing.Sequence["DashboardWidget"]] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param title: The title of the dashboard. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#title Dashboard#title}
        :param editable: Determines who can edit the dashboard in an account. Valid values are all, editable_by_all, editable_by_owner, or read_only. Defaults to editable_by_all. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#editable Dashboard#editable}
        :param filter: filter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#filter Dashboard#filter}
        :param grid_column_count: New Relic One supports a 3 column grid or a 12 column grid. New Relic Insights supports a 3 column grid. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#grid_column_count Dashboard#grid_column_count}
        :param icon: The icon for the dashboard. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#icon Dashboard#icon}
        :param visibility: Determines who can see the dashboard in an account. Valid values are all or owner. Defaults to all. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#visibility Dashboard#visibility}
        :param widget: widget block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#widget Dashboard#widget}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(filter, dict):
            filter = DashboardFilter(**filter)
        self._values: typing.Dict[str, typing.Any] = {
            "title": title,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if editable is not None:
            self._values["editable"] = editable
        if filter is not None:
            self._values["filter"] = filter
        if grid_column_count is not None:
            self._values["grid_column_count"] = grid_column_count
        if icon is not None:
            self._values["icon"] = icon
        if visibility is not None:
            self._values["visibility"] = visibility
        if widget is not None:
            self._values["widget"] = widget

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
    def title(self) -> builtins.str:
        '''The title of the dashboard.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#title Dashboard#title}
        '''
        result = self._values.get("title")
        assert result is not None, "Required property 'title' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def editable(self) -> typing.Optional[builtins.str]:
        '''Determines who can edit the dashboard in an account.

        Valid values are all, editable_by_all, editable_by_owner, or read_only. Defaults to editable_by_all.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#editable Dashboard#editable}
        '''
        result = self._values.get("editable")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def filter(self) -> typing.Optional["DashboardFilter"]:
        '''filter block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#filter Dashboard#filter}
        '''
        result = self._values.get("filter")
        return typing.cast(typing.Optional["DashboardFilter"], result)

    @builtins.property
    def grid_column_count(self) -> typing.Optional[jsii.Number]:
        '''New Relic One supports a 3 column grid or a 12 column grid.

        New Relic Insights supports a 3 column grid.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#grid_column_count Dashboard#grid_column_count}
        '''
        result = self._values.get("grid_column_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def icon(self) -> typing.Optional[builtins.str]:
        '''The icon for the dashboard.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#icon Dashboard#icon}
        '''
        result = self._values.get("icon")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def visibility(self) -> typing.Optional[builtins.str]:
        '''Determines who can see the dashboard in an account. Valid values are all or owner. Defaults to all.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#visibility Dashboard#visibility}
        '''
        result = self._values.get("visibility")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def widget(self) -> typing.Optional[typing.List["DashboardWidget"]]:
        '''widget block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#widget Dashboard#widget}
        '''
        result = self._values.get("widget")
        return typing.cast(typing.Optional[typing.List["DashboardWidget"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DashboardConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.DashboardFilter",
    jsii_struct_bases=[],
    name_mapping={"event_types": "eventTypes", "attributes": "attributes"},
)
class DashboardFilter:
    def __init__(
        self,
        *,
        event_types: typing.Sequence[builtins.str],
        attributes: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param event_types: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#event_types Dashboard#event_types}.
        :param attributes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#attributes Dashboard#attributes}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "event_types": event_types,
        }
        if attributes is not None:
            self._values["attributes"] = attributes

    @builtins.property
    def event_types(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#event_types Dashboard#event_types}.'''
        result = self._values.get("event_types")
        assert result is not None, "Required property 'event_types' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def attributes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#attributes Dashboard#attributes}.'''
        result = self._values.get("attributes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DashboardFilter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DashboardFilterOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-newrelic.DashboardFilterOutputReference",
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

    @jsii.member(jsii_name="resetAttributes")
    def reset_attributes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attributesInput")
    def attributes_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "attributesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="eventTypesInput")
    def event_types_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "eventTypesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attributes")
    def attributes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "attributes"))

    @attributes.setter
    def attributes(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "attributes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="eventTypes")
    def event_types(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "eventTypes"))

    @event_types.setter
    def event_types(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "eventTypes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DashboardFilter]:
        return typing.cast(typing.Optional[DashboardFilter], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[DashboardFilter]) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.DashboardWidget",
    jsii_struct_bases=[],
    name_mapping={
        "column": "column",
        "row": "row",
        "title": "title",
        "visualization": "visualization",
        "account_id": "accountId",
        "compare_with": "compareWith",
        "drilldown_dashboard_id": "drilldownDashboardId",
        "duration": "duration",
        "end_time": "endTime",
        "entity_ids": "entityIds",
        "facet": "facet",
        "height": "height",
        "limit": "limit",
        "metric": "metric",
        "notes": "notes",
        "nrql": "nrql",
        "order_by": "orderBy",
        "source": "source",
        "threshold_red": "thresholdRed",
        "threshold_yellow": "thresholdYellow",
        "width": "width",
    },
)
class DashboardWidget:
    def __init__(
        self,
        *,
        column: jsii.Number,
        row: jsii.Number,
        title: builtins.str,
        visualization: builtins.str,
        account_id: typing.Optional[jsii.Number] = None,
        compare_with: typing.Optional[typing.Sequence["DashboardWidgetCompareWith"]] = None,
        drilldown_dashboard_id: typing.Optional[jsii.Number] = None,
        duration: typing.Optional[jsii.Number] = None,
        end_time: typing.Optional[jsii.Number] = None,
        entity_ids: typing.Optional[typing.Sequence[jsii.Number]] = None,
        facet: typing.Optional[builtins.str] = None,
        height: typing.Optional[jsii.Number] = None,
        limit: typing.Optional[jsii.Number] = None,
        metric: typing.Optional[typing.Sequence["DashboardWidgetMetric"]] = None,
        notes: typing.Optional[builtins.str] = None,
        nrql: typing.Optional[builtins.str] = None,
        order_by: typing.Optional[builtins.str] = None,
        source: typing.Optional[builtins.str] = None,
        threshold_red: typing.Optional[jsii.Number] = None,
        threshold_yellow: typing.Optional[jsii.Number] = None,
        width: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param column: Column position of widget from top left, starting at 1. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#column Dashboard#column}
        :param row: Row position of widget from top left, starting at 1. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#row Dashboard#row}
        :param title: A title for the widget. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#title Dashboard#title}
        :param visualization: How the widget visualizes data. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#visualization Dashboard#visualization}
        :param account_id: The target account ID to fetch data from, if not the current account. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#account_id Dashboard#account_id}
        :param compare_with: compare_with block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#compare_with Dashboard#compare_with}
        :param drilldown_dashboard_id: The ID of a dashboard to link to from the widget's facets. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#drilldown_dashboard_id Dashboard#drilldown_dashboard_id}
        :param duration: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#duration Dashboard#duration}.
        :param end_time: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#end_time Dashboard#end_time}.
        :param entity_ids: A collection of entity ids to display data for. These are typically application IDs. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#entity_ids Dashboard#entity_ids}
        :param facet: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#facet Dashboard#facet}.
        :param height: Height of the widget. Valid values are 1 to 3 inclusive. Defaults to 1. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#height Dashboard#height}
        :param limit: The limit of distinct data series to display. Requires ``order_by`` to be set. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#limit Dashboard#limit}
        :param metric: metric block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#metric Dashboard#metric}
        :param notes: Description of the widget. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#notes Dashboard#notes}
        :param nrql: Valid NRQL query string. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#nrql Dashboard#nrql}
        :param order_by: Set the order of result series. Required when using ``limit``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#order_by Dashboard#order_by}
        :param source: The markdown source to be rendered in the widget. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#source Dashboard#source}
        :param threshold_red: Threshold above which the displayed value will be styled with a red color. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#threshold_red Dashboard#threshold_red}
        :param threshold_yellow: Threshold above which the displayed value will be styled with a yellow color. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#threshold_yellow Dashboard#threshold_yellow}
        :param width: Width of the widget. Valid values are 1 to 3 inclusive. Defaults to 1. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#width Dashboard#width}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "column": column,
            "row": row,
            "title": title,
            "visualization": visualization,
        }
        if account_id is not None:
            self._values["account_id"] = account_id
        if compare_with is not None:
            self._values["compare_with"] = compare_with
        if drilldown_dashboard_id is not None:
            self._values["drilldown_dashboard_id"] = drilldown_dashboard_id
        if duration is not None:
            self._values["duration"] = duration
        if end_time is not None:
            self._values["end_time"] = end_time
        if entity_ids is not None:
            self._values["entity_ids"] = entity_ids
        if facet is not None:
            self._values["facet"] = facet
        if height is not None:
            self._values["height"] = height
        if limit is not None:
            self._values["limit"] = limit
        if metric is not None:
            self._values["metric"] = metric
        if notes is not None:
            self._values["notes"] = notes
        if nrql is not None:
            self._values["nrql"] = nrql
        if order_by is not None:
            self._values["order_by"] = order_by
        if source is not None:
            self._values["source"] = source
        if threshold_red is not None:
            self._values["threshold_red"] = threshold_red
        if threshold_yellow is not None:
            self._values["threshold_yellow"] = threshold_yellow
        if width is not None:
            self._values["width"] = width

    @builtins.property
    def column(self) -> jsii.Number:
        '''Column position of widget from top left, starting at 1.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#column Dashboard#column}
        '''
        result = self._values.get("column")
        assert result is not None, "Required property 'column' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def row(self) -> jsii.Number:
        '''Row position of widget from top left, starting at 1.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#row Dashboard#row}
        '''
        result = self._values.get("row")
        assert result is not None, "Required property 'row' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def title(self) -> builtins.str:
        '''A title for the widget.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#title Dashboard#title}
        '''
        result = self._values.get("title")
        assert result is not None, "Required property 'title' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def visualization(self) -> builtins.str:
        '''How the widget visualizes data.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#visualization Dashboard#visualization}
        '''
        result = self._values.get("visualization")
        assert result is not None, "Required property 'visualization' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def account_id(self) -> typing.Optional[jsii.Number]:
        '''The target account ID to fetch data from, if not the current account.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#account_id Dashboard#account_id}
        '''
        result = self._values.get("account_id")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def compare_with(
        self,
    ) -> typing.Optional[typing.List["DashboardWidgetCompareWith"]]:
        '''compare_with block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#compare_with Dashboard#compare_with}
        '''
        result = self._values.get("compare_with")
        return typing.cast(typing.Optional[typing.List["DashboardWidgetCompareWith"]], result)

    @builtins.property
    def drilldown_dashboard_id(self) -> typing.Optional[jsii.Number]:
        '''The ID of a dashboard to link to from the widget's facets.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#drilldown_dashboard_id Dashboard#drilldown_dashboard_id}
        '''
        result = self._values.get("drilldown_dashboard_id")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def duration(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#duration Dashboard#duration}.'''
        result = self._values.get("duration")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def end_time(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#end_time Dashboard#end_time}.'''
        result = self._values.get("end_time")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def entity_ids(self) -> typing.Optional[typing.List[jsii.Number]]:
        '''A collection of entity ids to display data for. These are typically application IDs.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#entity_ids Dashboard#entity_ids}
        '''
        result = self._values.get("entity_ids")
        return typing.cast(typing.Optional[typing.List[jsii.Number]], result)

    @builtins.property
    def facet(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#facet Dashboard#facet}.'''
        result = self._values.get("facet")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def height(self) -> typing.Optional[jsii.Number]:
        '''Height of the widget. Valid values are 1 to 3 inclusive. Defaults to 1.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#height Dashboard#height}
        '''
        result = self._values.get("height")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def limit(self) -> typing.Optional[jsii.Number]:
        '''The limit of distinct data series to display.  Requires ``order_by`` to be set.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#limit Dashboard#limit}
        '''
        result = self._values.get("limit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def metric(self) -> typing.Optional[typing.List["DashboardWidgetMetric"]]:
        '''metric block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#metric Dashboard#metric}
        '''
        result = self._values.get("metric")
        return typing.cast(typing.Optional[typing.List["DashboardWidgetMetric"]], result)

    @builtins.property
    def notes(self) -> typing.Optional[builtins.str]:
        '''Description of the widget.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#notes Dashboard#notes}
        '''
        result = self._values.get("notes")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def nrql(self) -> typing.Optional[builtins.str]:
        '''Valid NRQL query string.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#nrql Dashboard#nrql}
        '''
        result = self._values.get("nrql")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def order_by(self) -> typing.Optional[builtins.str]:
        '''Set the order of result series.  Required when using ``limit``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#order_by Dashboard#order_by}
        '''
        result = self._values.get("order_by")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source(self) -> typing.Optional[builtins.str]:
        '''The markdown source to be rendered in the widget.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#source Dashboard#source}
        '''
        result = self._values.get("source")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def threshold_red(self) -> typing.Optional[jsii.Number]:
        '''Threshold above which the displayed value will be styled with a red color.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#threshold_red Dashboard#threshold_red}
        '''
        result = self._values.get("threshold_red")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def threshold_yellow(self) -> typing.Optional[jsii.Number]:
        '''Threshold above which the displayed value will be styled with a yellow color.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#threshold_yellow Dashboard#threshold_yellow}
        '''
        result = self._values.get("threshold_yellow")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def width(self) -> typing.Optional[jsii.Number]:
        '''Width of the widget. Valid values are 1 to 3 inclusive. Defaults to 1.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#width Dashboard#width}
        '''
        result = self._values.get("width")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DashboardWidget(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.DashboardWidgetCompareWith",
    jsii_struct_bases=[],
    name_mapping={"offset_duration": "offsetDuration", "presentation": "presentation"},
)
class DashboardWidgetCompareWith:
    def __init__(
        self,
        *,
        offset_duration: builtins.str,
        presentation: "DashboardWidgetCompareWithPresentation",
    ) -> None:
        '''
        :param offset_duration: The offset duration for the COMPARE WITH clause. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#offset_duration Dashboard#offset_duration}
        :param presentation: presentation block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#presentation Dashboard#presentation}
        '''
        if isinstance(presentation, dict):
            presentation = DashboardWidgetCompareWithPresentation(**presentation)
        self._values: typing.Dict[str, typing.Any] = {
            "offset_duration": offset_duration,
            "presentation": presentation,
        }

    @builtins.property
    def offset_duration(self) -> builtins.str:
        '''The offset duration for the COMPARE WITH clause.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#offset_duration Dashboard#offset_duration}
        '''
        result = self._values.get("offset_duration")
        assert result is not None, "Required property 'offset_duration' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def presentation(self) -> "DashboardWidgetCompareWithPresentation":
        '''presentation block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#presentation Dashboard#presentation}
        '''
        result = self._values.get("presentation")
        assert result is not None, "Required property 'presentation' is missing"
        return typing.cast("DashboardWidgetCompareWithPresentation", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DashboardWidgetCompareWith(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.DashboardWidgetCompareWithPresentation",
    jsii_struct_bases=[],
    name_mapping={"color": "color", "name": "name"},
)
class DashboardWidgetCompareWithPresentation:
    def __init__(self, *, color: builtins.str, name: builtins.str) -> None:
        '''
        :param color: The color for the rendered data. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#color Dashboard#color}
        :param name: The name for the rendered data. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#name Dashboard#name}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "color": color,
            "name": name,
        }

    @builtins.property
    def color(self) -> builtins.str:
        '''The color for the rendered data.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#color Dashboard#color}
        '''
        result = self._values.get("color")
        assert result is not None, "Required property 'color' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name for the rendered data.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#name Dashboard#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DashboardWidgetCompareWithPresentation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DashboardWidgetCompareWithPresentationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-newrelic.DashboardWidgetCompareWithPresentationOutputReference",
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
    @jsii.member(jsii_name="colorInput")
    def color_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "colorInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="color")
    def color(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "color"))

    @color.setter
    def color(self, value: builtins.str) -> None:
        jsii.set(self, "color", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DashboardWidgetCompareWithPresentation]:
        return typing.cast(typing.Optional[DashboardWidgetCompareWithPresentation], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DashboardWidgetCompareWithPresentation],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.DashboardWidgetMetric",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "scope": "scope",
        "units": "units",
        "values": "values",
    },
)
class DashboardWidgetMetric:
    def __init__(
        self,
        *,
        name: builtins.str,
        scope: typing.Optional[builtins.str] = None,
        units: typing.Optional[builtins.str] = None,
        values: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param name: The metric name to display. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#name Dashboard#name}
        :param scope: The metric scope. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#scope Dashboard#scope}
        :param units: The metric units. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#units Dashboard#units}
        :param values: The metric values to display. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#values Dashboard#values}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if scope is not None:
            self._values["scope"] = scope
        if units is not None:
            self._values["units"] = units
        if values is not None:
            self._values["values"] = values

    @builtins.property
    def name(self) -> builtins.str:
        '''The metric name to display.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#name Dashboard#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def scope(self) -> typing.Optional[builtins.str]:
        '''The metric scope.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#scope Dashboard#scope}
        '''
        result = self._values.get("scope")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def units(self) -> typing.Optional[builtins.str]:
        '''The metric units.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#units Dashboard#units}
        '''
        result = self._values.get("units")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def values(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The metric values to display.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/dashboard#values Dashboard#values}
        '''
        result = self._values.get("values")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DashboardWidgetMetric(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataNewrelicAccount(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-newrelic.DataNewrelicAccount",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/newrelic/d/account newrelic_account}.'''

    def __init__(
        self,
        scope_: constructs.Construct,
        id: builtins.str,
        *,
        account_id: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        scope: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/newrelic/d/account newrelic_account} Data Source.

        :param scope_: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param account_id: The ID of the account in New Relic. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/d/account#account_id DataNewrelicAccount#account_id}
        :param name: The name of the account in New Relic. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/d/account#name DataNewrelicAccount#name}
        :param scope: The scope of the account in New Relic. Valid values are "global" and "in_region". Defaults to "in_region". Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/d/account#scope DataNewrelicAccount#scope}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataNewrelicAccountConfig(
            account_id=account_id,
            name=name,
            scope=scope,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope_, id, config])

    @jsii.member(jsii_name="resetAccountId")
    def reset_account_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccountId", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetScope")
    def reset_scope(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetScope", []))

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
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "accountIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="scopeInput")
    def scope_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "scopeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: jsii.Number) -> None:
        jsii.set(self, "accountId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="scope")
    def scope(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "scope"))

    @scope.setter
    def scope(self, value: builtins.str) -> None:
        jsii.set(self, "scope", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.DataNewrelicAccountConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "account_id": "accountId",
        "name": "name",
        "scope": "scope",
    },
)
class DataNewrelicAccountConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        account_id: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        scope: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param account_id: The ID of the account in New Relic. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/d/account#account_id DataNewrelicAccount#account_id}
        :param name: The name of the account in New Relic. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/d/account#name DataNewrelicAccount#name}
        :param scope: The scope of the account in New Relic. Valid values are "global" and "in_region". Defaults to "in_region". Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/d/account#scope DataNewrelicAccount#scope}
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
        if account_id is not None:
            self._values["account_id"] = account_id
        if name is not None:
            self._values["name"] = name
        if scope is not None:
            self._values["scope"] = scope

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
    def account_id(self) -> typing.Optional[jsii.Number]:
        '''The ID of the account in New Relic.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/d/account#account_id DataNewrelicAccount#account_id}
        '''
        result = self._values.get("account_id")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''The name of the account in New Relic.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/d/account#name DataNewrelicAccount#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def scope(self) -> typing.Optional[builtins.str]:
        '''The scope of the account in New Relic.  Valid values are "global" and "in_region".  Defaults to "in_region".

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/d/account#scope DataNewrelicAccount#scope}
        '''
        result = self._values.get("scope")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataNewrelicAccountConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataNewrelicAlertChannel(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-newrelic.DataNewrelicAlertChannel",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/newrelic/d/alert_channel newrelic_alert_channel}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/newrelic/d/alert_channel newrelic_alert_channel} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: The name of the alert channel in New Relic. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/d/alert_channel#name DataNewrelicAlertChannel#name}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataNewrelicAlertChannelConfig(
            name=name,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="config")
    def config(self, index: builtins.str) -> "DataNewrelicAlertChannelConfigA":
        '''
        :param index: -
        '''
        return typing.cast("DataNewrelicAlertChannelConfigA", jsii.invoke(self, "config", [index]))

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
    @jsii.member(jsii_name="policyIds")
    def policy_ids(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "policyIds"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

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
    jsii_type="@cdktf/provider-newrelic.DataNewrelicAlertChannelConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
    },
)
class DataNewrelicAlertChannelConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: The name of the alert channel in New Relic. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/d/alert_channel#name DataNewrelicAlertChannel#name}
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
        '''The name of the alert channel in New Relic.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/d/alert_channel#name DataNewrelicAlertChannel#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataNewrelicAlertChannelConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataNewrelicAlertChannelConfigA(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-newrelic.DataNewrelicAlertChannelConfigA",
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
    @jsii.member(jsii_name="apiKey")
    def api_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "apiKey"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authPassword")
    def auth_password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authPassword"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authType")
    def auth_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authUsername")
    def auth_username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authUsername"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="baseUrl")
    def base_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "baseUrl"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="channel")
    def channel(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "channel"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="headers")
    def headers(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "headers"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="includeJsonAttachment")
    def include_json_attachment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "includeJsonAttachment"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="payload")
    def payload(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "payload"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="payloadType")
    def payload_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "payloadType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="recipients")
    def recipients(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "recipients"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="routeKey")
    def route_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "routeKey"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceKey")
    def service_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceKey"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="teams")
    def teams(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "teams"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userId")
    def user_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userId"))


class DataNewrelicAlertPolicy(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-newrelic.DataNewrelicAlertPolicy",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/newrelic/d/alert_policy newrelic_alert_policy}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        account_id: typing.Optional[jsii.Number] = None,
        incident_preference: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/newrelic/d/alert_policy newrelic_alert_policy} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: The name of the alert policy in New Relic. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/d/alert_policy#name DataNewrelicAlertPolicy#name}
        :param account_id: The New Relic account ID to operate on. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/d/alert_policy#account_id DataNewrelicAlertPolicy#account_id}
        :param incident_preference: The rollup strategy for the policy. Options include: ``PER_POLICY``, ``PER_CONDITION``, or ``PER_CONDITION_AND_TARGET``. The default is ``PER_POLICY``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/d/alert_policy#incident_preference DataNewrelicAlertPolicy#incident_preference}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataNewrelicAlertPolicyConfig(
            name=name,
            account_id=account_id,
            incident_preference=incident_preference,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetAccountId")
    def reset_account_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccountId", []))

    @jsii.member(jsii_name="resetIncidentPreference")
    def reset_incident_preference(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIncidentPreference", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdAt"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="updatedAt")
    def updated_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updatedAt"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "accountIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="incidentPreferenceInput")
    def incident_preference_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "incidentPreferenceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: jsii.Number) -> None:
        jsii.set(self, "accountId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="incidentPreference")
    def incident_preference(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "incidentPreference"))

    @incident_preference.setter
    def incident_preference(self, value: builtins.str) -> None:
        jsii.set(self, "incidentPreference", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.DataNewrelicAlertPolicyConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "account_id": "accountId",
        "incident_preference": "incidentPreference",
    },
)
class DataNewrelicAlertPolicyConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        account_id: typing.Optional[jsii.Number] = None,
        incident_preference: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: The name of the alert policy in New Relic. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/d/alert_policy#name DataNewrelicAlertPolicy#name}
        :param account_id: The New Relic account ID to operate on. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/d/alert_policy#account_id DataNewrelicAlertPolicy#account_id}
        :param incident_preference: The rollup strategy for the policy. Options include: ``PER_POLICY``, ``PER_CONDITION``, or ``PER_CONDITION_AND_TARGET``. The default is ``PER_POLICY``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/d/alert_policy#incident_preference DataNewrelicAlertPolicy#incident_preference}
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
        if account_id is not None:
            self._values["account_id"] = account_id
        if incident_preference is not None:
            self._values["incident_preference"] = incident_preference

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
        '''The name of the alert policy in New Relic.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/d/alert_policy#name DataNewrelicAlertPolicy#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def account_id(self) -> typing.Optional[jsii.Number]:
        '''The New Relic account ID to operate on.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/d/alert_policy#account_id DataNewrelicAlertPolicy#account_id}
        '''
        result = self._values.get("account_id")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def incident_preference(self) -> typing.Optional[builtins.str]:
        '''The rollup strategy for the policy. Options include: ``PER_POLICY``, ``PER_CONDITION``, or ``PER_CONDITION_AND_TARGET``. The default is ``PER_POLICY``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/d/alert_policy#incident_preference DataNewrelicAlertPolicy#incident_preference}
        '''
        result = self._values.get("incident_preference")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataNewrelicAlertPolicyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataNewrelicApplication(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-newrelic.DataNewrelicApplication",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/newrelic/d/application newrelic_application}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/newrelic/d/application newrelic_application} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: The name of the application in New Relic. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/d/application#name DataNewrelicApplication#name}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataNewrelicApplicationConfig(
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
    @jsii.member(jsii_name="hostIds")
    def host_ids(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "hostIds"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceIds")
    def instance_ids(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "instanceIds"))

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
    jsii_type="@cdktf/provider-newrelic.DataNewrelicApplicationConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
    },
)
class DataNewrelicApplicationConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: The name of the application in New Relic. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/d/application#name DataNewrelicApplication#name}
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
        '''The name of the application in New Relic.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/d/application#name DataNewrelicApplication#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataNewrelicApplicationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataNewrelicEntity(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-newrelic.DataNewrelicEntity",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/newrelic/d/entity newrelic_entity}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        domain: typing.Optional[builtins.str] = None,
        ignore_case: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        tag: typing.Optional["DataNewrelicEntityTag"] = None,
        type: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/newrelic/d/entity newrelic_entity} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: The name of the entity in New Relic One. The first entity matching this name for the given search parameters will be returned. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/d/entity#name DataNewrelicEntity#name}
        :param domain: The entity's domain. Valid values are APM, BROWSER, INFRA, MOBILE, SYNTH, and VIZ. If not specified, all domains are searched. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/d/entity#domain DataNewrelicEntity#domain}
        :param ignore_case: Ignore case when searching the entity name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/d/entity#ignore_case DataNewrelicEntity#ignore_case}
        :param tag: tag block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/d/entity#tag DataNewrelicEntity#tag}
        :param type: The entity's type. Valid values are APPLICATION, DASHBOARD, HOST, MONITOR, and WORKLOAD. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/d/entity#type DataNewrelicEntity#type}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataNewrelicEntityConfig(
            name=name,
            domain=domain,
            ignore_case=ignore_case,
            tag=tag,
            type=type,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putTag")
    def put_tag(self, *, key: builtins.str, value: builtins.str) -> None:
        '''
        :param key: The tag key. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/d/entity#key DataNewrelicEntity#key}
        :param value: The tag value. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/d/entity#value DataNewrelicEntity#value}
        '''
        value_ = DataNewrelicEntityTag(key=key, value=value)

        return typing.cast(None, jsii.invoke(self, "putTag", [value_]))

    @jsii.member(jsii_name="resetDomain")
    def reset_domain(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDomain", []))

    @jsii.member(jsii_name="resetIgnoreCase")
    def reset_ignore_case(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIgnoreCase", []))

    @jsii.member(jsii_name="resetTag")
    def reset_tag(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTag", []))

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
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "accountId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="applicationId")
    def application_id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "applicationId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="guid")
    def guid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "guid"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="servingApmApplicationId")
    def serving_apm_application_id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "servingApmApplicationId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tag")
    def tag(self) -> "DataNewrelicEntityTagOutputReference":
        return typing.cast("DataNewrelicEntityTagOutputReference", jsii.get(self, "tag"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainInput")
    def domain_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "domainInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ignoreCaseInput")
    def ignore_case_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "ignoreCaseInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagInput")
    def tag_input(self) -> typing.Optional["DataNewrelicEntityTag"]:
        return typing.cast(typing.Optional["DataNewrelicEntityTag"], jsii.get(self, "tagInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domain")
    def domain(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "domain"))

    @domain.setter
    def domain(self, value: builtins.str) -> None:
        jsii.set(self, "domain", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ignoreCase")
    def ignore_case(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "ignoreCase"))

    @ignore_case.setter
    def ignore_case(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "ignoreCase", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        jsii.set(self, "type", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.DataNewrelicEntityConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "domain": "domain",
        "ignore_case": "ignoreCase",
        "tag": "tag",
        "type": "type",
    },
)
class DataNewrelicEntityConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        domain: typing.Optional[builtins.str] = None,
        ignore_case: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        tag: typing.Optional["DataNewrelicEntityTag"] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: The name of the entity in New Relic One. The first entity matching this name for the given search parameters will be returned. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/d/entity#name DataNewrelicEntity#name}
        :param domain: The entity's domain. Valid values are APM, BROWSER, INFRA, MOBILE, SYNTH, and VIZ. If not specified, all domains are searched. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/d/entity#domain DataNewrelicEntity#domain}
        :param ignore_case: Ignore case when searching the entity name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/d/entity#ignore_case DataNewrelicEntity#ignore_case}
        :param tag: tag block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/d/entity#tag DataNewrelicEntity#tag}
        :param type: The entity's type. Valid values are APPLICATION, DASHBOARD, HOST, MONITOR, and WORKLOAD. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/d/entity#type DataNewrelicEntity#type}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(tag, dict):
            tag = DataNewrelicEntityTag(**tag)
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
        if domain is not None:
            self._values["domain"] = domain
        if ignore_case is not None:
            self._values["ignore_case"] = ignore_case
        if tag is not None:
            self._values["tag"] = tag
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
        '''The name of the entity in New Relic One.

        The first entity matching this name for the given search parameters will be returned.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/d/entity#name DataNewrelicEntity#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def domain(self) -> typing.Optional[builtins.str]:
        '''The entity's domain.

        Valid values are APM, BROWSER, INFRA, MOBILE, SYNTH, and VIZ. If not specified, all domains are searched.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/d/entity#domain DataNewrelicEntity#domain}
        '''
        result = self._values.get("domain")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ignore_case(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Ignore case when searching the entity name.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/d/entity#ignore_case DataNewrelicEntity#ignore_case}
        '''
        result = self._values.get("ignore_case")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def tag(self) -> typing.Optional["DataNewrelicEntityTag"]:
        '''tag block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/d/entity#tag DataNewrelicEntity#tag}
        '''
        result = self._values.get("tag")
        return typing.cast(typing.Optional["DataNewrelicEntityTag"], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''The entity's type. Valid values are APPLICATION, DASHBOARD, HOST, MONITOR, and WORKLOAD.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/d/entity#type DataNewrelicEntity#type}
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataNewrelicEntityConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.DataNewrelicEntityTag",
    jsii_struct_bases=[],
    name_mapping={"key": "key", "value": "value"},
)
class DataNewrelicEntityTag:
    def __init__(self, *, key: builtins.str, value: builtins.str) -> None:
        '''
        :param key: The tag key. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/d/entity#key DataNewrelicEntity#key}
        :param value: The tag value. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/d/entity#value DataNewrelicEntity#value}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "key": key,
            "value": value,
        }

    @builtins.property
    def key(self) -> builtins.str:
        '''The tag key.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/d/entity#key DataNewrelicEntity#key}
        '''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''The tag value.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/d/entity#value DataNewrelicEntity#value}
        '''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataNewrelicEntityTag(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataNewrelicEntityTagOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-newrelic.DataNewrelicEntityTagOutputReference",
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
    @jsii.member(jsii_name="keyInput")
    def key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "valueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        jsii.set(self, "key", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        jsii.set(self, "value", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DataNewrelicEntityTag]:
        return typing.cast(typing.Optional[DataNewrelicEntityTag], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[DataNewrelicEntityTag]) -> None:
        jsii.set(self, "internalValue", value)


class DataNewrelicKeyTransaction(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-newrelic.DataNewrelicKeyTransaction",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/newrelic/d/key_transaction newrelic_key_transaction}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/newrelic/d/key_transaction newrelic_key_transaction} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: The name of the key transaction in New Relic. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/d/key_transaction#name DataNewrelicKeyTransaction#name}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataNewrelicKeyTransactionConfig(
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
    jsii_type="@cdktf/provider-newrelic.DataNewrelicKeyTransactionConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
    },
)
class DataNewrelicKeyTransactionConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: The name of the key transaction in New Relic. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/d/key_transaction#name DataNewrelicKeyTransaction#name}
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
        '''The name of the key transaction in New Relic.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/d/key_transaction#name DataNewrelicKeyTransaction#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataNewrelicKeyTransactionConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataNewrelicPlugin(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-newrelic.DataNewrelicPlugin",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/newrelic/d/plugin newrelic_plugin}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        guid: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/newrelic/d/plugin newrelic_plugin} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param guid: The GUID of the plugin in New Relic. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/d/plugin#guid DataNewrelicPlugin#guid}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataNewrelicPluginConfig(
            guid=guid,
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
    @jsii.member(jsii_name="guidInput")
    def guid_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "guidInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="guid")
    def guid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "guid"))

    @guid.setter
    def guid(self, value: builtins.str) -> None:
        jsii.set(self, "guid", value)


class DataNewrelicPluginComponent(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-newrelic.DataNewrelicPluginComponent",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/newrelic/d/plugin_component newrelic_plugin_component}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        plugin_id: jsii.Number,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/newrelic/d/plugin_component newrelic_plugin_component} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: The name of the plugin component. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/d/plugin_component#name DataNewrelicPluginComponent#name}
        :param plugin_id: The ID of the plugin instance this component belongs to. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/d/plugin_component#plugin_id DataNewrelicPluginComponent#plugin_id}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataNewrelicPluginComponentConfig(
            name=name,
            plugin_id=plugin_id,
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
    @jsii.member(jsii_name="healthStatus")
    def health_status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "healthStatus"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pluginIdInput")
    def plugin_id_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "pluginIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pluginId")
    def plugin_id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "pluginId"))

    @plugin_id.setter
    def plugin_id(self, value: jsii.Number) -> None:
        jsii.set(self, "pluginId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.DataNewrelicPluginComponentConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "plugin_id": "pluginId",
    },
)
class DataNewrelicPluginComponentConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        plugin_id: jsii.Number,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: The name of the plugin component. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/d/plugin_component#name DataNewrelicPluginComponent#name}
        :param plugin_id: The ID of the plugin instance this component belongs to. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/d/plugin_component#plugin_id DataNewrelicPluginComponent#plugin_id}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "plugin_id": plugin_id,
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
        '''The name of the plugin component.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/d/plugin_component#name DataNewrelicPluginComponent#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def plugin_id(self) -> jsii.Number:
        '''The ID of the plugin instance this component belongs to.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/d/plugin_component#plugin_id DataNewrelicPluginComponent#plugin_id}
        '''
        result = self._values.get("plugin_id")
        assert result is not None, "Required property 'plugin_id' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataNewrelicPluginComponentConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.DataNewrelicPluginConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "guid": "guid",
    },
)
class DataNewrelicPluginConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        guid: builtins.str,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param guid: The GUID of the plugin in New Relic. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/d/plugin#guid DataNewrelicPlugin#guid}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "guid": guid,
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
    def guid(self) -> builtins.str:
        '''The GUID of the plugin in New Relic.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/d/plugin#guid DataNewrelicPlugin#guid}
        '''
        result = self._values.get("guid")
        assert result is not None, "Required property 'guid' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataNewrelicPluginConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataNewrelicSyntheticsMonitor(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-newrelic.DataNewrelicSyntheticsMonitor",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/newrelic/d/synthetics_monitor newrelic_synthetics_monitor}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/newrelic/d/synthetics_monitor newrelic_synthetics_monitor} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: The name of the synthetics monitor in New Relic. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/d/synthetics_monitor#name DataNewrelicSyntheticsMonitor#name}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataNewrelicSyntheticsMonitorConfig(
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
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="monitorId")
    def monitor_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "monitorId"))

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
    jsii_type="@cdktf/provider-newrelic.DataNewrelicSyntheticsMonitorConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
    },
)
class DataNewrelicSyntheticsMonitorConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: The name of the synthetics monitor in New Relic. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/d/synthetics_monitor#name DataNewrelicSyntheticsMonitor#name}
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
        '''The name of the synthetics monitor in New Relic.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/d/synthetics_monitor#name DataNewrelicSyntheticsMonitor#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataNewrelicSyntheticsMonitorConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataNewrelicSyntheticsMonitorLocation(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-newrelic.DataNewrelicSyntheticsMonitorLocation",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/newrelic/d/synthetics_monitor_location newrelic_synthetics_monitor_location}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        label: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/newrelic/d/synthetics_monitor_location newrelic_synthetics_monitor_location} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param label: The label of the Synthetics monitor location. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/d/synthetics_monitor_location#label DataNewrelicSyntheticsMonitorLocation#label}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataNewrelicSyntheticsMonitorLocationConfig(
            label=label,
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
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="highSecurityMode")
    def high_security_mode(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "highSecurityMode"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="private")
    def private(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "private"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="labelInput")
    def label_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "labelInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="label")
    def label(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "label"))

    @label.setter
    def label(self, value: builtins.str) -> None:
        jsii.set(self, "label", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.DataNewrelicSyntheticsMonitorLocationConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "label": "label",
    },
)
class DataNewrelicSyntheticsMonitorLocationConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        label: builtins.str,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param label: The label of the Synthetics monitor location. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/d/synthetics_monitor_location#label DataNewrelicSyntheticsMonitorLocation#label}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "label": label,
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
    def label(self) -> builtins.str:
        '''The label of the Synthetics monitor location.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/d/synthetics_monitor_location#label DataNewrelicSyntheticsMonitorLocation#label}
        '''
        result = self._values.get("label")
        assert result is not None, "Required property 'label' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataNewrelicSyntheticsMonitorLocationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataNewrelicSyntheticsSecureCredential(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-newrelic.DataNewrelicSyntheticsSecureCredential",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/newrelic/d/synthetics_secure_credential newrelic_synthetics_secure_credential}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        key: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/newrelic/d/synthetics_secure_credential newrelic_synthetics_secure_credential} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param key: The secure credential's key name. Regardless of the case used in the configuration, the provider will provide an upcased key to the underlying API. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/d/synthetics_secure_credential#key DataNewrelicSyntheticsSecureCredential#key}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataNewrelicSyntheticsSecureCredentialConfig(
            key=key,
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
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdAt"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lastUpdated")
    def last_updated(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lastUpdated"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyInput")
    def key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        jsii.set(self, "key", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.DataNewrelicSyntheticsSecureCredentialConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "key": "key",
    },
)
class DataNewrelicSyntheticsSecureCredentialConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        key: builtins.str,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param key: The secure credential's key name. Regardless of the case used in the configuration, the provider will provide an upcased key to the underlying API. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/d/synthetics_secure_credential#key DataNewrelicSyntheticsSecureCredential#key}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "key": key,
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
    def key(self) -> builtins.str:
        '''The secure credential's key name.

        Regardless of the case used in the configuration, the provider will provide an upcased key to the underlying API.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/d/synthetics_secure_credential#key DataNewrelicSyntheticsSecureCredential#key}
        '''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataNewrelicSyntheticsSecureCredentialConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class EntityTags(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-newrelic.EntityTags",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/newrelic/r/entity_tags newrelic_entity_tags}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        guid: builtins.str,
        tag: typing.Sequence["EntityTagsTag"],
        timeouts: typing.Optional["EntityTagsTimeouts"] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/newrelic/r/entity_tags newrelic_entity_tags} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param guid: The guid of the entity to tag. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/entity_tags#guid EntityTags#guid}
        :param tag: tag block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/entity_tags#tag EntityTags#tag}
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/entity_tags#timeouts EntityTags#timeouts}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = EntityTagsConfig(
            guid=guid,
            tag=tag,
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
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/entity_tags#create EntityTags#create}.
        '''
        value = EntityTagsTimeouts(create=create)

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
    def timeouts(self) -> "EntityTagsTimeoutsOutputReference":
        return typing.cast("EntityTagsTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="guidInput")
    def guid_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "guidInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagInput")
    def tag_input(self) -> typing.Optional[typing.List["EntityTagsTag"]]:
        return typing.cast(typing.Optional[typing.List["EntityTagsTag"]], jsii.get(self, "tagInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(self) -> typing.Optional["EntityTagsTimeouts"]:
        return typing.cast(typing.Optional["EntityTagsTimeouts"], jsii.get(self, "timeoutsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="guid")
    def guid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "guid"))

    @guid.setter
    def guid(self, value: builtins.str) -> None:
        jsii.set(self, "guid", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tag")
    def tag(self) -> typing.List["EntityTagsTag"]:
        return typing.cast(typing.List["EntityTagsTag"], jsii.get(self, "tag"))

    @tag.setter
    def tag(self, value: typing.List["EntityTagsTag"]) -> None:
        jsii.set(self, "tag", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.EntityTagsConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "guid": "guid",
        "tag": "tag",
        "timeouts": "timeouts",
    },
)
class EntityTagsConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        guid: builtins.str,
        tag: typing.Sequence["EntityTagsTag"],
        timeouts: typing.Optional["EntityTagsTimeouts"] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param guid: The guid of the entity to tag. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/entity_tags#guid EntityTags#guid}
        :param tag: tag block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/entity_tags#tag EntityTags#tag}
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/entity_tags#timeouts EntityTags#timeouts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(timeouts, dict):
            timeouts = EntityTagsTimeouts(**timeouts)
        self._values: typing.Dict[str, typing.Any] = {
            "guid": guid,
            "tag": tag,
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
    def guid(self) -> builtins.str:
        '''The guid of the entity to tag.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/entity_tags#guid EntityTags#guid}
        '''
        result = self._values.get("guid")
        assert result is not None, "Required property 'guid' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def tag(self) -> typing.List["EntityTagsTag"]:
        '''tag block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/entity_tags#tag EntityTags#tag}
        '''
        result = self._values.get("tag")
        assert result is not None, "Required property 'tag' is missing"
        return typing.cast(typing.List["EntityTagsTag"], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["EntityTagsTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/entity_tags#timeouts EntityTags#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["EntityTagsTimeouts"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EntityTagsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.EntityTagsTag",
    jsii_struct_bases=[],
    name_mapping={"key": "key", "values": "values"},
)
class EntityTagsTag:
    def __init__(
        self,
        *,
        key: builtins.str,
        values: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param key: The tag key. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/entity_tags#key EntityTags#key}
        :param values: The tag values. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/entity_tags#values EntityTags#values}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "key": key,
            "values": values,
        }

    @builtins.property
    def key(self) -> builtins.str:
        '''The tag key.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/entity_tags#key EntityTags#key}
        '''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def values(self) -> typing.List[builtins.str]:
        '''The tag values.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/entity_tags#values EntityTags#values}
        '''
        result = self._values.get("values")
        assert result is not None, "Required property 'values' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EntityTagsTag(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.EntityTagsTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create"},
)
class EntityTagsTimeouts:
    def __init__(self, *, create: typing.Optional[builtins.str] = None) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/entity_tags#create EntityTags#create}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if create is not None:
            self._values["create"] = create

    @builtins.property
    def create(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/entity_tags#create EntityTags#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EntityTagsTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class EntityTagsTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-newrelic.EntityTagsTimeoutsOutputReference",
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
    def internal_value(self) -> typing.Optional[EntityTagsTimeouts]:
        return typing.cast(typing.Optional[EntityTagsTimeouts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[EntityTagsTimeouts]) -> None:
        jsii.set(self, "internalValue", value)


class EventsToMetricsRule(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-newrelic.EventsToMetricsRule",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/newrelic/r/events_to_metrics_rule newrelic_events_to_metrics_rule}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        nrql: builtins.str,
        account_id: typing.Optional[jsii.Number] = None,
        description: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/newrelic/r/events_to_metrics_rule newrelic_events_to_metrics_rule} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: The name of the rule. This must be unique within an account. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/events_to_metrics_rule#name EventsToMetricsRule#name}
        :param nrql: Explains how to create metrics from events. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/events_to_metrics_rule#nrql EventsToMetricsRule#nrql}
        :param account_id: Account with the event and where the metrics will be put. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/events_to_metrics_rule#account_id EventsToMetricsRule#account_id}
        :param description: Provides additional information about the rule. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/events_to_metrics_rule#description EventsToMetricsRule#description}
        :param enabled: True means this rule is enabled. False means the rule is currently not creating metrics. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/events_to_metrics_rule#enabled EventsToMetricsRule#enabled}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = EventsToMetricsRuleConfig(
            name=name,
            nrql=nrql,
            account_id=account_id,
            description=description,
            enabled=enabled,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetAccountId")
    def reset_account_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccountId", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

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
    @jsii.member(jsii_name="ruleId")
    def rule_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ruleId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "accountIdInput"))

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
    @jsii.member(jsii_name="nrqlInput")
    def nrql_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nrqlInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: jsii.Number) -> None:
        jsii.set(self, "accountId", value)

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
    @jsii.member(jsii_name="nrql")
    def nrql(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nrql"))

    @nrql.setter
    def nrql(self, value: builtins.str) -> None:
        jsii.set(self, "nrql", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.EventsToMetricsRuleConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "nrql": "nrql",
        "account_id": "accountId",
        "description": "description",
        "enabled": "enabled",
    },
)
class EventsToMetricsRuleConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        nrql: builtins.str,
        account_id: typing.Optional[jsii.Number] = None,
        description: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: The name of the rule. This must be unique within an account. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/events_to_metrics_rule#name EventsToMetricsRule#name}
        :param nrql: Explains how to create metrics from events. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/events_to_metrics_rule#nrql EventsToMetricsRule#nrql}
        :param account_id: Account with the event and where the metrics will be put. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/events_to_metrics_rule#account_id EventsToMetricsRule#account_id}
        :param description: Provides additional information about the rule. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/events_to_metrics_rule#description EventsToMetricsRule#description}
        :param enabled: True means this rule is enabled. False means the rule is currently not creating metrics. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/events_to_metrics_rule#enabled EventsToMetricsRule#enabled}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "nrql": nrql,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if account_id is not None:
            self._values["account_id"] = account_id
        if description is not None:
            self._values["description"] = description
        if enabled is not None:
            self._values["enabled"] = enabled

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
        '''The name of the rule. This must be unique within an account.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/events_to_metrics_rule#name EventsToMetricsRule#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def nrql(self) -> builtins.str:
        '''Explains how to create metrics from events.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/events_to_metrics_rule#nrql EventsToMetricsRule#nrql}
        '''
        result = self._values.get("nrql")
        assert result is not None, "Required property 'nrql' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def account_id(self) -> typing.Optional[jsii.Number]:
        '''Account with the event and where the metrics will be put.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/events_to_metrics_rule#account_id EventsToMetricsRule#account_id}
        '''
        result = self._values.get("account_id")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Provides additional information about the rule.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/events_to_metrics_rule#description EventsToMetricsRule#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''True means this rule is enabled. False means the rule is currently not creating metrics.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/events_to_metrics_rule#enabled EventsToMetricsRule#enabled}
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EventsToMetricsRuleConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class InfraAlertCondition(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-newrelic.InfraAlertCondition",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/newrelic/r/infra_alert_condition newrelic_infra_alert_condition}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        policy_id: jsii.Number,
        type: builtins.str,
        comparison: typing.Optional[builtins.str] = None,
        critical: typing.Optional["InfraAlertConditionCritical"] = None,
        description: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        event: typing.Optional[builtins.str] = None,
        integration_provider: typing.Optional[builtins.str] = None,
        process_where: typing.Optional[builtins.str] = None,
        runbook_url: typing.Optional[builtins.str] = None,
        select: typing.Optional[builtins.str] = None,
        violation_close_timer: typing.Optional[jsii.Number] = None,
        warning: typing.Optional["InfraAlertConditionWarning"] = None,
        where: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/newrelic/r/infra_alert_condition newrelic_infra_alert_condition} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: The Infrastructure alert condition's name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/infra_alert_condition#name InfraAlertCondition#name}
        :param policy_id: The ID of the alert policy where this condition should be used. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/infra_alert_condition#policy_id InfraAlertCondition#policy_id}
        :param type: The type of Infrastructure alert condition. Valid values are infra_process_running, infra_metric, and infra_host_not_reporting. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/infra_alert_condition#type InfraAlertCondition#type}
        :param comparison: The operator used to evaluate the threshold value. Valid values are above, below, and equal. Supported by the infra_metric and infra_process_running condition types. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/infra_alert_condition#comparison InfraAlertCondition#comparison}
        :param critical: critical block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/infra_alert_condition#critical InfraAlertCondition#critical}
        :param description: The description of the Infrastructure alert condition. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/infra_alert_condition#description InfraAlertCondition#description}
        :param enabled: Whether the condition is turned on or off. Valid values are true and false. Defaults to true. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/infra_alert_condition#enabled InfraAlertCondition#enabled}
        :param event: The metric event; for example, SystemSample or StorageSample. Supported by the infra_metric condition type. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/infra_alert_condition#event InfraAlertCondition#event}
        :param integration_provider: For alerts on integrations, use this instead of event. Supported by the infra_metric condition type. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/infra_alert_condition#integration_provider InfraAlertCondition#integration_provider}
        :param process_where: Any filters applied to processes; for example: commandName = 'java'. Supported by the infra_process_running condition type. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/infra_alert_condition#process_where InfraAlertCondition#process_where}
        :param runbook_url: Runbook URL to display in notifications. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/infra_alert_condition#runbook_url InfraAlertCondition#runbook_url}
        :param select: The attribute name to identify the metric being targeted; for example, cpuPercent, diskFreePercent, or memoryResidentSizeBytes. The underlying API will automatically populate this value for Infrastructure integrations (for example diskFreePercent), so make sure to explicitly include this value to avoid diff issues. Supported by the infra_metric condition type. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/infra_alert_condition#select InfraAlertCondition#select}
        :param violation_close_timer: Determines how much time, in hours, will pass before a violation is automatically closed. Valid values are 1, 2, 4, 8, 12, 24, 48, or 72 Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/infra_alert_condition#violation_close_timer InfraAlertCondition#violation_close_timer}
        :param warning: warning block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/infra_alert_condition#warning InfraAlertCondition#warning}
        :param where: If applicable, this identifies any Infrastructure host filters used; for example: hostname LIKE '%cassandra%'. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/infra_alert_condition#where InfraAlertCondition#where}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = InfraAlertConditionConfig(
            name=name,
            policy_id=policy_id,
            type=type,
            comparison=comparison,
            critical=critical,
            description=description,
            enabled=enabled,
            event=event,
            integration_provider=integration_provider,
            process_where=process_where,
            runbook_url=runbook_url,
            select=select,
            violation_close_timer=violation_close_timer,
            warning=warning,
            where=where,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putCritical")
    def put_critical(
        self,
        *,
        duration: jsii.Number,
        time_function: typing.Optional[builtins.str] = None,
        value: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param duration: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/infra_alert_condition#duration InfraAlertCondition#duration}.
        :param time_function: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/infra_alert_condition#time_function InfraAlertCondition#time_function}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/infra_alert_condition#value InfraAlertCondition#value}.
        '''
        value_ = InfraAlertConditionCritical(
            duration=duration, time_function=time_function, value=value
        )

        return typing.cast(None, jsii.invoke(self, "putCritical", [value_]))

    @jsii.member(jsii_name="putWarning")
    def put_warning(
        self,
        *,
        duration: jsii.Number,
        time_function: typing.Optional[builtins.str] = None,
        value: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param duration: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/infra_alert_condition#duration InfraAlertCondition#duration}.
        :param time_function: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/infra_alert_condition#time_function InfraAlertCondition#time_function}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/infra_alert_condition#value InfraAlertCondition#value}.
        '''
        value_ = InfraAlertConditionWarning(
            duration=duration, time_function=time_function, value=value
        )

        return typing.cast(None, jsii.invoke(self, "putWarning", [value_]))

    @jsii.member(jsii_name="resetComparison")
    def reset_comparison(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetComparison", []))

    @jsii.member(jsii_name="resetCritical")
    def reset_critical(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCritical", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="resetEvent")
    def reset_event(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEvent", []))

    @jsii.member(jsii_name="resetIntegrationProvider")
    def reset_integration_provider(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIntegrationProvider", []))

    @jsii.member(jsii_name="resetProcessWhere")
    def reset_process_where(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProcessWhere", []))

    @jsii.member(jsii_name="resetRunbookUrl")
    def reset_runbook_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRunbookUrl", []))

    @jsii.member(jsii_name="resetSelect")
    def reset_select(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSelect", []))

    @jsii.member(jsii_name="resetViolationCloseTimer")
    def reset_violation_close_timer(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetViolationCloseTimer", []))

    @jsii.member(jsii_name="resetWarning")
    def reset_warning(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWarning", []))

    @jsii.member(jsii_name="resetWhere")
    def reset_where(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWhere", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "createdAt"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="critical")
    def critical(self) -> "InfraAlertConditionCriticalOutputReference":
        return typing.cast("InfraAlertConditionCriticalOutputReference", jsii.get(self, "critical"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="updatedAt")
    def updated_at(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "updatedAt"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="warning")
    def warning(self) -> "InfraAlertConditionWarningOutputReference":
        return typing.cast("InfraAlertConditionWarningOutputReference", jsii.get(self, "warning"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="comparisonInput")
    def comparison_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "comparisonInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="criticalInput")
    def critical_input(self) -> typing.Optional["InfraAlertConditionCritical"]:
        return typing.cast(typing.Optional["InfraAlertConditionCritical"], jsii.get(self, "criticalInput"))

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
    @jsii.member(jsii_name="eventInput")
    def event_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "eventInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="integrationProviderInput")
    def integration_provider_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "integrationProviderInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyIdInput")
    def policy_id_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "policyIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="processWhereInput")
    def process_where_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "processWhereInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="runbookUrlInput")
    def runbook_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "runbookUrlInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="selectInput")
    def select_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "selectInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="violationCloseTimerInput")
    def violation_close_timer_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "violationCloseTimerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="warningInput")
    def warning_input(self) -> typing.Optional["InfraAlertConditionWarning"]:
        return typing.cast(typing.Optional["InfraAlertConditionWarning"], jsii.get(self, "warningInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="whereInput")
    def where_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "whereInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="comparison")
    def comparison(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "comparison"))

    @comparison.setter
    def comparison(self, value: builtins.str) -> None:
        jsii.set(self, "comparison", value)

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
    @jsii.member(jsii_name="event")
    def event(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "event"))

    @event.setter
    def event(self, value: builtins.str) -> None:
        jsii.set(self, "event", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="integrationProvider")
    def integration_provider(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "integrationProvider"))

    @integration_provider.setter
    def integration_provider(self, value: builtins.str) -> None:
        jsii.set(self, "integrationProvider", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyId")
    def policy_id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "policyId"))

    @policy_id.setter
    def policy_id(self, value: jsii.Number) -> None:
        jsii.set(self, "policyId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="processWhere")
    def process_where(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "processWhere"))

    @process_where.setter
    def process_where(self, value: builtins.str) -> None:
        jsii.set(self, "processWhere", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="runbookUrl")
    def runbook_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "runbookUrl"))

    @runbook_url.setter
    def runbook_url(self, value: builtins.str) -> None:
        jsii.set(self, "runbookUrl", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="select")
    def select(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "select"))

    @select.setter
    def select(self, value: builtins.str) -> None:
        jsii.set(self, "select", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        jsii.set(self, "type", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="violationCloseTimer")
    def violation_close_timer(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "violationCloseTimer"))

    @violation_close_timer.setter
    def violation_close_timer(self, value: jsii.Number) -> None:
        jsii.set(self, "violationCloseTimer", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="where")
    def where(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "where"))

    @where.setter
    def where(self, value: builtins.str) -> None:
        jsii.set(self, "where", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.InfraAlertConditionConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "policy_id": "policyId",
        "type": "type",
        "comparison": "comparison",
        "critical": "critical",
        "description": "description",
        "enabled": "enabled",
        "event": "event",
        "integration_provider": "integrationProvider",
        "process_where": "processWhere",
        "runbook_url": "runbookUrl",
        "select": "select",
        "violation_close_timer": "violationCloseTimer",
        "warning": "warning",
        "where": "where",
    },
)
class InfraAlertConditionConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        policy_id: jsii.Number,
        type: builtins.str,
        comparison: typing.Optional[builtins.str] = None,
        critical: typing.Optional["InfraAlertConditionCritical"] = None,
        description: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        event: typing.Optional[builtins.str] = None,
        integration_provider: typing.Optional[builtins.str] = None,
        process_where: typing.Optional[builtins.str] = None,
        runbook_url: typing.Optional[builtins.str] = None,
        select: typing.Optional[builtins.str] = None,
        violation_close_timer: typing.Optional[jsii.Number] = None,
        warning: typing.Optional["InfraAlertConditionWarning"] = None,
        where: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: The Infrastructure alert condition's name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/infra_alert_condition#name InfraAlertCondition#name}
        :param policy_id: The ID of the alert policy where this condition should be used. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/infra_alert_condition#policy_id InfraAlertCondition#policy_id}
        :param type: The type of Infrastructure alert condition. Valid values are infra_process_running, infra_metric, and infra_host_not_reporting. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/infra_alert_condition#type InfraAlertCondition#type}
        :param comparison: The operator used to evaluate the threshold value. Valid values are above, below, and equal. Supported by the infra_metric and infra_process_running condition types. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/infra_alert_condition#comparison InfraAlertCondition#comparison}
        :param critical: critical block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/infra_alert_condition#critical InfraAlertCondition#critical}
        :param description: The description of the Infrastructure alert condition. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/infra_alert_condition#description InfraAlertCondition#description}
        :param enabled: Whether the condition is turned on or off. Valid values are true and false. Defaults to true. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/infra_alert_condition#enabled InfraAlertCondition#enabled}
        :param event: The metric event; for example, SystemSample or StorageSample. Supported by the infra_metric condition type. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/infra_alert_condition#event InfraAlertCondition#event}
        :param integration_provider: For alerts on integrations, use this instead of event. Supported by the infra_metric condition type. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/infra_alert_condition#integration_provider InfraAlertCondition#integration_provider}
        :param process_where: Any filters applied to processes; for example: commandName = 'java'. Supported by the infra_process_running condition type. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/infra_alert_condition#process_where InfraAlertCondition#process_where}
        :param runbook_url: Runbook URL to display in notifications. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/infra_alert_condition#runbook_url InfraAlertCondition#runbook_url}
        :param select: The attribute name to identify the metric being targeted; for example, cpuPercent, diskFreePercent, or memoryResidentSizeBytes. The underlying API will automatically populate this value for Infrastructure integrations (for example diskFreePercent), so make sure to explicitly include this value to avoid diff issues. Supported by the infra_metric condition type. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/infra_alert_condition#select InfraAlertCondition#select}
        :param violation_close_timer: Determines how much time, in hours, will pass before a violation is automatically closed. Valid values are 1, 2, 4, 8, 12, 24, 48, or 72 Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/infra_alert_condition#violation_close_timer InfraAlertCondition#violation_close_timer}
        :param warning: warning block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/infra_alert_condition#warning InfraAlertCondition#warning}
        :param where: If applicable, this identifies any Infrastructure host filters used; for example: hostname LIKE '%cassandra%'. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/infra_alert_condition#where InfraAlertCondition#where}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(critical, dict):
            critical = InfraAlertConditionCritical(**critical)
        if isinstance(warning, dict):
            warning = InfraAlertConditionWarning(**warning)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "policy_id": policy_id,
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
        if comparison is not None:
            self._values["comparison"] = comparison
        if critical is not None:
            self._values["critical"] = critical
        if description is not None:
            self._values["description"] = description
        if enabled is not None:
            self._values["enabled"] = enabled
        if event is not None:
            self._values["event"] = event
        if integration_provider is not None:
            self._values["integration_provider"] = integration_provider
        if process_where is not None:
            self._values["process_where"] = process_where
        if runbook_url is not None:
            self._values["runbook_url"] = runbook_url
        if select is not None:
            self._values["select"] = select
        if violation_close_timer is not None:
            self._values["violation_close_timer"] = violation_close_timer
        if warning is not None:
            self._values["warning"] = warning
        if where is not None:
            self._values["where"] = where

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
        '''The Infrastructure alert condition's name.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/infra_alert_condition#name InfraAlertCondition#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def policy_id(self) -> jsii.Number:
        '''The ID of the alert policy where this condition should be used.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/infra_alert_condition#policy_id InfraAlertCondition#policy_id}
        '''
        result = self._values.get("policy_id")
        assert result is not None, "Required property 'policy_id' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''The type of Infrastructure alert condition. Valid values are infra_process_running, infra_metric, and infra_host_not_reporting.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/infra_alert_condition#type InfraAlertCondition#type}
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def comparison(self) -> typing.Optional[builtins.str]:
        '''The operator used to evaluate the threshold value.

        Valid values are above, below, and equal. Supported by the infra_metric and infra_process_running condition types.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/infra_alert_condition#comparison InfraAlertCondition#comparison}
        '''
        result = self._values.get("comparison")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def critical(self) -> typing.Optional["InfraAlertConditionCritical"]:
        '''critical block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/infra_alert_condition#critical InfraAlertCondition#critical}
        '''
        result = self._values.get("critical")
        return typing.cast(typing.Optional["InfraAlertConditionCritical"], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''The description of the Infrastructure alert condition.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/infra_alert_condition#description InfraAlertCondition#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Whether the condition is turned on or off. Valid values are true and false. Defaults to true.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/infra_alert_condition#enabled InfraAlertCondition#enabled}
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def event(self) -> typing.Optional[builtins.str]:
        '''The metric event; for example, SystemSample or StorageSample. Supported by the infra_metric condition type.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/infra_alert_condition#event InfraAlertCondition#event}
        '''
        result = self._values.get("event")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def integration_provider(self) -> typing.Optional[builtins.str]:
        '''For alerts on integrations, use this instead of event. Supported by the infra_metric condition type.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/infra_alert_condition#integration_provider InfraAlertCondition#integration_provider}
        '''
        result = self._values.get("integration_provider")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def process_where(self) -> typing.Optional[builtins.str]:
        '''Any filters applied to processes; for example: commandName = 'java'. Supported by the infra_process_running condition type.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/infra_alert_condition#process_where InfraAlertCondition#process_where}
        '''
        result = self._values.get("process_where")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def runbook_url(self) -> typing.Optional[builtins.str]:
        '''Runbook URL to display in notifications.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/infra_alert_condition#runbook_url InfraAlertCondition#runbook_url}
        '''
        result = self._values.get("runbook_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def select(self) -> typing.Optional[builtins.str]:
        '''The attribute name to identify the metric being targeted;

        for example, cpuPercent, diskFreePercent, or memoryResidentSizeBytes. The underlying API will automatically populate this value for Infrastructure integrations (for example diskFreePercent), so make sure to explicitly include this value to avoid diff issues. Supported by the infra_metric condition type.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/infra_alert_condition#select InfraAlertCondition#select}
        '''
        result = self._values.get("select")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def violation_close_timer(self) -> typing.Optional[jsii.Number]:
        '''Determines how much time, in hours, will pass before a violation is automatically closed.

        Valid values are 1, 2, 4, 8, 12, 24, 48, or 72

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/infra_alert_condition#violation_close_timer InfraAlertCondition#violation_close_timer}
        '''
        result = self._values.get("violation_close_timer")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def warning(self) -> typing.Optional["InfraAlertConditionWarning"]:
        '''warning block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/infra_alert_condition#warning InfraAlertCondition#warning}
        '''
        result = self._values.get("warning")
        return typing.cast(typing.Optional["InfraAlertConditionWarning"], result)

    @builtins.property
    def where(self) -> typing.Optional[builtins.str]:
        '''If applicable, this identifies any Infrastructure host filters used; for example: hostname LIKE '%cassandra%'.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/infra_alert_condition#where InfraAlertCondition#where}
        '''
        result = self._values.get("where")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "InfraAlertConditionConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.InfraAlertConditionCritical",
    jsii_struct_bases=[],
    name_mapping={
        "duration": "duration",
        "time_function": "timeFunction",
        "value": "value",
    },
)
class InfraAlertConditionCritical:
    def __init__(
        self,
        *,
        duration: jsii.Number,
        time_function: typing.Optional[builtins.str] = None,
        value: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param duration: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/infra_alert_condition#duration InfraAlertCondition#duration}.
        :param time_function: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/infra_alert_condition#time_function InfraAlertCondition#time_function}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/infra_alert_condition#value InfraAlertCondition#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "duration": duration,
        }
        if time_function is not None:
            self._values["time_function"] = time_function
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def duration(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/infra_alert_condition#duration InfraAlertCondition#duration}.'''
        result = self._values.get("duration")
        assert result is not None, "Required property 'duration' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def time_function(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/infra_alert_condition#time_function InfraAlertCondition#time_function}.'''
        result = self._values.get("time_function")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def value(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/infra_alert_condition#value InfraAlertCondition#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "InfraAlertConditionCritical(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class InfraAlertConditionCriticalOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-newrelic.InfraAlertConditionCriticalOutputReference",
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

    @jsii.member(jsii_name="resetTimeFunction")
    def reset_time_function(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeFunction", []))

    @jsii.member(jsii_name="resetValue")
    def reset_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValue", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="durationInput")
    def duration_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "durationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeFunctionInput")
    def time_function_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "timeFunctionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "valueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="duration")
    def duration(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "duration"))

    @duration.setter
    def duration(self, value: jsii.Number) -> None:
        jsii.set(self, "duration", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeFunction")
    def time_function(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "timeFunction"))

    @time_function.setter
    def time_function(self, value: builtins.str) -> None:
        jsii.set(self, "timeFunction", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="value")
    def value(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "value"))

    @value.setter
    def value(self, value: jsii.Number) -> None:
        jsii.set(self, "value", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[InfraAlertConditionCritical]:
        return typing.cast(typing.Optional[InfraAlertConditionCritical], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[InfraAlertConditionCritical],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.InfraAlertConditionWarning",
    jsii_struct_bases=[],
    name_mapping={
        "duration": "duration",
        "time_function": "timeFunction",
        "value": "value",
    },
)
class InfraAlertConditionWarning:
    def __init__(
        self,
        *,
        duration: jsii.Number,
        time_function: typing.Optional[builtins.str] = None,
        value: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param duration: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/infra_alert_condition#duration InfraAlertCondition#duration}.
        :param time_function: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/infra_alert_condition#time_function InfraAlertCondition#time_function}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/infra_alert_condition#value InfraAlertCondition#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "duration": duration,
        }
        if time_function is not None:
            self._values["time_function"] = time_function
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def duration(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/infra_alert_condition#duration InfraAlertCondition#duration}.'''
        result = self._values.get("duration")
        assert result is not None, "Required property 'duration' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def time_function(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/infra_alert_condition#time_function InfraAlertCondition#time_function}.'''
        result = self._values.get("time_function")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def value(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/infra_alert_condition#value InfraAlertCondition#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "InfraAlertConditionWarning(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class InfraAlertConditionWarningOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-newrelic.InfraAlertConditionWarningOutputReference",
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

    @jsii.member(jsii_name="resetTimeFunction")
    def reset_time_function(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeFunction", []))

    @jsii.member(jsii_name="resetValue")
    def reset_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValue", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="durationInput")
    def duration_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "durationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeFunctionInput")
    def time_function_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "timeFunctionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "valueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="duration")
    def duration(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "duration"))

    @duration.setter
    def duration(self, value: jsii.Number) -> None:
        jsii.set(self, "duration", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeFunction")
    def time_function(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "timeFunction"))

    @time_function.setter
    def time_function(self, value: builtins.str) -> None:
        jsii.set(self, "timeFunction", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="value")
    def value(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "value"))

    @value.setter
    def value(self, value: jsii.Number) -> None:
        jsii.set(self, "value", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[InfraAlertConditionWarning]:
        return typing.cast(typing.Optional[InfraAlertConditionWarning], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[InfraAlertConditionWarning],
    ) -> None:
        jsii.set(self, "internalValue", value)


class InsightsEvent(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-newrelic.InsightsEvent",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/newrelic/r/insights_event newrelic_insights_event}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        event: typing.Sequence["InsightsEventEvent"],
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/newrelic/r/insights_event newrelic_insights_event} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param event: event block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/insights_event#event InsightsEvent#event}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = InsightsEventConfig(
            event=event,
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
    @jsii.member(jsii_name="eventInput")
    def event_input(self) -> typing.Optional[typing.List["InsightsEventEvent"]]:
        return typing.cast(typing.Optional[typing.List["InsightsEventEvent"]], jsii.get(self, "eventInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="event")
    def event(self) -> typing.List["InsightsEventEvent"]:
        return typing.cast(typing.List["InsightsEventEvent"], jsii.get(self, "event"))

    @event.setter
    def event(self, value: typing.List["InsightsEventEvent"]) -> None:
        jsii.set(self, "event", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.InsightsEventConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "event": "event",
    },
)
class InsightsEventConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        event: typing.Sequence["InsightsEventEvent"],
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param event: event block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/insights_event#event InsightsEvent#event}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "event": event,
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
    def event(self) -> typing.List["InsightsEventEvent"]:
        '''event block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/insights_event#event InsightsEvent#event}
        '''
        result = self._values.get("event")
        assert result is not None, "Required property 'event' is missing"
        return typing.cast(typing.List["InsightsEventEvent"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "InsightsEventConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.InsightsEventEvent",
    jsii_struct_bases=[],
    name_mapping={"attribute": "attribute", "type": "type", "timestamp": "timestamp"},
)
class InsightsEventEvent:
    def __init__(
        self,
        *,
        attribute: typing.Sequence["InsightsEventEventAttribute"],
        type: builtins.str,
        timestamp: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param attribute: attribute block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/insights_event#attribute InsightsEvent#attribute}
        :param type: The event's name. Can be a combination of alphanumeric characters, underscores, and colons. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/insights_event#type InsightsEvent#type}
        :param timestamp: Must be a Unix epoch timestamp. You can define timestamps either in seconds or in milliseconds. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/insights_event#timestamp InsightsEvent#timestamp}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "attribute": attribute,
            "type": type,
        }
        if timestamp is not None:
            self._values["timestamp"] = timestamp

    @builtins.property
    def attribute(self) -> typing.List["InsightsEventEventAttribute"]:
        '''attribute block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/insights_event#attribute InsightsEvent#attribute}
        '''
        result = self._values.get("attribute")
        assert result is not None, "Required property 'attribute' is missing"
        return typing.cast(typing.List["InsightsEventEventAttribute"], result)

    @builtins.property
    def type(self) -> builtins.str:
        '''The event's name. Can be a combination of alphanumeric characters, underscores, and colons.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/insights_event#type InsightsEvent#type}
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def timestamp(self) -> typing.Optional[jsii.Number]:
        '''Must be a Unix epoch timestamp. You can define timestamps either in seconds or in milliseconds.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/insights_event#timestamp InsightsEvent#timestamp}
        '''
        result = self._values.get("timestamp")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "InsightsEventEvent(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.InsightsEventEventAttribute",
    jsii_struct_bases=[],
    name_mapping={"key": "key", "value": "value", "type": "type"},
)
class InsightsEventEventAttribute:
    def __init__(
        self,
        *,
        key: builtins.str,
        value: builtins.str,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param key: The name of the attribute. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/insights_event#key InsightsEvent#key}
        :param value: The value of the attribute. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/insights_event#value InsightsEvent#value}
        :param type: Specify the type for the attribute value. This is useful when passing integer or float values to Insights. Allowed values are string, int, or float. Defaults to string. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/insights_event#type InsightsEvent#type}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "key": key,
            "value": value,
        }
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def key(self) -> builtins.str:
        '''The name of the attribute.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/insights_event#key InsightsEvent#key}
        '''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''The value of the attribute.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/insights_event#value InsightsEvent#value}
        '''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Specify the type for the attribute value.

        This is useful when passing integer or float values to Insights. Allowed values are string, int, or float. Defaults to string.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/insights_event#type InsightsEvent#type}
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "InsightsEventEventAttribute(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NewrelicProvider(
    cdktf.TerraformProvider,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-newrelic.NewrelicProvider",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/newrelic newrelic}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        account_id: jsii.Number,
        admin_api_key: typing.Optional[builtins.str] = None,
        alias: typing.Optional[builtins.str] = None,
        api_key: typing.Optional[builtins.str] = None,
        api_url: typing.Optional[builtins.str] = None,
        cacert_file: typing.Optional[builtins.str] = None,
        infrastructure_api_url: typing.Optional[builtins.str] = None,
        insecure_skip_verify: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        insights_insert_key: typing.Optional[builtins.str] = None,
        insights_insert_url: typing.Optional[builtins.str] = None,
        insights_query_url: typing.Optional[builtins.str] = None,
        nerdgraph_api_url: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
        synthetics_api_url: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/newrelic newrelic} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param account_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic#account_id NewrelicProvider#account_id}.
        :param admin_api_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic#admin_api_key NewrelicProvider#admin_api_key}.
        :param alias: Alias name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic#alias NewrelicProvider#alias}
        :param api_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic#api_key NewrelicProvider#api_key}.
        :param api_url: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic#api_url NewrelicProvider#api_url}.
        :param cacert_file: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic#cacert_file NewrelicProvider#cacert_file}.
        :param infrastructure_api_url: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic#infrastructure_api_url NewrelicProvider#infrastructure_api_url}.
        :param insecure_skip_verify: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic#insecure_skip_verify NewrelicProvider#insecure_skip_verify}.
        :param insights_insert_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic#insights_insert_key NewrelicProvider#insights_insert_key}.
        :param insights_insert_url: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic#insights_insert_url NewrelicProvider#insights_insert_url}.
        :param insights_query_url: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic#insights_query_url NewrelicProvider#insights_query_url}.
        :param nerdgraph_api_url: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic#nerdgraph_api_url NewrelicProvider#nerdgraph_api_url}.
        :param region: The data center for which your New Relic account is configured. Only one region per provider block is permitted. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic#region NewrelicProvider#region}
        :param synthetics_api_url: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic#synthetics_api_url NewrelicProvider#synthetics_api_url}.
        '''
        config = NewrelicProviderConfig(
            account_id=account_id,
            admin_api_key=admin_api_key,
            alias=alias,
            api_key=api_key,
            api_url=api_url,
            cacert_file=cacert_file,
            infrastructure_api_url=infrastructure_api_url,
            insecure_skip_verify=insecure_skip_verify,
            insights_insert_key=insights_insert_key,
            insights_insert_url=insights_insert_url,
            insights_query_url=insights_query_url,
            nerdgraph_api_url=nerdgraph_api_url,
            region=region,
            synthetics_api_url=synthetics_api_url,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetAdminApiKey")
    def reset_admin_api_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAdminApiKey", []))

    @jsii.member(jsii_name="resetAlias")
    def reset_alias(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAlias", []))

    @jsii.member(jsii_name="resetApiKey")
    def reset_api_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetApiKey", []))

    @jsii.member(jsii_name="resetApiUrl")
    def reset_api_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetApiUrl", []))

    @jsii.member(jsii_name="resetCacertFile")
    def reset_cacert_file(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCacertFile", []))

    @jsii.member(jsii_name="resetInfrastructureApiUrl")
    def reset_infrastructure_api_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInfrastructureApiUrl", []))

    @jsii.member(jsii_name="resetInsecureSkipVerify")
    def reset_insecure_skip_verify(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInsecureSkipVerify", []))

    @jsii.member(jsii_name="resetInsightsInsertKey")
    def reset_insights_insert_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInsightsInsertKey", []))

    @jsii.member(jsii_name="resetInsightsInsertUrl")
    def reset_insights_insert_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInsightsInsertUrl", []))

    @jsii.member(jsii_name="resetInsightsQueryUrl")
    def reset_insights_query_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInsightsQueryUrl", []))

    @jsii.member(jsii_name="resetNerdgraphApiUrl")
    def reset_nerdgraph_api_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNerdgraphApiUrl", []))

    @jsii.member(jsii_name="resetRegion")
    def reset_region(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegion", []))

    @jsii.member(jsii_name="resetSyntheticsApiUrl")
    def reset_synthetics_api_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSyntheticsApiUrl", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "accountIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="adminApiKeyInput")
    def admin_api_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "adminApiKeyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="aliasInput")
    def alias_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "aliasInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiKeyInput")
    def api_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "apiKeyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiUrlInput")
    def api_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "apiUrlInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cacertFileInput")
    def cacert_file_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cacertFileInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="infrastructureApiUrlInput")
    def infrastructure_api_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "infrastructureApiUrlInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="insecureSkipVerifyInput")
    def insecure_skip_verify_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "insecureSkipVerifyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="insightsInsertKeyInput")
    def insights_insert_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "insightsInsertKeyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="insightsInsertUrlInput")
    def insights_insert_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "insightsInsertUrlInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="insightsQueryUrlInput")
    def insights_query_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "insightsQueryUrlInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nerdgraphApiUrlInput")
    def nerdgraph_api_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nerdgraphApiUrlInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="regionInput")
    def region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "regionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="syntheticsApiUrlInput")
    def synthetics_api_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "syntheticsApiUrlInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: typing.Optional[jsii.Number]) -> None:
        jsii.set(self, "accountId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="adminApiKey")
    def admin_api_key(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "adminApiKey"))

    @admin_api_key.setter
    def admin_api_key(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "adminApiKey", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="alias")
    def alias(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "alias"))

    @alias.setter
    def alias(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "alias", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiKey")
    def api_key(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "apiKey"))

    @api_key.setter
    def api_key(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "apiKey", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiUrl")
    def api_url(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "apiUrl"))

    @api_url.setter
    def api_url(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "apiUrl", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cacertFile")
    def cacert_file(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cacertFile"))

    @cacert_file.setter
    def cacert_file(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "cacertFile", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="infrastructureApiUrl")
    def infrastructure_api_url(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "infrastructureApiUrl"))

    @infrastructure_api_url.setter
    def infrastructure_api_url(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "infrastructureApiUrl", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="insecureSkipVerify")
    def insecure_skip_verify(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "insecureSkipVerify"))

    @insecure_skip_verify.setter
    def insecure_skip_verify(
        self,
        value: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "insecureSkipVerify", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="insightsInsertKey")
    def insights_insert_key(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "insightsInsertKey"))

    @insights_insert_key.setter
    def insights_insert_key(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "insightsInsertKey", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="insightsInsertUrl")
    def insights_insert_url(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "insightsInsertUrl"))

    @insights_insert_url.setter
    def insights_insert_url(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "insightsInsertUrl", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="insightsQueryUrl")
    def insights_query_url(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "insightsQueryUrl"))

    @insights_query_url.setter
    def insights_query_url(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "insightsQueryUrl", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nerdgraphApiUrl")
    def nerdgraph_api_url(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nerdgraphApiUrl"))

    @nerdgraph_api_url.setter
    def nerdgraph_api_url(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "nerdgraphApiUrl", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="region")
    def region(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "region"))

    @region.setter
    def region(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "region", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="syntheticsApiUrl")
    def synthetics_api_url(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "syntheticsApiUrl"))

    @synthetics_api_url.setter
    def synthetics_api_url(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "syntheticsApiUrl", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.NewrelicProviderConfig",
    jsii_struct_bases=[],
    name_mapping={
        "account_id": "accountId",
        "admin_api_key": "adminApiKey",
        "alias": "alias",
        "api_key": "apiKey",
        "api_url": "apiUrl",
        "cacert_file": "cacertFile",
        "infrastructure_api_url": "infrastructureApiUrl",
        "insecure_skip_verify": "insecureSkipVerify",
        "insights_insert_key": "insightsInsertKey",
        "insights_insert_url": "insightsInsertUrl",
        "insights_query_url": "insightsQueryUrl",
        "nerdgraph_api_url": "nerdgraphApiUrl",
        "region": "region",
        "synthetics_api_url": "syntheticsApiUrl",
    },
)
class NewrelicProviderConfig:
    def __init__(
        self,
        *,
        account_id: jsii.Number,
        admin_api_key: typing.Optional[builtins.str] = None,
        alias: typing.Optional[builtins.str] = None,
        api_key: typing.Optional[builtins.str] = None,
        api_url: typing.Optional[builtins.str] = None,
        cacert_file: typing.Optional[builtins.str] = None,
        infrastructure_api_url: typing.Optional[builtins.str] = None,
        insecure_skip_verify: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        insights_insert_key: typing.Optional[builtins.str] = None,
        insights_insert_url: typing.Optional[builtins.str] = None,
        insights_query_url: typing.Optional[builtins.str] = None,
        nerdgraph_api_url: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
        synthetics_api_url: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param account_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic#account_id NewrelicProvider#account_id}.
        :param admin_api_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic#admin_api_key NewrelicProvider#admin_api_key}.
        :param alias: Alias name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic#alias NewrelicProvider#alias}
        :param api_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic#api_key NewrelicProvider#api_key}.
        :param api_url: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic#api_url NewrelicProvider#api_url}.
        :param cacert_file: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic#cacert_file NewrelicProvider#cacert_file}.
        :param infrastructure_api_url: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic#infrastructure_api_url NewrelicProvider#infrastructure_api_url}.
        :param insecure_skip_verify: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic#insecure_skip_verify NewrelicProvider#insecure_skip_verify}.
        :param insights_insert_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic#insights_insert_key NewrelicProvider#insights_insert_key}.
        :param insights_insert_url: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic#insights_insert_url NewrelicProvider#insights_insert_url}.
        :param insights_query_url: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic#insights_query_url NewrelicProvider#insights_query_url}.
        :param nerdgraph_api_url: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic#nerdgraph_api_url NewrelicProvider#nerdgraph_api_url}.
        :param region: The data center for which your New Relic account is configured. Only one region per provider block is permitted. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic#region NewrelicProvider#region}
        :param synthetics_api_url: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic#synthetics_api_url NewrelicProvider#synthetics_api_url}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "account_id": account_id,
        }
        if admin_api_key is not None:
            self._values["admin_api_key"] = admin_api_key
        if alias is not None:
            self._values["alias"] = alias
        if api_key is not None:
            self._values["api_key"] = api_key
        if api_url is not None:
            self._values["api_url"] = api_url
        if cacert_file is not None:
            self._values["cacert_file"] = cacert_file
        if infrastructure_api_url is not None:
            self._values["infrastructure_api_url"] = infrastructure_api_url
        if insecure_skip_verify is not None:
            self._values["insecure_skip_verify"] = insecure_skip_verify
        if insights_insert_key is not None:
            self._values["insights_insert_key"] = insights_insert_key
        if insights_insert_url is not None:
            self._values["insights_insert_url"] = insights_insert_url
        if insights_query_url is not None:
            self._values["insights_query_url"] = insights_query_url
        if nerdgraph_api_url is not None:
            self._values["nerdgraph_api_url"] = nerdgraph_api_url
        if region is not None:
            self._values["region"] = region
        if synthetics_api_url is not None:
            self._values["synthetics_api_url"] = synthetics_api_url

    @builtins.property
    def account_id(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic#account_id NewrelicProvider#account_id}.'''
        result = self._values.get("account_id")
        assert result is not None, "Required property 'account_id' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def admin_api_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic#admin_api_key NewrelicProvider#admin_api_key}.'''
        result = self._values.get("admin_api_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def alias(self) -> typing.Optional[builtins.str]:
        '''Alias name.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic#alias NewrelicProvider#alias}
        '''
        result = self._values.get("alias")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def api_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic#api_key NewrelicProvider#api_key}.'''
        result = self._values.get("api_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def api_url(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic#api_url NewrelicProvider#api_url}.'''
        result = self._values.get("api_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cacert_file(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic#cacert_file NewrelicProvider#cacert_file}.'''
        result = self._values.get("cacert_file")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def infrastructure_api_url(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic#infrastructure_api_url NewrelicProvider#infrastructure_api_url}.'''
        result = self._values.get("infrastructure_api_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def insecure_skip_verify(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic#insecure_skip_verify NewrelicProvider#insecure_skip_verify}.'''
        result = self._values.get("insecure_skip_verify")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def insights_insert_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic#insights_insert_key NewrelicProvider#insights_insert_key}.'''
        result = self._values.get("insights_insert_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def insights_insert_url(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic#insights_insert_url NewrelicProvider#insights_insert_url}.'''
        result = self._values.get("insights_insert_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def insights_query_url(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic#insights_query_url NewrelicProvider#insights_query_url}.'''
        result = self._values.get("insights_query_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def nerdgraph_api_url(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic#nerdgraph_api_url NewrelicProvider#nerdgraph_api_url}.'''
        result = self._values.get("nerdgraph_api_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''The data center for which your New Relic account is configured. Only one region per provider block is permitted.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic#region NewrelicProvider#region}
        '''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def synthetics_api_url(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic#synthetics_api_url NewrelicProvider#synthetics_api_url}.'''
        result = self._values.get("synthetics_api_url")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NewrelicProviderConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NrqlAlertCondition(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-newrelic.NrqlAlertCondition",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition newrelic_nrql_alert_condition}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        nrql: "NrqlAlertConditionNrql",
        policy_id: jsii.Number,
        account_id: typing.Optional[jsii.Number] = None,
        aggregation_delay: typing.Optional[jsii.Number] = None,
        aggregation_method: typing.Optional[builtins.str] = None,
        aggregation_timer: typing.Optional[jsii.Number] = None,
        aggregation_window: typing.Optional[jsii.Number] = None,
        baseline_direction: typing.Optional[builtins.str] = None,
        close_violations_on_expiration: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        critical: typing.Optional["NrqlAlertConditionCritical"] = None,
        description: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        expected_groups: typing.Optional[jsii.Number] = None,
        expiration_duration: typing.Optional[jsii.Number] = None,
        fill_option: typing.Optional[builtins.str] = None,
        fill_value: typing.Optional[jsii.Number] = None,
        ignore_overlap: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        open_violation_on_expiration: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        open_violation_on_group_overlap: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        runbook_url: typing.Optional[builtins.str] = None,
        term: typing.Optional[typing.Sequence["NrqlAlertConditionTerm"]] = None,
        type: typing.Optional[builtins.str] = None,
        value_function: typing.Optional[builtins.str] = None,
        violation_time_limit: typing.Optional[builtins.str] = None,
        violation_time_limit_seconds: typing.Optional[jsii.Number] = None,
        warning: typing.Optional["NrqlAlertConditionWarning"] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition newrelic_nrql_alert_condition} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: The title of the condition. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#name NrqlAlertCondition#name}
        :param nrql: nrql block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#nrql NrqlAlertCondition#nrql}
        :param policy_id: The ID of the policy where this condition should be used. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#policy_id NrqlAlertCondition#policy_id}
        :param account_id: The New Relic account ID for managing your NRQL alert conditions. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#account_id NrqlAlertCondition#account_id}
        :param aggregation_delay: How long we wait for data that belongs in each aggregation window. Depending on your data, a longer delay may increase accuracy but delay notifications. Use aggregationDelay with the EVENT_FLOW and CADENCE aggregation methods. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#aggregation_delay NrqlAlertCondition#aggregation_delay}
        :param aggregation_method: The method that determines when we consider an aggregation window to be complete so that we can evaluate the signal for violations. Default is CADENCE. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#aggregation_method NrqlAlertCondition#aggregation_method}
        :param aggregation_timer: How long we wait after each data point arrives to make sure we've processed the whole batch. Use aggregationTimer with the EVENT_TIMER aggregation method. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#aggregation_timer NrqlAlertCondition#aggregation_timer}
        :param aggregation_window: The duration of the time window used to evaluate the NRQL query, in seconds. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#aggregation_window NrqlAlertCondition#aggregation_window}
        :param baseline_direction: The baseline direction of a baseline NRQL alert condition. Valid values are: 'LOWER_ONLY', 'UPPER_AND_LOWER', 'UPPER_ONLY' (case insensitive). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#baseline_direction NrqlAlertCondition#baseline_direction}
        :param close_violations_on_expiration: Whether to close all open violations when the signal expires. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#close_violations_on_expiration NrqlAlertCondition#close_violations_on_expiration}
        :param critical: critical block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#critical NrqlAlertCondition#critical}
        :param description: The description of the NRQL alert condition. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#description NrqlAlertCondition#description}
        :param enabled: Whether or not to enable the alert condition. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#enabled NrqlAlertCondition#enabled}
        :param expected_groups: Number of expected groups when using outlier detection. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#expected_groups NrqlAlertCondition#expected_groups}
        :param expiration_duration: The amount of time (in seconds) to wait before considering the signal expired. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#expiration_duration NrqlAlertCondition#expiration_duration}
        :param fill_option: Which strategy to use when filling gaps in the signal. If static, the 'fill value' will be used for filling gaps in the signal. Valid values are: 'NONE', 'LAST_VALUE', or 'STATIC' (case insensitive). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#fill_option NrqlAlertCondition#fill_option}
        :param fill_value: If using the 'static' fill option, this value will be used for filling gaps in the signal. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#fill_value NrqlAlertCondition#fill_value}
        :param ignore_overlap: Whether to look for a convergence of groups when using outlier detection. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#ignore_overlap NrqlAlertCondition#ignore_overlap}
        :param open_violation_on_expiration: Whether to create a new violation to capture that the signal expired. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#open_violation_on_expiration NrqlAlertCondition#open_violation_on_expiration}
        :param open_violation_on_group_overlap: Whether overlapping groups should produce a violation. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#open_violation_on_group_overlap NrqlAlertCondition#open_violation_on_group_overlap}
        :param runbook_url: Runbook URL to display in notifications. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#runbook_url NrqlAlertCondition#runbook_url}
        :param term: term block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#term NrqlAlertCondition#term}
        :param type: The type of NRQL alert condition to create. Valid values are: 'static', 'baseline', 'outlier' (deprecated). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#type NrqlAlertCondition#type}
        :param value_function: Valid values are: 'single_value' or 'sum'. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#value_function NrqlAlertCondition#value_function}
        :param violation_time_limit: Sets a time limit, in hours, that will automatically force-close a long-lasting violation after the time limit you select. Possible values are 'ONE_HOUR', 'TWO_HOURS', 'FOUR_HOURS', 'EIGHT_HOURS', 'TWELVE_HOURS', 'TWENTY_FOUR_HOURS', 'THIRTY_DAYS' (case insensitive). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#violation_time_limit NrqlAlertCondition#violation_time_limit}
        :param violation_time_limit_seconds: Sets a time limit, in seconds, that will automatically force-close a long-lasting violation after the time limit you select. Must be in the range of 300 to 2592000 (inclusive) Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#violation_time_limit_seconds NrqlAlertCondition#violation_time_limit_seconds}
        :param warning: warning block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#warning NrqlAlertCondition#warning}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = NrqlAlertConditionConfig(
            name=name,
            nrql=nrql,
            policy_id=policy_id,
            account_id=account_id,
            aggregation_delay=aggregation_delay,
            aggregation_method=aggregation_method,
            aggregation_timer=aggregation_timer,
            aggregation_window=aggregation_window,
            baseline_direction=baseline_direction,
            close_violations_on_expiration=close_violations_on_expiration,
            critical=critical,
            description=description,
            enabled=enabled,
            expected_groups=expected_groups,
            expiration_duration=expiration_duration,
            fill_option=fill_option,
            fill_value=fill_value,
            ignore_overlap=ignore_overlap,
            open_violation_on_expiration=open_violation_on_expiration,
            open_violation_on_group_overlap=open_violation_on_group_overlap,
            runbook_url=runbook_url,
            term=term,
            type=type,
            value_function=value_function,
            violation_time_limit=violation_time_limit,
            violation_time_limit_seconds=violation_time_limit_seconds,
            warning=warning,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putCritical")
    def put_critical(
        self,
        *,
        threshold: jsii.Number,
        duration: typing.Optional[jsii.Number] = None,
        operator: typing.Optional[builtins.str] = None,
        threshold_duration: typing.Optional[jsii.Number] = None,
        threshold_occurrences: typing.Optional[builtins.str] = None,
        time_function: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param threshold: Must be 0 or greater. For baseline conditions must be in range [1, 1000]. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#threshold NrqlAlertCondition#threshold}
        :param duration: In minutes, must be in the range of 1 to 120 (inclusive). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#duration NrqlAlertCondition#duration}
        :param operator: One of (above, below, equals). Defaults to 'equals'. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#operator NrqlAlertCondition#operator}
        :param threshold_duration: The duration, in seconds, that the threshold must violate in order to create a violation. Value must be a multiple of the 'aggregation_window' (which has a default of 60 seconds). Value must be within 120-3600 seconds for baseline and outlier conditions, within 120-7200 seconds for static conditions with the sum value function, and within 60-7200 seconds for static conditions with the single_value value function. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#threshold_duration NrqlAlertCondition#threshold_duration}
        :param threshold_occurrences: The criteria for how many data points must be in violation for the specified threshold duration. Valid values are: 'ALL' or 'AT_LEAST_ONCE' (case insensitive). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#threshold_occurrences NrqlAlertCondition#threshold_occurrences}
        :param time_function: Valid values are: 'all' or 'any'. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#time_function NrqlAlertCondition#time_function}
        '''
        value = NrqlAlertConditionCritical(
            threshold=threshold,
            duration=duration,
            operator=operator,
            threshold_duration=threshold_duration,
            threshold_occurrences=threshold_occurrences,
            time_function=time_function,
        )

        return typing.cast(None, jsii.invoke(self, "putCritical", [value]))

    @jsii.member(jsii_name="putNrql")
    def put_nrql(
        self,
        *,
        query: builtins.str,
        evaluation_offset: typing.Optional[jsii.Number] = None,
        since_value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param query: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#query NrqlAlertCondition#query}.
        :param evaluation_offset: NRQL queries are evaluated in one-minute time windows. The start time depends on the value you provide in the NRQL condition's ``evaluation_offset``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#evaluation_offset NrqlAlertCondition#evaluation_offset}
        :param since_value: NRQL queries are evaluated in one-minute time windows. The start time depends on the value you provide in the NRQL condition's ``since_value``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#since_value NrqlAlertCondition#since_value}
        '''
        value = NrqlAlertConditionNrql(
            query=query, evaluation_offset=evaluation_offset, since_value=since_value
        )

        return typing.cast(None, jsii.invoke(self, "putNrql", [value]))

    @jsii.member(jsii_name="putWarning")
    def put_warning(
        self,
        *,
        threshold: jsii.Number,
        duration: typing.Optional[jsii.Number] = None,
        operator: typing.Optional[builtins.str] = None,
        threshold_duration: typing.Optional[jsii.Number] = None,
        threshold_occurrences: typing.Optional[builtins.str] = None,
        time_function: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param threshold: Must be 0 or greater. For baseline conditions must be in range [1, 1000]. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#threshold NrqlAlertCondition#threshold}
        :param duration: In minutes, must be in the range of 1 to 120 (inclusive). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#duration NrqlAlertCondition#duration}
        :param operator: One of (above, below, equals). Defaults to 'equals'. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#operator NrqlAlertCondition#operator}
        :param threshold_duration: The duration, in seconds, that the threshold must violate in order to create a violation. Value must be a multiple of the 'aggregation_window' (which has a default of 60 seconds). Value must be within 120-3600 seconds for baseline and outlier conditions, within 120-7200 seconds for static conditions with the sum value function, and within 60-7200 seconds for static conditions with the single_value value function. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#threshold_duration NrqlAlertCondition#threshold_duration}
        :param threshold_occurrences: The criteria for how many data points must be in violation for the specified threshold duration. Valid values are: 'ALL' or 'AT_LEAST_ONCE' (case insensitive). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#threshold_occurrences NrqlAlertCondition#threshold_occurrences}
        :param time_function: Valid values are: 'all' or 'any'. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#time_function NrqlAlertCondition#time_function}
        '''
        value = NrqlAlertConditionWarning(
            threshold=threshold,
            duration=duration,
            operator=operator,
            threshold_duration=threshold_duration,
            threshold_occurrences=threshold_occurrences,
            time_function=time_function,
        )

        return typing.cast(None, jsii.invoke(self, "putWarning", [value]))

    @jsii.member(jsii_name="resetAccountId")
    def reset_account_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccountId", []))

    @jsii.member(jsii_name="resetAggregationDelay")
    def reset_aggregation_delay(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAggregationDelay", []))

    @jsii.member(jsii_name="resetAggregationMethod")
    def reset_aggregation_method(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAggregationMethod", []))

    @jsii.member(jsii_name="resetAggregationTimer")
    def reset_aggregation_timer(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAggregationTimer", []))

    @jsii.member(jsii_name="resetAggregationWindow")
    def reset_aggregation_window(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAggregationWindow", []))

    @jsii.member(jsii_name="resetBaselineDirection")
    def reset_baseline_direction(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBaselineDirection", []))

    @jsii.member(jsii_name="resetCloseViolationsOnExpiration")
    def reset_close_violations_on_expiration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCloseViolationsOnExpiration", []))

    @jsii.member(jsii_name="resetCritical")
    def reset_critical(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCritical", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="resetExpectedGroups")
    def reset_expected_groups(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExpectedGroups", []))

    @jsii.member(jsii_name="resetExpirationDuration")
    def reset_expiration_duration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExpirationDuration", []))

    @jsii.member(jsii_name="resetFillOption")
    def reset_fill_option(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFillOption", []))

    @jsii.member(jsii_name="resetFillValue")
    def reset_fill_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFillValue", []))

    @jsii.member(jsii_name="resetIgnoreOverlap")
    def reset_ignore_overlap(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIgnoreOverlap", []))

    @jsii.member(jsii_name="resetOpenViolationOnExpiration")
    def reset_open_violation_on_expiration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOpenViolationOnExpiration", []))

    @jsii.member(jsii_name="resetOpenViolationOnGroupOverlap")
    def reset_open_violation_on_group_overlap(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOpenViolationOnGroupOverlap", []))

    @jsii.member(jsii_name="resetRunbookUrl")
    def reset_runbook_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRunbookUrl", []))

    @jsii.member(jsii_name="resetTerm")
    def reset_term(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTerm", []))

    @jsii.member(jsii_name="resetType")
    def reset_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetType", []))

    @jsii.member(jsii_name="resetValueFunction")
    def reset_value_function(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValueFunction", []))

    @jsii.member(jsii_name="resetViolationTimeLimit")
    def reset_violation_time_limit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetViolationTimeLimit", []))

    @jsii.member(jsii_name="resetViolationTimeLimitSeconds")
    def reset_violation_time_limit_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetViolationTimeLimitSeconds", []))

    @jsii.member(jsii_name="resetWarning")
    def reset_warning(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWarning", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="critical")
    def critical(self) -> "NrqlAlertConditionCriticalOutputReference":
        return typing.cast("NrqlAlertConditionCriticalOutputReference", jsii.get(self, "critical"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nrql")
    def nrql(self) -> "NrqlAlertConditionNrqlOutputReference":
        return typing.cast("NrqlAlertConditionNrqlOutputReference", jsii.get(self, "nrql"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="warning")
    def warning(self) -> "NrqlAlertConditionWarningOutputReference":
        return typing.cast("NrqlAlertConditionWarningOutputReference", jsii.get(self, "warning"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "accountIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="aggregationDelayInput")
    def aggregation_delay_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "aggregationDelayInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="aggregationMethodInput")
    def aggregation_method_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "aggregationMethodInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="aggregationTimerInput")
    def aggregation_timer_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "aggregationTimerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="aggregationWindowInput")
    def aggregation_window_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "aggregationWindowInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="baselineDirectionInput")
    def baseline_direction_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "baselineDirectionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="closeViolationsOnExpirationInput")
    def close_violations_on_expiration_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "closeViolationsOnExpirationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="criticalInput")
    def critical_input(self) -> typing.Optional["NrqlAlertConditionCritical"]:
        return typing.cast(typing.Optional["NrqlAlertConditionCritical"], jsii.get(self, "criticalInput"))

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
    @jsii.member(jsii_name="expectedGroupsInput")
    def expected_groups_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "expectedGroupsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="expirationDurationInput")
    def expiration_duration_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "expirationDurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fillOptionInput")
    def fill_option_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fillOptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fillValueInput")
    def fill_value_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "fillValueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ignoreOverlapInput")
    def ignore_overlap_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "ignoreOverlapInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nrqlInput")
    def nrql_input(self) -> typing.Optional["NrqlAlertConditionNrql"]:
        return typing.cast(typing.Optional["NrqlAlertConditionNrql"], jsii.get(self, "nrqlInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="openViolationOnExpirationInput")
    def open_violation_on_expiration_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "openViolationOnExpirationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="openViolationOnGroupOverlapInput")
    def open_violation_on_group_overlap_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "openViolationOnGroupOverlapInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyIdInput")
    def policy_id_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "policyIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="runbookUrlInput")
    def runbook_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "runbookUrlInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="termInput")
    def term_input(self) -> typing.Optional[typing.List["NrqlAlertConditionTerm"]]:
        return typing.cast(typing.Optional[typing.List["NrqlAlertConditionTerm"]], jsii.get(self, "termInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="valueFunctionInput")
    def value_function_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "valueFunctionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="violationTimeLimitInput")
    def violation_time_limit_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "violationTimeLimitInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="violationTimeLimitSecondsInput")
    def violation_time_limit_seconds_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "violationTimeLimitSecondsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="warningInput")
    def warning_input(self) -> typing.Optional["NrqlAlertConditionWarning"]:
        return typing.cast(typing.Optional["NrqlAlertConditionWarning"], jsii.get(self, "warningInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: jsii.Number) -> None:
        jsii.set(self, "accountId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="aggregationDelay")
    def aggregation_delay(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "aggregationDelay"))

    @aggregation_delay.setter
    def aggregation_delay(self, value: jsii.Number) -> None:
        jsii.set(self, "aggregationDelay", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="aggregationMethod")
    def aggregation_method(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "aggregationMethod"))

    @aggregation_method.setter
    def aggregation_method(self, value: builtins.str) -> None:
        jsii.set(self, "aggregationMethod", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="aggregationTimer")
    def aggregation_timer(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "aggregationTimer"))

    @aggregation_timer.setter
    def aggregation_timer(self, value: jsii.Number) -> None:
        jsii.set(self, "aggregationTimer", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="aggregationWindow")
    def aggregation_window(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "aggregationWindow"))

    @aggregation_window.setter
    def aggregation_window(self, value: jsii.Number) -> None:
        jsii.set(self, "aggregationWindow", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="baselineDirection")
    def baseline_direction(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "baselineDirection"))

    @baseline_direction.setter
    def baseline_direction(self, value: builtins.str) -> None:
        jsii.set(self, "baselineDirection", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="closeViolationsOnExpiration")
    def close_violations_on_expiration(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "closeViolationsOnExpiration"))

    @close_violations_on_expiration.setter
    def close_violations_on_expiration(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "closeViolationsOnExpiration", value)

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
    @jsii.member(jsii_name="expectedGroups")
    def expected_groups(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "expectedGroups"))

    @expected_groups.setter
    def expected_groups(self, value: jsii.Number) -> None:
        jsii.set(self, "expectedGroups", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="expirationDuration")
    def expiration_duration(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "expirationDuration"))

    @expiration_duration.setter
    def expiration_duration(self, value: jsii.Number) -> None:
        jsii.set(self, "expirationDuration", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fillOption")
    def fill_option(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fillOption"))

    @fill_option.setter
    def fill_option(self, value: builtins.str) -> None:
        jsii.set(self, "fillOption", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fillValue")
    def fill_value(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "fillValue"))

    @fill_value.setter
    def fill_value(self, value: jsii.Number) -> None:
        jsii.set(self, "fillValue", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ignoreOverlap")
    def ignore_overlap(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "ignoreOverlap"))

    @ignore_overlap.setter
    def ignore_overlap(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "ignoreOverlap", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="openViolationOnExpiration")
    def open_violation_on_expiration(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "openViolationOnExpiration"))

    @open_violation_on_expiration.setter
    def open_violation_on_expiration(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "openViolationOnExpiration", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="openViolationOnGroupOverlap")
    def open_violation_on_group_overlap(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "openViolationOnGroupOverlap"))

    @open_violation_on_group_overlap.setter
    def open_violation_on_group_overlap(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "openViolationOnGroupOverlap", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyId")
    def policy_id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "policyId"))

    @policy_id.setter
    def policy_id(self, value: jsii.Number) -> None:
        jsii.set(self, "policyId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="runbookUrl")
    def runbook_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "runbookUrl"))

    @runbook_url.setter
    def runbook_url(self, value: builtins.str) -> None:
        jsii.set(self, "runbookUrl", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="term")
    def term(self) -> typing.List["NrqlAlertConditionTerm"]:
        return typing.cast(typing.List["NrqlAlertConditionTerm"], jsii.get(self, "term"))

    @term.setter
    def term(self, value: typing.List["NrqlAlertConditionTerm"]) -> None:
        jsii.set(self, "term", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        jsii.set(self, "type", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="valueFunction")
    def value_function(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "valueFunction"))

    @value_function.setter
    def value_function(self, value: builtins.str) -> None:
        jsii.set(self, "valueFunction", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="violationTimeLimit")
    def violation_time_limit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "violationTimeLimit"))

    @violation_time_limit.setter
    def violation_time_limit(self, value: builtins.str) -> None:
        jsii.set(self, "violationTimeLimit", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="violationTimeLimitSeconds")
    def violation_time_limit_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "violationTimeLimitSeconds"))

    @violation_time_limit_seconds.setter
    def violation_time_limit_seconds(self, value: jsii.Number) -> None:
        jsii.set(self, "violationTimeLimitSeconds", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.NrqlAlertConditionConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "nrql": "nrql",
        "policy_id": "policyId",
        "account_id": "accountId",
        "aggregation_delay": "aggregationDelay",
        "aggregation_method": "aggregationMethod",
        "aggregation_timer": "aggregationTimer",
        "aggregation_window": "aggregationWindow",
        "baseline_direction": "baselineDirection",
        "close_violations_on_expiration": "closeViolationsOnExpiration",
        "critical": "critical",
        "description": "description",
        "enabled": "enabled",
        "expected_groups": "expectedGroups",
        "expiration_duration": "expirationDuration",
        "fill_option": "fillOption",
        "fill_value": "fillValue",
        "ignore_overlap": "ignoreOverlap",
        "open_violation_on_expiration": "openViolationOnExpiration",
        "open_violation_on_group_overlap": "openViolationOnGroupOverlap",
        "runbook_url": "runbookUrl",
        "term": "term",
        "type": "type",
        "value_function": "valueFunction",
        "violation_time_limit": "violationTimeLimit",
        "violation_time_limit_seconds": "violationTimeLimitSeconds",
        "warning": "warning",
    },
)
class NrqlAlertConditionConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        nrql: "NrqlAlertConditionNrql",
        policy_id: jsii.Number,
        account_id: typing.Optional[jsii.Number] = None,
        aggregation_delay: typing.Optional[jsii.Number] = None,
        aggregation_method: typing.Optional[builtins.str] = None,
        aggregation_timer: typing.Optional[jsii.Number] = None,
        aggregation_window: typing.Optional[jsii.Number] = None,
        baseline_direction: typing.Optional[builtins.str] = None,
        close_violations_on_expiration: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        critical: typing.Optional["NrqlAlertConditionCritical"] = None,
        description: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        expected_groups: typing.Optional[jsii.Number] = None,
        expiration_duration: typing.Optional[jsii.Number] = None,
        fill_option: typing.Optional[builtins.str] = None,
        fill_value: typing.Optional[jsii.Number] = None,
        ignore_overlap: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        open_violation_on_expiration: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        open_violation_on_group_overlap: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        runbook_url: typing.Optional[builtins.str] = None,
        term: typing.Optional[typing.Sequence["NrqlAlertConditionTerm"]] = None,
        type: typing.Optional[builtins.str] = None,
        value_function: typing.Optional[builtins.str] = None,
        violation_time_limit: typing.Optional[builtins.str] = None,
        violation_time_limit_seconds: typing.Optional[jsii.Number] = None,
        warning: typing.Optional["NrqlAlertConditionWarning"] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: The title of the condition. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#name NrqlAlertCondition#name}
        :param nrql: nrql block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#nrql NrqlAlertCondition#nrql}
        :param policy_id: The ID of the policy where this condition should be used. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#policy_id NrqlAlertCondition#policy_id}
        :param account_id: The New Relic account ID for managing your NRQL alert conditions. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#account_id NrqlAlertCondition#account_id}
        :param aggregation_delay: How long we wait for data that belongs in each aggregation window. Depending on your data, a longer delay may increase accuracy but delay notifications. Use aggregationDelay with the EVENT_FLOW and CADENCE aggregation methods. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#aggregation_delay NrqlAlertCondition#aggregation_delay}
        :param aggregation_method: The method that determines when we consider an aggregation window to be complete so that we can evaluate the signal for violations. Default is CADENCE. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#aggregation_method NrqlAlertCondition#aggregation_method}
        :param aggregation_timer: How long we wait after each data point arrives to make sure we've processed the whole batch. Use aggregationTimer with the EVENT_TIMER aggregation method. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#aggregation_timer NrqlAlertCondition#aggregation_timer}
        :param aggregation_window: The duration of the time window used to evaluate the NRQL query, in seconds. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#aggregation_window NrqlAlertCondition#aggregation_window}
        :param baseline_direction: The baseline direction of a baseline NRQL alert condition. Valid values are: 'LOWER_ONLY', 'UPPER_AND_LOWER', 'UPPER_ONLY' (case insensitive). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#baseline_direction NrqlAlertCondition#baseline_direction}
        :param close_violations_on_expiration: Whether to close all open violations when the signal expires. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#close_violations_on_expiration NrqlAlertCondition#close_violations_on_expiration}
        :param critical: critical block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#critical NrqlAlertCondition#critical}
        :param description: The description of the NRQL alert condition. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#description NrqlAlertCondition#description}
        :param enabled: Whether or not to enable the alert condition. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#enabled NrqlAlertCondition#enabled}
        :param expected_groups: Number of expected groups when using outlier detection. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#expected_groups NrqlAlertCondition#expected_groups}
        :param expiration_duration: The amount of time (in seconds) to wait before considering the signal expired. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#expiration_duration NrqlAlertCondition#expiration_duration}
        :param fill_option: Which strategy to use when filling gaps in the signal. If static, the 'fill value' will be used for filling gaps in the signal. Valid values are: 'NONE', 'LAST_VALUE', or 'STATIC' (case insensitive). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#fill_option NrqlAlertCondition#fill_option}
        :param fill_value: If using the 'static' fill option, this value will be used for filling gaps in the signal. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#fill_value NrqlAlertCondition#fill_value}
        :param ignore_overlap: Whether to look for a convergence of groups when using outlier detection. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#ignore_overlap NrqlAlertCondition#ignore_overlap}
        :param open_violation_on_expiration: Whether to create a new violation to capture that the signal expired. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#open_violation_on_expiration NrqlAlertCondition#open_violation_on_expiration}
        :param open_violation_on_group_overlap: Whether overlapping groups should produce a violation. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#open_violation_on_group_overlap NrqlAlertCondition#open_violation_on_group_overlap}
        :param runbook_url: Runbook URL to display in notifications. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#runbook_url NrqlAlertCondition#runbook_url}
        :param term: term block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#term NrqlAlertCondition#term}
        :param type: The type of NRQL alert condition to create. Valid values are: 'static', 'baseline', 'outlier' (deprecated). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#type NrqlAlertCondition#type}
        :param value_function: Valid values are: 'single_value' or 'sum'. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#value_function NrqlAlertCondition#value_function}
        :param violation_time_limit: Sets a time limit, in hours, that will automatically force-close a long-lasting violation after the time limit you select. Possible values are 'ONE_HOUR', 'TWO_HOURS', 'FOUR_HOURS', 'EIGHT_HOURS', 'TWELVE_HOURS', 'TWENTY_FOUR_HOURS', 'THIRTY_DAYS' (case insensitive). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#violation_time_limit NrqlAlertCondition#violation_time_limit}
        :param violation_time_limit_seconds: Sets a time limit, in seconds, that will automatically force-close a long-lasting violation after the time limit you select. Must be in the range of 300 to 2592000 (inclusive) Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#violation_time_limit_seconds NrqlAlertCondition#violation_time_limit_seconds}
        :param warning: warning block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#warning NrqlAlertCondition#warning}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(nrql, dict):
            nrql = NrqlAlertConditionNrql(**nrql)
        if isinstance(critical, dict):
            critical = NrqlAlertConditionCritical(**critical)
        if isinstance(warning, dict):
            warning = NrqlAlertConditionWarning(**warning)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "nrql": nrql,
            "policy_id": policy_id,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if account_id is not None:
            self._values["account_id"] = account_id
        if aggregation_delay is not None:
            self._values["aggregation_delay"] = aggregation_delay
        if aggregation_method is not None:
            self._values["aggregation_method"] = aggregation_method
        if aggregation_timer is not None:
            self._values["aggregation_timer"] = aggregation_timer
        if aggregation_window is not None:
            self._values["aggregation_window"] = aggregation_window
        if baseline_direction is not None:
            self._values["baseline_direction"] = baseline_direction
        if close_violations_on_expiration is not None:
            self._values["close_violations_on_expiration"] = close_violations_on_expiration
        if critical is not None:
            self._values["critical"] = critical
        if description is not None:
            self._values["description"] = description
        if enabled is not None:
            self._values["enabled"] = enabled
        if expected_groups is not None:
            self._values["expected_groups"] = expected_groups
        if expiration_duration is not None:
            self._values["expiration_duration"] = expiration_duration
        if fill_option is not None:
            self._values["fill_option"] = fill_option
        if fill_value is not None:
            self._values["fill_value"] = fill_value
        if ignore_overlap is not None:
            self._values["ignore_overlap"] = ignore_overlap
        if open_violation_on_expiration is not None:
            self._values["open_violation_on_expiration"] = open_violation_on_expiration
        if open_violation_on_group_overlap is not None:
            self._values["open_violation_on_group_overlap"] = open_violation_on_group_overlap
        if runbook_url is not None:
            self._values["runbook_url"] = runbook_url
        if term is not None:
            self._values["term"] = term
        if type is not None:
            self._values["type"] = type
        if value_function is not None:
            self._values["value_function"] = value_function
        if violation_time_limit is not None:
            self._values["violation_time_limit"] = violation_time_limit
        if violation_time_limit_seconds is not None:
            self._values["violation_time_limit_seconds"] = violation_time_limit_seconds
        if warning is not None:
            self._values["warning"] = warning

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
        '''The title of the condition.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#name NrqlAlertCondition#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def nrql(self) -> "NrqlAlertConditionNrql":
        '''nrql block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#nrql NrqlAlertCondition#nrql}
        '''
        result = self._values.get("nrql")
        assert result is not None, "Required property 'nrql' is missing"
        return typing.cast("NrqlAlertConditionNrql", result)

    @builtins.property
    def policy_id(self) -> jsii.Number:
        '''The ID of the policy where this condition should be used.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#policy_id NrqlAlertCondition#policy_id}
        '''
        result = self._values.get("policy_id")
        assert result is not None, "Required property 'policy_id' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def account_id(self) -> typing.Optional[jsii.Number]:
        '''The New Relic account ID for managing your NRQL alert conditions.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#account_id NrqlAlertCondition#account_id}
        '''
        result = self._values.get("account_id")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def aggregation_delay(self) -> typing.Optional[jsii.Number]:
        '''How long we wait for data that belongs in each aggregation window.

        Depending on your data, a longer delay may increase accuracy but delay notifications. Use aggregationDelay with the EVENT_FLOW and CADENCE aggregation methods.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#aggregation_delay NrqlAlertCondition#aggregation_delay}
        '''
        result = self._values.get("aggregation_delay")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def aggregation_method(self) -> typing.Optional[builtins.str]:
        '''The method that determines when we consider an aggregation window to be complete so that we can evaluate the signal for violations.

        Default is CADENCE.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#aggregation_method NrqlAlertCondition#aggregation_method}
        '''
        result = self._values.get("aggregation_method")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def aggregation_timer(self) -> typing.Optional[jsii.Number]:
        '''How long we wait after each data point arrives to make sure we've processed the whole batch.

        Use aggregationTimer with the EVENT_TIMER aggregation method.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#aggregation_timer NrqlAlertCondition#aggregation_timer}
        '''
        result = self._values.get("aggregation_timer")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def aggregation_window(self) -> typing.Optional[jsii.Number]:
        '''The duration of the time window used to evaluate the NRQL query, in seconds.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#aggregation_window NrqlAlertCondition#aggregation_window}
        '''
        result = self._values.get("aggregation_window")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def baseline_direction(self) -> typing.Optional[builtins.str]:
        '''The baseline direction of a baseline NRQL alert condition. Valid values are: 'LOWER_ONLY', 'UPPER_AND_LOWER', 'UPPER_ONLY' (case insensitive).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#baseline_direction NrqlAlertCondition#baseline_direction}
        '''
        result = self._values.get("baseline_direction")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def close_violations_on_expiration(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Whether to close all open violations when the signal expires.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#close_violations_on_expiration NrqlAlertCondition#close_violations_on_expiration}
        '''
        result = self._values.get("close_violations_on_expiration")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def critical(self) -> typing.Optional["NrqlAlertConditionCritical"]:
        '''critical block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#critical NrqlAlertCondition#critical}
        '''
        result = self._values.get("critical")
        return typing.cast(typing.Optional["NrqlAlertConditionCritical"], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''The description of the NRQL alert condition.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#description NrqlAlertCondition#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Whether or not to enable the alert condition.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#enabled NrqlAlertCondition#enabled}
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def expected_groups(self) -> typing.Optional[jsii.Number]:
        '''Number of expected groups when using outlier detection.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#expected_groups NrqlAlertCondition#expected_groups}
        '''
        result = self._values.get("expected_groups")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def expiration_duration(self) -> typing.Optional[jsii.Number]:
        '''The amount of time (in seconds) to wait before considering the signal expired.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#expiration_duration NrqlAlertCondition#expiration_duration}
        '''
        result = self._values.get("expiration_duration")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def fill_option(self) -> typing.Optional[builtins.str]:
        '''Which strategy to use when filling gaps in the signal.

        If static, the 'fill value' will be used for filling gaps in the signal. Valid values are: 'NONE', 'LAST_VALUE', or 'STATIC' (case insensitive).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#fill_option NrqlAlertCondition#fill_option}
        '''
        result = self._values.get("fill_option")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def fill_value(self) -> typing.Optional[jsii.Number]:
        '''If using the 'static' fill option, this value will be used for filling gaps in the signal.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#fill_value NrqlAlertCondition#fill_value}
        '''
        result = self._values.get("fill_value")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ignore_overlap(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Whether to look for a convergence of groups when using outlier detection.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#ignore_overlap NrqlAlertCondition#ignore_overlap}
        '''
        result = self._values.get("ignore_overlap")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def open_violation_on_expiration(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Whether to create a new violation to capture that the signal expired.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#open_violation_on_expiration NrqlAlertCondition#open_violation_on_expiration}
        '''
        result = self._values.get("open_violation_on_expiration")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def open_violation_on_group_overlap(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Whether overlapping groups should produce a violation.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#open_violation_on_group_overlap NrqlAlertCondition#open_violation_on_group_overlap}
        '''
        result = self._values.get("open_violation_on_group_overlap")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def runbook_url(self) -> typing.Optional[builtins.str]:
        '''Runbook URL to display in notifications.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#runbook_url NrqlAlertCondition#runbook_url}
        '''
        result = self._values.get("runbook_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def term(self) -> typing.Optional[typing.List["NrqlAlertConditionTerm"]]:
        '''term block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#term NrqlAlertCondition#term}
        '''
        result = self._values.get("term")
        return typing.cast(typing.Optional[typing.List["NrqlAlertConditionTerm"]], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''The type of NRQL alert condition to create. Valid values are: 'static', 'baseline', 'outlier' (deprecated).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#type NrqlAlertCondition#type}
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def value_function(self) -> typing.Optional[builtins.str]:
        '''Valid values are: 'single_value' or 'sum'.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#value_function NrqlAlertCondition#value_function}
        '''
        result = self._values.get("value_function")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def violation_time_limit(self) -> typing.Optional[builtins.str]:
        '''Sets a time limit, in hours, that will automatically force-close a long-lasting violation after the time limit you select.

        Possible values are 'ONE_HOUR', 'TWO_HOURS', 'FOUR_HOURS', 'EIGHT_HOURS', 'TWELVE_HOURS', 'TWENTY_FOUR_HOURS', 'THIRTY_DAYS' (case insensitive).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#violation_time_limit NrqlAlertCondition#violation_time_limit}
        '''
        result = self._values.get("violation_time_limit")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def violation_time_limit_seconds(self) -> typing.Optional[jsii.Number]:
        '''Sets a time limit, in seconds, that will automatically force-close a long-lasting violation after the time limit you select.

        Must be in the range of 300 to 2592000 (inclusive)

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#violation_time_limit_seconds NrqlAlertCondition#violation_time_limit_seconds}
        '''
        result = self._values.get("violation_time_limit_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def warning(self) -> typing.Optional["NrqlAlertConditionWarning"]:
        '''warning block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#warning NrqlAlertCondition#warning}
        '''
        result = self._values.get("warning")
        return typing.cast(typing.Optional["NrqlAlertConditionWarning"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NrqlAlertConditionConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.NrqlAlertConditionCritical",
    jsii_struct_bases=[],
    name_mapping={
        "threshold": "threshold",
        "duration": "duration",
        "operator": "operator",
        "threshold_duration": "thresholdDuration",
        "threshold_occurrences": "thresholdOccurrences",
        "time_function": "timeFunction",
    },
)
class NrqlAlertConditionCritical:
    def __init__(
        self,
        *,
        threshold: jsii.Number,
        duration: typing.Optional[jsii.Number] = None,
        operator: typing.Optional[builtins.str] = None,
        threshold_duration: typing.Optional[jsii.Number] = None,
        threshold_occurrences: typing.Optional[builtins.str] = None,
        time_function: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param threshold: Must be 0 or greater. For baseline conditions must be in range [1, 1000]. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#threshold NrqlAlertCondition#threshold}
        :param duration: In minutes, must be in the range of 1 to 120 (inclusive). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#duration NrqlAlertCondition#duration}
        :param operator: One of (above, below, equals). Defaults to 'equals'. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#operator NrqlAlertCondition#operator}
        :param threshold_duration: The duration, in seconds, that the threshold must violate in order to create a violation. Value must be a multiple of the 'aggregation_window' (which has a default of 60 seconds). Value must be within 120-3600 seconds for baseline and outlier conditions, within 120-7200 seconds for static conditions with the sum value function, and within 60-7200 seconds for static conditions with the single_value value function. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#threshold_duration NrqlAlertCondition#threshold_duration}
        :param threshold_occurrences: The criteria for how many data points must be in violation for the specified threshold duration. Valid values are: 'ALL' or 'AT_LEAST_ONCE' (case insensitive). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#threshold_occurrences NrqlAlertCondition#threshold_occurrences}
        :param time_function: Valid values are: 'all' or 'any'. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#time_function NrqlAlertCondition#time_function}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "threshold": threshold,
        }
        if duration is not None:
            self._values["duration"] = duration
        if operator is not None:
            self._values["operator"] = operator
        if threshold_duration is not None:
            self._values["threshold_duration"] = threshold_duration
        if threshold_occurrences is not None:
            self._values["threshold_occurrences"] = threshold_occurrences
        if time_function is not None:
            self._values["time_function"] = time_function

    @builtins.property
    def threshold(self) -> jsii.Number:
        '''Must be 0 or greater. For baseline conditions must be in range [1, 1000].

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#threshold NrqlAlertCondition#threshold}
        '''
        result = self._values.get("threshold")
        assert result is not None, "Required property 'threshold' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def duration(self) -> typing.Optional[jsii.Number]:
        '''In minutes, must be in the range of 1 to 120 (inclusive).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#duration NrqlAlertCondition#duration}
        '''
        result = self._values.get("duration")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def operator(self) -> typing.Optional[builtins.str]:
        '''One of (above, below, equals). Defaults to 'equals'.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#operator NrqlAlertCondition#operator}
        '''
        result = self._values.get("operator")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def threshold_duration(self) -> typing.Optional[jsii.Number]:
        '''The duration, in seconds, that the threshold must violate in order to create a violation.

        Value must be a multiple of the 'aggregation_window' (which has a default of 60 seconds). Value must be within 120-3600 seconds for baseline and outlier conditions, within 120-7200 seconds for static conditions with the sum value function, and within 60-7200 seconds for static conditions with the single_value value function.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#threshold_duration NrqlAlertCondition#threshold_duration}
        '''
        result = self._values.get("threshold_duration")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def threshold_occurrences(self) -> typing.Optional[builtins.str]:
        '''The criteria for how many data points must be in violation for the specified threshold duration.

        Valid values are: 'ALL' or 'AT_LEAST_ONCE' (case insensitive).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#threshold_occurrences NrqlAlertCondition#threshold_occurrences}
        '''
        result = self._values.get("threshold_occurrences")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def time_function(self) -> typing.Optional[builtins.str]:
        '''Valid values are: 'all' or 'any'.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#time_function NrqlAlertCondition#time_function}
        '''
        result = self._values.get("time_function")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NrqlAlertConditionCritical(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NrqlAlertConditionCriticalOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-newrelic.NrqlAlertConditionCriticalOutputReference",
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

    @jsii.member(jsii_name="resetDuration")
    def reset_duration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDuration", []))

    @jsii.member(jsii_name="resetOperator")
    def reset_operator(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOperator", []))

    @jsii.member(jsii_name="resetThresholdDuration")
    def reset_threshold_duration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetThresholdDuration", []))

    @jsii.member(jsii_name="resetThresholdOccurrences")
    def reset_threshold_occurrences(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetThresholdOccurrences", []))

    @jsii.member(jsii_name="resetTimeFunction")
    def reset_time_function(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeFunction", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="durationInput")
    def duration_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "durationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="operatorInput")
    def operator_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "operatorInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="thresholdDurationInput")
    def threshold_duration_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "thresholdDurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="thresholdInput")
    def threshold_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "thresholdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="thresholdOccurrencesInput")
    def threshold_occurrences_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "thresholdOccurrencesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeFunctionInput")
    def time_function_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "timeFunctionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="duration")
    def duration(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "duration"))

    @duration.setter
    def duration(self, value: jsii.Number) -> None:
        jsii.set(self, "duration", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="operator")
    def operator(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "operator"))

    @operator.setter
    def operator(self, value: builtins.str) -> None:
        jsii.set(self, "operator", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="threshold")
    def threshold(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "threshold"))

    @threshold.setter
    def threshold(self, value: jsii.Number) -> None:
        jsii.set(self, "threshold", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="thresholdDuration")
    def threshold_duration(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "thresholdDuration"))

    @threshold_duration.setter
    def threshold_duration(self, value: jsii.Number) -> None:
        jsii.set(self, "thresholdDuration", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="thresholdOccurrences")
    def threshold_occurrences(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "thresholdOccurrences"))

    @threshold_occurrences.setter
    def threshold_occurrences(self, value: builtins.str) -> None:
        jsii.set(self, "thresholdOccurrences", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeFunction")
    def time_function(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "timeFunction"))

    @time_function.setter
    def time_function(self, value: builtins.str) -> None:
        jsii.set(self, "timeFunction", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[NrqlAlertConditionCritical]:
        return typing.cast(typing.Optional[NrqlAlertConditionCritical], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[NrqlAlertConditionCritical],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.NrqlAlertConditionNrql",
    jsii_struct_bases=[],
    name_mapping={
        "query": "query",
        "evaluation_offset": "evaluationOffset",
        "since_value": "sinceValue",
    },
)
class NrqlAlertConditionNrql:
    def __init__(
        self,
        *,
        query: builtins.str,
        evaluation_offset: typing.Optional[jsii.Number] = None,
        since_value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param query: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#query NrqlAlertCondition#query}.
        :param evaluation_offset: NRQL queries are evaluated in one-minute time windows. The start time depends on the value you provide in the NRQL condition's ``evaluation_offset``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#evaluation_offset NrqlAlertCondition#evaluation_offset}
        :param since_value: NRQL queries are evaluated in one-minute time windows. The start time depends on the value you provide in the NRQL condition's ``since_value``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#since_value NrqlAlertCondition#since_value}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "query": query,
        }
        if evaluation_offset is not None:
            self._values["evaluation_offset"] = evaluation_offset
        if since_value is not None:
            self._values["since_value"] = since_value

    @builtins.property
    def query(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#query NrqlAlertCondition#query}.'''
        result = self._values.get("query")
        assert result is not None, "Required property 'query' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def evaluation_offset(self) -> typing.Optional[jsii.Number]:
        '''NRQL queries are evaluated in one-minute time windows.

        The start time depends on the value you provide in the NRQL condition's ``evaluation_offset``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#evaluation_offset NrqlAlertCondition#evaluation_offset}
        '''
        result = self._values.get("evaluation_offset")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def since_value(self) -> typing.Optional[builtins.str]:
        '''NRQL queries are evaluated in one-minute time windows.

        The start time depends on the value you provide in the NRQL condition's ``since_value``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#since_value NrqlAlertCondition#since_value}
        '''
        result = self._values.get("since_value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NrqlAlertConditionNrql(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NrqlAlertConditionNrqlOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-newrelic.NrqlAlertConditionNrqlOutputReference",
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

    @jsii.member(jsii_name="resetEvaluationOffset")
    def reset_evaluation_offset(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEvaluationOffset", []))

    @jsii.member(jsii_name="resetSinceValue")
    def reset_since_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSinceValue", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="evaluationOffsetInput")
    def evaluation_offset_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "evaluationOffsetInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="queryInput")
    def query_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "queryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sinceValueInput")
    def since_value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sinceValueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="evaluationOffset")
    def evaluation_offset(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "evaluationOffset"))

    @evaluation_offset.setter
    def evaluation_offset(self, value: jsii.Number) -> None:
        jsii.set(self, "evaluationOffset", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="query")
    def query(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "query"))

    @query.setter
    def query(self, value: builtins.str) -> None:
        jsii.set(self, "query", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sinceValue")
    def since_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sinceValue"))

    @since_value.setter
    def since_value(self, value: builtins.str) -> None:
        jsii.set(self, "sinceValue", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[NrqlAlertConditionNrql]:
        return typing.cast(typing.Optional[NrqlAlertConditionNrql], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[NrqlAlertConditionNrql]) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.NrqlAlertConditionTerm",
    jsii_struct_bases=[],
    name_mapping={
        "threshold": "threshold",
        "duration": "duration",
        "operator": "operator",
        "priority": "priority",
        "threshold_duration": "thresholdDuration",
        "threshold_occurrences": "thresholdOccurrences",
        "time_function": "timeFunction",
    },
)
class NrqlAlertConditionTerm:
    def __init__(
        self,
        *,
        threshold: jsii.Number,
        duration: typing.Optional[jsii.Number] = None,
        operator: typing.Optional[builtins.str] = None,
        priority: typing.Optional[builtins.str] = None,
        threshold_duration: typing.Optional[jsii.Number] = None,
        threshold_occurrences: typing.Optional[builtins.str] = None,
        time_function: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param threshold: Must be 0 or greater. For baseline conditions must be in range [1, 1000]. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#threshold NrqlAlertCondition#threshold}
        :param duration: In minutes, must be in the range of 1 to 120 (inclusive). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#duration NrqlAlertCondition#duration}
        :param operator: One of (above, below, equals). Defaults to 'equals'. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#operator NrqlAlertCondition#operator}
        :param priority: One of (critical, warning). Defaults to 'critical'. At least one condition term must have priority set to 'critical'. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#priority NrqlAlertCondition#priority}
        :param threshold_duration: The duration, in seconds, that the threshold must violate in order to create a violation. Value must be a multiple of the 'aggregation_window' (which has a default of 60 seconds). Value must be within 120-3600 seconds for baseline and outlier conditions, within 120-7200 seconds for static conditions with the sum value function, and within 60-7200 seconds for static conditions with the single_value value function. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#threshold_duration NrqlAlertCondition#threshold_duration}
        :param threshold_occurrences: The criteria for how many data points must be in violation for the specified threshold duration. Valid values are: 'ALL' or 'AT_LEAST_ONCE' (case insensitive). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#threshold_occurrences NrqlAlertCondition#threshold_occurrences}
        :param time_function: Valid values are: 'all' or 'any'. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#time_function NrqlAlertCondition#time_function}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "threshold": threshold,
        }
        if duration is not None:
            self._values["duration"] = duration
        if operator is not None:
            self._values["operator"] = operator
        if priority is not None:
            self._values["priority"] = priority
        if threshold_duration is not None:
            self._values["threshold_duration"] = threshold_duration
        if threshold_occurrences is not None:
            self._values["threshold_occurrences"] = threshold_occurrences
        if time_function is not None:
            self._values["time_function"] = time_function

    @builtins.property
    def threshold(self) -> jsii.Number:
        '''Must be 0 or greater. For baseline conditions must be in range [1, 1000].

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#threshold NrqlAlertCondition#threshold}
        '''
        result = self._values.get("threshold")
        assert result is not None, "Required property 'threshold' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def duration(self) -> typing.Optional[jsii.Number]:
        '''In minutes, must be in the range of 1 to 120 (inclusive).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#duration NrqlAlertCondition#duration}
        '''
        result = self._values.get("duration")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def operator(self) -> typing.Optional[builtins.str]:
        '''One of (above, below, equals). Defaults to 'equals'.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#operator NrqlAlertCondition#operator}
        '''
        result = self._values.get("operator")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def priority(self) -> typing.Optional[builtins.str]:
        '''One of (critical, warning). Defaults to 'critical'. At least one condition term must have priority set to 'critical'.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#priority NrqlAlertCondition#priority}
        '''
        result = self._values.get("priority")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def threshold_duration(self) -> typing.Optional[jsii.Number]:
        '''The duration, in seconds, that the threshold must violate in order to create a violation.

        Value must be a multiple of the 'aggregation_window' (which has a default of 60 seconds). Value must be within 120-3600 seconds for baseline and outlier conditions, within 120-7200 seconds for static conditions with the sum value function, and within 60-7200 seconds for static conditions with the single_value value function.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#threshold_duration NrqlAlertCondition#threshold_duration}
        '''
        result = self._values.get("threshold_duration")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def threshold_occurrences(self) -> typing.Optional[builtins.str]:
        '''The criteria for how many data points must be in violation for the specified threshold duration.

        Valid values are: 'ALL' or 'AT_LEAST_ONCE' (case insensitive).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#threshold_occurrences NrqlAlertCondition#threshold_occurrences}
        '''
        result = self._values.get("threshold_occurrences")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def time_function(self) -> typing.Optional[builtins.str]:
        '''Valid values are: 'all' or 'any'.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#time_function NrqlAlertCondition#time_function}
        '''
        result = self._values.get("time_function")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NrqlAlertConditionTerm(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.NrqlAlertConditionWarning",
    jsii_struct_bases=[],
    name_mapping={
        "threshold": "threshold",
        "duration": "duration",
        "operator": "operator",
        "threshold_duration": "thresholdDuration",
        "threshold_occurrences": "thresholdOccurrences",
        "time_function": "timeFunction",
    },
)
class NrqlAlertConditionWarning:
    def __init__(
        self,
        *,
        threshold: jsii.Number,
        duration: typing.Optional[jsii.Number] = None,
        operator: typing.Optional[builtins.str] = None,
        threshold_duration: typing.Optional[jsii.Number] = None,
        threshold_occurrences: typing.Optional[builtins.str] = None,
        time_function: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param threshold: Must be 0 or greater. For baseline conditions must be in range [1, 1000]. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#threshold NrqlAlertCondition#threshold}
        :param duration: In minutes, must be in the range of 1 to 120 (inclusive). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#duration NrqlAlertCondition#duration}
        :param operator: One of (above, below, equals). Defaults to 'equals'. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#operator NrqlAlertCondition#operator}
        :param threshold_duration: The duration, in seconds, that the threshold must violate in order to create a violation. Value must be a multiple of the 'aggregation_window' (which has a default of 60 seconds). Value must be within 120-3600 seconds for baseline and outlier conditions, within 120-7200 seconds for static conditions with the sum value function, and within 60-7200 seconds for static conditions with the single_value value function. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#threshold_duration NrqlAlertCondition#threshold_duration}
        :param threshold_occurrences: The criteria for how many data points must be in violation for the specified threshold duration. Valid values are: 'ALL' or 'AT_LEAST_ONCE' (case insensitive). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#threshold_occurrences NrqlAlertCondition#threshold_occurrences}
        :param time_function: Valid values are: 'all' or 'any'. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#time_function NrqlAlertCondition#time_function}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "threshold": threshold,
        }
        if duration is not None:
            self._values["duration"] = duration
        if operator is not None:
            self._values["operator"] = operator
        if threshold_duration is not None:
            self._values["threshold_duration"] = threshold_duration
        if threshold_occurrences is not None:
            self._values["threshold_occurrences"] = threshold_occurrences
        if time_function is not None:
            self._values["time_function"] = time_function

    @builtins.property
    def threshold(self) -> jsii.Number:
        '''Must be 0 or greater. For baseline conditions must be in range [1, 1000].

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#threshold NrqlAlertCondition#threshold}
        '''
        result = self._values.get("threshold")
        assert result is not None, "Required property 'threshold' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def duration(self) -> typing.Optional[jsii.Number]:
        '''In minutes, must be in the range of 1 to 120 (inclusive).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#duration NrqlAlertCondition#duration}
        '''
        result = self._values.get("duration")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def operator(self) -> typing.Optional[builtins.str]:
        '''One of (above, below, equals). Defaults to 'equals'.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#operator NrqlAlertCondition#operator}
        '''
        result = self._values.get("operator")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def threshold_duration(self) -> typing.Optional[jsii.Number]:
        '''The duration, in seconds, that the threshold must violate in order to create a violation.

        Value must be a multiple of the 'aggregation_window' (which has a default of 60 seconds). Value must be within 120-3600 seconds for baseline and outlier conditions, within 120-7200 seconds for static conditions with the sum value function, and within 60-7200 seconds for static conditions with the single_value value function.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#threshold_duration NrqlAlertCondition#threshold_duration}
        '''
        result = self._values.get("threshold_duration")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def threshold_occurrences(self) -> typing.Optional[builtins.str]:
        '''The criteria for how many data points must be in violation for the specified threshold duration.

        Valid values are: 'ALL' or 'AT_LEAST_ONCE' (case insensitive).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#threshold_occurrences NrqlAlertCondition#threshold_occurrences}
        '''
        result = self._values.get("threshold_occurrences")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def time_function(self) -> typing.Optional[builtins.str]:
        '''Valid values are: 'all' or 'any'.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_alert_condition#time_function NrqlAlertCondition#time_function}
        '''
        result = self._values.get("time_function")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NrqlAlertConditionWarning(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NrqlAlertConditionWarningOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-newrelic.NrqlAlertConditionWarningOutputReference",
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

    @jsii.member(jsii_name="resetDuration")
    def reset_duration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDuration", []))

    @jsii.member(jsii_name="resetOperator")
    def reset_operator(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOperator", []))

    @jsii.member(jsii_name="resetThresholdDuration")
    def reset_threshold_duration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetThresholdDuration", []))

    @jsii.member(jsii_name="resetThresholdOccurrences")
    def reset_threshold_occurrences(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetThresholdOccurrences", []))

    @jsii.member(jsii_name="resetTimeFunction")
    def reset_time_function(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeFunction", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="durationInput")
    def duration_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "durationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="operatorInput")
    def operator_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "operatorInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="thresholdDurationInput")
    def threshold_duration_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "thresholdDurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="thresholdInput")
    def threshold_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "thresholdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="thresholdOccurrencesInput")
    def threshold_occurrences_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "thresholdOccurrencesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeFunctionInput")
    def time_function_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "timeFunctionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="duration")
    def duration(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "duration"))

    @duration.setter
    def duration(self, value: jsii.Number) -> None:
        jsii.set(self, "duration", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="operator")
    def operator(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "operator"))

    @operator.setter
    def operator(self, value: builtins.str) -> None:
        jsii.set(self, "operator", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="threshold")
    def threshold(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "threshold"))

    @threshold.setter
    def threshold(self, value: jsii.Number) -> None:
        jsii.set(self, "threshold", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="thresholdDuration")
    def threshold_duration(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "thresholdDuration"))

    @threshold_duration.setter
    def threshold_duration(self, value: jsii.Number) -> None:
        jsii.set(self, "thresholdDuration", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="thresholdOccurrences")
    def threshold_occurrences(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "thresholdOccurrences"))

    @threshold_occurrences.setter
    def threshold_occurrences(self, value: builtins.str) -> None:
        jsii.set(self, "thresholdOccurrences", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeFunction")
    def time_function(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "timeFunction"))

    @time_function.setter
    def time_function(self, value: builtins.str) -> None:
        jsii.set(self, "timeFunction", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[NrqlAlertConditionWarning]:
        return typing.cast(typing.Optional[NrqlAlertConditionWarning], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[NrqlAlertConditionWarning]) -> None:
        jsii.set(self, "internalValue", value)


class NrqlDropRule(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-newrelic.NrqlDropRule",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_drop_rule newrelic_nrql_drop_rule}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        action: builtins.str,
        nrql: builtins.str,
        account_id: typing.Optional[jsii.Number] = None,
        description: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_drop_rule newrelic_nrql_drop_rule} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param action: The drop rule action (drop_data, drop_attributes, or drop_attributes_from_metric_aggregates). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_drop_rule#action NrqlDropRule#action}
        :param nrql: Explains which data to apply the drop rule to. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_drop_rule#nrql NrqlDropRule#nrql}
        :param account_id: Account with the NRQL drop rule will be put. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_drop_rule#account_id NrqlDropRule#account_id}
        :param description: Provides additional information about the rule. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_drop_rule#description NrqlDropRule#description}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = NrqlDropRuleConfig(
            action=action,
            nrql=nrql,
            account_id=account_id,
            description=description,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetAccountId")
    def reset_account_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccountId", []))

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
    @jsii.member(jsii_name="ruleId")
    def rule_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ruleId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "accountIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="actionInput")
    def action_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "actionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nrqlInput")
    def nrql_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nrqlInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: jsii.Number) -> None:
        jsii.set(self, "accountId", value)

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
    @jsii.member(jsii_name="nrql")
    def nrql(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nrql"))

    @nrql.setter
    def nrql(self, value: builtins.str) -> None:
        jsii.set(self, "nrql", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.NrqlDropRuleConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "action": "action",
        "nrql": "nrql",
        "account_id": "accountId",
        "description": "description",
    },
)
class NrqlDropRuleConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        action: builtins.str,
        nrql: builtins.str,
        account_id: typing.Optional[jsii.Number] = None,
        description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param action: The drop rule action (drop_data, drop_attributes, or drop_attributes_from_metric_aggregates). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_drop_rule#action NrqlDropRule#action}
        :param nrql: Explains which data to apply the drop rule to. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_drop_rule#nrql NrqlDropRule#nrql}
        :param account_id: Account with the NRQL drop rule will be put. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_drop_rule#account_id NrqlDropRule#account_id}
        :param description: Provides additional information about the rule. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_drop_rule#description NrqlDropRule#description}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "action": action,
            "nrql": nrql,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if account_id is not None:
            self._values["account_id"] = account_id
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
    def action(self) -> builtins.str:
        '''The drop rule action (drop_data, drop_attributes, or drop_attributes_from_metric_aggregates).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_drop_rule#action NrqlDropRule#action}
        '''
        result = self._values.get("action")
        assert result is not None, "Required property 'action' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def nrql(self) -> builtins.str:
        '''Explains which data to apply the drop rule to.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_drop_rule#nrql NrqlDropRule#nrql}
        '''
        result = self._values.get("nrql")
        assert result is not None, "Required property 'nrql' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def account_id(self) -> typing.Optional[jsii.Number]:
        '''Account with the NRQL drop rule will be put.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_drop_rule#account_id NrqlDropRule#account_id}
        '''
        result = self._values.get("account_id")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Provides additional information about the rule.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/nrql_drop_rule#description NrqlDropRule#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NrqlDropRuleConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OneDashboard(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-newrelic.OneDashboard",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard newrelic_one_dashboard}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        page: typing.Sequence["OneDashboardPage"],
        account_id: typing.Optional[jsii.Number] = None,
        description: typing.Optional[builtins.str] = None,
        permissions: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard newrelic_one_dashboard} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: The dashboard's name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#name OneDashboard#name}
        :param page: page block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#page OneDashboard#page}
        :param account_id: The New Relic account ID where you want to create the dashboard. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#account_id OneDashboard#account_id}
        :param description: The dashboard's description. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#description OneDashboard#description}
        :param permissions: Determines who can see or edit the dashboard. Valid values are private, public_read_only, public_read_write. Defaults to public_read_only. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#permissions OneDashboard#permissions}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = OneDashboardConfig(
            name=name,
            page=page,
            account_id=account_id,
            description=description,
            permissions=permissions,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetAccountId")
    def reset_account_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccountId", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetPermissions")
    def reset_permissions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPermissions", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="guid")
    def guid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "guid"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="permalink")
    def permalink(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "permalink"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "accountIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pageInput")
    def page_input(self) -> typing.Optional[typing.List["OneDashboardPage"]]:
        return typing.cast(typing.Optional[typing.List["OneDashboardPage"]], jsii.get(self, "pageInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="permissionsInput")
    def permissions_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "permissionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: jsii.Number) -> None:
        jsii.set(self, "accountId", value)

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
    @jsii.member(jsii_name="page")
    def page(self) -> typing.List["OneDashboardPage"]:
        return typing.cast(typing.List["OneDashboardPage"], jsii.get(self, "page"))

    @page.setter
    def page(self, value: typing.List["OneDashboardPage"]) -> None:
        jsii.set(self, "page", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="permissions")
    def permissions(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "permissions"))

    @permissions.setter
    def permissions(self, value: builtins.str) -> None:
        jsii.set(self, "permissions", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.OneDashboardConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "page": "page",
        "account_id": "accountId",
        "description": "description",
        "permissions": "permissions",
    },
)
class OneDashboardConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        page: typing.Sequence["OneDashboardPage"],
        account_id: typing.Optional[jsii.Number] = None,
        description: typing.Optional[builtins.str] = None,
        permissions: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: The dashboard's name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#name OneDashboard#name}
        :param page: page block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#page OneDashboard#page}
        :param account_id: The New Relic account ID where you want to create the dashboard. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#account_id OneDashboard#account_id}
        :param description: The dashboard's description. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#description OneDashboard#description}
        :param permissions: Determines who can see or edit the dashboard. Valid values are private, public_read_only, public_read_write. Defaults to public_read_only. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#permissions OneDashboard#permissions}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "page": page,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if account_id is not None:
            self._values["account_id"] = account_id
        if description is not None:
            self._values["description"] = description
        if permissions is not None:
            self._values["permissions"] = permissions

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
        '''The dashboard's name.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#name OneDashboard#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def page(self) -> typing.List["OneDashboardPage"]:
        '''page block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#page OneDashboard#page}
        '''
        result = self._values.get("page")
        assert result is not None, "Required property 'page' is missing"
        return typing.cast(typing.List["OneDashboardPage"], result)

    @builtins.property
    def account_id(self) -> typing.Optional[jsii.Number]:
        '''The New Relic account ID where you want to create the dashboard.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#account_id OneDashboard#account_id}
        '''
        result = self._values.get("account_id")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''The dashboard's description.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#description OneDashboard#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def permissions(self) -> typing.Optional[builtins.str]:
        '''Determines who can see or edit the dashboard. Valid values are private, public_read_only, public_read_write. Defaults to public_read_only.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#permissions OneDashboard#permissions}
        '''
        result = self._values.get("permissions")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OneDashboardConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.OneDashboardPage",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "description": "description",
        "widget_area": "widgetArea",
        "widget_bar": "widgetBar",
        "widget_billboard": "widgetBillboard",
        "widget_bullet": "widgetBullet",
        "widget_funnel": "widgetFunnel",
        "widget_heatmap": "widgetHeatmap",
        "widget_histogram": "widgetHistogram",
        "widget_json": "widgetJson",
        "widget_line": "widgetLine",
        "widget_markdown": "widgetMarkdown",
        "widget_pie": "widgetPie",
        "widget_stacked_bar": "widgetStackedBar",
        "widget_table": "widgetTable",
    },
)
class OneDashboardPage:
    def __init__(
        self,
        *,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        widget_area: typing.Optional[typing.Sequence["OneDashboardPageWidgetArea"]] = None,
        widget_bar: typing.Optional[typing.Sequence["OneDashboardPageWidgetBar"]] = None,
        widget_billboard: typing.Optional[typing.Sequence["OneDashboardPageWidgetBillboard"]] = None,
        widget_bullet: typing.Optional[typing.Sequence["OneDashboardPageWidgetBullet"]] = None,
        widget_funnel: typing.Optional[typing.Sequence["OneDashboardPageWidgetFunnel"]] = None,
        widget_heatmap: typing.Optional[typing.Sequence["OneDashboardPageWidgetHeatmap"]] = None,
        widget_histogram: typing.Optional[typing.Sequence["OneDashboardPageWidgetHistogram"]] = None,
        widget_json: typing.Optional[typing.Sequence["OneDashboardPageWidgetJson"]] = None,
        widget_line: typing.Optional[typing.Sequence["OneDashboardPageWidgetLine"]] = None,
        widget_markdown: typing.Optional[typing.Sequence["OneDashboardPageWidgetMarkdown"]] = None,
        widget_pie: typing.Optional[typing.Sequence["OneDashboardPageWidgetPie"]] = None,
        widget_stacked_bar: typing.Optional[typing.Sequence["OneDashboardPageWidgetStackedBar"]] = None,
        widget_table: typing.Optional[typing.Sequence["OneDashboardPageWidgetTable"]] = None,
    ) -> None:
        '''
        :param name: The dashboard page's name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#name OneDashboard#name}
        :param description: The dashboard page's description. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#description OneDashboard#description}
        :param widget_area: widget_area block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#widget_area OneDashboard#widget_area}
        :param widget_bar: widget_bar block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#widget_bar OneDashboard#widget_bar}
        :param widget_billboard: widget_billboard block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#widget_billboard OneDashboard#widget_billboard}
        :param widget_bullet: widget_bullet block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#widget_bullet OneDashboard#widget_bullet}
        :param widget_funnel: widget_funnel block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#widget_funnel OneDashboard#widget_funnel}
        :param widget_heatmap: widget_heatmap block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#widget_heatmap OneDashboard#widget_heatmap}
        :param widget_histogram: widget_histogram block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#widget_histogram OneDashboard#widget_histogram}
        :param widget_json: widget_json block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#widget_json OneDashboard#widget_json}
        :param widget_line: widget_line block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#widget_line OneDashboard#widget_line}
        :param widget_markdown: widget_markdown block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#widget_markdown OneDashboard#widget_markdown}
        :param widget_pie: widget_pie block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#widget_pie OneDashboard#widget_pie}
        :param widget_stacked_bar: widget_stacked_bar block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#widget_stacked_bar OneDashboard#widget_stacked_bar}
        :param widget_table: widget_table block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#widget_table OneDashboard#widget_table}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if description is not None:
            self._values["description"] = description
        if widget_area is not None:
            self._values["widget_area"] = widget_area
        if widget_bar is not None:
            self._values["widget_bar"] = widget_bar
        if widget_billboard is not None:
            self._values["widget_billboard"] = widget_billboard
        if widget_bullet is not None:
            self._values["widget_bullet"] = widget_bullet
        if widget_funnel is not None:
            self._values["widget_funnel"] = widget_funnel
        if widget_heatmap is not None:
            self._values["widget_heatmap"] = widget_heatmap
        if widget_histogram is not None:
            self._values["widget_histogram"] = widget_histogram
        if widget_json is not None:
            self._values["widget_json"] = widget_json
        if widget_line is not None:
            self._values["widget_line"] = widget_line
        if widget_markdown is not None:
            self._values["widget_markdown"] = widget_markdown
        if widget_pie is not None:
            self._values["widget_pie"] = widget_pie
        if widget_stacked_bar is not None:
            self._values["widget_stacked_bar"] = widget_stacked_bar
        if widget_table is not None:
            self._values["widget_table"] = widget_table

    @builtins.property
    def name(self) -> builtins.str:
        '''The dashboard page's name.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#name OneDashboard#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''The dashboard page's description.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#description OneDashboard#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def widget_area(self) -> typing.Optional[typing.List["OneDashboardPageWidgetArea"]]:
        '''widget_area block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#widget_area OneDashboard#widget_area}
        '''
        result = self._values.get("widget_area")
        return typing.cast(typing.Optional[typing.List["OneDashboardPageWidgetArea"]], result)

    @builtins.property
    def widget_bar(self) -> typing.Optional[typing.List["OneDashboardPageWidgetBar"]]:
        '''widget_bar block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#widget_bar OneDashboard#widget_bar}
        '''
        result = self._values.get("widget_bar")
        return typing.cast(typing.Optional[typing.List["OneDashboardPageWidgetBar"]], result)

    @builtins.property
    def widget_billboard(
        self,
    ) -> typing.Optional[typing.List["OneDashboardPageWidgetBillboard"]]:
        '''widget_billboard block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#widget_billboard OneDashboard#widget_billboard}
        '''
        result = self._values.get("widget_billboard")
        return typing.cast(typing.Optional[typing.List["OneDashboardPageWidgetBillboard"]], result)

    @builtins.property
    def widget_bullet(
        self,
    ) -> typing.Optional[typing.List["OneDashboardPageWidgetBullet"]]:
        '''widget_bullet block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#widget_bullet OneDashboard#widget_bullet}
        '''
        result = self._values.get("widget_bullet")
        return typing.cast(typing.Optional[typing.List["OneDashboardPageWidgetBullet"]], result)

    @builtins.property
    def widget_funnel(
        self,
    ) -> typing.Optional[typing.List["OneDashboardPageWidgetFunnel"]]:
        '''widget_funnel block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#widget_funnel OneDashboard#widget_funnel}
        '''
        result = self._values.get("widget_funnel")
        return typing.cast(typing.Optional[typing.List["OneDashboardPageWidgetFunnel"]], result)

    @builtins.property
    def widget_heatmap(
        self,
    ) -> typing.Optional[typing.List["OneDashboardPageWidgetHeatmap"]]:
        '''widget_heatmap block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#widget_heatmap OneDashboard#widget_heatmap}
        '''
        result = self._values.get("widget_heatmap")
        return typing.cast(typing.Optional[typing.List["OneDashboardPageWidgetHeatmap"]], result)

    @builtins.property
    def widget_histogram(
        self,
    ) -> typing.Optional[typing.List["OneDashboardPageWidgetHistogram"]]:
        '''widget_histogram block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#widget_histogram OneDashboard#widget_histogram}
        '''
        result = self._values.get("widget_histogram")
        return typing.cast(typing.Optional[typing.List["OneDashboardPageWidgetHistogram"]], result)

    @builtins.property
    def widget_json(self) -> typing.Optional[typing.List["OneDashboardPageWidgetJson"]]:
        '''widget_json block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#widget_json OneDashboard#widget_json}
        '''
        result = self._values.get("widget_json")
        return typing.cast(typing.Optional[typing.List["OneDashboardPageWidgetJson"]], result)

    @builtins.property
    def widget_line(self) -> typing.Optional[typing.List["OneDashboardPageWidgetLine"]]:
        '''widget_line block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#widget_line OneDashboard#widget_line}
        '''
        result = self._values.get("widget_line")
        return typing.cast(typing.Optional[typing.List["OneDashboardPageWidgetLine"]], result)

    @builtins.property
    def widget_markdown(
        self,
    ) -> typing.Optional[typing.List["OneDashboardPageWidgetMarkdown"]]:
        '''widget_markdown block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#widget_markdown OneDashboard#widget_markdown}
        '''
        result = self._values.get("widget_markdown")
        return typing.cast(typing.Optional[typing.List["OneDashboardPageWidgetMarkdown"]], result)

    @builtins.property
    def widget_pie(self) -> typing.Optional[typing.List["OneDashboardPageWidgetPie"]]:
        '''widget_pie block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#widget_pie OneDashboard#widget_pie}
        '''
        result = self._values.get("widget_pie")
        return typing.cast(typing.Optional[typing.List["OneDashboardPageWidgetPie"]], result)

    @builtins.property
    def widget_stacked_bar(
        self,
    ) -> typing.Optional[typing.List["OneDashboardPageWidgetStackedBar"]]:
        '''widget_stacked_bar block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#widget_stacked_bar OneDashboard#widget_stacked_bar}
        '''
        result = self._values.get("widget_stacked_bar")
        return typing.cast(typing.Optional[typing.List["OneDashboardPageWidgetStackedBar"]], result)

    @builtins.property
    def widget_table(
        self,
    ) -> typing.Optional[typing.List["OneDashboardPageWidgetTable"]]:
        '''widget_table block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#widget_table OneDashboard#widget_table}
        '''
        result = self._values.get("widget_table")
        return typing.cast(typing.Optional[typing.List["OneDashboardPageWidgetTable"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OneDashboardPage(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.OneDashboardPageWidgetArea",
    jsii_struct_bases=[],
    name_mapping={
        "column": "column",
        "nrql_query": "nrqlQuery",
        "row": "row",
        "title": "title",
        "height": "height",
        "width": "width",
    },
)
class OneDashboardPageWidgetArea:
    def __init__(
        self,
        *,
        column: jsii.Number,
        nrql_query: typing.Sequence["OneDashboardPageWidgetAreaNrqlQuery"],
        row: jsii.Number,
        title: builtins.str,
        height: typing.Optional[jsii.Number] = None,
        width: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param column: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#column OneDashboard#column}.
        :param nrql_query: nrql_query block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#nrql_query OneDashboard#nrql_query}
        :param row: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#row OneDashboard#row}.
        :param title: A title for the widget. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#title OneDashboard#title}
        :param height: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#height OneDashboard#height}.
        :param width: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#width OneDashboard#width}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "column": column,
            "nrql_query": nrql_query,
            "row": row,
            "title": title,
        }
        if height is not None:
            self._values["height"] = height
        if width is not None:
            self._values["width"] = width

    @builtins.property
    def column(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#column OneDashboard#column}.'''
        result = self._values.get("column")
        assert result is not None, "Required property 'column' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def nrql_query(self) -> typing.List["OneDashboardPageWidgetAreaNrqlQuery"]:
        '''nrql_query block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#nrql_query OneDashboard#nrql_query}
        '''
        result = self._values.get("nrql_query")
        assert result is not None, "Required property 'nrql_query' is missing"
        return typing.cast(typing.List["OneDashboardPageWidgetAreaNrqlQuery"], result)

    @builtins.property
    def row(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#row OneDashboard#row}.'''
        result = self._values.get("row")
        assert result is not None, "Required property 'row' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def title(self) -> builtins.str:
        '''A title for the widget.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#title OneDashboard#title}
        '''
        result = self._values.get("title")
        assert result is not None, "Required property 'title' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def height(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#height OneDashboard#height}.'''
        result = self._values.get("height")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def width(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#width OneDashboard#width}.'''
        result = self._values.get("width")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OneDashboardPageWidgetArea(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.OneDashboardPageWidgetAreaNrqlQuery",
    jsii_struct_bases=[],
    name_mapping={"query": "query", "account_id": "accountId"},
)
class OneDashboardPageWidgetAreaNrqlQuery:
    def __init__(
        self,
        *,
        query: builtins.str,
        account_id: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param query: The NRQL query. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#query OneDashboard#query}
        :param account_id: The account id used for the NRQL query. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#account_id OneDashboard#account_id}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "query": query,
        }
        if account_id is not None:
            self._values["account_id"] = account_id

    @builtins.property
    def query(self) -> builtins.str:
        '''The NRQL query.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#query OneDashboard#query}
        '''
        result = self._values.get("query")
        assert result is not None, "Required property 'query' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def account_id(self) -> typing.Optional[jsii.Number]:
        '''The account id used for the NRQL query.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#account_id OneDashboard#account_id}
        '''
        result = self._values.get("account_id")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OneDashboardPageWidgetAreaNrqlQuery(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.OneDashboardPageWidgetBar",
    jsii_struct_bases=[],
    name_mapping={
        "column": "column",
        "nrql_query": "nrqlQuery",
        "row": "row",
        "title": "title",
        "filter_current_dashboard": "filterCurrentDashboard",
        "height": "height",
        "linked_entity_guids": "linkedEntityGuids",
        "width": "width",
    },
)
class OneDashboardPageWidgetBar:
    def __init__(
        self,
        *,
        column: jsii.Number,
        nrql_query: typing.Sequence["OneDashboardPageWidgetBarNrqlQuery"],
        row: jsii.Number,
        title: builtins.str,
        filter_current_dashboard: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        height: typing.Optional[jsii.Number] = None,
        linked_entity_guids: typing.Optional[typing.Sequence[builtins.str]] = None,
        width: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param column: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#column OneDashboard#column}.
        :param nrql_query: nrql_query block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#nrql_query OneDashboard#nrql_query}
        :param row: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#row OneDashboard#row}.
        :param title: A title for the widget. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#title OneDashboard#title}
        :param filter_current_dashboard: Use this item to filter the current dashboard. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#filter_current_dashboard OneDashboard#filter_current_dashboard}
        :param height: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#height OneDashboard#height}.
        :param linked_entity_guids: Related entities. Currently only supports Dashboard entities, but may allow other cases in the future. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#linked_entity_guids OneDashboard#linked_entity_guids}
        :param width: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#width OneDashboard#width}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "column": column,
            "nrql_query": nrql_query,
            "row": row,
            "title": title,
        }
        if filter_current_dashboard is not None:
            self._values["filter_current_dashboard"] = filter_current_dashboard
        if height is not None:
            self._values["height"] = height
        if linked_entity_guids is not None:
            self._values["linked_entity_guids"] = linked_entity_guids
        if width is not None:
            self._values["width"] = width

    @builtins.property
    def column(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#column OneDashboard#column}.'''
        result = self._values.get("column")
        assert result is not None, "Required property 'column' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def nrql_query(self) -> typing.List["OneDashboardPageWidgetBarNrqlQuery"]:
        '''nrql_query block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#nrql_query OneDashboard#nrql_query}
        '''
        result = self._values.get("nrql_query")
        assert result is not None, "Required property 'nrql_query' is missing"
        return typing.cast(typing.List["OneDashboardPageWidgetBarNrqlQuery"], result)

    @builtins.property
    def row(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#row OneDashboard#row}.'''
        result = self._values.get("row")
        assert result is not None, "Required property 'row' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def title(self) -> builtins.str:
        '''A title for the widget.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#title OneDashboard#title}
        '''
        result = self._values.get("title")
        assert result is not None, "Required property 'title' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def filter_current_dashboard(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Use this item to filter the current dashboard.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#filter_current_dashboard OneDashboard#filter_current_dashboard}
        '''
        result = self._values.get("filter_current_dashboard")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def height(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#height OneDashboard#height}.'''
        result = self._values.get("height")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def linked_entity_guids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Related entities. Currently only supports Dashboard entities, but may allow other cases in the future.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#linked_entity_guids OneDashboard#linked_entity_guids}
        '''
        result = self._values.get("linked_entity_guids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def width(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#width OneDashboard#width}.'''
        result = self._values.get("width")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OneDashboardPageWidgetBar(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.OneDashboardPageWidgetBarNrqlQuery",
    jsii_struct_bases=[],
    name_mapping={"query": "query", "account_id": "accountId"},
)
class OneDashboardPageWidgetBarNrqlQuery:
    def __init__(
        self,
        *,
        query: builtins.str,
        account_id: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param query: The NRQL query. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#query OneDashboard#query}
        :param account_id: The account id used for the NRQL query. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#account_id OneDashboard#account_id}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "query": query,
        }
        if account_id is not None:
            self._values["account_id"] = account_id

    @builtins.property
    def query(self) -> builtins.str:
        '''The NRQL query.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#query OneDashboard#query}
        '''
        result = self._values.get("query")
        assert result is not None, "Required property 'query' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def account_id(self) -> typing.Optional[jsii.Number]:
        '''The account id used for the NRQL query.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#account_id OneDashboard#account_id}
        '''
        result = self._values.get("account_id")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OneDashboardPageWidgetBarNrqlQuery(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.OneDashboardPageWidgetBillboard",
    jsii_struct_bases=[],
    name_mapping={
        "column": "column",
        "nrql_query": "nrqlQuery",
        "row": "row",
        "title": "title",
        "critical": "critical",
        "height": "height",
        "warning": "warning",
        "width": "width",
    },
)
class OneDashboardPageWidgetBillboard:
    def __init__(
        self,
        *,
        column: jsii.Number,
        nrql_query: typing.Sequence["OneDashboardPageWidgetBillboardNrqlQuery"],
        row: jsii.Number,
        title: builtins.str,
        critical: typing.Optional[jsii.Number] = None,
        height: typing.Optional[jsii.Number] = None,
        warning: typing.Optional[jsii.Number] = None,
        width: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param column: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#column OneDashboard#column}.
        :param nrql_query: nrql_query block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#nrql_query OneDashboard#nrql_query}
        :param row: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#row OneDashboard#row}.
        :param title: A title for the widget. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#title OneDashboard#title}
        :param critical: The critical threshold value. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#critical OneDashboard#critical}
        :param height: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#height OneDashboard#height}.
        :param warning: The warning threshold value. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#warning OneDashboard#warning}
        :param width: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#width OneDashboard#width}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "column": column,
            "nrql_query": nrql_query,
            "row": row,
            "title": title,
        }
        if critical is not None:
            self._values["critical"] = critical
        if height is not None:
            self._values["height"] = height
        if warning is not None:
            self._values["warning"] = warning
        if width is not None:
            self._values["width"] = width

    @builtins.property
    def column(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#column OneDashboard#column}.'''
        result = self._values.get("column")
        assert result is not None, "Required property 'column' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def nrql_query(self) -> typing.List["OneDashboardPageWidgetBillboardNrqlQuery"]:
        '''nrql_query block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#nrql_query OneDashboard#nrql_query}
        '''
        result = self._values.get("nrql_query")
        assert result is not None, "Required property 'nrql_query' is missing"
        return typing.cast(typing.List["OneDashboardPageWidgetBillboardNrqlQuery"], result)

    @builtins.property
    def row(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#row OneDashboard#row}.'''
        result = self._values.get("row")
        assert result is not None, "Required property 'row' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def title(self) -> builtins.str:
        '''A title for the widget.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#title OneDashboard#title}
        '''
        result = self._values.get("title")
        assert result is not None, "Required property 'title' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def critical(self) -> typing.Optional[jsii.Number]:
        '''The critical threshold value.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#critical OneDashboard#critical}
        '''
        result = self._values.get("critical")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def height(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#height OneDashboard#height}.'''
        result = self._values.get("height")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def warning(self) -> typing.Optional[jsii.Number]:
        '''The warning threshold value.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#warning OneDashboard#warning}
        '''
        result = self._values.get("warning")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def width(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#width OneDashboard#width}.'''
        result = self._values.get("width")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OneDashboardPageWidgetBillboard(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.OneDashboardPageWidgetBillboardNrqlQuery",
    jsii_struct_bases=[],
    name_mapping={"query": "query", "account_id": "accountId"},
)
class OneDashboardPageWidgetBillboardNrqlQuery:
    def __init__(
        self,
        *,
        query: builtins.str,
        account_id: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param query: The NRQL query. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#query OneDashboard#query}
        :param account_id: The account id used for the NRQL query. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#account_id OneDashboard#account_id}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "query": query,
        }
        if account_id is not None:
            self._values["account_id"] = account_id

    @builtins.property
    def query(self) -> builtins.str:
        '''The NRQL query.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#query OneDashboard#query}
        '''
        result = self._values.get("query")
        assert result is not None, "Required property 'query' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def account_id(self) -> typing.Optional[jsii.Number]:
        '''The account id used for the NRQL query.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#account_id OneDashboard#account_id}
        '''
        result = self._values.get("account_id")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OneDashboardPageWidgetBillboardNrqlQuery(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.OneDashboardPageWidgetBullet",
    jsii_struct_bases=[],
    name_mapping={
        "column": "column",
        "nrql_query": "nrqlQuery",
        "row": "row",
        "title": "title",
        "height": "height",
        "limit": "limit",
        "width": "width",
    },
)
class OneDashboardPageWidgetBullet:
    def __init__(
        self,
        *,
        column: jsii.Number,
        nrql_query: typing.Sequence["OneDashboardPageWidgetBulletNrqlQuery"],
        row: jsii.Number,
        title: builtins.str,
        height: typing.Optional[jsii.Number] = None,
        limit: typing.Optional[jsii.Number] = None,
        width: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param column: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#column OneDashboard#column}.
        :param nrql_query: nrql_query block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#nrql_query OneDashboard#nrql_query}
        :param row: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#row OneDashboard#row}.
        :param title: A title for the widget. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#title OneDashboard#title}
        :param height: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#height OneDashboard#height}.
        :param limit: The maximum value for the visualization. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#limit OneDashboard#limit}
        :param width: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#width OneDashboard#width}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "column": column,
            "nrql_query": nrql_query,
            "row": row,
            "title": title,
        }
        if height is not None:
            self._values["height"] = height
        if limit is not None:
            self._values["limit"] = limit
        if width is not None:
            self._values["width"] = width

    @builtins.property
    def column(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#column OneDashboard#column}.'''
        result = self._values.get("column")
        assert result is not None, "Required property 'column' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def nrql_query(self) -> typing.List["OneDashboardPageWidgetBulletNrqlQuery"]:
        '''nrql_query block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#nrql_query OneDashboard#nrql_query}
        '''
        result = self._values.get("nrql_query")
        assert result is not None, "Required property 'nrql_query' is missing"
        return typing.cast(typing.List["OneDashboardPageWidgetBulletNrqlQuery"], result)

    @builtins.property
    def row(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#row OneDashboard#row}.'''
        result = self._values.get("row")
        assert result is not None, "Required property 'row' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def title(self) -> builtins.str:
        '''A title for the widget.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#title OneDashboard#title}
        '''
        result = self._values.get("title")
        assert result is not None, "Required property 'title' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def height(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#height OneDashboard#height}.'''
        result = self._values.get("height")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def limit(self) -> typing.Optional[jsii.Number]:
        '''The maximum value for the visualization.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#limit OneDashboard#limit}
        '''
        result = self._values.get("limit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def width(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#width OneDashboard#width}.'''
        result = self._values.get("width")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OneDashboardPageWidgetBullet(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.OneDashboardPageWidgetBulletNrqlQuery",
    jsii_struct_bases=[],
    name_mapping={"query": "query", "account_id": "accountId"},
)
class OneDashboardPageWidgetBulletNrqlQuery:
    def __init__(
        self,
        *,
        query: builtins.str,
        account_id: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param query: The NRQL query. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#query OneDashboard#query}
        :param account_id: The account id used for the NRQL query. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#account_id OneDashboard#account_id}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "query": query,
        }
        if account_id is not None:
            self._values["account_id"] = account_id

    @builtins.property
    def query(self) -> builtins.str:
        '''The NRQL query.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#query OneDashboard#query}
        '''
        result = self._values.get("query")
        assert result is not None, "Required property 'query' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def account_id(self) -> typing.Optional[jsii.Number]:
        '''The account id used for the NRQL query.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#account_id OneDashboard#account_id}
        '''
        result = self._values.get("account_id")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OneDashboardPageWidgetBulletNrqlQuery(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.OneDashboardPageWidgetFunnel",
    jsii_struct_bases=[],
    name_mapping={
        "column": "column",
        "nrql_query": "nrqlQuery",
        "row": "row",
        "title": "title",
        "height": "height",
        "width": "width",
    },
)
class OneDashboardPageWidgetFunnel:
    def __init__(
        self,
        *,
        column: jsii.Number,
        nrql_query: typing.Sequence["OneDashboardPageWidgetFunnelNrqlQuery"],
        row: jsii.Number,
        title: builtins.str,
        height: typing.Optional[jsii.Number] = None,
        width: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param column: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#column OneDashboard#column}.
        :param nrql_query: nrql_query block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#nrql_query OneDashboard#nrql_query}
        :param row: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#row OneDashboard#row}.
        :param title: A title for the widget. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#title OneDashboard#title}
        :param height: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#height OneDashboard#height}.
        :param width: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#width OneDashboard#width}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "column": column,
            "nrql_query": nrql_query,
            "row": row,
            "title": title,
        }
        if height is not None:
            self._values["height"] = height
        if width is not None:
            self._values["width"] = width

    @builtins.property
    def column(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#column OneDashboard#column}.'''
        result = self._values.get("column")
        assert result is not None, "Required property 'column' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def nrql_query(self) -> typing.List["OneDashboardPageWidgetFunnelNrqlQuery"]:
        '''nrql_query block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#nrql_query OneDashboard#nrql_query}
        '''
        result = self._values.get("nrql_query")
        assert result is not None, "Required property 'nrql_query' is missing"
        return typing.cast(typing.List["OneDashboardPageWidgetFunnelNrqlQuery"], result)

    @builtins.property
    def row(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#row OneDashboard#row}.'''
        result = self._values.get("row")
        assert result is not None, "Required property 'row' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def title(self) -> builtins.str:
        '''A title for the widget.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#title OneDashboard#title}
        '''
        result = self._values.get("title")
        assert result is not None, "Required property 'title' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def height(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#height OneDashboard#height}.'''
        result = self._values.get("height")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def width(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#width OneDashboard#width}.'''
        result = self._values.get("width")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OneDashboardPageWidgetFunnel(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.OneDashboardPageWidgetFunnelNrqlQuery",
    jsii_struct_bases=[],
    name_mapping={"query": "query", "account_id": "accountId"},
)
class OneDashboardPageWidgetFunnelNrqlQuery:
    def __init__(
        self,
        *,
        query: builtins.str,
        account_id: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param query: The NRQL query. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#query OneDashboard#query}
        :param account_id: The account id used for the NRQL query. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#account_id OneDashboard#account_id}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "query": query,
        }
        if account_id is not None:
            self._values["account_id"] = account_id

    @builtins.property
    def query(self) -> builtins.str:
        '''The NRQL query.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#query OneDashboard#query}
        '''
        result = self._values.get("query")
        assert result is not None, "Required property 'query' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def account_id(self) -> typing.Optional[jsii.Number]:
        '''The account id used for the NRQL query.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#account_id OneDashboard#account_id}
        '''
        result = self._values.get("account_id")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OneDashboardPageWidgetFunnelNrqlQuery(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.OneDashboardPageWidgetHeatmap",
    jsii_struct_bases=[],
    name_mapping={
        "column": "column",
        "nrql_query": "nrqlQuery",
        "row": "row",
        "title": "title",
        "height": "height",
        "width": "width",
    },
)
class OneDashboardPageWidgetHeatmap:
    def __init__(
        self,
        *,
        column: jsii.Number,
        nrql_query: typing.Sequence["OneDashboardPageWidgetHeatmapNrqlQuery"],
        row: jsii.Number,
        title: builtins.str,
        height: typing.Optional[jsii.Number] = None,
        width: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param column: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#column OneDashboard#column}.
        :param nrql_query: nrql_query block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#nrql_query OneDashboard#nrql_query}
        :param row: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#row OneDashboard#row}.
        :param title: A title for the widget. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#title OneDashboard#title}
        :param height: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#height OneDashboard#height}.
        :param width: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#width OneDashboard#width}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "column": column,
            "nrql_query": nrql_query,
            "row": row,
            "title": title,
        }
        if height is not None:
            self._values["height"] = height
        if width is not None:
            self._values["width"] = width

    @builtins.property
    def column(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#column OneDashboard#column}.'''
        result = self._values.get("column")
        assert result is not None, "Required property 'column' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def nrql_query(self) -> typing.List["OneDashboardPageWidgetHeatmapNrqlQuery"]:
        '''nrql_query block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#nrql_query OneDashboard#nrql_query}
        '''
        result = self._values.get("nrql_query")
        assert result is not None, "Required property 'nrql_query' is missing"
        return typing.cast(typing.List["OneDashboardPageWidgetHeatmapNrqlQuery"], result)

    @builtins.property
    def row(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#row OneDashboard#row}.'''
        result = self._values.get("row")
        assert result is not None, "Required property 'row' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def title(self) -> builtins.str:
        '''A title for the widget.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#title OneDashboard#title}
        '''
        result = self._values.get("title")
        assert result is not None, "Required property 'title' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def height(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#height OneDashboard#height}.'''
        result = self._values.get("height")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def width(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#width OneDashboard#width}.'''
        result = self._values.get("width")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OneDashboardPageWidgetHeatmap(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.OneDashboardPageWidgetHeatmapNrqlQuery",
    jsii_struct_bases=[],
    name_mapping={"query": "query", "account_id": "accountId"},
)
class OneDashboardPageWidgetHeatmapNrqlQuery:
    def __init__(
        self,
        *,
        query: builtins.str,
        account_id: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param query: The NRQL query. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#query OneDashboard#query}
        :param account_id: The account id used for the NRQL query. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#account_id OneDashboard#account_id}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "query": query,
        }
        if account_id is not None:
            self._values["account_id"] = account_id

    @builtins.property
    def query(self) -> builtins.str:
        '''The NRQL query.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#query OneDashboard#query}
        '''
        result = self._values.get("query")
        assert result is not None, "Required property 'query' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def account_id(self) -> typing.Optional[jsii.Number]:
        '''The account id used for the NRQL query.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#account_id OneDashboard#account_id}
        '''
        result = self._values.get("account_id")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OneDashboardPageWidgetHeatmapNrqlQuery(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.OneDashboardPageWidgetHistogram",
    jsii_struct_bases=[],
    name_mapping={
        "column": "column",
        "nrql_query": "nrqlQuery",
        "row": "row",
        "title": "title",
        "height": "height",
        "width": "width",
    },
)
class OneDashboardPageWidgetHistogram:
    def __init__(
        self,
        *,
        column: jsii.Number,
        nrql_query: typing.Sequence["OneDashboardPageWidgetHistogramNrqlQuery"],
        row: jsii.Number,
        title: builtins.str,
        height: typing.Optional[jsii.Number] = None,
        width: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param column: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#column OneDashboard#column}.
        :param nrql_query: nrql_query block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#nrql_query OneDashboard#nrql_query}
        :param row: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#row OneDashboard#row}.
        :param title: A title for the widget. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#title OneDashboard#title}
        :param height: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#height OneDashboard#height}.
        :param width: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#width OneDashboard#width}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "column": column,
            "nrql_query": nrql_query,
            "row": row,
            "title": title,
        }
        if height is not None:
            self._values["height"] = height
        if width is not None:
            self._values["width"] = width

    @builtins.property
    def column(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#column OneDashboard#column}.'''
        result = self._values.get("column")
        assert result is not None, "Required property 'column' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def nrql_query(self) -> typing.List["OneDashboardPageWidgetHistogramNrqlQuery"]:
        '''nrql_query block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#nrql_query OneDashboard#nrql_query}
        '''
        result = self._values.get("nrql_query")
        assert result is not None, "Required property 'nrql_query' is missing"
        return typing.cast(typing.List["OneDashboardPageWidgetHistogramNrqlQuery"], result)

    @builtins.property
    def row(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#row OneDashboard#row}.'''
        result = self._values.get("row")
        assert result is not None, "Required property 'row' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def title(self) -> builtins.str:
        '''A title for the widget.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#title OneDashboard#title}
        '''
        result = self._values.get("title")
        assert result is not None, "Required property 'title' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def height(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#height OneDashboard#height}.'''
        result = self._values.get("height")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def width(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#width OneDashboard#width}.'''
        result = self._values.get("width")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OneDashboardPageWidgetHistogram(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.OneDashboardPageWidgetHistogramNrqlQuery",
    jsii_struct_bases=[],
    name_mapping={"query": "query", "account_id": "accountId"},
)
class OneDashboardPageWidgetHistogramNrqlQuery:
    def __init__(
        self,
        *,
        query: builtins.str,
        account_id: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param query: The NRQL query. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#query OneDashboard#query}
        :param account_id: The account id used for the NRQL query. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#account_id OneDashboard#account_id}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "query": query,
        }
        if account_id is not None:
            self._values["account_id"] = account_id

    @builtins.property
    def query(self) -> builtins.str:
        '''The NRQL query.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#query OneDashboard#query}
        '''
        result = self._values.get("query")
        assert result is not None, "Required property 'query' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def account_id(self) -> typing.Optional[jsii.Number]:
        '''The account id used for the NRQL query.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#account_id OneDashboard#account_id}
        '''
        result = self._values.get("account_id")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OneDashboardPageWidgetHistogramNrqlQuery(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.OneDashboardPageWidgetJson",
    jsii_struct_bases=[],
    name_mapping={
        "column": "column",
        "nrql_query": "nrqlQuery",
        "row": "row",
        "title": "title",
        "height": "height",
        "width": "width",
    },
)
class OneDashboardPageWidgetJson:
    def __init__(
        self,
        *,
        column: jsii.Number,
        nrql_query: typing.Sequence["OneDashboardPageWidgetJsonNrqlQuery"],
        row: jsii.Number,
        title: builtins.str,
        height: typing.Optional[jsii.Number] = None,
        width: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param column: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#column OneDashboard#column}.
        :param nrql_query: nrql_query block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#nrql_query OneDashboard#nrql_query}
        :param row: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#row OneDashboard#row}.
        :param title: A title for the widget. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#title OneDashboard#title}
        :param height: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#height OneDashboard#height}.
        :param width: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#width OneDashboard#width}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "column": column,
            "nrql_query": nrql_query,
            "row": row,
            "title": title,
        }
        if height is not None:
            self._values["height"] = height
        if width is not None:
            self._values["width"] = width

    @builtins.property
    def column(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#column OneDashboard#column}.'''
        result = self._values.get("column")
        assert result is not None, "Required property 'column' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def nrql_query(self) -> typing.List["OneDashboardPageWidgetJsonNrqlQuery"]:
        '''nrql_query block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#nrql_query OneDashboard#nrql_query}
        '''
        result = self._values.get("nrql_query")
        assert result is not None, "Required property 'nrql_query' is missing"
        return typing.cast(typing.List["OneDashboardPageWidgetJsonNrqlQuery"], result)

    @builtins.property
    def row(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#row OneDashboard#row}.'''
        result = self._values.get("row")
        assert result is not None, "Required property 'row' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def title(self) -> builtins.str:
        '''A title for the widget.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#title OneDashboard#title}
        '''
        result = self._values.get("title")
        assert result is not None, "Required property 'title' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def height(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#height OneDashboard#height}.'''
        result = self._values.get("height")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def width(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#width OneDashboard#width}.'''
        result = self._values.get("width")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OneDashboardPageWidgetJson(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.OneDashboardPageWidgetJsonNrqlQuery",
    jsii_struct_bases=[],
    name_mapping={"query": "query", "account_id": "accountId"},
)
class OneDashboardPageWidgetJsonNrqlQuery:
    def __init__(
        self,
        *,
        query: builtins.str,
        account_id: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param query: The NRQL query. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#query OneDashboard#query}
        :param account_id: The account id used for the NRQL query. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#account_id OneDashboard#account_id}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "query": query,
        }
        if account_id is not None:
            self._values["account_id"] = account_id

    @builtins.property
    def query(self) -> builtins.str:
        '''The NRQL query.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#query OneDashboard#query}
        '''
        result = self._values.get("query")
        assert result is not None, "Required property 'query' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def account_id(self) -> typing.Optional[jsii.Number]:
        '''The account id used for the NRQL query.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#account_id OneDashboard#account_id}
        '''
        result = self._values.get("account_id")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OneDashboardPageWidgetJsonNrqlQuery(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.OneDashboardPageWidgetLine",
    jsii_struct_bases=[],
    name_mapping={
        "column": "column",
        "nrql_query": "nrqlQuery",
        "row": "row",
        "title": "title",
        "height": "height",
        "width": "width",
    },
)
class OneDashboardPageWidgetLine:
    def __init__(
        self,
        *,
        column: jsii.Number,
        nrql_query: typing.Sequence["OneDashboardPageWidgetLineNrqlQuery"],
        row: jsii.Number,
        title: builtins.str,
        height: typing.Optional[jsii.Number] = None,
        width: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param column: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#column OneDashboard#column}.
        :param nrql_query: nrql_query block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#nrql_query OneDashboard#nrql_query}
        :param row: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#row OneDashboard#row}.
        :param title: A title for the widget. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#title OneDashboard#title}
        :param height: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#height OneDashboard#height}.
        :param width: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#width OneDashboard#width}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "column": column,
            "nrql_query": nrql_query,
            "row": row,
            "title": title,
        }
        if height is not None:
            self._values["height"] = height
        if width is not None:
            self._values["width"] = width

    @builtins.property
    def column(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#column OneDashboard#column}.'''
        result = self._values.get("column")
        assert result is not None, "Required property 'column' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def nrql_query(self) -> typing.List["OneDashboardPageWidgetLineNrqlQuery"]:
        '''nrql_query block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#nrql_query OneDashboard#nrql_query}
        '''
        result = self._values.get("nrql_query")
        assert result is not None, "Required property 'nrql_query' is missing"
        return typing.cast(typing.List["OneDashboardPageWidgetLineNrqlQuery"], result)

    @builtins.property
    def row(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#row OneDashboard#row}.'''
        result = self._values.get("row")
        assert result is not None, "Required property 'row' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def title(self) -> builtins.str:
        '''A title for the widget.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#title OneDashboard#title}
        '''
        result = self._values.get("title")
        assert result is not None, "Required property 'title' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def height(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#height OneDashboard#height}.'''
        result = self._values.get("height")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def width(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#width OneDashboard#width}.'''
        result = self._values.get("width")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OneDashboardPageWidgetLine(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.OneDashboardPageWidgetLineNrqlQuery",
    jsii_struct_bases=[],
    name_mapping={"query": "query", "account_id": "accountId"},
)
class OneDashboardPageWidgetLineNrqlQuery:
    def __init__(
        self,
        *,
        query: builtins.str,
        account_id: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param query: The NRQL query. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#query OneDashboard#query}
        :param account_id: The account id used for the NRQL query. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#account_id OneDashboard#account_id}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "query": query,
        }
        if account_id is not None:
            self._values["account_id"] = account_id

    @builtins.property
    def query(self) -> builtins.str:
        '''The NRQL query.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#query OneDashboard#query}
        '''
        result = self._values.get("query")
        assert result is not None, "Required property 'query' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def account_id(self) -> typing.Optional[jsii.Number]:
        '''The account id used for the NRQL query.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#account_id OneDashboard#account_id}
        '''
        result = self._values.get("account_id")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OneDashboardPageWidgetLineNrqlQuery(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.OneDashboardPageWidgetMarkdown",
    jsii_struct_bases=[],
    name_mapping={
        "column": "column",
        "row": "row",
        "title": "title",
        "height": "height",
        "text": "text",
        "width": "width",
    },
)
class OneDashboardPageWidgetMarkdown:
    def __init__(
        self,
        *,
        column: jsii.Number,
        row: jsii.Number,
        title: builtins.str,
        height: typing.Optional[jsii.Number] = None,
        text: typing.Optional[builtins.str] = None,
        width: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param column: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#column OneDashboard#column}.
        :param row: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#row OneDashboard#row}.
        :param title: A title for the widget. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#title OneDashboard#title}
        :param height: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#height OneDashboard#height}.
        :param text: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#text OneDashboard#text}.
        :param width: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#width OneDashboard#width}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "column": column,
            "row": row,
            "title": title,
        }
        if height is not None:
            self._values["height"] = height
        if text is not None:
            self._values["text"] = text
        if width is not None:
            self._values["width"] = width

    @builtins.property
    def column(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#column OneDashboard#column}.'''
        result = self._values.get("column")
        assert result is not None, "Required property 'column' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def row(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#row OneDashboard#row}.'''
        result = self._values.get("row")
        assert result is not None, "Required property 'row' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def title(self) -> builtins.str:
        '''A title for the widget.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#title OneDashboard#title}
        '''
        result = self._values.get("title")
        assert result is not None, "Required property 'title' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def height(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#height OneDashboard#height}.'''
        result = self._values.get("height")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def text(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#text OneDashboard#text}.'''
        result = self._values.get("text")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def width(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#width OneDashboard#width}.'''
        result = self._values.get("width")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OneDashboardPageWidgetMarkdown(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.OneDashboardPageWidgetPie",
    jsii_struct_bases=[],
    name_mapping={
        "column": "column",
        "nrql_query": "nrqlQuery",
        "row": "row",
        "title": "title",
        "filter_current_dashboard": "filterCurrentDashboard",
        "height": "height",
        "linked_entity_guids": "linkedEntityGuids",
        "width": "width",
    },
)
class OneDashboardPageWidgetPie:
    def __init__(
        self,
        *,
        column: jsii.Number,
        nrql_query: typing.Sequence["OneDashboardPageWidgetPieNrqlQuery"],
        row: jsii.Number,
        title: builtins.str,
        filter_current_dashboard: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        height: typing.Optional[jsii.Number] = None,
        linked_entity_guids: typing.Optional[typing.Sequence[builtins.str]] = None,
        width: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param column: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#column OneDashboard#column}.
        :param nrql_query: nrql_query block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#nrql_query OneDashboard#nrql_query}
        :param row: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#row OneDashboard#row}.
        :param title: A title for the widget. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#title OneDashboard#title}
        :param filter_current_dashboard: Use this item to filter the current dashboard. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#filter_current_dashboard OneDashboard#filter_current_dashboard}
        :param height: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#height OneDashboard#height}.
        :param linked_entity_guids: Related entities. Currently only supports Dashboard entities, but may allow other cases in the future. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#linked_entity_guids OneDashboard#linked_entity_guids}
        :param width: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#width OneDashboard#width}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "column": column,
            "nrql_query": nrql_query,
            "row": row,
            "title": title,
        }
        if filter_current_dashboard is not None:
            self._values["filter_current_dashboard"] = filter_current_dashboard
        if height is not None:
            self._values["height"] = height
        if linked_entity_guids is not None:
            self._values["linked_entity_guids"] = linked_entity_guids
        if width is not None:
            self._values["width"] = width

    @builtins.property
    def column(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#column OneDashboard#column}.'''
        result = self._values.get("column")
        assert result is not None, "Required property 'column' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def nrql_query(self) -> typing.List["OneDashboardPageWidgetPieNrqlQuery"]:
        '''nrql_query block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#nrql_query OneDashboard#nrql_query}
        '''
        result = self._values.get("nrql_query")
        assert result is not None, "Required property 'nrql_query' is missing"
        return typing.cast(typing.List["OneDashboardPageWidgetPieNrqlQuery"], result)

    @builtins.property
    def row(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#row OneDashboard#row}.'''
        result = self._values.get("row")
        assert result is not None, "Required property 'row' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def title(self) -> builtins.str:
        '''A title for the widget.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#title OneDashboard#title}
        '''
        result = self._values.get("title")
        assert result is not None, "Required property 'title' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def filter_current_dashboard(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Use this item to filter the current dashboard.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#filter_current_dashboard OneDashboard#filter_current_dashboard}
        '''
        result = self._values.get("filter_current_dashboard")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def height(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#height OneDashboard#height}.'''
        result = self._values.get("height")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def linked_entity_guids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Related entities. Currently only supports Dashboard entities, but may allow other cases in the future.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#linked_entity_guids OneDashboard#linked_entity_guids}
        '''
        result = self._values.get("linked_entity_guids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def width(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#width OneDashboard#width}.'''
        result = self._values.get("width")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OneDashboardPageWidgetPie(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.OneDashboardPageWidgetPieNrqlQuery",
    jsii_struct_bases=[],
    name_mapping={"query": "query", "account_id": "accountId"},
)
class OneDashboardPageWidgetPieNrqlQuery:
    def __init__(
        self,
        *,
        query: builtins.str,
        account_id: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param query: The NRQL query. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#query OneDashboard#query}
        :param account_id: The account id used for the NRQL query. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#account_id OneDashboard#account_id}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "query": query,
        }
        if account_id is not None:
            self._values["account_id"] = account_id

    @builtins.property
    def query(self) -> builtins.str:
        '''The NRQL query.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#query OneDashboard#query}
        '''
        result = self._values.get("query")
        assert result is not None, "Required property 'query' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def account_id(self) -> typing.Optional[jsii.Number]:
        '''The account id used for the NRQL query.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#account_id OneDashboard#account_id}
        '''
        result = self._values.get("account_id")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OneDashboardPageWidgetPieNrqlQuery(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.OneDashboardPageWidgetStackedBar",
    jsii_struct_bases=[],
    name_mapping={
        "column": "column",
        "nrql_query": "nrqlQuery",
        "row": "row",
        "title": "title",
        "height": "height",
        "width": "width",
    },
)
class OneDashboardPageWidgetStackedBar:
    def __init__(
        self,
        *,
        column: jsii.Number,
        nrql_query: typing.Sequence["OneDashboardPageWidgetStackedBarNrqlQuery"],
        row: jsii.Number,
        title: builtins.str,
        height: typing.Optional[jsii.Number] = None,
        width: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param column: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#column OneDashboard#column}.
        :param nrql_query: nrql_query block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#nrql_query OneDashboard#nrql_query}
        :param row: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#row OneDashboard#row}.
        :param title: A title for the widget. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#title OneDashboard#title}
        :param height: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#height OneDashboard#height}.
        :param width: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#width OneDashboard#width}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "column": column,
            "nrql_query": nrql_query,
            "row": row,
            "title": title,
        }
        if height is not None:
            self._values["height"] = height
        if width is not None:
            self._values["width"] = width

    @builtins.property
    def column(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#column OneDashboard#column}.'''
        result = self._values.get("column")
        assert result is not None, "Required property 'column' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def nrql_query(self) -> typing.List["OneDashboardPageWidgetStackedBarNrqlQuery"]:
        '''nrql_query block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#nrql_query OneDashboard#nrql_query}
        '''
        result = self._values.get("nrql_query")
        assert result is not None, "Required property 'nrql_query' is missing"
        return typing.cast(typing.List["OneDashboardPageWidgetStackedBarNrqlQuery"], result)

    @builtins.property
    def row(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#row OneDashboard#row}.'''
        result = self._values.get("row")
        assert result is not None, "Required property 'row' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def title(self) -> builtins.str:
        '''A title for the widget.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#title OneDashboard#title}
        '''
        result = self._values.get("title")
        assert result is not None, "Required property 'title' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def height(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#height OneDashboard#height}.'''
        result = self._values.get("height")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def width(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#width OneDashboard#width}.'''
        result = self._values.get("width")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OneDashboardPageWidgetStackedBar(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.OneDashboardPageWidgetStackedBarNrqlQuery",
    jsii_struct_bases=[],
    name_mapping={"query": "query", "account_id": "accountId"},
)
class OneDashboardPageWidgetStackedBarNrqlQuery:
    def __init__(
        self,
        *,
        query: builtins.str,
        account_id: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param query: The NRQL query. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#query OneDashboard#query}
        :param account_id: The account id used for the NRQL query. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#account_id OneDashboard#account_id}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "query": query,
        }
        if account_id is not None:
            self._values["account_id"] = account_id

    @builtins.property
    def query(self) -> builtins.str:
        '''The NRQL query.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#query OneDashboard#query}
        '''
        result = self._values.get("query")
        assert result is not None, "Required property 'query' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def account_id(self) -> typing.Optional[jsii.Number]:
        '''The account id used for the NRQL query.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#account_id OneDashboard#account_id}
        '''
        result = self._values.get("account_id")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OneDashboardPageWidgetStackedBarNrqlQuery(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.OneDashboardPageWidgetTable",
    jsii_struct_bases=[],
    name_mapping={
        "column": "column",
        "nrql_query": "nrqlQuery",
        "row": "row",
        "title": "title",
        "filter_current_dashboard": "filterCurrentDashboard",
        "height": "height",
        "linked_entity_guids": "linkedEntityGuids",
        "width": "width",
    },
)
class OneDashboardPageWidgetTable:
    def __init__(
        self,
        *,
        column: jsii.Number,
        nrql_query: typing.Sequence["OneDashboardPageWidgetTableNrqlQuery"],
        row: jsii.Number,
        title: builtins.str,
        filter_current_dashboard: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        height: typing.Optional[jsii.Number] = None,
        linked_entity_guids: typing.Optional[typing.Sequence[builtins.str]] = None,
        width: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param column: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#column OneDashboard#column}.
        :param nrql_query: nrql_query block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#nrql_query OneDashboard#nrql_query}
        :param row: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#row OneDashboard#row}.
        :param title: A title for the widget. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#title OneDashboard#title}
        :param filter_current_dashboard: Use this item to filter the current dashboard. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#filter_current_dashboard OneDashboard#filter_current_dashboard}
        :param height: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#height OneDashboard#height}.
        :param linked_entity_guids: Related entities. Currently only supports Dashboard entities, but may allow other cases in the future. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#linked_entity_guids OneDashboard#linked_entity_guids}
        :param width: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#width OneDashboard#width}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "column": column,
            "nrql_query": nrql_query,
            "row": row,
            "title": title,
        }
        if filter_current_dashboard is not None:
            self._values["filter_current_dashboard"] = filter_current_dashboard
        if height is not None:
            self._values["height"] = height
        if linked_entity_guids is not None:
            self._values["linked_entity_guids"] = linked_entity_guids
        if width is not None:
            self._values["width"] = width

    @builtins.property
    def column(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#column OneDashboard#column}.'''
        result = self._values.get("column")
        assert result is not None, "Required property 'column' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def nrql_query(self) -> typing.List["OneDashboardPageWidgetTableNrqlQuery"]:
        '''nrql_query block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#nrql_query OneDashboard#nrql_query}
        '''
        result = self._values.get("nrql_query")
        assert result is not None, "Required property 'nrql_query' is missing"
        return typing.cast(typing.List["OneDashboardPageWidgetTableNrqlQuery"], result)

    @builtins.property
    def row(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#row OneDashboard#row}.'''
        result = self._values.get("row")
        assert result is not None, "Required property 'row' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def title(self) -> builtins.str:
        '''A title for the widget.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#title OneDashboard#title}
        '''
        result = self._values.get("title")
        assert result is not None, "Required property 'title' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def filter_current_dashboard(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Use this item to filter the current dashboard.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#filter_current_dashboard OneDashboard#filter_current_dashboard}
        '''
        result = self._values.get("filter_current_dashboard")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def height(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#height OneDashboard#height}.'''
        result = self._values.get("height")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def linked_entity_guids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Related entities. Currently only supports Dashboard entities, but may allow other cases in the future.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#linked_entity_guids OneDashboard#linked_entity_guids}
        '''
        result = self._values.get("linked_entity_guids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def width(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#width OneDashboard#width}.'''
        result = self._values.get("width")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OneDashboardPageWidgetTable(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.OneDashboardPageWidgetTableNrqlQuery",
    jsii_struct_bases=[],
    name_mapping={"query": "query", "account_id": "accountId"},
)
class OneDashboardPageWidgetTableNrqlQuery:
    def __init__(
        self,
        *,
        query: builtins.str,
        account_id: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param query: The NRQL query. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#query OneDashboard#query}
        :param account_id: The account id used for the NRQL query. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#account_id OneDashboard#account_id}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "query": query,
        }
        if account_id is not None:
            self._values["account_id"] = account_id

    @builtins.property
    def query(self) -> builtins.str:
        '''The NRQL query.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#query OneDashboard#query}
        '''
        result = self._values.get("query")
        assert result is not None, "Required property 'query' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def account_id(self) -> typing.Optional[jsii.Number]:
        '''The account id used for the NRQL query.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard#account_id OneDashboard#account_id}
        '''
        result = self._values.get("account_id")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OneDashboardPageWidgetTableNrqlQuery(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OneDashboardRaw(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-newrelic.OneDashboardRaw",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard_raw newrelic_one_dashboard_raw}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        page: typing.Sequence["OneDashboardRawPage"],
        account_id: typing.Optional[jsii.Number] = None,
        description: typing.Optional[builtins.str] = None,
        permissions: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard_raw newrelic_one_dashboard_raw} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: The dashboard's name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard_raw#name OneDashboardRaw#name}
        :param page: page block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard_raw#page OneDashboardRaw#page}
        :param account_id: The New Relic account ID where you want to create the dashboard. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard_raw#account_id OneDashboardRaw#account_id}
        :param description: The dashboard's description. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard_raw#description OneDashboardRaw#description}
        :param permissions: Determines who can see or edit the dashboard. Valid values are private, public_read_only, public_read_write. Defaults to public_read_only. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard_raw#permissions OneDashboardRaw#permissions}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = OneDashboardRawConfig(
            name=name,
            page=page,
            account_id=account_id,
            description=description,
            permissions=permissions,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetAccountId")
    def reset_account_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccountId", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetPermissions")
    def reset_permissions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPermissions", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="guid")
    def guid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "guid"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="permalink")
    def permalink(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "permalink"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "accountIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pageInput")
    def page_input(self) -> typing.Optional[typing.List["OneDashboardRawPage"]]:
        return typing.cast(typing.Optional[typing.List["OneDashboardRawPage"]], jsii.get(self, "pageInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="permissionsInput")
    def permissions_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "permissionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: jsii.Number) -> None:
        jsii.set(self, "accountId", value)

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
    @jsii.member(jsii_name="page")
    def page(self) -> typing.List["OneDashboardRawPage"]:
        return typing.cast(typing.List["OneDashboardRawPage"], jsii.get(self, "page"))

    @page.setter
    def page(self, value: typing.List["OneDashboardRawPage"]) -> None:
        jsii.set(self, "page", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="permissions")
    def permissions(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "permissions"))

    @permissions.setter
    def permissions(self, value: builtins.str) -> None:
        jsii.set(self, "permissions", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.OneDashboardRawConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "page": "page",
        "account_id": "accountId",
        "description": "description",
        "permissions": "permissions",
    },
)
class OneDashboardRawConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        page: typing.Sequence["OneDashboardRawPage"],
        account_id: typing.Optional[jsii.Number] = None,
        description: typing.Optional[builtins.str] = None,
        permissions: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: The dashboard's name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard_raw#name OneDashboardRaw#name}
        :param page: page block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard_raw#page OneDashboardRaw#page}
        :param account_id: The New Relic account ID where you want to create the dashboard. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard_raw#account_id OneDashboardRaw#account_id}
        :param description: The dashboard's description. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard_raw#description OneDashboardRaw#description}
        :param permissions: Determines who can see or edit the dashboard. Valid values are private, public_read_only, public_read_write. Defaults to public_read_only. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard_raw#permissions OneDashboardRaw#permissions}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "page": page,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if account_id is not None:
            self._values["account_id"] = account_id
        if description is not None:
            self._values["description"] = description
        if permissions is not None:
            self._values["permissions"] = permissions

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
        '''The dashboard's name.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard_raw#name OneDashboardRaw#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def page(self) -> typing.List["OneDashboardRawPage"]:
        '''page block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard_raw#page OneDashboardRaw#page}
        '''
        result = self._values.get("page")
        assert result is not None, "Required property 'page' is missing"
        return typing.cast(typing.List["OneDashboardRawPage"], result)

    @builtins.property
    def account_id(self) -> typing.Optional[jsii.Number]:
        '''The New Relic account ID where you want to create the dashboard.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard_raw#account_id OneDashboardRaw#account_id}
        '''
        result = self._values.get("account_id")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''The dashboard's description.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard_raw#description OneDashboardRaw#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def permissions(self) -> typing.Optional[builtins.str]:
        '''Determines who can see or edit the dashboard. Valid values are private, public_read_only, public_read_write. Defaults to public_read_only.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard_raw#permissions OneDashboardRaw#permissions}
        '''
        result = self._values.get("permissions")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OneDashboardRawConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.OneDashboardRawPage",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "description": "description", "widget": "widget"},
)
class OneDashboardRawPage:
    def __init__(
        self,
        *,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        widget: typing.Optional[typing.Sequence["OneDashboardRawPageWidget"]] = None,
    ) -> None:
        '''
        :param name: The dashboard page's name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard_raw#name OneDashboardRaw#name}
        :param description: The dashboard page's description. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard_raw#description OneDashboardRaw#description}
        :param widget: widget block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard_raw#widget OneDashboardRaw#widget}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if description is not None:
            self._values["description"] = description
        if widget is not None:
            self._values["widget"] = widget

    @builtins.property
    def name(self) -> builtins.str:
        '''The dashboard page's name.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard_raw#name OneDashboardRaw#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''The dashboard page's description.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard_raw#description OneDashboardRaw#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def widget(self) -> typing.Optional[typing.List["OneDashboardRawPageWidget"]]:
        '''widget block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard_raw#widget OneDashboardRaw#widget}
        '''
        result = self._values.get("widget")
        return typing.cast(typing.Optional[typing.List["OneDashboardRawPageWidget"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OneDashboardRawPage(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.OneDashboardRawPageWidget",
    jsii_struct_bases=[],
    name_mapping={
        "column": "column",
        "configuration": "configuration",
        "row": "row",
        "title": "title",
        "visualization_id": "visualizationId",
        "height": "height",
        "linked_entity_guids": "linkedEntityGuids",
        "width": "width",
    },
)
class OneDashboardRawPageWidget:
    def __init__(
        self,
        *,
        column: jsii.Number,
        configuration: builtins.str,
        row: jsii.Number,
        title: builtins.str,
        visualization_id: builtins.str,
        height: typing.Optional[jsii.Number] = None,
        linked_entity_guids: typing.Optional[typing.Sequence[builtins.str]] = None,
        width: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param column: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard_raw#column OneDashboardRaw#column}.
        :param configuration: The configuration of the widget. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard_raw#configuration OneDashboardRaw#configuration}
        :param row: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard_raw#row OneDashboardRaw#row}.
        :param title: A title for the widget. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard_raw#title OneDashboardRaw#title}
        :param visualization_id: The visualization ID of the widget. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard_raw#visualization_id OneDashboardRaw#visualization_id}
        :param height: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard_raw#height OneDashboardRaw#height}.
        :param linked_entity_guids: (Optional) Related entity GUIDs. Currently only supports Dashboard entity GUIDs. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard_raw#linked_entity_guids OneDashboardRaw#linked_entity_guids}
        :param width: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard_raw#width OneDashboardRaw#width}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "column": column,
            "configuration": configuration,
            "row": row,
            "title": title,
            "visualization_id": visualization_id,
        }
        if height is not None:
            self._values["height"] = height
        if linked_entity_guids is not None:
            self._values["linked_entity_guids"] = linked_entity_guids
        if width is not None:
            self._values["width"] = width

    @builtins.property
    def column(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard_raw#column OneDashboardRaw#column}.'''
        result = self._values.get("column")
        assert result is not None, "Required property 'column' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def configuration(self) -> builtins.str:
        '''The configuration of the widget.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard_raw#configuration OneDashboardRaw#configuration}
        '''
        result = self._values.get("configuration")
        assert result is not None, "Required property 'configuration' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def row(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard_raw#row OneDashboardRaw#row}.'''
        result = self._values.get("row")
        assert result is not None, "Required property 'row' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def title(self) -> builtins.str:
        '''A title for the widget.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard_raw#title OneDashboardRaw#title}
        '''
        result = self._values.get("title")
        assert result is not None, "Required property 'title' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def visualization_id(self) -> builtins.str:
        '''The visualization ID of the widget.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard_raw#visualization_id OneDashboardRaw#visualization_id}
        '''
        result = self._values.get("visualization_id")
        assert result is not None, "Required property 'visualization_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def height(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard_raw#height OneDashboardRaw#height}.'''
        result = self._values.get("height")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def linked_entity_guids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(Optional) Related entity GUIDs. Currently only supports Dashboard entity GUIDs.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard_raw#linked_entity_guids OneDashboardRaw#linked_entity_guids}
        '''
        result = self._values.get("linked_entity_guids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def width(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/one_dashboard_raw#width OneDashboardRaw#width}.'''
        result = self._values.get("width")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OneDashboardRawPageWidget(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PluginsAlertCondition(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-newrelic.PluginsAlertCondition",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/newrelic/r/plugins_alert_condition newrelic_plugins_alert_condition}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        entities: typing.Sequence[jsii.Number],
        metric: builtins.str,
        metric_description: builtins.str,
        name: builtins.str,
        plugin_guid: builtins.str,
        plugin_id: builtins.str,
        policy_id: jsii.Number,
        term: typing.Sequence["PluginsAlertConditionTerm"],
        value_function: builtins.str,
        enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        runbook_url: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/newrelic/r/plugins_alert_condition newrelic_plugins_alert_condition} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param entities: The plugin component IDs to target. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/plugins_alert_condition#entities PluginsAlertCondition#entities}
        :param metric: The plugin metric to evaluate. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/plugins_alert_condition#metric PluginsAlertCondition#metric}
        :param metric_description: The metric description. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/plugins_alert_condition#metric_description PluginsAlertCondition#metric_description}
        :param name: The title of the condition. Must be between 1 and 64 characters, inclusive. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/plugins_alert_condition#name PluginsAlertCondition#name}
        :param plugin_guid: The GUID of the plugin which produces the metric. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/plugins_alert_condition#plugin_guid PluginsAlertCondition#plugin_guid}
        :param plugin_id: The ID of the installed plugin instance which produces the metric. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/plugins_alert_condition#plugin_id PluginsAlertCondition#plugin_id}
        :param policy_id: The ID of the policy where this condition should be used. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/plugins_alert_condition#policy_id PluginsAlertCondition#policy_id}
        :param term: term block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/plugins_alert_condition#term PluginsAlertCondition#term}
        :param value_function: The value function to apply to the metric data. One of ``min``, ``max``, ``average``, ``sample_size``, ``total``, or ``percent``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/plugins_alert_condition#value_function PluginsAlertCondition#value_function}
        :param enabled: Whether or not this condition is enabled. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/plugins_alert_condition#enabled PluginsAlertCondition#enabled}
        :param runbook_url: Runbook URL to display in notifications. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/plugins_alert_condition#runbook_url PluginsAlertCondition#runbook_url}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = PluginsAlertConditionConfig(
            entities=entities,
            metric=metric,
            metric_description=metric_description,
            name=name,
            plugin_guid=plugin_guid,
            plugin_id=plugin_id,
            policy_id=policy_id,
            term=term,
            value_function=value_function,
            enabled=enabled,
            runbook_url=runbook_url,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="resetRunbookUrl")
    def reset_runbook_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRunbookUrl", []))

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
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="entitiesInput")
    def entities_input(self) -> typing.Optional[typing.List[jsii.Number]]:
        return typing.cast(typing.Optional[typing.List[jsii.Number]], jsii.get(self, "entitiesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="metricDescriptionInput")
    def metric_description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "metricDescriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="metricInput")
    def metric_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "metricInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pluginGuidInput")
    def plugin_guid_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pluginGuidInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pluginIdInput")
    def plugin_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pluginIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyIdInput")
    def policy_id_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "policyIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="runbookUrlInput")
    def runbook_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "runbookUrlInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="termInput")
    def term_input(self) -> typing.Optional[typing.List["PluginsAlertConditionTerm"]]:
        return typing.cast(typing.Optional[typing.List["PluginsAlertConditionTerm"]], jsii.get(self, "termInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="valueFunctionInput")
    def value_function_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "valueFunctionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "enabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="entities")
    def entities(self) -> typing.List[jsii.Number]:
        return typing.cast(typing.List[jsii.Number], jsii.get(self, "entities"))

    @entities.setter
    def entities(self, value: typing.List[jsii.Number]) -> None:
        jsii.set(self, "entities", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="metric")
    def metric(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "metric"))

    @metric.setter
    def metric(self, value: builtins.str) -> None:
        jsii.set(self, "metric", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="metricDescription")
    def metric_description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "metricDescription"))

    @metric_description.setter
    def metric_description(self, value: builtins.str) -> None:
        jsii.set(self, "metricDescription", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pluginGuid")
    def plugin_guid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pluginGuid"))

    @plugin_guid.setter
    def plugin_guid(self, value: builtins.str) -> None:
        jsii.set(self, "pluginGuid", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pluginId")
    def plugin_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pluginId"))

    @plugin_id.setter
    def plugin_id(self, value: builtins.str) -> None:
        jsii.set(self, "pluginId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyId")
    def policy_id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "policyId"))

    @policy_id.setter
    def policy_id(self, value: jsii.Number) -> None:
        jsii.set(self, "policyId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="runbookUrl")
    def runbook_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "runbookUrl"))

    @runbook_url.setter
    def runbook_url(self, value: builtins.str) -> None:
        jsii.set(self, "runbookUrl", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="term")
    def term(self) -> typing.List["PluginsAlertConditionTerm"]:
        return typing.cast(typing.List["PluginsAlertConditionTerm"], jsii.get(self, "term"))

    @term.setter
    def term(self, value: typing.List["PluginsAlertConditionTerm"]) -> None:
        jsii.set(self, "term", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="valueFunction")
    def value_function(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "valueFunction"))

    @value_function.setter
    def value_function(self, value: builtins.str) -> None:
        jsii.set(self, "valueFunction", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.PluginsAlertConditionConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "entities": "entities",
        "metric": "metric",
        "metric_description": "metricDescription",
        "name": "name",
        "plugin_guid": "pluginGuid",
        "plugin_id": "pluginId",
        "policy_id": "policyId",
        "term": "term",
        "value_function": "valueFunction",
        "enabled": "enabled",
        "runbook_url": "runbookUrl",
    },
)
class PluginsAlertConditionConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        entities: typing.Sequence[jsii.Number],
        metric: builtins.str,
        metric_description: builtins.str,
        name: builtins.str,
        plugin_guid: builtins.str,
        plugin_id: builtins.str,
        policy_id: jsii.Number,
        term: typing.Sequence["PluginsAlertConditionTerm"],
        value_function: builtins.str,
        enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        runbook_url: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param entities: The plugin component IDs to target. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/plugins_alert_condition#entities PluginsAlertCondition#entities}
        :param metric: The plugin metric to evaluate. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/plugins_alert_condition#metric PluginsAlertCondition#metric}
        :param metric_description: The metric description. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/plugins_alert_condition#metric_description PluginsAlertCondition#metric_description}
        :param name: The title of the condition. Must be between 1 and 64 characters, inclusive. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/plugins_alert_condition#name PluginsAlertCondition#name}
        :param plugin_guid: The GUID of the plugin which produces the metric. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/plugins_alert_condition#plugin_guid PluginsAlertCondition#plugin_guid}
        :param plugin_id: The ID of the installed plugin instance which produces the metric. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/plugins_alert_condition#plugin_id PluginsAlertCondition#plugin_id}
        :param policy_id: The ID of the policy where this condition should be used. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/plugins_alert_condition#policy_id PluginsAlertCondition#policy_id}
        :param term: term block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/plugins_alert_condition#term PluginsAlertCondition#term}
        :param value_function: The value function to apply to the metric data. One of ``min``, ``max``, ``average``, ``sample_size``, ``total``, or ``percent``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/plugins_alert_condition#value_function PluginsAlertCondition#value_function}
        :param enabled: Whether or not this condition is enabled. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/plugins_alert_condition#enabled PluginsAlertCondition#enabled}
        :param runbook_url: Runbook URL to display in notifications. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/plugins_alert_condition#runbook_url PluginsAlertCondition#runbook_url}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "entities": entities,
            "metric": metric,
            "metric_description": metric_description,
            "name": name,
            "plugin_guid": plugin_guid,
            "plugin_id": plugin_id,
            "policy_id": policy_id,
            "term": term,
            "value_function": value_function,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if enabled is not None:
            self._values["enabled"] = enabled
        if runbook_url is not None:
            self._values["runbook_url"] = runbook_url

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
    def entities(self) -> typing.List[jsii.Number]:
        '''The plugin component IDs to target.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/plugins_alert_condition#entities PluginsAlertCondition#entities}
        '''
        result = self._values.get("entities")
        assert result is not None, "Required property 'entities' is missing"
        return typing.cast(typing.List[jsii.Number], result)

    @builtins.property
    def metric(self) -> builtins.str:
        '''The plugin metric to evaluate.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/plugins_alert_condition#metric PluginsAlertCondition#metric}
        '''
        result = self._values.get("metric")
        assert result is not None, "Required property 'metric' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def metric_description(self) -> builtins.str:
        '''The metric description.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/plugins_alert_condition#metric_description PluginsAlertCondition#metric_description}
        '''
        result = self._values.get("metric_description")
        assert result is not None, "Required property 'metric_description' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The title of the condition. Must be between 1 and 64 characters, inclusive.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/plugins_alert_condition#name PluginsAlertCondition#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def plugin_guid(self) -> builtins.str:
        '''The GUID of the plugin which produces the metric.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/plugins_alert_condition#plugin_guid PluginsAlertCondition#plugin_guid}
        '''
        result = self._values.get("plugin_guid")
        assert result is not None, "Required property 'plugin_guid' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def plugin_id(self) -> builtins.str:
        '''The ID of the installed plugin instance which produces the metric.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/plugins_alert_condition#plugin_id PluginsAlertCondition#plugin_id}
        '''
        result = self._values.get("plugin_id")
        assert result is not None, "Required property 'plugin_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def policy_id(self) -> jsii.Number:
        '''The ID of the policy where this condition should be used.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/plugins_alert_condition#policy_id PluginsAlertCondition#policy_id}
        '''
        result = self._values.get("policy_id")
        assert result is not None, "Required property 'policy_id' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def term(self) -> typing.List["PluginsAlertConditionTerm"]:
        '''term block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/plugins_alert_condition#term PluginsAlertCondition#term}
        '''
        result = self._values.get("term")
        assert result is not None, "Required property 'term' is missing"
        return typing.cast(typing.List["PluginsAlertConditionTerm"], result)

    @builtins.property
    def value_function(self) -> builtins.str:
        '''The value function to apply to the metric data.  One of ``min``, ``max``, ``average``, ``sample_size``, ``total``, or ``percent``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/plugins_alert_condition#value_function PluginsAlertCondition#value_function}
        '''
        result = self._values.get("value_function")
        assert result is not None, "Required property 'value_function' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Whether or not this condition is enabled.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/plugins_alert_condition#enabled PluginsAlertCondition#enabled}
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def runbook_url(self) -> typing.Optional[builtins.str]:
        '''Runbook URL to display in notifications.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/plugins_alert_condition#runbook_url PluginsAlertCondition#runbook_url}
        '''
        result = self._values.get("runbook_url")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PluginsAlertConditionConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.PluginsAlertConditionTerm",
    jsii_struct_bases=[],
    name_mapping={
        "duration": "duration",
        "threshold": "threshold",
        "time_function": "timeFunction",
        "operator": "operator",
        "priority": "priority",
    },
)
class PluginsAlertConditionTerm:
    def __init__(
        self,
        *,
        duration: jsii.Number,
        threshold: jsii.Number,
        time_function: builtins.str,
        operator: typing.Optional[builtins.str] = None,
        priority: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param duration: In minutes, must be in the range of 5 to 120, inclusive. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/plugins_alert_condition#duration PluginsAlertCondition#duration}
        :param threshold: Must be 0 or greater. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/plugins_alert_condition#threshold PluginsAlertCondition#threshold}
        :param time_function: One of ``all`` or ``any``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/plugins_alert_condition#time_function PluginsAlertCondition#time_function}
        :param operator: One of ``above``, ``below``, or ``equal``. Defaults to equal. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/plugins_alert_condition#operator PluginsAlertCondition#operator}
        :param priority: One of ``critical`` or ``warning``. Defaults to critical. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/plugins_alert_condition#priority PluginsAlertCondition#priority}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "duration": duration,
            "threshold": threshold,
            "time_function": time_function,
        }
        if operator is not None:
            self._values["operator"] = operator
        if priority is not None:
            self._values["priority"] = priority

    @builtins.property
    def duration(self) -> jsii.Number:
        '''In minutes, must be in the range of 5 to 120, inclusive.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/plugins_alert_condition#duration PluginsAlertCondition#duration}
        '''
        result = self._values.get("duration")
        assert result is not None, "Required property 'duration' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def threshold(self) -> jsii.Number:
        '''Must be 0 or greater.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/plugins_alert_condition#threshold PluginsAlertCondition#threshold}
        '''
        result = self._values.get("threshold")
        assert result is not None, "Required property 'threshold' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def time_function(self) -> builtins.str:
        '''One of ``all`` or ``any``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/plugins_alert_condition#time_function PluginsAlertCondition#time_function}
        '''
        result = self._values.get("time_function")
        assert result is not None, "Required property 'time_function' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def operator(self) -> typing.Optional[builtins.str]:
        '''One of ``above``, ``below``, or ``equal``. Defaults to equal.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/plugins_alert_condition#operator PluginsAlertCondition#operator}
        '''
        result = self._values.get("operator")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def priority(self) -> typing.Optional[builtins.str]:
        '''One of ``critical`` or ``warning``. Defaults to critical.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/plugins_alert_condition#priority PluginsAlertCondition#priority}
        '''
        result = self._values.get("priority")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PluginsAlertConditionTerm(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ServiceLevel(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-newrelic.ServiceLevel",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/newrelic/r/service_level newrelic_service_level}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        events: "ServiceLevelEvents",
        guid: builtins.str,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        objective: typing.Optional[typing.Sequence["ServiceLevelObjective"]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/newrelic/r/service_level newrelic_service_level} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param events: events block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/service_level#events ServiceLevel#events}
        :param guid: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/service_level#guid ServiceLevel#guid}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/service_level#name ServiceLevel#name}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/service_level#description ServiceLevel#description}.
        :param objective: objective block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/service_level#objective ServiceLevel#objective}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ServiceLevelConfig(
            events=events,
            guid=guid,
            name=name,
            description=description,
            objective=objective,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putEvents")
    def put_events(
        self,
        *,
        account_id: jsii.Number,
        valid_events: "ServiceLevelEventsValidEvents",
        bad_events: typing.Optional["ServiceLevelEventsBadEvents"] = None,
        good_events: typing.Optional["ServiceLevelEventsGoodEvents"] = None,
    ) -> None:
        '''
        :param account_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/service_level#account_id ServiceLevel#account_id}.
        :param valid_events: valid_events block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/service_level#valid_events ServiceLevel#valid_events}
        :param bad_events: bad_events block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/service_level#bad_events ServiceLevel#bad_events}
        :param good_events: good_events block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/service_level#good_events ServiceLevel#good_events}
        '''
        value = ServiceLevelEvents(
            account_id=account_id,
            valid_events=valid_events,
            bad_events=bad_events,
            good_events=good_events,
        )

        return typing.cast(None, jsii.invoke(self, "putEvents", [value]))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetObjective")
    def reset_objective(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetObjective", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="events")
    def events(self) -> "ServiceLevelEventsOutputReference":
        return typing.cast("ServiceLevelEventsOutputReference", jsii.get(self, "events"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sliId")
    def sli_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sliId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="eventsInput")
    def events_input(self) -> typing.Optional["ServiceLevelEvents"]:
        return typing.cast(typing.Optional["ServiceLevelEvents"], jsii.get(self, "eventsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="guidInput")
    def guid_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "guidInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="objectiveInput")
    def objective_input(self) -> typing.Optional[typing.List["ServiceLevelObjective"]]:
        return typing.cast(typing.Optional[typing.List["ServiceLevelObjective"]], jsii.get(self, "objectiveInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="guid")
    def guid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "guid"))

    @guid.setter
    def guid(self, value: builtins.str) -> None:
        jsii.set(self, "guid", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="objective")
    def objective(self) -> typing.List["ServiceLevelObjective"]:
        return typing.cast(typing.List["ServiceLevelObjective"], jsii.get(self, "objective"))

    @objective.setter
    def objective(self, value: typing.List["ServiceLevelObjective"]) -> None:
        jsii.set(self, "objective", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.ServiceLevelConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "events": "events",
        "guid": "guid",
        "name": "name",
        "description": "description",
        "objective": "objective",
    },
)
class ServiceLevelConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        events: "ServiceLevelEvents",
        guid: builtins.str,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        objective: typing.Optional[typing.Sequence["ServiceLevelObjective"]] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param events: events block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/service_level#events ServiceLevel#events}
        :param guid: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/service_level#guid ServiceLevel#guid}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/service_level#name ServiceLevel#name}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/service_level#description ServiceLevel#description}.
        :param objective: objective block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/service_level#objective ServiceLevel#objective}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(events, dict):
            events = ServiceLevelEvents(**events)
        self._values: typing.Dict[str, typing.Any] = {
            "events": events,
            "guid": guid,
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
        if objective is not None:
            self._values["objective"] = objective

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
    def events(self) -> "ServiceLevelEvents":
        '''events block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/service_level#events ServiceLevel#events}
        '''
        result = self._values.get("events")
        assert result is not None, "Required property 'events' is missing"
        return typing.cast("ServiceLevelEvents", result)

    @builtins.property
    def guid(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/service_level#guid ServiceLevel#guid}.'''
        result = self._values.get("guid")
        assert result is not None, "Required property 'guid' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/service_level#name ServiceLevel#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/service_level#description ServiceLevel#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def objective(self) -> typing.Optional[typing.List["ServiceLevelObjective"]]:
        '''objective block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/service_level#objective ServiceLevel#objective}
        '''
        result = self._values.get("objective")
        return typing.cast(typing.Optional[typing.List["ServiceLevelObjective"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceLevelConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.ServiceLevelEvents",
    jsii_struct_bases=[],
    name_mapping={
        "account_id": "accountId",
        "valid_events": "validEvents",
        "bad_events": "badEvents",
        "good_events": "goodEvents",
    },
)
class ServiceLevelEvents:
    def __init__(
        self,
        *,
        account_id: jsii.Number,
        valid_events: "ServiceLevelEventsValidEvents",
        bad_events: typing.Optional["ServiceLevelEventsBadEvents"] = None,
        good_events: typing.Optional["ServiceLevelEventsGoodEvents"] = None,
    ) -> None:
        '''
        :param account_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/service_level#account_id ServiceLevel#account_id}.
        :param valid_events: valid_events block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/service_level#valid_events ServiceLevel#valid_events}
        :param bad_events: bad_events block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/service_level#bad_events ServiceLevel#bad_events}
        :param good_events: good_events block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/service_level#good_events ServiceLevel#good_events}
        '''
        if isinstance(valid_events, dict):
            valid_events = ServiceLevelEventsValidEvents(**valid_events)
        if isinstance(bad_events, dict):
            bad_events = ServiceLevelEventsBadEvents(**bad_events)
        if isinstance(good_events, dict):
            good_events = ServiceLevelEventsGoodEvents(**good_events)
        self._values: typing.Dict[str, typing.Any] = {
            "account_id": account_id,
            "valid_events": valid_events,
        }
        if bad_events is not None:
            self._values["bad_events"] = bad_events
        if good_events is not None:
            self._values["good_events"] = good_events

    @builtins.property
    def account_id(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/service_level#account_id ServiceLevel#account_id}.'''
        result = self._values.get("account_id")
        assert result is not None, "Required property 'account_id' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def valid_events(self) -> "ServiceLevelEventsValidEvents":
        '''valid_events block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/service_level#valid_events ServiceLevel#valid_events}
        '''
        result = self._values.get("valid_events")
        assert result is not None, "Required property 'valid_events' is missing"
        return typing.cast("ServiceLevelEventsValidEvents", result)

    @builtins.property
    def bad_events(self) -> typing.Optional["ServiceLevelEventsBadEvents"]:
        '''bad_events block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/service_level#bad_events ServiceLevel#bad_events}
        '''
        result = self._values.get("bad_events")
        return typing.cast(typing.Optional["ServiceLevelEventsBadEvents"], result)

    @builtins.property
    def good_events(self) -> typing.Optional["ServiceLevelEventsGoodEvents"]:
        '''good_events block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/service_level#good_events ServiceLevel#good_events}
        '''
        result = self._values.get("good_events")
        return typing.cast(typing.Optional["ServiceLevelEventsGoodEvents"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceLevelEvents(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.ServiceLevelEventsBadEvents",
    jsii_struct_bases=[],
    name_mapping={"from_": "from", "where": "where"},
)
class ServiceLevelEventsBadEvents:
    def __init__(
        self,
        *,
        from_: builtins.str,
        where: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param from_: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/service_level#from ServiceLevel#from}.
        :param where: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/service_level#where ServiceLevel#where}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "from_": from_,
        }
        if where is not None:
            self._values["where"] = where

    @builtins.property
    def from_(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/service_level#from ServiceLevel#from}.'''
        result = self._values.get("from_")
        assert result is not None, "Required property 'from_' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def where(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/service_level#where ServiceLevel#where}.'''
        result = self._values.get("where")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceLevelEventsBadEvents(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ServiceLevelEventsBadEventsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-newrelic.ServiceLevelEventsBadEventsOutputReference",
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

    @jsii.member(jsii_name="resetWhere")
    def reset_where(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWhere", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fromInput")
    def from_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fromInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="whereInput")
    def where_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "whereInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="from")
    def from_(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "from"))

    @from_.setter
    def from_(self, value: builtins.str) -> None:
        jsii.set(self, "from", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="where")
    def where(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "where"))

    @where.setter
    def where(self, value: builtins.str) -> None:
        jsii.set(self, "where", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ServiceLevelEventsBadEvents]:
        return typing.cast(typing.Optional[ServiceLevelEventsBadEvents], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ServiceLevelEventsBadEvents],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.ServiceLevelEventsGoodEvents",
    jsii_struct_bases=[],
    name_mapping={"from_": "from", "where": "where"},
)
class ServiceLevelEventsGoodEvents:
    def __init__(
        self,
        *,
        from_: builtins.str,
        where: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param from_: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/service_level#from ServiceLevel#from}.
        :param where: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/service_level#where ServiceLevel#where}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "from_": from_,
        }
        if where is not None:
            self._values["where"] = where

    @builtins.property
    def from_(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/service_level#from ServiceLevel#from}.'''
        result = self._values.get("from_")
        assert result is not None, "Required property 'from_' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def where(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/service_level#where ServiceLevel#where}.'''
        result = self._values.get("where")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceLevelEventsGoodEvents(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ServiceLevelEventsGoodEventsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-newrelic.ServiceLevelEventsGoodEventsOutputReference",
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

    @jsii.member(jsii_name="resetWhere")
    def reset_where(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWhere", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fromInput")
    def from_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fromInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="whereInput")
    def where_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "whereInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="from")
    def from_(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "from"))

    @from_.setter
    def from_(self, value: builtins.str) -> None:
        jsii.set(self, "from", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="where")
    def where(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "where"))

    @where.setter
    def where(self, value: builtins.str) -> None:
        jsii.set(self, "where", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ServiceLevelEventsGoodEvents]:
        return typing.cast(typing.Optional[ServiceLevelEventsGoodEvents], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ServiceLevelEventsGoodEvents],
    ) -> None:
        jsii.set(self, "internalValue", value)


class ServiceLevelEventsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-newrelic.ServiceLevelEventsOutputReference",
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

    @jsii.member(jsii_name="putBadEvents")
    def put_bad_events(
        self,
        *,
        from_: builtins.str,
        where: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param from_: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/service_level#from ServiceLevel#from}.
        :param where: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/service_level#where ServiceLevel#where}.
        '''
        value = ServiceLevelEventsBadEvents(from_=from_, where=where)

        return typing.cast(None, jsii.invoke(self, "putBadEvents", [value]))

    @jsii.member(jsii_name="putGoodEvents")
    def put_good_events(
        self,
        *,
        from_: builtins.str,
        where: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param from_: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/service_level#from ServiceLevel#from}.
        :param where: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/service_level#where ServiceLevel#where}.
        '''
        value = ServiceLevelEventsGoodEvents(from_=from_, where=where)

        return typing.cast(None, jsii.invoke(self, "putGoodEvents", [value]))

    @jsii.member(jsii_name="putValidEvents")
    def put_valid_events(
        self,
        *,
        from_: builtins.str,
        where: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param from_: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/service_level#from ServiceLevel#from}.
        :param where: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/service_level#where ServiceLevel#where}.
        '''
        value = ServiceLevelEventsValidEvents(from_=from_, where=where)

        return typing.cast(None, jsii.invoke(self, "putValidEvents", [value]))

    @jsii.member(jsii_name="resetBadEvents")
    def reset_bad_events(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBadEvents", []))

    @jsii.member(jsii_name="resetGoodEvents")
    def reset_good_events(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGoodEvents", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="badEvents")
    def bad_events(self) -> ServiceLevelEventsBadEventsOutputReference:
        return typing.cast(ServiceLevelEventsBadEventsOutputReference, jsii.get(self, "badEvents"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="goodEvents")
    def good_events(self) -> ServiceLevelEventsGoodEventsOutputReference:
        return typing.cast(ServiceLevelEventsGoodEventsOutputReference, jsii.get(self, "goodEvents"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="validEvents")
    def valid_events(self) -> "ServiceLevelEventsValidEventsOutputReference":
        return typing.cast("ServiceLevelEventsValidEventsOutputReference", jsii.get(self, "validEvents"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "accountIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="badEventsInput")
    def bad_events_input(self) -> typing.Optional[ServiceLevelEventsBadEvents]:
        return typing.cast(typing.Optional[ServiceLevelEventsBadEvents], jsii.get(self, "badEventsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="goodEventsInput")
    def good_events_input(self) -> typing.Optional[ServiceLevelEventsGoodEvents]:
        return typing.cast(typing.Optional[ServiceLevelEventsGoodEvents], jsii.get(self, "goodEventsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="validEventsInput")
    def valid_events_input(self) -> typing.Optional["ServiceLevelEventsValidEvents"]:
        return typing.cast(typing.Optional["ServiceLevelEventsValidEvents"], jsii.get(self, "validEventsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: jsii.Number) -> None:
        jsii.set(self, "accountId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ServiceLevelEvents]:
        return typing.cast(typing.Optional[ServiceLevelEvents], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[ServiceLevelEvents]) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.ServiceLevelEventsValidEvents",
    jsii_struct_bases=[],
    name_mapping={"from_": "from", "where": "where"},
)
class ServiceLevelEventsValidEvents:
    def __init__(
        self,
        *,
        from_: builtins.str,
        where: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param from_: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/service_level#from ServiceLevel#from}.
        :param where: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/service_level#where ServiceLevel#where}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "from_": from_,
        }
        if where is not None:
            self._values["where"] = where

    @builtins.property
    def from_(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/service_level#from ServiceLevel#from}.'''
        result = self._values.get("from_")
        assert result is not None, "Required property 'from_' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def where(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/service_level#where ServiceLevel#where}.'''
        result = self._values.get("where")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceLevelEventsValidEvents(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ServiceLevelEventsValidEventsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-newrelic.ServiceLevelEventsValidEventsOutputReference",
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

    @jsii.member(jsii_name="resetWhere")
    def reset_where(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWhere", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fromInput")
    def from_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fromInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="whereInput")
    def where_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "whereInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="from")
    def from_(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "from"))

    @from_.setter
    def from_(self, value: builtins.str) -> None:
        jsii.set(self, "from", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="where")
    def where(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "where"))

    @where.setter
    def where(self, value: builtins.str) -> None:
        jsii.set(self, "where", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ServiceLevelEventsValidEvents]:
        return typing.cast(typing.Optional[ServiceLevelEventsValidEvents], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ServiceLevelEventsValidEvents],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.ServiceLevelObjective",
    jsii_struct_bases=[],
    name_mapping={
        "target": "target",
        "time_window": "timeWindow",
        "description": "description",
        "name": "name",
    },
)
class ServiceLevelObjective:
    def __init__(
        self,
        *,
        target: jsii.Number,
        time_window: "ServiceLevelObjectiveTimeWindow",
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param target: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/service_level#target ServiceLevel#target}.
        :param time_window: time_window block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/service_level#time_window ServiceLevel#time_window}
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/service_level#description ServiceLevel#description}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/service_level#name ServiceLevel#name}.
        '''
        if isinstance(time_window, dict):
            time_window = ServiceLevelObjectiveTimeWindow(**time_window)
        self._values: typing.Dict[str, typing.Any] = {
            "target": target,
            "time_window": time_window,
        }
        if description is not None:
            self._values["description"] = description
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def target(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/service_level#target ServiceLevel#target}.'''
        result = self._values.get("target")
        assert result is not None, "Required property 'target' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def time_window(self) -> "ServiceLevelObjectiveTimeWindow":
        '''time_window block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/service_level#time_window ServiceLevel#time_window}
        '''
        result = self._values.get("time_window")
        assert result is not None, "Required property 'time_window' is missing"
        return typing.cast("ServiceLevelObjectiveTimeWindow", result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/service_level#description ServiceLevel#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/service_level#name ServiceLevel#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceLevelObjective(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.ServiceLevelObjectiveTimeWindow",
    jsii_struct_bases=[],
    name_mapping={"rolling": "rolling"},
)
class ServiceLevelObjectiveTimeWindow:
    def __init__(self, *, rolling: "ServiceLevelObjectiveTimeWindowRolling") -> None:
        '''
        :param rolling: rolling block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/service_level#rolling ServiceLevel#rolling}
        '''
        if isinstance(rolling, dict):
            rolling = ServiceLevelObjectiveTimeWindowRolling(**rolling)
        self._values: typing.Dict[str, typing.Any] = {
            "rolling": rolling,
        }

    @builtins.property
    def rolling(self) -> "ServiceLevelObjectiveTimeWindowRolling":
        '''rolling block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/service_level#rolling ServiceLevel#rolling}
        '''
        result = self._values.get("rolling")
        assert result is not None, "Required property 'rolling' is missing"
        return typing.cast("ServiceLevelObjectiveTimeWindowRolling", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceLevelObjectiveTimeWindow(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ServiceLevelObjectiveTimeWindowOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-newrelic.ServiceLevelObjectiveTimeWindowOutputReference",
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

    @jsii.member(jsii_name="putRolling")
    def put_rolling(self, *, count: jsii.Number, unit: builtins.str) -> None:
        '''
        :param count: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/service_level#count ServiceLevel#count}.
        :param unit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/service_level#unit ServiceLevel#unit}.
        '''
        value = ServiceLevelObjectiveTimeWindowRolling(count=count, unit=unit)

        return typing.cast(None, jsii.invoke(self, "putRolling", [value]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rolling")
    def rolling(self) -> "ServiceLevelObjectiveTimeWindowRollingOutputReference":
        return typing.cast("ServiceLevelObjectiveTimeWindowRollingOutputReference", jsii.get(self, "rolling"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rollingInput")
    def rolling_input(
        self,
    ) -> typing.Optional["ServiceLevelObjectiveTimeWindowRolling"]:
        return typing.cast(typing.Optional["ServiceLevelObjectiveTimeWindowRolling"], jsii.get(self, "rollingInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ServiceLevelObjectiveTimeWindow]:
        return typing.cast(typing.Optional[ServiceLevelObjectiveTimeWindow], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ServiceLevelObjectiveTimeWindow],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.ServiceLevelObjectiveTimeWindowRolling",
    jsii_struct_bases=[],
    name_mapping={"count": "count", "unit": "unit"},
)
class ServiceLevelObjectiveTimeWindowRolling:
    def __init__(self, *, count: jsii.Number, unit: builtins.str) -> None:
        '''
        :param count: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/service_level#count ServiceLevel#count}.
        :param unit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/service_level#unit ServiceLevel#unit}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "count": count,
            "unit": unit,
        }

    @builtins.property
    def count(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/service_level#count ServiceLevel#count}.'''
        result = self._values.get("count")
        assert result is not None, "Required property 'count' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def unit(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/service_level#unit ServiceLevel#unit}.'''
        result = self._values.get("unit")
        assert result is not None, "Required property 'unit' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceLevelObjectiveTimeWindowRolling(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ServiceLevelObjectiveTimeWindowRollingOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-newrelic.ServiceLevelObjectiveTimeWindowRollingOutputReference",
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
    @jsii.member(jsii_name="countInput")
    def count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "countInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="unitInput")
    def unit_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "unitInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="count")
    def count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "count"))

    @count.setter
    def count(self, value: jsii.Number) -> None:
        jsii.set(self, "count", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="unit")
    def unit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "unit"))

    @unit.setter
    def unit(self, value: builtins.str) -> None:
        jsii.set(self, "unit", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ServiceLevelObjectiveTimeWindowRolling]:
        return typing.cast(typing.Optional[ServiceLevelObjectiveTimeWindowRolling], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ServiceLevelObjectiveTimeWindowRolling],
    ) -> None:
        jsii.set(self, "internalValue", value)


class SyntheticsAlertCondition(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-newrelic.SyntheticsAlertCondition",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_alert_condition newrelic_synthetics_alert_condition}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        monitor_id: builtins.str,
        name: builtins.str,
        policy_id: jsii.Number,
        enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        runbook_url: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_alert_condition newrelic_synthetics_alert_condition} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param monitor_id: The ID of the Synthetics monitor to be referenced in the alert condition. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_alert_condition#monitor_id SyntheticsAlertCondition#monitor_id}
        :param name: The title of this condition. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_alert_condition#name SyntheticsAlertCondition#name}
        :param policy_id: The ID of the policy where this condition should be used. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_alert_condition#policy_id SyntheticsAlertCondition#policy_id}
        :param enabled: Set whether to enable the alert condition. Defaults to true. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_alert_condition#enabled SyntheticsAlertCondition#enabled}
        :param runbook_url: Runbook URL to display in notifications. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_alert_condition#runbook_url SyntheticsAlertCondition#runbook_url}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = SyntheticsAlertConditionConfig(
            monitor_id=monitor_id,
            name=name,
            policy_id=policy_id,
            enabled=enabled,
            runbook_url=runbook_url,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="resetRunbookUrl")
    def reset_runbook_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRunbookUrl", []))

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
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="monitorIdInput")
    def monitor_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "monitorIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyIdInput")
    def policy_id_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "policyIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="runbookUrlInput")
    def runbook_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "runbookUrlInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "enabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="monitorId")
    def monitor_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "monitorId"))

    @monitor_id.setter
    def monitor_id(self, value: builtins.str) -> None:
        jsii.set(self, "monitorId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyId")
    def policy_id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "policyId"))

    @policy_id.setter
    def policy_id(self, value: jsii.Number) -> None:
        jsii.set(self, "policyId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="runbookUrl")
    def runbook_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "runbookUrl"))

    @runbook_url.setter
    def runbook_url(self, value: builtins.str) -> None:
        jsii.set(self, "runbookUrl", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.SyntheticsAlertConditionConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "monitor_id": "monitorId",
        "name": "name",
        "policy_id": "policyId",
        "enabled": "enabled",
        "runbook_url": "runbookUrl",
    },
)
class SyntheticsAlertConditionConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        monitor_id: builtins.str,
        name: builtins.str,
        policy_id: jsii.Number,
        enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        runbook_url: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param monitor_id: The ID of the Synthetics monitor to be referenced in the alert condition. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_alert_condition#monitor_id SyntheticsAlertCondition#monitor_id}
        :param name: The title of this condition. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_alert_condition#name SyntheticsAlertCondition#name}
        :param policy_id: The ID of the policy where this condition should be used. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_alert_condition#policy_id SyntheticsAlertCondition#policy_id}
        :param enabled: Set whether to enable the alert condition. Defaults to true. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_alert_condition#enabled SyntheticsAlertCondition#enabled}
        :param runbook_url: Runbook URL to display in notifications. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_alert_condition#runbook_url SyntheticsAlertCondition#runbook_url}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "monitor_id": monitor_id,
            "name": name,
            "policy_id": policy_id,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if enabled is not None:
            self._values["enabled"] = enabled
        if runbook_url is not None:
            self._values["runbook_url"] = runbook_url

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
    def monitor_id(self) -> builtins.str:
        '''The ID of the Synthetics monitor to be referenced in the alert condition.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_alert_condition#monitor_id SyntheticsAlertCondition#monitor_id}
        '''
        result = self._values.get("monitor_id")
        assert result is not None, "Required property 'monitor_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The title of this condition.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_alert_condition#name SyntheticsAlertCondition#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def policy_id(self) -> jsii.Number:
        '''The ID of the policy where this condition should be used.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_alert_condition#policy_id SyntheticsAlertCondition#policy_id}
        '''
        result = self._values.get("policy_id")
        assert result is not None, "Required property 'policy_id' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Set whether to enable the alert condition. Defaults to true.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_alert_condition#enabled SyntheticsAlertCondition#enabled}
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def runbook_url(self) -> typing.Optional[builtins.str]:
        '''Runbook URL to display in notifications.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_alert_condition#runbook_url SyntheticsAlertCondition#runbook_url}
        '''
        result = self._values.get("runbook_url")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SyntheticsAlertConditionConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SyntheticsMonitor(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-newrelic.SyntheticsMonitor",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_monitor newrelic_synthetics_monitor}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        frequency: jsii.Number,
        locations: typing.Sequence[builtins.str],
        name: builtins.str,
        status: builtins.str,
        type: builtins.str,
        bypass_head_request: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        sla_threshold: typing.Optional[jsii.Number] = None,
        treat_redirect_as_failure: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        uri: typing.Optional[builtins.str] = None,
        validation_string: typing.Optional[builtins.str] = None,
        verify_ssl: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_monitor newrelic_synthetics_monitor} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param frequency: The interval (in minutes) at which this monitor should run. Valid values are 1, 5, 10, 15, 30, 60, 360, 720, or 1440. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_monitor#frequency SyntheticsMonitor#frequency}
        :param locations: The locations in which this monitor should be run. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_monitor#locations SyntheticsMonitor#locations}
        :param name: The title of this monitor. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_monitor#name SyntheticsMonitor#name}
        :param status: The monitor status (i.e. ENABLED, MUTED, DISABLED). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_monitor#status SyntheticsMonitor#status}
        :param type: The monitor type. Valid values are SIMPLE, BROWSER, SCRIPT_BROWSER, and SCRIPT_API. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_monitor#type SyntheticsMonitor#type}
        :param bypass_head_request: Bypass HEAD request. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_monitor#bypass_head_request SyntheticsMonitor#bypass_head_request}
        :param sla_threshold: The base threshold for the SLA report. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_monitor#sla_threshold SyntheticsMonitor#sla_threshold}
        :param treat_redirect_as_failure: Fail the monitor check if redirected. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_monitor#treat_redirect_as_failure SyntheticsMonitor#treat_redirect_as_failure}
        :param uri: The URI for the monitor to hit. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_monitor#uri SyntheticsMonitor#uri}
        :param validation_string: The string to validate against in the response. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_monitor#validation_string SyntheticsMonitor#validation_string}
        :param verify_ssl: Verify SSL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_monitor#verify_ssl SyntheticsMonitor#verify_ssl}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = SyntheticsMonitorConfig(
            frequency=frequency,
            locations=locations,
            name=name,
            status=status,
            type=type,
            bypass_head_request=bypass_head_request,
            sla_threshold=sla_threshold,
            treat_redirect_as_failure=treat_redirect_as_failure,
            uri=uri,
            validation_string=validation_string,
            verify_ssl=verify_ssl,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetBypassHeadRequest")
    def reset_bypass_head_request(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBypassHeadRequest", []))

    @jsii.member(jsii_name="resetSlaThreshold")
    def reset_sla_threshold(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSlaThreshold", []))

    @jsii.member(jsii_name="resetTreatRedirectAsFailure")
    def reset_treat_redirect_as_failure(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTreatRedirectAsFailure", []))

    @jsii.member(jsii_name="resetUri")
    def reset_uri(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUri", []))

    @jsii.member(jsii_name="resetValidationString")
    def reset_validation_string(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValidationString", []))

    @jsii.member(jsii_name="resetVerifySsl")
    def reset_verify_ssl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVerifySsl", []))

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
    @jsii.member(jsii_name="bypassHeadRequestInput")
    def bypass_head_request_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "bypassHeadRequestInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="frequencyInput")
    def frequency_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "frequencyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="locationsInput")
    def locations_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "locationsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="slaThresholdInput")
    def sla_threshold_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "slaThresholdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statusInput")
    def status_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "statusInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="treatRedirectAsFailureInput")
    def treat_redirect_as_failure_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "treatRedirectAsFailureInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="uriInput")
    def uri_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "uriInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="validationStringInput")
    def validation_string_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "validationStringInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="verifySslInput")
    def verify_ssl_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "verifySslInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bypassHeadRequest")
    def bypass_head_request(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "bypassHeadRequest"))

    @bypass_head_request.setter
    def bypass_head_request(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "bypassHeadRequest", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="frequency")
    def frequency(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "frequency"))

    @frequency.setter
    def frequency(self, value: jsii.Number) -> None:
        jsii.set(self, "frequency", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="locations")
    def locations(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "locations"))

    @locations.setter
    def locations(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "locations", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="slaThreshold")
    def sla_threshold(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "slaThreshold"))

    @sla_threshold.setter
    def sla_threshold(self, value: jsii.Number) -> None:
        jsii.set(self, "slaThreshold", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @status.setter
    def status(self, value: builtins.str) -> None:
        jsii.set(self, "status", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="treatRedirectAsFailure")
    def treat_redirect_as_failure(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "treatRedirectAsFailure"))

    @treat_redirect_as_failure.setter
    def treat_redirect_as_failure(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "treatRedirectAsFailure", value)

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

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="validationString")
    def validation_string(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "validationString"))

    @validation_string.setter
    def validation_string(self, value: builtins.str) -> None:
        jsii.set(self, "validationString", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="verifySsl")
    def verify_ssl(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "verifySsl"))

    @verify_ssl.setter
    def verify_ssl(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "verifySsl", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.SyntheticsMonitorConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "frequency": "frequency",
        "locations": "locations",
        "name": "name",
        "status": "status",
        "type": "type",
        "bypass_head_request": "bypassHeadRequest",
        "sla_threshold": "slaThreshold",
        "treat_redirect_as_failure": "treatRedirectAsFailure",
        "uri": "uri",
        "validation_string": "validationString",
        "verify_ssl": "verifySsl",
    },
)
class SyntheticsMonitorConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        frequency: jsii.Number,
        locations: typing.Sequence[builtins.str],
        name: builtins.str,
        status: builtins.str,
        type: builtins.str,
        bypass_head_request: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        sla_threshold: typing.Optional[jsii.Number] = None,
        treat_redirect_as_failure: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        uri: typing.Optional[builtins.str] = None,
        validation_string: typing.Optional[builtins.str] = None,
        verify_ssl: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param frequency: The interval (in minutes) at which this monitor should run. Valid values are 1, 5, 10, 15, 30, 60, 360, 720, or 1440. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_monitor#frequency SyntheticsMonitor#frequency}
        :param locations: The locations in which this monitor should be run. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_monitor#locations SyntheticsMonitor#locations}
        :param name: The title of this monitor. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_monitor#name SyntheticsMonitor#name}
        :param status: The monitor status (i.e. ENABLED, MUTED, DISABLED). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_monitor#status SyntheticsMonitor#status}
        :param type: The monitor type. Valid values are SIMPLE, BROWSER, SCRIPT_BROWSER, and SCRIPT_API. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_monitor#type SyntheticsMonitor#type}
        :param bypass_head_request: Bypass HEAD request. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_monitor#bypass_head_request SyntheticsMonitor#bypass_head_request}
        :param sla_threshold: The base threshold for the SLA report. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_monitor#sla_threshold SyntheticsMonitor#sla_threshold}
        :param treat_redirect_as_failure: Fail the monitor check if redirected. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_monitor#treat_redirect_as_failure SyntheticsMonitor#treat_redirect_as_failure}
        :param uri: The URI for the monitor to hit. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_monitor#uri SyntheticsMonitor#uri}
        :param validation_string: The string to validate against in the response. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_monitor#validation_string SyntheticsMonitor#validation_string}
        :param verify_ssl: Verify SSL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_monitor#verify_ssl SyntheticsMonitor#verify_ssl}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "frequency": frequency,
            "locations": locations,
            "name": name,
            "status": status,
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
        if bypass_head_request is not None:
            self._values["bypass_head_request"] = bypass_head_request
        if sla_threshold is not None:
            self._values["sla_threshold"] = sla_threshold
        if treat_redirect_as_failure is not None:
            self._values["treat_redirect_as_failure"] = treat_redirect_as_failure
        if uri is not None:
            self._values["uri"] = uri
        if validation_string is not None:
            self._values["validation_string"] = validation_string
        if verify_ssl is not None:
            self._values["verify_ssl"] = verify_ssl

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
    def frequency(self) -> jsii.Number:
        '''The interval (in minutes) at which this monitor should run.

        Valid values are 1, 5, 10, 15, 30, 60, 360, 720, or 1440.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_monitor#frequency SyntheticsMonitor#frequency}
        '''
        result = self._values.get("frequency")
        assert result is not None, "Required property 'frequency' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def locations(self) -> typing.List[builtins.str]:
        '''The locations in which this monitor should be run.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_monitor#locations SyntheticsMonitor#locations}
        '''
        result = self._values.get("locations")
        assert result is not None, "Required property 'locations' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The title of this monitor.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_monitor#name SyntheticsMonitor#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def status(self) -> builtins.str:
        '''The monitor status (i.e. ENABLED, MUTED, DISABLED).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_monitor#status SyntheticsMonitor#status}
        '''
        result = self._values.get("status")
        assert result is not None, "Required property 'status' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''The monitor type. Valid values are SIMPLE, BROWSER, SCRIPT_BROWSER, and SCRIPT_API.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_monitor#type SyntheticsMonitor#type}
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def bypass_head_request(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Bypass HEAD request.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_monitor#bypass_head_request SyntheticsMonitor#bypass_head_request}
        '''
        result = self._values.get("bypass_head_request")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def sla_threshold(self) -> typing.Optional[jsii.Number]:
        '''The base threshold for the SLA report.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_monitor#sla_threshold SyntheticsMonitor#sla_threshold}
        '''
        result = self._values.get("sla_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def treat_redirect_as_failure(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Fail the monitor check if redirected.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_monitor#treat_redirect_as_failure SyntheticsMonitor#treat_redirect_as_failure}
        '''
        result = self._values.get("treat_redirect_as_failure")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def uri(self) -> typing.Optional[builtins.str]:
        '''The URI for the monitor to hit.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_monitor#uri SyntheticsMonitor#uri}
        '''
        result = self._values.get("uri")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def validation_string(self) -> typing.Optional[builtins.str]:
        '''The string to validate against in the response.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_monitor#validation_string SyntheticsMonitor#validation_string}
        '''
        result = self._values.get("validation_string")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def verify_ssl(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Verify SSL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_monitor#verify_ssl SyntheticsMonitor#verify_ssl}
        '''
        result = self._values.get("verify_ssl")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SyntheticsMonitorConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SyntheticsMonitorScript(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-newrelic.SyntheticsMonitorScript",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_monitor_script newrelic_synthetics_monitor_script}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        monitor_id: builtins.str,
        text: builtins.str,
        location: typing.Optional[typing.Sequence["SyntheticsMonitorScriptLocation"]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_monitor_script newrelic_synthetics_monitor_script} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param monitor_id: The ID of the monitor to attach the script to. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_monitor_script#monitor_id SyntheticsMonitorScript#monitor_id}
        :param text: The plaintext representing the monitor script. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_monitor_script#text SyntheticsMonitorScript#text}
        :param location: location block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_monitor_script#location SyntheticsMonitorScript#location}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = SyntheticsMonitorScriptConfig(
            monitor_id=monitor_id,
            text=text,
            location=location,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetLocation")
    def reset_location(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLocation", []))

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
    @jsii.member(jsii_name="locationInput")
    def location_input(
        self,
    ) -> typing.Optional[typing.List["SyntheticsMonitorScriptLocation"]]:
        return typing.cast(typing.Optional[typing.List["SyntheticsMonitorScriptLocation"]], jsii.get(self, "locationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="monitorIdInput")
    def monitor_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "monitorIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="textInput")
    def text_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "textInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="location")
    def location(self) -> typing.List["SyntheticsMonitorScriptLocation"]:
        return typing.cast(typing.List["SyntheticsMonitorScriptLocation"], jsii.get(self, "location"))

    @location.setter
    def location(self, value: typing.List["SyntheticsMonitorScriptLocation"]) -> None:
        jsii.set(self, "location", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="monitorId")
    def monitor_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "monitorId"))

    @monitor_id.setter
    def monitor_id(self, value: builtins.str) -> None:
        jsii.set(self, "monitorId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="text")
    def text(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "text"))

    @text.setter
    def text(self, value: builtins.str) -> None:
        jsii.set(self, "text", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.SyntheticsMonitorScriptConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "monitor_id": "monitorId",
        "text": "text",
        "location": "location",
    },
)
class SyntheticsMonitorScriptConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        monitor_id: builtins.str,
        text: builtins.str,
        location: typing.Optional[typing.Sequence["SyntheticsMonitorScriptLocation"]] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param monitor_id: The ID of the monitor to attach the script to. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_monitor_script#monitor_id SyntheticsMonitorScript#monitor_id}
        :param text: The plaintext representing the monitor script. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_monitor_script#text SyntheticsMonitorScript#text}
        :param location: location block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_monitor_script#location SyntheticsMonitorScript#location}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "monitor_id": monitor_id,
            "text": text,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if location is not None:
            self._values["location"] = location

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
    def monitor_id(self) -> builtins.str:
        '''The ID of the monitor to attach the script to.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_monitor_script#monitor_id SyntheticsMonitorScript#monitor_id}
        '''
        result = self._values.get("monitor_id")
        assert result is not None, "Required property 'monitor_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def text(self) -> builtins.str:
        '''The plaintext representing the monitor script.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_monitor_script#text SyntheticsMonitorScript#text}
        '''
        result = self._values.get("text")
        assert result is not None, "Required property 'text' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def location(
        self,
    ) -> typing.Optional[typing.List["SyntheticsMonitorScriptLocation"]]:
        '''location block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_monitor_script#location SyntheticsMonitorScript#location}
        '''
        result = self._values.get("location")
        return typing.cast(typing.Optional[typing.List["SyntheticsMonitorScriptLocation"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SyntheticsMonitorScriptConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.SyntheticsMonitorScriptLocation",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "hmac": "hmac", "vse_password": "vsePassword"},
)
class SyntheticsMonitorScriptLocation:
    def __init__(
        self,
        *,
        name: builtins.str,
        hmac: typing.Optional[builtins.str] = None,
        vse_password: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param name: The monitor script location name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_monitor_script#name SyntheticsMonitorScript#name}
        :param hmac: The HMAC for the monitor script location. Use only one of ``hmac`` or ``vse_password.``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_monitor_script#hmac SyntheticsMonitorScript#hmac}
        :param vse_password: The password for the monitor script location used to calculate HMAC. Use only one of ``vse_password`` or ``hmac.``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_monitor_script#vse_password SyntheticsMonitorScript#vse_password}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if hmac is not None:
            self._values["hmac"] = hmac
        if vse_password is not None:
            self._values["vse_password"] = vse_password

    @builtins.property
    def name(self) -> builtins.str:
        '''The monitor script location name.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_monitor_script#name SyntheticsMonitorScript#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def hmac(self) -> typing.Optional[builtins.str]:
        '''The HMAC for the monitor script location. Use only one of ``hmac`` or ``vse_password.``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_monitor_script#hmac SyntheticsMonitorScript#hmac}
        '''
        result = self._values.get("hmac")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vse_password(self) -> typing.Optional[builtins.str]:
        '''The password for the monitor script location used to calculate HMAC. Use only one of ``vse_password`` or ``hmac.``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_monitor_script#vse_password SyntheticsMonitorScript#vse_password}
        '''
        result = self._values.get("vse_password")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SyntheticsMonitorScriptLocation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SyntheticsMultilocationAlertCondition(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-newrelic.SyntheticsMultilocationAlertCondition",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_multilocation_alert_condition newrelic_synthetics_multilocation_alert_condition}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        critical: "SyntheticsMultilocationAlertConditionCritical",
        entities: typing.Sequence[builtins.str],
        name: builtins.str,
        policy_id: jsii.Number,
        violation_time_limit_seconds: jsii.Number,
        enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        runbook_url: typing.Optional[builtins.str] = None,
        warning: typing.Optional["SyntheticsMultilocationAlertConditionWarning"] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_multilocation_alert_condition newrelic_synthetics_multilocation_alert_condition} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param critical: critical block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_multilocation_alert_condition#critical SyntheticsMultilocationAlertCondition#critical}
        :param entities: The GUIDs of the Synthetics monitors to alert on. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_multilocation_alert_condition#entities SyntheticsMultilocationAlertCondition#entities}
        :param name: The title of this condition. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_multilocation_alert_condition#name SyntheticsMultilocationAlertCondition#name}
        :param policy_id: The ID of the policy where this condition will be used. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_multilocation_alert_condition#policy_id SyntheticsMultilocationAlertCondition#policy_id}
        :param violation_time_limit_seconds: The maximum number of seconds a violation can remain open before being closed by the system. Must be one of: 0, 3600, 7200, 14400, 28800, 43200, 86400 Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_multilocation_alert_condition#violation_time_limit_seconds SyntheticsMultilocationAlertCondition#violation_time_limit_seconds}
        :param enabled: Set whether to enable the alert condition. Defaults to true. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_multilocation_alert_condition#enabled SyntheticsMultilocationAlertCondition#enabled}
        :param runbook_url: Runbook URL to display in notifications. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_multilocation_alert_condition#runbook_url SyntheticsMultilocationAlertCondition#runbook_url}
        :param warning: warning block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_multilocation_alert_condition#warning SyntheticsMultilocationAlertCondition#warning}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = SyntheticsMultilocationAlertConditionConfig(
            critical=critical,
            entities=entities,
            name=name,
            policy_id=policy_id,
            violation_time_limit_seconds=violation_time_limit_seconds,
            enabled=enabled,
            runbook_url=runbook_url,
            warning=warning,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putCritical")
    def put_critical(self, *, threshold: jsii.Number) -> None:
        '''
        :param threshold: The minimum number of monitor locations that must be concurrently failing before a violation is opened. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_multilocation_alert_condition#threshold SyntheticsMultilocationAlertCondition#threshold}
        '''
        value = SyntheticsMultilocationAlertConditionCritical(threshold=threshold)

        return typing.cast(None, jsii.invoke(self, "putCritical", [value]))

    @jsii.member(jsii_name="putWarning")
    def put_warning(self, *, threshold: jsii.Number) -> None:
        '''
        :param threshold: The minimum number of monitor locations that must be concurrently failing before a violation is opened. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_multilocation_alert_condition#threshold SyntheticsMultilocationAlertCondition#threshold}
        '''
        value = SyntheticsMultilocationAlertConditionWarning(threshold=threshold)

        return typing.cast(None, jsii.invoke(self, "putWarning", [value]))

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="resetRunbookUrl")
    def reset_runbook_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRunbookUrl", []))

    @jsii.member(jsii_name="resetWarning")
    def reset_warning(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWarning", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="critical")
    def critical(
        self,
    ) -> "SyntheticsMultilocationAlertConditionCriticalOutputReference":
        return typing.cast("SyntheticsMultilocationAlertConditionCriticalOutputReference", jsii.get(self, "critical"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="warning")
    def warning(self) -> "SyntheticsMultilocationAlertConditionWarningOutputReference":
        return typing.cast("SyntheticsMultilocationAlertConditionWarningOutputReference", jsii.get(self, "warning"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="criticalInput")
    def critical_input(
        self,
    ) -> typing.Optional["SyntheticsMultilocationAlertConditionCritical"]:
        return typing.cast(typing.Optional["SyntheticsMultilocationAlertConditionCritical"], jsii.get(self, "criticalInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="entitiesInput")
    def entities_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "entitiesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyIdInput")
    def policy_id_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "policyIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="runbookUrlInput")
    def runbook_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "runbookUrlInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="violationTimeLimitSecondsInput")
    def violation_time_limit_seconds_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "violationTimeLimitSecondsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="warningInput")
    def warning_input(
        self,
    ) -> typing.Optional["SyntheticsMultilocationAlertConditionWarning"]:
        return typing.cast(typing.Optional["SyntheticsMultilocationAlertConditionWarning"], jsii.get(self, "warningInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "enabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="entities")
    def entities(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "entities"))

    @entities.setter
    def entities(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "entities", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyId")
    def policy_id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "policyId"))

    @policy_id.setter
    def policy_id(self, value: jsii.Number) -> None:
        jsii.set(self, "policyId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="runbookUrl")
    def runbook_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "runbookUrl"))

    @runbook_url.setter
    def runbook_url(self, value: builtins.str) -> None:
        jsii.set(self, "runbookUrl", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="violationTimeLimitSeconds")
    def violation_time_limit_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "violationTimeLimitSeconds"))

    @violation_time_limit_seconds.setter
    def violation_time_limit_seconds(self, value: jsii.Number) -> None:
        jsii.set(self, "violationTimeLimitSeconds", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.SyntheticsMultilocationAlertConditionConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "critical": "critical",
        "entities": "entities",
        "name": "name",
        "policy_id": "policyId",
        "violation_time_limit_seconds": "violationTimeLimitSeconds",
        "enabled": "enabled",
        "runbook_url": "runbookUrl",
        "warning": "warning",
    },
)
class SyntheticsMultilocationAlertConditionConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        critical: "SyntheticsMultilocationAlertConditionCritical",
        entities: typing.Sequence[builtins.str],
        name: builtins.str,
        policy_id: jsii.Number,
        violation_time_limit_seconds: jsii.Number,
        enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        runbook_url: typing.Optional[builtins.str] = None,
        warning: typing.Optional["SyntheticsMultilocationAlertConditionWarning"] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param critical: critical block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_multilocation_alert_condition#critical SyntheticsMultilocationAlertCondition#critical}
        :param entities: The GUIDs of the Synthetics monitors to alert on. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_multilocation_alert_condition#entities SyntheticsMultilocationAlertCondition#entities}
        :param name: The title of this condition. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_multilocation_alert_condition#name SyntheticsMultilocationAlertCondition#name}
        :param policy_id: The ID of the policy where this condition will be used. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_multilocation_alert_condition#policy_id SyntheticsMultilocationAlertCondition#policy_id}
        :param violation_time_limit_seconds: The maximum number of seconds a violation can remain open before being closed by the system. Must be one of: 0, 3600, 7200, 14400, 28800, 43200, 86400 Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_multilocation_alert_condition#violation_time_limit_seconds SyntheticsMultilocationAlertCondition#violation_time_limit_seconds}
        :param enabled: Set whether to enable the alert condition. Defaults to true. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_multilocation_alert_condition#enabled SyntheticsMultilocationAlertCondition#enabled}
        :param runbook_url: Runbook URL to display in notifications. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_multilocation_alert_condition#runbook_url SyntheticsMultilocationAlertCondition#runbook_url}
        :param warning: warning block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_multilocation_alert_condition#warning SyntheticsMultilocationAlertCondition#warning}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(critical, dict):
            critical = SyntheticsMultilocationAlertConditionCritical(**critical)
        if isinstance(warning, dict):
            warning = SyntheticsMultilocationAlertConditionWarning(**warning)
        self._values: typing.Dict[str, typing.Any] = {
            "critical": critical,
            "entities": entities,
            "name": name,
            "policy_id": policy_id,
            "violation_time_limit_seconds": violation_time_limit_seconds,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if enabled is not None:
            self._values["enabled"] = enabled
        if runbook_url is not None:
            self._values["runbook_url"] = runbook_url
        if warning is not None:
            self._values["warning"] = warning

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
    def critical(self) -> "SyntheticsMultilocationAlertConditionCritical":
        '''critical block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_multilocation_alert_condition#critical SyntheticsMultilocationAlertCondition#critical}
        '''
        result = self._values.get("critical")
        assert result is not None, "Required property 'critical' is missing"
        return typing.cast("SyntheticsMultilocationAlertConditionCritical", result)

    @builtins.property
    def entities(self) -> typing.List[builtins.str]:
        '''The GUIDs of the Synthetics monitors to alert on.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_multilocation_alert_condition#entities SyntheticsMultilocationAlertCondition#entities}
        '''
        result = self._values.get("entities")
        assert result is not None, "Required property 'entities' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The title of this condition.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_multilocation_alert_condition#name SyntheticsMultilocationAlertCondition#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def policy_id(self) -> jsii.Number:
        '''The ID of the policy where this condition will be used.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_multilocation_alert_condition#policy_id SyntheticsMultilocationAlertCondition#policy_id}
        '''
        result = self._values.get("policy_id")
        assert result is not None, "Required property 'policy_id' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def violation_time_limit_seconds(self) -> jsii.Number:
        '''The maximum number of seconds a violation can remain open before being closed by the system.

        Must be one of: 0, 3600, 7200, 14400, 28800, 43200, 86400

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_multilocation_alert_condition#violation_time_limit_seconds SyntheticsMultilocationAlertCondition#violation_time_limit_seconds}
        '''
        result = self._values.get("violation_time_limit_seconds")
        assert result is not None, "Required property 'violation_time_limit_seconds' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Set whether to enable the alert condition. Defaults to true.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_multilocation_alert_condition#enabled SyntheticsMultilocationAlertCondition#enabled}
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def runbook_url(self) -> typing.Optional[builtins.str]:
        '''Runbook URL to display in notifications.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_multilocation_alert_condition#runbook_url SyntheticsMultilocationAlertCondition#runbook_url}
        '''
        result = self._values.get("runbook_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def warning(
        self,
    ) -> typing.Optional["SyntheticsMultilocationAlertConditionWarning"]:
        '''warning block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_multilocation_alert_condition#warning SyntheticsMultilocationAlertCondition#warning}
        '''
        result = self._values.get("warning")
        return typing.cast(typing.Optional["SyntheticsMultilocationAlertConditionWarning"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SyntheticsMultilocationAlertConditionConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.SyntheticsMultilocationAlertConditionCritical",
    jsii_struct_bases=[],
    name_mapping={"threshold": "threshold"},
)
class SyntheticsMultilocationAlertConditionCritical:
    def __init__(self, *, threshold: jsii.Number) -> None:
        '''
        :param threshold: The minimum number of monitor locations that must be concurrently failing before a violation is opened. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_multilocation_alert_condition#threshold SyntheticsMultilocationAlertCondition#threshold}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "threshold": threshold,
        }

    @builtins.property
    def threshold(self) -> jsii.Number:
        '''The minimum number of monitor locations that must be concurrently failing before a violation is opened.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_multilocation_alert_condition#threshold SyntheticsMultilocationAlertCondition#threshold}
        '''
        result = self._values.get("threshold")
        assert result is not None, "Required property 'threshold' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SyntheticsMultilocationAlertConditionCritical(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SyntheticsMultilocationAlertConditionCriticalOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-newrelic.SyntheticsMultilocationAlertConditionCriticalOutputReference",
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
    @jsii.member(jsii_name="thresholdInput")
    def threshold_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "thresholdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="threshold")
    def threshold(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "threshold"))

    @threshold.setter
    def threshold(self, value: jsii.Number) -> None:
        jsii.set(self, "threshold", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[SyntheticsMultilocationAlertConditionCritical]:
        return typing.cast(typing.Optional[SyntheticsMultilocationAlertConditionCritical], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[SyntheticsMultilocationAlertConditionCritical],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.SyntheticsMultilocationAlertConditionWarning",
    jsii_struct_bases=[],
    name_mapping={"threshold": "threshold"},
)
class SyntheticsMultilocationAlertConditionWarning:
    def __init__(self, *, threshold: jsii.Number) -> None:
        '''
        :param threshold: The minimum number of monitor locations that must be concurrently failing before a violation is opened. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_multilocation_alert_condition#threshold SyntheticsMultilocationAlertCondition#threshold}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "threshold": threshold,
        }

    @builtins.property
    def threshold(self) -> jsii.Number:
        '''The minimum number of monitor locations that must be concurrently failing before a violation is opened.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_multilocation_alert_condition#threshold SyntheticsMultilocationAlertCondition#threshold}
        '''
        result = self._values.get("threshold")
        assert result is not None, "Required property 'threshold' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SyntheticsMultilocationAlertConditionWarning(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SyntheticsMultilocationAlertConditionWarningOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-newrelic.SyntheticsMultilocationAlertConditionWarningOutputReference",
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
    @jsii.member(jsii_name="thresholdInput")
    def threshold_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "thresholdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="threshold")
    def threshold(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "threshold"))

    @threshold.setter
    def threshold(self, value: jsii.Number) -> None:
        jsii.set(self, "threshold", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[SyntheticsMultilocationAlertConditionWarning]:
        return typing.cast(typing.Optional[SyntheticsMultilocationAlertConditionWarning], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[SyntheticsMultilocationAlertConditionWarning],
    ) -> None:
        jsii.set(self, "internalValue", value)


class SyntheticsSecureCredential(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-newrelic.SyntheticsSecureCredential",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_secure_credential newrelic_synthetics_secure_credential}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        key: builtins.str,
        value: builtins.str,
        created_at: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        last_updated: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_secure_credential newrelic_synthetics_secure_credential} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param key: The secure credential's key name. Regardless of the case used in the configuration, the provider will provide an upcased key to the underlying API. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_secure_credential#key SyntheticsSecureCredential#key}
        :param value: The secure credential's value. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_secure_credential#value SyntheticsSecureCredential#value}
        :param created_at: The time the secure credential was created. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_secure_credential#created_at SyntheticsSecureCredential#created_at}
        :param description: The secure credential's description. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_secure_credential#description SyntheticsSecureCredential#description}
        :param last_updated: The time the secure credential was last updated. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_secure_credential#last_updated SyntheticsSecureCredential#last_updated}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = SyntheticsSecureCredentialConfig(
            key=key,
            value=value,
            created_at=created_at,
            description=description,
            last_updated=last_updated,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetCreatedAt")
    def reset_created_at(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreatedAt", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetLastUpdated")
    def reset_last_updated(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLastUpdated", []))

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
    @jsii.member(jsii_name="createdAtInput")
    def created_at_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createdAtInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyInput")
    def key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lastUpdatedInput")
    def last_updated_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "lastUpdatedInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "valueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdAt"))

    @created_at.setter
    def created_at(self, value: builtins.str) -> None:
        jsii.set(self, "createdAt", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        jsii.set(self, "key", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lastUpdated")
    def last_updated(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lastUpdated"))

    @last_updated.setter
    def last_updated(self, value: builtins.str) -> None:
        jsii.set(self, "lastUpdated", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        jsii.set(self, "value", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.SyntheticsSecureCredentialConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "key": "key",
        "value": "value",
        "created_at": "createdAt",
        "description": "description",
        "last_updated": "lastUpdated",
    },
)
class SyntheticsSecureCredentialConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        key: builtins.str,
        value: builtins.str,
        created_at: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        last_updated: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param key: The secure credential's key name. Regardless of the case used in the configuration, the provider will provide an upcased key to the underlying API. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_secure_credential#key SyntheticsSecureCredential#key}
        :param value: The secure credential's value. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_secure_credential#value SyntheticsSecureCredential#value}
        :param created_at: The time the secure credential was created. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_secure_credential#created_at SyntheticsSecureCredential#created_at}
        :param description: The secure credential's description. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_secure_credential#description SyntheticsSecureCredential#description}
        :param last_updated: The time the secure credential was last updated. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_secure_credential#last_updated SyntheticsSecureCredential#last_updated}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "key": key,
            "value": value,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if created_at is not None:
            self._values["created_at"] = created_at
        if description is not None:
            self._values["description"] = description
        if last_updated is not None:
            self._values["last_updated"] = last_updated

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
    def key(self) -> builtins.str:
        '''The secure credential's key name.

        Regardless of the case used in the configuration, the provider will provide an upcased key to the underlying API.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_secure_credential#key SyntheticsSecureCredential#key}
        '''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''The secure credential's value.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_secure_credential#value SyntheticsSecureCredential#value}
        '''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def created_at(self) -> typing.Optional[builtins.str]:
        '''The time the secure credential was created.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_secure_credential#created_at SyntheticsSecureCredential#created_at}
        '''
        result = self._values.get("created_at")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''The secure credential's description.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_secure_credential#description SyntheticsSecureCredential#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def last_updated(self) -> typing.Optional[builtins.str]:
        '''The time the secure credential was last updated.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/synthetics_secure_credential#last_updated SyntheticsSecureCredential#last_updated}
        '''
        result = self._values.get("last_updated")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SyntheticsSecureCredentialConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Workload(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-newrelic.Workload",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/newrelic/r/workload newrelic_workload}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        account_id: typing.Optional[jsii.Number] = None,
        entity_guids: typing.Optional[typing.Sequence[builtins.str]] = None,
        entity_search_query: typing.Optional[typing.Sequence["WorkloadEntitySearchQuery"]] = None,
        scope_account_ids: typing.Optional[typing.Sequence[jsii.Number]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/newrelic/r/workload newrelic_workload} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: The workload's name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/workload#name Workload#name}
        :param account_id: The New Relic account ID where you want to create the workload. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/workload#account_id Workload#account_id}
        :param entity_guids: A list of entity GUIDs manually assigned to this workload. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/workload#entity_guids Workload#entity_guids}
        :param entity_search_query: entity_search_query block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/workload#entity_search_query Workload#entity_search_query}
        :param scope_account_ids: A list of account IDs that will be used to get entities from. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/workload#scope_account_ids Workload#scope_account_ids}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = WorkloadConfig(
            name=name,
            account_id=account_id,
            entity_guids=entity_guids,
            entity_search_query=entity_search_query,
            scope_account_ids=scope_account_ids,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetAccountId")
    def reset_account_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccountId", []))

    @jsii.member(jsii_name="resetEntityGuids")
    def reset_entity_guids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEntityGuids", []))

    @jsii.member(jsii_name="resetEntitySearchQuery")
    def reset_entity_search_query(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEntitySearchQuery", []))

    @jsii.member(jsii_name="resetScopeAccountIds")
    def reset_scope_account_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetScopeAccountIds", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="compositeEntitySearchQuery")
    def composite_entity_search_query(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "compositeEntitySearchQuery"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="guid")
    def guid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "guid"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="permalink")
    def permalink(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "permalink"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="workloadId")
    def workload_id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "workloadId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "accountIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="entityGuidsInput")
    def entity_guids_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "entityGuidsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="entitySearchQueryInput")
    def entity_search_query_input(
        self,
    ) -> typing.Optional[typing.List["WorkloadEntitySearchQuery"]]:
        return typing.cast(typing.Optional[typing.List["WorkloadEntitySearchQuery"]], jsii.get(self, "entitySearchQueryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="scopeAccountIdsInput")
    def scope_account_ids_input(self) -> typing.Optional[typing.List[jsii.Number]]:
        return typing.cast(typing.Optional[typing.List[jsii.Number]], jsii.get(self, "scopeAccountIdsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: jsii.Number) -> None:
        jsii.set(self, "accountId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="entityGuids")
    def entity_guids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "entityGuids"))

    @entity_guids.setter
    def entity_guids(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "entityGuids", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="entitySearchQuery")
    def entity_search_query(self) -> typing.List["WorkloadEntitySearchQuery"]:
        return typing.cast(typing.List["WorkloadEntitySearchQuery"], jsii.get(self, "entitySearchQuery"))

    @entity_search_query.setter
    def entity_search_query(
        self,
        value: typing.List["WorkloadEntitySearchQuery"],
    ) -> None:
        jsii.set(self, "entitySearchQuery", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="scopeAccountIds")
    def scope_account_ids(self) -> typing.List[jsii.Number]:
        return typing.cast(typing.List[jsii.Number], jsii.get(self, "scopeAccountIds"))

    @scope_account_ids.setter
    def scope_account_ids(self, value: typing.List[jsii.Number]) -> None:
        jsii.set(self, "scopeAccountIds", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.WorkloadConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "account_id": "accountId",
        "entity_guids": "entityGuids",
        "entity_search_query": "entitySearchQuery",
        "scope_account_ids": "scopeAccountIds",
    },
)
class WorkloadConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        account_id: typing.Optional[jsii.Number] = None,
        entity_guids: typing.Optional[typing.Sequence[builtins.str]] = None,
        entity_search_query: typing.Optional[typing.Sequence["WorkloadEntitySearchQuery"]] = None,
        scope_account_ids: typing.Optional[typing.Sequence[jsii.Number]] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: The workload's name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/workload#name Workload#name}
        :param account_id: The New Relic account ID where you want to create the workload. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/workload#account_id Workload#account_id}
        :param entity_guids: A list of entity GUIDs manually assigned to this workload. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/workload#entity_guids Workload#entity_guids}
        :param entity_search_query: entity_search_query block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/workload#entity_search_query Workload#entity_search_query}
        :param scope_account_ids: A list of account IDs that will be used to get entities from. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/workload#scope_account_ids Workload#scope_account_ids}
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
        if account_id is not None:
            self._values["account_id"] = account_id
        if entity_guids is not None:
            self._values["entity_guids"] = entity_guids
        if entity_search_query is not None:
            self._values["entity_search_query"] = entity_search_query
        if scope_account_ids is not None:
            self._values["scope_account_ids"] = scope_account_ids

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
        '''The workload's name.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/workload#name Workload#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def account_id(self) -> typing.Optional[jsii.Number]:
        '''The New Relic account ID where you want to create the workload.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/workload#account_id Workload#account_id}
        '''
        result = self._values.get("account_id")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def entity_guids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of entity GUIDs manually assigned to this workload.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/workload#entity_guids Workload#entity_guids}
        '''
        result = self._values.get("entity_guids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def entity_search_query(
        self,
    ) -> typing.Optional[typing.List["WorkloadEntitySearchQuery"]]:
        '''entity_search_query block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/workload#entity_search_query Workload#entity_search_query}
        '''
        result = self._values.get("entity_search_query")
        return typing.cast(typing.Optional[typing.List["WorkloadEntitySearchQuery"]], result)

    @builtins.property
    def scope_account_ids(self) -> typing.Optional[typing.List[jsii.Number]]:
        '''A list of account IDs that will be used to get entities from.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/workload#scope_account_ids Workload#scope_account_ids}
        '''
        result = self._values.get("scope_account_ids")
        return typing.cast(typing.Optional[typing.List[jsii.Number]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkloadConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-newrelic.WorkloadEntitySearchQuery",
    jsii_struct_bases=[],
    name_mapping={"query": "query"},
)
class WorkloadEntitySearchQuery:
    def __init__(self, *, query: builtins.str) -> None:
        '''
        :param query: The query. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/workload#query Workload#query}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "query": query,
        }

    @builtins.property
    def query(self) -> builtins.str:
        '''The query.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/newrelic/r/workload#query Workload#query}
        '''
        result = self._values.get("query")
        assert result is not None, "Required property 'query' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkloadEntitySearchQuery(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AlertChannel",
    "AlertChannelConfig",
    "AlertChannelConfigA",
    "AlertChannelConfigAOutputReference",
    "AlertCondition",
    "AlertConditionConfig",
    "AlertConditionTerm",
    "AlertMutingRule",
    "AlertMutingRuleCondition",
    "AlertMutingRuleConditionConditions",
    "AlertMutingRuleConditionOutputReference",
    "AlertMutingRuleConfig",
    "AlertMutingRuleSchedule",
    "AlertMutingRuleScheduleOutputReference",
    "AlertPolicy",
    "AlertPolicyChannel",
    "AlertPolicyChannelConfig",
    "AlertPolicyConfig",
    "ApiAccessKey",
    "ApiAccessKeyConfig",
    "ApplicationSettings",
    "ApplicationSettingsConfig",
    "Dashboard",
    "DashboardConfig",
    "DashboardFilter",
    "DashboardFilterOutputReference",
    "DashboardWidget",
    "DashboardWidgetCompareWith",
    "DashboardWidgetCompareWithPresentation",
    "DashboardWidgetCompareWithPresentationOutputReference",
    "DashboardWidgetMetric",
    "DataNewrelicAccount",
    "DataNewrelicAccountConfig",
    "DataNewrelicAlertChannel",
    "DataNewrelicAlertChannelConfig",
    "DataNewrelicAlertChannelConfigA",
    "DataNewrelicAlertPolicy",
    "DataNewrelicAlertPolicyConfig",
    "DataNewrelicApplication",
    "DataNewrelicApplicationConfig",
    "DataNewrelicEntity",
    "DataNewrelicEntityConfig",
    "DataNewrelicEntityTag",
    "DataNewrelicEntityTagOutputReference",
    "DataNewrelicKeyTransaction",
    "DataNewrelicKeyTransactionConfig",
    "DataNewrelicPlugin",
    "DataNewrelicPluginComponent",
    "DataNewrelicPluginComponentConfig",
    "DataNewrelicPluginConfig",
    "DataNewrelicSyntheticsMonitor",
    "DataNewrelicSyntheticsMonitorConfig",
    "DataNewrelicSyntheticsMonitorLocation",
    "DataNewrelicSyntheticsMonitorLocationConfig",
    "DataNewrelicSyntheticsSecureCredential",
    "DataNewrelicSyntheticsSecureCredentialConfig",
    "EntityTags",
    "EntityTagsConfig",
    "EntityTagsTag",
    "EntityTagsTimeouts",
    "EntityTagsTimeoutsOutputReference",
    "EventsToMetricsRule",
    "EventsToMetricsRuleConfig",
    "InfraAlertCondition",
    "InfraAlertConditionConfig",
    "InfraAlertConditionCritical",
    "InfraAlertConditionCriticalOutputReference",
    "InfraAlertConditionWarning",
    "InfraAlertConditionWarningOutputReference",
    "InsightsEvent",
    "InsightsEventConfig",
    "InsightsEventEvent",
    "InsightsEventEventAttribute",
    "NewrelicProvider",
    "NewrelicProviderConfig",
    "NrqlAlertCondition",
    "NrqlAlertConditionConfig",
    "NrqlAlertConditionCritical",
    "NrqlAlertConditionCriticalOutputReference",
    "NrqlAlertConditionNrql",
    "NrqlAlertConditionNrqlOutputReference",
    "NrqlAlertConditionTerm",
    "NrqlAlertConditionWarning",
    "NrqlAlertConditionWarningOutputReference",
    "NrqlDropRule",
    "NrqlDropRuleConfig",
    "OneDashboard",
    "OneDashboardConfig",
    "OneDashboardPage",
    "OneDashboardPageWidgetArea",
    "OneDashboardPageWidgetAreaNrqlQuery",
    "OneDashboardPageWidgetBar",
    "OneDashboardPageWidgetBarNrqlQuery",
    "OneDashboardPageWidgetBillboard",
    "OneDashboardPageWidgetBillboardNrqlQuery",
    "OneDashboardPageWidgetBullet",
    "OneDashboardPageWidgetBulletNrqlQuery",
    "OneDashboardPageWidgetFunnel",
    "OneDashboardPageWidgetFunnelNrqlQuery",
    "OneDashboardPageWidgetHeatmap",
    "OneDashboardPageWidgetHeatmapNrqlQuery",
    "OneDashboardPageWidgetHistogram",
    "OneDashboardPageWidgetHistogramNrqlQuery",
    "OneDashboardPageWidgetJson",
    "OneDashboardPageWidgetJsonNrqlQuery",
    "OneDashboardPageWidgetLine",
    "OneDashboardPageWidgetLineNrqlQuery",
    "OneDashboardPageWidgetMarkdown",
    "OneDashboardPageWidgetPie",
    "OneDashboardPageWidgetPieNrqlQuery",
    "OneDashboardPageWidgetStackedBar",
    "OneDashboardPageWidgetStackedBarNrqlQuery",
    "OneDashboardPageWidgetTable",
    "OneDashboardPageWidgetTableNrqlQuery",
    "OneDashboardRaw",
    "OneDashboardRawConfig",
    "OneDashboardRawPage",
    "OneDashboardRawPageWidget",
    "PluginsAlertCondition",
    "PluginsAlertConditionConfig",
    "PluginsAlertConditionTerm",
    "ServiceLevel",
    "ServiceLevelConfig",
    "ServiceLevelEvents",
    "ServiceLevelEventsBadEvents",
    "ServiceLevelEventsBadEventsOutputReference",
    "ServiceLevelEventsGoodEvents",
    "ServiceLevelEventsGoodEventsOutputReference",
    "ServiceLevelEventsOutputReference",
    "ServiceLevelEventsValidEvents",
    "ServiceLevelEventsValidEventsOutputReference",
    "ServiceLevelObjective",
    "ServiceLevelObjectiveTimeWindow",
    "ServiceLevelObjectiveTimeWindowOutputReference",
    "ServiceLevelObjectiveTimeWindowRolling",
    "ServiceLevelObjectiveTimeWindowRollingOutputReference",
    "SyntheticsAlertCondition",
    "SyntheticsAlertConditionConfig",
    "SyntheticsMonitor",
    "SyntheticsMonitorConfig",
    "SyntheticsMonitorScript",
    "SyntheticsMonitorScriptConfig",
    "SyntheticsMonitorScriptLocation",
    "SyntheticsMultilocationAlertCondition",
    "SyntheticsMultilocationAlertConditionConfig",
    "SyntheticsMultilocationAlertConditionCritical",
    "SyntheticsMultilocationAlertConditionCriticalOutputReference",
    "SyntheticsMultilocationAlertConditionWarning",
    "SyntheticsMultilocationAlertConditionWarningOutputReference",
    "SyntheticsSecureCredential",
    "SyntheticsSecureCredentialConfig",
    "Workload",
    "WorkloadConfig",
    "WorkloadEntitySearchQuery",
]

publication.publish()
