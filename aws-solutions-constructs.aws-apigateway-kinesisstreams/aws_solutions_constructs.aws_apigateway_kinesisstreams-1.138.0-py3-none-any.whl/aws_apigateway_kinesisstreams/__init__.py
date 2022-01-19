'''
# aws-apigateway-kinesisstreams module

<!--BEGIN STABILITY BANNER-->---


![Stability: Stable](https://img.shields.io/badge/cfn--resources-stable-success.svg?style=for-the-badge)

---
<!--END STABILITY BANNER-->

| **Reference Documentation**:| <span style="font-weight: normal">https://docs.aws.amazon.com/solutions/latest/constructs/</span>|
|:-------------|:-------------|

<div style="height:8px"></div>

| **Language**     | **Package**        |
|:-------------|-----------------|
|![Python Logo](https://docs.aws.amazon.com/cdk/api/latest/img/python32.png) Python|`aws_solutions_constructs.aws_apigateway_kinesisstreams`|
|![Typescript Logo](https://docs.aws.amazon.com/cdk/api/latest/img/typescript32.png) Typescript|`@aws-solutions-constructs/aws-apigateway-kinesisstreams`|
|![Java Logo](https://docs.aws.amazon.com/cdk/api/latest/img/java32.png) Java|`software.amazon.awsconstructs.services.apigatewaykinesisstreams`|

## Overview

This AWS Solutions Construct implements an Amazon API Gateway connected to an Amazon Kinesis Data Stream pattern.

Here is a minimal deployable pattern definition in Typescript:

```javascript
import { ApiGatewayToKinesisStreams, ApiGatewayToKinesisStreamsProps } from '@aws-solutions-constructs/aws-apigateway-kinesisstreams';

new ApiGatewayToKinesisStreams(this, 'test-apigw-kinesis', {});

```

## Initializer

```text
new ApiGatewayToKinesisStreams(scope: Construct, id: string, props: ApiGatewayToKinesisStreamsProps);
```

*Parameters*

* scope [`Construct`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_core.Construct.html)
* id `string`
* props [`ApiGatewayToKinesisStreamsProps`](#pattern-construct-props)

## Pattern Construct Props

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
|apiGatewayProps?|[`api.RestApiProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-apigateway.RestApiProps.html)|Optional user-provided props to override the default props for the API Gateway.|
|putRecordRequestTemplate?|`string`|API Gateway request template for the PutRecord action. If not provided, a default one will be used.|
|putRecordRequestModel?|[`api.ModelOptions`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-apigateway.ModelOptions.html)|API Gateway request model for the PutRecord action. If not provided, a default one will be created.|
|putRecordsRequestTemplate?|`string`|API Gateway request template for the PutRecords action. If not provided, a default one will be used.|
|putRecordsRequestModel?|[`api.ModelOptions`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-apigateway.ModelOptions.html)|API Gateway request model for the PutRecords action. If not provided, a default one will be created.|
|existingStreamObj?|[`kinesis.Stream`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-kinesis.Stream.html)|Existing instance of Kinesis Stream, providing both this and `kinesisStreamProps` will cause an error.|
|kinesisStreamProps?|[`kinesis.StreamProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-kinesis.StreamProps.html)|Optional user-provided props to override the default props for the Kinesis stream.|
|logGroupProps?|[`logs.LogGroupProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-logs.LogGroupProps.html)|User provided props to override the default props for for the CloudWatchLogs LogGroup.|
|createCloudWatchAlarms|`boolean`|Whether to create recommended CloudWatch alarms for Kinesis Data Stream. Default value is set to `true`|

## Pattern Properties

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
|apiGateway|[`api.RestApi`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-apigateway.RestApi.html)|Returns an instance of the API Gateway REST API created by the pattern.|
|apiGatewayRole|[`iam.Role`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-iam.Role.html)|Returns an instance of the iam.Role created by the construct for API Gateway.|
|apiGatewayCloudWatchRole?|[`iam.Role`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-iam.Role.html)|Returns an instance of the iam.Role created by the construct for API Gateway for CloudWatch access.|
|apiGatewayLogGroup|[`logs.LogGroup`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-logs.LogGroup.html)|Returns an instance of the LogGroup created by the construct for API Gateway access logging to CloudWatch.|
|kinesisStream|[`kinesis.Stream`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-kinesis.Stream.html)|Returns an instance of the Kinesis stream created or used by the pattern.|
|cloudwatchAlarms?|[`cloudwatch.Alarm[]`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-cloudwatch.Alarm.html)|Returns an array of recommended CloudWatch Alarms created by the construct for Kinesis Data stream|

## Sample API Usage

| **Method** | **Request Path** | **Request Body** | **Stream Action** | **Description** |
|:-------------|:----------------|-----------------|-----------------|-----------------|
|POST|`/record`| `{ "data": "Hello World!", "partitionKey": "pk001" }` |`kinesis:PutRecord`|Writes a single data record into the stream.|
|POST|`/records`| `{ "records": [{ "data": "abc", "partitionKey": "pk001" }, { "data": "xyz", "partitionKey": "pk001" }] }` |`kinesis:PutRecords`|Writes multiple data records into the stream in a single call.|

## Default settings

Out of the box implementation of the Construct without any override will set the following defaults:

### Amazon API Gateway

* Deploy an edge-optimized API endpoint
* Enable CloudWatch logging for API Gateway
* Configure least privilege access IAM role for API Gateway
* Set the default authorizationType for all API methods to IAM
* Enable X-Ray Tracing
* Validate request body before passing data to Kinesis

### Amazon Kinesis Data Stream

* Configure least privilege access IAM role for Kinesis Stream
* Enable server-side encryption for Kinesis Stream using AWS Managed KMS Key

## Architecture

![Architecture Diagram](architecture.png)

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
import aws_cdk.aws_cloudwatch
import aws_cdk.aws_iam
import aws_cdk.aws_kinesis
import aws_cdk.aws_logs
import aws_cdk.core


class ApiGatewayToKinesisStreams(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-solutions-constructs/aws-apigateway-kinesisstreams.ApiGatewayToKinesisStreams",
):
    '''
    :summary: The ApiGatewayToKinesisStreams class.
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        api_gateway_props: typing.Optional[aws_cdk.aws_apigateway.RestApiProps] = None,
        create_cloud_watch_alarms: typing.Optional[builtins.bool] = None,
        existing_stream_obj: typing.Optional[aws_cdk.aws_kinesis.Stream] = None,
        kinesis_stream_props: typing.Optional[aws_cdk.aws_kinesis.StreamProps] = None,
        log_group_props: typing.Optional[aws_cdk.aws_logs.LogGroupProps] = None,
        put_record_request_model: typing.Optional[aws_cdk.aws_apigateway.ModelOptions] = None,
        put_record_request_template: typing.Optional[builtins.str] = None,
        put_records_request_model: typing.Optional[aws_cdk.aws_apigateway.ModelOptions] = None,
        put_records_request_template: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: - represents the scope for all the resources.
        :param id: - this is a a scope-unique id.
        :param api_gateway_props: Optional user-provided props to override the default props for the API Gateway. Default: - Default properties are used.
        :param create_cloud_watch_alarms: Whether to create recommended CloudWatch alarms. Default: - Alarms are created
        :param existing_stream_obj: Existing instance of Kinesis Stream, providing both this and ``kinesisStreamProps`` will cause an error. Default: - None
        :param kinesis_stream_props: Optional user-provided props to override the default props for the Kinesis Data Stream. Default: - Default properties are used.
        :param log_group_props: User provided props to override the default props for the CloudWatchLogs LogGroup. Default: - Default props are used
        :param put_record_request_model: API Gateway request model for the PutRecord action. If not provided, a default one will be created. Default: - {"$schema":"http://json-schema.org/draft-04/schema#","title":"PutRecord proxy single-record payload","type":"object", "required":["data","partitionKey"],"properties":{"data":{"type":"string"},"partitionKey":{"type":"string"}}}
        :param put_record_request_template: API Gateway request template for the PutRecord action. If not provided, a default one will be used. Default: - { "StreamName": "${this.kinesisStream.streamName}", "Data": "$util.base64Encode($input.json('$.data'))", "PartitionKey": "$input.path('$.partitionKey')" }
        :param put_records_request_model: API Gateway request model for the PutRecords action. If not provided, a default one will be created. Default: - {"$schema":"http://json-schema.org/draft-04/schema#","title":"PutRecords proxy payload data","type":"object","required":["records"], "properties":{"records":{"type":"array","items":{"type":"object", "required":["data","partitionKey"],"properties":{"data":{"type":"string"},"partitionKey":{"type":"string"}}}}}}
        :param put_records_request_template: API Gateway request template for the PutRecords action. If not provided, a default one will be used. Default: - { "StreamName": "${this.kinesisStream.streamName}", "Records": [ #foreach($elem in $input.path('$.records')) { "Data": "$util.base64Encode($elem.data)", "PartitionKey": "$elem.partitionKey"}#if($foreach.hasNext),#end #end ] }

        :access: public
        :since: 1.62.0
        :summary: Constructs a new instance of the ApiGatewayToKinesisStreams class.
        '''
        props = ApiGatewayToKinesisStreamsProps(
            api_gateway_props=api_gateway_props,
            create_cloud_watch_alarms=create_cloud_watch_alarms,
            existing_stream_obj=existing_stream_obj,
            kinesis_stream_props=kinesis_stream_props,
            log_group_props=log_group_props,
            put_record_request_model=put_record_request_model,
            put_record_request_template=put_record_request_template,
            put_records_request_model=put_records_request_model,
            put_records_request_template=put_records_request_template,
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
    def api_gateway_role(self) -> aws_cdk.aws_iam.Role:
        return typing.cast(aws_cdk.aws_iam.Role, jsii.get(self, "apiGatewayRole"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kinesisStream")
    def kinesis_stream(self) -> aws_cdk.aws_kinesis.Stream:
        return typing.cast(aws_cdk.aws_kinesis.Stream, jsii.get(self, "kinesisStream"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiGatewayCloudWatchRole")
    def api_gateway_cloud_watch_role(self) -> typing.Optional[aws_cdk.aws_iam.Role]:
        return typing.cast(typing.Optional[aws_cdk.aws_iam.Role], jsii.get(self, "apiGatewayCloudWatchRole"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cloudwatchAlarms")
    def cloudwatch_alarms(
        self,
    ) -> typing.Optional[typing.List[aws_cdk.aws_cloudwatch.Alarm]]:
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_cloudwatch.Alarm]], jsii.get(self, "cloudwatchAlarms"))


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/aws-apigateway-kinesisstreams.ApiGatewayToKinesisStreamsProps",
    jsii_struct_bases=[],
    name_mapping={
        "api_gateway_props": "apiGatewayProps",
        "create_cloud_watch_alarms": "createCloudWatchAlarms",
        "existing_stream_obj": "existingStreamObj",
        "kinesis_stream_props": "kinesisStreamProps",
        "log_group_props": "logGroupProps",
        "put_record_request_model": "putRecordRequestModel",
        "put_record_request_template": "putRecordRequestTemplate",
        "put_records_request_model": "putRecordsRequestModel",
        "put_records_request_template": "putRecordsRequestTemplate",
    },
)
class ApiGatewayToKinesisStreamsProps:
    def __init__(
        self,
        *,
        api_gateway_props: typing.Optional[aws_cdk.aws_apigateway.RestApiProps] = None,
        create_cloud_watch_alarms: typing.Optional[builtins.bool] = None,
        existing_stream_obj: typing.Optional[aws_cdk.aws_kinesis.Stream] = None,
        kinesis_stream_props: typing.Optional[aws_cdk.aws_kinesis.StreamProps] = None,
        log_group_props: typing.Optional[aws_cdk.aws_logs.LogGroupProps] = None,
        put_record_request_model: typing.Optional[aws_cdk.aws_apigateway.ModelOptions] = None,
        put_record_request_template: typing.Optional[builtins.str] = None,
        put_records_request_model: typing.Optional[aws_cdk.aws_apigateway.ModelOptions] = None,
        put_records_request_template: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param api_gateway_props: Optional user-provided props to override the default props for the API Gateway. Default: - Default properties are used.
        :param create_cloud_watch_alarms: Whether to create recommended CloudWatch alarms. Default: - Alarms are created
        :param existing_stream_obj: Existing instance of Kinesis Stream, providing both this and ``kinesisStreamProps`` will cause an error. Default: - None
        :param kinesis_stream_props: Optional user-provided props to override the default props for the Kinesis Data Stream. Default: - Default properties are used.
        :param log_group_props: User provided props to override the default props for the CloudWatchLogs LogGroup. Default: - Default props are used
        :param put_record_request_model: API Gateway request model for the PutRecord action. If not provided, a default one will be created. Default: - {"$schema":"http://json-schema.org/draft-04/schema#","title":"PutRecord proxy single-record payload","type":"object", "required":["data","partitionKey"],"properties":{"data":{"type":"string"},"partitionKey":{"type":"string"}}}
        :param put_record_request_template: API Gateway request template for the PutRecord action. If not provided, a default one will be used. Default: - { "StreamName": "${this.kinesisStream.streamName}", "Data": "$util.base64Encode($input.json('$.data'))", "PartitionKey": "$input.path('$.partitionKey')" }
        :param put_records_request_model: API Gateway request model for the PutRecords action. If not provided, a default one will be created. Default: - {"$schema":"http://json-schema.org/draft-04/schema#","title":"PutRecords proxy payload data","type":"object","required":["records"], "properties":{"records":{"type":"array","items":{"type":"object", "required":["data","partitionKey"],"properties":{"data":{"type":"string"},"partitionKey":{"type":"string"}}}}}}
        :param put_records_request_template: API Gateway request template for the PutRecords action. If not provided, a default one will be used. Default: - { "StreamName": "${this.kinesisStream.streamName}", "Records": [ #foreach($elem in $input.path('$.records')) { "Data": "$util.base64Encode($elem.data)", "PartitionKey": "$elem.partitionKey"}#if($foreach.hasNext),#end #end ] }

        :summary: The properties for the ApiGatewayToKinesisStreamsProps class.
        '''
        if isinstance(api_gateway_props, dict):
            api_gateway_props = aws_cdk.aws_apigateway.RestApiProps(**api_gateway_props)
        if isinstance(kinesis_stream_props, dict):
            kinesis_stream_props = aws_cdk.aws_kinesis.StreamProps(**kinesis_stream_props)
        if isinstance(log_group_props, dict):
            log_group_props = aws_cdk.aws_logs.LogGroupProps(**log_group_props)
        if isinstance(put_record_request_model, dict):
            put_record_request_model = aws_cdk.aws_apigateway.ModelOptions(**put_record_request_model)
        if isinstance(put_records_request_model, dict):
            put_records_request_model = aws_cdk.aws_apigateway.ModelOptions(**put_records_request_model)
        self._values: typing.Dict[str, typing.Any] = {}
        if api_gateway_props is not None:
            self._values["api_gateway_props"] = api_gateway_props
        if create_cloud_watch_alarms is not None:
            self._values["create_cloud_watch_alarms"] = create_cloud_watch_alarms
        if existing_stream_obj is not None:
            self._values["existing_stream_obj"] = existing_stream_obj
        if kinesis_stream_props is not None:
            self._values["kinesis_stream_props"] = kinesis_stream_props
        if log_group_props is not None:
            self._values["log_group_props"] = log_group_props
        if put_record_request_model is not None:
            self._values["put_record_request_model"] = put_record_request_model
        if put_record_request_template is not None:
            self._values["put_record_request_template"] = put_record_request_template
        if put_records_request_model is not None:
            self._values["put_records_request_model"] = put_records_request_model
        if put_records_request_template is not None:
            self._values["put_records_request_template"] = put_records_request_template

    @builtins.property
    def api_gateway_props(self) -> typing.Optional[aws_cdk.aws_apigateway.RestApiProps]:
        '''Optional user-provided props to override the default props for the API Gateway.

        :default: - Default properties are used.
        '''
        result = self._values.get("api_gateway_props")
        return typing.cast(typing.Optional[aws_cdk.aws_apigateway.RestApiProps], result)

    @builtins.property
    def create_cloud_watch_alarms(self) -> typing.Optional[builtins.bool]:
        '''Whether to create recommended CloudWatch alarms.

        :default: - Alarms are created
        '''
        result = self._values.get("create_cloud_watch_alarms")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def existing_stream_obj(self) -> typing.Optional[aws_cdk.aws_kinesis.Stream]:
        '''Existing instance of Kinesis Stream, providing both this and ``kinesisStreamProps`` will cause an error.

        :default: - None
        '''
        result = self._values.get("existing_stream_obj")
        return typing.cast(typing.Optional[aws_cdk.aws_kinesis.Stream], result)

    @builtins.property
    def kinesis_stream_props(self) -> typing.Optional[aws_cdk.aws_kinesis.StreamProps]:
        '''Optional user-provided props to override the default props for the Kinesis Data Stream.

        :default: - Default properties are used.
        '''
        result = self._values.get("kinesis_stream_props")
        return typing.cast(typing.Optional[aws_cdk.aws_kinesis.StreamProps], result)

    @builtins.property
    def log_group_props(self) -> typing.Optional[aws_cdk.aws_logs.LogGroupProps]:
        '''User provided props to override the default props for the CloudWatchLogs LogGroup.

        :default: - Default props are used
        '''
        result = self._values.get("log_group_props")
        return typing.cast(typing.Optional[aws_cdk.aws_logs.LogGroupProps], result)

    @builtins.property
    def put_record_request_model(
        self,
    ) -> typing.Optional[aws_cdk.aws_apigateway.ModelOptions]:
        '''API Gateway request model for the PutRecord action.

        If not provided, a default one will be created.

        :default:

        - {"$schema":"http://json-schema.org/draft-04/schema#","title":"PutRecord proxy single-record payload","type":"object",
        "required":["data","partitionKey"],"properties":{"data":{"type":"string"},"partitionKey":{"type":"string"}}}
        '''
        result = self._values.get("put_record_request_model")
        return typing.cast(typing.Optional[aws_cdk.aws_apigateway.ModelOptions], result)

    @builtins.property
    def put_record_request_template(self) -> typing.Optional[builtins.str]:
        '''API Gateway request template for the PutRecord action.

        If not provided, a default one will be used.

        :default:

        - { "StreamName": "${this.kinesisStream.streamName}", "Data": "$util.base64Encode($input.json('$.data'))",
        "PartitionKey": "$input.path('$.partitionKey')" }
        '''
        result = self._values.get("put_record_request_template")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def put_records_request_model(
        self,
    ) -> typing.Optional[aws_cdk.aws_apigateway.ModelOptions]:
        '''API Gateway request model for the PutRecords action.

        If not provided, a default one will be created.

        :default:

        - {"$schema":"http://json-schema.org/draft-04/schema#","title":"PutRecords proxy payload data","type":"object","required":["records"],
        "properties":{"records":{"type":"array","items":{"type":"object",
        "required":["data","partitionKey"],"properties":{"data":{"type":"string"},"partitionKey":{"type":"string"}}}}}}
        '''
        result = self._values.get("put_records_request_model")
        return typing.cast(typing.Optional[aws_cdk.aws_apigateway.ModelOptions], result)

    @builtins.property
    def put_records_request_template(self) -> typing.Optional[builtins.str]:
        '''API Gateway request template for the PutRecords action.

        If not provided, a default one will be used.

        :default:

        - { "StreamName": "${this.kinesisStream.streamName}", "Records": [ #foreach($elem in $input.path('$.records'))
        { "Data": "$util.base64Encode($elem.data)", "PartitionKey": "$elem.partitionKey"}#if($foreach.hasNext),#end #end ] }
        '''
        result = self._values.get("put_records_request_template")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApiGatewayToKinesisStreamsProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ApiGatewayToKinesisStreams",
    "ApiGatewayToKinesisStreamsProps",
]

publication.publish()
