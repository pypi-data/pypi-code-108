'''
# aws-apigateway-sqs module

<!--BEGIN STABILITY BANNER-->---


![Stability: Stable](https://img.shields.io/badge/cfn--resources-stable-success.svg?style=for-the-badge)

---
<!--END STABILITY BANNER-->

| **Reference Documentation**:| <span style="font-weight: normal">https://docs.aws.amazon.com/solutions/latest/constructs/</span>|
|:-------------|:-------------|

<div style="height:8px"></div>

| **Language**     | **Package**        |
|:-------------|-----------------|
|![Python Logo](https://docs.aws.amazon.com/cdk/api/latest/img/python32.png) Python|`aws_solutions_constructs.aws_apigateway_sqs`|
|![Typescript Logo](https://docs.aws.amazon.com/cdk/api/latest/img/typescript32.png) Typescript|`@aws-solutions-constructs/aws-apigateway-sqs`|
|![Java Logo](https://docs.aws.amazon.com/cdk/api/latest/img/java32.png) Java|`software.amazon.awsconstructs.services.apigatewaysqs`|

## Overview

This AWS Solutions Construct implements an Amazon API Gateway connected to an Amazon SQS queue pattern.

Here is a minimal deployable pattern definition in Typescript:

```python
import { ApiGatewayToSqs, ApiGatewayToSqsProps } from "@aws-solutions-constructs/aws-apigateway-sqs";

new ApiGatewayToSqs(this, 'ApiGatewayToSqsPattern', {});
```

## Initializer

```text
new ApiGatewayToSqs(scope: Construct, id: string, props: ApiGatewayToSqsProps);
```

*Parameters*

* scope [`Construct`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_core.Construct.html)
* id `string`
* props [`ApiGatewayToSqsProps`](#pattern-construct-props)

## Pattern Construct Props

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
|apiGatewayProps?|[`api.RestApiProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-apigateway.RestApiProps.html)|Optional user-provided props to override the default props for the API Gateway.|
|queueProps?|[`sqs.QueueProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-sqs.QueueProps.html)|Optional user-provided props to override the default props for the queue.|
|deployDeadLetterQueue?|`boolean`|Whether to deploy a secondary queue to be used as a dead letter queue. Defaults to `true`.|
|maxReceiveCount|`number`|The number of times a message can be unsuccessfully dequeued before being moved to the dead-letter queue.|
|allowCreateOperation?|`boolean`|Whether to deploy an API Gateway Method for Create operations on the queue (i.e. sqs:SendMessage).|
|createRequestTemplate?|`string`|Override the default API Gateway Request template for Create method, if allowCreateOperation set to true.|
|allowReadOperation?|`boolean`|Whether to deploy an API Gateway Method for Read operations on the queue (i.e. sqs:ReceiveMessage).|
|readRequestTemplate?|`string`|Override the default API Gateway Request template for Read method, if allowReadOperation set to true.|
|allowDeleteOperation?|`boolean`|Whether to deploy an API Gateway Method for Delete operations on the queue (i.e. sqs:DeleteMessage).|
|deleteRequestTemplate?|`string`|Override the default API Gateway Request template for Delete method, if allowDeleteOperation set to true.|
|logGroupProps?|[`logs.LogGroupProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-logs.LogGroupProps.html)|User provided props to override the default props for for the CloudWatchLogs LogGroup.|

## Pattern Properties

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
|apiGateway|[`api.RestApi`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-apigateway.RestApi.html)|Returns an instance of the API Gateway REST API created by the pattern.|
|apiGatewayRole|[`iam.Role`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-iam.Role.html)|Returns an instance of the iam.Role created by the construct for API Gateway.|
|apiGatewayCloudWatchRole?|[`iam.Role`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-iam.Role.html)|Returns an instance of the iam.Role created by the construct for API Gateway for CloudWatch access.|
|apiGatewayLogGroup|[`logs.LogGroup`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-logs.LogGroup.html)|Returns an instance of the LogGroup created by the construct for API Gateway access logging to CloudWatch.|
|sqsQueue|[`sqs.Queue`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-sqs.Queue.html)|Returns an instance of the SQS queue created by the pattern.|
|deadLetterQueue?|[`sqs.DeadLetterQueue`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-sqs.DeadLetterQueue.html)|Returns an instance of the DeadLetterQueue created by the pattern.|

## Sample API Usage

| **Method** | **Request Path** | **Request Body** | **Queue Action** | **Description** |
|:-------------|:----------------|-----------------|-----------------|-----------------|
|GET|`/`| |`sqs::ReceiveMessage`|Retrieves a message from the queue.|
|POST|`/`| `{ "data": "Hello World!" }` |`sqs::SendMessage`|Delivers a message to the queue.|
|DELETE|`/message?receiptHandle=[value]`||`sqs::DeleteMessage`|Deletes a specified message from the queue|

## Default settings

Out of the box implementation of the Construct without any override will set the following defaults:

### Amazon API Gateway

* Deploy an edge-optimized API endpoint
* Enable CloudWatch logging for API Gateway
* Configure least privilege access IAM role for API Gateway
* Set the default authorizationType for all API methods to IAM
* Enable X-Ray Tracing

### Amazon SQS Queue

* Deploy SQS dead-letter queue for the source SQS Queue
* Enable server-side encryption for source SQS Queue using AWS Managed KMS Key
* Enforce encryption of data in transit

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
import aws_cdk.aws_iam
import aws_cdk.aws_logs
import aws_cdk.aws_sqs
import aws_cdk.core


class ApiGatewayToSqs(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-solutions-constructs/aws-apigateway-sqs.ApiGatewayToSqs",
):
    '''
    :summary: The ApiGatewayToSqs class.
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        allow_create_operation: typing.Optional[builtins.bool] = None,
        allow_delete_operation: typing.Optional[builtins.bool] = None,
        allow_read_operation: typing.Optional[builtins.bool] = None,
        api_gateway_props: typing.Any = None,
        create_request_template: typing.Optional[builtins.str] = None,
        dead_letter_queue_props: typing.Optional[aws_cdk.aws_sqs.QueueProps] = None,
        delete_request_template: typing.Optional[builtins.str] = None,
        deploy_dead_letter_queue: typing.Optional[builtins.bool] = None,
        existing_queue_obj: typing.Optional[aws_cdk.aws_sqs.Queue] = None,
        log_group_props: typing.Optional[aws_cdk.aws_logs.LogGroupProps] = None,
        max_receive_count: typing.Optional[jsii.Number] = None,
        queue_props: typing.Optional[aws_cdk.aws_sqs.QueueProps] = None,
        read_request_template: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: - represents the scope for all the resources.
        :param id: - this is a a scope-unique id.
        :param allow_create_operation: Whether to deploy an API Gateway Method for Create operations on the queue (i.e. sqs:SendMessage). Default: - false
        :param allow_delete_operation: Whether to deploy an API Gateway Method for Delete operations on the queue (i.e. sqs:DeleteMessage). Default: - false
        :param allow_read_operation: Whether to deploy an API Gateway Method for Read operations on the queue (i.e. sqs:ReceiveMessage). Default: - "Action=SendMessage&MessageBody=$util.urlEncode("$input.body")"
        :param api_gateway_props: Optional user-provided props to override the default props for the API Gateway. Default: - Default properties are used.
        :param create_request_template: API Gateway Request template for Create method, if allowCreateOperation set to true. Default: - None
        :param dead_letter_queue_props: Optional user provided properties for the dead letter queue. Default: - Default props are used
        :param delete_request_template: API Gateway Request template for Delete method, if allowDeleteOperation set to true. Default: - "Action=DeleteMessage&ReceiptHandle=$util.urlEncode($input.params('receiptHandle'))"
        :param deploy_dead_letter_queue: Whether to deploy a secondary queue to be used as a dead letter queue. Default: - required field.
        :param existing_queue_obj: Existing instance of SQS queue object, providing both this and queueProps will cause an error. Default: - None
        :param log_group_props: User provided props to override the default props for the CloudWatchLogs LogGroup. Default: - Default props are used
        :param max_receive_count: The number of times a message can be unsuccessfully dequeued before being moved to the dead-letter queue. Default: - required only if deployDeadLetterQueue = true.
        :param queue_props: User provided props to override the default props for the SQS queue. Default: - Default props are used
        :param read_request_template: API Gateway Request template for Get method, if allowReadOperation set to true. Default: - "Action=ReceiveMessage"

        :access: public
        :since: 0.8.0
        :summary: Constructs a new instance of the ApiGatewayToSqs class.
        '''
        props = ApiGatewayToSqsProps(
            allow_create_operation=allow_create_operation,
            allow_delete_operation=allow_delete_operation,
            allow_read_operation=allow_read_operation,
            api_gateway_props=api_gateway_props,
            create_request_template=create_request_template,
            dead_letter_queue_props=dead_letter_queue_props,
            delete_request_template=delete_request_template,
            deploy_dead_letter_queue=deploy_dead_letter_queue,
            existing_queue_obj=existing_queue_obj,
            log_group_props=log_group_props,
            max_receive_count=max_receive_count,
            queue_props=queue_props,
            read_request_template=read_request_template,
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
    @jsii.member(jsii_name="sqsQueue")
    def sqs_queue(self) -> aws_cdk.aws_sqs.Queue:
        return typing.cast(aws_cdk.aws_sqs.Queue, jsii.get(self, "sqsQueue"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiGatewayCloudWatchRole")
    def api_gateway_cloud_watch_role(self) -> typing.Optional[aws_cdk.aws_iam.Role]:
        return typing.cast(typing.Optional[aws_cdk.aws_iam.Role], jsii.get(self, "apiGatewayCloudWatchRole"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deadLetterQueue")
    def dead_letter_queue(self) -> typing.Optional[aws_cdk.aws_sqs.DeadLetterQueue]:
        return typing.cast(typing.Optional[aws_cdk.aws_sqs.DeadLetterQueue], jsii.get(self, "deadLetterQueue"))


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/aws-apigateway-sqs.ApiGatewayToSqsProps",
    jsii_struct_bases=[],
    name_mapping={
        "allow_create_operation": "allowCreateOperation",
        "allow_delete_operation": "allowDeleteOperation",
        "allow_read_operation": "allowReadOperation",
        "api_gateway_props": "apiGatewayProps",
        "create_request_template": "createRequestTemplate",
        "dead_letter_queue_props": "deadLetterQueueProps",
        "delete_request_template": "deleteRequestTemplate",
        "deploy_dead_letter_queue": "deployDeadLetterQueue",
        "existing_queue_obj": "existingQueueObj",
        "log_group_props": "logGroupProps",
        "max_receive_count": "maxReceiveCount",
        "queue_props": "queueProps",
        "read_request_template": "readRequestTemplate",
    },
)
class ApiGatewayToSqsProps:
    def __init__(
        self,
        *,
        allow_create_operation: typing.Optional[builtins.bool] = None,
        allow_delete_operation: typing.Optional[builtins.bool] = None,
        allow_read_operation: typing.Optional[builtins.bool] = None,
        api_gateway_props: typing.Any = None,
        create_request_template: typing.Optional[builtins.str] = None,
        dead_letter_queue_props: typing.Optional[aws_cdk.aws_sqs.QueueProps] = None,
        delete_request_template: typing.Optional[builtins.str] = None,
        deploy_dead_letter_queue: typing.Optional[builtins.bool] = None,
        existing_queue_obj: typing.Optional[aws_cdk.aws_sqs.Queue] = None,
        log_group_props: typing.Optional[aws_cdk.aws_logs.LogGroupProps] = None,
        max_receive_count: typing.Optional[jsii.Number] = None,
        queue_props: typing.Optional[aws_cdk.aws_sqs.QueueProps] = None,
        read_request_template: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param allow_create_operation: Whether to deploy an API Gateway Method for Create operations on the queue (i.e. sqs:SendMessage). Default: - false
        :param allow_delete_operation: Whether to deploy an API Gateway Method for Delete operations on the queue (i.e. sqs:DeleteMessage). Default: - false
        :param allow_read_operation: Whether to deploy an API Gateway Method for Read operations on the queue (i.e. sqs:ReceiveMessage). Default: - "Action=SendMessage&MessageBody=$util.urlEncode("$input.body")"
        :param api_gateway_props: Optional user-provided props to override the default props for the API Gateway. Default: - Default properties are used.
        :param create_request_template: API Gateway Request template for Create method, if allowCreateOperation set to true. Default: - None
        :param dead_letter_queue_props: Optional user provided properties for the dead letter queue. Default: - Default props are used
        :param delete_request_template: API Gateway Request template for Delete method, if allowDeleteOperation set to true. Default: - "Action=DeleteMessage&ReceiptHandle=$util.urlEncode($input.params('receiptHandle'))"
        :param deploy_dead_letter_queue: Whether to deploy a secondary queue to be used as a dead letter queue. Default: - required field.
        :param existing_queue_obj: Existing instance of SQS queue object, providing both this and queueProps will cause an error. Default: - None
        :param log_group_props: User provided props to override the default props for the CloudWatchLogs LogGroup. Default: - Default props are used
        :param max_receive_count: The number of times a message can be unsuccessfully dequeued before being moved to the dead-letter queue. Default: - required only if deployDeadLetterQueue = true.
        :param queue_props: User provided props to override the default props for the SQS queue. Default: - Default props are used
        :param read_request_template: API Gateway Request template for Get method, if allowReadOperation set to true. Default: - "Action=ReceiveMessage"

        :summary: The properties for the ApiGatewayToSqs class.
        '''
        if isinstance(dead_letter_queue_props, dict):
            dead_letter_queue_props = aws_cdk.aws_sqs.QueueProps(**dead_letter_queue_props)
        if isinstance(log_group_props, dict):
            log_group_props = aws_cdk.aws_logs.LogGroupProps(**log_group_props)
        if isinstance(queue_props, dict):
            queue_props = aws_cdk.aws_sqs.QueueProps(**queue_props)
        self._values: typing.Dict[str, typing.Any] = {}
        if allow_create_operation is not None:
            self._values["allow_create_operation"] = allow_create_operation
        if allow_delete_operation is not None:
            self._values["allow_delete_operation"] = allow_delete_operation
        if allow_read_operation is not None:
            self._values["allow_read_operation"] = allow_read_operation
        if api_gateway_props is not None:
            self._values["api_gateway_props"] = api_gateway_props
        if create_request_template is not None:
            self._values["create_request_template"] = create_request_template
        if dead_letter_queue_props is not None:
            self._values["dead_letter_queue_props"] = dead_letter_queue_props
        if delete_request_template is not None:
            self._values["delete_request_template"] = delete_request_template
        if deploy_dead_letter_queue is not None:
            self._values["deploy_dead_letter_queue"] = deploy_dead_letter_queue
        if existing_queue_obj is not None:
            self._values["existing_queue_obj"] = existing_queue_obj
        if log_group_props is not None:
            self._values["log_group_props"] = log_group_props
        if max_receive_count is not None:
            self._values["max_receive_count"] = max_receive_count
        if queue_props is not None:
            self._values["queue_props"] = queue_props
        if read_request_template is not None:
            self._values["read_request_template"] = read_request_template

    @builtins.property
    def allow_create_operation(self) -> typing.Optional[builtins.bool]:
        '''Whether to deploy an API Gateway Method for Create operations on the queue (i.e. sqs:SendMessage).

        :default: - false
        '''
        result = self._values.get("allow_create_operation")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def allow_delete_operation(self) -> typing.Optional[builtins.bool]:
        '''Whether to deploy an API Gateway Method for Delete operations on the queue (i.e. sqs:DeleteMessage).

        :default: - false
        '''
        result = self._values.get("allow_delete_operation")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def allow_read_operation(self) -> typing.Optional[builtins.bool]:
        '''Whether to deploy an API Gateway Method for Read operations on the queue (i.e. sqs:ReceiveMessage).

        :default: - "Action=SendMessage&MessageBody=$util.urlEncode("$input.body")"
        '''
        result = self._values.get("allow_read_operation")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def api_gateway_props(self) -> typing.Any:
        '''Optional user-provided props to override the default props for the API Gateway.

        :default: - Default properties are used.
        '''
        result = self._values.get("api_gateway_props")
        return typing.cast(typing.Any, result)

    @builtins.property
    def create_request_template(self) -> typing.Optional[builtins.str]:
        '''API Gateway Request template for Create method, if allowCreateOperation set to true.

        :default: - None
        '''
        result = self._values.get("create_request_template")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def dead_letter_queue_props(self) -> typing.Optional[aws_cdk.aws_sqs.QueueProps]:
        '''Optional user provided properties for the dead letter queue.

        :default: - Default props are used
        '''
        result = self._values.get("dead_letter_queue_props")
        return typing.cast(typing.Optional[aws_cdk.aws_sqs.QueueProps], result)

    @builtins.property
    def delete_request_template(self) -> typing.Optional[builtins.str]:
        '''API Gateway Request template for Delete method, if allowDeleteOperation set to true.

        :default: - "Action=DeleteMessage&ReceiptHandle=$util.urlEncode($input.params('receiptHandle'))"
        '''
        result = self._values.get("delete_request_template")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def deploy_dead_letter_queue(self) -> typing.Optional[builtins.bool]:
        '''Whether to deploy a secondary queue to be used as a dead letter queue.

        :default: - required field.
        '''
        result = self._values.get("deploy_dead_letter_queue")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def existing_queue_obj(self) -> typing.Optional[aws_cdk.aws_sqs.Queue]:
        '''Existing instance of SQS queue object, providing both this  and queueProps will cause an error.

        :default: - None
        '''
        result = self._values.get("existing_queue_obj")
        return typing.cast(typing.Optional[aws_cdk.aws_sqs.Queue], result)

    @builtins.property
    def log_group_props(self) -> typing.Optional[aws_cdk.aws_logs.LogGroupProps]:
        '''User provided props to override the default props for the CloudWatchLogs LogGroup.

        :default: - Default props are used
        '''
        result = self._values.get("log_group_props")
        return typing.cast(typing.Optional[aws_cdk.aws_logs.LogGroupProps], result)

    @builtins.property
    def max_receive_count(self) -> typing.Optional[jsii.Number]:
        '''The number of times a message can be unsuccessfully dequeued before being moved to the dead-letter queue.

        :default: - required only if deployDeadLetterQueue = true.
        '''
        result = self._values.get("max_receive_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def queue_props(self) -> typing.Optional[aws_cdk.aws_sqs.QueueProps]:
        '''User provided props to override the default props for the SQS queue.

        :default: - Default props are used
        '''
        result = self._values.get("queue_props")
        return typing.cast(typing.Optional[aws_cdk.aws_sqs.QueueProps], result)

    @builtins.property
    def read_request_template(self) -> typing.Optional[builtins.str]:
        '''API Gateway Request template for Get method, if allowReadOperation set to true.

        :default: - "Action=ReceiveMessage"
        '''
        result = self._values.get("read_request_template")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApiGatewayToSqsProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ApiGatewayToSqs",
    "ApiGatewayToSqsProps",
]

publication.publish()
