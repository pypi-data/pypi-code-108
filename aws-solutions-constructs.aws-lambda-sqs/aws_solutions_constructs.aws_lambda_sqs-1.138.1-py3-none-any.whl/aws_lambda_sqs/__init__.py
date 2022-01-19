'''
# aws-lambda-sqs module

<!--BEGIN STABILITY BANNER-->---


![Stability: Stable](https://img.shields.io/badge/cfn--resources-stable-success.svg?style=for-the-badge)

---
<!--END STABILITY BANNER-->

| **Reference Documentation**:| <span style="font-weight: normal">https://docs.aws.amazon.com/solutions/latest/constructs/</span>|
|:-------------|:-------------|

<div style="height:8px"></div>

| **Language**     | **Package**        |
|:-------------|-----------------|
|![Python Logo](https://docs.aws.amazon.com/cdk/api/latest/img/python32.png) Python|`aws_solutions_constructs.aws_lambda_sqs`|
|![Typescript Logo](https://docs.aws.amazon.com/cdk/api/latest/img/typescript32.png) Typescript|`@aws-solutions-constructs/aws-lambda-sqs`|
|![Java Logo](https://docs.aws.amazon.com/cdk/api/latest/img/java32.png) Java|`software.amazon.awsconstructs.services.lambdasqs`|

This AWS Solutions Construct implements an AWS Lambda function connected to an Amazon SQS queue.

Here is a minimal deployable pattern definition in Typescript:

```python
import { LambdaToSqs, LambdaToSqsProps } from "@aws-solutions-constructs/aws-lambda-sqs";

new LambdaToSqs(this, 'LambdaToSqsPattern', {
    lambdaFunctionProps: {
        runtime: lambda.Runtime.NODEJS_14_X,
        handler: 'index.handler',
        code: lambda.Code.fromAsset(`${__dirname}/lambda`)
    }
});
```

## Initializer

```text
new LambdaToSqs(scope: Construct, id: string, props: LambdaToSqsProps);
```

*Parameters*

* scope [`Construct`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_core.Construct.html)
* id `string`
* props [`LambdaToSqsProps`](#pattern-construct-props)

## Pattern Construct Props

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
|existingLambdaObj?|[`lambda.Function`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-lambda.Function.html)|An optional, existing Lambda function to be used instead of the default function. Providing both this and `lambdaFunctionProps` will cause an error.|
|lambdaFunctionProps?|[`lambda.FunctionProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-lambda.FunctionProps.html)|Optional user-provided properties to override the default properties for the Lambda function. |
|existingQueueObj?|[`sqs.Queue`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-sqs.Queue.html)|An optional, existing SQS queue to be used instead of the default queue. Providing both this and `queueProps` will cause an error.|
|queueProps?|[`sqs.QueueProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-sqs.QueueProps.html)|Optional user-provided properties to override the default properties for the SQS queue.|
|enableQueuePurging?|`boolean`|Whether to grant additional permissions to the Lambda function enabling it to purge the SQS queue. Defaults to `false`.|
|deployDeadLetterQueue?|`boolean`|Whether to create a secondary queue to be used as a dead letter queue. Defaults to `true`.|
|deadLetterQueueProps?|[`sqs.QueueProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-sqs.QueueProps.html)|Optional user-provided props to override the default props for the dead letter queue. Only used if the `deployDeadLetterQueue` property is set to true.|
|maxReceiveCount?|`number`|The number of times a message can be unsuccessfully dequeued before being moved to the dead letter queue. Defaults to `15`.|
|existingVpc?|[`ec2.IVpc`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-ec2.IVpc.html)|An optional, existing VPC into which this pattern should be deployed. When deployed in a VPC, the Lambda function will use ENIs in the VPC to access network resources and an Interface Endpoint will be created in the VPC for Amazon SQS. If an existing VPC is provided, the `deployVpc` property cannot be `true`. This uses `ec2.IVpc` to allow clients to supply VPCs that exist outside the stack using the [`ec2.Vpc.fromLookup()`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-ec2.Vpc.html#static-fromwbrlookupscope-id-options) method.|
|vpcProps?|[`ec2.VpcProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-ec2.VpcProps.html)|Optional user-provided properties to override the default properties for the new VPC. `enableDnsHostnames`, `enableDnsSupport`, `natGateways` and `subnetConfiguration` are set by the pattern, so any values for those properties supplied here will be overrriden. If `deployVpc` is not `true` then this property will be ignored.|
|deployVpc?|`boolean`|Whether to create a new VPC based on `vpcProps` into which to deploy this pattern. Setting this to true will deploy the minimal, most private VPC to run the pattern:<ul><li> One isolated subnet in each Availability Zone used by the CDK program</li><li>`enableDnsHostnames` and `enableDnsSupport` will both be set to true</li></ul>If this property is `true` then `existingVpc` cannot be specified. Defaults to `false`.|
|queueEnvironmentVariableName?|`string`|Optional Name for the SQS queue URL environment variable set for the Lambda function.|

## Pattern Properties

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
|lambdaFunction|[`lambda.Function`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-lambda.Function.html)|Returns an instance of the Lambda function created by the pattern.|
|sqsQueue|[`sqs.Queue`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-sqs.Queue.html)|Returns an instance of the SQS queue created by the pattern. |
|deadLetterQueue?|[`sqs.Queue`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-sqs.Queue.html)|Returns an instance of the dead letter queue created by the pattern, if one is deployed.|
|vpc?|[`ec2.IVpc`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-ec2.IVpc.html)|Returns an interface on the VPC used by the pattern (if any). This may be a VPC created by the pattern or the VPC supplied to the pattern constructor.|

## Default settings

Out of the box implementation of the Construct without any override will set the following defaults:

### AWS Lambda Function

* Configure limited privilege access IAM role for Lambda function.
* Enable reusing connections with Keep-Alive for NodeJs Lambda function.
* Allow the function to send messages only to the queue (purging can be enabled using the `enableQueuePurge` property).
* Enable X-Ray Tracing
* Set Environment Variables

  * SQS_QUEUE_URL
  * AWS_NODEJS_CONNECTION_REUSE_ENABLED (for Node 10.x and higher functions)

### Amazon SQS Queue

* Deploy SQS dead-letter queue for the source SQS Queue.
* Enable server-side encryption for source SQS Queue using AWS Managed KMS Key.
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
import aws_cdk.aws_sqs
import aws_cdk.core


class LambdaToSqs(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-solutions-constructs/aws-lambda-sqs.LambdaToSqs",
):
    '''
    :summary: The LambdaToSqs class.
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        dead_letter_queue_props: typing.Optional[aws_cdk.aws_sqs.QueueProps] = None,
        deploy_dead_letter_queue: typing.Optional[builtins.bool] = None,
        deploy_vpc: typing.Optional[builtins.bool] = None,
        enable_queue_purging: typing.Optional[builtins.bool] = None,
        existing_lambda_obj: typing.Optional[aws_cdk.aws_lambda.Function] = None,
        existing_queue_obj: typing.Optional[aws_cdk.aws_sqs.Queue] = None,
        existing_vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
        lambda_function_props: typing.Optional[aws_cdk.aws_lambda.FunctionProps] = None,
        max_receive_count: typing.Optional[jsii.Number] = None,
        queue_environment_variable_name: typing.Optional[builtins.str] = None,
        queue_props: typing.Optional[aws_cdk.aws_sqs.QueueProps] = None,
        vpc_props: typing.Optional[aws_cdk.aws_ec2.VpcProps] = None,
    ) -> None:
        '''
        :param scope: - represents the scope for all the resources.
        :param id: - this is a a scope-unique id.
        :param dead_letter_queue_props: Optional user provided properties for the dead letter queue. Default: - Default props are used
        :param deploy_dead_letter_queue: Whether to deploy a secondary queue to be used as a dead letter queue. Default: - true.
        :param deploy_vpc: Whether to deploy a new VPC. Default: - false
        :param enable_queue_purging: Whether to grant additional permissions to the Lambda function enabling it to purge the SQS queue. Default: - "false", disabled by default.
        :param existing_lambda_obj: Existing instance of Lambda Function object, providing both this and ``lambdaFunctionProps`` will cause an error. Default: - None
        :param existing_queue_obj: Existing instance of SQS queue object, Providing both this and queueProps will cause an error. Default: - Default props are used
        :param existing_vpc: An existing VPC for the construct to use (construct will NOT create a new VPC in this case).
        :param lambda_function_props: User provided props to override the default props for the Lambda function. Default: - Default properties are used.
        :param max_receive_count: The number of times a message can be unsuccessfully dequeued before being moved to the dead-letter queue. Default: - required field if deployDeadLetterQueue=true.
        :param queue_environment_variable_name: Optional Name for the SQS queue URL environment variable set for the Lambda function. Default: - None
        :param queue_props: Optional user-provided props to override the default props for the SQS queue. Default: - Default props are used
        :param vpc_props: Properties to override default properties if deployVpc is true.

        :access: public
        :since: 1.49.0
        :summary: Constructs a new instance of the LambdaToSqs class.
        '''
        props = LambdaToSqsProps(
            dead_letter_queue_props=dead_letter_queue_props,
            deploy_dead_letter_queue=deploy_dead_letter_queue,
            deploy_vpc=deploy_vpc,
            enable_queue_purging=enable_queue_purging,
            existing_lambda_obj=existing_lambda_obj,
            existing_queue_obj=existing_queue_obj,
            existing_vpc=existing_vpc,
            lambda_function_props=lambda_function_props,
            max_receive_count=max_receive_count,
            queue_environment_variable_name=queue_environment_variable_name,
            queue_props=queue_props,
            vpc_props=vpc_props,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambdaFunction")
    def lambda_function(self) -> aws_cdk.aws_lambda.Function:
        return typing.cast(aws_cdk.aws_lambda.Function, jsii.get(self, "lambdaFunction"))

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
    jsii_type="@aws-solutions-constructs/aws-lambda-sqs.LambdaToSqsProps",
    jsii_struct_bases=[],
    name_mapping={
        "dead_letter_queue_props": "deadLetterQueueProps",
        "deploy_dead_letter_queue": "deployDeadLetterQueue",
        "deploy_vpc": "deployVpc",
        "enable_queue_purging": "enableQueuePurging",
        "existing_lambda_obj": "existingLambdaObj",
        "existing_queue_obj": "existingQueueObj",
        "existing_vpc": "existingVpc",
        "lambda_function_props": "lambdaFunctionProps",
        "max_receive_count": "maxReceiveCount",
        "queue_environment_variable_name": "queueEnvironmentVariableName",
        "queue_props": "queueProps",
        "vpc_props": "vpcProps",
    },
)
class LambdaToSqsProps:
    def __init__(
        self,
        *,
        dead_letter_queue_props: typing.Optional[aws_cdk.aws_sqs.QueueProps] = None,
        deploy_dead_letter_queue: typing.Optional[builtins.bool] = None,
        deploy_vpc: typing.Optional[builtins.bool] = None,
        enable_queue_purging: typing.Optional[builtins.bool] = None,
        existing_lambda_obj: typing.Optional[aws_cdk.aws_lambda.Function] = None,
        existing_queue_obj: typing.Optional[aws_cdk.aws_sqs.Queue] = None,
        existing_vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
        lambda_function_props: typing.Optional[aws_cdk.aws_lambda.FunctionProps] = None,
        max_receive_count: typing.Optional[jsii.Number] = None,
        queue_environment_variable_name: typing.Optional[builtins.str] = None,
        queue_props: typing.Optional[aws_cdk.aws_sqs.QueueProps] = None,
        vpc_props: typing.Optional[aws_cdk.aws_ec2.VpcProps] = None,
    ) -> None:
        '''
        :param dead_letter_queue_props: Optional user provided properties for the dead letter queue. Default: - Default props are used
        :param deploy_dead_letter_queue: Whether to deploy a secondary queue to be used as a dead letter queue. Default: - true.
        :param deploy_vpc: Whether to deploy a new VPC. Default: - false
        :param enable_queue_purging: Whether to grant additional permissions to the Lambda function enabling it to purge the SQS queue. Default: - "false", disabled by default.
        :param existing_lambda_obj: Existing instance of Lambda Function object, providing both this and ``lambdaFunctionProps`` will cause an error. Default: - None
        :param existing_queue_obj: Existing instance of SQS queue object, Providing both this and queueProps will cause an error. Default: - Default props are used
        :param existing_vpc: An existing VPC for the construct to use (construct will NOT create a new VPC in this case).
        :param lambda_function_props: User provided props to override the default props for the Lambda function. Default: - Default properties are used.
        :param max_receive_count: The number of times a message can be unsuccessfully dequeued before being moved to the dead-letter queue. Default: - required field if deployDeadLetterQueue=true.
        :param queue_environment_variable_name: Optional Name for the SQS queue URL environment variable set for the Lambda function. Default: - None
        :param queue_props: Optional user-provided props to override the default props for the SQS queue. Default: - Default props are used
        :param vpc_props: Properties to override default properties if deployVpc is true.

        :summary: The properties for the LambdaToSqs class.
        '''
        if isinstance(dead_letter_queue_props, dict):
            dead_letter_queue_props = aws_cdk.aws_sqs.QueueProps(**dead_letter_queue_props)
        if isinstance(lambda_function_props, dict):
            lambda_function_props = aws_cdk.aws_lambda.FunctionProps(**lambda_function_props)
        if isinstance(queue_props, dict):
            queue_props = aws_cdk.aws_sqs.QueueProps(**queue_props)
        if isinstance(vpc_props, dict):
            vpc_props = aws_cdk.aws_ec2.VpcProps(**vpc_props)
        self._values: typing.Dict[str, typing.Any] = {}
        if dead_letter_queue_props is not None:
            self._values["dead_letter_queue_props"] = dead_letter_queue_props
        if deploy_dead_letter_queue is not None:
            self._values["deploy_dead_letter_queue"] = deploy_dead_letter_queue
        if deploy_vpc is not None:
            self._values["deploy_vpc"] = deploy_vpc
        if enable_queue_purging is not None:
            self._values["enable_queue_purging"] = enable_queue_purging
        if existing_lambda_obj is not None:
            self._values["existing_lambda_obj"] = existing_lambda_obj
        if existing_queue_obj is not None:
            self._values["existing_queue_obj"] = existing_queue_obj
        if existing_vpc is not None:
            self._values["existing_vpc"] = existing_vpc
        if lambda_function_props is not None:
            self._values["lambda_function_props"] = lambda_function_props
        if max_receive_count is not None:
            self._values["max_receive_count"] = max_receive_count
        if queue_environment_variable_name is not None:
            self._values["queue_environment_variable_name"] = queue_environment_variable_name
        if queue_props is not None:
            self._values["queue_props"] = queue_props
        if vpc_props is not None:
            self._values["vpc_props"] = vpc_props

    @builtins.property
    def dead_letter_queue_props(self) -> typing.Optional[aws_cdk.aws_sqs.QueueProps]:
        '''Optional user provided properties for the dead letter queue.

        :default: - Default props are used
        '''
        result = self._values.get("dead_letter_queue_props")
        return typing.cast(typing.Optional[aws_cdk.aws_sqs.QueueProps], result)

    @builtins.property
    def deploy_dead_letter_queue(self) -> typing.Optional[builtins.bool]:
        '''Whether to deploy a secondary queue to be used as a dead letter queue.

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
    def enable_queue_purging(self) -> typing.Optional[builtins.bool]:
        '''Whether to grant additional permissions to the Lambda function enabling it to purge the SQS queue.

        :default: - "false", disabled by default.
        '''
        result = self._values.get("enable_queue_purging")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def existing_lambda_obj(self) -> typing.Optional[aws_cdk.aws_lambda.Function]:
        '''Existing instance of Lambda Function object, providing both this and ``lambdaFunctionProps`` will cause an error.

        :default: - None
        '''
        result = self._values.get("existing_lambda_obj")
        return typing.cast(typing.Optional[aws_cdk.aws_lambda.Function], result)

    @builtins.property
    def existing_queue_obj(self) -> typing.Optional[aws_cdk.aws_sqs.Queue]:
        '''Existing instance of SQS queue object, Providing both this and queueProps will cause an error.

        :default: - Default props are used
        '''
        result = self._values.get("existing_queue_obj")
        return typing.cast(typing.Optional[aws_cdk.aws_sqs.Queue], result)

    @builtins.property
    def existing_vpc(self) -> typing.Optional[aws_cdk.aws_ec2.IVpc]:
        '''An existing VPC for the construct to use (construct will NOT create a new VPC in this case).'''
        result = self._values.get("existing_vpc")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.IVpc], result)

    @builtins.property
    def lambda_function_props(
        self,
    ) -> typing.Optional[aws_cdk.aws_lambda.FunctionProps]:
        '''User provided props to override the default props for the Lambda function.

        :default: - Default properties are used.
        '''
        result = self._values.get("lambda_function_props")
        return typing.cast(typing.Optional[aws_cdk.aws_lambda.FunctionProps], result)

    @builtins.property
    def max_receive_count(self) -> typing.Optional[jsii.Number]:
        '''The number of times a message can be unsuccessfully dequeued before being moved to the dead-letter queue.

        :default: - required field if deployDeadLetterQueue=true.
        '''
        result = self._values.get("max_receive_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def queue_environment_variable_name(self) -> typing.Optional[builtins.str]:
        '''Optional Name for the SQS queue URL environment variable set for the Lambda function.

        :default: - None
        '''
        result = self._values.get("queue_environment_variable_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def queue_props(self) -> typing.Optional[aws_cdk.aws_sqs.QueueProps]:
        '''Optional user-provided props to override the default props for the SQS queue.

        :default: - Default props are used
        '''
        result = self._values.get("queue_props")
        return typing.cast(typing.Optional[aws_cdk.aws_sqs.QueueProps], result)

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
        return "LambdaToSqsProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "LambdaToSqs",
    "LambdaToSqsProps",
]

publication.publish()
