'''
# aws-dynamodbstreams-lambda module

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
|![Python Logo](https://docs.aws.amazon.com/cdk/api/latest/img/python32.png) Python|`aws_solutions_constructs.aws_dynamodbstreams_lambda`|
|![Typescript Logo](https://docs.aws.amazon.com/cdk/api/latest/img/typescript32.png) Typescript|`@aws-solutions-constructs/aws-dynamodbstreams-lambda`|
|![Java Logo](https://docs.aws.amazon.com/cdk/api/latest/img/java32.png) Java|`software.amazon.awsconstructs.services.dynamodbstreamslambda`|

This AWS Solutions Construct implements a pattern Amazon DynamoDB table with stream to invoke the AWS Lambda function  with the least privileged permissions.

Here is a minimal deployable pattern definition in Typescript:

```python
import { DynamoDBStreamsToLambdaProps,  DynamoDBStreamsToLambda} from '@aws-solutions-constructs/aws-dynamodbstreams-lambda';

new DynamoDBStreamsToLambda(this, 'test-dynamodbstreams-lambda', {
  lambdaFunctionProps: {
      code: lambda.Code.fromAsset(`${__dirname}/lambda`),
      runtime: lambda.Runtime.NODEJS_14_X,
      handler: 'index.handler'
  },
});
```

## Initializer

```text
new DynamoDBStreamsToLambda(scope: Construct, id: string, props: DynamoDBStreamsToLambdaProps);
```

*Parameters*

* scope [`Construct`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_core.Construct.html)
* id `string`
* props [`DynamoDBStreamsToLambdaProps`](#pattern-construct-props)

## Pattern Construct Props

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
|existingLambdaObj?|[`lambda.Function`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-lambda.Function.html)|Existing instance of Lambda Function object, providing both this and `lambdaFunctionProps` will cause an error.|
|lambdaFunctionProps?|[`lambda.FunctionProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-lambda.FunctionProps.html)|User provided props to override the default props for the Lambda function.|
|dynamoTableProps?|[`dynamodb.TableProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-dynamodb.TableProps.html)|Optional user provided props to override the default props for DynamoDB Table|
|existingTableInterface?|[`dynamodb.ITable`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-dynamodb.ITable.html)|Existing instance of DynamoDB table object or interface, providing both this and `dynamoTableProps` will cause an error.|
|dynamoEventSourceProps?|[`aws-lambda-event-sources.DynamoEventSourceProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-lambda-event-sources.DynamoEventSourceProps.html)|Optional user provided props to override the default props for DynamoDB Event Source|

## Pattern Properties

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
|dynamoTableInterface|[`dynamodb.ITable`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-dynamodb.ITable.html)|Returns an instance of dynamodb.ITable created by the construct|
|dynamoTable?|[`dynamodb.Table`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-dynamodb.Table.html)|Returns an instance of dynamodb.Table created by the construct. IMPORTANT: If existingTableInterface was provided in Pattern Construct Props, this property will be `undefined`|
|lambdaFunction|[`lambda.Function`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-lambda.Function.html)|Returns an instance of lambda.Function created by the construct|

## Lambda Function

This pattern requires a lambda function that can post data into the Elasticsearch. A sample function is provided [here](https://github.com/awslabs/aws-solutions-constructs/blob/master/source/patterns/%40aws-solutions-constructs/aws-dynamodbstreams-lambda-elasticsearch-kibana/test/lambda/index.js).

## Default settings

Out of the box implementation of the Construct without any override will set the following defaults:

### Amazon DynamoDB Table

* Set the billing mode for DynamoDB Table to On-Demand (Pay per request)
* Enable server-side encryption for DynamoDB Table using AWS managed KMS Key
* Creates a partition key called 'id' for DynamoDB Table
* Retain the Table when deleting the CloudFormation stack
* Enable continuous backups and point-in-time recovery

### AWS Lambda Function

* Configure limited privilege access IAM role for Lambda function
* Enable reusing connections with Keep-Alive for NodeJs Lambda function
* Enable X-Ray Tracing
* Enable Failure-Handling features like enable bisect on function Error, set defaults for Maximum Record Age (24 hours) & Maximum Retry Attempts (500) and deploy SQS dead-letter queue as destination on failure
* Set Environment Variables

  * AWS_NODEJS_CONNECTION_REUSE_ENABLED (for Node 10.x and higher functions)

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

import aws_cdk.aws_dynamodb
import aws_cdk.aws_lambda
import aws_cdk.aws_sqs
import aws_cdk.core


class DynamoDBStreamsToLambda(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-solutions-constructs/aws-dynamodbstreams-lambda.DynamoDBStreamsToLambda",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        deploy_sqs_dlq_queue: typing.Optional[builtins.bool] = None,
        dynamo_event_source_props: typing.Any = None,
        dynamo_table_props: typing.Optional[aws_cdk.aws_dynamodb.TableProps] = None,
        existing_lambda_obj: typing.Optional[aws_cdk.aws_lambda.Function] = None,
        existing_table_interface: typing.Optional[aws_cdk.aws_dynamodb.ITable] = None,
        lambda_function_props: typing.Optional[aws_cdk.aws_lambda.FunctionProps] = None,
        sqs_dlq_queue_props: typing.Optional[aws_cdk.aws_sqs.QueueProps] = None,
    ) -> None:
        '''
        :param scope: - represents the scope for all the resources.
        :param id: - this is a a scope-unique id.
        :param deploy_sqs_dlq_queue: Whether to deploy a SQS dead letter queue when a data record reaches the Maximum Retry Attempts or Maximum Record Age, its metadata like shard ID and stream ARN will be sent to an SQS queue. Default: - true.
        :param dynamo_event_source_props: Optional user provided props to override the default props. Default: - Default props are used
        :param dynamo_table_props: Optional user provided props to override the default props. Default: - Default props are used
        :param existing_lambda_obj: Existing instance of Lambda Function object, providing both this and ``lambdaFunctionProps`` will cause an error. Default: - None
        :param existing_table_interface: Existing instance of DynamoDB table object, providing both this and ``dynamoTableProps`` will cause an error. Default: - None
        :param lambda_function_props: User provided props to override the default props for the Lambda function. Default: - Default props are used
        :param sqs_dlq_queue_props: Optional user provided properties for the SQS dead letter queue. Default: - Default props are used

        :access: public
        :summary: Constructs a new instance of the LambdaToDynamoDB class.
        '''
        props = DynamoDBStreamsToLambdaProps(
            deploy_sqs_dlq_queue=deploy_sqs_dlq_queue,
            dynamo_event_source_props=dynamo_event_source_props,
            dynamo_table_props=dynamo_table_props,
            existing_lambda_obj=existing_lambda_obj,
            existing_table_interface=existing_table_interface,
            lambda_function_props=lambda_function_props,
            sqs_dlq_queue_props=sqs_dlq_queue_props,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dynamoTableInterface")
    def dynamo_table_interface(self) -> aws_cdk.aws_dynamodb.ITable:
        return typing.cast(aws_cdk.aws_dynamodb.ITable, jsii.get(self, "dynamoTableInterface"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambdaFunction")
    def lambda_function(self) -> aws_cdk.aws_lambda.Function:
        return typing.cast(aws_cdk.aws_lambda.Function, jsii.get(self, "lambdaFunction"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dynamoTable")
    def dynamo_table(self) -> typing.Optional[aws_cdk.aws_dynamodb.Table]:
        return typing.cast(typing.Optional[aws_cdk.aws_dynamodb.Table], jsii.get(self, "dynamoTable"))


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/aws-dynamodbstreams-lambda.DynamoDBStreamsToLambdaProps",
    jsii_struct_bases=[],
    name_mapping={
        "deploy_sqs_dlq_queue": "deploySqsDlqQueue",
        "dynamo_event_source_props": "dynamoEventSourceProps",
        "dynamo_table_props": "dynamoTableProps",
        "existing_lambda_obj": "existingLambdaObj",
        "existing_table_interface": "existingTableInterface",
        "lambda_function_props": "lambdaFunctionProps",
        "sqs_dlq_queue_props": "sqsDlqQueueProps",
    },
)
class DynamoDBStreamsToLambdaProps:
    def __init__(
        self,
        *,
        deploy_sqs_dlq_queue: typing.Optional[builtins.bool] = None,
        dynamo_event_source_props: typing.Any = None,
        dynamo_table_props: typing.Optional[aws_cdk.aws_dynamodb.TableProps] = None,
        existing_lambda_obj: typing.Optional[aws_cdk.aws_lambda.Function] = None,
        existing_table_interface: typing.Optional[aws_cdk.aws_dynamodb.ITable] = None,
        lambda_function_props: typing.Optional[aws_cdk.aws_lambda.FunctionProps] = None,
        sqs_dlq_queue_props: typing.Optional[aws_cdk.aws_sqs.QueueProps] = None,
    ) -> None:
        '''
        :param deploy_sqs_dlq_queue: Whether to deploy a SQS dead letter queue when a data record reaches the Maximum Retry Attempts or Maximum Record Age, its metadata like shard ID and stream ARN will be sent to an SQS queue. Default: - true.
        :param dynamo_event_source_props: Optional user provided props to override the default props. Default: - Default props are used
        :param dynamo_table_props: Optional user provided props to override the default props. Default: - Default props are used
        :param existing_lambda_obj: Existing instance of Lambda Function object, providing both this and ``lambdaFunctionProps`` will cause an error. Default: - None
        :param existing_table_interface: Existing instance of DynamoDB table object, providing both this and ``dynamoTableProps`` will cause an error. Default: - None
        :param lambda_function_props: User provided props to override the default props for the Lambda function. Default: - Default props are used
        :param sqs_dlq_queue_props: Optional user provided properties for the SQS dead letter queue. Default: - Default props are used

        :summary: The properties for the DynamoDBStreamsToLambda Construct
        '''
        if isinstance(dynamo_table_props, dict):
            dynamo_table_props = aws_cdk.aws_dynamodb.TableProps(**dynamo_table_props)
        if isinstance(lambda_function_props, dict):
            lambda_function_props = aws_cdk.aws_lambda.FunctionProps(**lambda_function_props)
        if isinstance(sqs_dlq_queue_props, dict):
            sqs_dlq_queue_props = aws_cdk.aws_sqs.QueueProps(**sqs_dlq_queue_props)
        self._values: typing.Dict[str, typing.Any] = {}
        if deploy_sqs_dlq_queue is not None:
            self._values["deploy_sqs_dlq_queue"] = deploy_sqs_dlq_queue
        if dynamo_event_source_props is not None:
            self._values["dynamo_event_source_props"] = dynamo_event_source_props
        if dynamo_table_props is not None:
            self._values["dynamo_table_props"] = dynamo_table_props
        if existing_lambda_obj is not None:
            self._values["existing_lambda_obj"] = existing_lambda_obj
        if existing_table_interface is not None:
            self._values["existing_table_interface"] = existing_table_interface
        if lambda_function_props is not None:
            self._values["lambda_function_props"] = lambda_function_props
        if sqs_dlq_queue_props is not None:
            self._values["sqs_dlq_queue_props"] = sqs_dlq_queue_props

    @builtins.property
    def deploy_sqs_dlq_queue(self) -> typing.Optional[builtins.bool]:
        '''Whether to deploy a SQS dead letter queue when a data record reaches the Maximum Retry Attempts or Maximum Record Age, its metadata like shard ID and stream ARN will be sent to an SQS queue.

        :default: - true.
        '''
        result = self._values.get("deploy_sqs_dlq_queue")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def dynamo_event_source_props(self) -> typing.Any:
        '''Optional user provided props to override the default props.

        :default: - Default props are used
        '''
        result = self._values.get("dynamo_event_source_props")
        return typing.cast(typing.Any, result)

    @builtins.property
    def dynamo_table_props(self) -> typing.Optional[aws_cdk.aws_dynamodb.TableProps]:
        '''Optional user provided props to override the default props.

        :default: - Default props are used
        '''
        result = self._values.get("dynamo_table_props")
        return typing.cast(typing.Optional[aws_cdk.aws_dynamodb.TableProps], result)

    @builtins.property
    def existing_lambda_obj(self) -> typing.Optional[aws_cdk.aws_lambda.Function]:
        '''Existing instance of Lambda Function object, providing both this and ``lambdaFunctionProps`` will cause an error.

        :default: - None
        '''
        result = self._values.get("existing_lambda_obj")
        return typing.cast(typing.Optional[aws_cdk.aws_lambda.Function], result)

    @builtins.property
    def existing_table_interface(self) -> typing.Optional[aws_cdk.aws_dynamodb.ITable]:
        '''Existing instance of DynamoDB table object, providing both this and ``dynamoTableProps`` will cause an error.

        :default: - None
        '''
        result = self._values.get("existing_table_interface")
        return typing.cast(typing.Optional[aws_cdk.aws_dynamodb.ITable], result)

    @builtins.property
    def lambda_function_props(
        self,
    ) -> typing.Optional[aws_cdk.aws_lambda.FunctionProps]:
        '''User provided props to override the default props for the Lambda function.

        :default: - Default props are used
        '''
        result = self._values.get("lambda_function_props")
        return typing.cast(typing.Optional[aws_cdk.aws_lambda.FunctionProps], result)

    @builtins.property
    def sqs_dlq_queue_props(self) -> typing.Optional[aws_cdk.aws_sqs.QueueProps]:
        '''Optional user provided properties for the SQS dead letter queue.

        :default: - Default props are used
        '''
        result = self._values.get("sqs_dlq_queue_props")
        return typing.cast(typing.Optional[aws_cdk.aws_sqs.QueueProps], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DynamoDBStreamsToLambdaProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "DynamoDBStreamsToLambda",
    "DynamoDBStreamsToLambdaProps",
]

publication.publish()
