'''
[![cloudcomponents Logo](https://raw.githubusercontent.com/cloudcomponents/cdk-constructs/master/logo.png)](https://github.com/cloudcomponents/cdk-constructs)

# @cloudcomponents/cdk-stripe-webhook

[![Build Status](https://github.com/cloudcomponents/cdk-constructs/workflows/Build/badge.svg)](https://github.com/cloudcomponents/cdk-constructs/actions?query=workflow=Build)
[![cdkdx](https://img.shields.io/badge/buildtool-cdkdx-blue.svg)](https://github.com/hupe1980/cdkdx)
[![typescript](https://img.shields.io/badge/jsii-typescript-blueviolet.svg)](https://www.npmjs.com/package/@cloudcomponents/cdk-stripe-webhook)
[![python](https://img.shields.io/badge/jsii-python-blueviolet.svg)](https://pypi.org/project/cloudcomponents.cdk-stripe-webhook/)

> Create, update and delete stripe webhooks with your app deployment

## Install

TypeScript/JavaScript:

```bash
npm i @cloudcomponents/cdk-stripe-webhook
```

Python:

```bash
pip install cloudcomponents.cdk-stripe-webhook
```

## How to use

### EventBus Producer

```python
import { StringParameter } from '@aws-cdk/aws-ssm';
import { Construct, Stack, StackProps } from '@aws-cdk/core';
import { SecretKey, SecretKeyStore } from '@cloudcomponents/cdk-secret-key';
import { StripeWebhook, StripeEventBusProducer } from '@cloudcomponents/cdk-stripe-webhook';

export class StripeWebhookStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const secretKey = SecretKey.fromPlainText(process.env.SECRET_KEY as string);

    const endpointSecretParameter = StringParameter.fromSecureStringParameterAttributes(this, 'Param', {
      parameterName: 'stripe',
      version: 1,
    });

    const producer = new StripeEventBusProducer(this, 'Producer', {
      secretKey,
      endpointSecret: SecretKey.fromSSMParameter(endpointSecretParameter),
    });

    const events = ['charge.failed', 'charge.succeeded'];

    const endpointSecretStore = SecretKeyStore.fromSSMParameter(endpointSecretParameter);

    new StripeWebhook(this, 'StripeWebhook', {
      secretKey,
      url: producer.url,
      events,
      logLevel: 'debug',
      endpointSecretStore,
    });
  }
}
```

### Custom Handler

```python
import { RestApi } from '@aws-cdk/aws-apigateway';
import { Construct, Stack, StackProps } from '@aws-cdk/core';
import { SecretKey } from '@cloudcomponents/cdk-secret-key';
import { StripeWebhook } from '@cloudcomponents/cdk-stripe-webhook';
export class StripeWebhookStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const api = new RestApi(this, 'Endpoint');
    api.root.addMethod('POST');

    const secretKey = SecretKey.fromPlainText(process.env.SECRET_KEY as string);

    const events = ['charge.failed', 'charge.succeeded'];

    new StripeWebhook(this, 'StripeWebhook', {
      secretKey,
      url: api.url,
      events,
      logLevel: 'debug',
    });
  }
}
```

## API Reference

See [API.md](https://github.com/cloudcomponents/cdk-constructs/tree/master/packages/cdk-stripe-webhook/API.md).

## Example

See more complete [examples](https://github.com/cloudcomponents/cdk-constructs/tree/master/examples).

## License

[MIT](https://github.com/cloudcomponents/cdk-constructs/tree/master/packages/cdk-stripe-webhook/LICENSE)
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

import aws_cdk.aws_events
import aws_cdk.core
import cloudcomponents.cdk_secret_key


class StripeEventBusProducer(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudcomponents/cdk-stripe-webhook.StripeEventBusProducer",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        endpoint_secret: cloudcomponents.cdk_secret_key.SecretKey,
        secret_key: cloudcomponents.cdk_secret_key.SecretKey,
        event_bus: typing.Optional[aws_cdk.aws_events.IEventBus] = None,
        source: typing.Optional[builtins.str] = None,
        throttling_burst_limit: typing.Optional[jsii.Number] = None,
        throttling_rate_limit: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param endpoint_secret: -
        :param secret_key: -
        :param event_bus: -
        :param source: -
        :param throttling_burst_limit: -
        :param throttling_rate_limit: -
        '''
        props = StripeEventBusProducerProps(
            endpoint_secret=endpoint_secret,
            secret_key=secret_key,
            event_bus=event_bus,
            source=source,
            throttling_burst_limit=throttling_burst_limit,
            throttling_rate_limit=throttling_rate_limit,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))


