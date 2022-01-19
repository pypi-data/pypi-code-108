'''
# aws-apigateway-iot module

<!--BEGIN STABILITY BANNER-->---


![Stability: Experimental](https://img.shields.io/badge/stability-Experimental-important.svg?style=for-the-badge)

> All classes are under active development and subject to non-backward compatible changes or removal in any
> future version. These are not subject to the [Semantic Versioning](https://semver.org/) model.
> This means that while you may use them, you may need to update your source code when upgrading to a newer version of this package.

---
<!--END STABILITY BANNER-->

| **Reference Documentation**:| <span style="font-weight: normal">https://docs.aws.amazon.com/solutions/latest/constructs/</span>|
|:-------------|:-------------|

<div style="height:8px"></div>

| **Language**     | **Package**        |
|:-------------|-----------------|
|![Python Logo](https://docs.aws.amazon.com/cdk/api/latest/img/python32.png) Python|`aws_solutions_constructs.aws_apigateway_iot`|
|![Typescript Logo](https://docs.aws.amazon.com/cdk/api/latest/img/typescript32.png) Typescript|`@aws-solutions-constructs/aws-apigateway-iot`|
|![Java Logo](https://docs.aws.amazon.com/cdk/api/latest/img/java32.png) Java|`software.amazon.awsconstructs.services.apigatewayiot`|

## Overview

This AWS Solutions Construct implements an Amazon API Gateway REST API connected to AWS IoT pattern.

This construct creates a scalable HTTPS proxy between API Gateway and AWS IoT. This comes in handy when wanting to allow legacy devices that do not support the MQTT or MQTT/Websocket protocol to interact with the AWS IoT platform.

This implementation enables write-only messages to be published on given MQTT topics, and also supports shadow updates of HTTPS devices to allowed things in the device registry. It does not involve Lambda functions for proxying messages, and instead relies on direct API Gateway to AWS IoT integration which supports both JSON messages as well as binary messages.

Here is a minimal deployable pattern definition in Typescript:

```python
import { ApiGatewayToIot } from '@aws-solutions-constructs/aws-apigateway-iot';

new ApiGatewayToIot(this, 'ApiGatewayToIotPattern', {
    iotEndpoint: 'a1234567890123-ats'
});
```

## Initializer

```text
new ApiGatewayToIot(scope: Construct, id: string, props: ApiGatewayToIotProps);
```

*Parameters*

* scope [`Construct`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_core.Construct.html)
* id `string`
* props [`ApiGatewayToIotProps`](#pattern-construct-props)

## Pattern Construct Props

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
|iotEndpoint|`string`|The AWS IoT endpoint subdomain to integrate the API Gateway with (e.g a1234567890123-ats).|
|apiGatewayCreateApiKey?|`boolean`|If set to `true`, an API Key is created and associated to a UsagePlan. User should specify `x-api-key` header while accessing RestApi. Default value set to `false`|
|apiGatewayExecutionRole?|[`iam.Role`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-iam.Role.html)|IAM Role used by the API Gateway to access AWS IoT. If not specified, a default role is created with wildcard ('*') access to all topics and things.|
|apiGatewayProps?|[`api.restApiProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-apigateway.RestApiProps.html)|Optional user-provided props to override the default props for the API Gateway.|
|logGroupProps?|[`logs.LogGroupProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-logs.LogGroupProps.html)|User provided props to override the default props for for the CloudWatchLogs LogGroup.|

## Pattern Properties

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
|apiGateway|[`api.RestApi`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-apigateway.RestApi.html)|Returns an instance of the API Gateway REST API created by the pattern.|
|apiGatewayRole|[`iam.Role`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-iam.Role.html)|Returns an instance of the iam.Role created by the construct for API Gateway.|
|apiGatewayCloudWatchRole?|[`iam.Role`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-iam.Role.html)|Returns an instance of the iam.Role created by the construct for API Gateway for CloudWatch access.|
|apiGatewayLogGroup|[`logs.LogGroup`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-logs.LogGroup.html)|Returns an instance of the LogGroup created by the construct for API Gateway access logging to CloudWatch.|

## Default settings

Out of the box implementation of the Construct without any override will set the following defaults:

### Amazon API Gateway

* Deploy an edge-optimized API Endpoint
* Creates API Resources with `POST` Method to publish messages to IoT Topics
* Creates API Resources with `POST` Method to publish messages to ThingShadow & NamedShadows
* Enable CloudWatch logging for API Gateway
* Configure IAM role for API Gateway with access to all topics and things
* Set the default authorizationType for all API methods to IAM
* Enable X-Ray Tracing
* Creates a UsagePlan and associates to `prod` stage

Below is a description of the different resources and methods exposed by the API Gateway after deploying the Construct. See the [Examples](#examples) section for more information on how to easily test these endpoints using `curl`.

|Method         | Resource              | Query parameter(s) |  Return code(s)   |  Description|
|-------------- | --------------------- | ------------------ | ----------------- | -----------------|
|  **POST**     |  `/message/<topics>`  |      **qos**       |   `200/403/500`   | By calling this endpoint, you need to pass the topics on which you would like to publish (e.g `/message/device/foo`).|
|  **POST**     | `/shadow/<thingName>` |      **None**      |   `200/403/500`   | This route allows to update the shadow document of a thing, given its `thingName` using Unnamed (classic) shadow type. The body shall comply with the standard shadow stucture comprising a `state` node and associated `desired` and `reported` nodes. See the [Updating device shadows](#updating-device-shadows) section for an example.|
|  **POST**     | `/shadow/<thingName>/<shadowName>` |      **None**      |   `200/403/500`   | This route allows to update the named shadow document of a thing, given its `thingName` and the `shadowName` using the Named shadow type. The body shall comply with the standard shadow stucture comprising a `state` node and associated `desired` and `reported` nodes. See the [Updating named shadows](#updating-named-shadows) section for an example.|

## Architecture

![Architecture Diagram](architecture.png)

## Examples

The following examples only work with `API_KEY` authentication types, since IAM authorization requires a SIGv4 token to be specified as well, make sure the **apiGatewayCreateApiKey** property of your Construct props is set to **true** while deploying the stack, otherwise the below examples won't work.

### Publishing a message

You can use `curl` to publish a message on different MQTT topics using the HTTPS API. The below example will post a message on the `device/foo` topic.

```bash
curl -XPOST https://<stage-id>.execute-api.<region>.amazonaws.com/prod/message/device/foo -H "x-api-key: <api-key>" -H "Content-Type: application/json" -d '{"Hello": "World"}'
```

> Replace the `stage-id`, `region` and `api-key` parameters with your deployment values.

You can chain topic names in the URL and the API accepts up to 7 sub-topics that you can publish on. For instance, the below example publishes a message on the topic `device/foo/bar/abc/xyz`.

```bash
curl -XPOST https://<stage-id>.execute-api.<region>.amazonaws.com/prod/message/device/foo/bar/abc/xyz -H "x-api-key: <api-key>" -H "Content-Type: application/json" -d '{"Hello": "World"}'
```

### Updating device shadows

To update the shadow document associated with a given thing, you can issue a shadow state request using a thing name. See the following example on how to update a thing shadow.

```bash
curl -XPOST https://<stage-id>.execute-api.<region>.amazonaws.com/prod/shadow/device1 -H "x-api-key: <api-key>" -H "Content-Type: application/json" -d '{"state": {"desired": { "Hello": "World" }}}'
```

### Updating named shadows

To update the shadow document associated with a given thing's named shadow, you can issue a shadow state request using a thing name and shadow name. See the following example on how to update a named shadow.

```bash
curl -XPOST https://<stage-id>.execute-api.<region>.amazonaws.com/prod/shadow/device1/shadow1 -H "x-api-key: <api-key>" -H "Content-Type: application/json" -d '{"state": {"desired": { "Hello": "World" }}}'
```

### Sending binary payloads

It is possible to send a binary payload to the proxy API, down to the AWS IoT service. In the following example, we send the content of the `README.md` file associated with this module (treated as a binary data) to `device/foo` topic using the `application/octet-stream` content type.

```bash
curl -XPOST https://<stage-id>.execute-api.<region>.amazonaws.com/prod/message/device/foo/bar/baz/qux -H "x-api-key: <api-key>" -H "Content-Type: application/octet-stream" --data-binary @README.md
```

> Execute this command while in the directory of this project. You can then test sending other type of binary files from your file-system.

---


© Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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

import aws_cdk.aws_apigateway
import aws_cdk.aws_iam
import aws_cdk.aws_logs
import aws_cdk.core


class ApiGatewayToIot(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-solutions-constructs/aws-apigateway-iot.ApiGatewayToIot",
):
    '''
    :summary: The ApiGatewayIot class.
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        iot_endpoint: builtins.str,
        api_gateway_create_api_key: typing.Optional[builtins.bool] = None,
        api_gateway_execution_role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        api_gateway_props: typing.Optional[aws_cdk.aws_apigateway.RestApiProps] = None,
        log_group_props: typing.Optional[aws_cdk.aws_logs.LogGroupProps] = None,
    ) -> None:
        '''
        :param scope: - represents the scope for all the resources.
        :param id: - this is a a scope-unique id.
        :param iot_endpoint: The AWS IoT endpoint subdomain to integrate the API Gateway with (e.g ab123cdefghij4l-ats). Added as AWS Subdomain to the Integration Request. Default: - None.
        :param api_gateway_create_api_key: Creates an api key and associates to usage plan if set to true. Default: - false
        :param api_gateway_execution_role: The IAM role that is used by API Gateway to publish messages to IoT topics and Thing shadows. Default: - An IAM role with iot:Publish access to all topics (topic/*) and iot:UpdateThingShadow access to all things (thing/*) is created.
        :param api_gateway_props: Optional user-provided props to override the default props for the API. Default: - Default props are used.
        :param log_group_props: User provided props to override the default props for the CloudWatchLogs LogGroup. Default: - Default props are used

        :access: public
        :since: 0.8.0
        :summary: Constructs a new instance of the ApiGatewayIot class.
        '''
        props = ApiGatewayToIotProps(
            iot_endpoint=iot_endpoint,
            api_gateway_create_api_key=api_gateway_create_api_key,
            api_gateway_execution_role=api_gateway_execution_role,
            api_gateway_props=api_gateway_props,
            log_group_props=log_group_props,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiGateway")
    def api_gateway(self) -> aws_cdk.aws_apigateway.RestApi:
        return typing.cast(aws_cdk.aws_apigateway.RestApi, jsii.get(self, "apiGateway"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiGatewayLogGroup")
    def api_gateway_log_group(self) -> aws_cdk.aws_logs.LogGroup:
        return typing.cast(aws_cdk.aws_logs.LogGroup, jsii.get(self, "apiGatewayLogGroup"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiGatewayRole")
    def api_gateway_role(self) -> aws_cdk.aws_iam.IRole:
        return typing.cast(aws_cdk.aws_iam.IRole, jsii.get(self, "apiGatewayRole"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiGatewayCloudWatchRole")
    def api_gateway_cloud_watch_role(self) -> typing.Optional[aws_cdk.aws_iam.Role]:
        return typing.cast(typing.Optional[aws_cdk.aws_iam.Role], jsii.get(self, "apiGatewayCloudWatchRole"))


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/aws-apigateway-iot.ApiGatewayToIotProps",
    jsii_struct_bases=[],
    name_mapping={
        "iot_endpoint": "iotEndpoint",
        "api_gateway_create_api_key": "apiGatewayCreateApiKey",
        "api_gateway_execution_role": "apiGatewayExecutionRole",
        "api_gateway_props": "apiGatewayProps",
        "log_group_props": "logGroupProps",
    },
)
class ApiGatewayToIotProps:
    def __init__(
        self,
        *,
        iot_endpoint: builtins.str,
        api_gateway_create_api_key: typing.Optional[builtins.bool] = None,
        api_gateway_execution_role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        api_gateway_props: typing.Optional[aws_cdk.aws_apigateway.RestApiProps] = None,
        log_group_props: typing.Optional[aws_cdk.aws_logs.LogGroupProps] = None,
    ) -> None:
        '''The properties for the ApiGatewayIot class.

        :param iot_endpoint: The AWS IoT endpoint subdomain to integrate the API Gateway with (e.g ab123cdefghij4l-ats). Added as AWS Subdomain to the Integration Request. Default: - None.
        :param api_gateway_create_api_key: Creates an api key and associates to usage plan if set to true. Default: - false
        :param api_gateway_execution_role: The IAM role that is used by API Gateway to publish messages to IoT topics and Thing shadows. Default: - An IAM role with iot:Publish access to all topics (topic/*) and iot:UpdateThingShadow access to all things (thing/*) is created.
        :param api_gateway_props: Optional user-provided props to override the default props for the API. Default: - Default props are used.
        :param log_group_props: User provided props to override the default props for the CloudWatchLogs LogGroup. Default: - Default props are used
        '''
        if isinstance(api_gateway_props, dict):
            api_gateway_props = aws_cdk.aws_apigateway.RestApiProps(**api_gateway_props)
        if isinstance(log_group_props, dict):
            log_group_props = aws_cdk.aws_logs.LogGroupProps(**log_group_props)
        self._values: typing.Dict[str, typing.Any] = {
            "iot_endpoint": iot_endpoint,
        }
        if api_gateway_create_api_key is not None:
            self._values["api_gateway_create_api_key"] = api_gateway_create_api_key
        if api_gateway_execution_role is not None:
            self._values["api_gateway_execution_role"] = api_gateway_execution_role
        if api_gateway_props is not None:
            self._values["api_gateway_props"] = api_gateway_props
        if log_group_props is not None:
            self._values["log_group_props"] = log_group_props

    @builtins.property
    def iot_endpoint(self) -> builtins.str:
        '''The AWS IoT endpoint subdomain to integrate the API Gateway with (e.g ab123cdefghij4l-ats). Added as AWS Subdomain to the Integration Request.

        :default: - None.
        '''
        result = self._values.get("iot_endpoint")
        assert result is not None, "Required property 'iot_endpoint' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def api_gateway_create_api_key(self) -> typing.Optional[builtins.bool]:
        '''Creates an api key and associates to usage plan if set to true.

        :default: - false
        '''
        result = self._values.get("api_gateway_create_api_key")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def api_gateway_execution_role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        '''The IAM role that is used by API Gateway to publish messages to IoT topics and Thing shadows.

        :default: - An IAM role with iot:Publish access to all topics (topic/*) and iot:UpdateThingShadow access to all things (thing/*) is created.
        '''
        result = self._values.get("api_gateway_execution_role")
        return typing.cast(typing.Optional[aws_cdk.aws_iam.IRole], result)

    @builtins.property
    def api_gateway_props(self) -> typing.Optional[aws_cdk.aws_apigateway.RestApiProps]:
        '''Optional user-provided props to override the default props for the API.

        :default: - Default props are used.
        '''
        result = self._values.get("api_gateway_props")
        return typing.cast(typing.Optional[aws_cdk.aws_apigateway.RestApiProps], result)

    @builtins.property
    def log_group_props(self) -> typing.Optional[aws_cdk.aws_logs.LogGroupProps]:
        '''User provided props to override the default props for the CloudWatchLogs LogGroup.

        :default: - Default props are used
        '''
        result = self._values.get("log_group_props")
        return typing.cast(typing.Optional[aws_cdk.aws_logs.LogGroupProps], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApiGatewayToIotProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ApiGatewayToIot",
    "ApiGatewayToIotProps",
]

publication.publish()
