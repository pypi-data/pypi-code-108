'''
# aws-lambda-sqs-lambda module

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
|![Python Logo](https://docs.aws.amazon.com/cdk/api/latest/img/python32.png) Python|`aws_solutions_constructs.aws_lambda_sqs_lambda`|
|![Typescript Logo](https://docs.aws.amazon.com/cdk/api/latest/img/typescript32.png) Typescript|`@aws-solutions-constructs/aws-lambda-sqs-lambda`|
|![Java Logo](https://docs.aws.amazon.com/cdk/api/latest/img/java32.png) Java|`software.amazon.awsconstructs.services.lambdasqslambda`|

This AWS Solutions Construct implements (1) an AWS Lambda function that is configured to send messages to a queue; (2) an Amazon SQS queue; and (3) an AWS Lambda function configured to consume messages from the queue.

Here is a minimal deployable pattern definition in Typescript:

```python
import { LambdaToSqsToLambda, LambdaToSqsToLambdaProps } from "@aws-solutions-constructs/aws-lambda-sqs-lambda";

new LambdaToSqsToLambda(this, 'LambdaToSqsToLambdaPattern', {
  producerLambdaFunctionProps: {
      runtime: lambda.Runtime.NODEJS_14_X,
      handler: 'index.handler',
      code: lambda.Code.fromAsset(`${__dirname}/lambda/producer-function`)
  },
  consumerLambdaFunctionProps: {
    runtime: lambda.Runtime.NODEJS_14_X,
    handler: 'index.handler',
    code: lambda.Code.fromAsset(`${__dirname}/lambda/consumer-function`)
  }
});
```

## Initializer

```text
new LambdaToSqsToLambda(scope: Construct, id: string, props: LambdaToSqsToLambdaProps);
```

*Parameters*

* scope [`Construct`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_core.Construct.html)
* id `string`
* props [`LambdaToSqsToLambdaProps`](#pattern-construct-props)

## Pattern Construct Props

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
|existingProducerLambdaObj?|[`lambda.Function`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-lambda.Function.html)|An optional, existing Lambda function to be used instead of the default function for sending messages to the queue. Providing both this and `producerLambdaFunctionProps` will cause an error. |
|producerLambdaFunctionProps?|[`lambda.FunctionProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-lambda.FunctionProps.html)|Optional user-provided properties to override the default properties for the producer Lambda function. |
|existingQueueObj?|[`sqs.Queue`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-sqs.Queue.html)|An optional, existing SQS queue to be used instead of the default queue. Providing both this and `queueProps` will cause an error.|
|queueProps?|[`sqs.QueueProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-sqs.QueueProps.html)|Optional user-provided properties to override the default properties for the SQS queue. Providing both this and `existingQueueObj` will cause an error. |
|deployDeadLetterQueue?|`boolean`|Whether to create a secondary queue to be used as a dead letter queue. Defaults to `true`.|
|deadLetterQueueProps?|[`sqs.QueueProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-sqs.QueueProps.html)|Optional user-provided props to override the default props for the dead letter queue. Only used if the `deployDeadLetterQueue` property is set to `true`.|
|maxReceiveCount?|`number`|The number of times a message can be unsuccessfully dequeued before being moved to the dead letter queue. Defaults to `15`.|
|existingConsumerLambdaObj?|[`lambda.Function`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-lambda.Function.html)|An optional, existing Lambda function to be used instead of the default function for receiving/consuming messages from the queue. Providing both this and `consumerLambdaFunctionProps` will cause an error. |
|consumerLambdaFunctionProps?|[`lambda.FunctionProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-lambda.FunctionProps.html)|Optional user-provided properties to override the default properties for the consumer Lambda function.|
|queueEnvironmentVariableName?|`string`|Optional Name for the SQS queue URL environment variable set for the producer Lambda function.|
|sqsEventSourceProps?| [`SqsEventSourceProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-lambda-event-sources.SqsEventSourceProps.html)|Optional user provided properties for the queue event source.|
|existingVpc?|[`ec2.IVpc`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-ec2.IVpc.html)|An optional, existing VPC into which this pattern should be deployed. When deployed in a VPC, the Lambda function will use ENIs in the VPC to access network resources and an Interface Endpoint will be created in the VPC for Amazon SQS. If an existing VPC is provided, the `deployVpc` property cannot be `true`. This uses `ec2.IVpc` to allow clients to supply VPCs that exist outside the stack using the [`ec2.Vpc.fromLookup()`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-ec2.Vpc.html#static-fromwbrlookupscope-id-options) method.|
|vpcProps?|[`ec2.VpcProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-ec2.VpcProps.html)|Optional user-provided properties to override the default properties for the new VPC. `enableDnsHostnames`, `enableDnsSupport`, `natGateways` and `subnetConfiguration` are set by the pattern, so any values for those properties supplied here will be overrriden. If `deployVpc` is not `true` then this property will be ignored.|
|deployVpc?|`boolean`|Whether to create a new VPC based on `vpcProps` into which to deploy this pattern. Setting this to true will deploy the minimal, most private VPC to run the pattern:<ul><li> One isolated subnet in each Availability Zone used by the CDK program</li><li>`enableDnsHostnames` and `enableDnsSupport` will both be set to true</li></ul>If this property is `true` then `existingVpc` cannot be specified. Defaults to `false`.|

## Pattern Properties

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
|producerLambdaFunction|[`lambda.Function`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-lambda.Function.html)|Returns an instance of the producer Lambda function created by the pattern.|
|sqsQueue|[`sqs.Queue`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-sqs.Queue.html)|Returns an instance of the SQS queue created by the pattern. |
|deadLetterQueue?|[`sqs.Queue \| undefined`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-sqs.Queue.html)|Returns an instance of the dead letter queue created by the pattern, if one is deployed.|
|consumerLambdaFunction|[`lambda.Function`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-lambda.Function.html)|Returns an instance of the consumer Lambda function created by the pattern.|
|vpc?|[`ec2.IVpc`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-ec2.IVpc.html)|Returns an interface on the VPC used by the pattern (if any). This may be a VPC created by the pattern or the VPC supplied to the pattern constructor.|

## Default Settings

Out-of-the-box implementation of this Construct (without any overridden properties) will adhere to the following defaults:

### AWS Lambda Functions

* Configure limited privilege access IAM role for Lambda functions.
* Enable reusing connections with Keep-Alive for NodeJs Lambda functions.
* Enable X-Ray Tracing
* Set Environment Variables

  * AWS_NODEJS_CONNECTION_REUSE_ENABLED (for Node 10.x and higher functions)

### Amazon SQS Queue

* Deploy a dead letter queue for the primary queue.
* Enable server-side encryption for the primary queue using an AWS Managed KMS Key.
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

import aws_cdk.aws_ec2
import aws_cdk.aws_lambda
import aws_cdk.aws_lambda_event_sources
import aws_cdk.aws_sqs
import aws_cdk.core


class LambdaToSqsToLambda(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-solutions-constructs/aws-lambda-sqs-lambda.LambdaToSqsToLambda",
):
    '''
    :summary: The LambdaToSqsToLambda class.
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        consumer_lambda_function_props: typing.Optional[aws_cdk.aws_lambda.FunctionProps] = None,
        dead_letter_queue_props: typing.Optional[aws_cdk.aws_sqs.QueueProps] = None,
        deploy_dead_letter_queue: typing.Optional[builtins.bool] = None,
        deploy_vpc: typing.Optional[builtins.bool] = None,
        existing_consumer_lambda_obj: typing.Optional[aws_cdk.aws_lambda.Function] = None,
        existing_producer_lambda_obj: typing.Optional[aws_cdk.aws_lambda.Function] = None,
        existing_queue_obj: typing.Optional[aws_cdk.aws_sqs.Queue] = None,
        existing_vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
        max_receive_count: typing.Optional[jsii.Number] = None,
        producer_lambda_function_props: typing.Optional[aws_cdk.aws_lambda.FunctionProps] = None,
        queue_environment_variable_name: typing.Optional[builtins.str] = None,
        queue_props: typing.Optional[aws_cdk.aws_sqs.QueueProps] = None,
        sqs_event_source_props: typing.Optional[aws_cdk.aws_lambda_event_sources.SqsEventSourceProps] = None,
        vpc_props: typing.Optional[aws_cdk.aws_ec2.VpcProps] = None,
    ) -> None:
        '''
        :param scope: - represents the scope for all the resources.
        :param id: - this is a a scope-unique id.
        :param consumer_lambda_function_props: Optional user-provided properties to override the default properties for the consumer Lambda function. Default: - Default properties are used.
        :param dead_letter_queue_props: Optional user-provided props to override the default props for the dead letter queue. Only used if the ``deployDeadLetterQueue`` property is set to true. Default: - Default props are used.
        :param deploy_dead_letter_queue: Whether to create a secondary queue to be used as a dead letter queue. Defaults to ``true``. Default: - true.
        :param deploy_vpc: Whether to deploy a new VPC. Default: - false
        :param existing_consumer_lambda_obj: An optional, existing Lambda function to be used instead of the default function for receiving/consuming messages from the queue. Providing both this and ``consumerLambdaFunctionProps`` will cause an error. Default: - None.
        :param existing_producer_lambda_obj: An optional, existing Lambda function to be used instead of the default function for sending messages to the queue. Providing both this and ``producerLambdaFunctionProps`` property will cause an error. Default: - None.
        :param existing_queue_obj: An optional, existing SQS queue to be used instead of the default queue. Providing both this and ``queueProps`` will cause an error. Default: - None.
        :param existing_vpc: An existing VPC for the construct to use (construct will NOT create a new VPC in this case).
        :param max_receive_count: The number of times a message can be unsuccessfully dequeued before being moved to the dead letter queue. Defaults to ``15``. Default: - 15.
        :param producer_lambda_function_props: Optional user-provided properties to override the default properties for the producer Lambda function. Default: - Default properties are used.
        :param queue_environment_variable_name: Optional Name for the SQS queue URL environment variable set for the producer Lambda function. Default: - None
        :param queue_props: Optional user-provided properties to override the default properties for the SQS queue. Default: - Default props are used.
        :param sqs_event_source_props: Optional user provided properties for the queue event source. Default: - Default props are used
        :param vpc_props: Properties to override default properties if deployVpc is true.

        :access: public
        :summary: Constructs a new instance of the LambdaToSqsToLambda class.
        '''
        props = LambdaToSqsToLambdaProps(
            consumer_lambda_function_props=consumer_lambda_function_props,
            dead_letter_queue_props=dead_letter_queue_props,
            deploy_dead_letter_queue=deploy_dead_letter_queue,
            deploy_vpc=deploy_vpc,
            existing_consumer_lambda_obj=existing_consumer_lambda_obj,
            existing_producer_lambda_obj=existing_producer_lambda_obj,
            existing_queue_obj=existing_queue_obj,
            existing_vpc=existing_vpc,
            max_receive_count=max_receive_count,
            producer_lambda_function_props=producer_lambda_function_props,
            queue_environment_variable_name=queue_environment_variable_name,
            queue_props=queue_props,
            sqs_event_source_props=sqs_event_source_props,
            vpc_props=vpc_props,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="consumerLambdaFunction")
    def consumer_lambda_function(self) -> aws_cdk.aws_lambda.Function:
        return typing.cast(aws_cdk.aws_lambda.Function, jsii.get(self, "consumerLambdaFunction"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="producerLambdaFunction")
    def producer_lambda_function(self) -> aws_cdk.aws_lambda.Function:
        return typing.cast(aws_cdk.aws_lambda.Function, jsii.get(self, "producerLambdaFunction"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sqsQueue")
    def sqs_queue(self) -> aws_cdk.aws_sqs.Queue:
        return typing.cast(aws_cdk.aws_sqs.Queue, jsii.get(self, "sqsQueue"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deadLetterQueue")
    def dead_letter_queue(self) -> typing.Optional[aws_cdk.aws_sqs.DeadLetterQueue]:
        return typing.cast(typing.Optional[aws_cdk.aws_sqs.DeadLetterQueue], jsii.get(self, "deadLetterQueue"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> typing.Optional[aws_cdk.aws_ec2.IVpc]:
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.IVpc], jsii.get(self, "vpc"))


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/aws-lambda-sqs-lambda.LambdaToSqsToLambdaProps",
    jsii_struct_bases=[],
    name_mapping={
        "consumer_lambda_function_props": "consumerLambdaFunctionProps",
        "dead_letter_queue_props": "deadLetterQueueProps",
        "deploy_dead_letter_queue": "deployDeadLetterQueue",
        "deploy_vpc": "deployVpc",
        "existing_consumer_lambda_obj": "existingConsumerLambdaObj",
        "existing_producer_lambda_obj": "existingProducerLambdaObj",
        "existing_queue_obj": "existingQueueObj",
        "existing_vpc": "existingVpc",
        "max_receive_count": "maxReceiveCount",
        "producer_lambda_function_props": "producerLambdaFunctionProps",
        "queue_environment_variable_name": "queueEnvironmentVariableName",
        "queue_props": "queueProps",
        "sqs_event_source_props": "sqsEventSourceProps",
        "vpc_props": "vpcProps",
    },
)
class LambdaToSqsToLambdaProps:
    def __init__(
        self,
        *,
        consumer_lambda_function_props: typing.Optional[aws_cdk.aws_lambda.FunctionProps] = None,
        dead_letter_queue_props: typing.Optional[aws_cdk.aws_sqs.QueueProps] = None,
        deploy_dead_letter_queue: typing.Optional[builtins.bool] = None,
        deploy_vpc: typing.Optional[builtins.bool] = None,
        existing_consumer_lambda_obj: typing.Optional[aws_cdk.aws_lambda.Function] = None,
        existing_producer_lambda_obj: typing.Optional[aws_cdk.aws_lambda.Function] = None,
        existing_queue_obj: typing.Optional[aws_cdk.aws_sqs.Queue] = None,
        existing_vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
        max_receive_count: typing.Optional[jsii.Number] = None,
        producer_lambda_function_props: typing.Optional[aws_cdk.aws_lambda.FunctionProps] = None,
        queue_environment_variable_name: typing.Optional[builtins.str] = None,
        queue_props: typing.Optional[aws_cdk.aws_sqs.QueueProps] = None,
        sqs_event_source_props: typing.Optional[aws_cdk.aws_lambda_event_sources.SqsEventSourceProps] = None,
        vpc_props: typing.Optional[aws_cdk.aws_ec2.VpcProps] = None,
    ) -> None:
        '''
        :param consumer_lambda_function_props: Optional user-provided properties to override the default properties for the consumer Lambda function. Default: - Default properties are used.
        :param dead_letter_queue_props: Optional user-provided props to override the default props for the dead letter queue. Only used if the ``deployDeadLetterQueue`` property is set to true. Default: - Default props are used.
        :param deploy_dead_letter_queue: Whether to create a secondary queue to be used as a dead letter queue. Defaults to ``true``. Default: - true.
        :param deploy_vpc: Whether to deploy a new VPC. Default: - false
        :param existing_consumer_lambda_obj: An optional, existing Lambda function to be used instead of the default function for receiving/consuming messages from the queue. Providing both this and ``consumerLambdaFunctionProps`` will cause an error. Default: - None.
        :param existing_producer_lambda_obj: An optional, existing Lambda function to be used instead of the default function for sending messages to the queue. Providing both this and ``producerLambdaFunctionProps`` property will cause an error. Default: - None.
        :param existing_queue_obj: An optional, existing SQS queue to be used instead of the default queue. Providing both this and ``queueProps`` will cause an error. Default: - None.
        :param existing_vpc: An existing VPC for the construct to use (construct will NOT create a new VPC in this case).
        :param max_receive_count: The number of times a message can be unsuccessfully dequeued before being moved to the dead letter queue. Defaults to ``15``. Default: - 15.
        :param producer_lambda_function_props: Optional user-provided properties to override the default properties for the producer Lambda function. Default: - Default properties are used.
        :param queue_environment_variable_name: Optional Name for the SQS queue URL environment variable set for the producer Lambda function. Default: - None
        :param queue_props: Optional user-provided properties to override the default properties for the SQS queue. Default: - Default props are used.
        :param sqs_event_source_props: Optional user provided properties for the queue event source. Default: - Default props are used
        :param vpc_props: Properties to override default properties if deployVpc is true.

        :summary: The properties for the LambdaToSqsToLambda class.
        '''
        if isinstance(consumer_lambda_function_props, dict):
            consumer_lambda_function_props = aws_cdk.aws_lambda.FunctionProps(**consumer_lambda_function_props)
        if isinstance(dead_letter_queue_props, dict):
            dead_letter_queue_props = aws_cdk.aws_sqs.QueueProps(**dead_letter_queue_props)
        if isinstance(producer_lambda_function_props, dict):
            producer_lambda_function_props = aws_cdk.aws_lambda.FunctionProps(**producer_lambda_function_props)
        if isinstance(queue_props, dict):
            queue_props = aws_cdk.aws_sqs.QueueProps(**queue_props)
        if isinstance(sqs_event_source_props, dict):
            sqs_event_source_props = aws_cdk.aws_lambda_event_sources.SqsEventSourceProps(**sqs_event_source_props)
        if isinstance(vpc_props, dict):
            vpc_props = aws_cdk.aws_ec2.VpcProps(**vpc_props)
        self._values: typing.Dict[str, typing.Any] = {}
        if consumer_lambda_function_props is not None:
            self._values["consumer_lambda_function_props"] = consumer_lambda_function_props
        if dead_letter_queue_props is not None:
            self._values["dead_letter_queue_props"] = dead_letter_queue_props
        if deploy_dead_letter_queue is not None:
            self._values["deploy_dead_letter_queue"] = deploy_dead_letter_queue
        if deploy_vpc is not None:
            self._values["deploy_vpc"] = deploy_vpc
        if existing_consumer_lambda_obj is not None:
            self._values["existing_consumer_lambda_obj"] = existing_consumer_lambda_obj
        if existing_producer_lambda_obj is not None:
            self._values["existing_producer_lambda_obj"] = existing_producer_lambda_obj
        if existing_queue_obj is not None:
            self._values["existing_queue_obj"] = existing_queue_obj
        if existing_vpc is not None:
            self._values["existing_vpc"] = existing_vpc
        if max_receive_count is not None:
            self._values["max_receive_count"] = max_receive_count
        if producer_lambda_function_props is not None:
            self._values["producer_lambda_function_props"] = producer_lambda_function_props
        if queue_environment_variable_name is not None:
            self._values["queue_environment_variable_name"] = queue_environment_variable_name
        if queue_props is not None:
            self._values["queue_props"] = queue_props
        if sqs_event_source_props is not None:
            self._values["sqs_event_source_props"] = sqs_event_source_props
        if vpc_props is not None:
            self._values["vpc_props"] = vpc_props

    @builtins.property
    def consumer_lambda_function_props(
        self,
    ) -> typing.Optional[aws_cdk.aws_lambda.FunctionProps]:
        '''Optional user-provided properties to override the default properties for the consumer Lambda function.

        :default: - Default properties are used.
        '''
        result = self._values.get("consumer_lambda_function_props")
        return typing.cast(typing.Optional[aws_cdk.aws_lambda.FunctionProps], result)

    @builtins.property
    def dead_letter_queue_props(self) -> typing.Optional[aws_cdk.aws_sqs.QueueProps]:
        '''Optional user-provided props to override the default props for the dead letter queue.

        Only used if the
        ``deployDeadLetterQueue`` property is set to true.

        :default: - Default props are used.
        '''
        result = self._values.get("dead_letter_queue_props")
        return typing.cast(typing.Optional[aws_cdk.aws_sqs.QueueProps], result)

    @builtins.property
    def deploy_dead_letter_queue(self) -> typing.Optional[builtins.bool]:
        '''Whether to create a secondary queue to be used as a dead letter queue.

        Defaults to ``true``.

        :default: - true.
        '''
        result = self._values.get("deploy_dead_letter_queue")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def deploy_vpc(self) -> typing.Optional[builtins.bool]:
        '''Whether to deploy a new VPC.

        :default: - false
        '''
        result = self._values.get("deploy_vpc")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def existing_consumer_lambda_obj(
        self,
    ) -> typing.Optional[aws_cdk.aws_lambda.Function]:
        '''An optional, existing Lambda function to be used instead of the default function for receiving/consuming messages from the queue.

        Providing both this and ``consumerLambdaFunctionProps`` will cause an error.

        :default: - None.
        '''
        result = self._values.get("existing_consumer_lambda_obj")
        return typing.cast(typing.Optional[aws_cdk.aws_lambda.Function], result)

    @builtins.property
    def existing_producer_lambda_obj(
        self,
    ) -> typing.Optional[aws_cdk.aws_lambda.Function]:
        '''An optional, existing Lambda function to be used instead of the default function for sending messages to the queue.

        Providing both this and ``producerLambdaFunctionProps`` property will cause an error.

        :default: - None.
        '''
        result = self._values.get("existing_producer_lambda_obj")
        return typing.cast(typing.Optional[aws_cdk.aws_lambda.Function], result)

    @builtins.property
    def existing_queue_obj(self) -> typing.Optional[aws_cdk.aws_sqs.Queue]:
        '''An optional, existing SQS queue to be used instead of the default queue.

        Providing both this and ``queueProps``
        will cause an error.

        :default: - None.
        '''
        result = self._values.get("existing_queue_obj")
        return typing.cast(typing.Optional[aws_cdk.aws_sqs.Queue], result)

    @builtins.property
    def existing_vpc(self) -> typing.Optional[aws_cdk.aws_ec2.IVpc]:
        '''An existing VPC for the construct to use (construct will NOT create a new VPC in this case).'''
        result = self._values.get("existing_vpc")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.IVpc], result)

    @builtins.property
    def max_receive_count(self) -> typing.Optional[jsii.Number]:
        '''The number of times a message can be unsuccessfully dequeued before being moved to the dead letter queue.

        Defaults to ``15``.

        :default:

        -
        15.
        '''
        result = self._values.get("max_receive_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def producer_lambda_function_props(
        self,
    ) -> typing.Optional[aws_cdk.aws_lambda.FunctionProps]:
        '''Optional user-provided properties to override the default properties for the producer Lambda function.

        :default: - Default properties are used.
        '''
        result = self._values.get("producer_lambda_function_props")
        return typing.cast(typing.Optional[aws_cdk.aws_lambda.FunctionProps], result)

    @builtins.property
    def queue_environment_variable_name(self) -> typing.Optional[builtins.str]:
        '''Optional Name for the SQS queue URL environment variable set for the producer Lambda function.

        :default: - None
        '''
        result = self._values.get("queue_environment_variable_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def queue_props(self) -> typing.Optional[aws_cdk.aws_sqs.QueueProps]:
        '''Optional user-provided properties to override the default properties for the SQS queue.

        :default: - Default props are used.
        '''
        result = self._values.get("queue_props")
        return typing.cast(typing.Optional[aws_cdk.aws_sqs.QueueProps], result)

    @builtins.property
    def sqs_event_source_props(
        self,
    ) -> typing.Optional[aws_cdk.aws_lambda_event_sources.SqsEventSourceProps]:
        '''Optional user provided properties for the queue event source.

        :default: - Default props are used
        '''
        result = self._values.get("sqs_event_source_props")
        return typing.cast(typing.Optional[aws_cdk.aws_lambda_event_sources.SqsEventSourceProps], result)

    @builtins.property
    def vpc_props(self) -> typing.Optional[aws_cdk.aws_ec2.VpcProps]:
        '''Properties to override default properties if deployVpc is true.'''
        result = self._values.get("vpc_props")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.VpcProps], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LambdaToSqsToLambdaProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "LambdaToSqsToLambda",
    "LambdaToSqsToLambdaProps",
]

publication.publish()