@jsii.data_type(
    jsii_type="@cloudcomponents/cdk-stripe-webhook.StripeEventBusProducerProps",
    jsii_struct_bases=[],
    name_mapping={
        "endpoint_secret": "endpointSecret",
        "secret_key": "secretKey",
        "event_bus": "eventBus",
        "source": "source",
        "throttling_burst_limit": "throttlingBurstLimit",
        "throttling_rate_limit": "throttlingRateLimit",
    },
)
class StripeEventBusProducerProps:
    def __init__(
        self,
        *,
        endpoint_secret: cloudcomponents.cdk_secret_key.SecretKey,
        secret_key: cloudcomponents.cdk_secret_key.SecretKey,
        event_bus: typing.Optional[aws_cdk.aws_events.IEventBus] = None,
        source: typing.Optional[builtins.str] = None,
        throttling_burst_limit: typing.Optional[jsii.Number] = None,
        throttling_rate_limit: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param endpoint_secret: -
        :param secret_key: -
        :param event_bus: -
        :param source: -
        :param throttling_burst_limit: -
        :param throttling_rate_limit: -
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "endpoint_secret": endpoint_secret,
            "secret_key": secret_key,
        }
        if event_bus is not None:
            self._values["event_bus"] = event_bus
        if source is not None:
            self._values["source"] = source
        if throttling_burst_limit is not None:
            self._values["throttling_burst_limit"] = throttling_burst_limit
        if throttling_rate_limit is not None:
            self._values["throttling_rate_limit"] = throttling_rate_limit

    @builtins.property
    def endpoint_secret(self) -> cloudcomponents.cdk_secret_key.SecretKey:
        result = self._values.get("endpoint_secret")
        assert result is not None, "Required property 'endpoint_secret' is missing"
        return typing.cast(cloudcomponents.cdk_secret_key.SecretKey, result)

    @builtins.property
    def secret_key(self) -> cloudcomponents.cdk_secret_key.SecretKey:
        result = self._values.get("secret_key")
        assert result is not None, "Required property 'secret_key' is missing"
        return typing.cast(cloudcomponents.cdk_secret_key.SecretKey, result)

    @builtins.property
    def event_bus(self) -> typing.Optional[aws_cdk.aws_events.IEventBus]:
        result = self._values.get("event_bus")
        return typing.cast(typing.Optional[aws_cdk.aws_events.IEventBus], result)

    @builtins.property
    def source(self) -> typing.Optional[builtins.str]:
        result = self._values.get("source")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def throttling_burst_limit(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("throttling_burst_limit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def throttling_rate_limit(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("throttling_rate_limit")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StripeEventBusProducerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StripeWebhook(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudcomponents/cdk-stripe-webhook.StripeWebhook",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        events: typing.Sequence[builtins.str],
        secret_key: typing.Union[builtins.str, cloudcomponents.cdk_secret_key.SecretKey],
        url: builtins.str,
        description: typing.Optional[builtins.str] = None,
        endpoint_secret_store: typing.Optional[cloudcomponents.cdk_secret_key.SecretKeyStore] = None,
        log_level: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param events: -
        :param secret_key: -
        :param url: -
        :param description: -
        :param endpoint_secret_store: -
        :param log_level: -
        '''
        props = StripeWebhookProps(
            events=events,
            secret_key=secret_key,
            url=url,
            description=description,
            endpoint_secret_store=endpoint_secret_store,
            log_level=log_level,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))


@jsii.data_type(
    jsii_type="@cloudcomponents/cdk-stripe-webhook.StripeWebhookProps",
    jsii_struct_bases=[],
    name_mapping={
        "events": "events",
        "secret_key": "secretKey",
        "url": "url",
        "description": "description",
        "endpoint_secret_store": "endpointSecretStore",
        "log_level": "logLevel",
    },
)
class StripeWebhookProps:
    def __init__(
        self,
        *,
        events: typing.Sequence[builtins.str],
        secret_key: typing.Union[builtins.str, cloudcomponents.cdk_secret_key.SecretKey],
        url: builtins.str,
        description: typing.Optional[builtins.str] = None,
        endpoint_secret_store: typing.Optional[cloudcomponents.cdk_secret_key.SecretKeyStore] = None,
        log_level: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param events: -
        :param secret_key: -
        :param url: -
        :param description: -
        :param endpoint_secret_store: -
        :param log_level: -
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "events": events,
            "secret_key": secret_key,
            "url": url,
        }
        if description is not None:
            self._values["description"] = description
        if endpoint_secret_store is not None:
            self._values["endpoint_secret_store"] = endpoint_secret_store
        if log_level is not None:
            self._values["log_level"] = log_level

    @builtins.property
    def events(self) -> typing.List[builtins.str]:
        result = self._values.get("events")
        assert result is not None, "Required property 'events' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def secret_key(
        self,
    ) -> typing.Union[builtins.str, cloudcomponents.cdk_secret_key.SecretKey]:
        result = self._values.get("secret_key")
        assert result is not None, "Required property 'secret_key' is missing"
        return typing.cast(typing.Union[builtins.str, cloudcomponents.cdk_secret_key.SecretKey], result)

    @builtins.property
    def url(self) -> builtins.str:
        result = self._values.get("url")
        assert result is not None, "Required property 'url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def endpoint_secret_store(
        self,
    ) -> typing.Optional[cloudcomponents.cdk_secret_key.SecretKeyStore]:
        result = self._values.get("endpoint_secret_store")
        return typing.cast(typing.Optional[cloudcomponents.cdk_secret_key.SecretKeyStore], result)

    @builtins.property
    def log_level(self) -> typing.Optional[builtins.str]:
        result = self._values.get("log_level")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StripeWebhookProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "StripeEventBusProducer",
    "StripeEventBusProducerProps",
    "StripeWebhook",
    "StripeWebhookProps",
]

publication.publish()
